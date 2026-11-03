# Push local file(s) to Linux over SSH as plain UTF-8 bytes (avoid TSD-wrapped scp).
param(
    [Parameter(Mandatory = $true)]
    [string]$UserHost,

    [Parameter(Mandatory = $true)]
    [string]$RemoteDir,

    [Parameter(Mandatory = $true, ValueFromRemainingArguments = $true)]
    [string[]]$LocalFiles
)

$ErrorActionPreference = 'Stop'
$py = Join-Path $env:LocalAppData 'Programs\Python\Python313\python.exe'
if (-not (Test-Path $py)) { $py = 'py' }

foreach ($local in $LocalFiles) {
    if (-not (Test-Path -LiteralPath $local)) {
        throw "Local file not found: $local"
    }
    $name = [System.IO.Path]::GetFileName($local)
    $remote = ($RemoteDir.TrimEnd('/') + '/' + $name) -replace '\\', '/'
    & $py -c @"
import base64, pathlib, subprocess, sys
src = pathlib.Path(r'''$($local -replace "'","''")''')
data = src.read_bytes()
remote = '''$($remote -replace "'","''")'''
subprocess.run(
    ['ssh', '$UserHost', f'base64 -d > {remote}'],
    input=base64.b64encode(data),
    check=True,
)
print(f'OK {src} -> {remote} ({len(data)} bytes)')
"@
}

Write-Host "Verify on Linux: file $RemoteDir/<name>"
