# very cool roblox loading thing because sober doesn't have that

import json
import math
import shutil
import struct
import subprocess
import threading
import time
import zlib
from pathlib import Path

import envvars
import log
import sober
import themes

SOBER_APP_ID = "org.vinegarhq.Sober"

CONFIG_DIR = Path.home() / ".local/Lution"
CONFIG_FILE = CONFIG_DIR / "launcher_config.json"
STABLE_BIN = CONFIG_DIR / "Lution-bootstrap"
DESKTOP_FILE = Path.home() / ".local/share/applications/sober-with-lution.desktop"
DEFAULT_LOGO = CONFIG_DIR / "launcher_logo_default.png"
LAUNCH_LOG = CONFIG_DIR / "sober_launch.log"

WIN_W = 600
WIN_H = 350

DARK = {
    "theme": "dark",
    "bg_type": "color", "bg_color": "#232527", "bg_image": "",
    "menu_logo_size": 300,
    "logo_size": 130, "logo_align": "center", "logo_pos_y": "middle",
    "text_color": "#ffffff", "text_size": 11, "text_align": "center",
    "bar_color": "#ffffff", "bar_track_color": "#3c3f41",
    "bar_width": 280, "bar_height": 7, "bar_rounded": True,
    "bar_align": "center", "progress_mode": "auto",
    "check_updates": True,
}
LIGHT = {
    "theme": "light",
    "bg_type": "color", "bg_color": "#f2f4f5", "bg_image": "",
    "menu_logo_size": 300,
    "logo_size": 130, "logo_align": "center", "logo_pos_y": "middle",
    "text_color": "#393b3d", "text_size": 11, "text_align": "center",
    "bar_color": "#393b3d", "bar_track_color": "#d3d6d9",
    "bar_width": 280, "bar_height": 7, "bar_rounded": True,
    "bar_align": "center", "progress_mode": "auto",
    "check_updates": True,
}

MILESTONES = [
    ("app_start", 0.05), ("runtime_handler", 0.12),
    ("fs_init", 0.22), ("check_security", 0.32), ("app_core", 0.42),
    ("devices_init", 0.52), ("global_window_init", 0.58),
    ("gamemode_init", 0.64), ("interface_init", 0.70),
    ("Loaded Vulkan libs", 0.76), ("pre_main_loop", 0.84),
    ("enter_main_loop", 0.88), ("did_handle_app_startup", 1.0),
]

READY_MARKERS = (
    "did_handle_app_startup",
    '"type":"game_loaded"',
    "setStage: (stage:LuaApp)",
)

UPDATE_SCALE = 0.35

def _shade(hex_color, amt):
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    f = 1 + amt
    clamp = lambda v: max(0, min(255, int(v * f)))
    return f"#{clamp(r):02x}{clamp(g):02x}{clamp(b):02x}"

def _shade_safe(hex_color):
    try:
        return _shade(hex_color, 0)
    except Exception:
        return "#7aa2f7"

LUTION_LOGO_PNG = CONFIG_DIR / "lution_logo.png"

def _resolve_lution_logo():
    import sys
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    png = base / "lution.png"
    if png.exists():
        return png
    return None

def get_config():
    cfg = dict(DARK)
    try:
        data = json.loads(CONFIG_FILE.read_text())
        if isinstance(data, dict):
            cfg.update({k: v for k, v in data.items() if k in DARK})
    except Exception:
        pass
    return cfg

def save_config(cfg):
    clean = {k: cfg.get(k, DARK[k]) for k in DARK}
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(clean, indent=2) + "\n")
    _ensure_default_logo(clean)
    _install_shortcut(clean)
    return clean

def apply_theme_defaults(theme):
    return dict(DARK if theme == "dark" else LIGHT)

def _ensure_default_logo(cfg):
    import sys

    src = Path(getattr(sys, "_MEIPASS", Path(__file__).parent)) / "sober.svg"
    if src.exists():
        up_to_date = False
        if DEFAULT_LOGO.exists():
            try:
                up_to_date = DEFAULT_LOGO.stat().st_mtime \
                             >= src.stat().st_mtime
            except OSError:
                up_to_date = False
        if not up_to_date:
            try:
                subprocess.run(
                    ["rsvg-convert", "-w", "256", "-h", "256",
                     str(src), "-o", str(DEFAULT_LOGO)],
                    check=True, capture_output=True, timeout=10)
                return
            except Exception:
                pass
        elif up_to_date:
            return

    if DEFAULT_LOGO.exists():
        return
    size = 256
    cx = cy = size / 2
    half = size * 0.33
    hole = half * 0.44
    angle = math.radians(-14)
    cos_a, sin_a = math.cos(angle), math.sin(angle)

    def px(x, y):
        dx, dy = x - cx, y - cy
        rx = dx * cos_a + dy * sin_a
        ry = -dx * sin_a + dy * cos_a
        if abs(rx) <= half and abs(ry) <= half \
                and not (abs(rx) <= hole and abs(ry) <= hole):
            return (255, 255, 255, 255)
        return (0, 0, 0, 0)

    _png_from_fn(DEFAULT_LOGO, size, size, px)

