# App Factory v2 — start the brain loop (Windows).
# Usage:  .\scripts\run_brain.ps1            (loop forever, 30-min cycles)
#         .\scripts\run_brain.ps1 --once     (single cycle)
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
python -m brain.brain @args
