import os
import shutil
import winshell
from win32com.client import Dispatch

src_exe = r"C:\Users\nnoub\AppData\Local\Programs\Antigravity\dist\Faseeh-ArabicKeyFix.exe"
target_dir = r"C:\Users\nnoub\.gemini\antigravity\scratch\keyboard-arabic-converter\dist"
os.makedirs(target_dir, exist_ok=True)
dest_exe = os.path.join(target_dir, "Faseeh-ArabicKeyFix.exe")

if os.path.exists(src_exe):
    shutil.copy2(src_exe, dest_exe)
    print(f"Copied EXE to: {dest_exe}")

desktop = os.path.join(os.path.expanduser("~"), "Desktop")
shortcut_path = os.path.join(desktop, "فصيح - مصحح الكيبورد.lnk")

import win32com.client
shell = win32com.client.Dispatch("WScript.Shell")
shortcut = shell.CreateShortCut(shortcut_path)
shortcut.Targetpath = dest_exe
shortcut.WorkingDirectory = target_dir
shortcut.Description = "مصحح لوحة المفاتيح الذكي - اختصار Ctrl+Q"
shortcut.save()
print(f"Created desktop shortcut at: {shortcut_path}")