def _png_from_fn(path, w, h, fn):
    raw = b"".join(
        b"\x00" + b"".join(bytes(fn(x, y)) for x in range(w))
        for y in range(h))
    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff))
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b""))

def _short_status(line):
    line = line.strip()
    if "Mimalloc" in line or "Hello world" in line or "Hello World" in line:
        return None
    for prefix in ("info: ", "debug: ", "WARN: ", "warning: ", "error: "):
        if line.startswith(prefix):
            line = line[len(prefix):]
    if line.startswith("Roblox:"):
        line = "Roblox: " + line[len("Roblox:"):].strip()
    if len(line) > 64:
        line = line[:61] + "..."
    return line

def _milestone_progress(line):
    for needle, frac in MILESTONES:
        if needle in line:
            return frac
    return None

class BootstrapperWindow:

    def __init__(self, root, parent, cfg, menu=False):
        import tkinter as tk

        self.root = root
        self.cfg = cfg
        self.menu = menu
        self.on_play = None
        self.on_configure = None
        self.closed = False
        self.mode = cfg.get("progress_mode", "auto")
        self.frac = None
        self._anim_id = None
        self._menu_items = []
        self._accent = _shade_safe(themes.load_theme().get("accent", "#7aa2f7"))
        self.win_holder = {"closed": False}
        self.detach = False

        self.frame = tk.Frame(parent, width=WIN_W, height=WIN_H,
                              highlightthickness=1,
                              highlightbackground="#000000")
        self.frame.pack_propagate(False)

        self.canvas = tk.Canvas(self.frame, width=WIN_W, height=WIN_H,
                                 highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)

        def _on_win_destroy(e):
            if e.widget is parent:
                self.win_holder["closed"] = True
                try:
                    r = self.root
                    if getattr(r, "_lution_standalone", False) \
                            and r.winfo_exists():
                        r.destroy()
                except Exception:
                    pass
        parent.bind("<Destroy>", _on_win_destroy)

        self._images = []
        self.bar_w = int(cfg.get("bar_width", 280))
        self.bar_h = int(cfg.get("bar_height", 7))
        self.bar_r = min(self.bar_h // 2, 8) if cfg.get("bar_rounded") else 0
        self.inner_r = min(self.bar_h // 2, 8)
        self.bar_x0 = self._align_x(self.bar_w)
        self.bar_y0 = WIN_H - 84
        self._disp_frac = None
        self._draw_background()

        if menu:
            self._draw_menu()
            return

        self._build_progress_ui()
        self._start_bounce()

    def start_progress(self):
        if not self.menu:
            return
        for item in self._menu_items:
            try:
                self.canvas.delete(item)
            except Exception:
                pass
        self._menu_items.clear()
        self.menu = False
        self._build_progress_ui()
        self._start_bounce()

    def _draw_menu(self):
        import tkinter as tk

        logo_path = _resolve_lution_logo()
        if logo_path:
            try:
                img = tk.PhotoImage(file=str(logo_path))
                target = max(24, int(self.cfg.get("menu_logo_size", 300)))
                w0 = img.width()
                best_z, best_s, best_err = 1, 1, float("inf")
                for z in range(1, 9):
                    for s in range(1, 9):
                        err = abs(w0 * z / s - target)
                        if err < best_err:
                            best_err, best_z, best_s = err, z, s
                if (best_z, best_s) != (1, 1):
                    if best_z > 1:
                        img = img.zoom(best_z, best_z)
                    if best_s > 1:
                        img = img.subsample(best_s, best_s)
                self._images.append(img)
                self._menu_items.append(
                    self.canvas.create_image(WIN_W // 2, 84, image=img))
            except Exception:
                pass

        pressed_bg = _shade(self._accent, -0.18)

        def make_btn(text, handler):
            f = tk.Frame(self.canvas, bg=self._accent,
                         highlightthickness=0)
            lbl = tk.Label(f, text=text, bg=self._accent, fg="#0a0a0a",
                           font=("TkDefaultFont", 12, "bold"),
                           padx=16, pady=6, cursor="hand2")
            lbl.pack(fill="both", expand=True)

            def on_press(_e):
                lbl.configure(bg=pressed_bg)

            def on_release(_e):
                lbl.configure(bg=self._accent)
                handler()

            lbl.bind("<ButtonPress-1>", on_press)
            lbl.bind("<ButtonRelease-1>", on_release)
            return f

        play_f = make_btn("Play Roblox", self._do_play)
        cfg_f = make_btn("Configure Roblox", self._do_configure)

        y_btn = WIN_H - 64
        w_play, w_cfg, gap = 138, 200, 24
        left_edge = WIN_W // 2 - (w_play + gap + w_cfg) // 2
        i1 = self.canvas.create_window(left_edge + w_play // 2, y_btn,
                                        window=play_f,
                                        width=w_play, height=40)
        i2 = self.canvas.create_window(left_edge + w_play + gap
                                        + w_cfg // 2, y_btn,
                                        window=cfg_f,
                                        width=w_cfg, height=40)
        self._menu_items.extend([i1, i2])

    def _do_play(self):
        if self.on_play:
            self.on_play()

    def _do_configure(self):
        if self.on_configure:
            self.on_configure()

    def _build_progress_ui(self):
        self._draw_logo()

        self._draw_round_rect(
            self.bar_x0, self.bar_y0, self.bar_x0 + self.bar_w,
            self.bar_y0 + self.bar_h,
            radius=self.bar_r,
            fill=self.cfg.get("bar_track_color", "#3c3f41"), outline="")

        self.inner_w = max(18, int(self.bar_w * 0.32))
        self.inner = self.canvas.create_rectangle(
            self.bar_x0, self.bar_y0, self.bar_x0 + self.inner_w,
            self.bar_y0 + self.bar_h,
            fill=self.cfg.get("bar_color", "#ffffff"), outline="")
        if self.cfg.get("bar_rounded"):
            try:
                self.canvas.itemconfigure(self.inner, state="hidden")
                self.inner = self._draw_round_rect(
                    self.bar_x0, self.bar_y0, self.bar_x0 + self.inner_w,
                    self.bar_y0 + self.bar_h,
                    radius=self.inner_r,
                    fill=self.cfg.get("bar_color", "#ffffff"), outline="")
            except Exception:
                pass

        tx = self._align_x(0)
        anchor_map = {"left": "w", "center": "center", "right": "e"}
        self.text_item = self.canvas.create_text(
            tx, self.bar_y0 + self.bar_h + 18,
            text="Starting...",
            fill=self.cfg.get("text_color", "#ffffff"),
            font=("TkDefaultFont", int(self.cfg.get("text_size", 11))),
            anchor=anchor_map.get(self.cfg.get("text_align", "center"),
                                   "center"),
            width=WIN_W - 80)

        self._start_bounce()

    def _place_inner(self, x_left, width):
        c = self.canvas
        y0, y1 = self.bar_y0, self.bar_y0 + self.bar_h
        if isinstance(self.inner, list):
            r = self.inner_r
            p = self.inner
            c.coords(p[0], x_left + r, y0, x_left + width - r, y1)
            c.coords(p[1], x_left, y0 + r, x_left + width, y1 - r)
            c.coords(p[2], x_left, y0, x_left + 2 * r, y0 + 2 * r)
            c.coords(p[3], x_left + width - 2 * r, y0,
                     x_left + width, y0 + 2 * r)
            c.coords(p[4], x_left, y1 - 2 * r, x_left + 2 * r, y1)
            c.coords(p[5], x_left + width - 2 * r, y1 - 2 * r,
                     x_left + width, y1)
        else:
            c.coords(self.inner, x_left, y0, x_left + width, y1)

    def _align_x(self, item_w):
        align = self.cfg.get("bar_align", "center")
        if align == "left":
            return 30
        if align == "right":
            return WIN_W - 30 - item_w
        return (WIN_W - item_w) // 2

    def _draw_background(self):
        cfg = self.cfg
        if cfg.get("bg_type") == "image" and cfg.get("bg_image"):
            try:
                import tkinter as tk
                img = tk.PhotoImage(file=cfg["bg_image"])
                wf = max(1, img.width() // WIN_W + 1)
                hf = max(1, img.height() // WIN_H + 1)
                f = max(wf, hf)
                if f > 1:
                    img = img.subsample(f, f)
                self._images.append(img)
                self.canvas.create_image(WIN_W // 2, WIN_H // 2,
                                          image=img)
                return
            except Exception:
                pass
        self.canvas.configure(bg=cfg.get("bg_color", "#232527"))

    def _draw_logo(self):
        import tkinter as tk
        cfg = self.cfg
        path = cfg.get("logo_path") or str(DEFAULT_LOGO)
        try:
            img = tk.PhotoImage(file=path)
        except Exception:
            img = tk.PhotoImage(file=str(DEFAULT_LOGO))

        target = max(24, int(cfg.get("logo_size", 130)))
        w0, h0 = img.width(), img.height()
        best_z, best_s, best_err = 1, 1, float("inf")
        for z in range(1, 9):
            for s in range(1, 9):
                err = abs(w0 * z / s - target)
                if err < best_err:
                    best_err = err
                    best_z, best_s = z, s
        if (best_z, best_s) != (1, 1):
            if best_z > 1:
                img = img.zoom(best_z, best_z)
            if best_s > 1:
                img = img.subsample(best_s, best_s)
        self._images.append(img)

        align = cfg.get("logo_align", "center")
        if align == "left":
            x = 30 + img.width() // 2
        elif align == "right":
            x = WIN_W - 30 - img.width() // 2
        else:
            x = WIN_W // 2

        pos_y = cfg.get("logo_pos_y", "middle")
        if pos_y == "top":
            y = 46 + img.height() // 2
        elif pos_y == "bottom":
            y = self.bar_y0 - 60
        else:
            y = int(WIN_H * 0.42)

        self.canvas.create_image(x, y, image=img)

    def _draw_round_rect(self, x1, y1, x2, y2, radius=0, **kw):
        c = self.canvas
        if radius <= 0:
            return c.create_rectangle(x1, y1, x2, y2, **kw)
        parts = [
            c.create_rectangle(x1 + radius, y1, x2 - radius, y2, **kw),
            c.create_rectangle(x1, y1 + radius, x2, y2 - radius, **kw),
            c.create_oval(x1, y1, x1 + 2 * radius, y1 + 2 * radius, **kw),
            c.create_oval(x2 - 2 * radius, y1, x2, y1 + 2 * radius, **kw),
            c.create_oval(x1, y2 - 2 * radius, x1 + 2 * radius, y2, **kw),
            c.create_oval(x2 - 2 * radius, y2 - 2 * radius, x2, y2, **kw),
        ]
        return parts

    def _start_bounce(self):
        total = self.bar_w + self.inner_w
        duration_ms = 1800
        pause_ms = 2000
        cycle_ms = duration_ms + pause_ms
        state = {"ms": 0.0}

        def step():
            if self.closed:
                return
            if self.frac is None or self.mode == "bounce":
                state["ms"] = (state["ms"] + 33) % cycle_ms
                if state["ms"] < duration_ms:
                    d = (state["ms"] / duration_ms) * total
                    xl = d - self.inner_w
                    xr = d
                    vis_l = max(xl, 0.0)
                    vis_r = min(float(self.bar_w), xr)
                    if vis_r <= vis_l:
                        self._place_inner(self.bar_x0, 0)
                    else:
                        self._place_inner(self.bar_x0 + int(vis_l),
                                          int(vis_r - vis_l))
                else:
                    self._place_inner(self.bar_x0, 0)
            else:
                target = min(1.0, max(0.0, self.frac))
                cur = self._disp_frac
                if cur is None:
                    cur = 0.0
                    self._place_inner(self.bar_x0, 1)
                cur += (target - cur) * 0.18
                if abs(target - cur) < 0.002:
                    cur = target
                self._disp_frac = cur
                min_w = 2 * self.inner_r if isinstance(self.inner, list) else 2
                width = max(int(cur * self.bar_w), min_w)
                self._place_inner(self.bar_x0, width)
            self._anim_id = self.root.after(33, step)

        self._anim_id = self.root.after(33, step)

    def _schedule(self, fn):
        def run():
            try:
                if not self.closed and self.canvas.winfo_exists():
                    fn()
            except Exception:
                pass
        self.root.after(0, run)

    def status(self, text):
        def do():
            self.canvas.itemconfigure(self.text_item, text=text)
        self._schedule(do)

    def progress(self, frac):
        def do():
            self.frac = max(self.frac or 0.0, frac)
            if self.mode == "bounce":
                self.mode = "auto"
        self._schedule(do)

    def done(self):
        def do():
            self.frac = 1.0
        self._schedule(do)

    def fail(self, msg):
        def do():
            self.canvas.itemconfigure(self.text_item, text=msg)
            for w in (self.canvas, self.frame):
                w.bind("<Button-1>", lambda e: self.close())
        self._schedule(do)

    def close(self):
        if self.closed:
            return
        self.closed = True
        try:
            if self._anim_id:
                self.root.after_cancel(self._anim_id)
        except Exception:
            pass
        try:
            if self.frame.winfo_exists():
                self.frame.master.destroy()
        except Exception:
            pass
        try:
            if getattr(self.root, "_lution_standalone", False) \
                    and self.root.winfo_exists():
                self.root.destroy()
        except Exception:
            pass

    def pack(self, **kw):
        self.frame.pack(**kw)

def run_launch(cfg, ui, root, url=None):
    def T(fn):
        root.after(0, fn)
    try:
        if cfg.get("check_updates", True):
            ui.status("Checking for updates...")
            log.info("Bootstrapper: checking for Sober updates")

            def on_line(line):
                import re
                m = re.search(r"(\d{1,3})\s*%", line)
                if m:
                    pct = int(m.group(1))
                    ui.progress(UPDATE_SCALE * pct / 100.0)
                    ui.status(f"Updating Sober... {pct}%")
                else:
                    s = _short_status(line)
                    if s:
                        ui.status(s)

            ok, msg = sober.ensure_sober(on_line)
            if not ok:
                log.error("Bootstrapper: Sober update failed")
                ui.fail("Update failed")
                return

        ui.status("Launching Roblox...")
        ui.progress(UPDATE_SCALE if cfg.get("check_updates", True) else 0.02)
        log.info("Bootstrapper: launching Sober")

        args = ["flatpak", "run"] + envvars.env_flatpak_args() \
               + [SOBER_APP_ID]
        if url:
            args.append(url)
        LAUNCH_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(LAUNCH_LOG, "w") as logfile:
            proc = subprocess.Popen(args, stdout=logfile,
                                    stderr=subprocess.STDOUT)

        base = UPDATE_SCALE if cfg.get("check_updates", True) else 0.02
        span = 1.0 - base
        offset = 0
        pending = ""
        reached = {}
        ready = False
        while True:
            try:
                with open(LAUNCH_LOG) as f:
                    f.seek(offset)
                    chunk = f.read()
                    offset += len(chunk)
            except OSError:
                chunk = ""
            if chunk:
                parts = (pending + chunk).replace("\r", "\n").split("\n")
                pending = parts.pop()
                for line in parts:
                    line = line.strip()
                    if not line:
                        continue
                    frac = _milestone_progress(line)
                    if frac is not None and frac > reached.get("max", 0):
                        reached["max"] = frac
                        ui.progress(base + span * frac)
                    s = _short_status(line)
                    if s and "json" not in s:
                        ui.status(s)
                    if not ready and any(
                            m in line for m in READY_MARKERS):
                        ready = True
                        log.info("Bootstrapper: Sober is running")
                        ui.detach = True
                        T(ui.done)
                        T(lambda: ui.status("Sober is running"))
                        root.after(1500, ui.close)

            rc = proc.poll()

            if ui.win_holder.get("closed"):
                if rc is None and not getattr(ui, "detach", False):
                    proc.terminate()
                    try:
                        proc.wait(timeout=5)
                    except Exception:
                        proc.kill()
                    log.info("Launcher closed, Sober stopped")
                elif rc is None:
                    log.info("Launcher closed, Sober keeps running")
                return

            if rc is not None:
                if ready:
                    log.info("Sober closed")
                    T(ui.close)
                    return
                log.error(f"Bootstrapper: Sober exited early (code {rc})")
                ui.fail(f"Sober exited early (code {rc})")
                return
            time.sleep(0.15)
    except Exception as e:
        log.error(f"Bootstrapper error: {e}")
        T(lambda: ui.fail(f"Error: {e}"))

def open_in(app, url=None):
    import tkinter as tk

    cfg = get_config()
    _ensure_default_logo(cfg)
    win = tk.Toplevel(app, bg=cfg.get("bg_color", "#232527"))
    win.title("Lution")
    win.resizable(False, False)
    try:
        win.attributes("-type", "splash")
    except tk.TclError:
        pass
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    win.geometry(f"{WIN_W}x{WIN_H}+{(sw - WIN_W) // 2}+{(sh - WIN_H) // 2}")

    ui = BootstrapperWindow(win, win, cfg)
    ui.pack(fill="both", expand=True)

    threading.Thread(target=run_launch, args=(cfg, ui, win, url),
                     daemon=True).start()
    return win

def refresh_shortcut():
    if not DESKTOP_FILE.exists():
        return
    _install_shortcut(get_config())

def _clean_child_env():
    import os
    return {k: v for k, v in os.environ.items()
            if not k.startswith("_MEI") and not k.startswith("_PYI")}

def _launch_full_lution(root):
    import sys
    log.info("Bootstrapper: opening Lution")
    if getattr(sys, "frozen", False):
        cmd = [sys.executable]
        cwd = None
    else:
        cmd = [sys.executable, str(Path(__file__).parent / "main.py")]
        cwd = str(Path(__file__).parent)
    try:
        subprocess.Popen(cmd, cwd=cwd, env=_clean_child_env())
    except Exception as e:
        log.error(f"Could not open Lution: {e}")
        return
    root.after(300, root.destroy)

def run_standalone():
    root = _make_root()
    cfg = get_config()
    _ensure_default_logo(cfg)
    win = _standalone_window(root, cfg)
    ui = BootstrapperWindow(win, win, cfg, menu=True)
    ui.pack(fill="both", expand=True)

    def play():
        ui.start_progress()
        threading.Thread(target=run_launch, args=(cfg, ui, win),
                         daemon=True).start()

    ui.on_play = play
    ui.on_configure = lambda: _launch_full_lution(root)
    root.mainloop()

def _make_root():
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    root._lution_standalone = True
    return root

def _standalone_window(root, cfg):
    import tkinter as tk
    win = tk.Toplevel(root, bg=cfg.get("bg_color", "#232527"))
    win.title("Lution")
    win.resizable(False, False)
    try:
        win.attributes("-type", "splash")
    except tk.TclError:
        pass
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    win.geometry(f"{WIN_W}x{WIN_H}+{(sw - WIN_W) // 2}+{(sh - WIN_H) // 2}")
    return win

def _is_frozen():
    import sys
    return getattr(sys, "frozen", False)

def _sync_stable_binary():
    import sys

    if not _is_frozen():
        return

    exe = Path(sys.executable)
    try:
        stale = (not STABLE_BIN.exists()
                 or exe.stat().st_size != STABLE_BIN.stat().st_size
                 or exe.stat().st_mtime > STABLE_BIN.stat().st_mtime)
        if stale:
            shutil.copy2(exe, STABLE_BIN)
            log.debug("Refreshed stable launcher binary copy")
    except Exception as e:
        log.warning(f"Could not refresh stable launcher copy: {e}")

def _exec_command():
    main_py = Path(__file__).parent / "main.py"
    if _is_frozen():
        return f'"{STABLE_BIN}" --launcher'
    return f'python3 "{main_py}" --launcher'

def _install_shortcut(cfg):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    _sync_stable_binary()

    import sys
    icon_src = Path(getattr(sys, "_MEIPASS", Path(__file__).parent)) \
               / "sober.svg"
    icon = CONFIG_DIR / "sober.svg"
    try:
        if icon_src.exists():
            shutil.copyfile(icon_src, icon)
    except Exception:
        pass

    desktop = "\n".join([
        "[Desktop Entry]",
        "Name=Sober with Lution",
        "Comment=Launch Sober through the Lution bootstrapper",
        f"Exec={_exec_command()}",
        f"Icon={icon if icon.exists() else 'applications-games'}",
        "Terminal=false",
        "Type=Application",
        "Categories=Game;",
        "StartupWMClass=Lution",
    ]) + "\n"
    DESKTOP_FILE.parent.mkdir(parents=True, exist_ok=True)
    DESKTOP_FILE.write_text(desktop)

    for legacy in (CONFIG_DIR / "sober_with_lution.sh",
                   CONFIG_DIR / "sober_with_lution.py",
                   CONFIG_DIR / "lution_bootstrapper_lib.py",
                   CONFIG_DIR / "Lution"):
        try:
            if legacy.exists():
                legacy.unlink()
        except Exception:
            pass
    legacy_pycache = CONFIG_DIR / "__pycache__"
    if legacy_pycache.is_dir():
        shutil.rmtree(legacy_pycache, ignore_errors=True)
    log.info("Bootstrapper shortcut installed")
