import tkinter as tk
from tkinter import ttk, messagebox, font
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

class GlassFrame(tk.Canvas):
    """Glassmorphism effect frame"""
    def __init__(self, parent, bg_color, alpha=0.3, blur=20, **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        self.bg_color = bg_color
        self.alpha = alpha
        self.configure(bg=bg_color, highlightthickness=0)

class AnimatedGradient(tk.Canvas):
    """Animated gradient background"""
    def __init__(self, parent, colors, **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        self.colors = colors
        self.current_offset = 0
        self.bind("<Configure>", self._draw_gradient)
        
    def _draw_gradient(self, event=None):
        self.delete("gradient")
        width = self.winfo_width()
        height = self.winfo_height()
        
        # Create vertical gradient
        for i in range(height):
            ratio = i / height
            
            # Interpolate between colors
            if ratio < 0.5:
                r1, g1, b1 = self.winfo_rgb(self.colors[0])
                r2, g2, b2 = self.winfo_rgb(self.colors[1])
                local_ratio = ratio * 2
            else:
                r1, g1, b1 = self.winfo_rgb(self.colors[1])
                r2, g2, b2 = self.winfo_rgb(self.colors[2])
                local_ratio = (ratio - 0.5) * 2
            
            r = int(r1 + (r2 - r1) * local_ratio)
            g = int(g1 + (g2 - g1) * local_ratio)
            b = int(b1 + (b2 - b1) * local_ratio)
            
            color = f'#{r>>8:02x}{g>>8:02x}{b>>8:02x}'
            self.create_line(0, i, width, i, tags=("gradient",), fill=color)
        self.lower("gradient")

class ProcessKillerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Seven Knights Multi Screen")
        self.root.geometry("800x700")
        self.root.minsize(700, 600)  # ขนาดต่ำสุด
        self.root.resizable(True, True)  # เปิดให้ resize ได้
        
        # Set window icon (embedded in exe)
        try:
            import sys
            import os
            if getattr(sys, 'frozen', False):
                # Running as compiled exe
                application_path = sys._MEIPASS
            else:
                # Running as script
                application_path = os.path.dirname(os.path.abspath(__file__))
            
            icon_path = os.path.join(application_path, 'icon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass  # Ignore if icon not found
        
        # Premium color scheme
        self.colors = {
            'bg_start': '#0a0e27',
            'bg_mid': '#1a1f3a',
            'bg_end': '#2d1b4e',
            'accent': '#8b5cf6',
            'accent_light': '#a78bfa',
            'accent_glow': '#c4b5fd',
            'success': '#10b981',
            'success_glow': '#34d399',
            'error': '#ef4444',
            'error_glow': '#f87171',
            'warning': '#f59e0b',
            'warning_glow': '#fbbf24',
            'glass_bg': '#1e1b4b',
            'glass_border': '#4c1d95',
            'text_primary': '#f8fafc',
            'text_secondary': '#cbd5e1',
            'text_muted': '#94a3b8',
        }
        
        # Target process name
        self.process_name = "ProjectRE.exe"
        
        # Store widgets for dynamic resizing
        self.widgets = {}
        
        # Base window size for scaling
        self.base_width = 800
        self.base_height = 700
        
        self.setup_ui()
        self.update_process_status()
        
        # Bind resize event
        self.root.bind('<Configure>', self.on_window_resize)
        
    def get_scale_factor(self):
        """Calculate scale factor based on current window size"""
        current_width = self.root.winfo_width()
        current_height = self.root.winfo_height()
        
        # Use average of width and height scaling
        width_scale = current_width / self.base_width
        height_scale = current_height / self.base_height
        
        return (width_scale + height_scale) / 2
    
    def scale_font_size(self, base_size):
        """Scale font size based on window size"""
        scale = self.get_scale_factor()
        return max(6, int(base_size * scale))  # Minimum 6pt
    
    def on_window_resize(self, event=None):
        """Handle window resize to update font sizes"""
        if event and event.widget == self.root:
            # Update all text widgets with scaled fonts
            try:
                scale = self.get_scale_factor()
                
                # Update header
                if 'title' in self.widgets:
                    self.widgets['title'].config(font=("Segoe UI", self.scale_font_size(20), "bold"))
                if 'subtitle' in self.widgets:
                    self.widgets['subtitle'].config(font=("Segoe UI", self.scale_font_size(13), "bold"))
                if 'desc' in self.widgets:
                    self.widgets['desc'].config(font=("Segoe UI", self.scale_font_size(8)))
                
                # Update icons
                if 'icon_canvas' in self.widgets:
                    canvas = self.widgets['icon_canvas']
                    size = int(60 * scale)
                    canvas.config(width=size, height=size)
                    self.redraw_header_icon(canvas, size)
                
                if 'target_icon' in self.widgets:
                    self.widgets['target_icon'].config(font=("Segoe UI Emoji", self.scale_font_size(16)))
                if 'status_icon' in self.widgets:
                    self.status_icon.config(font=("Segoe UI Emoji", self.scale_font_size(16)))
                
                # Update card text
                if 'target_label' in self.widgets:
                    self.widgets['target_label'].config(font=("Segoe UI", self.scale_font_size(7), "bold"))
                if 'target_value' in self.widgets:
                    self.widgets['target_value'].config(font=("Segoe UI", self.scale_font_size(11), "bold"))
                
                if 'status_text_label' in self.widgets:
                    self.widgets['status_text_label'].config(font=("Segoe UI", self.scale_font_size(7), "bold"))
                if 'status_label' in self.widgets:
                    self.status_label.config(font=("Segoe UI", self.scale_font_size(12), "bold"))
                
                # Update info card
                if 'info_header_icon' in self.widgets:
                    self.widgets['info_header_icon'].config(font=("Segoe UI Emoji", self.scale_font_size(14)))
                if 'info_header_text' in self.widgets:
                    self.widgets['info_header_text'].config(font=("Segoe UI", self.scale_font_size(9), "bold"))
                if 'info_text' in self.widgets:
                    self.info_text.config(font=("Cascadia Mono", self.scale_font_size(8)))
                
                # Update footer
                if 'footer' in self.widgets:
                    self.widgets['footer'].config(font=("Segoe UI", self.scale_font_size(7)))
                    
            except:
                pass  # Ignore errors during resize
    
    def redraw_header_icon(self, canvas, size):
        """Redraw header icon with new size"""
        canvas.delete("all")
        center = size // 2
        
        # Glow effect
        for i in range(3, 0, -1):
            glow_size = center + (i * 3)
            color_val = int(139 + (i * 10))
            glow_color = f'#{color_val:02x}5cf6'
            canvas.create_oval(center-glow_size, center-glow_size, center+glow_size, center+glow_size, 
                             fill='', outline=glow_color, width=2)
        
        # Main icon
        icon_size = int(30 * (size / 60))
        canvas.create_text(center, center, text="⚔️", font=("Segoe UI Emoji", icon_size))
        
    def setup_ui(self):
        # Animated gradient background
        self.bg = AnimatedGradient(
            self.root,
            [self.colors['bg_start'], self.colors['bg_mid'], self.colors['bg_end']],
            highlightthickness=0
        )
        self.bg.pack(fill="both", expand=True)
        
        # Main container
        main_frame = tk.Frame(self.bg, bg=self.colors['bg_mid'])
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Top section (header + cards) - ไม่ expand
        top_section = tk.Frame(main_frame, bg=self.colors['bg_mid'])
        top_section.pack(fill="x")
        
        self._create_header(top_section)
        self._create_target_card(top_section)
        self._create_status_card(top_section)
        
        # Info card - expand แต่จำกัดความสูง
        self._create_info_card(main_frame)
        
        # Bottom section (buttons + footer) - ไม่ expand, อยู่ด้านล่างเสมอ
        bottom_section = tk.Frame(main_frame, bg=self.colors['bg_mid'])
        bottom_section.pack(fill="x", side="bottom")
        
        self._create_buttons(bottom_section)
        self._create_footer(bottom_section)
        
    def _create_header(self, parent):
        header = tk.Frame(parent, bg=self.colors['bg_mid'])
        header.pack(pady=(5, 5))
        
        # Icon with glow
        icon_canvas = tk.Canvas(header, width=60, height=60, bg=self.colors['bg_mid'], highlightthickness=0)
        icon_canvas.pack()
        self.widgets['icon_canvas'] = icon_canvas
        
        # Draw initial icon
        self.redraw_header_icon(icon_canvas, 60)
        
        # Title
        title = tk.Label(
            header,
            text="SEVEN KNIGHTS",
            font=("Segoe UI", 20, "bold"),
            bg=self.colors['bg_mid'],
            fg=self.colors['accent_light']
        )
        title.pack(pady=(5, 0))
        self.widgets['title'] = title
        
        # Subtitle
        subtitle = tk.Label(
            header,
            text="MULTI SCREEN",
            font=("Segoe UI", 13, "bold"),
            bg=self.colors['bg_mid'],
            fg=self.colors['text_primary']
        )
        subtitle.pack()
        self.widgets['subtitle'] = subtitle
        
        # Description
        desc = tk.Label(
            header,
            text="Multi-Instance Support • Run Multiple Accounts",
            font=("Segoe UI", 8),
            bg=self.colors['bg_mid'],
            fg=self.colors['text_muted']
        )
        desc.pack(pady=(2, 0))
        self.widgets['desc'] = desc
        
    def _create_glass_card(self, parent, **kwargs):
        """Create a glassmorphism card"""
        canvas = tk.Canvas(
            parent,
            bg=self.colors['glass_bg'],
            highlightthickness=0,
            **kwargs
        )
        
        # Draw border with glow
        w = kwargs.get('width', 700)
        h = kwargs.get('height', 100)
        
        # Outer glow
        canvas.create_rectangle(0, 0, w, h, outline=self.colors['glass_border'], width=1)
        
        return canvas
        
    def _create_target_card(self, parent):
        card_frame = tk.Frame(parent, bg=self.colors['bg_mid'])
        card_frame.pack(pady=4, fill="x")
        
        card_bg = tk.Frame(card_frame, bg=self.colors['glass_bg'], relief="flat", bd=0)
        card_bg.pack(fill="x", padx=2, pady=2)
        
        inner = tk.Frame(card_bg, bg=self.colors['glass_bg'])
        inner.pack(pady=8, padx=15, fill="x")
        
        # Icon
        icon_label = tk.Label(
            inner,
            text="🎯",
            font=("Segoe UI Emoji", 16),
            bg=self.colors['glass_bg'],
            fg=self.colors['warning_glow']
        )
        icon_label.pack(side="left", padx=(0, 10))
        self.widgets['target_icon'] = icon_label
        
        # Text container
        text_frame = tk.Frame(inner, bg=self.colors['glass_bg'])
        text_frame.pack(side="left", fill="x", expand=True)
        
        label = tk.Label(
            text_frame,
            text="TARGET PROCESS",
            font=("Segoe UI", 7, "bold"),
            bg=self.colors['glass_bg'],
            fg=self.colors['text_muted']
        )
        label.pack(anchor="w")
        self.widgets['target_label'] = label
        
        value = tk.Label(
            text_frame,
            text=self.process_name,
            font=("Segoe UI", 11, "bold"),
            bg=self.colors['glass_bg'],
            fg=self.colors['warning']
        )
        value.pack(anchor="w")
        self.widgets['target_value'] = value
        
    def _create_status_card(self, parent):
        card_frame = tk.Frame(parent, bg=self.colors['bg_mid'])
        card_frame.pack(pady=4, fill="x")
        
        card_bg = tk.Frame(card_frame, bg=self.colors['glass_bg'], relief="flat", bd=0)
        card_bg.pack(fill="x", padx=2, pady=2)
        
        inner = tk.Frame(card_bg, bg=self.colors['glass_bg'])
        inner.pack(pady=8, padx=15, fill="x")
        
        # Status icon
        self.status_icon = tk.Label(
            inner,
            text="⏳",
            font=("Segoe UI Emoji", 16),
            bg=self.colors['glass_bg']
        )
        self.status_icon.pack(side="left", padx=(0, 10))
        self.widgets['status_icon'] = self.status_icon
        
        # Status text
        status_text_frame = tk.Frame(inner, bg=self.colors['glass_bg'])
        status_text_frame.pack(side="left", fill="x", expand=True)
        
        status_text_label = tk.Label(
            status_text_frame,
            text="STATUS",
            font=("Segoe UI", 7, "bold"),
            bg=self.colors['glass_bg'],
            fg=self.colors['text_muted']
        )
        status_text_label.pack(anchor="w")
        self.widgets['status_text_label'] = status_text_label
        
        self.status_label = tk.Label(
            status_text_frame,
            text="Scanning...",
            font=("Segoe UI", 12, "bold"),
            bg=self.colors['glass_bg'],
            fg=self.colors['text_primary']
        )
        self.status_label.pack(anchor="w")
        self.widgets['status_label'] = self.status_label
        
    def _create_info_card(self, parent):
        card_frame = tk.Frame(parent, bg=self.colors['bg_mid'])
        card_frame.pack(pady=3, fill="both", expand=True)  # ลด padding จาก 4 เป็น 3
        
        card_bg = tk.Frame(card_frame, bg=self.colors['glass_bg'], relief="flat", bd=0)
        card_bg.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Header
        header = tk.Frame(card_bg, bg=self.colors['glass_bg'])
        header.pack(pady=(6, 2), padx=15, fill="x")  # ลด padding จาก 8,3 เป็น 6,2
        
        info_icon = tk.Label(
            header,
            text="📊",
            font=("Segoe UI Emoji", 14),
            bg=self.colors['glass_bg']
        )
        info_icon.pack(side="left", padx=(0, 8))
        self.widgets['info_header_icon'] = info_icon
        
        info_text_label = tk.Label(
            header,
            text="PROCESS DETAILS",
            font=("Segoe UI", 9, "bold"),
            bg=self.colors['glass_bg'],
            fg=self.colors['text_primary']
        )
        info_text_label.pack(side="left")
        self.widgets['info_header_text'] = info_text_label
        
        # Text area with custom styling
        text_frame = tk.Frame(card_bg, bg=self.colors['glass_bg'])
        text_frame.pack(pady=(0, 6), padx=15, fill="both", expand=True)  # ลด padding จาก 8 เป็น 6
        
        scrollbar = tk.Scrollbar(text_frame, bg=self.colors['glass_bg'])
        scrollbar.pack(side="right", fill="y")
        
        self.info_text = tk.Text(
            text_frame,
            height=8,  # กำหนดความสูงคงที่ 8 บรรทัด
            font=("Cascadia Mono", 8),
            bg='#0d1117',
            fg='#e6edf3',
            relief="flat",
            padx=10,
            pady=10,
            yscrollcommand=scrollbar.set,
            wrap="word",
            insertbackground=self.colors['accent'],
            selectbackground=self.colors['accent'],
            selectforeground="#ffffff",
            borderwidth=0
        )
        self.info_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.info_text.yview)
        self.info_text.config(state="disabled")
        self.widgets['info_text'] = self.info_text
        
    def _create_buttons(self, parent):
        button_frame = tk.Frame(parent, bg=self.colors['bg_mid'])
        button_frame.pack(pady=6)  # ลด padding จาก 8 เป็น 6
        
        # Kill button with glow
        self.kill_btn = self._create_glow_button(
            button_frame,
            text="🔴  TERMINATE",
            color=self.colors['error'],
            glow_color=self.colors['error_glow'],
            command=self.kill_process
        )
        self.kill_btn.pack(side="left", padx=6)
        
        # Refresh button with glow
        refresh_btn = self._create_glow_button(
            button_frame,
            text="🔄  REFRESH",
            color=self.colors['accent'],
            glow_color=self.colors['accent_glow'],
            command=self.update_process_status
        )
        refresh_btn.pack(side="left", padx=6)
        
    def _create_footer(self, parent):
        footer = tk.Label(
            parent,
            text="Seven Knights Multi Screen • Made with ❤️ by Yusinz & Claude",
            font=("Segoe UI", 7),
            bg=self.colors['bg_mid'],
            fg=self.colors['text_muted']
        )
        footer.pack(pady=(3, 3))
        self.widgets['footer'] = footer
        
    def _create_glow_button(self, parent, text, color, glow_color, command):
        """Create a button with glow effect"""
        container = tk.Frame(parent, bg=self.colors['bg_mid'])
        
        canvas = tk.Canvas(
            container,
            width=200,
            height=50,
            bg=self.colors['bg_mid'],
            highlightthickness=0
        )
        canvas.pack()
        
        # Store button state
        canvas.enabled = True
        canvas.base_color = color
        canvas.glow_color = glow_color
        canvas.text = text
        
        def draw_button(is_hover=False, is_pressed=False):
            canvas.delete("all")
            w, h = 200, 50
            
            # Glow layers
            if not is_pressed and canvas.enabled:
                glow_size = 8 if is_hover else 4
                for i in range(glow_size, 0, -1):
                    alpha = i / glow_size * 0.3
                    offset = i * 2
                    canvas.create_rectangle(
                        -offset, -offset, w+offset, h+offset,
                        outline=glow_color, width=1
                    )
            
            # Main button
            offset_y = 3 if is_pressed else 0
            btn_color = glow_color if is_hover and canvas.enabled else color
            
            if not canvas.enabled:
                btn_color = '#4b5563'
            
            # Button background
            canvas.create_rectangle(
                5, 5+offset_y, w-5, h-5+offset_y,
                fill=btn_color, outline='', width=0
            )
            
            # Top highlight
            if not is_pressed and canvas.enabled:
                highlight = '#ffffff' if is_hover else glow_color
                canvas.create_line(
                    10, 8+offset_y, w-10, 8+offset_y,
                    fill=highlight, width=2
                )
            
            # Text
            text_color = '#ffffff' if canvas.enabled else '#9ca3af'
            canvas.create_text(
                w//2, h//2+offset_y,
                text=text,
                fill=text_color,
                font=("Segoe UI", 11, "bold")
            )
        
        def on_enter(e):
            if canvas.enabled:
                draw_button(is_hover=True)
                canvas.config(cursor="hand2")
        
        def on_leave(e):
            draw_button(is_hover=False)
            canvas.config(cursor="")
        
        def on_press(e):
            if canvas.enabled:
                draw_button(is_hover=True, is_pressed=True)
        
        def on_release(e):
            if canvas.enabled:
                draw_button(is_hover=True, is_pressed=False)
                command()
        
        canvas.bind("<Enter>", on_enter)
        canvas.bind("<Leave>", on_leave)
        canvas.bind("<ButtonPress-1>", on_press)
        canvas.bind("<ButtonRelease-1>", on_release)
        
        draw_button()
        
        # Store canvas for later access
        container.canvas = canvas
        return container
    
    def get_process_path(self, pid):
        """Get the full path of a process by PID using multiple methods"""
        # Method 1: Try PowerShell (most reliable)
        try:
            ps_command = f'(Get-Process -Id {pid}).Path'
            result = subprocess.run(
                ['powershell', '-Command', ps_command],
                capture_output=True,
                text=True,
                timeout=3,
                creationflags=CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            path = result.stdout.strip()
            if path and os.path.exists(path):
                return path
        except:
            pass
        
        # Method 2: Try WMIC
        try:
            result = subprocess.run(
                ['wmic', 'process', 'where', f'ProcessId={pid}', 'get', 'ExecutablePath', '/value'],
                capture_output=True,
                text=True,
                encoding='cp874',
                timeout=3,
                creationflags=CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            for line in result.stdout.split('\n'):
                if 'ExecutablePath=' in line:
                    path = line.split('=', 1)[1].strip()
                    if path and os.path.exists(path):
                        return path
        except:
            pass
        
        return "Unable to determine location (Try running as Administrator)"
    
    def check_process(self):
        """Check for running ProjectRE.exe processes"""
        try:
            result = subprocess.run(
                ['tasklist', '/FI', f'IMAGENAME eq {self.process_name}', '/FO', 'CSV', '/V'],
                capture_output=True,
                text=True,
                encoding='cp874',
                creationflags=CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            
            lines = result.stdout.strip().split('\n')
            processes = []
            
            for line in lines[1:]:  # Skip header
                if self.process_name in line:
                    parts = line.replace('"', '').split(',')
                    if len(parts) >= 2:
                        pid = parts[1]
                        path = self.get_process_path(pid)
                        
                        # Get memory in MB
                        memory_kb = parts[4] if len(parts) > 4 else '0'
                        try:
                            memory_mb = f"{int(memory_kb.replace(' K', '').replace(',', '')) / 1024:.1f} MB"
                        except:
                            memory_mb = memory_kb
                        
                        processes.append({
                            'name': parts[0],
                            'pid': pid,
                            'memory': memory_mb,
                            'path': path
                        })
            
            return processes
        except Exception as e:
            return None
            
    def update_process_status(self):
        def update():
            self.update_info_text("🔍 Scanning for processes...\n⏳ Please wait...")
            processes = self.check_process()
            
            if processes is None:
                self.status_icon.config(text="❌")
                self.status_label.config(
                    text="Error",
                    fg=self.colors['error']
                )
                self.kill_btn.canvas.enabled = False
                self.kill_btn.canvas.delete("all")
                self.kill_btn.canvas.create_rectangle(5, 5, 195, 45, fill='#4b5563', outline='')
                self.kill_btn.canvas.create_text(100, 25, text="🔴  TERMINATE", fill='#9ca3af', font=("Segoe UI", 11, "bold"))
                
                self.update_info_text(
                    "❌ Unable to check process status\n\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "💡 Suggestions:\n"
                    "  • Try running this program as Administrator\n"
                    "  • Check if Windows Management Instrumentation is running"
                )
                return
                
            if len(processes) == 0:
                self.status_icon.config(text="✅")
                self.status_label.config(
                    text="Ready",
                    fg=self.colors['success']
                )
                self.kill_btn.canvas.enabled = False
                self.kill_btn.canvas.delete("all")
                self.kill_btn.canvas.create_rectangle(5, 5, 195, 45, fill='#4b5563', outline='')
                self.kill_btn.canvas.create_text(100, 25, text="🔴  TERMINATE", fill='#9ca3af', font=("Segoe UI", 11, "bold"))
                
                self.update_info_text(
                    f"✅ No {self.process_name} processes found\n\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "🎮 Status: Ready to launch\n\n"
                    "💡 You can now:\n"
                    "  ✓ Launch multiple game instances\n"
                    "  ✓ Run unlimited accounts simultaneously\n\n"
                    "🚀 Start playing now!"
                )
            else:
                self.status_icon.config(text="⚠️")
                self.status_label.config(
                    text=f"{len(processes)} Process{'es' if len(processes) > 1 else ''} Found",
                    fg=self.colors['warning']
                )
                self.kill_btn.canvas.enabled = True
                
                # Redraw button in enabled state
                def redraw():
                    self.kill_btn.canvas.delete("all")
                    self.kill_btn.canvas.create_rectangle(5, 5, 195, 45, fill=self.colors['error'], outline='')
                    self.kill_btn.canvas.create_text(100, 25, text="🔴  TERMINATE", fill='#ffffff', font=("Segoe UI", 11, "bold"))
                redraw()
                
                info = f"⚠️ Detected {self.process_name} running ({len(processes)} process{'es' if len(processes) > 1 else ''})\n\n"
                info += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                
                for i, proc in enumerate(processes, 1):
                    info += f"🎯 Process #{i}\n"
                    info += f"├─ PID:      {proc['pid']}\n"
                    info += f"├─ Memory:   {proc['memory']}\n"
                    info += f"└─ Location: {proc['path']}\n"
                    
                    if i < len(processes):
                        info += "\n" + "─" * 65 + "\n\n"
                
                info += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                info += "💡 Click 'TERMINATE' to close all processes and launch new instances"
                
                self.update_info_text(info)
        
        threading.Thread(target=update, daemon=True).start()
        
    def update_info_text(self, text):
        self.info_text.config(state="normal")
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, text)
        self.info_text.config(state="disabled")
        
    def kill_process(self):
        if not self.kill_btn.canvas.enabled:
            return
        
        # แสดงคำเตือนก่อนดำเนินการ
        warning_result = messagebox.askokcancel(
            "⚠️ คำเตือนสำคัญ",
            "⚠️ คำเตือน: การใช้งานเครื่องมือนี้มีความเสี่ยง!\n\n"
            "🚫 ความเสี่ยงที่อาจเกิดขึ้น:\n"
            "  • บัญชีของคุณอาจถูกแบนจากเกม\n"
            "  • อาจไม่สามารถใช้บัญชีนี้ได้อีก\n"
            "  • อาจถูกระงับการใช้งานถาวร\n\n"
            "⚡ การรันหลายบัญชีพร้อมกันอาจขัดต่อข้อกำหนดการใช้งาน\n\n"
            "💡 คุณใช้เครื่องมือนี้ด้วยความเสี่ยงของตัวคุณเอง\n"
            "   ผู้พัฒนาไม่รับผิดชอบต่อความเสียหายใดๆ\n\n"
            "❓ คุณต้องการดำเนินการต่อหรือไม่?",
            icon='warning'
        )
        
        if not warning_result:
            return  # ผู้ใช้กด Cancel
            
        def kill():
            try:
                self.root.after(0, lambda: self.update_info_text(
                    "⏳ Processing...\n\n"
                    "🔄 Terminating ProjectRE.exe processes\n"
                    "⏱️  Please wait..."
                ))
                
                result = subprocess.run(
                    ['taskkill', '/F', '/IM', self.process_name],
                    capture_output=True,
                    text=True,
                    encoding='cp874',
                    creationflags=CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                )
                
                time.sleep(0.8)
                
                self.root.after(0, lambda: messagebox.showinfo(
                    "✅ Success",
                    f"Successfully terminated {self.process_name}!\n\n"
                    "🎮 You can now:\n"
                    "  • Launch multiple game instances\n"
                    "  • Run unlimited accounts\n\n"
                    "⚠️ Remember: Use at your own risk!\n"
                    "✨ Start playing!"
                ))
                
                self.root.after(0, self.update_process_status)
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "❌ Error",
                    f"Unable to terminate process\n\n"
                    f"Details: {str(e)}\n\n"
                    "💡 Suggestions:\n"
                    "  • Try running as Administrator\n"
                    "  • Check if the process is still running"
                ))
        
        threading.Thread(target=kill, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = ProcessKillerApp(root)
    root.mainloop()
