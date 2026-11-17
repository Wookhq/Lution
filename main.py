# lution developed by wookhq uhh hello
# i shortened this because triplean said half of lution is in main.py so like why not split it more
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import subprocess
import json
import sys
import threading
import queue
import os
import shlex
import shutil

import themes
import paths
import log
import sober

log.install_hooks()

BASE = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
CONFIG_FILE = BASE / "ui.md"

def load_theme_globals():
    global BG, BG_SIDEBAR, BG_ACTIVE, FG, FG_DIM, ACCENT, ERROR, BORDER
    global INPUT_BG, INPUT_FG, INPUT_BORDER, BUTTON_BG, BUTTON_FG, BUTTON_HOVER
    global SCROLLBAR, SCROLLBAR_HOVER, _widgets, _WIDGET_BUILDERS
    t = themes.load_theme()
    BG = t["bg"]
    BG_SIDEBAR = t["bg_sidebar"]
    BG_ACTIVE = t.get("bg_active", "#2a2a2a")
    FG = t["fg"]
    FG_DIM = t.get("fg_dim", "#888888")
    ACCENT = t["accent"]
    ERROR = t.get("error", "#e06c75")
    BORDER = t.get("border", "#3a3a3a")
    INPUT_BG = t.get("input_bg", "#2a2a2a")
    INPUT_FG = t.get("input_fg", "#e0e0e0")
    INPUT_BORDER = t.get("input_border", "#3a3a3a")
    BUTTON_BG = t.get("button_bg", ACCENT)
    BUTTON_FG = t.get("button_fg", "#0a0a0a")
    BUTTON_HOVER = t.get("button_hover") or None
    SCROLLBAR = t.get("scrollbar", "#3a3a3a")
    SCROLLBAR_HOVER = t.get("scrollbar_hover", "#5a5a5a")
    _widgets = None
    _WIDGET_BUILDERS = None

load_theme_globals()
BODY_FONT = ("TkDefaultFont", 13)

APK_CHECKSUM_FILE = Path.home() / ".local" / "Lution" / "apk_checksum.txt"
LEGACY_CHECKSUM_FILES = [
    Path.home() / ".local/Lution/emoji_checksum.txt",
    Path.home() / ".local/Lution/cursor_checksum.txt",
    Path.home() / ".local/Lution/mods_checksum.txt",
    Path.home() / ".local/Lution/sounds_checksum.txt",
]

_widgets = None
_WIDGET_BUILDERS = None


def get_widgets():
    global _widgets, _WIDGET_BUILDERS
    if _widgets is None:
        import widgets as w
        w.BG = BG
        w.BG_SIDEBAR = BG_SIDEBAR
        w.BG_ACTIVE = BG_ACTIVE
        w.FG = FG
        w.FG_DIM = FG_DIM
        w.ACCENT = ACCENT
        w.ERROR = ERROR
        w.BORDER = BORDER
        w.INPUT_BG = INPUT_BG
        w.INPUT_FG = INPUT_FG
        w.INPUT_BORDER = INPUT_BORDER
        w.SCROLLBAR = SCROLLBAR
        w.SCROLLBAR_HOVER = SCROLLBAR_HOVER
        w.BODY_FONT = BODY_FONT
        _widgets = w
        _WIDGET_BUILDERS = {
            "flaglist": w.build_flaglist,
            "fpsinput": w.build_fpsinput,
            "envvars": w.build_envvars,
            "bootstrapper": w.build_bootstrapper,
            "fontpicker": w.build_fontpicker,
            "cursorpicker": w.build_cursorpicker,
            "emotewheelpicker": w.build_emotewheelpicker,
            "themepicker": w.build_themepicker,
            "emojipicker": w.build_emojipicker,
            "versionlabel": w.build_versionlabel,
            "soberversion": w.build_soberversion,
            "soberguide": w.build_soberguide,
            "soberlauncher": w.build_soberlauncher,
            "sobersettings": w.build_sobersettings,
            "playhistory": w.build_playhistory,
            "marketplace": w.build_marketplace,
            "resetall": w.build_resetall,
            "backupmanager": w.build_backupmanager,
            "modconflicts": w.build_modconflicts,
            "modmanager": w.build_modmanager,
            "soundmods": w.build_soundmods,
            "serverselector": w.build_serversel,
            "shortcutmanager": w.build_shortcuts,
            "account": w.build_account,
            "restartsetup": w.build_restartsetup,
        }
    return _widgets, _WIDGET_BUILDERS

def _find_apk():
    return paths.find_base_apk()

