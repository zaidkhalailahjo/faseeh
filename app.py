# -*- coding: utf-8 -*-
"""
Arabic Keyboard Fixer (فَصِيح) - Version 1.2.0
Features:
- Real-Time Download Percentage & Progress Bar (نسبة مئوية رقمية وشريط تقدم دقيق)
- Modern Seamless UI/UX Edition (Clean, Borderless, Premium Dark Theme)
- Bento-Grid Analytics (ساعات، دقائق، ثواني)
- Visual Keycap Badges: [Ctrl+Shift+A], [Alt+Q], [F9]
- Auto-Updater with live MB tracking
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

CURRENT_VERSION = "1.4.0"
UPDATE_CHECK_URL = "https://raw.githubusercontent.com/zaidkhalailahjo/faseeh/main/version.json"

try:
    myappid = 'faseeh.keyboard.fixer.v1.4.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

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
    try:
        clean = v_str.strip().lstrip("vV")
        return tuple(map(int, clean.split(".")))
    except Exception:
        return (0, 0, 0)


def apply_update_and_restart(new_exe_path):
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
    _active_toast = None

    @staticmethod
    def show(message, title="فَصِيح ✨"):
        def _run():
            try:
                # Close any existing active toast cleanly
                if FloatingToast._active_toast:
                    try:
                        FloatingToast._active_toast.destroy()
                    except Exception:
                        pass

                toast = tk.Tk()
                FloatingToast._active_toast = toast
                toast.overrideredirect(True)
                toast.attributes("-topmost", True)
                toast.attributes("-alpha", 0.98)
                toast.configure(bg="#0F172A")

                sw = toast.winfo_screenwidth()
                sh = toast.winfo_screenheight()

                width = 350
                height = 92
                target_x = sw - width - 24
                hidden_x = sw + 10
                y = sh - height - 60

                # Start completely off-screen on the right for sliding entrance
                cur_x = hidden_x
                toast.geometry(f"{width}x{height}+{cur_x}+{y}")

                # Modern card container with subtle accent border
                border_frame = tk.Frame(toast, bg="#334155", padx=1, pady=1)
                border_frame.pack(fill=tk.BOTH, expand=True)

                inner = tk.Frame(border_frame, bg="#0F172A", padx=14, pady=9)
                inner.pack(fill=tk.BOTH, expand=True)

                # Header: Close button on Left, Title on Right
                top_bar = tk.Frame(inner, bg="#0F172A")
                top_bar.pack(fill=tk.X, pady=(0, 4))

                # Dismiss Button (✕)
                close_btn = tk.Label(
                    top_bar,
                    text="✕",
                    font=("Segoe UI", 9, "bold"),
                    fg="#94A3B8",
                    bg="#0F172A",
                    cursor="hand2",
                    padx=6,
                    pady=1
                )
                close_btn.pack(side=tk.LEFT)

                # Cyan Title
                title_lbl = tk.Label(
                    top_bar,
                    text=title,
                    font=("Segoe UI", 10, "bold"),
                    fg="#38BDF8",
                    bg="#0F172A"
                )
                title_lbl.pack(side=tk.RIGHT)

                # Message Body
                msg_lbl = tk.Label(
                    inner,
                    text=message,
                    font=("Segoe UI", 9),
                    fg="#F8FAFC",
                    bg="#0F172A",
                    wraplength=315,
                    justify=tk.RIGHT
                )
                msg_lbl.pack(fill=tk.BOTH, expand=True, anchor="e")

                # Animation State
                anim_state = {"cur_x": hidden_x, "closing": False, "timer_id": None}

                def _slide_out():
                    anim_state["closing"] = True
                    if anim_state["timer_id"]:
                        try:
                            toast.after_cancel(anim_state["timer_id"])
                        except Exception:
                            pass

                    # Slide back to the right off-screen
                    if anim_state["cur_x"] < hidden_x:
                        dist = hidden_x - anim_state["cur_x"]
                        step = max(5, int(max(dist, 10) * 0.28))
                        anim_state["cur_x"] += step
                        if anim_state["cur_x"] >= hidden_x:
                            try:
                                toast.destroy()
                            except Exception:
                                pass
                        else:
                            try:
                                toast.geometry(f"{width}x{height}+{anim_state['cur_x']}+{y}")
                                toast.after(12, _slide_out)
                            except Exception:
                                try:
                                    toast.destroy()
                                except Exception:
                                    pass
                    else:
                        try:
                            toast.destroy()
                        except Exception:
                            pass

                def _slide_in():
                    if anim_state["closing"]:
                        return
                    # Slide from the right into target position
                    if anim_state["cur_x"] > target_x:
                        dist = anim_state["cur_x"] - target_x
                        step = max(3, int(dist * 0.28))
                        anim_state["cur_x"] -= step
                        if anim_state["cur_x"] <= target_x:
                            anim_state["cur_x"] = target_x
                            try:
                                toast.geometry(f"{width}x{height}+{target_x}+{y}")
                                # Stay visible for 5 seconds (5000ms), then slide out
                                anim_state["timer_id"] = toast.after(5000, _slide_out)
                            except Exception:
                                pass
                        else:
                            try:
                                toast.geometry(f"{width}x{height}+{anim_state['cur_x']}+{y}")
                                toast.after(12, _slide_in)
                            except Exception:
                                pass
                    else:
                        anim_state["cur_x"] = target_x
                        try:
                            toast.geometry(f"{width}x{height}+{target_x}+{y}")
                            anim_state["timer_id"] = toast.after(5000, _slide_out)
                        except Exception:
                            pass

                # Close Button Hover and Click Effects
                def _on_hover_in(e):
                    close_btn.configure(fg="#EF4444", bg="#1E293B")

                def _on_hover_out(e):
                    close_btn.configure(fg="#94A3B8", bg="#0F172A")

                def _on_click_close(e):
                    _slide_out()

                close_btn.bind("<Enter>", _on_hover_in)
                close_btn.bind("<Leave>", _on_hover_out)
                close_btn.bind("<Button-1>", _on_click_close)

                # Start smooth slide-in immediately
                toast.after(10, _slide_in)
                toast.mainloop()
            except Exception:
                pass

        threading.Thread(target=_run, daemon=True).start()


class KeyboardFixerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("فَصِيح - مصحح الكيبورد الذكي")
        self.root.geometry("560x610")
        self.root.resizable(False, False)

        self.COLOR_BG = "#0B1120"
        self.COLOR_SURFACE = "#1E293B"
        self.COLOR_SURFACE_LIGHT = "#334155"
        self.COLOR_TEXT_MAIN = "#F8FAFC"
        self.COLOR_TEXT_MUTED = "#94A3B8"
        self.COLOR_PRIMARY = "#3B82F6"
        self.COLOR_PRIMARY_HOVER = "#2563EB"
        self.COLOR_CYAN = "#38BDF8"
        self.COLOR_EMERALD = "#10B981"
        self.COLOR_INDIGO = "#818CF8"

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
        self.root.configure(bg=self.COLOR_BG)

        # ----------------- 1. HEADER -----------------
        header = tk.Frame(self.root, bg=self.COLOR_BG, padx=26, pady=16)
        header.pack(fill=tk.X)

        self.status_chip = tk.Label(
            header,
            text="● نَشِط بالخلفية",
            font=("Segoe UI", 9, "bold"),
            fg=self.COLOR_EMERALD,
            bg="#064E3B",
            padx=12,
            pady=5,
            relief=tk.FLAT
        )
        self.status_chip.pack(side=tk.LEFT)

        brand_box = tk.Frame(header, bg=self.COLOR_BG)
        brand_box.pack(side=tk.RIGHT)

        text_col = tk.Frame(brand_box, bg=self.COLOR_BG)
        text_col.pack(side=tk.RIGHT, padx=(0, 10))

        title_lbl = tk.Label(
            text_col,
            text="فَصِـــيح",
            font=("Segoe UI", 18, "bold"),
            fg=self.COLOR_TEXT_MAIN,
            bg=self.COLOR_BG
        )
        title_lbl.pack(anchor="e")

        sub_lbl = tk.Label(
            text_col,
            text="المساعد الذكي للغة الكيبورد",
            font=("Segoe UI", 9),
            fg=self.COLOR_TEXT_MUTED,
            bg=self.COLOR_BG
        )
        sub_lbl.pack(anchor="e")

        if hasattr(self, 'logo_photo') and self.logo_photo:
            try:
                img_raw = Image.open(get_resource_path("app_icon.png")).resize((46, 46), Image.Resampling.LANCZOS)
                self.logo_head = ImageTk.PhotoImage(img_raw)
                logo_lbl = tk.Label(brand_box, image=self.logo_head, bg=self.COLOR_BG)
                logo_lbl.pack(side=tk.RIGHT)
            except Exception:
                pass

        # ----------------- 2. MAIN CONTAINER -----------------
        main_box = tk.Frame(self.root, bg=self.COLOR_BG, padx=26, pady=4)
        main_box.pack(fill=tk.BOTH, expand=True)

        # ----------------- 3. BENTO STATS CARDS -----------------
        stats_frame = tk.Frame(main_box, bg=self.COLOR_BG)
        stats_frame.pack(fill=tk.X, pady=(0, 16))

        # Card 1: Rescues
        c1 = tk.Frame(stats_frame, bg=self.COLOR_SURFACE, padx=16, pady=14)
        c1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        tk.Label(c1, text="مرات الإنقاذ 🛡️", font=("Segoe UI", 9, "bold"), fg=self.COLOR_CYAN, bg=self.COLOR_SURFACE).pack(anchor="center")
        self.c1_val = tk.Label(
            c1,
            text=f"{self.rescues_count} مرة",
            font=("Segoe UI", 20, "bold"),
            fg=self.COLOR_TEXT_MAIN,
            bg=self.COLOR_SURFACE
        )
        self.c1_val.pack(anchor="center", pady=(4, 2))
        tk.Label(c1, text="تصحيح فوري دون مسح", font=("Segoe UI", 8), fg=self.COLOR_TEXT_MUTED, bg=self.COLOR_SURFACE).pack(anchor="center")

        # Card 2: Time Saved
        c2 = tk.Frame(stats_frame, bg=self.COLOR_SURFACE, padx=16, pady=14)
        c2.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))

        tk.Label(c2, text="الوقت الموفّر ⏱️", font=("Segoe UI", 9, "bold"), fg=self.COLOR_EMERALD, bg=self.COLOR_SURFACE).pack(anchor="center")
        self.c2_val = tk.Label(
            c2,
            text=format_time_saved(self.seconds_saved),
            font=("Segoe UI", 13, "bold"),
            fg=self.COLOR_TEXT_MAIN,
            bg=self.COLOR_SURFACE
        )
        self.c2_val.pack(anchor="center", pady=(6, 2))
        tk.Label(c2, text="ساعات • دقائق • ثواني", font=("Segoe UI", 8), fg=self.COLOR_TEXT_MUTED, bg=self.COLOR_SURFACE).pack(anchor="center")

        # ----------------- 4. SHORTCUT PILLS -----------------
        shortcuts_card = tk.Frame(main_box, bg=self.COLOR_SURFACE, padx=18, pady=14)
        shortcuts_card.pack(fill=tk.X, pady=(0, 16))

        tk.Label(
            shortcuts_card,
            text="اختصارات التصحيح السريع في أي نافذة:",
            font=("Segoe UI", 9, "bold"),
            fg=self.COLOR_TEXT_MAIN,
            bg=self.COLOR_SURFACE
        ).pack(anchor="e", pady=(0, 8))

        pills_row = tk.Frame(shortcuts_card, bg=self.COLOR_SURFACE)
        pills_row.pack(fill=tk.X)

        p1 = tk.Label(pills_row, text="Ctrl + Shift + A", font=("Segoe UI", 10, "bold"), fg=self.COLOR_CYAN, bg=self.COLOR_SURFACE_LIGHT, padx=12, pady=5)
        p1.pack(side=tk.RIGHT, padx=4)

        p2 = tk.Label(pills_row, text="Alt + Q", font=("Segoe UI", 10, "bold"), fg=self.COLOR_INDIGO, bg=self.COLOR_SURFACE_LIGHT, padx=12, pady=5)
        p2.pack(side=tk.RIGHT, padx=4)

        p3 = tk.Label(pills_row, text="F9", font=("Segoe UI", 10, "bold"), fg=self.COLOR_EMERALD, bg=self.COLOR_SURFACE_LIGHT, padx=12, pady=5)
        p3.pack(side=tk.RIGHT, padx=4)

        # ----------------- 5. TEST ZONE -----------------
        test_card = tk.Frame(main_box, bg=self.COLOR_SURFACE, padx=18, pady=14)
        test_card.pack(fill=tk.X, pady=(0, 16))

        tk.Label(
            test_card,
            text="تجربة التحويل المباشر داخل التطبيق:",
            font=("Segoe UI", 9, "bold"),
            fg=self.COLOR_CYAN,
            bg=self.COLOR_SURFACE
        ).pack(anchor="e", pady=(0, 8))

        self.test_entry = tk.Entry(
            test_card,
            font=("Segoe UI", 12),
            justify=tk.CENTER,
            bg=self.COLOR_SURFACE_LIGHT,
            fg=self.COLOR_TEXT_MAIN,
            insertbackground=self.COLOR_CYAN,
            relief=tk.FLAT,
            bd=8
        )
        self.test_entry.insert(0, ";dt phg;")
        self.test_entry.pack(fill=tk.X, pady=(0, 10))
        self.test_entry.bind("<Return>", lambda e: self._convert_test_box())

        action_row = tk.Frame(test_card, bg=self.COLOR_SURFACE)
        action_row.pack(fill=tk.X)

        test_btn = tk.Button(
            action_row,
            text="✨ تحويل فوري (Enter)",
            font=("Segoe UI", 9, "bold"),
            bg=self.COLOR_PRIMARY,
            fg="#FFFFFF",
            activebackground=self.COLOR_PRIMARY_HOVER,
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            padx=16,
            pady=6,
            cursor="hand2",
            command=self._convert_test_box
        )
        test_btn.pack(side=tk.LEFT, padx=(0, 8))

        clear_btn = tk.Button(
            action_row,
            text="مسح",
            font=("Segoe UI", 9),
            bg=self.COLOR_SURFACE_LIGHT,
            fg=self.COLOR_TEXT_MUTED,
            activebackground="#475569",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            padx=14,
            pady=6,
            cursor="hand2",
            command=lambda: self.test_entry.delete(0, tk.END)
        )
        clear_btn.pack(side=tk.LEFT)

        # ----------------- 6. SETTINGS STRIP -----------------
        settings_strip = tk.Frame(main_box, bg=self.COLOR_SURFACE, padx=18, pady=10)
        settings_strip.pack(fill=tk.X, pady=(0, 16))

        self.autostart_var = tk.BooleanVar(value=is_autostart_enabled())

        autostart_chk = tk.Checkbutton(
            settings_strip,
            text="تشغيل فصيح تلقائياً عند فتح اللابتوب (Startup)",
            variable=self.autostart_var,
            font=("Segoe UI", 9),
            fg=self.COLOR_TEXT_MAIN,
            bg=self.COLOR_SURFACE,
            activebackground=self.COLOR_SURFACE,
            activeforeground=self.COLOR_CYAN,
            selectcolor=self.COLOR_SURFACE_LIGHT,
            command=self._toggle_autostart
        )
        autostart_chk.pack(anchor="w")

        # ----------------- 7. BOTTOM BAR -----------------
        bottom_bar = tk.Frame(main_box, bg=self.COLOR_BG)
        bottom_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.update_btn = tk.Button(
            bottom_bar,
            text=f"🔄 فحص التحديثات (v{CURRENT_VERSION})",
            font=("Segoe UI", 8, "bold"),
            bg=self.COLOR_SURFACE,
            fg=self.COLOR_CYAN,
            relief=tk.FLAT,
            padx=12,
            pady=6,
            cursor="hand2",
            command=lambda: threading.Thread(target=self._check_update_task, args=(True,), daemon=True).start()
        )
        self.update_btn.pack(side=tk.LEFT)

        self.toggle_btn = tk.Button(
            bottom_bar,
            text="⏸️ إيقاف مؤقت",
            font=("Segoe UI", 9),
            bg=self.COLOR_SURFACE,
            fg=self.COLOR_TEXT_MAIN,
            relief=tk.FLAT,
            padx=14,
            pady=5,
            cursor="hand2",
            command=self._toggle_service
        )
        self.toggle_btn.pack(side=tk.RIGHT)

        min_btn = tk.Button(
            bottom_bar,
            text="🔽 تصغير",
            font=("Segoe UI", 9),
            bg=self.COLOR_SURFACE,
            fg=self.COLOR_TEXT_MAIN,
            relief=tk.FLAT,
            padx=14,
            pady=5,
            cursor="hand2",
            command=self.root.iconify
        )
        min_btn.pack(side=tk.RIGHT, padx=8)

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
            self.status_chip.config(text="● نَشِط بالخلفية", fg=self.COLOR_EMERALD, bg="#064E3B")
            self.toggle_btn.config(text="⏸️ إيقاف مؤقت")
            FloatingToast.show("تم استئناف عمل مصحح الكيبورد", "فَصِيح 🟢")
        else:
            self.status_chip.config(text="● متوقف مؤقتاً", fg="#EF4444", bg="#450A0A")
            self.toggle_btn.config(text="▶️ تشغيل")
            FloatingToast.show("تم إيقاف الأداة مؤقتاً", "فَصِيح 🔴")

    def _register_hotkeys(self):
        try:
            keyboard.add_hotkey('ctrl+shift+a', self._trigger_hotkey, suppress=False)
            keyboard.add_hotkey('alt+q', self._trigger_hotkey, suppress=False)
            keyboard.add_hotkey('f9', self._trigger_hotkey, suppress=False)
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

    # ----------------- REAL-TIME AUTO-UPDATER WITH PROGRESS BAR -----------------
    def _check_update_task(self, manual=False):
        try:
            if manual:
                self.update_btn.config(text="⏳ جاري الفحص...")

            req = urllib.request.Request(UPDATE_CHECK_URL, headers={'User-Agent': 'Faseeh-Updater'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))

            remote_ver_str = data.get("version", "1.0.0")
            download_url = data.get("download_url", "")
            notes = data.get("release_notes", "تحسينات عامة وإصلاحات.")

            if parse_version(remote_ver_str) > parse_version(CURRENT_VERSION):
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
                    f"الإصدار الحالي: v{CURRENT_VERSION}\nتعذر الاتصال بـ GitHub، تأكد من اتصال الإنترنت."
                ))
        finally:
            if manual:
                self.root.after(0, lambda: self.update_btn.config(text=f"🔄 فحص التحديثات (v{CURRENT_VERSION})"))

    def _prompt_update_modal(self, new_ver, dl_url, notes):
        modal = tk.Toplevel(self.root)
        modal.title(f"تحديث جديد متاح: v{new_ver}")
        modal.geometry("460x300")
        modal.resizable(False, False)
        modal.configure(bg=self.COLOR_BG)
        modal.transient(self.root)
        modal.grab_set()

        head = tk.Label(
            modal, text=f"🎉 يتوفر إصدار جديد من فَصِيح (v{new_ver})",
            font=("Segoe UI", 12, "bold"), fg=self.COLOR_CYAN, bg=self.COLOR_BG
        )
        head.pack(pady=(16, 6))

        notes_box = tk.Label(
            modal, text=f"ما الجديد في هذا التحديث:\n{notes}",
            font=("Segoe UI", 9), fg=self.COLOR_TEXT_MUTED, bg=self.COLOR_BG,
            wraplength=410, justify=tk.RIGHT
        )
        notes_box.pack(pady=(0, 12), padx=20)

        # Live Progress Display Frame
        prog_frame = tk.Frame(modal, bg=self.COLOR_BG)
        prog_frame.pack(fill=tk.X, padx=25, pady=(0, 10))

        status_lbl = tk.Label(
            prog_frame, text="", font=("Segoe UI", 9, "bold"),
            fg=self.COLOR_TEXT_MAIN, bg=self.COLOR_BG
        )
        status_lbl.pack(pady=(0, 6))

        # Modern Progress Bar
        style = ttk.Style()
        style.theme_use('default')
        style.configure(
            "Faseeh.Horizontal.TProgressbar",
            troughcolor="#1E293B",
            background="#3B82F6",
            thickness=12,
            relief=tk.FLAT
        )

        prog_bar = ttk.Progressbar(
            prog_frame,
            style="Faseeh.Horizontal.TProgressbar",
            orient="horizontal",
            mode="determinate",
            maximum=100
        )
        # Initially hidden until download starts
        prog_bar.pack_forget()

        btn_row = tk.Frame(modal, bg=self.COLOR_BG)
        btn_row.pack(side=tk.BOTTOM, pady=16)

        def _start_download():
            dl_btn.config(state=tk.DISABLED)
            prog_bar.pack(fill=tk.X, pady=(4, 0))
            status_lbl.config(text="⚡ جاري الاتصال وبدء التحميل...")

            def _dl_worker():
                try:
                    temp_dir = os.environ.get("TEMP", ".")
                    new_file = os.path.join(temp_dir, f"Faseeh_{new_ver}.exe")

                    def _reporthook(block_num, block_size, total_size):
                        if total_size > 0:
                            downloaded = block_num * block_size
                            percent = min(100, int(downloaded * 100 / total_size))
                            mb_down = downloaded / (1024 * 1024)
                            mb_total = total_size / (1024 * 1024)

                            modal.after(0, lambda: _update_progress(percent, mb_down, mb_total))

                    def _update_progress(percent, mb_down, mb_total):
                        prog_bar['value'] = percent
                        status_lbl.config(
                            text=f"⚡ جاري التحميل: {percent}%  ({mb_down:.1f} MB من {mb_total:.1f} MB)",
                            fg=self.COLOR_CYAN
                        )

                    urllib.request.urlretrieve(dl_url, new_file, reporthook=_reporthook)

                    status_lbl.config(text="✅ اكتمل التحميل بنسبة 100%! جاري التثبيت...", fg=self.COLOR_EMERALD)
                    time.sleep(0.9)
                    apply_update_and_restart(new_file)
                except Exception as e:
                    status_lbl.config(text=f"❌ تعذر التحميل: {e}", fg="#EF4444")
                    dl_btn.config(state=tk.NORMAL)

            threading.Thread(target=_dl_worker, daemon=True).start()

        dl_btn = tk.Button(
            btn_row, text="🚀 تحديث وتثبيت الآن",
            font=("Segoe UI", 9, "bold"), bg=self.COLOR_PRIMARY, fg="#FFFFFF",
            relief=tk.FLAT, padx=14, pady=6, cursor="hand2",
            command=_start_download
        )
        dl_btn.pack(side=tk.LEFT, padx=6)

        cancel_btn = tk.Button(
            btn_row, text="إلغاء",
            font=("Segoe UI", 9), bg=self.COLOR_SURFACE, fg=self.COLOR_TEXT_MUTED,
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
