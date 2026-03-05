import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import time
import os
import sys

# Hide console windows for subprocess calls
if sys.platform == 'win32':
    CREATE_NO_WINDOW = 0x08000000
else:
    CREATE_NO_WINDOW = 0

# Modern Aesthetic Config
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Color Palette (Ultra-Modern Dark Theme)
BG_COLOR = "#0f111a"
SURFACE_COLOR = "#1e2130"
CARD_COLOR = "#141724"
BORDER_COLOR = "#2a2f45"

ACCENT_COLOR = "#3b82f6"     # Modern Blue
SUCCESS_COLOR = "#10b981"    # Emerald Green
WARNING_COLOR = "#f59e0b"    # Amber
DANGER_COLOR = "#ef4444"     # Rose Red

TEXT_MAIN = "#f8fafc"
TEXT_MUTED = "#94a3b8"

class ProcessKillerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Seven Knights – Multi Screen Manager")
        self.geometry("860x720")
        self.minsize(750, 600)
        self.configure(fg_color=BG_COLOR)
        
        # Icon setup
        try:
            if getattr(sys, 'frozen', False):
                app_path = sys._MEIPASS
            else:
                app_path = os.path.dirname(os.path.abspath(__file__))
            ico = os.path.join(app_path, 'icon.ico')
            if os.path.exists(ico):
                self.iconbitmap(ico)
                self.wm_iconbitmap(ico)
                # Workaround for CustomTkinter icon issue on Windows
                self.after(200, lambda: self.iconbitmap(ico))
        except Exception as e:
            print(f"Icon Error: {e}")

        self.process_name = "ProjectRE.exe"
        
        # Layout configurations
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Main Canvas (Container)
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=0, sticky="nsew", padx=35, pady=30)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(2, weight=1)
        
        self.fonts = {
            "title": ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            "subtitle": ctk.CTkFont(family="Segoe UI", size=13),
            "card_title": ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            "card_value": ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            "log": ctk.CTkFont(family="Consolas", size=13),
            "btn": ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        }

        self._build_header()
        self._build_dashboard()
        self._build_log_console()
        self._build_controls()
        self._build_footer()
        
        self.after(500, self.scan) # small delay before scanning

    def _build_header(self):
        hdr = ctk.CTkFrame(self.container, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 25))
        hdr.grid_columnconfigure(1, weight=1)
        
        # Titling & Branding
        left_box = ctk.CTkFrame(hdr, fg_color="transparent")
        left_box.grid(row=0, column=0, sticky="w")
        
        icon_cv = tk.Canvas(left_box, width=54, height=54, bg=BG_COLOR, highlightthickness=0)
        icon_cv.pack(side="left", padx=(0, 18))
        self._render_premium_logo(icon_cv)
        
        text_box = ctk.CTkFrame(left_box, fg_color="transparent")
        text_box.pack(side="left")
        
        ctk.CTkLabel(text_box, text="SEVEN KNIGHTS", font=self.fonts["title"], text_color=ACCENT_COLOR).pack(anchor="w", pady=(0, 0))
        ctk.CTkLabel(text_box, text="Multi Screen Manager Application", font=self.fonts["subtitle"], text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 0))
        
        # Version Badge
        badge_frame = ctk.CTkFrame(hdr, fg_color=SURFACE_COLOR, corner_radius=8, border_width=1, border_color=BORDER_COLOR)
        badge_frame.grid(row=0, column=1, sticky="ne")
        ctk.CTkLabel(badge_frame, text=" v2.5 PRO ", font=self.fonts["card_title"], text_color=SUCCESS_COLOR).pack(padx=12, pady=6)

    def _render_premium_logo(self, cv):
        cv.delete('all')
        cx, cy = 27, 27
        # Subtle glow rings
        cv.create_oval(cx - 26, cy - 26, cx + 26, cy + 26, outline=BORDER_COLOR, width=1)
        cv.create_oval(cx - 22, cy - 22, cx + 22, cy + 22, fill=CARD_COLOR, outline=ACCENT_COLOR, width=2.5)
        # Inner emblem
        cv.create_text(cx, cy, text='⚔', font=('Segoe UI Emoji', 20), fill="#ffffff")

    def _build_dashboard(self):
        dash = ctk.CTkFrame(self.container, fg_color="transparent")
        dash.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        dash.grid_columnconfigure((0, 1), weight=1)
        
        # Card 1: Process Target
        c1 = ctk.CTkFrame(dash, fg_color=CARD_COLOR, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        c1.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        ctk.CTkLabel(c1, text="TARGET APPLICATION", font=self.fonts["card_title"], text_color=TEXT_MUTED).pack(anchor="w", padx=20, pady=(16, 2))
        ctk.CTkLabel(c1, text=self.process_name, font=self.fonts["card_value"], text_color="#e2e8f0").pack(anchor="w", padx=20, pady=(0, 16))

        # Card 2: Status Real-time
        self.c2 = ctk.CTkFrame(dash, fg_color=CARD_COLOR, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        self.c2.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        ctk.CTkLabel(self.c2, text="SYSTEM STATUS", font=self.fonts["card_title"], text_color=TEXT_MUTED).pack(anchor="w", padx=20, pady=(16, 2))
        
        # Status wrapper with indicator dot
        st_wrap = ctk.CTkFrame(self.c2, fg_color="transparent")
        st_wrap.pack(fill="x", padx=20, pady=(0, 16))
        
        self.status_dot = ctk.CTkFrame(st_wrap, width=12, height=12, corner_radius=6, fg_color=TEXT_MUTED)
        self.status_dot.pack(side="left", padx=(0, 10))
        
        self._status_lbl = ctk.CTkLabel(st_wrap, text="Initializing...", font=self.fonts["card_value"], text_color="#e2e8f0")
        self._status_lbl.pack(side="left")

    def _build_log_console(self):
        console_frame = ctk.CTkFrame(self.container, fg_color=CARD_COLOR, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        console_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 20))
        console_frame.grid_columnconfigure(0, weight=1)
        console_frame.grid_rowconfigure(1, weight=1)
        
        # Console Header
        c_hdr = ctk.CTkFrame(console_frame, fg_color=SURFACE_COLOR, corner_radius=12)
        c_hdr.grid(row=0, column=0, sticky="ew")
        
        ctk.CTkLabel(c_hdr, text="TERMINAL LOG", font=self.fonts["card_title"], text_color=TEXT_MUTED).pack(side="left", padx=20, pady=10)
        
        # Window buttons decoration
        for c in ("#22c55e", "#f59e0b", "#ef4444"):
            dot = ctk.CTkFrame(c_hdr, width=12, height=12, corner_radius=6, fg_color=c)
            if c == "#22c55e":
                # Rightmost dot (green) gets extra padding on the right to offset the whole group
                dot.pack(side="right", padx=(6, 20), pady=14)
            else:
                dot.pack(side="right", padx=6, pady=14)
        
        # Log Textbox
        self._log = ctk.CTkTextbox(console_frame, fg_color="#09090b", text_color="#d4d4d8", 
                                   font=self.fonts["log"], wrap="word", corner_radius=0, border_width=0,
                                   state="disabled")
        self._log.grid(row=1, column=0, sticky="nsew", padx=1, pady=(0, 12)) # padding to prevent rounding clash at bottom
        
        # Color tags initialization (fallback if tk isn't directly exposed)
        try:
            tw = self._log._textbox
            tw.tag_config('ok', foreground=SUCCESS_COLOR)
            tw.tag_config('err', foreground=DANGER_COLOR)
            tw.tag_config('warn', foreground=WARNING_COLOR)
            tw.tag_config('dim', foreground='#52525b')
            tw.tag_config('acc', foreground=ACCENT_COLOR)
            tw.tag_config('h', foreground='#ffffff', font=('Consolas', 13, 'bold'))
        except Exception:
            pass

    def _build_controls(self):
        ctrls = ctk.CTkFrame(self.container, fg_color="transparent")
        ctrls.grid(row=3, column=0, sticky="ew", pady=(0, 15))
        ctrls.grid_columnconfigure((0, 1), weight=1)
        
        btn_wrapper = ctk.CTkFrame(ctrls, fg_color="transparent")
        btn_wrapper.pack()
        
        self._kill_btn = ctk.CTkButton(btn_wrapper, text="TERMINATE PROCESSES", font=self.fonts["btn"],
                                       fg_color=DANGER_COLOR, hover_color="#be123c", command=self.kill_process, 
                                       width=240, height=50, corner_radius=25,
                                       image=self._create_emoji_image("🛑"))
        self._kill_btn.pack(side="left", padx=10)
        
        self._refresh_btn = ctk.CTkButton(btn_wrapper, text="REFRESH SCAN", font=self.fonts["btn"],
                                          fg_color=SURFACE_COLOR, hover_color=BORDER_COLOR, border_width=1, border_color=BORDER_COLOR, 
                                          command=self.scan, width=180, height=50, corner_radius=25,
                                          image=self._create_emoji_image("🔄"))
        self._refresh_btn.pack(side="left", padx=10)

    def _create_emoji_image(self, emoji_char):
        # We simulate images using emoji labels or return nothing if CTk doesn't strictly need it.
        # CustomTkinter buttons support Unicode emojis in text without images!
        pass 

    def _build_footer(self):
        ftr = ctk.CTkLabel(self.container, text="Seven Knights Multi Screen  •  Made with ❤️ by Yusinz & Claude",
                           font=ctk.CTkFont(family="Segoe UI", size=11), text_color=TEXT_MUTED)
        ftr.grid(row=4, column=0, sticky="s")

    # --- LOGIC INTEGRATION ---
    def _log_write(self, segments):
        self._log.configure(state='normal')
        self._log.delete('1.0', 'end')
        
        try:
            tw = self._log._textbox
            for text, tag in segments:
                if tag:
                    tw.insert('end', text, tag)
                else:
                    tw.insert('end', text)
        except AttributeError:
            for text, tag in segments:
                self._log.insert('end', text)
                
        self._log.configure(state='disabled')

    def _set_status(self, text, txt_color, dot_color):
        self._status_lbl.configure(text=text, text_color=txt_color)
        self.status_dot.configure(fg_color=dot_color)

    def get_process_path(self, pid):
        try:
            ps_cmd = f'(Get-Process -Id {pid}).Path'
            r = subprocess.run(
                ['powershell', '-Command', ps_cmd],
                capture_output=True, text=True, timeout=3,
                creationflags=CREATE_NO_WINDOW)
            p = r.stdout.strip()
            if p and os.path.exists(p):
                return p
        except Exception:
            pass
        try:
            r = subprocess.run(
                ['wmic', 'process', 'where',
                 f'ProcessId={pid}', 'get', 'ExecutablePath', '/value'],
                capture_output=True, text=True, encoding='cp874',
                timeout=3, creationflags=CREATE_NO_WINDOW)
            for line in r.stdout.split('\n'):
                if 'ExecutablePath=' in line:
                    p = line.split('=', 1)[1].strip()
                    if p and os.path.exists(p):
                        return p
        except Exception:
            pass
        return '— Access Denied (Run as Administrator) —'

    def check_process(self):
        try:
            r = subprocess.run(
                ['tasklist', '/FI',
                 f'IMAGENAME eq {self.process_name}',
                 '/FO', 'CSV', '/V'],
                capture_output=True, text=True, encoding='cp874',
                creationflags=CREATE_NO_WINDOW)
            procs = []
            lines = [line for line in r.stdout.strip().split('\n') if self.process_name in line]
            for line in lines:
                parts = line.replace('"', '').split(',')
                if len(parts) >= 2:
                    pid = parts[1].strip()
                    mem_kb = parts[4] if len(parts) > 4 else '0'
                    try:
                        mb = f"{int(mem_kb.replace(' K', '').replace(',', '')) / 1024:.1f} MB"
                    except:
                        mb = mem_kb
                    procs.append({
                        'name': parts[0].strip(),
                        'pid': pid,
                        'memory': mb,
                        'path': self.get_process_path(pid),
                    })
            return procs
        except Exception:
            return None

    def scan(self):
        self._set_status('Scanning...', TEXT_MUTED, TEXT_MUTED)
        self._kill_btn.configure(state="disabled")
        self._refresh_btn.configure(state="disabled")
        
        self._log_write([('=> Initiating deep system scan for ', ''),
                         (self.process_name, 'acc'),
                         ('...\n', ''), ('=> Please hold...\n', 'dim')])

        def _work():
            procs = self.check_process()
            self.after(0, lambda: self._apply_scan(procs))

        threading.Thread(target=_work, daemon=True).start()

    def _apply_scan(self, procs):
        self._refresh_btn.configure(state="normal")
        if procs is None:
            self._set_status('Error', DANGER_COLOR, DANGER_COLOR)
            self._kill_btn.configure(state="disabled")
            self._log_write([
                ('[!] Unable to fetch process list\n\n', 'err'),
                ('----------------------------------------------------------\n', 'dim'),
                ('Suggestions:\n', 'h'),
                ('  - Run this application as Administrator\n', ''),
                ('  - Verify Windows Management Instrumentation service\n', ''),
            ])
            return

        if not procs:
            self._set_status('Standby', SUCCESS_COLOR, SUCCESS_COLOR)
            self._kill_btn.configure(state="disabled")
            self._log_write([
                ('[+] No target processes detected\n\n', 'ok'),
                ('----------------------------------------------------------\n', 'dim'),
                ('Status      : ', 'h'), ('Ready for multiple instances\n', 'ok'),
                ('Action Plan : ', 'h'), ('You are clear to launch the game.\n\n', 'ok'),
                ('Enjoy your multi-accounting experience!', 'acc'),
            ])
            return

        n = len(procs)
        self._set_status(f'{n} Instance{"s" if n > 1 else ""} Detected', WARNING_COLOR, WARNING_COLOR)
        self._kill_btn.configure(state="normal")

        msg = [
            (f'[!] Detected {n} active instance{"s" if n > 1 else ""} of ', 'warn'),
            (self.process_name + '\n\n', 'acc'),
            ('----------------------------------------------------------\n', 'dim'),
        ]
        
        for i, p in enumerate(procs, 1):
            msg += [
                (f' PROCESS [{i}]\n', 'h'),
                ('    PID    => ', 'dim'), (f'{p["pid"]}\n', 'ok'),
                ('    Memory => ', 'dim'), (f'{p["memory"]}\n', 'warn'),
                ('    Path   => ', 'dim'), (f'{p["path"]}\n', ''),
            ]
            if i < n:
                msg.append(('\n··························································\n\n', 'dim'))

        msg += [
            ('\n----------------------------------------------------------\n', 'dim'),
            ("ACTION REQUIRED: ", 'warn'),
            ('Press TERMINATE PROCESSES to close all instances safely.', 'dim'),
        ]
        self._log_write(msg)

    def kill_process(self):
        ok = messagebox.askokcancel(
            'High-Risk Operation Confirmation',
            'WARNING: You are about to forcefully terminate multiple game processes.\n\n'
            'Risks associated with multi-accounting & forceful closure:\n'
            '- Account suspension or permanent ban.\n'
            '- Corrupted local cache files.\n\n'
            'The developer assumes no responsibility for account bans.\n\n'
            'Do you want to proceed?',
            icon='warning',
        )
        if not ok:
            return

        def _do_kill():
            self.after(0, lambda: self._log_write([
                ('=> Executing termination sequence for ', 'err'),
                (self.process_name, 'acc'),
                (' ...\n', 'err'),
            ]))
            try:
                subprocess.run(
                    ['taskkill', '/F', '/IM', self.process_name],
                    capture_output=True, text=True, encoding='cp874',
                    creationflags=CREATE_NO_WINDOW)
                time.sleep(0.8)
                self.after(0, lambda: messagebox.showinfo(
                    'Sequence Complete',
                    f'All active processes of {self.process_name} have been neutralized.\n\n'
                    'You may now restart the application for multi-accounting.\n'
                    'Play safe!'
                ))
                self.after(0, self.scan)
            except Exception as e:
                self.after(0, lambda: messagebox.showerror(
                    'Operation Failed',
                    f'Could not complete termination sequence.\nDetails: {e}'
                ))

        threading.Thread(target=_do_kill, daemon=True).start()

if __name__ == '__main__':
    app = ProcessKillerApp()
    app.mainloop()
