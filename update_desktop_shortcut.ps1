$icoPath = "C:\Users\nnoub\.gemini\antigravity\scratch\keyboard-arabic-converter\app_icon.ico"
$destExe = "C:\Users\nnoub\.gemini\antigravity\scratch\keyboard-arabic-converter\dist\Faseeh-ArabicKeyFix.exe"
$desktop = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop)
$shortcutPath = Join-Path $desktop "Faseeh - ArabicKeyFix.lnk"

# Remove old shortcut if exists
if (Test-Path $shortcutPath) {
    Remove-Item $shortcutPath -Force
}

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = $destExe
$Shortcut.WorkingDirectory = "C:\Users\nnoub\.gemini\antigravity\scratch\keyboard-arabic-converter\dist"
$Shortcut.IconLocation = "$icoPath,0"
$Shortcut.Description = "فصيح - مصحح الكيبورد الذكي"
$Shortcut.Save()

Write-Host "Created new shortcut with Feather Icon at:" $shortcutPath

# Refresh Windows Shell Icon Cache
try {
    [Windows.Storage.StorageFile] | Out-Null
    ie4uinit.exe -show
} catch {}
