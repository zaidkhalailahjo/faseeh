# -*- coding: utf-8 -*-
"""
Arabic Keyboard Fixer (فَصِيح) - Version 4.0 Auto-Updater & Ultra UI Edition
Features:
- Seamless In-App Auto-Updater (Check, Download & Swap EXE)
- Premium Dark Modern Bento-Grid UI
- Exact Time Breakdown (ساعات، دقائق، ثواني)
- Sleek Keycap Badges: [Ctrl+Shift+A], [Alt+Q], [F9]
- Persistent AppData storage
- Windows Startup integration with toggle
- Native Windows keyboard hook & sound
"""

import sys
import os
import json
import time
import urllib.request
import ctypes
import winsound
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import pyperclip
import keyboard

from converter import fix_text, is_mostly_arabic

CURRENT_VERSION = "1.0.0"
UPDATE_CHECK_URL = "https://raw.githubusercontent.com/zaidkhalailahjo/faseeh/main/version.json"

# Set Windows AppUserModelID for dedicated Taskbar icon
try:
    myappid = 'faseeh.keyboard.fixer.v4'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

# Native Windows API setup
user32 = ctypes.windll.user32
VK_CONTROL = 0x11
VK_SHIFT = 0x10
VK_MENU = 0x12
VK_C = 0x43
VK_V = 0x56
VK_HOME = 0x24
VK_Q = 0x51
VK_A = 0x41
KEYEVENTF_KEYUP = 0x0002


def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


DATA_FILE = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "Faseeh_Data.json")
STARTUP_FOLDER = os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs\Startup")
STARTUP_SHORTCUT = os.path.join(STARTUP_FOLDER, "Faseeh.lnk")


def load_user_data():
    default_data = {
        "rescues_count": 0,
        "seconds_saved": 0.0,
        "autostart": True
    }
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                default_data.update(data)
        except Exception:
            pass
    return default_data


def save_user_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def set_autostart(enable: bool):
    target_exe = sys.executable
    if not target_exe.lower().endswith("faseeh-arabickeyfix.exe"):
        candidate = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist", "Faseeh-ArabicKeyFix.exe")
        if os.path.exists(candidate):
            target_exe = candidate
        else:
            target_exe = sys.executable

    if enable:
        ps_cmd = (
            f"$WshShell = New-Object -ComObject WScript.Shell; "
            f"$Shortcut = $WshShell.CreateShortcut('{STARTUP_SHORTCUT}'); "
            f"$Shortcut.TargetPath = '{target_exe}'; "
            f"$Shortcut.WorkingDirectory = '{os.path.dirname(target_exe)}'; "
            f"$Shortcut.IconLocation = '{target_exe},0'; "
            f"$Shortcut.Description = 'فصيح - مصحح الكيبورد الذكي'; "
            f"$Shortcut.Save()"
        )
        os.system(f'powershell -Command "{ps_cmd}"')
    else:
        if os.path.exists(STARTUP_SHORTCUT):
            try:
                os.remove(STARTUP_SHORTCUT)
            except Exception:
                pass


def is_autostart_enabled():
    return os.path.exists(STARTUP_SHORTCUT)


def format_time_saved(seconds):
    seconds = int(round(seconds))
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60

    parts = []
    if h > 0:
        parts.append(f"{h} ساعة")
    if m > 0:
        parts.append(f"{m} دقيقة")
    if s > 0 or len(parts) == 0:
        parts.append(f"{s} ثانية")

    return " و ".join(parts)


def parse_version(v_str):
    """Convert version string like '1.0.5' into comparable tuple (1, 0, 5)."""
    try:
        clean = v_str.strip().lstrip("vV")
        return tuple(map(int, clean.split(".")))
    except Exception:
        return (0, 0, 0)


