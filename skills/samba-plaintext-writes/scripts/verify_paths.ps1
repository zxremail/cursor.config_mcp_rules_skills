param(
    [string[]]$Path,
    [string]$Root,
    [string[]]$Include = @('*.py', '*.md', '*.json', '*.yaml', '*.yml', '*.ps1', '*.cmd', '*.js', '*.ts', '*.html', '*.css')
)

$ErrorActionPreference = 'Stop'
$verify = Join-Path $PSScriptRoot 'verify_not_tsd.ps1'
$files = [System.Collections.Generic.List[string]]::new()

if ($Path) {
    foreach ($p in $Path) {
        if (Test-Path -LiteralPath $p -PathType Leaf) { [void]$files.Add((Resolve-Path -LiteralPath $p).Path) }
    }
}
if ($Root) {
    Get-ChildItem -LiteralPath $Root -Recurse -File -Include $Include | ForEach-Object { [void]$files.Add($_.FullName) }
}
if ($files.Count -eq 0) {
    Write-Error 'No files to verify. Use -Path and/or -Root.'
    exit 2
}

$fail = @()
foreach ($f in $files) {
    & $verify -Path $f 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) { $fail += $f }
}

if ($fail.Count -gt 0) {
    Write-Host "TSD verify FAIL ($($fail.Count)/$($files.Count)):"
    $fail | ForEach-Object { Write-Host "  $_" }
    exit 1
}

Write-Host "TSD verify OK ($($files.Count) files)"
exit 0
