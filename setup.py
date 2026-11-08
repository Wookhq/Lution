# setup wizard that checks if sober is instaled and the faq and tells u to customize lution or not and yeah

import json
import subprocess
import sys
import threading
import tkinter as tk
import webbrowser
from pathlib import Path

import log
import paths
import sober
import themes

SETUP_FLAG = paths.STATE_DIR / "setup_done.json"
REPO_URL = "https://github.com/Wookhq/Lution"
BASE = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))

_theme = themes.load_theme()
BG = _theme["bg"]
BG_ACTIVE = "#2a2a2a"
FG = _theme["fg"]
FG_DIM = "#888888"
ACCENT = _theme["accent"]
ERROR = "#e06c75"
DARK_TEXT = "#0a0a0a"
BODY_FONT = ("TkDefaultFont", 13)
SMALL_FONT = ("TkDefaultFont", 10)

INSTALL_GUIDE = (
    "Sober is installed and updated through Flatpak.\n\n"
    "install Sober:\n"
    "$ flatpak install flathub org.vinegarhq.Sober\n\n"
    "update Sober:\n"
    "$ flatpak update org.vinegarhq.Sober"
)

FAQ = [
    ("does lution have docs?",
     "no, https://lution.chip.is-a.dev/ is lution's old docs and lution has been rewritten and simply does not need docs because it's easy to use and install."),
    ("can i use blacklisted fflags and hacks using lution?",
     "no."),
    ("i found a bug, what do i do? ",
     "make an issue in Lution's github or join the discord server also through Lution's github in the readme"),
]


def reset():
    try:
        SETUP_FLAG.unlink()
    except FileNotFoundError:
        pass
    except OSError as e:
        log.error(f"could not reset setup state: {e}")


def restart(app):
    reset()
    show_wizard(app)


def is_complete():
    return SETUP_FLAG.exists()


def mark_complete():
    try:
        SETUP_FLAG.parent.mkdir(parents=True, exist_ok=True)
        SETUP_FLAG.write_text(json.dumps({"completed": True}, indent=2) + "\n")
    except OSError as e:
        log.error(f"could not save setup state: {e}")


def _open_guide(app):
    win = tk.Toplevel(app, bg=BG)
    win.title("Install Sober")
    win.configure(bg=BG)
    win.resizable(False, False)

    text = tk.Text(win, bg=BG_ACTIVE, fg=FG, font=("TkDefaultFont", 12),
                   relief="flat", highlightthickness=0, wrap="word",
                   padx=16, pady=16, width=64, height=10, cursor="xterm")
    text.insert("1.0", INSTALL_GUIDE)
    text.configure(state="disabled")
    text.pack(fill="both", expand=True)


