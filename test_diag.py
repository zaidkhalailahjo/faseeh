import time
import pyperclip
import pyautogui
import keyboard

print("Diagnostic listener ready.")
print("Testing with hotkey ctrl+q. Press Ctrl+Q anywhere to test...")

def on_press():
    print("HOTKEY TRIGGERED!")
    time.sleep(0.3) # wait for physical key release
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.1)
    txt = pyperclip.paste()
    print(f"Copied text: [{txt}]")

keyboard.add_hotkey('ctrl+q', on_press)
print("Listening for 5 seconds...")
# keep alive 5 seconds
time.sleep(5)
keyboard.unhook_all()
print("Done test.")
