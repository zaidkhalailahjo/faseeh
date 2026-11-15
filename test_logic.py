# -*- coding: utf-8 -*-
"""
Test hotkey and clipboard replacement mechanics
"""
import time
import pyperclip
import pyautogui
from converter import fix_text

def perform_conversion():
    # Save current clipboard
    old_clipboard = ""
    try:
        old_clipboard = pyperclip.paste()
    except Exception:
        pass

    # Clear clipboard to detect if copy succeeds
    pyperclip.copy("")
    time.sleep(0.05)

    # Trigger Ctrl+C
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.1)

    copied = pyperclip.paste()
    if not copied:
        print("Nothing copied!")
        return

    print(f"Original: {copied}")
    fixed = fix_text(copied)
    print(f"Fixed: {fixed}")

    if fixed != copied:
        pyperclip.copy(fixed)
        time.sleep(0.05)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.05)
        print("Replaced successfully!")
    else:
        print("No change needed.")

if __name__ == '__main__':
    print("Testing converter logic...")
    sample = ";dt phg;"
    pyperclip.copy(sample)
    print("Clipboard set to:", pyperclip.paste())
    print("Fixed:", fix_text(pyperclip.paste()))