def _welcome_step(app, frame):
    middle = tk.Frame(frame, bg=BG)
    middle.pack(expand=True)

    logo_path = BASE / "lution.png"
    if logo_path.exists():
        raw = tk.PhotoImage(file=str(logo_path))
        factor = max(1, max(raw.width(), raw.height()) // 318)
        logo = raw.subsample(factor, factor)
        frame._logo = logo
        tk.Label(middle, image=logo, bg=BG).pack(pady=(0, 20))

    tk.Label(middle,
             text="Welcome to Lution, an alternative to Bloxstrap but on "
                  "Linux!",
             bg=BG, fg=FG, font=("TkDefaultFont", 22, "bold"),
             wraplength=820, justify="center", anchor="center"
             ).pack()


def _sober_step(app, frame):
    tk.Label(frame, text="Check Sober", bg=BG, fg=FG,
             font=("TkDefaultFont", 17, "bold"), anchor="w"
             ).pack(anchor="w", padx=48, pady=(32, 4))
    tk.Label(frame,
             text="Lution needs Sober installed through Flatpak. this step "
                  "only checks that it is there.",
             bg=BG, fg=FG_DIM, font=BODY_FONT, anchor="w",
             justify="left", wraplength=820
             ).pack(anchor="w", padx=48, pady=(0, 16))

    status = tk.Label(frame, text="checking for Sober...", bg=BG,
                      fg=FG_DIM, font=BODY_FONT, anchor="w",
                      justify="left", wraplength=820)
    status.pack(anchor="w", padx=48, pady=(0, 16))

    holder = {"running": False, "result": None}

    def apply(text, color):
        status.configure(text=text, fg=color)

    def poll():
        if holder["result"] is not None:
            text, color = holder["result"]
            holder["result"] = None
            apply(text, color)
            return
        if holder["running"]:
            app.after(100, poll)

    def check():
        if holder["running"]:
            return
        holder["running"] = True
        apply("checking for Sober...", FG_DIM)

        def work():
            text = ""
            color = FG_DIM
            try:
                result = subprocess.run(
                    ["flatpak", "info", paths.SOBER_APP_ID],
                    capture_output=True, text=True, timeout=10,
                    env=sober.clean_env())
                version = None
                for line in result.stdout.splitlines():
                    if line.strip().startswith("Version:"):
                        version = line.split(":", 1)[1].strip()
                        break
                if result.returncode == 0:
                    if version:
                        text = f"Sober {version} is installed."
                    else:
                        text = "Sober is installed."
                    color = ACCENT
                    log.info(f"Setup: Sober {version or 'installed'}")
                else:
                    text = ("Sober is not installed yet. install it with "
                            "Flatpak, then press Re-check.")
                    color = ERROR
                    log.info("Setup: Sober not installed")
            except Exception as e:
                text = f"could not check Sober: {e}"
                color = ERROR
                log.error(f"Setup: Sober check failed: {e}")
            holder["result"] = (text, color)
            holder["running"] = False

        threading.Thread(target=work, daemon=True).start()
        app.after(100, poll)

    row = tk.Frame(frame, bg=BG)
    row.pack(anchor="w", padx=48, pady=(0, 20))
    app.make_button(row, "Re-check", command=check, padx=16, pady=8
                    ).pack(side="left", padx=(0, 8))
    app.make_button(row, "How to install Sober",
                    command=lambda: _open_guide(app), padx=16, pady=8
                    ).pack(side="left")

    app.after(200, check)


def _theme_step(app, frame):
    tk.Label(frame, text="Lution theme", bg=BG, fg=FG,
             font=("TkDefaultFont", 17, "bold"), anchor="w"
             ).pack(anchor="w", padx=48, pady=(32, 4))
    tk.Label(frame,
             text="pick Lution's colors. you can change these later on the "
                  "Config page.",
             bg=BG, fg=FG_DIM, font=BODY_FONT, anchor="w",
             justify="left", wraplength=820
             ).pack(anchor="w", padx=48, pady=(0, 14))

    current = themes.load_theme()
    labels = {
        "accent": "Accent",
        "bg": "Background",
        "bg_sidebar": "Sidebar",
        "fg": "Text",
    }
    entries = {}

    form = tk.Frame(frame, bg=BG)
    form.pack(anchor="w", fill="x", padx=48, pady=(0, 10))

    for key in themes.COLOR_KEYS:
        row = tk.Frame(form, bg=BG)
        row.pack(anchor="w", fill="x", pady=(0, 6))
        tk.Label(row, text=labels[key], bg=BG, fg=FG,
                 font=BODY_FONT, width=12, anchor="w").pack(side="left")
        entry = tk.Entry(row, bg=BG_ACTIVE, fg=FG, insertbackground=FG,
                         font=BODY_FONT, relief="flat",
                         highlightthickness=1,
                         highlightbackground=BG_ACTIVE,
                         highlightcolor=ACCENT)
        entry.insert(0, current[key])
        entry.pack(side="left", fill="x", expand=True, ipady=7,
                   padx=(0, 8))
        entries[key] = entry
        swatch = tk.Label(row, bg=current[key], width=3, height=1,
                          relief="flat", highlightthickness=1,
                          highlightbackground=BG_ACTIVE)
        swatch.pack(side="left")

        def update_swatch(event=None, ent=entry, sw=swatch):
            val = ent.get().strip()
            if len(val) == 7 and val.startswith("#"):
                try:
                    int(val[1:], 16)
                    sw.configure(bg=val)
                except ValueError:
                    pass

        entry.bind("<KeyRelease>", update_swatch)

    status = tk.Label(frame, text="", bg=BG, fg=FG_DIM,
                      font=SMALL_FONT, anchor="w", justify="left",
                      wraplength=820)
    status.pack(anchor="w", padx=48, pady=(0, 10))

    def save():
        colors = {}
        for key in themes.COLOR_KEYS:
            val = entries[key].get().strip()
            if len(val) == 7 and val.startswith("#"):
                try:
                    int(val[1:], 16)
                except ValueError:
                    status.configure(text=f"invalid hex color for {labels[key]}",
                                     fg=ERROR)
                    return
            else:
                status.configure(text=f"invalid hex color for {labels[key]}",
                                 fg=ERROR)
                return
            colors[key] = val
        themes.save_theme(colors)
        status.configure(text="theme saved. restart Lution to apply it.",
                         fg=FG_DIM)

    def restore():
        themes.save_theme(dict(themes.DEFAULTS))
        for key in themes.COLOR_KEYS:
            entries[key].delete(0, "end")
            entries[key].insert(0, themes.DEFAULTS[key])
        status.configure(text="default theme restored. restart Lution to "
                              "apply it.", fg=FG_DIM)

    row = tk.Frame(frame, bg=BG)
    row.pack(anchor="w", padx=48, pady=(0, 20))
    app.make_button(row, "Save theme", command=save, padx=16, pady=8
                    ).pack(side="left", padx=(0, 8))
    app.make_button(row, "Restore defaults", command=restore,
                    bg=ERROR, fg=DARK_TEXT, padx=16, pady=8
                    ).pack(side="left")


def _faq_step(app, frame):
    tk.Label(frame, text="FAQ", bg=BG, fg=FG,
             font=("TkDefaultFont", 17, "bold"), anchor="w"
             ).pack(anchor="w", padx=48, pady=(32, 10))

    for question, answer in FAQ:
        tk.Label(frame, text=question, bg=BG, fg=FG,
                 font=("TkDefaultFont", 13, "bold"), anchor="w"
                 ).pack(anchor="w", padx=48, pady=(0, 2))
        tk.Label(frame, text=answer, bg=BG, fg=FG_DIM,
                 font=BODY_FONT, anchor="w", justify="left",
                 wraplength=820).pack(anchor="w", padx=48, pady=(0, 12))

    tk.Label(frame, text="support us", bg=BG, fg=FG,
             font=("TkDefaultFont", 15, "bold"), anchor="w"
             ).pack(anchor="w", padx=48, pady=(8, 4))
    tk.Label(frame,
             text="Lution is free and open source. if it is useful to you, "
                  "giving the repository a star helps a lot :D",
             bg=BG, fg=FG_DIM, font=BODY_FONT, anchor="w",
             justify="left", wraplength=820
             ).pack(anchor="w", padx=48, pady=(0, 12))
    app.make_button(frame, "Open Lution on GitHub",
                    command=lambda: webbrowser.open(REPO_URL),
                    padx=16, pady=8
                    ).pack(anchor="w", padx=48, pady=(0, 20))


def show_wizard(app):
    existing = getattr(app, "_setup_overlay", None)
    if existing is not None:
        try:
            if existing.winfo_exists():
                existing.destroy()
        except Exception:
            pass

    overlay = tk.Frame(app, bg=BG)
    app._setup_overlay = overlay
    overlay.grid(row=0, column=0, columnspan=2, sticky="nsew")
    overlay.lift()
    overlay.rowconfigure(0, weight=1)
    overlay.columnconfigure(0, weight=1)

    canvas = tk.Canvas(overlay, bg=BG, highlightthickness=0)
    scrollbar = tk.Scrollbar(overlay, orient="vertical", command=canvas.yview,
                             bg=BG, troughcolor=BG, activebackground=FG_DIM,
                             width=10)
    stack = tk.Frame(canvas, bg=BG)
    window = canvas.create_window((0, 0), window=stack, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")
    canvas._lution_scrollable = True
    stack.columnconfigure(0, weight=1)
    stack.rowconfigure(0, weight=1)

    steps = []
    for builder in (_welcome_step, _sober_step, _theme_step, _faq_step):
        frame = tk.Frame(stack, bg=BG)
        builder(app, frame)
        steps.append(frame)

    state = {"index": 0}

    indicator = tk.Label(overlay, text="", bg=BG, fg=FG_DIM,
                         font=SMALL_FONT, anchor="center")
    indicator.grid(row=1, column=0, columnspan=2, sticky="ew",
                   pady=(10, 6))

    nav = tk.Frame(overlay, bg=BG)
    nav.grid(row=2, column=0, columnspan=2, pady=(0, 28))

    def finish():
        mark_complete()
        log.info("Setup completed")
        overlay.destroy()
        if getattr(app, "_setup_overlay", None) is overlay:
            app._setup_overlay = None

    def resize(event=None):
        index = state["index"]
        width = max(1, canvas.winfo_width())
        height = max(canvas.winfo_height(), steps[index].winfo_reqheight())
        canvas.itemconfigure(window, width=width, height=height)
        canvas.configure(scrollregion=(0, 0, width, height))

    def show(index):
        state["index"] = max(0, min(index, len(steps) - 1))
        for position, frame in enumerate(steps):
            if position == state["index"]:
                frame.grid(row=0, column=0, sticky="nsew")
            else:
                frame.grid_remove()
        indicator.configure(text=f"step {state['index'] + 1} of {len(steps)}")
        next_btn.configure(
            text="Finish" if state["index"] == len(steps) - 1 else "Next")
        app.update_idletasks()
        resize()

    def go_back():
        show(state["index"] - 1)

    def go_next():
        if state["index"] == len(steps) - 1:
            finish()
        else:
            show(state["index"] + 1)

    back_btn = app.make_button(nav, "Back", command=go_back, padx=18, pady=10)
    back_btn.pack(side="left", padx=(0, 8))
    next_btn = app.make_button(nav, "Next", command=go_next, padx=18, pady=10)
    next_btn.pack(side="left", padx=(0, 8))
    skip_btn = app.make_button(nav, "Skip setup", command=finish,
                               bg=BG_ACTIVE, fg=FG, padx=18, pady=10)
    skip_btn.pack(side="left")

    canvas.bind("<Configure>", resize)
    show(0)
    return overlay
