#!/usr/bin/env python3
"""
mini_martes.py - Mascota de Escritorio Inteligente "Martes" (Desktop Pet AI)
Edición Portable Independiente - 100% Local, Pixel Art animado con 3 paletas.
- Mirada direccional (arriba, abajo, izquierda, derecha, centro)
- Parpadeo natural y direccional
- Animación de concentración en 2 fases al pensar
- Reacción de sorpresa / alerta (!) al ser invocado con Ctrl+Alt+M
- Modo siesta por inactividad con ojos dormilones (v v) y Zzz flotantes
- Acrobacias: ¡Backflip autónomo y manual (Salto Mortal 360°)!
- Motor de personalidad autónomo y conexión opcional con Ollama
"""

import os
import sys
import math
import time
import json
import random
import threading
import urllib.request
import ctypes
from ctypes import wintypes
import subprocess
import re
import tkinter as tk
from tkinter import messagebox

# Resolución de rutas (compatible con ejecución directa y PyInstaller .EXE)
if getattr(sys, 'frozen', False):
    BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    EXE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    EXE_DIR = BASE_DIR

# Buscar assets empaquetados o junto al ejecutable
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
if not os.path.exists(ASSETS_DIR):
    ASSETS_DIR = os.path.join(EXE_DIR, "assets")

# Configuración del modelo local Ollama (opcional)
OLLAMA_API_URL = "http://127.0.0.1:11434/api/chat"
MODEL_NAME = "mart-es:latest"

# ----------------------------------------------------
# CONFIGURACIÓN DE VERSIÓN Y AUTO-UPDATER (GITHUB)
# ----------------------------------------------------
APP_VERSION = "1.0.0"
GITHUB_USER = "kenzeta-cyber"   # <- Nombre de usuario en GitHub
GITHUB_REPO = "mart-es-portable"  # <- Nombre del repositorio en GitHub
UPDATE_CHECK_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/version.json"

# ----------------------------------------------------
# OBTENER POSICIÓN GLOBAL DEL RATÓN EN WINDOWS
# ----------------------------------------------------
def get_mouse_pos():
    if os.name == 'nt':
        pt = wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        return pt.x, pt.y
    return 0, 0

# ----------------------------------------------------
# TEMAS DE PALETAS DISPONIBLES (3 PALETAS OFICIALES)
# ----------------------------------------------------
PALETTE_THEMES = {
    "marte": {
        "name": "Marte Ámbar (Terracota)",
        "bg": "#1e0f0a",
        "border": "#d68e49",
        "text": "#f7e7c6",
        "accent": "#ff7b00",
        "input_bg": "#120805"
    },
    "verde": {
        "name": "Verde Clásico (Retro Game Boy)",
        "bg": "#081820",
        "border": "#346856",
        "text": "#e0f8d0",
        "accent": "#88c070",
        "input_bg": "#040c10"
    },
    "cyber": {
        "name": "Cyberpunk (Oro & Oliva)",
        "bg": "#0c0e0b",
        "border": "#424a3c",
        "text": "#f9d75c",
        "accent": "#f9d75c",
        "input_bg": "#090c07"
    }
}