def _calculate_sha256_checksum(apk_path):
    import hashlib
    with open(apk_path, "rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()

def _has_files(path):
    try:
        return path.is_dir() and any(p.is_file() for p in path.rglob("*"))
    except OSError:
        return False

def _customizations_present():
    import fonts
    import emoji
    import cursors
    import emote_wheel
    import mods
    import sound_mods

    overlay = paths.LUTION_OVERLAY

    if _has_files(fonts.INSTALLED_FONTS_DIR):
        font_dir = overlay / "content/fonts"
        emoji_names = {name.lower() for name in emoji.EMOJI_FONT_NAMES}
        try:
            if not any(p.is_file() and p.name.lower() not in emoji_names
                       for p in font_dir.iterdir()):
                return False
        except OSError:
            return False

    if _has_files(emoji.INSTALLED_EMOJI_DIR):
        font_dir = overlay / "content/fonts"
        if not all((font_dir / name).exists()
                   for name in emoji.EMOJI_FONT_NAMES):
            return False

    try:
        for path in cursors.INSTALLED_CURSORS_DIR.glob("*.png"):
            if not (cursors.OVERLAY_TEXTURE_DIR / path.name).exists():
                return False
        for path in emote_wheel.INSTALLED_EMOTE_DIR.glob("*.png"):
            for scale in emote_wheel.SCALES:
                target = emote_wheel.OVERLAY_EMOTE_DIR / f"{path.stem}{scale}.png"
                if not target.exists():
                    return False
        if sound_mods.INSTALLED_SOUNDS_DIR.exists():
            for path in sound_mods.INSTALLED_SOUNDS_DIR.iterdir():
                if path.is_file() and not (
                        sound_mods.OVERLAY_SOUNDS_DIR / path.name).exists():
                    return False
    except OSError:
        return False

    if mods._load_manifest() and not mods.content_present():
        return False

    return True

def reapply_customizations():
    import fonts
    import emoji
    import cursors
    import emote_wheel
    import mods
    import sound_mods

    for legacy in LEGACY_CHECKSUM_FILES:
        try:
            if legacy.exists():
                legacy.unlink()
                log.debug(f"Removed old checksum file {legacy.name}")
        except OSError as e:
            log.warning(f"Could not remove old checksum file {legacy}: {e}")

    apk_path = _find_apk()
    if apk_path is None:
        log.debug("Sober apk not found")
        return

    current = _calculate_sha256_checksum(apk_path)
    last = ""
    if APK_CHECKSUM_FILE.exists():
        last = APK_CHECKSUM_FILE.read_text().strip()

    if current == last and _customizations_present():
        log.debug("Sober apk unchanged and customizations are still applied")
        return

    if current != last:
        log.info("Sober apk changed we reapplying all customizations")
    else:
        log.info("Sober overlay lost customizations, reapplying them")
    failed = []
    for name, fn in (("fonts", fonts.reapply_fonts),
                     ("emoji", emoji.reapply_emoji),
                     ("cursors", cursors.reapply_cursors),
                     ("emote wheel", emote_wheel.reapply_wheel),
                     ("mods", mods.reapply_mods),
                     ("sounds", sound_mods.reapply_sounds)):
        try:
            result = fn()
            if name == "mods" and result:
                failed.extend(result)
        except Exception as e:
            log.error(f"Failed to reapply {name}: {e}")
            failed.append(name)

    if failed:
        log.error(f"Not recording the new APK checksum, retry next launch: "
                  f"{', '.join(str(f) for f in failed)}")
        return

    try:
        APK_CHECKSUM_FILE.parent.mkdir(parents=True, exist_ok=True)
        APK_CHECKSUM_FILE.write_text(current)
    except OSError as e:
        log.error(f"Could not save APK checksum: {e}")

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
            try:
                rest = shlex.split(line[len("CreateButton > "):].strip())
            except ValueError as e:
                log.warning(f"Ignoring CreateButton with invalid arguments: {e}")
                pending_label = None
                continue
            if not rest:
                log.warning("Ignoring CreateButton with no script")
                pending_label = None
                continue
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

        elif line == "EmoteWheelPicker":
            if current is not None:
                pages[current].append(("emotewheelpicker",))

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

        elif line == "SoberGuide":
            if current is not None:
                pages[current].append(("soberguide",))

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

        elif line == "ServerSelector":
            if current is not None:
                pages[current].append(("serverselector",))

        elif line == "ShortcutManager":
            if current is not None:
                pages[current].append(("shortcutmanager",))

        elif line == "Account":
            if current is not None:
                pages[current].append(("account",))

        elif line == "RestartSetup":
            if current is not None:
                pages[current].append(("restartsetup",))

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

    if not path.exists():
        log.error(f"Script not found: {path}")
        return

    try:
        if path.suffix == ".py":
            if getattr(sys, "frozen", False) or globals().get("__compiled__"):
                python = shutil.which("python3") or "python3"
            else:
                python = sys.executable or "python3"
            subprocess.Popen([python, str(path), *args],
                             env=sober.clean_env())
        else:
            subprocess.Popen([str(path), *args],
                             env=sober.clean_env())
    except OSError as e:
        log.exception(f"Could not run {path}: {e}")

class Lution(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Lution")
        self.configure(bg=BG)
        self.minsize(1280, 720)

        self.mainloop_started = threading.Event()
        self._ui_queue = queue.Queue()
        self.after(50, self._drain_ui_queue)

        self.setup_style()

        self.bind_all("<MouseWheel>", self._global_scroll)
        self.bind_all("<Button-4>", self._global_scroll)
        self.bind_all("<Button-5>", self._global_scroll)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.pages_config = parse_config(CONFIG_FILE)
        self.nav_buttons = {}
        self.pages = {}
        self.fflag_rows = []
        self.reload_fflags_ui = lambda: None

        self.page_shown_listeners = []
        self._visible_logged = False
        self.bind("<Map>", self._on_map)

        self.build_sidebar()
        self.build_content()

        import setup as setup_mod
        if not setup_mod.is_complete():
            setup_mod.show_wizard(self)

        self.after_idle(self._start_background_tasks)
        self.update_idletasks()
        self.after(0, self._post_show_init)

    def _post_show_init(self):
        log.debug(f"Loaded {len(self.pages_config)} page(s) from ui.md")

    def _start_background_tasks(self):
        threading.Thread(target=self._run_startup_tasks, daemon=True).start()

    def _run_startup_tasks(self):
        try:
            reapply_customizations()
        except Exception:
            log.exception("Startup customization check failed")

    def report_callback_exception(self, exc, val, tb):
        log.tk_exception(exc, val, tb)

    def run_on_ui(self, fn):
        self._ui_queue.put(fn)

    def after(self, ms, func=None, *args):
        queue_ = getattr(self, "_ui_queue", None)
        if (func is not None and queue_ is not None
                and threading.current_thread() is not threading.main_thread()):
            queue_.put(lambda: self.after(ms, func, *args))
            return None
        return super().after(ms, func, *args)

    def _drain_ui_queue(self):
        while True:
            try:
                fn = self._ui_queue.get_nowait()
            except queue.Empty:
                break
            try:
                fn()
            except Exception:
                log.exception("UI callback failed")
        try:
            self.after(50, self._drain_ui_queue)
        except tk.TclError:
            pass

    def setup_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TCombobox",
                         fieldbackground=INPUT_BG, background=INPUT_BG,
                         foreground=INPUT_FG, arrowcolor=INPUT_FG,
                         bordercolor=INPUT_BORDER,
                         lightcolor=INPUT_BORDER, darkcolor=INPUT_BORDER)
        style.map("TCombobox", fieldbackground=[("readonly", INPUT_BG)])

    def make_button(self, parent, text, command=None, bg=None, fg=None,
                     font=BODY_FONT, padx=20, pady=10):
        bg = BUTTON_BG if bg is None else bg
        fg = BUTTON_FG if fg is None else fg
        pressed_bg = (BUTTON_HOVER or darken(bg)) if bg == BUTTON_BG else darken(bg)
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
        self.sidebar = sidebar
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
            wrapper = tk.Frame(self.container, bg=BG)
            wrapper.grid(row=0, column=0, sticky="nsew")
            self.pages[name] = {"frame": wrapper, "cfg": widgets_cfg, "built": False}

        if self.pages_config:
            self.current_page = None
            self._pending_page = next(iter(self.pages_config))
            self.after(0, self._build_all_pages_bg)

    def build_page(self, name, widgets_cfg, wrapper=None):
        if wrapper is None:
            wrapper = tk.Frame(self.container, bg=BG)

        canvas = tk.Canvas(wrapper, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(wrapper, orient="vertical",
                                  command=canvas.yview,
                                  bg=SCROLLBAR, troughcolor=SCROLLBAR,
                                  activebackground=SCROLLBAR_HOVER, width=10)
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
                 anchor="w").pack(anchor="w", pady=(0, 8))

        group = None
        group_inputs = []

        def new_group():
            frame = tk.Frame(page, bg=BG_ACTIVE, highlightthickness=1,
                              highlightbackground=BORDER)
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
                entry = tk.Entry(target, bg=INPUT_BG, fg=INPUT_FG,
                                  insertbackground=INPUT_FG, font=BODY_FONT,
                                  relief="flat", highlightthickness=1,
                                  highlightbackground=INPUT_BORDER,
                                  highlightcolor=ACCENT)
                state = {"placeholder": bool(placeholder)}
                if placeholder:
                    entry.insert(0, placeholder)
                    entry.configure(fg=FG_DIM)

                    def clear_placeholder(e=None, ent=entry, st=state):
                        if st["placeholder"]:
                            ent.delete(0, "end")
                            ent.configure(fg=FG)
                            st["placeholder"] = False

                    def restore_placeholder(e=None, ent=entry, st=state,
                                            text=placeholder):
                        if not ent.get().strip():
                            ent.delete(0, "end")
                            ent.insert(0, text)
                            ent.configure(fg=FG_DIM)
                            st["placeholder"] = True

                    entry.bind("<FocusIn>", clear_placeholder)
                    entry.bind("<FocusOut>", restore_placeholder)
                entry.pack(anchor="w", fill="x", padx=pad,
                            pady=(0, 10), ipady=8)

                def entry_value(e=entry, st=state):
                    return "" if st["placeholder"] else e.get()

                group_inputs.append(entry_value)

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

            elif kind in ("flaglist", "fpsinput", "envvars", "bootstrapper", "fontpicker",
                         "cursorpicker", "emotewheelpicker", "themepicker", "emojipicker",
                         "versionlabel", "soberversion", "soberguide", "soberlauncher",
                         "sobersettings", "playhistory", "marketplace", "resetall",
                         "backupmanager", "modconflicts", "modmanager", "soundmods",
                         "serverselector", "shortcutmanager", "account", "restartsetup"):
                target = group if group is not None else page
                pad = 14 if group is not None else 0
                _, builders = get_widgets()
                builders[kind](self, target, pad)

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

    def _on_map(self, event):
        if not self._visible_logged:
            self._visible_logged = True
            log.info("Starting Lution")
        return None

    def _build_all_pages_bg(self):
        name = getattr(self, "_pending_page", None)
        if not name:
            return
        self._pending_page = None
        self._build_first_page(name)
        self.after(700, self._warm_remaining_pages)

    def _warm_remaining_pages(self):
        for name, entry in self.pages.items():
            if not entry["built"]:
                self._build_page_on_main(name)
                self.after(150, self._warm_remaining_pages)
                return

    def _build_page_on_main(self, name):
        entry = self.pages[name]
        if entry["built"]:
            return
        try:
            self.build_page(name, entry["cfg"], entry["frame"])
        except Exception:
            log.exception(f"Failed to build page '{name}'")
        entry["built"] = True

    def _build_first_page(self, name):
        self._build_page_on_main(name)
        try:
            self.show_page(name)
        except Exception:
            log.exception(f"Failed to show page '{name}'")

    def reload_theme(self):
        current = getattr(self, "current_page", None)
        load_theme_globals()
        self.configure(bg=BG)
        self.setup_style()
        for widget in (getattr(self, "sidebar", None),
                       getattr(self, "container", None)):
            try:
                if widget is not None and widget.winfo_exists():
                    widget.destroy()
            except tk.TclError:
                pass
        self.nav_buttons = {}
        self.pages = {}
        self.fflag_rows = []
        self.reload_fflags_ui = lambda: None
        self.page_shown_listeners = []
        self.build_sidebar()
        self.build_content()
        self._pending_page = None
        self.update_idletasks()
        if current in self.pages:
            self.show_page(current)
        self.after(0, self._warm_remaining_pages)

    def show_page(self, name):
        log.debug(f"Page opened: '{name}'")
        self.current_page = name
        entry = self.pages[name]
        self._build_page_on_main(name)
        entry["frame"].tkraise()
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
    elif "--play" in sys.argv:
        import bootstrapper
        pos = sys.argv.index("--play")
        place = sys.argv[pos + 1] if pos + 1 < len(sys.argv) else ""
        url = None
        if str(place).isdigit():
            url = f"roblox://experiences/start?placeId={place}"
        else:
            log.error(f"--play needs a place id, got: {place!r}")
            sys.exit(1)
        bootstrapper.run_standalone(url=url, autostart=True)
    else:
        app = Lution()

        def startup_bg():
            try:
                import fflags
                fflags.refresh_allowlist_if_stale()
            except Exception:
                log.exception("Allowlist refresh check failed")
            try:
                import bootstrapper
                bootstrapper.refresh_shortcut()
            except Exception:
                log.exception("Could not refresh the Sober with Lution shortcut")

        threading.Thread(target=startup_bg, daemon=True).start()
        app.mainloop()
