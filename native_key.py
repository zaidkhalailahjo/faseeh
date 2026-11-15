# -*- coding: utf-8 -*-
import ctypes
import time
import pyperclip
from converter import fix_text

user32 = ctypes.windll.user32

# Virtual Key Codes
VK_CONTROL = 0x11
VK_SHIFT = 0x10
VK_C = 0x43
VK_V = 0x56
VK_HOME = 0x24
VK_Q = 0x51
KEYEVENTF_KEYUP = 0x0002

def release_all_modifiers():
    """Ensure modifier keys are physically released."""
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_SHIFT, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_Q, 0, KEYEVENTF_KEYUP, 0)

def send_copy():
    release_all_modifiers()
    time.sleep(0.02)
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    user32.keybd_event(VK_C, 0, 0, 0)
    time.sleep(0.03)
    user32.keybd_event(VK_C, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)

def send_paste():
    release_all_modifiers()
    time.sleep(0.02)
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    user32.keybd_event(VK_V, 0, 0, 0)
    time.sleep(0.03)
    user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)

def send_select_line_to_cursor():
    release_all_modifiers()
    time.sleep(0.02)
    user32.keybd_event(VK_SHIFT, 0, 0, 0)
    user32.keybd_event(VK_HOME, 0, 0, 0)
    time.sleep(0.03)
    user32.keybd_event(VK_HOME, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_SHIFT, 0, KEYEVENTF_KEYUP, 0)

def get_clipboard_text(timeout=0.3):
    start = time.time()
    while time.time() - start < timeout:
        try:
            txt = pyperclip.paste()
            if txt:
                return txt
        except Exception:
            pass
        time.sleep(0.03)
    return ""

print("Test harness loaded.")
