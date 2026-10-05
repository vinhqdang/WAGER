"""Fetch only the VG150 test images, by HTTP range requests into the two image zips.

The SGCls/SGDet runs read the 26,446 test images only, but the codebase's loader
keeps an image in its list only if its file exists, and indexes the annotation file
by that list, so every other image gets an empty placeholder file. Each zip's central
directory is read once (zip64-aware, via zipfile on a range-backed file object) and
each needed member is fetched with one range request, from a thread pool.

Usage (on the VM): python colab_vg_test_images.py <h5> <image_data.json> <out_dir>
"""
import concurrent.futures as cf
import io
import json
import os
import struct
import sys
import time
import urllib.request
import zipfile
import zlib

import h5py
import numpy as np

BASE = "https://cs.stanford.edu/people/rak248/VG_100K_2/"
CORRUPTED = {"1592.jpg", "1722.jpg", "4616.jpg", "4617.jpg"}


def get_range(url, a, b, tries=6):
    for t in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0",
                                                       "Range": f"bytes={a}-{b}"})
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
            if len(data) == b - a + 1:
                return data
        except Exception:
            time.sleep(2 ** t)
    raise RuntimeError(f"range {a}-{b} of {url} failed")


class RangeFile(io.RawIOBase):
    def __init__(self, url):
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            self.size = int(r.headers["Content-Length"])
        self.url, self.pos = url, 0

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, off, whence=0):
        self.pos = {0: off, 1: self.pos + off, 2: self.size + off}[whence]
        return self.pos

    def read(self, n=-1):
        if n < 0:
            n = self.size - self.pos
        n = min(n, self.size - self.pos)
        if n <= 0:
            return b""
        data = get_range(self.url, self.pos, self.pos + n - 1)
        self.pos += n
        return data


def member(url, info):
    """Fetch and decode one member from its local header offset."""
    head = get_range(url, info.header_offset, info.header_offset + 29)
    n_name, n_extra = struct.unpack("<HH", head[26:30])
    start = info.header_offset + 30 + n_name + n_extra
    raw = get_range(url, start, start + info.compress_size - 1)
    if info.compress_type == zipfile.ZIP_STORED:
        return raw
    return zlib.decompress(raw, -15)


def main(h5, image_data, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    im_data = json.load(open(image_data))
    names = [f"{im['image_id']}.jpg" for im in im_data if f"{im['image_id']}.jpg" not in CORRUPTED]
    assert len(names) == 108073, len(names)
    with h5py.File(h5, "r") as f:
        test = (f["split"][:] == 2) & (f["img_to_first_box"][:] >= 0) & (f["img_to_first_rel"][:] >= 0)
    need = {names[i] for i in np.flatnonzero(test)}
    print(f"{len(need)} test images to fetch", flush=True)
    todo = []
    for z in ("images.zip", "images2.zip"):
        url = BASE + z
        with zipfile.ZipFile(RangeFile(url)) as zf:
            for info in zf.infolist():
                b = os.path.basename(info.filename)
                if b in need and not os.path.exists(os.path.join(out_dir, b)):
                    todo.append((url, info))
        print(f"{z}: central directory read; {len(todo)} members queued so far", flush=True)
    t0, done = time.time(), 0

    def work(item):
        url, info = item
        data = member(url, info)
        out = os.path.join(out_dir, os.path.basename(info.filename))
        with open(out + ".part", "wb") as o:
            o.write(data)
        os.replace(out + ".part", out)
    with cf.ThreadPoolExecutor(24) as ex:
        for _ in ex.map(work, todo):
            done += 1
            if done % 2000 == 0:
                print(f"  {done}/{len(todo)} images ({time.time()-t0:.0f}s)", flush=True)
    missing = [b for b in need if not os.path.exists(os.path.join(out_dir, b))]
    assert not missing, f"{len(missing)} test images missing"
    n_ph = 0
    for b in names:                      # placeholders keep the loader's index aligned
        p = os.path.join(out_dir, b)
        if not os.path.exists(p):
            open(p, "wb").close()
            n_ph += 1
    print(f"TEST IMAGES READY: {len(need)} fetched, {n_ph} placeholders", flush=True)


if __name__ == "__main__":
    main(*sys.argv[1:4])
