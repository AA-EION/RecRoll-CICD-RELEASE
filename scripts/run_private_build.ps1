<#
.SYNOPSIS
    Runs one of the private repository's build scripts and records its exit
    status in a file.

.DESCRIPTION
    The build's output has to be piped through scripts/redact_log.py, and a
    PowerShell pipeline reports the exit status of the *last* command in it -
    the redactor, which always succeeds. Piping the build directly would
    therefore turn every build failure into a green job.

    So the build runs as a child process whose status is written to
    build-exit.txt, and the workflow reads that file after the pipeline drains.

.PARAMETER Script
    Path to the build script to run, e.g. src/ci/build_windows.ps1.

.PARAMETER StatusFile
    Where to record the exit status. Defaults to build-exit.txt in the working
    directory as it stands when this script starts.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Script,
    [string]$StatusFile
)

# Both paths are resolved to absolute form BEFORE the build runs. The build
# script calls Set-Location to the private source root, which changes this
# session's working directory too - so a relative status path would be written
# inside src/, where the workflow does not look for it and where the source
# cleanup then deletes it. That turned a fully successful 21-minute Windows
# build into a reported failure.
if (-not $StatusFile) { $StatusFile = Join-Path (Get-Location).Path "build-exit.txt" }
$StatusFile = [System.IO.Path]::GetFullPath($StatusFile)
$Script = (Resolve-Path -LiteralPath $Script).Path

# Continue, not Stop: a failure has to be recorded, not thrown away by this
# wrapper terminating before it writes the file.
$ErrorActionPreference = "Continue"
$exitCode = 0

try {
    & $Script
    if ($LASTEXITCODE) { $exitCode = $LASTEXITCODE }
}
catch {
    # "[!]" is one of the prefixes the redactor passes through, so the reason
    # survives into the public log. The scripts throw their own messages; a
    # runtime exception message may be terser but never quotes source.
    Write-Host "[!] build failed: $($_.Exception.Message)"
    $exitCode = 1
}

Set-Content -Path $StatusFile -Value $exitCode
Write-Host "[!] build exit status: $exitCode (recorded in $StatusFile)"
