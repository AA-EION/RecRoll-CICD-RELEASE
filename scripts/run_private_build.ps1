[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Script,
    [string]$StatusFile
)

if (-not $StatusFile) { $StatusFile = Join-Path (Get-Location).Path "build-exit.txt" }
$StatusFile = [System.IO.Path]::GetFullPath($StatusFile)
$Script = (Resolve-Path -LiteralPath $Script).Path

$ErrorActionPreference = "Continue"
$exitCode = 0

try {
    & $Script
    if ($LASTEXITCODE) { $exitCode = $LASTEXITCODE }
}
catch {
    Write-Host "[!] build failed: $($_.Exception.Message)"
    $exitCode = 1
}

Set-Content -Path $StatusFile -Value $exitCode
Write-Host "[!] build exit status: $exitCode"