def apply_update_and_restart(new_exe_path):
    """Seamlessly replaces the current running EXE with the new EXE and restarts."""
    target_exe = sys.executable
    if not target_exe.lower().endswith(".exe"):
        target_exe = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist", "Faseeh-ArabicKeyFix.exe")

    updater_bat = os.path.join(os.environ.get("TEMP", "."), "faseeh_updater.bat")
    with open(updater_bat, "w", encoding="utf-8") as f:
        f.write(f"""@echo off
timeout /t 1 /nobreak >nul
move /y "{new_exe_path}" "{target_exe}"
start "" "{target_exe}"
del "%~f0"
""")
    ctypes.windll.shell32.ShellExecuteW(None, "open", updater_bat, None, None, 0)
    sys.exit(0)


def release_modifiers():
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_SHIFT, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_Q, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_A, 0, KEYEVENTF_KEYUP, 0)


def send_copy():
    release_modifiers()
    time.sleep(0.04)
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    user32.keybd_event(VK_C, 0, 0, 0)
    time.sleep(0.04)
    user32.keybd_event(VK_C, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)


def send_paste():
    release_modifiers()
    time.sleep(0.04)
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    user32.keybd_event(VK_V, 0, 0, 0)
    time.sleep(0.04)
    user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)


def send_select_line_to_cursor():
    release_modifiers()
    time.sleep(0.04)
    user32.keybd_event(VK_SHIFT, 0, 0, 0)
    user32.keybd_event(VK_HOME, 0, 0, 0)
    time.sleep(0.04)
    user32.keybd_event(VK_HOME, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_SHIFT, 0, KEYEVENTF_KEYUP, 0)


def get_clipboard_text(timeout=0.35):
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


class FloatingToast:
    @staticmethod
    def show(message, title="فَصِيح ✨"):
        def _run():
            try:
                toast = tk.Tk()
                toast.overrideredirect(True)
                toast.attributes("-topmost", True)
                toast.attributes("-alpha", 0.95)
                toast.configure(bg="#0B0F19")

                sw = toast.winfo_screenwidth()
                sh = toast.winfo_screenheight()

                width = 330
                height = 80
                x = sw - width - 25
                y = sh - height - 60
                toast.geometry(f"{width}x{height}+{x}+{y}")

                border_frame = tk.Frame(toast, bg="#1E293B", padx=1, pady=1)
                border_frame.pack(fill=tk.BOTH, expand=True)

                inner = tk.Frame(border_frame, bg="#0B0F19", padx=12, pady=8)
                inner.pack(fill=tk.BOTH, expand=True)

                title_lbl = tk.Label(
                    inner, text=title, font=("Segoe UI", 10, "bold"),
                    fg="#38BDF8", bg="#0B0F19"
                )
                title_lbl.pack(anchor="e")

                msg_lbl = tk.Label(
                    inner, text=message, font=("Segoe UI", 9),
                    fg="#F8FAFC", bg="#0B0F19", wraplength=300, justify=tk.RIGHT
                )
                msg_lbl.pack(anchor="e", pady=(2, 0))

                toast.after(2300, toast.destroy)
                toast.mainloop()
            except Exception:
                pass

        threading.Thread(target=_run, daemon=True).start()


class KeyboardFixerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("فَصِيح - مصحح الكيبورد الذكي")
        self.root.geometry("580x640")
        self.root.resizable(False, False)

        # Theme Colors
        self.BG_MAIN = "#0B0F19"
        self.BG_CARD = "#131C2E"
        self.BG_CARD_SUB = "#1B273F"
        self.BORDER_COLOR = "#25334D"
        self.TEXT_PRIMARY = "#FFFFFF"
        self.TEXT_SECONDARY = "#94A3B8"
        self.ACCENT_BLUE = "#3B82F6"
        self.ACCENT_CYAN = "#38BDF8"
        self.ACCENT_GREEN = "#10B981"

        self.user_data = load_user_data()
        self.rescues_count = self.user_data.get("rescues_count", 0)
        self.seconds_saved = self.user_data.get("seconds_saved", 0.0)

        self._apply_icons()

        self.is_active = True
        self.is_processing = False

        self._setup_ui()
        self._register_hotkeys()

        if self.user_data.get("autostart", True) and not is_autostart_enabled():
            set_autostart(True)

        # Silent background update check after 4 seconds
        self.root.after(4000, lambda: threading.Thread(target=self._check_update_task, args=(False,), daemon=True).start())

    def _apply_icons(self):
        ico_file = get_resource_path("app_icon.ico")
        png_file = get_resource_path("app_icon.png")

        if os.path.exists(ico_file):
            try:
                self.root.iconbitmap(ico_file)
            except Exception:
                pass

        if os.path.exists(png_file):
            try:
                icon_img = ImageTk.PhotoImage(file=png_file)
                self.root.iconphoto(True, icon_img)
                self.logo_photo = icon_img
            except Exception:
                self.logo_photo = None
        else:
            self.logo_photo = None

    def _setup_ui(self):
        self.root.configure(bg=self.BG_MAIN)

        # ----------------- 1. HEADER -----------------
        header = tk.Frame(self.root, bg=self.BG_CARD, padx=22, pady=14)
        header.pack(fill=tk.X)

        sep = tk.Frame(self.root, bg=self.BORDER_COLOR, height=1)
        sep.pack(fill=tk.X)

        self.status_badge = tk.Label(
            header,
            text="● نَشِط في الخلفية",
            font=("Segoe UI", 9, "bold"),
            fg=self.ACCENT_GREEN,
            bg="#064E3B",
            padx=10,
            pady=4
        )
        self.status_badge.pack(side=tk.LEFT)

        header_right = tk.Frame(header, bg=self.BG_CARD)
        header_right.pack(side=tk.RIGHT)

        title_texts = tk.Frame(header_right, bg=self.BG_CARD)
        title_texts.pack(side=tk.RIGHT, padx=(0, 10))

        title_lbl = tk.Label(
            title_texts,
            text="فَصِـــيح",
            font=("Segoe UI", 18, "bold"),
            fg=self.TEXT_PRIMARY,
            bg=self.BG_CARD
        )
        title_lbl.pack(anchor="e")

        sub_lbl = tk.Label(
            title_texts,
            text="المساعد الذكي لتصحيح لغة الكيبورد",
            font=("Segoe UI", 9),
            fg=self.TEXT_SECONDARY,
            bg=self.BG_CARD
        )
        sub_lbl.pack(anchor="e")

        if hasattr(self, 'logo_photo') and self.logo_photo:
            try:
                img_raw = Image.open(get_resource_path("app_icon.png")).resize((48, 48), Image.Resampling.LANCZOS)
                self.logo_head = ImageTk.PhotoImage(img_raw)
                logo_lbl = tk.Label(header_right, image=self.logo_head, bg=self.BG_CARD)
                logo_lbl.pack(side=tk.RIGHT)
            except Exception:
                pass

        # ----------------- 2. MAIN BODY -----------------
        body = tk.Frame(self.root, bg=self.BG_MAIN, padx=22, pady=14)
        body.pack(fill=tk.BOTH, expand=True)

        # ----------------- 3. ANALYTICS BENTO CARDS -----------------
        stats_frame = tk.Frame(body, bg=self.BG_MAIN)
        stats_frame.pack(fill=tk.X, pady=(0, 12))

        # Card 1: Rescue Count
        c1 = tk.Frame(stats_frame, bg=self.BG_CARD, bd=1, relief=tk.SOLID, padx=14, pady=10)
        c1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))

        c1_head = tk.Label(c1, text="🛡️ مرات الإنقاذ", font=("Segoe UI", 9, "bold"), fg=self.ACCENT_CYAN, bg=self.BG_CARD)
        c1_head.pack(anchor="center")

        self.c1_val = tk.Label(
            c1,
            text=f"{self.rescues_count} مرة",
            font=("Segoe UI", 18, "bold"),
            fg=self.TEXT_PRIMARY,
            bg=self.BG_CARD
        )
        self.c1_val.pack(anchor="center", pady=(3, 1))

        c1_sub = tk.Label(c1, text="تصحيح فوري دون مسح", font=("Segoe UI", 8), fg=self.TEXT_SECONDARY, bg=self.BG_CARD)
        c1_sub.pack(anchor="center")

        # Card 2: Time Saved (Hours, Minutes, Seconds)
        c2 = tk.Frame(stats_frame, bg=self.BG_CARD, bd=1, relief=tk.SOLID, padx=14, pady=10)
        c2.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(6, 0))

        c2_head = tk.Label(c2, text="⏱️ الوقت الموفّر", font=("Segoe UI", 9, "bold"), fg=self.ACCENT_GREEN, bg=self.BG_CARD)
        c2_head.pack(anchor="center")

        self.c2_val = tk.Label(
            c2,
            text=format_time_saved(self.seconds_saved),
            font=("Segoe UI", 13, "bold"),
            fg=self.TEXT_PRIMARY,
            bg=self.BG_CARD
        )
        self.c2_val.pack(anchor="center", pady=(5, 1))

        c2_sub = tk.Label(c2, text="ساعات • دقائق • ثواني", font=("Segoe UI", 8), fg=self.TEXT_SECONDARY, bg=self.BG_CARD)
        c2_sub.pack(anchor="center")

        # ----------------- 4. VISUAL KEYCAP CHIPS -----------------
        chips_card = tk.Frame(body, bg=self.BG_CARD, bd=1, relief=tk.SOLID, padx=16, pady=10)
        chips_card.pack(fill=tk.X, pady=(0, 12))

        chips_title = tk.Label(
            chips_card,
            text="⚡ الاختصارات المعتمدة لتصحيح أي نص مظلل في جهازك:",
            font=("Segoe UI", 9, "bold"),
            fg=self.TEXT_PRIMARY,
            bg=self.BG_CARD
        )
        chips_title.pack(anchor="e", pady=(0, 6))

        chips_row = tk.Frame(chips_card, bg=self.BG_CARD)
        chips_row.pack(fill=tk.X)

        chip1 = tk.Frame(chips_row, bg=self.BG_CARD_SUB, padx=8, pady=3, relief=tk.RIDGE, bd=1)
        chip1.pack(side=tk.RIGHT, padx=4)
        tk.Label(chip1, text="Ctrl + Shift + A", font=("Consolas", 10, "bold"), fg="#38BDF8", bg=self.BG_CARD_SUB).pack()

        chip2 = tk.Frame(chips_row, bg=self.BG_CARD_SUB, padx=8, pady=3, relief=tk.RIDGE, bd=1)
        chip2.pack(side=tk.RIGHT, padx=4)
        tk.Label(chip2, text="Alt + Q", font=("Consolas", 10, "bold"), fg="#A78BFA", bg=self.BG_CARD_SUB).pack()

        chip3 = tk.Frame(chips_row, bg=self.BG_CARD_SUB, padx=8, pady=3, relief=tk.RIDGE, bd=1)
        chip3.pack(side=tk.RIGHT, padx=4)
        tk.Label(chip3, text="F9", font=("Consolas", 10, "bold"), fg="#34D399", bg=self.BG_CARD_SUB).pack()

        # ----------------- 5. INTERACTIVE LIVE TEST ZONE -----------------
        test_frame = tk.LabelFrame(
            body,
            text="  جرب التصحيح المباشر هنا  ",
            font=("Segoe UI", 9, "bold"),
            fg=self.ACCENT_CYAN,
            bg=self.BG_MAIN,
            padx=14,
            pady=8
        )
        test_frame.pack(fill=tk.X, pady=(0, 12))

        self.test_entry = tk.Entry(
            test_frame,
            font=("Segoe UI", 12),
            justify=tk.CENTER,
            bg="#1E293B",
            fg="#FFFFFF",
            insertbackground="#38BDF8",
            relief=tk.FLAT,
            bd=5
        )
        self.test_entry.insert(0, ";dt phg;")
        self.test_entry.pack(fill=tk.X, pady=(2, 6))
        self.test_entry.bind("<Return>", lambda e: self._convert_test_box())

        btn_row = tk.Frame(test_frame, bg=self.BG_MAIN)
        btn_row.pack(fill=tk.X)

        test_btn = tk.Button(
            btn_row,
            text="✨ تحويل فوري (Enter)",
            font=("Segoe UI", 9, "bold"),
            bg="#2563EB",
            fg="#FFFFFF",
            activebackground="#1D4ED8",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            padx=14,
            pady=4,
            cursor="hand2",
            command=self._convert_test_box
        )
        test_btn.pack(side=tk.LEFT, padx=(0, 8))

        clear_btn = tk.Button(
            btn_row,
            text="مسح",
            font=("Segoe UI", 9),
            bg="#1E293B",
            fg=self.TEXT_SECONDARY,
            relief=tk.FLAT,
            padx=10,
            pady=4,
            cursor="hand2",
            command=lambda: self.test_entry.delete(0, tk.END)
        )
        clear_btn.pack(side=tk.LEFT)

        # ----------------- 6. AUTOSTART & UPDATES BAR -----------------
        settings_box = tk.Frame(body, bg=self.BG_CARD, bd=1, relief=tk.SOLID, padx=14, pady=8)
        settings_box.pack(fill=tk.X, pady=(0, 12))

        self.autostart_var = tk.BooleanVar(value=is_autostart_enabled())

        autostart_chk = tk.Checkbutton(
            settings_box,
            text=" تشغيل «فَصِيح» تلقائياً عند فتح اللابتوب (Run at Startup)",
            variable=self.autostart_var,
            font=("Segoe UI", 9, "bold"),
            fg=self.TEXT_PRIMARY,
            bg=self.BG_CARD,
            activebackground=self.BG_CARD,
            activeforeground=self.ACCENT_CYAN,
            selectcolor="#1E293B",
            command=self._toggle_autostart
        )
        autostart_chk.pack(anchor="w")

        # ----------------- 7. FOOTER CONTROLS -----------------
        footer = tk.Frame(body, bg=self.BG_MAIN)
        footer.pack(fill=tk.X, side=tk.BOTTOM)

        # Check update button (Left)
        self.update_btn = tk.Button(
            footer,
            text=f"🔄 فحص التحديثات (v{CURRENT_VERSION})",
            font=("Segoe UI", 8, "bold"),
            bg="#1E293B",
            fg=self.ACCENT_CYAN,
            relief=tk.FLAT,
            padx=10,
            pady=4,
            cursor="hand2",
            command=lambda: threading.Thread(target=self._check_update_task, args=(True,), daemon=True).start()
        )
        self.update_btn.pack(side=tk.LEFT)

        # Minimize & Toggle (Right)
        self.toggle_btn = tk.Button(
            footer,
            text="⏸️ إيقاف مؤقت",
            font=("Segoe UI", 9),
            bg=self.BG_CARD,
            fg=self.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=10,
            pady=4,
            command=self._toggle_service
        )
        self.toggle_btn.pack(side=tk.RIGHT)

        min_btn = tk.Button(
            footer,
            text="🔽 تصغير للشريط",
            font=("Segoe UI", 9),
            bg=self.BG_CARD,
            fg=self.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=10,
            pady=4,
            command=self.root.iconify
        )
        min_btn.pack(side=tk.RIGHT, padx=6)

    def _toggle_autostart(self):
        enabled = self.autostart_var.get()
        set_autostart(enabled)
        self.user_data["autostart"] = enabled
        save_user_data(self.user_data)
        if enabled:
            FloatingToast.show("تم تفعيل التشغيل التلقائي عند فتح اللابتوب", "فَصِيح 🚀")
        else:
            FloatingToast.show("تم إيقاف التشغيل التلقائي مع فتح الجهاز", "فَصِيح ⏸️")

    def _convert_test_box(self):
        txt = self.test_entry.get()
        if txt:
            fixed = fix_text(txt)
            self.test_entry.delete(0, tk.END)
            self.test_entry.insert(0, fixed)
            self._record_rescue(len(txt))
            FloatingToast.show(f"تم التحويل إلى:\n{fixed}")

    def _record_rescue(self, char_count):
        self.rescues_count += 1
        saved_delta = round(3.5 + (char_count * 0.22), 1)
        self.seconds_saved += saved_delta

        self.user_data["rescues_count"] = self.rescues_count
        self.user_data["seconds_saved"] = self.seconds_saved
        save_user_data(self.user_data)

        self.c1_val.config(text=f"{self.rescues_count} مرة")
        self.c2_val.config(text=format_time_saved(self.seconds_saved))

    def _toggle_service(self):
        self.is_active = not self.is_active
        if self.is_active:
            self.status_badge.config(text="● نَشِط في الخلفية", fg=self.ACCENT_GREEN, bg="#064E3B")
            self.toggle_btn.config(text="⏸️ إيقاف مؤقت")
            FloatingToast.show("تم استئناف عمل مصحح الكيبورد", "فَصِيح 🟢")
        else:
            self.status_badge.config(text="● متوقف مؤقتاً", fg="#EF4444", bg="#450A0A")
            self.toggle_btn.config(text="▶️ تشغيل")
            FloatingToast.show("تم إيقاف الأداة مؤقتاً", "فَصِيح 🔴")

    def _register_hotkeys(self):
        try:
            keyboard.add_hotkey('ctrl+shift+a', self._trigger_hotkey, suppress=False)
            keyboard.add_hotkey('alt+q', self._trigger_hotkey, suppress=False)
            keyboard.add_hotkey('f9', self._trigger_hotkey, suppress=False)
            print("Registered: Ctrl+Shift+A, Alt+Q, F9.")
        except Exception as e:
            print(f"Error registering hotkeys: {e}")

    def _trigger_hotkey(self):
        if not self.is_active or self.is_processing:
            return
        threading.Thread(target=self._execute_replacement, daemon=True).start()

    def _execute_replacement(self):
        self.is_processing = True
        try:
            time.sleep(0.18)

            saved_clip = ""
            try:
                saved_clip = pyperclip.paste()
            except Exception:
                pass

            pyperclip.copy("")
            time.sleep(0.04)

            send_copy()
            copied = get_clipboard_text(timeout=0.3)

            if not copied:
                send_select_line_to_cursor()
                time.sleep(0.04)
                send_copy()
                copied = get_clipboard_text(timeout=0.3)

            if not copied:
                if saved_clip:
                    pyperclip.copy(saved_clip)
                FloatingToast.show("الرجاء تظليل النص أولاً ثم ضغط الاختصار", "تنبيه ⚠️")
                return

            fixed = fix_text(copied)

            if fixed and fixed != copied:
                pyperclip.copy(fixed)
                time.sleep(0.05)
                send_paste()

                try:
                    winsound.MessageBeep(winsound.MB_OK)
                except Exception:
                    pass

                self.root.after(0, lambda: self._record_rescue(len(copied)))

                preview = (fixed[:35] + "...") if len(fixed) > 35 else fixed
                FloatingToast.show(f"تم التصحيح بنجاح:\n{preview}", "فَصِيح ✨")
            else:
                FloatingToast.show("النص لا يحتاج إلى تعديل", "فَصِيح")
                if saved_clip:
                    pyperclip.copy(saved_clip)

        except Exception as err:
            print(f"Error during replacement: {err}")
        finally:
            self.is_processing = False

    # ----------------- AUTO-UPDATER ENGINE -----------------
    def _check_update_task(self, manual=False):
        try:
            if manual:
                self.update_btn.config(text="⏳ جاري الفحص...")

            req = urllib.request.Request(UPDATE_CHECK_URL, headers={'User-Agent': 'Faseeh-Updater'})
            with urllib.request.urlopen(req, timeout=4) as response:
                data = json.loads(response.read().decode('utf-8'))

            remote_ver_str = data.get("version", "1.0.0")
            download_url = data.get("download_url", "")
            notes = data.get("release_notes", "تحسينات عامة وإصلاحات.")

            if parse_version(remote_ver_str) > parse_version(CURRENT_VERSION):
                # New update found!
                self.root.after(0, lambda: self._prompt_update_modal(remote_ver_str, download_url, notes))
            else:
                if manual:
                    self.root.after(0, lambda: messagebox.showinfo(
                        "فَصِيح - التحديثات",
                        f"أنت تستخدم أحدث إصدار بالفعل (v{CURRENT_VERSION})! ✨\nلا توجد تحديثات جديدة حالياً."
                    ))
        except Exception:
            if manual:
                self.root.after(0, lambda: messagebox.showinfo(
                    "فَصِيح - التحديثات",
                    f"الإصدار المثبت: v{CURRENT_VERSION}\n\n(ملاحظة: خادم التحديثات السحابي جاهز وسيعمل فور رفع ملف version.json على مستودعك على الإنترنت)."
                ))
        finally:
            if manual:
                self.root.after(0, lambda: self.update_btn.config(text=f"🔄 فحص التحديثات (v{CURRENT_VERSION})"))

    def _prompt_update_modal(self, new_ver, dl_url, notes):
        modal = tk.Toplevel(self.root)
        modal.title(f"تحديث جديد متاح: v{new_ver}")
        modal.geometry("440x260")
        modal.resizable(False, False)
        modal.configure(bg=self.BG_MAIN)
        modal.transient(self.root)
        modal.grab_set()

        head = tk.Label(
            modal, text=f"🎉 يتوفر إصدار جديد من فَصِيح (v{new_ver})",
            font=("Segoe UI", 12, "bold"), fg=self.ACCENT_CYAN, bg=self.BG_MAIN
        )
        head.pack(pady=(16, 8))

        notes_box = tk.Label(
            modal, text=f"ما الجديد في هذا التحديث:\n{notes}",
            font=("Segoe UI", 9), fg=self.TEXT_SECONDARY, bg=self.BG_MAIN,
            wraplength=380, justify=tk.RIGHT
        )
        notes_box.pack(pady=(0, 16), padx=20)

        status_lbl = tk.Label(modal, text="", font=("Segoe UI", 9), fg=self.ACCENT_GREEN, bg=self.BG_MAIN)
        status_lbl.pack(pady=(0, 10))

        btn_row = tk.Frame(modal, bg=self.BG_MAIN)
        btn_row.pack(side=tk.BOTTOM, pady=16)

        def _start_download():
            status_lbl.config(text="⏳ جاري تحميل وتثبيت التحديث تلقائياً...")
            dl_btn.config(state=tk.DISABLED)

            def _dl_worker():
                try:
                    temp_dir = os.environ.get("TEMP", ".")
                    new_file = os.path.join(temp_dir, f"Faseeh_{new_ver}.exe")
                    urllib.request.urlretrieve(dl_url, new_file)
                    status_lbl.config(text="✅ اكتمل التحميل! جاري إعادة التشغيل...")
                    time.sleep(0.8)
                    apply_update_and_restart(new_file)
                except Exception as e:
                    status_lbl.config(text=f"❌ تعذر التحميل: {e}")
                    dl_btn.config(state=tk.NORMAL)

            threading.Thread(target=_dl_worker, daemon=True).start()

        dl_btn = tk.Button(
            btn_row, text="🚀 تحديث وتثبيت الآن",
            font=("Segoe UI", 9, "bold"), bg="#2563EB", fg="#FFFFFF",
            relief=tk.FLAT, padx=14, pady=6, cursor="hand2",
            command=_start_download
        )
        dl_btn.pack(side=tk.LEFT, padx=6)

        cancel_btn = tk.Button(
            btn_row, text="لاحقاً",
            font=("Segoe UI", 9), bg="#1E293B", fg=self.TEXT_SECONDARY,
            relief=tk.FLAT, padx=12, pady=6, cursor="hand2",
            command=modal.destroy
        )
        cancel_btn.pack(side=tk.LEFT)


def main():
    root = tk.Tk()
    app = KeyboardFixerApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
