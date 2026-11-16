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
import socket
import urllib.request
import ctypes
import winsound
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import pyperclip
import keyboard
import io
import base64

from app_icon_data import FEATHER_ICON_B64
from converter import fix_text, is_mostly_arabic, is_inverted_en_to_ar, convert_en_to_ar
from franco import is_franco_text, convert_franco_to_arabic

CURRENT_VERSION = "1.8.0"
UPDATE_CHECK_URL = "https://raw.githubusercontent.com/zaidkhalailahjo/faseeh/main/version.json"
SINGLE_INSTANCE_PORT = 47892

try:
    myappid = 'faseeh.keyboard.fixer.v1.8.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

def play_soft_chime(enabled=True):
    if not enabled:
        return
    def _run():
        try:
            winsound.Beep(920, 35)
            winsound.Beep(1380, 45)
        except Exception:
            pass
    threading.Thread(target=_run, daemon=True).start()

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
        "autostart": True,
        "sound_enabled": True,
        "autodetect_enabled": True,
        "ctrla_autofix": True,
        "real_downloads": 2,
        "preferred_hotkey": "Ctrl + Shift + A"
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


def fetch_real_github_downloads():
    try:
        req = urllib.request.Request(
            "https://api.github.com/repos/zaidkhalailahjo/faseeh/releases",
            headers={"User-Agent": "Faseeh-Real-Tracker"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            releases = json.loads(resp.read().decode("utf-8"))
            total_dl = sum(
                asset.get("download_count", 0)
                for rel in releases
                for asset in rel.get("assets", [])
            )
            return total_dl
    except Exception:
        return None


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


class AutoDetectBubble:
    _active = None

    @staticmethod
    def show(word, candidate, on_accept_callback):
        def _run():
            try:
                if AutoDetectBubble._active:
                    try:
                        AutoDetectBubble._active.destroy()
                    except Exception:
                        pass

                bubble = tk.Tk()
                AutoDetectBubble._active = bubble
                bubble.overrideredirect(True)
                bubble.attributes("-topmost", True)
                bubble.attributes("-alpha", 0.96)
                bubble.configure(bg="#0F172A")

                sw = bubble.winfo_screenwidth()
                sh = bubble.winfo_screenheight()
                w = 360
                h = 56
                x = sw - w - 24
                y = sh - h - 160
                bubble.geometry(f"{w}x{h}+{x}+{y}")

                border = tk.Frame(bubble, bg="#38BDF8", padx=1, pady=1)
                border.pack(fill=tk.BOTH, expand=True)

                inner = tk.Frame(border, bg="#0F172A", padx=12, pady=6)
                inner.pack(fill=tk.BOTH, expand=True)

                right_box = tk.Frame(inner, bg="#0F172A")
                right_box.pack(side=tk.RIGHT)

                preview = candidate if len(candidate) <= 18 else (candidate[:16] + "..")
                tk.Label(
                    right_box,
                    text=f"💡 تصحيح مقترح: «{preview}»",
                    font=("Segoe UI", 9, "bold"),
                    fg="#38BDF8",
                    bg="#0F172A"
                ).pack(anchor="e")

                tk.Label(
                    right_box,
                    text="انقر هنا أو اضغط الاختصار للتطبيق",
                    font=("Segoe UI", 7),
                    fg="#94A3B8",
                    bg="#0F172A"
                ).pack(anchor="e")

                left_box = tk.Frame(inner, bg="#0F172A")
                left_box.pack(side=tk.LEFT)

                accept_btn = tk.Label(
                    left_box,
                    text="✨ تطبيق فوري",
                    font=("Segoe UI", 8, "bold"),
                    fg="#FFFFFF",
                    bg="#2563EB",
                    padx=10,
                    pady=4,
                    cursor="hand2"
                )
                accept_btn.pack(side=tk.LEFT)

                def _do_accept(e=None):
                    AutoDetectBubble.hide()
                    on_accept_callback()

                accept_btn.bind("<Button-1>", _do_accept)
                inner.bind("<Button-1>", _do_accept)
                right_box.bind("<Button-1>", _do_accept)

                bubble.after(4500, lambda: AutoDetectBubble.hide())
                bubble.mainloop()
            except Exception:
                pass

        threading.Thread(target=_run, daemon=True).start()

    @staticmethod
    def hide():
        if AutoDetectBubble._active:
            try:
                AutoDetectBubble._active.destroy()
            except Exception:
                pass
            AutoDetectBubble._active = None


class KeyboardFixerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("فَصِيح - مصحح الكيبورد الذكي")
        self.root.geometry("575x700")
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
        self.real_downloads = self.user_data.get("real_downloads", 2)

        self.typed_buffer = []
        self._last_detected_pair = None

        self._apply_icons()

        self.is_active = True
        self.is_processing = False

        self._setup_ui()
        self._register_hotkeys()

        try:
            keyboard.on_press(self._on_key_typed)
        except Exception:
            pass

        self.root.protocol("WM_DELETE_WINDOW", self._on_close_clicked)
        self._start_ipc_server()

        if self.user_data.get("autostart", True) and not is_autostart_enabled():
            set_autostart(True)

        self.root.after(1500, lambda: threading.Thread(target=self._fetch_real_community_stats, daemon=True).start())
        self.root.after(4000, lambda: threading.Thread(target=self._check_update_task, args=(False,), daemon=True).start())

    def _apply_icons(self):
        try:
            raw_bytes = base64.b64decode(FEATHER_ICON_B64)
            img_pil = Image.open(io.BytesIO(raw_bytes))
            self.logo_photo = ImageTk.PhotoImage(img_pil)
            self.root.iconphoto(True, self.logo_photo)
        except Exception:
            self.logo_photo = None

        ico_file = get_resource_path("app_icon.ico")
        if os.path.exists(ico_file):
            try:
                self.root.iconbitmap(ico_file)
            except Exception:
                pass

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

        try:
            raw_bytes = base64.b64decode(FEATHER_ICON_B64)
            img_raw = Image.open(io.BytesIO(raw_bytes)).resize((52, 52), Image.Resampling.LANCZOS)
            self.logo_head = ImageTk.PhotoImage(img_raw)
            logo_lbl = tk.Label(brand_box, image=self.logo_head, bg=self.COLOR_BG)
            logo_lbl.pack(side=tk.RIGHT, padx=(12, 0))
        except Exception:
            pass

        text_col = tk.Frame(brand_box, bg=self.COLOR_BG)
        text_col.pack(side=tk.RIGHT, padx=(0, 4))

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

        # ----------------- 2. MAIN CONTAINER -----------------
        main_box = tk.Frame(self.root, bg=self.COLOR_BG, padx=26, pady=4)
        main_box.pack(fill=tk.BOTH, expand=True)

        # ----------------- 3. BENTO STATS CARDS (2 Cards) -----------------
        stats_frame = tk.Frame(main_box, bg=self.COLOR_BG)
        stats_frame.pack(fill=tk.X, pady=(0, 16))

        # Card 1: Rescues
        c1 = tk.Frame(stats_frame, bg=self.COLOR_SURFACE, padx=14, pady=14)
        c1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))

        tk.Label(c1, text="مرات الإنقاذ 🛡️", font=("Segoe UI", 10, "bold"), fg=self.COLOR_CYAN, bg=self.COLOR_SURFACE).pack(anchor="center")
        self.c1_val = tk.Label(
            c1,
            text=f"{self.rescues_count} مرة",
            font=("Segoe UI", 18, "bold"),
            fg=self.COLOR_TEXT_MAIN,
            bg=self.COLOR_SURFACE
        )
        self.c1_val.pack(anchor="center", pady=(5, 2))
        tk.Label(c1, text="تصحيح فوري دون مسح", font=("Segoe UI", 8), fg=self.COLOR_TEXT_MUTED, bg=self.COLOR_SURFACE).pack(anchor="center")

        # Card 2: Time Saved
        c2 = tk.Frame(stats_frame, bg=self.COLOR_SURFACE, padx=14, pady=14)
        c2.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(6, 0))

        tk.Label(c2, text="الوقت الموفّر ⏱️", font=("Segoe UI", 10, "bold"), fg=self.COLOR_EMERALD, bg=self.COLOR_SURFACE).pack(anchor="center")
        self.c2_val = tk.Label(
            c2,
            text=format_time_saved(self.seconds_saved),
            font=("Segoe UI", 14, "bold"),
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
        settings_strip.pack(fill=tk.X, pady=(0, 14))

        # Row 1: Startup & Sound
        row1 = tk.Frame(settings_strip, bg=self.COLOR_SURFACE)
        row1.pack(fill=tk.X, pady=(0, 4))

        self.autostart_var = tk.BooleanVar(value=is_autostart_enabled())
        autostart_chk = tk.Checkbutton(
            row1,
            text="تشغيل تلقائي مع الويندوز",
            variable=self.autostart_var,
            font=("Segoe UI", 8),
            fg=self.COLOR_TEXT_MAIN,
            bg=self.COLOR_SURFACE,
            activebackground=self.COLOR_SURFACE,
            activeforeground=self.COLOR_CYAN,
            selectcolor=self.COLOR_SURFACE_LIGHT,
            command=self._toggle_autostart
        )
        autostart_chk.pack(side=tk.RIGHT)

        self.sound_var = tk.BooleanVar(value=self.user_data.get("sound_enabled", True))
        sound_chk = tk.Checkbutton(
            row1,
            text="نغمة ناعمة عند التحويل (Juice 🔔)",
            variable=self.sound_var,
            font=("Segoe UI", 8),
            fg=self.COLOR_TEXT_MAIN,
            bg=self.COLOR_SURFACE,
            activebackground=self.COLOR_SURFACE,
            activeforeground=self.COLOR_CYAN,
            selectcolor=self.COLOR_SURFACE_LIGHT,
            command=self._toggle_sound
        )
        sound_chk.pack(side=tk.LEFT)

        # Row 2: Auto-Detect Bubble
        row2 = tk.Frame(settings_strip, bg=self.COLOR_SURFACE)
        row2.pack(fill=tk.X, pady=(0, 4))

        self.autodetect_var = tk.BooleanVar(value=self.user_data.get("autodetect_enabled", True))
        autodetect_chk = tk.Checkbutton(
            row2,
            text="بالون التصحيح التلقائي الذكي أثناء الكتابة (Auto-Detect 💡)",
            variable=self.autodetect_var,
            font=("Segoe UI", 8),
            fg=self.COLOR_TEXT_MAIN,
            bg=self.COLOR_SURFACE,
            activebackground=self.COLOR_SURFACE,
            activeforeground=self.COLOR_CYAN,
            selectcolor=self.COLOR_SURFACE_LIGHT,
            command=self._toggle_autodetect
        )
        autodetect_chk.pack(side=tk.RIGHT)

        # Row 3: Ctrl + A Auto-Fix
        row3 = tk.Frame(settings_strip, bg=self.COLOR_SURFACE)
        row3.pack(fill=tk.X, pady=(0, 6))

        self.ctrla_autofix_var = tk.BooleanVar(value=self.user_data.get("ctrla_autofix", True))
        ctrla_chk = tk.Checkbutton(
            row3,
            text="تصحيح فوري تلقائي عند التحديد بالكامل (Ctrl + A ⚡)",
            variable=self.ctrla_autofix_var,
            font=("Segoe UI", 8, "bold"),
            fg=self.COLOR_TEXT_MAIN,
            bg=self.COLOR_SURFACE,
            activebackground=self.COLOR_SURFACE,
            activeforeground=self.COLOR_CYAN,
            selectcolor=self.COLOR_SURFACE_LIGHT,
            command=self._toggle_ctrla_autofix
        )
        ctrla_chk.pack(side=tk.RIGHT)

        # Row 4: Hotkey Selector
        row4 = tk.Frame(settings_strip, bg=self.COLOR_SURFACE)
        row4.pack(fill=tk.X, pady=(2, 0))

        tk.Label(
            row4,
            text="الاختصار الأساسي:",
            font=("Segoe UI", 8, "bold"),
            fg=self.COLOR_CYAN,
            bg=self.COLOR_SURFACE
        ).pack(side=tk.RIGHT, padx=(4, 0))

        self.hotkey_options = [
            "Ctrl + Shift + A",
            "Alt + Q",
            "F9",
            "Caps Lock",
            "Ctrl + Space"
        ]
        self.selected_hotkey = tk.StringVar(value=self.user_data.get("preferred_hotkey", "Ctrl + Shift + A"))

        hotkey_dropdown = ttk.Combobox(
            row4,
            textvariable=self.selected_hotkey,
            values=self.hotkey_options,
            state="readonly",
            width=16,
            font=("Segoe UI", 8)
        )
        hotkey_dropdown.pack(side=tk.RIGHT)
        hotkey_dropdown.bind("<<ComboboxSelected>>", self._on_hotkey_changed)

        # ----------------- 6.5 STATUS / COMMUNITY BAR -----------------
        status_bar = tk.Frame(main_box, bg=self.COLOR_BG)
        status_bar.pack(fill=tk.X, pady=(0, 10))

        self.users_lbl = tk.Label(
            status_bar,
            text=f"المستخدمون : {self.real_downloads}",
            font=("Segoe UI", 9, "bold"),
            fg=self.COLOR_CYAN,
            bg=self.COLOR_BG
        )
        self.users_lbl.pack(side=tk.RIGHT)

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

        hide_btn = tk.Button(
            bottom_bar,
            text="🛡️ إخفاء بالخلفية",
            font=("Segoe UI", 9),
            bg=self.COLOR_SURFACE,
            fg=self.COLOR_TEXT_MAIN,
            relief=tk.FLAT,
            padx=12,
            pady=5,
            cursor="hand2",
            command=self._on_close_clicked
        )
        hide_btn.pack(side=tk.RIGHT, padx=6)

        exit_btn = tk.Button(
            bottom_bar,
            text="✕ إغلاق كامل",
            font=("Segoe UI", 8),
            bg=self.COLOR_BG,
            fg="#64748B",
            activeforeground="#EF4444",
            relief=tk.FLAT,
            padx=6,
            pady=5,
            cursor="hand2",
            command=self._quit_app
        )
        exit_btn.pack(side=tk.RIGHT, padx=2)

    def _start_ipc_server(self):
        def _server():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('127.0.0.1', SINGLE_INSTANCE_PORT))
                s.listen(3)
                while True:
                    conn, _ = s.accept()
                    data = conn.recv(64)
                    if data == b'SHOW':
                        self.root.after(0, self._restore_window)
                    conn.close()
            except Exception:
                pass
        threading.Thread(target=_server, daemon=True).start()

    def _on_close_clicked(self):
        self.root.withdraw()
        FloatingToast.show(
            "يعمل 'فَصِيح' الآن في الخلفية بهدوء 🛡️\nاضغط الاختصار في أي وقت لتحويل النص مباشرة.",
            "فَصِيح نَشِط ✨"
        )

    def _restore_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def _quit_app(self):
        try:
            self.root.destroy()
        except Exception:
            pass
        sys.exit(0)

    def _toggle_autostart(self):
        enabled = self.autostart_var.get()
        set_autostart(enabled)
        self.user_data["autostart"] = enabled
        save_user_data(self.user_data)
        if enabled:
            FloatingToast.show("تم تفعيل التشغيل التلقائي عند فتح اللابتوب", "فَصِيح 🚀")
        else:
            FloatingToast.show("تم إيقاف التشغيل التلقائي مع فتح الجهاز", "فَصِيح ⏸️")

    def _toggle_sound(self):
        enabled = self.sound_var.get()
        self.user_data["sound_enabled"] = enabled
        save_user_data(self.user_data)
        if enabled:
            play_soft_chime(True)
            FloatingToast.show("تم تفعيل النغمة التفاعلية الناعمة 🔔", "فَصِيح")
        else:
            FloatingToast.show("تم كتم النغمة التفاعلية 🔕", "فَصِيح")

    def _toggle_autodetect(self):
        enabled = self.autodetect_var.get()
        self.user_data["autodetect_enabled"] = enabled
        save_user_data(self.user_data)
        if enabled:
            FloatingToast.show("تم تفعيل بالون التصحيح التلقائي الاستباقي 💡", "فَصِيح")
        else:
            FloatingToast.show("تم إيقاف بالون التصحيح التلقائي", "فَصِيح")

    def _toggle_ctrla_autofix(self):
        enabled = self.ctrla_autofix_var.get()
        self.user_data["ctrla_autofix"] = enabled
        save_user_data(self.user_data)
        if enabled:
            FloatingToast.show("تم تفعيل التصحيح الفوري عند التحديد بـ Ctrl+A ⚡", "فَصِيح")
        else:
            FloatingToast.show("تم إيقاف التصحيح عند Ctrl+A", "فَصِيح")

    def _on_hotkey_changed(self, event=None):
        selected = self.selected_hotkey.get()
        self.user_data["preferred_hotkey"] = selected
        save_user_data(self.user_data)
        self._register_hotkeys()
        FloatingToast.show(f"تم تفعيل الاختصار المفضل: {selected}", "تخصيص الاختصارات ⌨️")

    def _on_key_typed(self, event):
        if not self.is_active:
            return
        try:
            name = (event.name or "").lower()

            # Instant auto-fix on Select All (Ctrl + A)
            if name == 'a' and keyboard.is_pressed('ctrl') and not (keyboard.is_pressed('shift') or keyboard.is_pressed('alt')):
                if hasattr(self, 'ctrla_autofix_var') and self.ctrla_autofix_var.get() and not self.is_processing:
                    threading.Thread(target=self._handle_ctrl_a_autofix, daemon=True).start()
                return

            if not self.autodetect_var.get():
                return

            if name == 'backspace':
                if self.typed_buffer:
                    self.typed_buffer.pop()
                return

            if name in ['escape', 'esc']:
                AutoDetectBubble.hide()
                return

            char = None
            if name == 'space':
                char = ' '
            elif len(name) == 1 and not (keyboard.is_pressed('ctrl') or keyboard.is_pressed('alt')):
                char = name

            if char is not None:
                self.typed_buffer.append(char)
                if len(self.typed_buffer) > 40:
                    self.typed_buffer.pop(0)

                # Check immediately on delimiters or word length
                if char in [' ', ';', '.', ',', '!', '?'] or len(self.typed_buffer) >= 3:
                    self._check_autodetect_buffer()
        except Exception:
            pass

    def _handle_ctrl_a_autofix(self):
        try:
            time.sleep(0.08)

            saved_clip = ""
            try:
                saved_clip = pyperclip.paste()
            except Exception:
                pass

            pyperclip.copy("")
            time.sleep(0.03)
            send_copy()
            copied = get_clipboard_text(timeout=0.25)

            if not copied:
                if saved_clip:
                    pyperclip.copy(saved_clip)
                return

            # CRITICAL RULE: If text is already Arabic, NEVER touch it on Ctrl+A!
            if any('\u0600' <= c <= '\u06FF' or c in '،؛؟' for c in copied):
                if saved_clip:
                    pyperclip.copy(saved_clip)
                return

            if is_inverted_en_to_ar(copied):
                if is_franco_text(copied):
                    fixed = convert_franco_to_arabic(copied)
                else:
                    fixed = convert_en_to_ar(copied)

                # STRICT RULE: Must be converted to Arabic and different from original
                if fixed and fixed != copied and any('\u0600' <= c <= '\u06FF' for c in fixed):
                    pyperclip.copy(fixed)
                    time.sleep(0.04)
                    send_paste()
                    play_soft_chime(self.sound_var.get())
                    self.root.after(0, lambda: self._record_rescue(len(copied)))
                    preview = (fixed[:32] + "...") if len(fixed) > 32 else fixed
                    FloatingToast.show(f"تم التصحيح الفوري بـ (Ctrl+A):\n{preview}", "فَصِيح ⚡")
                    return

            if saved_clip:
                pyperclip.copy(saved_clip)
        except Exception:
            pass

    def _check_autodetect_buffer(self):
        full_text = "".join(self.typed_buffer).strip()
        if len(full_text) < 3:
            return

        # 1. Check full buffer (e.g. ";dt phg;" or "mar7aba keefak")
        cand = fix_text(full_text)
        if cand and cand != full_text:
            self._last_detected_pair = (full_text, cand)
            AutoDetectBubble.show(full_text, cand, self._accept_autodetect)
            return

        # 2. Check the last word in buffer (e.g. "hello ;dt")
        words = full_text.split()
        if words:
            last = words[-1].strip(";,.")
            if len(last) >= 3:
                cw = fix_text(last)
                if cw and cw != last:
                    self._last_detected_pair = (last, cw)
                    AutoDetectBubble.show(last, cw, self._accept_autodetect)

    def _accept_autodetect(self):
        if not self._last_detected_pair:
            return
        orig, cand = self._last_detected_pair
        self._last_detected_pair = None
        self.typed_buffer = []
        AutoDetectBubble.hide()
        self._do_typed_replacement(orig, cand)

    def _do_typed_replacement(self, orig, cand):
        def _do_replace():
            time.sleep(0.04)
            erase_count = len(orig)
            for _ in range(erase_count):
                user32.keybd_event(0x08, 0, 0, 0)
                user32.keybd_event(0x08, 0, 0x0002, 0)
                time.sleep(0.01)
            time.sleep(0.04)
            pyperclip.copy(cand + " ")
            send_paste()
            play_soft_chime(self.sound_var.get())
            self.root.after(0, lambda: self._record_rescue(len(orig)))

        threading.Thread(target=_do_replace, daemon=True).start()

    def _convert_test_box(self):
        txt = self.test_entry.get()
        if txt:
            fixed = fix_text(txt)
            self.test_entry.delete(0, tk.END)
            self.test_entry.insert(0, fixed)
            self._record_rescue(len(txt))
            play_soft_chime(self.sound_var.get())
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

    def _update_users_display(self, real_dl):
        try:
            if hasattr(self, 'users_lbl') and self.users_lbl:
                self.users_lbl.config(text=f"المستخدمون : {real_dl}")
        except Exception:
            pass

    def _fetch_real_community_stats(self):
        real_dl = fetch_real_github_downloads()
        if real_dl is not None:
            self.real_downloads = real_dl
            self.user_data["real_downloads"] = real_dl
            save_user_data(self.user_data)
            self.root.after(0, lambda: self._update_users_display(self.real_downloads))

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
            keyboard.unhook_all_hotkeys()
        except Exception:
            pass
        try:
            # Standard persistent hotkeys
            keyboard.add_hotkey('ctrl+shift+a', self._trigger_hotkey, suppress=False)
            keyboard.add_hotkey('alt+q', self._trigger_hotkey, suppress=False)
            keyboard.add_hotkey('f9', self._trigger_hotkey, suppress=False)

            # Custom preferred hotkey
            pref = self.user_data.get("preferred_hotkey", "Ctrl + Shift + A")
            clean_pref = pref.lower().replace(" ", "")
            if clean_pref == "capslock":
                keyboard.add_hotkey('caps lock', self._trigger_hotkey, suppress=False)
            elif clean_pref == "ctrl+space":
                keyboard.add_hotkey('ctrl+space', self._trigger_hotkey, suppress=False)
            elif clean_pref not in ['ctrl+shift+a', 'alt+q', 'f9']:
                keyboard.add_hotkey(clean_pref, self._trigger_hotkey, suppress=False)
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
                if self._last_detected_pair:
                    orig, cand = self._last_detected_pair
                    self._last_detected_pair = None
                    self.typed_buffer = []
                    AutoDetectBubble.hide()
                    self._do_typed_replacement(orig, cand)
                    return

                if saved_clip:
                    pyperclip.copy(saved_clip)
                FloatingToast.show("الرجاء تظليل النص أولاً ثم ضغط الاختصار", "تنبيه ⚠️")
                return

            fixed = fix_text(copied)

            if fixed and fixed != copied:
                pyperclip.copy(fixed)
                time.sleep(0.05)
                send_paste()

                play_soft_chime(self.sound_var.get())

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

            check_url = f"{UPDATE_CHECK_URL}?nocache={int(time.time())}"
            req = urllib.request.Request(check_url, headers={
                'User-Agent': 'Faseeh-Updater',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            })
            with urllib.request.urlopen(req, timeout=6) as response:
                data = json.loads(response.read().decode('utf-8'))

            remote_ver_str = data.get("version", "1.0.0")
            download_url = data.get("download_url", "")
            notes = data.get("release_notes", "تحسينات عامة وإصلاحات.")

            # Fetch 100% REAL downloads from GitHub Releases API
            real_dl = fetch_real_github_downloads()
            if real_dl is not None:
                self.real_downloads = real_dl
                self.user_data["real_downloads"] = real_dl
                save_user_data(self.user_data)
                self.root.after(0, lambda: self._update_users_display(self.real_downloads))

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

                    fresh_dl_url = dl_url
                    sep = "&" if "?" in fresh_dl_url else "?"
                    fresh_dl_url = f"{fresh_dl_url}{sep}nocache={int(time.time())}"
                    urllib.request.urlretrieve(fresh_dl_url, new_file, reporthook=_reporthook)

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


def try_wake_existing_instance():
    """Attempt to contact a running instance of Faseeh to bring it to foreground."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.4)
        s.connect(('127.0.0.1', SINGLE_INSTANCE_PORT))
        s.sendall(b'SHOW')
        s.close()
        return True
    except Exception:
        return False


def main():
    if try_wake_existing_instance():
        # Another instance is already active in background. It has been restored!
        sys.exit(0)

    root = tk.Tk()
    app = KeyboardFixerApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
