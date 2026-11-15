$destExe = "C:\Users\nnoub\.gemini\antigravity\scratch\keyboard-arabic-converter\dist\Faseeh-ArabicKeyFix.exe"
$desktop = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop)
$shortcutPath = Join-Path $desktop "Faseeh - ArabicKeyFix.lnk"

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = $destExe
$Shortcut.WorkingDirectory = "C:\Users\nnoub\.gemini\antigravity\scratch\keyboard-arabic-converter\dist"
$Shortcut.IconLocation = "$destExe,0"
$Shortcut.Description = "فصيح - مصحح الكيبورد الذكي"
$Shortcut.Save()

Write-Host "Desktop shortcut icon configured:" $shortcutPath
