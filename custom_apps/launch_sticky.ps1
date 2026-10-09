<#
.SYNOPSIS
    Open kænbæn and local_agent custom apps in Windows Postit (Sticky Notes)
.DESCRIPTION
    Copies the custom_apps HTML files into Sticky Notes LocalState and launches Sticky Notes.
    The files persist in LocalState\ and survive app restarts.
.EXAMPLE
    powershell -NoProfile -ExecutionPolicy Bypass -File custom_apps\launch_sticky.ps1
#>
$ErrorActionPreference = "Stop"

$repo = "C:\Users\yaelm\vscode\aeaedotcom"
$snPkg = "C:\Users\yaelm\AppData\Local\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe"
$snLocal = Join-Path $snPkg "LocalState"

# Files to copy
$files = @(
    (Join-Path $repo "custom_apps\kabban-board.html"),
    (Join-Path $repo "custom_apps\local_agent.html")
)

foreach ($f in $files) {
    if (-not (Test-Path $f)) {
        Write-Host "MISSING: $f" -ForegroundColor Red
        continue
    }
    $dest = Join-Path $snLocal (Split-Path $f -Leaf)
    Copy-Item $f $dest -Force
    $bytes = (Get-Item $dest).Length
    Write-Host "Copied: $($f.Split('\')[-1]) -> $dest ($bytes bytes)" -ForegroundColor Green
}

# Launch Sticky Notes
$sn = Get-Process -Name "StickyNotes" -ErrorAction SilentlyContinue
if (-not $sn) {
    Start-Process "shell:AppsFolder\Microsoft.MicrosoftStickyNotes_4.0.6104.0_x64__8wekyb3d8bbwe"
    Start-Sleep -Seconds 2
}
Write-Host "Done. Sticky Notes LocalState now contains:" -ForegroundColor Cyan
Get-ChildItem (Join-Path $snLocal "*.html") | ForEach-Object { Write-Host "  $($_.Name) ($($_.Length) bytes)" }
