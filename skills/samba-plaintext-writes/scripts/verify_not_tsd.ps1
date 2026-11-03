param(
    [Parameter(Mandatory = $true)]
    [string]$Path
)

$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $Path)) {
    Write-Error "Not found: $Path"
    exit 2
}
$item = Get-Item -LiteralPath $Path
if ($item.PSIsContainer) {
    Write-Error "Use -Path on a file, not a directory"
    exit 2
}

$stream = [System.IO.File]::OpenRead($item.FullName)
try {
    $buf = New-Object byte[] 16
    $n = $stream.Read($buf, 0, 16)
} finally {
    $stream.Close()
}

$head = [System.Text.Encoding]::ASCII.GetString($buf, 0, $n)
if ($head.StartsWith('%TSD-Header')) {
    Write-Output "TSD: $Path"
    exit 1
}

# 常见文本文件不应全是高熵 binary；仅作弱提示
if ($n -ge 4 -and $buf[0] -eq 0 -and $buf[1] -eq 0) {
    Write-Host "Suspicious binary/null header: $Path"
    exit 1
}

Write-Output "OK: $Path"
exit 0
