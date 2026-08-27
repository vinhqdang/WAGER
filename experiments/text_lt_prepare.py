"""Cross-domain WAGER study: long-tailed text classification (20 Newsgroups-LT).

Builds a long-tailed *training* subset of the 20 Newsgroups corpus using the
same exponential-profile recipe as CIFAR-100-LT (imbalance ratio 100), and
prepares TF-IDF + truncated-SVD features for a small MLP.  The standard test
split is left untouched and balanced -- exactly the CIFAR-100-LT protocol,
just applied to a structurally different domain (sparse bag-of-words text
instead of pixels).

Coarse supergroups (the ``phi=superclass`` prior audited downstream) follow
the standard 20 Newsgroups grouping into six topics:

    comp.*             (5 classes)
    rec.*              (4 classes)
    sci.*              (4 classes)
    talk.politics.*    (3 classes)
    religion           (3 classes: alt.atheism, soc.religion.christian,
                         talk.religion.misc)
    misc.forsale       (1 class)

Long-tail construction
-----------------------
sklearn's ``fetch_20newsgroups`` returns the 20 fine classes in a fixed
alphabetical order (0=alt.atheism ... 19=talk.religion.misc).  Alphabetical
order is correlated with the coarse grouping above (e.g. all five comp.*
classes are contiguous), so imposing the long-tail profile directly on that
order would confound "head vs. tail" with "which supergroup".  We therefore
draw a *seeded* random permutation of the 20 class ids and let the resulting
rank (0=most training data, 19=least) determine each class's target count:

    mu = 100 ** (-1/19)
    target_c = floor(n_max * mu ** rank_of_class[c])
    n_c      = min(target_c, available_train_docs[c])

where ``n_max`` is the largest number of training documents available for any
single class in the raw corpus (the 20 Newsgroups classes are not perfectly
balanced to begin with, unlike CIFAR-100's exactly-500-per-class train set).
The cap on the second line is what keeps every class's request within what
actually exists; only the rank-0 class (or a class lucky enough to already
have >= n_max documents) is unaffected by it.
"""
from __future__ import annotations

import json
import os

import numpy as np
from sklearn.datasets import fetch_20newsgroups
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer

SEED = 0
IMBALANCE_RATIO = 100.0
SVD_DIM = 300
TFIDF_MAX_FEATURES = 20000

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "data", "text_lt")
os.makedirs(OUTDIR, exist_ok=True)

# Standard six-supergroup coarsening of the 20 fine classes (alphabetical
# sklearn class-id order): comp.*=0, rec.*=1, sci.*=2, talk.politics.*=3,
# religion=4, misc.forsale=5.
COARSE_GROUPS = {
    0: ["comp.graphics", "comp.os.ms-windows.misc", "comp.sys.ibm.pc.hardware",
        "comp.sys.mac.hardware", "comp.windows.x"],
    1: ["rec.autos", "rec.motorcycles", "rec.sport.baseball", "rec.sport.hockey"],
    2: ["sci.crypt", "sci.electronics", "sci.med", "sci.space"],
    3: ["talk.politics.misc", "talk.politics.guns", "talk.politics.mideast"],
    4: ["talk.religion.misc", "alt.atheism", "soc.religion.christian"],
    5: ["misc.forsale"],
}
COARSE_NAMES = {0: "comp", 1: "rec", 2: "sci", 3: "talk.politics",
                4: "religion", 5: "misc.forsale"}


