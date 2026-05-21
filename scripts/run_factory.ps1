# App Factory v2 — claim the next spec for the factory (Windows).
# Code generation is done by a Claude Code worker session inside the
# scaffolded workspace; this only scaffolds + reports.
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$ws = python -m factory.factory claim
Write-Output ""
Write-Output "Workspace scaffolded: $ws"
Write-Output "Run a Claude Code factory worker inside it, then:"
Write-Output "  python -m factory.factory complete <workspace_id>"