class MiniMartesPet:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Martes Pet")
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        
        # Color transparente para Windows
        self.trans_color = "#010101"
        self.root.config(bg=self.trans_color)
        self.root.attributes("-transparentcolor", self.trans_color)

        # Dimensiones del sprite (70x80 px)
        self.sprite_w = 70
        self.sprite_h = 80
        self.padding = 6
        self.win_w = self.sprite_w + self.padding * 2
        self.win_h = self.sprite_h + self.padding * 2

        # Dimensiones de pantalla
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()

        # Posición inicial (esquina inferior derecha)
        self.pos_x = float(self.screen_w - self.win_w - 60)
        self.pos_y = float(self.screen_h - self.win_h - 100)

        # Configuración de paleta actual
        self.current_palette = "marte"
        self.frames = {}
        self._load_sprites()

        # Icono oficial de la ventana
        ico_path = os.path.join(ASSETS_DIR, "martes.ico")
        if os.path.exists(ico_path):
            try:
                self.root.iconbitmap(ico_path)
            except Exception:
                pass

        # Verificación silenciosa de actualizaciones en segundo plano tras 3s
        self.root.after(3000, self.check_for_updates_silent)

        # Estado del personaje
        self.current_dir = "center"
        self.is_wandering = True
        self.speed = 1.6
        self.vx = 0.0
        self.vy = 0.0
        self.proximity_radius = 220.0
        self.tick_count = 0
        self.bob_phase = 0.0

        # Sistema de "Vida"
        self.is_blinking = False
        self.blink_countdown = random.randint(70, 160)
        self.blink_duration = 0

        self.alert_duration = 0

        self.is_thinking = False
        self.thinking_timer = 0

        self.is_sleeping = False
        self.last_activity_time = time.time()
        self.last_mouse_pos = get_mouse_pos()
        self.inactivity_sleep_delay = 90.0
        self.zzz_items = []

        self.hop_offset = 0.0
        self.hop_vel = 0.0

        # Sistema de Animaciones de Intermedio (Idle Flavor / Backflip)
        self.is_doing_backflip = False
        self.backflip_tick = 0
        self.backflip_total_ticks = 32
        self.backflip_sprite = "center"
        self.backflip_dir_x = -1.0
        self.idle_flavor_countdown = random.randint(550, 1200)

        # Temporizadores de IA de movimiento
        self.wander_timer = 0
        self.idle_pause_timer = 0

        # Arrastre con ratón
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.is_dragging = False
        self.has_dragged = False

        # Diálogo y preguntas
        self.dialog_window = None

        # Canvas para el sprite
        self.canvas = tk.Canvas(
            self.root,
            width=self.win_w,
            height=self.win_h,
            bg=self.trans_color,
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.sprite_item = self.canvas.create_image(
            self.win_w // 2,
            self.win_h // 2,
            image=self.frames[self.current_palette]["center"]
        )

        # Eventos del ratón sobre Martes
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_motion)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Double-Button-1>", self._on_double_click)
        self.canvas.bind("<Button-3>", self._show_context_menu)

        # Menú contextual de clic derecho
        self._build_context_menu()

        # Iniciar oyente de atajo global de teclado (Ctrl + Alt + M)
        self._start_global_hotkey()

        # Posicionar ventana inicial
        self._update_window_pos()

        # Iniciar ciclo de actualización
        self._update_loop()

    def _load_sprites(self):
        sprite_names = [
            "center", "up", "down", "left", "right",
            "blink_center", "blink_up", "blink_down", "blink_left", "blink_right",
            "thinking_1", "thinking_2", "alert", "sleep",
            "flip_45", "flip_90", "flip_135", "flip_180", "flip_225", "flip_270", "flip_315"
        ]
        for pal in ["marte", "verde", "cyber"]:
            self.frames[pal] = {}
            for name in sprite_names:
                path = os.path.join(ASSETS_DIR, f"{pal}_{name}.png")
                if os.path.exists(path):
                    self.frames[pal][name] = tk.PhotoImage(file=path)
                else:
                    if "center" in self.frames[pal]:
                        self.frames[pal][name] = self.frames[pal]["center"]

    def _build_context_menu(self):
        self.menu = tk.Menu(self.root, tearoff=0, bg="#1a110a", fg="#ffe5cc", activebackground="#ff7b00", activeforeground="#000")
        
        palette_menu = tk.Menu(self.menu, tearoff=0, bg="#1a110a", fg="#ffe5cc", activebackground="#ff7b00")
        palette_menu.add_command(label="🪐 Marte Ámbar (Terracota)", command=lambda: self.set_palette("marte"))
        palette_menu.add_command(label="🟩 Verde Clásico (Retro Game Boy)", command=lambda: self.set_palette("verde"))
        palette_menu.add_command(label="✨ Cyberpunk (Oro & Oliva)", command=lambda: self.set_palette("cyber"))
        self.menu.add_cascade(label="🎨 Cambiar Paleta", menu=palette_menu)

        self.menu.add_separator()
        self.menu.add_command(label="💬 Preguntarle algo (Ctrl+Alt+M)", command=self.open_dialog)
        self.menu.add_command(label="🤸 Hacer Backflip (Mortal 360°)", command=self.start_backflip)
        self.menu.add_command(label="🐾 Alternar Paseo / Quieto", command=self.toggle_wander)
        self.menu.add_command(label="💤 Echarse una siesta / Despertar", command=self.toggle_sleep)
        self.menu.add_separator()
        self.menu.add_command(label="🔄 Buscar Actualizaciones...", command=self.check_for_updates_manual)
        self.menu.add_command(label="❌ Salir", command=self.quit_app)

    def _show_context_menu(self, event):
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def _start_global_hotkey(self):
        def hotkey_thread():
            user32 = ctypes.windll.user32
            MOD_ALT = 0x0001
            MOD_CONTROL = 0x0002
            VK_M = 0x4D
            HOTKEY_ID = 999

            success = user32.RegisterHotKey(None, HOTKEY_ID, MOD_CONTROL | MOD_ALT, VK_M)
            if not success:
                return

            msg = wintypes.MSG()
            while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
                if msg.message == 0x0312:
                    if msg.wParam == HOTKEY_ID:
                        self.root.after(0, self.summon_to_cursor)
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))

        t = threading.Thread(target=hotkey_thread, daemon=True)
        t.start()

    def summon_to_cursor(self):
        self.root.deiconify()
        self.wake_up()

        mx, my = get_mouse_pos()
        self.pos_x = float(mx - (self.win_w / 2))
        self.pos_y = float(my - self.win_h - 25)
        self._clamp_to_screen()
        self._update_window_pos()

        self.alert_duration = 25
        self.do_hop(height=-14.0)
        self._update_sprite_image()
        self.open_dialog()

    def set_palette(self, pal):
        if pal in self.frames:
            self.current_palette = pal
            self._update_sprite_image()
            if self.dialog_window and self.dialog_window.winfo_exists():
                self.open_dialog()

    def toggle_wander(self):
        self.is_wandering = not self.is_wandering
        if not self.is_wandering:
            self.vx = 0
            self.vy = 0
            self.current_dir = "center"
            self._update_sprite_image()

    def toggle_sleep(self):
        if self.is_sleeping:
            self.wake_up()
        else:
            self.fall_asleep()

    def fall_asleep(self):
        self.is_sleeping = True
        self.is_doing_backflip = False
        self.vx = 0
        self.vy = 0
        self.alert_duration = 0
        self._update_sprite_image()

    def wake_up(self):
        if self.is_sleeping:
            self.is_sleeping = False
            self.last_activity_time = time.time()
            self._clear_zzz()
            self.alert_duration = 22
            self.do_hop(height=-14.0)
            self.current_dir = "center"
            self._update_sprite_image()

    def do_hop(self, height=-12.0):
        self.hop_vel = height

    def start_backflip(self):
        """Inicia la acrobacia del Backflip (Salto Mortal 360°)"""
        if self.is_doing_backflip or self.is_dragging:
            return
            
        if self.is_sleeping:
            self.wake_up()

        self.is_doing_backflip = True
        self.backflip_tick = 0
        self.backflip_sprite = "center"
        self.vx = 0.0
        self.vy = 0.0

        if self.current_dir == "right":
            self.backflip_dir_x = -1.0
        elif self.current_dir == "left":
            self.backflip_dir_x = 1.0
        else:
            self.backflip_dir_x = -1.0 if self.pos_x > (self.screen_w / 2) else 1.0

        if self.pos_x < 65:
            self.backflip_dir_x = 1.0
        elif self.pos_x > (self.screen_w - self.win_w - 65):
            self.backflip_dir_x = -1.0

        self._update_sprite_image()

    def _update_backflip(self):
        t = self.backflip_tick
        total = self.backflip_total_ticks

        if t == 4:
            try:
                import winsound
                winsound.Beep(587, 60)
            except Exception:
                pass

        if t < 4:
            self.hop_offset = 3.0 * (t / 3.0)
            self.backflip_sprite = "center"
        elif t < 27:
            flight_t = (t - 4) / 23.0
            apex = 52.0
            self.hop_offset = -apex * (4.0 * flight_t * (1.0 - flight_t))
            self.pos_x += self.backflip_dir_x * 0.95
            self._clamp_to_screen()

            rot_angles = [45, 90, 135, 180, 225, 270, 315]
            if self.backflip_dir_x < 0:
                frame_idx = min(6, int(flight_t * 7))
            else:
                frame_idx = 6 - min(6, int(flight_t * 7))

            ang = rot_angles[frame_idx]
            self.backflip_sprite = f"flip_{ang}"
        else:
            if t == 27:
                self.hop_offset = 0.0
                try:
                    import winsound
                    winsound.Beep(880, 70)
                    winsound.Beep(1175, 90)
                except Exception:
                    pass
            elif t == 28:
                self.hop_offset = 2.0
            elif t == 29:
                self.hop_offset = -3.0
            else:
                self.hop_offset = 0.0

            self.backflip_sprite = "center"

        self._update_sprite_image()
        self._update_window_pos()
        if self.dialog_window and self.dialog_window.winfo_exists():
            self._reposition_dialog()

        self.backflip_tick += 1
        if self.backflip_tick >= total:
            self.is_doing_backflip = False
            self.hop_offset = 0.0
            self.alert_duration = 18
            self.current_dir = "center"
            self._update_sprite_image()

    def quit_app(self):
        if self.dialog_window and self.dialog_window.winfo_exists():
            self.dialog_window.destroy()
        self.root.destroy()
        sys.exit(0)

    # ----------------------------------------------------
    # SISTEMA DE ACTUALIZACIÓN AUTOMÁTICA VÍA GITHUB
    # ----------------------------------------------------
    def check_for_updates_silent(self):
        """Comprobación silenciosa en segundo plano al iniciar."""
        threading.Thread(target=self._check_updates_worker, args=(False,), daemon=True).start()

    def check_for_updates_manual(self):
        """Comprobación manual invocada desde el menú contextual."""
        threading.Thread(target=self._check_updates_worker, args=(True,), daemon=True).start()

    def _check_updates_worker(self, manual=False):
        if GITHUB_USER == "TU_USUARIO":
            if manual:
                self.root.after(0, lambda: messagebox.showinfo(
                    "Martes - Actualizaciones",
                    f"Martes Mini v{APP_VERSION} ✨\n\n"
                    "El repositorio de GitHub aún no está vinculado.\n"
                    "Para activar las actualizaciones automáticas, indica tu usuario\n"
                    "y repositorio de GitHub en mini_martes.py."
                ))
            return

        try:
            req = urllib.request.Request(
                UPDATE_CHECK_URL,
                headers={"User-Agent": f"Martes-Mini/{APP_VERSION}"}
            )
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            remote_ver = str(data.get("version", "")).strip()
            notes = str(data.get("notes", "Mejoras de rendimiento y correcciones.")).strip()
            download_url = str(data.get("download_url", "")).strip()

            def parse_ver(v):
                nums = [int(x) for x in re.findall(r'\d+', str(v))]
                return nums if nums else [0]

            if parse_ver(remote_ver) > parse_ver(APP_VERSION):
                self.root.after(0, lambda: self._prompt_update(remote_ver, notes, download_url))
            else:
                if manual:
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Martes - Actualizaciones",
                        f"¡Tienes la versión más reciente! ✨\n\nVersión actual: v{APP_VERSION}"
                    ))
        except Exception as e:
            if manual:
                self.root.after(0, lambda: messagebox.showwarning(
                    "Martes - Actualizaciones",
                    f"No se pudo comprobar si hay actualizaciones.\n\nVerifica tu conexión a internet o el repositorio.\n(Detalle: {e})"
                ))

    def _prompt_update(self, new_ver, notes, download_url):
        msg = (
            f"¡Hay una nueva versión disponible de Martes! 🚀\n\n"
            f"• Versión instalada: v{APP_VERSION}\n"
            f"• Nueva versión: v{new_ver}\n\n"
            f"Novedades:\n{notes}\n\n"
            f"¿Deseas descargar e instalar la actualización ahora?"
        )
        if messagebox.askyesno("Martes - Actualización disponible", msg):
            self._start_download_update(new_ver, download_url)

    def _start_download_update(self, new_ver, download_url):
        theme = PALETTE_THEMES[self.current_palette]
        prog_win = tk.Toplevel(self.root)
        prog_win.title("Actualizando Martes")
        prog_win.attributes("-topmost", True)
        prog_win.overrideredirect(True)
        prog_win.config(bg=theme["border"])

        ico_path = os.path.join(ASSETS_DIR, "martes.ico")
        if os.path.exists(ico_path):
            try:
                prog_win.iconbitmap(ico_path)
            except Exception:
                pass

        pw, ph = 290, 105
        px = int(self.pos_x + (self.win_w / 2) - (pw / 2))
        py = int(self.pos_y - ph - 10)
        if py < 10:
            py = int(self.pos_y + self.win_h + 10)
        px = max(10, min(px, self.screen_w - pw - 10))
        prog_win.geometry(f"{pw}x{ph}+{px}+{py}")

        inner = tk.Frame(prog_win, bg=theme["bg"], bd=0)
        inner.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        lbl = tk.Label(
            inner,
            text=f"◈ Actualizando a v{new_ver} 🚀",
            font=("Consolas", 9, "bold"),
            fg=theme["accent"],
            bg=theme["bg"]
        )
        lbl.pack(pady=(8, 2))

        status_lbl = tk.Label(
            inner,
            text="Conectando...",
            font=("Consolas", 8),
            fg=theme["text"],
            bg=theme["bg"]
        )
        status_lbl.pack(pady=(0, 6))

        bar_canvas = tk.Canvas(inner, width=250, height=8, bg=theme["input_bg"], highlightthickness=1, highlightbackground=theme["border"])
        bar_canvas.pack(pady=(0, 6))
        bar_rect = bar_canvas.create_rectangle(0, 0, 0, 8, fill=theme["accent"], width=0)

        def worker():
            temp_exe = os.path.join(EXE_DIR, "Martes_update.exe")
            try:
                req = urllib.request.Request(
                    download_url,
                    headers={"User-Agent": f"Martes-Mini/{APP_VERSION}"}
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    total_size = int(resp.headers.get("content-length", 0))
                    downloaded = 0
                    chunk_size = 64 * 1024
                    with open(temp_exe, "wb") as f:
                        while True:
                            chunk = resp.read(chunk_size)
                            if not chunk:
                                break
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                frac = min(1.0, downloaded / total_size)
                                pct = int(frac * 100)
                                mb_down = downloaded / (1024 * 1024)
                                mb_tot = total_size / (1024 * 1024)
                                msg = f"{mb_down:.1f} MB / {mb_tot:.1f} MB ({pct}%)"
                                def update_ui(m=msg, w=frac * 250):
                                    if prog_win.winfo_exists():
                                        status_lbl.config(text=m)
                                        bar_canvas.coords(bar_rect, 0, 0, w, 8)
                                self.root.after(0, update_ui)
                            else:
                                mb_down = downloaded / (1024 * 1024)
                                msg = f"{mb_down:.1f} MB descargados..."
                                self.root.after(0, lambda m=msg: status_lbl.config(text=m) if prog_win.winfo_exists() else None)

                def on_done():
                    if prog_win.winfo_exists():
                        status_lbl.config(text="¡Instalando y reiniciando...")
                        bar_canvas.coords(bar_rect, 0, 0, 250, 8)
                    self.root.after(600, lambda: self._apply_update_and_restart(temp_exe))

                self.root.after(0, on_done)
            except Exception as e:
                def on_err():
                    if prog_win.winfo_exists():
                        prog_win.destroy()
                    messagebox.showerror("Error al actualizar", f"No se pudo descargar la actualización:\n{e}")
                self.root.after(0, on_err)

        threading.Thread(target=worker, daemon=True).start()

    def _apply_update_and_restart(self, temp_exe):
        is_frozen = getattr(sys, 'frozen', False)
        target_exe = sys.executable if is_frozen else os.path.join(EXE_DIR, "Martes.exe")
        target_name = os.path.basename(target_exe)
        updater_bat = os.path.join(EXE_DIR, "updater.bat")

        bat_script = f"""@echo off
chcp 65001 >nul
timeout /t 1 /nobreak >nul
:wait_proc
tasklist /fi "imagename eq {target_name}" 2>nul | find /i "{target_name}" >nul
if not errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto wait_proc
)
move /y "{temp_exe}" "{target_exe}" >nul
start "" "{target_exe}"
del "%~f0"
"""
        with open(updater_bat, "w", encoding="utf-8") as f:
            f.write(bat_script)

        CREATE_NO_WINDOW = 0x08000000
        subprocess.Popen([updater_bat], shell=True, creationflags=CREATE_NO_WINDOW)
        self.root.destroy()
        sys.exit(0)

    def _on_press(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.is_dragging = True
        self.has_dragged = False
        if self.is_sleeping:
            self.wake_up()

    def _on_motion(self, event):
        if self.is_dragging:
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y
            if abs(dx) > 3 or abs(dy) > 3:
                self.has_dragged = True
                self.pos_x += dx
                self.pos_y += dy
                self._clamp_to_screen()
                self._update_window_pos()
                if self.dialog_window and self.dialog_window.winfo_exists():
                    self._reposition_dialog()

    def _on_release(self, event):
        self.is_dragging = False
        if not self.has_dragged:
            self.toggle_dialog()

    def _on_double_click(self, event):
        if self.is_sleeping:
            self.wake_up()
        else:
            self.start_backflip()

    def _clamp_to_screen(self):
        max_x = self.screen_w - self.win_w
        max_y = self.screen_h - self.win_h - 45
        self.pos_x = max(10, min(self.pos_x, max_x - 10))
        self.pos_y = max(10, min(self.pos_y, max_y - 10))

    def _update_window_pos(self):
        bob_offset = int(math.sin(self.bob_phase) * 3) if not self.is_dragging and not self.is_sleeping and not self.is_doing_backflip else 0
        cur_y = int(self.pos_y + bob_offset + self.hop_offset)
        self.root.geometry(f"{self.win_w}x{self.win_h}+{int(self.pos_x)}+{cur_y}")

    def _update_sprite_image(self):
        active_sprite = "center"

        if self.is_doing_backflip:
            active_sprite = self.backflip_sprite
        elif self.alert_duration > 0:
            active_sprite = "alert"
        elif self.is_sleeping:
            active_sprite = "sleep"
        elif self.is_thinking:
            if self.thinking_timer <= 15:
                active_sprite = "thinking_1"
            else:
                active_sprite = "thinking_2"
        elif self.is_blinking:
            active_sprite = f"blink_{self.current_dir}"
            if active_sprite not in self.frames[self.current_palette]:
                active_sprite = "blink_center"
        else:
            active_sprite = self.current_dir

        img = self.frames[self.current_palette].get(active_sprite)
        if not img:
            img = self.frames[self.current_palette].get("center")
        if img:
            self.canvas.itemconfig(self.sprite_item, image=img)

    def _update_zzz(self):
        theme = PALETTE_THEMES[self.current_palette]
        if self.tick_count % 35 == 0:
            tx = (self.win_w // 2) + random.randint(10, 25)
            ty = (self.win_h // 2) - 10
            char = random.choice(["z", "Z", "·"])
            item = self.canvas.create_text(
                tx, ty,
                text=char,
                font=("Consolas", 10, "bold"),
                fill=theme["accent"]
            )
            self.zzz_items.append({"id": item, "life": 40, "vx": random.uniform(0.3, 0.7), "vy": -0.8})

        remaining = []
        for z in self.zzz_items:
            self.canvas.move(z["id"], z["vx"], z["vy"])
            z["life"] -= 1
            if z["life"] > 0:
                remaining.append(z)
            else:
                self.canvas.delete(z["id"])
        self.zzz_items = remaining

    def _clear_zzz(self):
        for z in self.zzz_items:
            self.canvas.delete(z["id"])
        self.zzz_items.clear()

    def _update_loop(self):
        self.tick_count += 1
        self.bob_phase += 0.10

        if self.is_doing_backflip:
            self._update_backflip()
            self.root.after(33, self._update_loop)
            return

        if self.alert_duration > 0:
            self.alert_duration -= 1
            if self.alert_duration == 0:
                self._update_sprite_image()

        if self.hop_vel != 0.0 or self.hop_offset < 0.0:
            self.hop_offset += self.hop_vel
            self.hop_vel += 1.4
            if self.hop_offset >= 0.0:
                self.hop_offset = 0.0
                self.hop_vel = 0.0

        mx, my = get_mouse_pos()
        center_x = self.pos_x + (self.win_w / 2.0)
        center_y = self.pos_y + (self.win_h / 2.0)
        dx = mx - center_x
        dy = my - center_y
        dist = math.hypot(dx, dy)

        if abs(mx - self.last_mouse_pos[0]) > 4 or abs(my - self.last_mouse_pos[1]) > 4:
            self.last_activity_time = time.time()
            self.last_mouse_pos = (mx, my)
            if self.is_sleeping and dist <= self.proximity_radius:
                self.wake_up()

        if not self.is_sleeping and not self.is_thinking:
            if time.time() - self.last_activity_time > self.inactivity_sleep_delay:
                self.fall_asleep()

        if self.is_sleeping:
            self._update_zzz()
            self._update_sprite_image()
            self._update_window_pos()
            self.root.after(33, self._update_loop)
            return
        else:
            if self.zzz_items:
                self._clear_zzz()

        if self.is_thinking:
            self.thinking_timer += 1
            self.vx = 0
            self.vy = 0
            self._update_sprite_image()
            self._update_window_pos()
            self.root.after(33, self._update_loop)
            return

        # Animación autónoma de intermedio (Backflip)
        if not self.is_sleeping and not self.is_thinking and not self.is_dragging:
            if (not self.dialog_window or not self.dialog_window.winfo_exists()) and dist > self.proximity_radius:
                self.idle_flavor_countdown -= 1
                if self.idle_flavor_countdown <= 0:
                    self.start_backflip()
                    self.idle_flavor_countdown = random.randint(650, 1350)
                    self.root.after(33, self._update_loop)
                    return

        # Parpadeo natural
        if not self.is_blinking:
            self.blink_countdown -= 1
            if self.blink_countdown <= 0:
                self.is_blinking = True
                self.blink_duration = random.randint(4, 7)
                self.blink_countdown = random.randint(80, 180)
                self._update_sprite_image()
        else:
            self.blink_duration -= 1
            if self.blink_duration <= 0:
                self.is_blinking = False
                self._update_sprite_image()

        if not self.is_dragging:
            if dist <= self.proximity_radius and mx >= 0 and my >= 0:
                self.vx = 0
                self.vy = 0
                new_dir = "center"
                if abs(dx) < 28 and abs(dy) < 28:
                    new_dir = "center"
                elif abs(dx) > abs(dy):
                    new_dir = "right" if dx > 0 else "left"
                else:
                    new_dir = "down" if dy > 0 else "up"

                if new_dir != self.current_dir:
                    self.current_dir = new_dir
                    self._update_sprite_image()
            elif self.is_wandering:
                self._update_wandering()

            self._update_window_pos()

        self.root.after(33, self._update_loop)

    def _update_wandering(self):
        if self.idle_pause_timer > 0:
            self.idle_pause_timer -= 1
            self.vx = 0
            self.vy = 0
            if self.current_dir != "center":
                self.current_dir = "center"
                self._update_sprite_image()
            return

        self.wander_timer -= 1
        if self.wander_timer <= 0:
            if random.random() < 0.35:
                self.idle_pause_timer = random.randint(60, 120)
                self.current_dir = "center"
                self._update_sprite_image()
                return
            else:
                angle = random.uniform(0, 2 * math.pi)
                spd = self.speed * random.uniform(0.7, 1.2)
                self.vx = math.cos(angle) * spd
                self.vy = math.sin(angle) * spd
                self.wander_timer = random.randint(90, 200)

        self.pos_x += self.vx
        self.pos_y += self.vy

        max_x = self.screen_w - self.win_w - 10
        max_y = self.screen_h - self.win_h - 45

        if self.pos_x <= 15:
            self.pos_x = 15
            self.vx = abs(self.vx)
        elif self.pos_x >= max_x:
            self.pos_x = max_x
            self.vx = -abs(self.vx)

        if self.pos_y <= 20:
            self.pos_y = 20
            self.vy = abs(self.vy)
        elif self.pos_y >= max_y:
            self.pos_y = max_y
            self.vy = -abs(self.vy)

        new_dir = "center"
        if abs(self.vx) > 0.3 or abs(self.vy) > 0.3:
            if abs(self.vx) >= abs(self.vy):
                new_dir = "right" if self.vx > 0 else "left"
            else:
                new_dir = "down" if self.vy > 0 else "up"

        if new_dir != self.current_dir:
            self.current_dir = new_dir
            self._update_sprite_image()

        if self.dialog_window and self.dialog_window.winfo_exists():
            self._reposition_dialog()

    def toggle_dialog(self):
        if self.dialog_window and self.dialog_window.winfo_exists():
            self.dialog_window.destroy()
            self.dialog_window = None
        else:
            self.open_dialog()

    def open_dialog(self, initial_text=None):
        if self.dialog_window and self.dialog_window.winfo_exists():
            self.dialog_window.destroy()

        if self.is_sleeping:
            self.wake_up()

        theme = PALETTE_THEMES[self.current_palette]

        self.dialog_window = tk.Toplevel(self.root)
        self.dialog_window.title("Martes Chat")
        self.dialog_window.attributes("-topmost", True)
        self.dialog_window.overrideredirect(True)
        self.dialog_window.config(bg=theme["border"])

        ico_path = os.path.join(ASSETS_DIR, "martes.ico")
        if os.path.exists(ico_path):
            try:
                self.dialog_window.iconbitmap(ico_path)
            except Exception:
                pass

        inner = tk.Frame(self.dialog_window, bg=theme["bg"], bd=0)
        inner.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        top_bar = tk.Frame(inner, bg=theme["bg"])
        top_bar.pack(fill=tk.X, padx=8, pady=(6, 2))

        title_lbl = tk.Label(
            top_bar,
            text="◈ MARTES 🪐",
            font=("Consolas", 10, "bold"),
            fg=theme["accent"],
            bg=theme["bg"]
        )
        title_lbl.pack(side=tk.LEFT)

        flip_btn = tk.Label(
            top_bar,
            text="[🤸 Flip]",
            font=("Consolas", 8, "bold"),
            fg=theme["accent"],
            bg=theme["bg"],
            cursor="hand2"
        )
        flip_btn.pack(side=tk.LEFT, padx=(10, 0))
        flip_btn.bind("<Button-1>", lambda e: self.start_backflip())

        close_btn = tk.Label(
            top_bar,
            text="✕",
            font=("Consolas", 10, "bold"),
            fg=theme["accent"],
            bg=theme["bg"],
            cursor="hand2"
        )
        close_btn.pack(side=tk.RIGHT)
        close_btn.bind("<Button-1>", lambda e: self.dialog_window.destroy())

        self.response_lbl = tk.Label(
            inner,
            text=initial_text if initial_text else "¿En qué te ayudo?",
            font=("Consolas", 9),
            fg=theme["text"],
            bg=theme["bg"],
            wraplength=260,
            justify=tk.LEFT
        )
        self.response_lbl.pack(fill=tk.BOTH, padx=8, pady=(4, 6))

        input_frame = tk.Frame(inner, bg=theme["input_bg"], bd=1, relief=tk.SOLID)
        input_frame.pack(fill=tk.X, padx=8, pady=(0, 8))

        self.entry = tk.Entry(
            input_frame,
            font=("Consolas", 9),
            fg=theme["text"],
            bg=theme["input_bg"],
            insertbackground=theme["accent"],
            bd=0
        )
        self.entry.pack(fill=tk.X, padx=6, pady=4)
        self.entry.focus_set()
        self.entry.bind("<Return>", self._send_question)
        self.entry.bind("<Escape>", lambda e: self.dialog_window.destroy())

        self._reposition_dialog()
        self.entry.focus_force()

    def _reposition_dialog(self):
        if not self.dialog_window or not self.dialog_window.winfo_exists():
            return
        
        self.dialog_window.update_idletasks()
        dw = self.dialog_window.winfo_width()
        dh = self.dialog_window.winfo_height()
        if dw <= 1:
            dw = 280
            dh = 120

        target_x = int(self.pos_x + (self.win_w / 2) - (dw / 2))
        target_y = int(self.pos_y - dh - 10)

        if target_y < 10:
            target_y = int(self.pos_y + self.win_h + 10)

        target_x = max(10, min(target_x, self.screen_w - dw - 10))
        self.dialog_window.geometry(f"+{target_x}+{target_y}")

    def _send_question(self, event=None):
        if self.is_thinking or self.is_doing_backflip:
            return
        
        question = self.entry.get().strip()
        if not question:
            return

        self.is_thinking = True
        self.thinking_timer = 0
        self.vx = 0
        self.vy = 0
        self.entry.delete(0, tk.END)
        self.response_lbl.config(text="Pensando...")
        self._update_sprite_image()
        self._reposition_dialog()

        threading.Thread(target=self._query_ai, args=(question,), daemon=True).start()

    def _query_ai(self, question):
        q_lower = question.lower()
        is_flip = any(k in q_lower for k in ["backflip", "mortal", "voltereta", "maroma", "acrobacia", "salto mortal", "flip", "gira"])
        is_palette_marte = any(k in q_lower for k in ["paleta marte", "color ambar", "ambar", "terracota", "naranja", "rojo marte"])
        is_palette_verde = any(k in q_lower for k in ["paleta verde", "game boy", "retro", "color verde"])
        is_palette_cyber = any(k in q_lower for k in ["paleta cyber", "cyberpunk", "color oro", "amarillo", "dorado"])
        is_sleep_cmd = any(k in q_lower for k in ["duermete", "duérmete", "a dormir", "siesta", "descansa", "sleep"])
        is_wander_cmd = any(k in q_lower for k in ["pasea", "camina", "camina un rato", "quieto", "detente", "no te muevas"])

        action_callback = None
        reply = None

        if is_flip:
            reply = "¡Afírmate que ahí va! 🤸💨 ¡Mira este mortal hacia atrás!"
            action_callback = self.start_backflip
        elif is_palette_marte:
            reply = "¡Cambiando a paleta Marte Ámbar (Terracota)! 🪐"
            action_callback = lambda: self.set_palette("marte")
        elif is_palette_verde:
            reply = "¡Activando paleta Verde Clásico (Retro Game Boy)! 🟩"
            action_callback = lambda: self.set_palette("verde")
        elif is_palette_cyber:
            reply = "¡Cambiando a paleta Cyberpunk (Oro & Oliva)! ✨"
            action_callback = lambda: self.set_palette("cyber")
        elif is_sleep_cmd:
            reply = "Zzz... me voy a echar una pequeña siesta marciana... (v v)"
            action_callback = self.fall_asleep
        elif is_wander_cmd:
            self.toggle_wander()
            estado = "paseando libremente" if self.is_wandering else "en modo quieto"
            reply = f"¡Entendido! Ahora estoy {estado} en tu escritorio. 🐾"
        else:
            # 1. Intentar conectar a Ollama local
            try:
                prompt = (
                    "Instrucción estricta: Eres mart-es en modo mini compañero de escritorio. "
                    "Responde de forma muy concisa, ingeniosa y directa (máximo 2 a 3 frases cortas). "
                    f"Pregunta del usuario: {question}"
                )
                payload = {
                    "model": MODEL_NAME,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False
                }
                req = urllib.request.Request(
                    OLLAMA_API_URL,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=12) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    reply = data.get("message", {}).get("content", "").strip()
            except Exception:
                # 2. Motor autónomo offline si no hay Ollama instalado
                if any(k in q_lower for k in ["quien eres", "quién eres", "como te llamas", "cómo te llamas", "hola"]):
                    reply = "¡Hola! Soy Martes 🪐, tu compañero de escritorio en pixel art 100% local. ¡Puedo vigilar tu cursor, hacer acrobacias y acompañarte mientras trabajas!"
                elif any(k in q_lower for k in ["que sabes hacer", "qué sabes hacer", "habilidades", "ayuda", "comandos"]):
                    reply = "¡Puedo pasear, hacer backflips (mortal 360°), dormir siestas con Zzz, cambiar paletas de color y reaccionar a tu ratón! Si inicias Ollama en este PC con el modelo 'mart-es', podré responderte cualquier duda compleja con IA generativa."
                elif any(k in q_lower for k in ["chiste", "cuentame un chiste", "cuéntame un chiste", "gracioso"]):
                    chistes = [
                        "¿Por qué los marcianos nunca juegan al escondite? Porque en Marte no hay con qué taparse... ¡solo polvo rojo! 🪐",
                        "¿Qué le dice un astronauta a un satélite descompuesto? 'No te pongas en órbita dramática'. 🚀",
                        "¿Sabes por qué me llamo Martes? ¡Porque los Lunes dan flojera y el Miércoles ya está muy lejos! 😄"
                    ]
                    reply = random.choice(chistes)
                elif any(k in q_lower for k in ["gracias", "te quiero", "buen chico", "lindo"]):
                    reply = "¡Gracias a ti por adoptarme en tu escritorio! ✨ Me caes genial humano."
                else:
                    reply = "¡Estoy activo y cuidando tu escritorio! 🪐 (Modo autónomo offline. Si deseas respuestas profundas con IA generativa, puedes iniciar Ollama con mart-es)."

        def update_ui():
            self.is_thinking = False
            self.current_dir = "center"
            self.do_hop(height=-12.0)
            self._update_sprite_image()
            if self.dialog_window and self.dialog_window.winfo_exists():
                self.response_lbl.config(text=reply if reply else "¿En qué te ayudo?")
                self._reposition_dialog()
            if action_callback:
                self.root.after(350, action_callback)

        self.root.after(0, update_ui)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MiniMartesPet()
    app.run()