def main():
    print("Fetching 20 Newsgroups (train/test, headers/footers/quotes stripped) ...",
          flush=True)
    train = fetch_20newsgroups(subset="train", remove=("headers", "footers", "quotes"))
    test = fetch_20newsgroups(subset="test", remove=("headers", "footers", "quotes"))
    class_names = train.target_names  # fixed alphabetical order, length 20
    n_cls = len(class_names)
    assert n_cls == 20 and test.target_names == class_names

    name_to_coarse = {}
    for coarse_id, names in COARSE_GROUPS.items():
        for name in names:
            name_to_coarse[name] = coarse_id
    assert set(name_to_coarse) == set(class_names), "coarse mapping does not cover all 20 classes"
    coarse_of_class = np.array([name_to_coarse[n] for n in class_names], dtype=np.int64)

    y_train_full = train.target.astype(np.int64)
    y_test = test.target.astype(np.int64)
    avail = np.bincount(y_train_full, minlength=n_cls)
    print(f"  train docs (balanced) = {len(y_train_full)}, test docs = {len(y_test)}",
          flush=True)
    print("  per-class available train docs:",
          dict(zip(class_names, avail.tolist())), flush=True)

    # ---- seeded rank permutation over the 20 classes ----
    rng = np.random.default_rng(SEED)
    perm = rng.permutation(n_cls)          # perm[r] = class id placed at rank r
    rank_of_class = np.empty(n_cls, dtype=np.int64)
    rank_of_class[perm] = np.arange(n_cls)
    print(f"  seeded permutation (perm[rank]=class_id): {perm.tolist()}", flush=True)
    print("  rank_of_class:", dict(zip(class_names, rank_of_class.tolist())), flush=True)

    mu = IMBALANCE_RATIO ** (-1.0 / (n_cls - 1))
    n_max = int(avail.max())
    target = np.floor(n_max * mu ** rank_of_class).astype(np.int64)
    per_class_train_n = np.minimum(target, avail)
    print(f"  mu={mu:.6f}  n_max={n_max}", flush=True)
    print("  final per-class LT train counts:",
          dict(zip(class_names, per_class_train_n.tolist())), flush=True)

    lt_indices = np.concatenate([
        rng.choice(np.flatnonzero(y_train_full == c), size=int(per_class_train_n[c]),
                   replace=False)
        for c in range(n_cls)
    ])
    rng.shuffle(lt_indices)
    y_train = y_train_full[lt_indices]
    texts_train = [train.data[i] for i in lt_indices]
    print(f"  LT train size: {len(y_train)} (from {len(y_train_full)} balanced)",
          flush=True)

    # ---- TF-IDF fit only on the LT train subset; transform test with it ----
    vectorizer = TfidfVectorizer(max_features=TFIDF_MAX_FEATURES, sublinear_tf=True,
                                 stop_words="english")
    X_train_tfidf = vectorizer.fit_transform(texts_train)
    X_test_tfidf = vectorizer.transform(test.data)
    print(f"  TF-IDF shapes: train={X_train_tfidf.shape} test={X_test_tfidf.shape}",
          flush=True)

    svd = TruncatedSVD(n_components=SVD_DIM, random_state=SEED)
    X_train = svd.fit_transform(X_train_tfidf).astype(np.float32)
    X_test = svd.transform(X_test_tfidf).astype(np.float32)
    explained = float(svd.explained_variance_ratio_.sum())
    print(f"  SVD({SVD_DIM}) explained variance ratio: {explained:.4f}", flush=True)

    out_path = os.path.join(OUTDIR, "text_lt_data.npz")
    np.savez_compressed(
        out_path,
        X_train=X_train, y_train=y_train,
        X_test=X_test, y_test=y_test,
        per_class_train_n=per_class_train_n,
        coarse_of_class=coarse_of_class,
        rank_of_class=rank_of_class,
        class_names=np.array(class_names),
        coarse_names=np.array([COARSE_NAMES[i] for i in range(len(COARSE_NAMES))]),
        seed=SEED,
        imbalance_ratio=IMBALANCE_RATIO,
        mu=mu,
        n_max=n_max,
        svd_dim=SVD_DIM,
        tfidf_max_features=TFIDF_MAX_FEATURES,
        svd_explained_variance=explained,
    )
    summary = {
        "n_train_lt": int(len(y_train)),
        "n_train_balanced": int(len(y_train_full)),
        "n_test": int(len(y_test)),
        "n_classes": n_cls,
        "n_coarse": len(COARSE_GROUPS),
        "imbalance_ratio": IMBALANCE_RATIO,
        "mu": mu,
        "n_max": n_max,
        "per_class_train_n_min": int(per_class_train_n.min()),
        "per_class_train_n_max": int(per_class_train_n.max()),
        "svd_dim": SVD_DIM,
        "svd_explained_variance": explained,
        "tfidf_max_features": TFIDF_MAX_FEATURES,
    }
    with open(os.path.join(OUTDIR, "text_lt_prepare_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Saved {out_path}", flush=True)
    print("Summary:", json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
