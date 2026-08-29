# lution developed by wookhq uhh hello
# i shortened this because triplean said half of lution is in main.py so like why not split it more
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import subprocess
import json
import sys
import threading

import themes

BASE = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
CONFIG_FILE = BASE / "ui.md"

_theme = themes.load_theme()
BG = _theme["bg"]
BG_SIDEBAR = _theme["bg_sidebar"]
BG_ACTIVE = "#2a2a2a"
FG = _theme["fg"]
FG_DIM = "#888888"
ACCENT = _theme["accent"]
ERROR = "#e06c75"
BODY_FONT = ("TkDefaultFont", 13)

import fonts
import emoji
import cursors
import mods
import sound_mods
import log

APK_CHECKSUM_FILE = Path.home() / ".local" / "Lution" / "apk_checksum.txt"
LEGACY_CHECKSUM_FILES = [
    Path.home() / ".local/Lution/emoji_checksum.txt",
    Path.home() / ".local/Lution/cursor_checksum.txt",
    Path.home() / ".local/Lution/mods_checksum.txt",
    Path.home() / ".local/Lution/sounds_checksum.txt",
]

def _find_apk():
    apk_dir = fonts.APK_DIR
    if not apk_dir.exists():
        return None
    candidates = sorted(apk_dir.glob("*.apk"),
                         key=lambda p: p.stat().st_size, reverse=True)
    return candidates[0] if candidates else None

