# Full LaTeX build (pdflatex -> bibtex -> pdflatex x2) for the WAGER manuscript.
$bin = "C:\Users\vinh.dq4\AppData\Local\Programs\MiKTeX\miktex\bin\x64"
$pdflatex = "$bin\pdflatex.exe"
$bibtex   = "$bin\bibtex.exe"
Set-Location "C:\work\WAGER\manuscript"
$opts = @("-interaction=nonstopmode", "-file-line-error", "main.tex")

& $pdflatex $opts            *> $null
& $bibtex   main             *> $null
& $pdflatex $opts            *> $null
& $pdflatex $opts            2>&1 | Out-Null

Write-Output "===== BUILD REPORT ====="
$out = (Select-String -Path main.log -Pattern "Output written on main.pdf").Line
Write-Output ($(if ($out) { $out.Trim() } else { "NO PDF WRITTEN" }))
$undef    = (Select-String -Path main.log -Pattern "Citation .* undefined").Count
$undefref = (Select-String -Path main.log -Pattern "Reference .* undefined").Count
$overfull = (Select-String -Path main.log -Pattern "Overfull \\hbox").Count
Write-Output "Undefined citations: $undef | Undefined refs: $undefref | Overfull hboxes: $overfull"
$errs = Select-String -Path main.log -Pattern "^main\.tex:\d+:|^\./|^! "
if ($errs) { Write-Output "ERRORS:"; $errs | Select-Object -First 15 | ForEach-Object { Write-Output ("  " + $_.Line) } }
else { Write-Output "No fatal errors." }