def _calculate_sha256_checksum(apk_path):
    import hashlib
    with open(apk_path, "rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()

def reapply_customizations():
    for legacy in LEGACY_CHECKSUM_FILES:
        try:
            if legacy.exists():
                legacy.unlink()
                log.debug(f"Removed old checksum file {legacy.name}")
        except OSError:
            pass

    apk_path = _find_apk()
    if apk_path is None:
        log.debug("Sober APK not found, skipping reapply check")
        return

    current = _calculate_sha256_checksum(apk_path)
    last = ""
    if APK_CHECKSUM_FILE.exists():
        last = APK_CHECKSUM_FILE.read_text().strip()

    if current == last:
        log.debug("Sober APK unchanged, customizations intact")
        return

    log.info("Sober APK changed, reapplying all customizations")
    for name, fn in (("fonts", fonts.reapply_fonts),
                     ("emoji", emoji.reapply_emoji),
                     ("cursors", cursors.reapply_cursors),
                     ("mods", mods.reapply_mods),
                     ("sounds", sound_mods.reapply_sounds)):
        try:
            fn()
        except Exception as e:
            log.error(f"Failed to reapply {name}: {e}")

    try:
        APK_CHECKSUM_FILE.parent.mkdir(parents=True, exist_ok=True)
        APK_CHECKSUM_FILE.write_text(current)
    except OSError as e:
        log.error(f"Could not save APK checksum: {e}")

import widgets
widgets.BG = BG
widgets.BG_SIDEBAR = BG_SIDEBAR
widgets.BG_ACTIVE = BG_ACTIVE
widgets.FG = FG
widgets.FG_DIM = FG_DIM
widgets.ACCENT = ACCENT
widgets.ERROR = ERROR
widgets.BODY_FONT = BODY_FONT

WIDGET_BUILDERS = {
    "flaglist": widgets.build_flaglist,
    "fpsinput": widgets.build_fpsinput,
    "envvars": widgets.build_envvars,
    "bootstrapper": widgets.build_bootstrapper,
    "fontpicker": widgets.build_fontpicker,
    "cursorpicker": widgets.build_cursorpicker,
    "themepicker": widgets.build_themepicker,
    "emojipicker": widgets.build_emojipicker,
    "versionlabel": widgets.build_versionlabel,
    "soberversion": widgets.build_soberversion,
    "sobermanager": widgets.build_sobermanager,
    "soberuninstall": widgets.build_soberuninstall,
    "soberlauncher": widgets.build_soberlauncher,
    "sobersettings": widgets.build_sobersettings,
    "playhistory": widgets.build_playhistory,
    "marketplace": widgets.build_marketplace,
    "resetall": widgets.build_resetall,
    "backupmanager": widgets.build_backupmanager,
    "modconflicts": widgets.build_modconflicts,
    "modmanager": widgets.build_modmanager,
    "soundmods": widgets.build_soundmods,
}

def darken(hex_color, amount=0.18):
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    r = max(0, int(r * (1 - amount)))
    g = max(0, int(g * (1 - amount)))
    b = max(0, int(b * (1 - amount)))
    return f"#{r:02x}{g:02x}{b:02x}"

def parse_config(path):
    pages = {}
    current = None
    pending_label = None

    if not Path(path).exists():
        return pages

    for raw_line in Path(path).read_text().splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith("# "):
            current = line[2:].strip()
            pages[current] = []

        elif line.startswith("Subtitle = "):
            text = line[len("Subtitle = "):].strip()
            if current is not None:
                pages[current].append(("subtitle", text))

        elif line.startswith("CreateButton = "):
            pending_label = line[len("CreateButton = "):].strip()

        elif line.startswith("CreateButton > "):
            rest = line[len("CreateButton > "):].strip().split()
            script, static_args = rest[0], rest[1:]
            if current is not None and pending_label is not None:
                pages[current].append(("button", pending_label, script, static_args))
            pending_label = None

        elif line.startswith("TextBox = "):
            rest = line[len("TextBox = "):].strip()
            if "|" in rest:
                label, placeholder = rest.split("|", 1)
            else:
                label, placeholder = rest, ""
            if current is not None:
                pages[current].append(("textbox", label.strip(), placeholder.strip()))

        elif line.startswith("Selection = "):
            rest = line[len("Selection = "):].strip()
            if "|" in rest:
                label, opts = rest.split("|", 1)
                options = [o.strip() for o in opts.split(",") if o.strip()]
            else:
                label, options = rest, []
            if current is not None:
                pages[current].append(("selection", label.strip(), options))

        elif line == "FlagList":
            if current is not None:
                pages[current].append(("flaglist",))

        elif line == "FPSInput":
            if current is not None:
                pages[current].append(("fpsinput",))

        elif line == "EnvVars":
            if current is not None:
                pages[current].append(("envvars",))

        elif line == "Bootstrapper":
            if current is not None:
                pages[current].append(("bootstrapper",))

        elif line == "FontPicker":
            if current is not None:
                pages[current].append(("fontpicker",))

        elif line == "CursorPicker":
            if current is not None:
                pages[current].append(("cursorpicker",))

        elif line == "ThemePicker":
            if current is not None:
                pages[current].append(("themepicker",))

        elif line == "EmojiPicker":
            if current is not None:
                pages[current].append(("emojipicker",))

        elif line == "VersionLabel":
            if current is not None:
                pages[current].append(("versionlabel",))

        elif line == "SoberVersion":
            if current is not None:
                pages[current].append(("soberversion",))

        elif line == "SoberManager":
            if current is not None:
                pages[current].append(("sobermanager",))

        elif line == "SoberUninstall":
            if current is not None:
                pages[current].append(("soberuninstall",))

        elif line == "SoberLauncher":
            if current is not None:
                pages[current].append(("soberlauncher",))

        elif line == "SoberSettings":
            if current is not None:
                pages[current].append(("sobersettings",))

        elif line == "PlayHistory":
            if current is not None:
                pages[current].append(("playhistory",))

        elif line == "Marketplace":
            if current is not None:
                pages[current].append(("marketplace",))

        elif line == "ResetAll":
            if current is not None:
                pages[current].append(("resetall",))

        elif line == "BackupManager":
            if current is not None:
                pages[current].append(("backupmanager",))

        elif line == "ModConflictDetector":
            if current is not None:
                pages[current].append(("modconflicts",))

        elif line == "ModManager":
            if current is not None:
                pages[current].append(("modmanager",))

        elif line == "SoundMods":
            if current is not None:
                pages[current].append(("soundmods",))

        elif line.startswith("Image = "):
            rest = line[len("Image = "):].strip()
            if "|" in rest:
                filename, caption = rest.split("|", 1)
            else:
                filename, caption = rest, ""
            if current is not None:
                pages[current].append(("image", filename.strip(), caption.strip()))

    return pages

def run_script(script, args=None):
    args = args or []
    path = BASE / script

    if path.suffix == ".py":
        subprocess.Popen(["python3", str(path), *args])
    else:
        subprocess.Popen([str(path), *args])

# the gui yay
class Lution(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Lution")
        self.configure(bg=BG)
        self.minsize(1280, 720)

        self.mainloop_started = threading.Event()

        self.setup_style()

        self.bind_all("<MouseWheel>", self._global_scroll)
        self.bind_all("<Button-4>", self._global_scroll)
        self.bind_all("<Button-5>", self._global_scroll)

        log.info("Starting Lution")
        reapply_customizations()

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.pages_config = parse_config(CONFIG_FILE)
        log.debug(f"Loaded {len(self.pages_config)} page(s) from ui.md")
        self.nav_buttons = {}
        self.pages = {}
        self.fflag_rows = []
        self.reload_fflags_ui = lambda: None

        self.page_shown_listeners = []
        self.build_sidebar()
        self.build_content()

    def setup_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TCombobox",
                         fieldbackground=BG_ACTIVE, background=BG_ACTIVE,
                         foreground=FG, arrowcolor=FG, bordercolor=BG_SIDEBAR)
        style.map("TCombobox", fieldbackground=[("readonly", BG_ACTIVE)])

    def make_button(self, parent, text, command=None, bg=ACCENT, fg="#0a0a0a",
                     font=BODY_FONT, padx=20, pady=10):
        pressed_bg = darken(bg)
        btn = tk.Label(parent, text=text, bg=bg, fg=fg, font=font,
                        padx=padx, pady=pady, cursor="hand2")

        def on_press(e):
            btn.configure(bg=pressed_bg)

        def on_release(e):
            log.debug(f"Button clicked: '{text}'")
            btn.configure(bg=bg)
            if command:
                command()

        btn.bind("<ButtonPress-1>", on_press)
        btn.bind("<ButtonRelease-1>", on_release)
        return btn

    def build_sidebar(self):
        sidebar = tk.Frame(self, width=240, bg=BG_SIDEBAR)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        logo_path = BASE / "lution.png"
        if logo_path.exists():
            raw_logo = tk.PhotoImage(file=str(logo_path))
            max_size = 128
            factor = max(1, max(raw_logo.width(), raw_logo.height()) // max_size)
            self.logo_img = raw_logo.subsample(factor, factor)
            tk.Label(sidebar, image=self.logo_img, bg=BG_SIDEBAR
                     ).pack(padx=18, pady=(20, 26))

        for name in self.pages_config:
            btn = tk.Label(
                sidebar, text=name, bg=BG_SIDEBAR, fg=FG_DIM,
                font=("TkDefaultFont", 14), anchor="w",
                padx=18, pady=12, cursor="hand2"
            )
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=BG_ACTIVE))
            btn.bind("<Leave>", lambda e, b=btn: self.refresh_button(b))
            btn.bind("<ButtonPress-1>",
                     lambda e, b=btn: b.configure(bg=darken(BG_ACTIVE)))
            btn.bind("<ButtonRelease-1>", lambda e, n=name: self.show_page(n))
            self.nav_buttons[name] = btn

    def refresh_button(self, btn):
        active = getattr(self, "current_page", None)
        name = [n for n, b in self.nav_buttons.items() if b is btn][0]
        if name == active:
            btn.configure(bg=BG_ACTIVE, fg=FG)
        else:
            btn.configure(bg=BG_SIDEBAR, fg=FG_DIM)

    def _scrollable_canvas(self, widget):
        while widget is not None:
            if isinstance(widget, tk.Canvas) \
                    and getattr(widget, "_lution_scrollable", False):
                return widget
            widget = getattr(widget, "master", None)
        return None

    def _global_scroll(self, event):
        
        try:
            target = self.winfo_containing(event.x_root, event.y_root)
        except (KeyError, tk.TclError):
            return
        canvas = self._scrollable_canvas(target)
        if canvas is None:
            return
        num = getattr(event, "num", None)
        if num == 4:
            canvas.yview_scroll(-1, "units")
        elif num == 5:
            canvas.yview_scroll(1, "units")
        else:
            delta = getattr(event, "delta", 0)
            if delta:
                steps = int(-1 * (delta / 120))
                if steps == 0:
                    steps = -1 if delta > 0 else 1
                canvas.yview_scroll(steps, "units")

    def build_content(self):
        self.container = tk.Frame(self, bg=BG)
        self.container.grid(row=0, column=1, sticky="nsew", padx=24, pady=20)
        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)

        for name, widgets_cfg in self.pages_config.items():
            page = self.build_page(name, widgets_cfg)
            page.grid(row=0, column=0, sticky="nsew")
            self.pages[name] = page

        if self.pages_config:
            self.show_page(next(iter(self.pages_config)))

    def build_page(self, name, widgets_cfg):
        wrapper = tk.Frame(self.container, bg=BG)

        canvas = tk.Canvas(wrapper, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(wrapper, orient="vertical",
                                  command=canvas.yview,
                                  bg=BG_SIDEBAR, troughcolor=BG_SIDEBAR,
                                  activebackground=FG_DIM, width=10)
        page = tk.Frame(canvas, bg=BG)
        page_window = canvas.create_window((0, 0), window=page, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        def on_page_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
        page.bind("<Configure>", on_page_configure)

        def on_canvas_configure(e):
            canvas.itemconfigure(page_window, width=e.width)
        canvas.bind("<Configure>", on_canvas_configure)

        canvas._lution_scrollable = True

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Label(page, text=name, bg=BG, fg=FG,
                 font=("TkDefaultFont", 18, "bold"),
                 anchor="w").pack(anchor="w", pady=(0, 18))

        group = None
        group_inputs = []

        def new_group():
            frame = tk.Frame(page, bg=BG_ACTIVE, highlightthickness=1,
                              highlightbackground=BG_SIDEBAR)
            frame.pack(anchor="w", fill="x", pady=(0, 14))
            return frame

        for widget in widgets_cfg:
            kind = widget[0]

            if kind == "subtitle":
                _, text = widget
                group = new_group()
                group_inputs = []
                tk.Label(group, text=text, bg=BG_ACTIVE, fg=FG,
                         font=("TkDefaultFont", 14, "bold"),
                         anchor="w").pack(anchor="w", fill="x",
                                          padx=14, pady=(12, 8))

            elif kind == "button":
                _, label, script, static_args = widget
                target = group if group is not None else page
                inputs_snapshot = list(group_inputs)
                pad = 14 if group is not None else 0
                btn = self.make_button(
                    target, label,
                    command=lambda s=script, sa=static_args, ins=inputs_snapshot:
                        run_script(s, list(sa) + [get() for get in ins]))
                btn.pack(anchor="w", padx=pad, pady=(4, 14 if group else 4))

            elif kind == "textbox":
                _, label, placeholder = widget
                target = group if group is not None else page
                pad = 14 if group is not None else 0
                tk.Label(target, text=label, bg=BG_ACTIVE if group else BG,
                         fg=FG, font=BODY_FONT).pack(anchor="w", padx=pad,
                                                       pady=(6, 2))
                entry = tk.Entry(target, bg=BG, fg=FG,
                                  insertbackground=FG, font=BODY_FONT,
                                  relief="flat", highlightthickness=1,
                                  highlightbackground=BG_SIDEBAR,
                                  highlightcolor=ACCENT)
                if placeholder:
                    entry.insert(0, placeholder)
                entry.pack(anchor="w", fill="x", padx=pad,
                            pady=(0, 10), ipady=8)
                group_inputs.append(entry.get)

            elif kind == "selection":
                _, label, options = widget
                target = group if group is not None else page
                pad = 14 if group is not None else 0
                tk.Label(target, text=label, bg=BG_ACTIVE if group else BG,
                         fg=FG, font=BODY_FONT).pack(anchor="w", padx=pad,
                                                       pady=(6, 2))
                combo = ttk.Combobox(target, values=options, font=BODY_FONT,
                                      state="readonly")
                if options:
                    combo.set(options[0])
                combo.pack(anchor="w", padx=pad, pady=(0, 10), ipady=4)
                group_inputs.append(combo.get)

            elif kind in WIDGET_BUILDERS:
                target = group if group is not None else page
                pad = 14 if group is not None else 0
                WIDGET_BUILDERS[kind](self, target, pad)

            elif kind == "image":
                _, filename, caption = widget
                target = group if group is not None else page
                pad = 14 if group is not None else 0
                img_path = BASE / filename
                if img_path.exists():
                    raw = tk.PhotoImage(file=str(img_path))
                    max_w = 400
                    factor = max(1, raw.width() // max_w)
                    img = raw.subsample(factor, factor)
                    setattr(self, f"_img_{filename}", img)
                    tk.Label(target, image=img, bg=target["bg"]
                             ).pack(anchor="w", padx=pad, pady=(6, 4))
                if caption:
                    tk.Label(target, text=caption, bg=target["bg"], fg=FG_DIM,
                             font=("TkDefaultFont", 12),
                             anchor="w").pack(anchor="w", padx=pad, pady=(0, 10))

        return wrapper

    def mainloop(self, n=0):
        self.mainloop_started.set()
        super().mainloop(n)

    def show_page(self, name):
        log.debug(f"Page opened: '{name}'")
        self.current_page = name
        self.pages[name].tkraise()
        for listener in getattr(self, "page_shown_listeners", []):
            try:
                listener(name)
            except Exception as e:
                log.error(f"page listener failed: {e}")
        for btn in self.nav_buttons.values():
            self.refresh_button(btn)

if __name__ == "__main__":
    if "--launcher" in sys.argv:
        import bootstrapper
        bootstrapper.run_standalone()
    else:
        try:
            import bootstrapper
            bootstrapper.refresh_shortcut()
        except Exception:
            pass
        app = Lution()
        app.mainloop()
