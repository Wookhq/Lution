# yep it's literally all the widgets every textbox, menu, window, dropdown menu, everything bro
import tkinter as tk
from tkinter import ttk, filedialog
import json
import subprocess
import webbrowser
from pathlib import Path
import fflags
import fonts
import fps
import cursors
import themes
import emoji
import mods
import sound_mods
import updater
import envvars
import bootstrapper
import backup
import sys

BG = "#1e1e1e"
BG_SIDEBAR = "#161616"
BG_ACTIVE = "#2a2a2a"
FG = "#e0e0e0"
FG_DIM = "#888888"
ACCENT = "#8D7EDC"
ERROR = "#e06c75"
BODY_FONT = ("TkDefaultFont", 13)

BASE = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))

USER_PRESETS_FILE = Path.home() / ".local/Lution/fflag_user_presets.json"

def _clear_all_fflags(app, reload_fn, status):
    win = tk.Toplevel(app, bg=BG)
    win.title("Clear All FFlags")
    win.geometry("400x120")
    win.configure(bg=BG)
    win.resizable(False, False)

    tk.Label(win, text="Remove all FFlags?", bg=BG, fg=FG,
             font=BODY_FONT).pack(pady=(20, 14))

    btn_row = tk.Frame(win, bg=BG)
    btn_row.pack()

    def confirm():
        fflags.save_fflags({})
        reload_fn()
        status.configure(text="All FFlags cleared.", fg=FG_DIM)
        win.destroy()

    app.make_button(btn_row, "yes clear all", command=confirm,
                      bg=ERROR, fg="#0a0a0a", padx=12, pady=6
                      ).pack(side="left", padx=(0, 8))
    app.make_button(btn_row, "cancel", command=win.destroy,
                      padx=12, pady=6).pack(side="left")

def _export_fflags_json(app, status):
    path = filedialog.asksaveasfilename(
        title="Export FFlags",
        defaultextension=".json",
        filetypes=[("JSON files", "*.json")],
        initialfile="fflags.json"
    )
    if path:
        try:
            current = fflags.get_fflags()
            Path(path).write_text(json.dumps(current, indent=4) + "\n")
            status.configure(text=f"Exported to {Path(path).name}", fg=FG_DIM)
        except Exception as e:
            status.configure(text=str(e), fg=ERROR)

def _load_fflag_presets():
    builtins = {}
    path = BASE / "fflag_presets.json"
    if path.exists():
        try:
            builtins = json.loads(path.read_text())
        except Exception:
            pass

    user = {}
    if USER_PRESETS_FILE.exists():
        try:
            user = json.loads(USER_PRESETS_FILE.read_text())
        except Exception:
            pass

    return builtins, user

def _save_user_presets(presets):
    USER_PRESETS_FILE.parent.mkdir(parents=True, exist_ok=True)
    USER_PRESETS_FILE.write_text(json.dumps(presets, indent=2) + "\n")

def build_flaglist(app, parent, pad):
    search_row = tk.Frame(parent, bg=parent["bg"])
    search_row.pack(anchor="w", fill="x", padx=pad, pady=(0, 6))

    tk.Label(search_row, text="Search", bg=parent["bg"], fg=FG,
             font=BODY_FONT).pack(side="left", padx=(0, 8))

    search_var = tk.StringVar()
    search_entry = tk.Entry(search_row, bg=BG, fg=FG, insertbackground=FG,
                             font=BODY_FONT, relief="flat",
                             highlightthickness=1,
                             highlightbackground=BG_SIDEBAR,
                             highlightcolor=ACCENT,
                             textvariable=search_var)
    search_entry.pack(side="left", fill="x", expand=True, ipady=6)

    count_label = tk.Label(search_row, text="", bg=parent["bg"], fg=FG_DIM,
                            font=("TkDefaultFont", 10))
    count_label.pack(side="left", padx=(8, 0))

    list_frame = tk.Frame(parent, bg=parent["bg"])
    list_frame.columnconfigure(0, weight=1)
    list_frame.pack(anchor="w", fill="x", padx=pad, pady=(0, 6))

    status = tk.Label(parent, text="", bg=parent["bg"], fg=FG_DIM,
                       font=("TkDefaultFont", 10), anchor="w",
                       wraplength=500, justify="left")
    status.pack(anchor="w", padx=pad, pady=(0, 6))

    btn_row = tk.Frame(parent, bg=parent["bg"])
    btn_row.pack(anchor="w", fill="x", padx=pad, pady=(0, 14))

    def apply_filter():
        query = search_var.get().strip().lower()
        shown = 0
        for key_entry, _, row in app.fflag_rows:
            matches = not query or query in key_entry.get().strip().lower()
            if matches:
                row.grid()
                shown += 1
            else:
                row.grid_remove()
        total = len(app.fflag_rows)
        count_label.configure(
            text=f"{shown}/{total} flags" if query else f"{total} flags")

    search_var.trace_add("write", lambda *_: apply_filter())

    def add_row(key="", value=""):
        list_frame.pack(anchor="w", fill="x", padx=pad, pady=(0, 6),
                        before=status)
        row_index = len(app.fflag_rows)
        row = tk.Frame(list_frame, bg=parent["bg"])
        row.grid(row=row_index, column=0, sticky="ew", pady=3)

        key_entry = tk.Entry(row, bg=BG, fg=FG, insertbackground=FG,
                              font=BODY_FONT, relief="flat", width=32,
                              highlightthickness=1,
                              highlightbackground=BG_SIDEBAR,
                              highlightcolor=ACCENT)
        key_entry.insert(0, key)
        key_entry.pack(side="left", padx=(0, 6), ipady=6)

        value_entry = tk.Entry(row, bg=BG, fg=FG, insertbackground=FG,
                                font=BODY_FONT, relief="flat", width=16,
                                highlightthickness=1,
                                highlightbackground=BG_SIDEBAR,
                                highlightcolor=ACCENT)
        value_entry.insert(0, value)
        value_entry.pack(side="left", padx=(0, 6), ipady=6)

        remove_btn = app.make_button(row, "x", command=lambda: remove_row(row),
                                      bg=BG_SIDEBAR, fg=FG_DIM,
                                      padx=10, pady=4)
        remove_btn.pack(side="left")

        app.fflag_rows.append((key_entry, value_entry, row))
        apply_filter()

    def open_add_flag():
        win = tk.Toplevel(app, bg=BG)
        win.title("Add FFlag")
        win.geometry("500x300")
        win.configure(bg=BG)
        win.resizable(False, False)

        tk.Label(win, text="Flag name:", bg=BG, fg=FG,
                 font=BODY_FONT).pack(anchor="w", padx=16, pady=(16, 2))
        key_entry = tk.Entry(win, bg=BG_ACTIVE, fg=FG, insertbackground=FG,
                              font=BODY_FONT, relief="flat", width=40,
                              highlightthickness=1,
                              highlightbackground=BG_SIDEBAR,
                              highlightcolor=ACCENT)
        key_entry.pack(anchor="w", padx=16, ipady=6)
        key_entry.focus()

        tk.Label(win, text="Value:", bg=BG, fg=FG,
                 font=BODY_FONT).pack(anchor="w", padx=16, pady=(8, 2))
        val_entry = tk.Entry(win, bg=BG_ACTIVE, fg=FG, insertbackground=FG,
                              font=BODY_FONT, relief="flat", width=40,
                              highlightthickness=1,
                              highlightbackground=BG_SIDEBAR,
                              highlightcolor=ACCENT)
        val_entry.pack(anchor="w", padx=16, ipady=6)

        def do_add():
            key = key_entry.get().strip()
            val = val_entry.get().strip()
            if key:
                add_row(key, val)
                win.destroy()

        key_entry.bind("<Return>", lambda e: do_add())
        val_entry.bind("<Return>", lambda e: do_add())

        app.make_button(win, "Add", command=do_add, padx=12, pady=6
                         ).pack(anchor="w", padx=16, pady=(12, 16))

    def remove_row(row):
        app.fflag_rows = [r for r in app.fflag_rows if r[2] is not row]
        row.destroy()
        for i, (_, _, r) in enumerate(app.fflag_rows):
            was_hidden = not r.winfo_manager()
            r.grid_configure(row=i)
            if was_hidden:
                r.grid_remove()
        apply_filter()

    def reload_rows():
        for w in list_frame.winfo_children():
            w.destroy()
        app.fflag_rows = []
        for key, value in fflags.get_fflags().items():
            add_row(key, str(value))
        if app.fflag_rows:
            list_frame.pack(anchor="w", fill="x", padx=pad, pady=(0, 6),
                            before=status)
        else:
            list_frame.pack_forget()
        apply_filter()
        parent.event_generate("<Configure>")

    def save_rows():
        new_fflags = {}
        for key_entry, value_entry, _ in app.fflag_rows:
            key = key_entry.get().strip()
            if not key:
                continue
            new_fflags[key] = fflags.parse_value(value_entry.get())
        fflags.save_fflags(new_fflags)
        status.configure(text="Flags saved.", fg=FG_DIM)

    app.reload_fflags_ui = reload_rows

    app.make_button(btn_row, "Add Flag", command=open_add_flag
                     ).pack(side="left", padx=(0, 6))
    app.make_button(btn_row, "Save Flags", command=save_rows
                     ).pack(side="left", padx=(0, 6))
    app.make_button(btn_row, "Paste JSON",
                     command=lambda: _open_paste_json(app)
                     ).pack(side="left", padx=(0, 6))
    app.make_button(btn_row, "Export JSON",
                     command=lambda: _export_fflags_json(app, status)
                     ).pack(side="left", padx=(0, 6))
    app.make_button(btn_row, "Presets",
                     command=lambda: _open_presets_window(app, reload_rows, status)
                     ).pack(side="left", padx=(0, 6))
    app.make_button(btn_row, "Clear All", command=lambda: _clear_all_fflags(app, reload_rows, status),
                     bg=ERROR, fg="#0a0a0a", padx=12
                     ).pack(side="left")

    reload_rows()

def _open_presets_window(app, reload_fn, status):
    win = tk.Toplevel(app, bg=BG)
    win.title("FFlag Presets")
    win.geometry("600x500")
    win.configure(bg=BG)
    win.resizable(True, True)

    builtins, user_presets = _load_fflag_presets()

    def apply_preset(name, flags):
        current = fflags.get_fflags()
        current.update(flags)
        fflags.save_fflags(current)
        reload_fn()
        status.configure(text=f"Applied preset: {name}", fg=FG_DIM)

    canvas = tk.Canvas(win, bg=BG, highlightthickness=0)
    scrollbar = tk.Scrollbar(win, orient="vertical",
                              command=canvas.yview,
                              bg=BG_SIDEBAR, troughcolor=BG_SIDEBAR,
                              activebackground=FG_DIM, width=10)
    body = tk.Frame(canvas, bg=BG)
    body_window = canvas.create_window((0, 0), window=body, anchor="nw")

    canvas.configure(yscrollcommand=scrollbar.set)

    def on_body_configure(e):
        canvas.configure(scrollregion=canvas.bbox("all"))
    body.bind("<Configure>", on_body_configure)

    def on_canvas_configure(e):
        canvas.itemconfigure(body_window, width=e.width)
    canvas.bind("<Configure>", on_canvas_configure)

    def on_mousewheel(e):
        steps = int(-1 * (e.delta / 120))
        if steps == 0 and e.delta:
            steps = -1 if e.delta > 0 else 1
        canvas.yview_scroll(steps, "units")
    def on_scroll_up(e):
        canvas.yview_scroll(-1, "units")
    def on_scroll_down(e):
        canvas.yview_scroll(1, "units")

    win.bind("<MouseWheel>", on_mousewheel)
    win.bind("<Button-4>", on_scroll_up)
    win.bind("<Button-5>", on_scroll_down)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    if builtins:
        tk.Label(body, text="Built-in Presets", bg=BG, fg=FG,
                 font=("TkDefaultFont", 13, "bold"),
                 anchor="w").pack(anchor="w", padx=16, pady=(16, 6))

        bi_frame = tk.Frame(body, bg=BG_ACTIVE, highlightthickness=1,
                             highlightbackground=BG_SIDEBAR)
        bi_frame.pack(anchor="w", fill="x", padx=16, pady=(0, 12))

        for name, data in builtins.items():
            row = tk.Frame(bi_frame, bg=BG_ACTIVE)
            row.pack(anchor="w", fill="x", padx=8, pady=4)

            info = tk.Frame(row, bg=BG_ACTIVE)
            info.pack(side="left", fill="x", expand=True)

            tk.Label(info, text=name, bg=BG_ACTIVE, fg=FG,
                     font=("TkDefaultFont", 11, "bold"),
                     anchor="w").pack(anchor="w")
            desc = data.get("description", "")
            if desc:
                tk.Label(info, text=desc, bg=BG_ACTIVE, fg=FG_DIM,
                         font=("TkDefaultFont", 9),
                         anchor="w").pack(anchor="w")

            app.make_button(row, "Apply", command=lambda n=name, f=data["flags"]: apply_preset(n, f),
                             padx=10, pady=4
                             ).pack(side="right")

    tk.Label(body, text="Your Presets", bg=BG, fg=FG,
             font=("TkDefaultFont", 13, "bold"),
             anchor="w").pack(anchor="w", padx=16, pady=(6, 6))

    user_frame = tk.Frame(body, bg=BG_ACTIVE, highlightthickness=1,
                           highlightbackground=BG_SIDEBAR)
    user_frame.pack(anchor="w", fill="x", padx=16, pady=(0, 12))

    def refresh_user():
        for w in user_frame.winfo_children():
            w.destroy()
        _, up = _load_fflag_presets()
        if not up:
            tk.Label(user_frame, text="No custom presets yet", bg=BG_ACTIVE, fg=FG_DIM,
                     font=("TkDefaultFont", 10)).pack(anchor="w", padx=8, pady=8)
            return
        for name, data in up.items():
            row = tk.Frame(user_frame, bg=BG_ACTIVE)
            row.pack(anchor="w", fill="x", padx=8, pady=4)

            app.make_button(row, name,
                             command=lambda n=name, f=data["flags"]: apply_preset(n, f),
                             padx=10, pady=4
                             ).pack(side="left")

            def delete_preset(n=name):
                d = {}
                if USER_PRESETS_FILE.exists():
                    try:
                        d = json.loads(USER_PRESETS_FILE.read_text())
                    except Exception:
                        pass
                d.pop(n, None)
                _save_user_presets(d)
                refresh_user()

            del_btn = tk.Label(row, text="x", bg=BG_ACTIVE, fg=ERROR,
                                font=("TkDefaultFont", 9), cursor="hand2", padx=4)
            del_btn.pack(side="right")
            del_btn.bind("<Button-1>", lambda e, n=name: delete_preset(n))

    refresh_user()

    def save_as_preset():
        save_win = tk.Toplevel(app, bg=BG)
        save_win.title("Save Preset")
        save_win.geometry("400x160")
        save_win.configure(bg=BG)
        save_win.resizable(False, False)

        tk.Label(save_win, text="Preset name:", bg=BG, fg=FG,
                 font=BODY_FONT).pack(anchor="w", padx=16, pady=(16, 4))

        name_entry = tk.Entry(save_win, bg=BG_ACTIVE, fg=FG, insertbackground=FG,
                               font=BODY_FONT, relief="flat",
                               highlightthickness=1,
                               highlightbackground=BG_SIDEBAR,
                               highlightcolor=ACCENT)
        name_entry.pack(fill="x", padx=16, pady=(0, 8), ipady=6)
        name_entry.focus()

        def save():
            name = name_entry.get().strip()
            if not name:
                return
            current = fflags.get_fflags()
            if not current:
                return
            d = {}
            if USER_PRESETS_FILE.exists():
                try:
                    d = json.loads(USER_PRESETS_FILE.read_text())
                except Exception:
                    pass
            d[name] = {"description": "", "flags": current}
            _save_user_presets(d)
            save_win.destroy()
            refresh_user()
            status.configure(text=f"Saved preset: {name}", fg=FG_DIM)

        name_entry.bind("<Return>", lambda e: save())
        app.make_button(save_win, "Save", command=save, padx=12, pady=6
                         ).pack(anchor="w", padx=16, pady=(0, 16))

    app.make_button(body, "Save Current as Preset", command=save_as_preset,
                     padx=12, pady=6
                     ).pack(anchor="w", padx=16, pady=(0, 16))

def _open_paste_json(app):
    win = tk.Toplevel(app, bg=BG)
    win.title("Paste FFlags JSON")
    win.geometry("600x820")
    win.configure(bg=BG)
    win.resizable(False, False)

    tk.Label(win, text="Paste FFlags JSON", bg=BG, fg=FG,
             font=("TkDefaultFont", 14, "bold"), anchor="w"
             ).pack(anchor="w", padx=16, pady=(16, 8))

    text = tk.Text(win, bg=BG_ACTIVE, fg=FG, insertbackground=FG,
                    font=BODY_FONT, relief="flat", wrap="word",
                    highlightthickness=1, highlightbackground=BG_SIDEBAR)
    text.pack(fill="both", expand=True, padx=16, pady=(0, 8))

    status = tk.Label(win, text="", bg=BG, fg=FG_DIM,
                       font=("TkDefaultFont", 10), anchor="w")
    status.pack(anchor="w", padx=16, pady=(0, 8))

    def apply_json():
        raw = text.get("1.0", "end").strip()
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            status.configure(text=f"Invalid JSON: {e}", fg=ERROR)
            return
        if not isinstance(parsed, dict):
            status.configure(text="JSON must be an object of flag: value pairs",
                             fg=ERROR)
            return
        current = fflags.get_fflags()
        current.update(parsed)
        fflags.save_fflags(current)
        app.reload_fflags_ui()
        win.destroy()

    btn_row = tk.Frame(win, bg=BG)
    btn_row.pack(anchor="w", padx=16, pady=(0, 16))
    app.make_button(btn_row, "Apply", command=apply_json).pack(side="left")

def build_fpsinput(app, parent, pad):
    tk.Label(parent, text="Framerate cap", bg=parent["bg"], fg=FG,
             font=BODY_FONT).pack(anchor="w", padx=pad, pady=(0, 2))

    vcmd = (app.register(fps.validate_digits), "%P")
    entry = tk.Entry(parent, bg=BG, fg=FG, insertbackground=FG,
                      font=BODY_FONT, relief="flat",
                      highlightthickness=1,
                      highlightbackground=BG_SIDEBAR,
                      highlightcolor=ACCENT,
                      validate="key", validatecommand=vcmd)
    current = fps.load_framerate_cap()
    if current:
        entry.insert(0, current)
    entry.pack(anchor="w", fill="x", padx=pad, pady=(0, 6), ipady=8)

    tk.Label(parent,
             text=("Only applies after you open Roblox, set in-game cap to "
                   "default (60), close Roblox, then set it here and "
                   "relaunch. and yes this is true, Roblox is probably gonna be patching this so don't be surprised when this doesn't work anymore"),
             bg=parent["bg"], fg=FG_DIM, font=("TkDefaultFont", 10),
             anchor="w", wraplength=500, justify="left"
             ).pack(anchor="w", padx=pad, pady=(0, 6))

    save_command = lambda: (fps.save_framerate_cap(entry.get().strip())
                             if entry.get().strip() else None)
    app.make_button(parent, "Save FPS Limit", command=save_command
                     ).pack(anchor="w", padx=pad, pady=(0, 14))

def build_fontpicker(app, parent, pad):
    tk.Label(parent, text="Font file (.ttf / .otf)", bg=parent["bg"],
             fg=FG, font=BODY_FONT).pack(anchor="w", padx=pad, pady=(0, 2))

    row = tk.Frame(parent, bg=parent["bg"])
    row.pack(anchor="w", fill="x", padx=pad, pady=(0, 6))

    path_entry = tk.Entry(row, bg=BG, fg=FG, insertbackground=FG,
                           font=BODY_FONT, relief="flat",
                           highlightthickness=1,
                           highlightbackground=BG_SIDEBAR,
                           highlightcolor=ACCENT)
    path_entry.pack(side="left", fill="x", expand=True, ipady=8,
                      padx=(0, 6))

    def browse():
        chosen = filedialog.askopenfilename(
            title="Choose a font file",
            filetypes=[("Font files", "*.ttf *.otf"), ("All files", "*.*")]
        )
        if chosen:
            path_entry.delete(0, "end")
            path_entry.insert(0, chosen)

    app.make_button(row, "Browse", command=browse, padx=14, pady=8
                     ).pack(side="left")

    status = tk.Label(parent, text="", bg=parent["bg"], fg=FG_DIM,
                       font=("TkDefaultFont", 10), anchor="w",
                       wraplength=500, justify="left")
    status.pack(anchor="w", padx=pad, pady=(0, 6))

    def apply_font():
        source = path_entry.get().strip()
        if not source:
            status.configure(text="Pick a font file first.", fg=ERROR)
            return
        try:
            replaced = fonts.apply_font(source)
            fonts.save_installed_font(source)
        except FileNotFoundError as e:
            status.configure(text=str(e), fg=ERROR)
            return
        if not replaced:
            status.configure(
                text="No font files found to replace yet",
                fg=ERROR)
            return
        status.configure(
            text=f"Replaced {len(replaced)} font file(s).", fg=FG_DIM)

    app.make_button(parent, "Apply Font", command=apply_font
                     ).pack(anchor="w", padx=pad, pady=(0, 6))

    def restore_default():
        removed = fonts.restore_fonts()
        if removed:
            status.configure(text="Default fonts restored.", fg=FG_DIM)
        else:
            status.configure(text="No custom font to restore.", fg=ERROR)

    app.make_button(parent, "Restore Default Fonts", command=restore_default,
                     bg=ERROR, fg="#0a0a0a"
                     ).pack(anchor="w", padx=pad, pady=(0, 6))

    tk.Label(parent,
             text=("NOTE: If Sober updates and removes your font, reopen Lution and we'll reapply it automatically"),
             bg=parent["bg"], fg=FG_DIM, font=("TkDefaultFont", 10),
             anchor="w", wraplength=500, justify="left"
             ).pack(anchor="w", padx=pad, pady=(0, 14))

def build_envvars(app, parent, pad):
    status = tk.Label(parent, text="", bg=parent["bg"], fg=FG_DIM,
                       font=("TkDefaultFont", 10), anchor="w",
                       wraplength=500, justify="left")
    status.pack(anchor="w", padx=pad, pady=(0, 6))

    list_frame = tk.Frame(parent, bg=parent["bg"])
    list_frame.pack(anchor="w", fill="x", padx=pad, pady=(0, 6))

    rows = []

    def add_row(key="", value=""):
        row = tk.Frame(list_frame, bg=parent["bg"])
        row.pack(anchor="w", fill="x", pady=3)

        key_entry = tk.Entry(row, bg=BG, fg=FG, insertbackground=FG,
                              font=BODY_FONT, relief="flat", width=22,
                              highlightthickness=1,
                              highlightbackground=BG_SIDEBAR,
                              highlightcolor=ACCENT)
        key_entry.insert(0, key)
        key_entry.pack(side="left", padx=(0, 6), ipady=6)

        eq_label = tk.Label(row, text="=", bg=parent["bg"], fg=FG_DIM,
                             font=BODY_FONT)
        eq_label.pack(side="left", padx=(0, 6))

        value_entry = tk.Entry(row, bg=BG, fg=FG, insertbackground=FG,
                                font=BODY_FONT, relief="flat",
                                highlightthickness=1,
                                highlightbackground=BG_SIDEBAR,
                                highlightcolor=ACCENT)
        value_entry.insert(0, value)
        value_entry.pack(side="left", fill="x", expand=True, ipady=6,
                          padx=(0, 6))

        def remove():
            row.destroy()
            for item in rows:
                if item[0] is key_entry:
                    rows.remove(item)
                    break

        app.make_button(row, "x", command=remove,
                         bg=BG_SIDEBAR, fg=FG_DIM, padx=10, pady=4
                         ).pack(side="left")

        rows.append((key_entry, value_entry))

    def open_add_var():
        win = tk.Toplevel(app, bg=BG)
        win.title("Add Environment Variable")
        win.geometry("500x300")
        win.configure(bg=BG)
        win.resizable(False, False)

        tk.Label(win, text="Variable name:", bg=BG, fg=FG,
                 font=BODY_FONT).pack(anchor="w", padx=16, pady=(16, 2))
        key_entry = tk.Entry(win, bg=BG_ACTIVE, fg=FG, insertbackground=FG,
                              font=BODY_FONT, width=40,
                              highlightthickness=1,
                              highlightbackground=BG_SIDEBAR,
                              highlightcolor=ACCENT)
        key_entry.pack(anchor="w", padx=16, ipady=6)
        key_entry.focus()

        tk.Label(win, text="Value:", bg=BG, fg=FG,
                 font=BODY_FONT).pack(anchor="w", padx=16, pady=(8, 2))
        val_entry = tk.Entry(win, bg=BG_ACTIVE, fg=FG, insertbackground=FG,
                              font=BODY_FONT, width=40,
                              highlightthickness=1,
                              highlightbackground=BG_SIDEBAR,
                              highlightcolor=ACCENT)
        val_entry.pack(anchor="w", padx=16, ipady=6)

        hint = tk.Label(win, text="", bg=BG, fg=ERROR,
                         font=("TkDefaultFont", 10), anchor="w")
        hint.pack(anchor="w", padx=16, pady=(6, 0))

        def do_add():
            key = key_entry.get().strip()
            if not envvars.valid_key(key):
                hint.configure(
                    text="Name can't be empty or contain spaces / '='.")
                return
            add_row(key, val_entry.get().strip())
            win.destroy()

        key_entry.bind("<Return>", lambda e: do_add())
        val_entry.bind("<Return>", lambda e: do_add())

        app.make_button(win, "Add", command=do_add, padx=12, pady=6
                         ).pack(anchor="w", padx=16, pady=(12, 16))

    btn_row = tk.Frame(parent, bg=parent["bg"])
    btn_row.pack(anchor="w", fill="x", padx=pad, pady=(0, 14))

    def save_vars_action():
        data = {}
        skipped = False
        for key_entry, value_entry in rows:
            key = key_entry.get().strip()
            if not envvars.valid_key(key):
                skipped = True
                continue
            data[key] = value_entry.get().strip()
        saved = envvars.save_vars(data)
        note = "Invalid names were skipped." if skipped else \
               "'Sober with Lution' shortcut is ready."
        status.configure(text=f"Saved {len(saved)} variable(s). {note}",
                          fg=ERROR if skipped else FG_DIM)

    for key, value in envvars.load_vars().items():
        add_row(str(key), str(value))

    app.make_button(btn_row, "Add Variable", command=open_add_var
                     ).pack(side="left", padx=(0, 6))
    app.make_button(btn_row, "Save Variables", command=save_vars_action
                     ).pack(side="left")

def build_cursorpicker(app, parent, pad):
    status = tk.Label(parent, text="", bg=parent["bg"], fg=FG_DIM,
                       font=("TkDefaultFont", 10), anchor="w",
                       wraplength=500, justify="left")
    status.pack(anchor="w", padx=pad, pady=(0, 6))

    preset_names = cursors.list_presets()
    cursor_entries = {}

    if preset_names:
        tk.Label(parent, text="Preset", bg=parent["bg"], fg=FG,
                 font=BODY_FONT).pack(anchor="w", padx=pad, pady=(6, 2))
        preset_combo = ttk.Combobox(parent, values=["Custom"] + preset_names,
                                     font=BODY_FONT, state="readonly")
        preset_combo.set("Custom")
        preset_combo.pack(anchor="w", padx=pad, pady=(0, 10), ipady=4)

        def on_preset_change(event=None):
            selection = preset_combo.get()
            if selection == "Custom":
                return
            preset_cursors = cursors.get_preset_cursors(selection)
            for name, entry in cursor_entries.items():
                entry.delete(0, "end")
                if name in preset_cursors:
                    entry.insert(0, preset_cursors[name])

        preset_combo.bind("<<ComboboxSelected>>", on_preset_change)

    for state_name in cursors.CURSOR_STATES:
        label_text = state_name + ".png"
        tk.Label(parent, text=label_text, bg=parent["bg"], fg=FG,
                 font=BODY_FONT).pack(anchor="w", padx=pad, pady=(6, 2))

        row = tk.Frame(parent, bg=parent["bg"])
        row.pack(anchor="w", fill="x", padx=pad, pady=(0, 6))

        entry = tk.Entry(row, bg=BG, fg=FG, insertbackground=FG,
                          font=BODY_FONT, relief="flat",
                          highlightthickness=1,
                          highlightbackground=BG_SIDEBAR,
                          highlightcolor=ACCENT)
        entry.pack(side="left", fill="x", expand=True, ipady=8,
                    padx=(0, 6))
        cursor_entries[state_name] = entry

        def browse_cursor(e=entry, s=state_name):
            chosen = filedialog.askopenfilename(
                title=f"Choose {s} cursor",
                filetypes=[("PNG images", "*.png"), ("All files", "*.*")]
            )
            if chosen:
                e.delete(0, "end")
                e.insert(0, chosen)
                if preset_combo.get() != "Custom":
                    preset_combo.set("Custom")

        app.make_button(row, "Browse", command=browse_cursor,
                          padx=14, pady=8).pack(side="left")

    def apply_cursors_action():
        cursors_dict = {}
        for name, entry in cursor_entries.items():
            path = entry.get().strip()
            if path:
                cursors_dict[name] = path
        if not cursors_dict:
            status.configure(text="Select at least one cursor file first.", fg=ERROR)
            return
        applied = cursors.apply_cursors(cursors_dict)
        cursors.save_installed_cursors(cursors_dict)
        status.configure(text=f"Applied {len(applied)} cursor file(s).", fg=FG_DIM)

    app.make_button(parent, "Apply Cursors", command=apply_cursors_action
                      ).pack(anchor="w", padx=pad, pady=(0, 6))

    def restore_default():
        removed = cursors.restore_cursors()
        if removed:
            status.configure(text="Default cursors restored.", fg=FG_DIM)
        else:
            status.configure(text="No custom cursors to restore.", fg=ERROR)

    app.make_button(parent, "Restore Default Cursors", command=restore_default,
                      bg=ERROR, fg="#0a0a0a"
                      ).pack(anchor="w", padx=pad, pady=(0, 14))

def build_themepicker(app, parent, pad):
    current = themes.load_theme()

    color_labels = {
        "accent": "Accent",
        "bg": "Background",
        "bg_sidebar": "Sidebar",
        "fg": "Text",
    }

    entries = {}
    for key in themes.COLOR_KEYS:
        label = color_labels[key]
        tk.Label(parent, text=label, bg=parent["bg"], fg=FG,
                 font=BODY_FONT).pack(anchor="w", padx=pad, pady=(6, 2))

        row = tk.Frame(parent, bg=parent["bg"])
        row.pack(anchor="w", fill="x", padx=pad, pady=(0, 6))

        entry = tk.Entry(row, bg=BG, fg=FG, insertbackground=FG,
                          font=BODY_FONT, relief="flat",
                          highlightthickness=1,
                          highlightbackground=BG_SIDEBAR,
                          highlightcolor=ACCENT)
        entry.insert(0, current[key])
        entry.pack(side="left", fill="x", expand=True, ipady=8,
                    padx=(0, 6))
        entries[key] = entry

        swatch = tk.Label(row, bg=current[key], width=3, height=1,
                           relief="flat", highlightthickness=1,
                           highlightbackground=BG_SIDEBAR)
        swatch.pack(side="left", padx=(0, 6))

        def update_swatch(event=None, ent=entry, s=swatch):
            val = ent.get().strip()
            if len(val) == 7 and val.startswith("#"):
                try:
                    int(val[1:], 16)
                    s.configure(bg=val)
                except ValueError:
                    pass

        entry.bind("<KeyRelease>", update_swatch)

    status = tk.Label(parent, text="", bg=parent["bg"], fg=FG_DIM,
                       font=("TkDefaultFont", 10), anchor="w",
                       wraplength=500, justify="left")
    status.pack(anchor="w", padx=pad, pady=(0, 6))

    def apply_theme():
        colors = {}
        for key in themes.COLOR_KEYS:
            val = entries[key].get().strip()
            if len(val) == 7 and val.startswith("#"):
                try:
                    int(val[1:], 16)
                    colors[key] = val
                except ValueError:
                    status.configure(text=f"Invalid hex color for {color_labels[key]}.", fg=ERROR)
                    return
            else:
                status.configure(text=f"Invalid hex color for {color_labels[key]}.", fg=ERROR)
                return
        themes.save_theme(colors)
        status.configure(text="Theme saved. Restart Lution to apply.", fg=FG_DIM)

    app.make_button(parent, "Save Theme", command=apply_theme
                     ).pack(anchor="w", padx=pad, pady=(0, 6))

    def restore_default():
        themes.save_theme(dict(themes.DEFAULTS))
        for key in themes.COLOR_KEYS:
            entries[key].delete(0, "end")
            entries[key].insert(0, themes.DEFAULTS[key])
        status.configure(text="Default theme restored. Restart Lution to apply.", fg=FG_DIM)

    app.make_button(parent, "Restore Default Theme", command=restore_default,
                     bg=ERROR, fg="#0a0a0a"
                     ).pack(anchor="w", padx=pad, pady=(0, 14))

def build_emojipicker(app, parent, pad):
    tk.Label(parent, text="Emoji font", bg=parent["bg"],
             fg=FG, font=BODY_FONT).pack(anchor="w", padx=pad, pady=(0, 2))

    preset_names = emoji.list_presets()
    selected_font = tk.StringVar()

    list_frame = tk.Frame(parent, bg=BG, highlightthickness=1,
                           highlightbackground=BG_SIDEBAR)
    list_frame.pack(anchor="w", fill="x", padx=pad, pady=(0, 6))

    canvas = tk.Canvas(list_frame, bg=BG, highlightthickness=0, height=200)
    scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
    inner = tk.Frame(canvas, bg=BG)

    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=inner, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def on_canvas_width(e):
        canvas.itemconfigure(canvas.find_all()[0], width=e.width)
    canvas.bind("<Configure>", on_canvas_width)

    font_buttons = []

    def select_font(name, path):
        selected_font.set(path)
        for btn, bname in font_buttons:
            if bname == name:
                btn.configure(bg=ACCENT, fg="#0a0a0a")
            else:
                btn.configure(bg=BG_ACTIVE, fg=FG)

    custom_row = tk.Frame(inner, bg=BG_ACTIVE, pady=6, padx=8)
    custom_row.pack(fill="x", padx=4, pady=2)

    tk.Label(custom_row, text="Custom file:", bg=BG_ACTIVE, fg=FG_DIM,
             font=("TkDefaultFont", 11)).pack(side="left", padx=(0, 6))

    custom_entry = tk.Entry(custom_row, bg=BG, fg=FG, insertbackground=FG,
                             font=("TkDefaultFont", 11), relief="flat",
                             highlightthickness=1,
                             highlightbackground=BG_SIDEBAR,
                             highlightcolor=ACCENT)
    custom_entry.pack(side="left", fill="x", expand=True, ipady=4, padx=(0, 6))

    def browse_custom(event=None):
        chosen = filedialog.askopenfilename(
            title="Choose an emoji font file",
            filetypes=[("Font files", "*.ttf"), ("All files", "*.*")]
        )
        if chosen:
            custom_entry.delete(0, "end")
            custom_entry.insert(0, chosen)
            select_font("", chosen)

    browse_btn = tk.Label(custom_row, text="Browse", bg=ACCENT, fg="#0a0a0a",
                           font=("TkDefaultFont", 11), cursor="hand2",
                           padx=8, pady=2)
    browse_btn.pack(side="left")
    browse_btn.bind("<Button-1>", browse_custom)

    for name in preset_names:
        font_path = emoji.get_preset_path(name)
        if not font_path:
            continue

        row = tk.Frame(inner, bg=BG_ACTIVE, pady=6, padx=8)
        row.pack(fill="x", padx=4, pady=2)

        btn = tk.Label(row, text=name, bg=BG_ACTIVE, fg=FG,
                        font=("TkDefaultFont", 12), cursor="hand2",
                        anchor="w")
        btn.pack(side="left", fill="x", expand=True)

        font_buttons.append((btn, name))
        btn.bind("<Button-1>", lambda e, n=name, p=font_path: select_font(n, p))
        row.bind("<Button-1>", lambda e, n=name, p=font_path: select_font(n, p))

    status = tk.Label(parent, text="", bg=parent["bg"], fg=FG_DIM,
                       font=("TkDefaultFont", 10), anchor="w",
                       wraplength=500, justify="left")
    status.pack(anchor="w", padx=pad, pady=(0, 6))

    def apply_emoji_font():
        path = selected_font.get()
        if not path:
            path = custom_entry.get().strip()
        if not path:
            status.configure(text="Select or browse for an emoji font first.", fg=ERROR)
            return
        try:
            replaced = emoji.apply_emoji(path)
        except FileNotFoundError as e:
            status.configure(text=str(e), fg=ERROR)
            return
        if not replaced:
            status.configure(text="No emoji font files found to replace.", fg=ERROR)
            return
        emoji.save_installed_emoji(path)
        status.configure(text=f"Replaced {len(replaced)} emoji file(s).", fg=FG_DIM)

    app.make_button(parent, "Apply Emoji Font", command=apply_emoji_font
                     ).pack(anchor="w", padx=pad, pady=(0, 6))

    def restore_default():
        removed = emoji.restore_emoji()
        if removed:
            status.configure(text="Default emoji fonts restored.", fg=FG_DIM)
        else:
            status.configure(text="No custom emoji font to restore.", fg=ERROR)

    app.make_button(parent, "Restore Default Emoji", command=restore_default,
                     bg=ERROR, fg="#0a0a0a"
                     ).pack(anchor="w", padx=pad, pady=(0, 6))

    tk.Label(parent,
             text=("NOTE: If Sober updates and removes your emoji font, reopen Lution and we'll reapply it automatically"),
             bg=parent["bg"], fg=FG_DIM, font=("TkDefaultFont", 10),
             anchor="w", wraplength=500, justify="left"
             ).pack(anchor="w", padx=pad, pady=(0, 14))

def build_modmanager(app, parent, pad):
    mods.ensure_dirs()

    list_frame = tk.Frame(parent, bg=parent["bg"])
    list_frame.pack(anchor="w", fill="x", padx=pad, pady=(0, 6))

    btn_row = tk.Frame(parent, bg=parent["bg"])
    btn_row.pack(anchor="w", fill="x", padx=pad, pady=(0, 6))

    status = tk.Label(parent, text="", bg=parent["bg"], fg=FG_DIM,
                       font=("TkDefaultFont", 10), anchor="w",
                       wraplength=500, justify="left")
    status.pack(anchor="w", padx=pad, pady=(0, 6))

    mod_listbox = tk.Listbox(list_frame, bg=BG, fg=FG,
                               selectbackground=ACCENT, selectforeground="#0a0a0a",
                               font=BODY_FONT, relief="flat", height=8,
                               highlightthickness=1,
                               highlightbackground=BG_SIDEBAR,
                               highlightcolor=ACCENT)
    mod_listbox.pack(fill="x", ipady=4)

    def refresh_list():
        mod_listbox.delete(0, tk.END)
        for mod in mods.list_mods():
            mod_listbox.insert(tk.END, mod.stem)

    def import_mod():
        chosen = filedialog.askopenfilename(
            title="Select Mod Archive",
            filetypes=[("ZIP Archives", "*.zip"), ("All Files", "*.*")]
        )
        if chosen:
            try:
                dest = mods.import_mod(chosen)
                status.configure(text=f"Imported: {dest.name}. Click install to make it work in Sober", fg=FG_DIM)
                refresh_list()
            except Exception as e:
                status.configure(text=str(e), fg=ERROR)

    def install_selected():
        sel = mod_listbox.curselection()
        if not sel:
            status.configure(text="Select a mod first by clicking on the mod's name or import one", fg=ERROR)
            return
        name = mod_listbox.get(sel[0])
        mod_path = mods.MODS_DIR / f"{name}.zip"
        conflicts = mods.check_mod_conflicts(mod_path)
        if conflicts:
            status.configure(
                text=f"Warning: {len(conflicts)} file(s) will be overwritten. Install anyway to proceed.",
                fg="#e0c252")
        ok, msg = mods.install_mod(mod_path)
        status.configure(text=msg, fg=FG_DIM if ok else ERROR)

    def remove_selected():
        sel = mod_listbox.curselection()
        if not sel:
            status.configure(text="Select a mod first by clicking on it (THIS WON'T REMOVE THE MOD DIRECTLY FROM SOBER, CLICK Delete all mods TO DO SO.)", fg=ERROR)
            return
        name = mod_listbox.get(sel[0])
        mod_path = mods.MODS_DIR / f"{name}.zip"
        mods.delete_mod(mod_path)
        status.configure(text=f"Deleted: {name} from mod manager. click delete all mods to fully remove the mod.", fg=FG_DIM)
        refresh_list()

    def cleanup_all():
        win = tk.Toplevel(app, bg=BG)
        win.title("Delete All Mods")
        win.geometry("440x220")
        win.configure(bg=BG)
        win.resizable(False, False)

        tk.Label(win, text="Delete all mod content from Sober?",
                 bg=BG, fg=FG, font=BODY_FONT,
                 anchor="w").pack(anchor="w", padx=16, pady=(16, 8))

        tk.Label(win, text="This removes mod files from the overlay.\nYour custom cursors, fonts, and emoji fonts will be kept.",
                 bg=BG, fg=FG_DIM, font=("TkDefaultFont", 10),
                 anchor="w", justify="left", wraplength=380).pack(anchor="w", padx=16, pady=(0, 10))

        also_var = tk.BooleanVar(value=False)
        cb = tk.Checkbutton(win, text="Also delete cursors, fonts, and emoji fonts",
                             variable=also_var, bg=BG, fg=FG,
                             font=("TkDefaultFont", 10),
                             selectcolor=BG_ACTIVE, activebackground=BG,
                             activeforeground=FG)
        cb.pack(anchor="w", padx=16, pady=(0, 10))

        btn_row = tk.Frame(win, bg=BG)
        btn_row.pack(anchor="w", padx=16, pady=(0, 16))

        def confirm():
            include = also_var.get()
            removed = mods.remove_mod_content(include_custom=include)
            if removed:
                status.configure(
                    text=f"Removed: {', '.join(removed)} from overlay.", fg=FG_DIM)
            else:
                status.configure(text="Nothing to clean up vro", fg=FG_DIM)
            win.destroy()

        app.make_button(btn_row, "Delete", command=confirm,
                          bg=ERROR, fg="#0a0a0a", padx=12, pady=6
                          ).pack(side="left", padx=(0, 8))
        app.make_button(btn_row, "Cancel", command=win.destroy,
                          padx=12, pady=6).pack(side="left")

    app.make_button(btn_row, "Import Mod", command=import_mod
                     ).pack(side="left", padx=(0, 6))
    app.make_button(btn_row, "Install mod", command=install_selected
                     ).pack(side="left", padx=(0, 6))
    app.make_button(btn_row, "Delete mod", command=remove_selected,
                     bg=ERROR, fg="#0a0a0a"
                     ).pack(side="left", padx=(0, 6))
    app.make_button(btn_row, "Delete all mods from Sober", command=cleanup_all,
                     bg=BG_SIDEBAR, fg=FG_DIM
                     ).pack(side="left")

    def on_page_shown(page_name):
        if page_name == "Mods":
            refresh_list()

    try:
        app.page_shown_listeners.append(on_page_shown)
    except AttributeError:
        pass

    refresh_list()

    def open_guide():
        win = tk.Toplevel(app, bg=BG)
        win.title("How mods work")
        win.geometry("560x460")
        win.configure(bg=BG)
        win.resizable(False, False)

        guide_frame = tk.Frame(win, bg=BG_SIDEBAR, highlightthickness=1,
                                highlightbackground=BG_SIDEBAR)
        guide_frame.pack(fill="both", expand=True, padx=16, pady=(16, 10))

        guide_box = tk.Text(guide_frame, bg=BG_ACTIVE, fg=FG,
                         font=("TkDefaultFont", 11), relief="flat",
                         highlightthickness=0, wrap="word",
                         padx=10, pady=10,
                         width=64, height=20)
        scroll = tk.Scrollbar(guide_frame, orient="vertical",
                               command=guide_box.yview,
                               bg=BG_SIDEBAR, troughcolor=BG_SIDEBAR,
                               activebackground=FG_DIM, width=10)
        guide_box.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        guide_box.pack(side="left", fill="both", expand=True)

        guide_text = (
            "## HOW MODS WORK\n"
            "\n"
            "when importing a mod, you need to select a .zip file "
            "containing any of these folders:\n"
            "  * content\n"
            "  * ExtraContent\n"
            "  * PlatformContent\n"
            "\n"
            "when installing a mod, you have to first select a mod in "
            "the mods list and then click install mod, which will be "
            "installed to sober\n"
            "\n"
            "when deleting a mod, you have to select a mod in the list "
            "and then click delete mod\n"
            "NOTE: it will only remove it from lution, NOT sober. "
            "click 'delete all mods from sober' to do so\n"
            "\n"
            "## CONFLICTS\n"
            "\n"
            "two mods clash when they change the SAME file. whoever you "
            "install LAST wins that file.\n"
            "\n"
            "example: mod 1 changes your cursor AND font, mod 2 only "
            "changes your cursor.\n"
            "install mod 1 first, then mod 2.\n"
            "now you have mod 2's cursor (it overwrote mod 1's) and "
            "mod 1's font (mod 2 doesn't touch fonts).\n"
            "\n"
            "in short: the mod you install LAST gets priority on any "
            "shared files.\n"
        )
        guide_box.insert("1.0", guide_text)
        guide_box.configure(state="disabled")

        app.make_button(win, "Close", command=win.destroy,
                         padx=14, pady=6).pack(side="right", padx=16,
                                                pady=(0, 14))

    app.make_button(parent, "What the fuck do I do?", command=open_guide,
                     bg=BG_SIDEBAR, fg=FG_DIM, padx=14, pady=8
                     ).pack(anchor="w", padx=pad, pady=(0, 14))

def build_modconflicts(app, parent, pad):
    conflict_list = tk.Frame(parent, bg=parent["bg"])
    conflict_list.pack(anchor="w", fill="x", padx=pad, pady=(0, 6))

    status = tk.Label(parent, text="", bg=parent["bg"], fg=FG_DIM,
                       font=("TkDefaultFont", 10), anchor="w",
                       wraplength=500, justify="left")
    status.pack(anchor="w", padx=pad, pady=(0, 6))

    def scan():
        for w in conflict_list.winfo_children():
            w.destroy()

        conflicts = mods.scan_all_conflicts()

        if not conflicts:
            tk.Label(conflict_list, text="No conflicts found",
                     bg=parent["bg"], fg=FG_DIM,
                     font=("TkDefaultFont", 10)).pack(anchor="w")
            status.configure(text="", fg=FG_DIM)
            return

        total = sum(len(v) for v in conflicts.values())
        status.configure(
            text=f"{len(conflicts)} conflict(s) found ({total} file(s) overlapping)",
            fg=ERROR)

        for (a, b), files in conflicts.items():
            pair = tk.Frame(conflict_list, bg=BG_ACTIVE, highlightthickness=1,
                             highlightbackground=ERROR)
            pair.pack(anchor="w", fill="x", pady=(0, 6))

            tk.Label(pair, text=f"{a}  <->  {b}",
                     bg=BG_ACTIVE, fg=ERROR,
                     font=("TkDefaultFont", 11, "bold"),
                     anchor="w").pack(anchor="w", padx=8, pady=(6, 2))

            for f in files[:10]:
                tk.Label(pair, text=f"  {f}",
                         bg=BG_ACTIVE, fg=FG_DIM,
                         font=("TkDefaultFont", 9),
                         anchor="w").pack(anchor="w", padx=8)
            if len(files) > 10:
                tk.Label(pair, text=f"  ... and {len(files) - 10} more",
                         bg=BG_ACTIVE, fg=FG_DIM,
                         font=("TkDefaultFont", 9),
                         anchor="w").pack(anchor="w", padx=8, pady=(0, 4))

    app.make_button(parent, "Scan for Conflicts", command=scan
                     ).pack(anchor="w", padx=pad, pady=(0, 14))

def build_soundmods(app, parent, pad):
    status = tk.Label(parent, text="", bg=parent["bg"], fg=FG_DIM,
                       font=("TkDefaultFont", 10), anchor="w",
                       wraplength=500, justify="left")
    status.pack(anchor="w", padx=pad, pady=(0, 6))

    sound_entries = {}

    for file_name in sound_mods.SOUND_STATES:
        tk.Label(parent, text=file_name, bg=parent["bg"],
                 fg=FG, font=BODY_FONT).pack(anchor="w", padx=pad,
                                              pady=(6, 2))

        row = tk.Frame(parent, bg=parent["bg"])
        row.pack(anchor="w", fill="x", padx=pad, pady=(0, 6))

        entry = tk.Entry(row, bg=BG, fg=FG, insertbackground=FG,
                          font=BODY_FONT, relief="flat",
                          highlightthickness=1,
                          highlightbackground=BG_SIDEBAR,
                          highlightcolor=ACCENT)
        entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 6))
        sound_entries[file_name] = entry

        def browse_sound(e=entry):
            chosen = filedialog.askopenfilename(
                title="Choose a sound file",
                filetypes=[("Audio files", "*.ogg *.mp3 *.wav *.flac"),
                           ("All files", "*.*")]
            )
            if chosen:
                e.delete(0, "end")
                e.insert(0, chosen)

        app.make_button(row, "Browse", command=browse_sound,
                          padx=14, pady=8).pack(side="left")

    def apply_sounds_action():
        sounds_dict = {}
        for name, entry in sound_entries.items():
            path = entry.get().strip()
            if path:
                sounds_dict[name] = path
        if not sounds_dict:
            status.configure(text="Pick at least one sound file first.", fg=ERROR)
            return
        applied = sound_mods.apply_sounds(sounds_dict)
        sound_mods.save_installed_sounds(sounds_dict)
        status.configure(text=f"Applied {len(applied)} sound file(s).",
                         fg=FG_DIM)

    app.make_button(parent, "Apply Sounds", command=apply_sounds_action
                      ).pack(anchor="w", padx=pad, pady=(0, 6))

    def restore_default():
        removed = sound_mods.restore_sounds()
        if removed:
            status.configure(text="Default sounds restored.", fg=FG_DIM)
        else:
            status.configure(text="No custom sounds to restore.", fg=ERROR)

    app.make_button(parent, "Restore Default Sounds", command=restore_default,
                      bg=ERROR, fg="#0a0a0a"
                      ).pack(anchor="w", padx=pad, pady=(0, 14))

def build_playhistory(app, parent, pad):
    import threading

    import history
    import log

    status = tk.Label(parent, text="", bg=parent["bg"], fg=FG_DIM,
                       font=("TkDefaultFont", 10), anchor="w",
                       wraplength=500, justify="left")
    status.pack(anchor="w", padx=pad, pady=(0, 6))

    list_frame = tk.Frame(parent, bg=parent["bg"])
    list_frame.pack(anchor="w", fill="x", padx=pad, pady=(0, 6))

    def render(entries, names):
        for w in list_frame.winfo_children():
            w.destroy()

        if not entries:
            tk.Label(list_frame,
                     text="No games played yet. Play something and it'll show up here.",
                     bg=parent["bg"], fg=FG_DIM,
                     font=("TkDefaultFont", 10)).pack(anchor="w", padx=4,
                                                       pady=8)
            return

        for place_id, ts in entries:
            row = tk.Frame(list_frame, bg=parent["bg"])
            row.pack(anchor="w", fill="x", pady=2)

            name_text = names.get(place_id, f"Place {place_id}")
            name_lbl = tk.Label(row, text=name_text,
                                 bg=BG_ACTIVE, fg=FG,
                                 font=("TkDefaultFont", 11, "bold"),
                                 anchor="w", padx=12)
            name_lbl.pack(side="left", fill="x", expand=True, ipady=6)

            time_lbl = tk.Label(row, text=history.rel_time(ts),
                                 bg=BG_ACTIVE, fg=FG_DIM,
                                 font=("TkDefaultFont", 10), padx=10)
            time_lbl.pack(side="right")

            def play(p=place_id, n=name_text):
                log.info(f"Play History: launching place {p} via bootstrapper")
                bootstrapper.open_in(app,
                                      url=f"roblox://experiences/start?placeId={p}")

            app.make_button(row, "Play", command=play,
                              padx=16, pady=7).pack(side="right",
                                                     padx=(0, 10))

    def refresh():
        entries = history.get_history()
        ids = [pid for pid, _ts in entries]

        render(entries, history.load_name_cache())

        def worker():
            ev = getattr(app, "mainloop_started", None)
            if ev is not None:
                ev.wait(timeout=10)
            names = history.resolve_names(ids)
            app.after(0, lambda: render(entries, names))

        threading.Thread(target=worker, daemon=True).start()

    def on_page_shown(page_name):
        if page_name == "Home":
            refresh()

    try:
        app.page_shown_listeners.append(on_page_shown)
    except AttributeError:
        pass

    refresh()

def _fit_icon(img, target=128):
    
    def steps(src):
        if src == target:
            return (1, 1)
        best_z, best_s, best_err = 1, 1, abs(src - target)
        for s in range(1, 33):
            for z in range(1, 33):
                err = abs(round(src * z / s) - target)
                if err < best_err:
                    best_err, best_z, best_s = err, z, s
                    if err == 0:
                        break
            if best_err == 0:
                break
        return best_z, best_s

    if img.width() == target and img.height() == target:
        return img
    zx, sx = steps(img.width())
    zy, sy = steps(img.height())
    if (zx, sx) != (1, 1):
        img = img.zoom(zx, zy)
    if (sx, sy) != (1, 1):
        img = img.subsample(sx, sy)
    return img

def build_marketplace(app, parent, pad):
    import threading

    import marketplace as mkt
    import mods as mods_mod
    import log

    base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    placeholder_file = base_dir / "placeholder.png"

    status = tk.Label(parent, text="", bg=parent["bg"], fg=FG_DIM,
                       font=("TkDefaultFont", 10), anchor="w",
                       wraplength=500, justify="left")
    status.pack(anchor="w", padx=pad, pady=(0, 6))

    progress_area = tk.Frame(parent, bg=parent["bg"])
    progress_label = tk.Label(progress_area, text="", bg=parent["bg"],
                               fg=FG_DIM, font=("TkDefaultFont", 10))
    progress_bar = ttk.Progressbar(progress_area, orient="horizontal",
                                    length=420, maximum=1.0)
    progress_bar.pack(side="left")
    progress_label.pack(side="left", padx=(8, 0))

    def show_progress():
        progress_bar.configure(value=0.0)
        progress_label.configure(text="Downloading...")
        progress_area.pack(anchor="w", fill="x", padx=pad, pady=(0, 8))

    def hide_progress():
        progress_area.pack_forget()

    list_frame = tk.Frame(parent, bg=parent["bg"])
    list_frame.pack(anchor="w", fill="x", padx=pad, pady=(0, 6))
    icon_refs = []

    def _show_installed_info(itype, name):
        win = tk.Toplevel(app, bg=BG)
        win.title("Installed")
        win.configure(bg=BG)
        win.resizable(False, False)

        tk.Label(win, text=f"'{name}' installed.",
                 bg=BG, fg=FG, font=BODY_FONT,
                 anchor="w").pack(anchor="w", padx=16, pady=(16, 6))

        if itype == "mod":
            msg = "You can apply this mod in the Mods section."
        else:
            msg = ("You can apply this FFlag by going to the FastFlags "
                   "section, then Presets, and clicking the preset you "
                   "installed.")
        tk.Label(win, text=msg, bg=BG, fg=FG_DIM,
                 font=("TkDefaultFont", 10), anchor="w", justify="left",
                 wraplength=430).pack(anchor="w", padx=16, pady=(0, 12))

        sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
        win.geometry(f"480x170+{(sw - 480) // 2}+{(sh - 170) // 2 - 100}")
        app.make_button(win, "OK", command=win.destroy,
                         padx=14, pady=6).pack(anchor="e", padx=16,
                                                pady=(0, 14))

    def set_status(text, error=False):
        app.after(0, lambda: status.configure(
            text=text, fg=ERROR if error else FG_DIM))

    def render(items, icons):
        for w in list_frame.winfo_children():
            w.destroy()
        icon_refs.clear()

        placeholder_img = None
        if placeholder_file.exists():
            try:
                placeholder_img = _fit_icon(
                    tk.PhotoImage(file=str(placeholder_file)))
                icon_refs.append(placeholder_img)
            except Exception as e:
                log.warning(f"placeholder.png load failed: {e}")
                placeholder_img = None

        if not items:
            tk.Label(list_frame,
                     text="Store unreachable and no cached copy available.",
                     bg=parent["bg"], fg=FG_DIM,
                     font=("TkDefaultFont", 10)).pack(anchor="w", pady=8)
            return

        for item in items:
            row = tk.Frame(list_frame, bg=BG_ACTIVE,
                            highlightthickness=1,
                            highlightbackground=BG_SIDEBAR)
            row.pack(anchor="w", fill="x", pady=2)

            icon_path = icons.get(item.get("name"))
            if icon_path:
                try:
                    img = _fit_icon(tk.PhotoImage(file=str(icon_path)))
                    icon_refs.append(img)
                    tk.Label(row, image=img, bg=BG_ACTIVE
                             ).pack(side="left", padx=(8, 6), pady=4)
                except Exception as e:
                    log.warning(f"Store icon load failed: {e}")
                    icon_path = None
            if not icon_path:
                if placeholder_img is not None:
                    icon_refs.append(placeholder_img)
                    tk.Label(row, image=placeholder_img, bg=BG_ACTIVE
                             ).pack(side="left", padx=(8, 6), pady=4)
                else:
                    badge = "FF" if item.get("type") == "fflags" else "MOD"
                    tk.Label(row, text=badge, bg=BG_SIDEBAR, fg=FG_DIM,
                             font=("TkDefaultFont", 11, "bold"),
                             width=7).pack(side="left", padx=(8, 6),
                                            pady=16, fill="y")

            info = tk.Frame(row, bg=BG_ACTIVE)
            info.pack(side="left", fill="x", expand=True, padx=6, pady=6)

            tk.Label(info, text=item.get("name", "?"), bg=BG_ACTIVE, fg=FG,
                     font=("TkDefaultFont", 13, "bold"),
                     anchor="w").pack(anchor="w")

            desc_bits = []
            if item.get("description"):
                desc_bits.append(item["description"])
            if item.get("author"):
                desc_bits.append(f"by {item['author']}")
            tk.Label(info, text="  ·  ".join(desc_bits), bg=BG_ACTIVE,
                      fg=FG_DIM, font=("TkDefaultFont", 10),
                      anchor="w").pack(anchor="w")

            def do_install(item=item):
                itype = item.get("type")
                try:
                    if itype == "mod":
                        app.after(0, show_progress)

                        def report(frac, label):
                            def update():
                                if frac is None:
                                    progress_bar.configure(mode="indeterminate")
                                    progress_bar.start(10)
                                else:
                                    progress_bar.stop()
                                    progress_bar.configure(
                                        mode="determinate", value=frac)
                                progress_label.configure(text=label)
                            app.after(0, update)

                        data = mkt.download_progress(item["url"], report)

                        mdir = mods_mod.MODS_DIR
                        mdir.mkdir(parents=True, exist_ok=True)
                        safe_name = item.get("name", "mod").replace(
                            " ", "_") + ".zip"
                        zip_path = mdir / safe_name
                        zip_path.write_bytes(data)
                        ok, msg = mods_mod.install_mod(zip_path)
                        if not ok:
                            app.after(0, hide_progress)
                            set_status(msg, error=True)
                            return
                    else:
                        data = mkt.download(item["url"])
                        parsed = json.loads(data)
                        if isinstance(parsed, dict) \
                                and isinstance(parsed.get("flags"), dict):
                            flags = parsed["flags"]
                            desc = parsed.get("description", "")
                        elif isinstance(parsed, dict):
                            flags = parsed
                            desc = ""
                        else:
                            raise ValueError("not a valid FFlags JSON")
                        presets = {}
                        if USER_PRESETS_FILE.exists():
                            try:
                                presets = json.loads(
                                    USER_PRESETS_FILE.read_text())
                            except Exception:
                                presets = {}
                        key = item.get("name", "?")
                        presets[key] = {
                            "description": desc or item.get("description", ""),
                            "flags": flags}
                        _save_user_presets(presets)

                    if itype == "mod":
                        app.after(0, hide_progress)

                    item_name = item.get("name", "?")
                    mkt.mark_installed(item_name)
                    log.info(f"Marketplace: installed '{item_name}' ({itype})")
                    app.after(0, lambda: set_status(
                        f"Installed: {item_name}"))
                    app.after(0, lambda: _show_installed_info(itype,
                                                              item_name))
                    app.after(0, lambda: refresh_list())
                except Exception as e:
                    app.after(0, hide_progress)
                    log.error(f"Marketplace install failed: {e}")
                    set_status(f"Install failed: {e}", error=True)

            def on_click(_e=None, do=do_install):
                threading.Thread(target=lambda: _safe_install(do),
                                  daemon=True).start()

            def _safe_install(fn):
                try:
                    fn()
                except Exception as e:
                    set_status(f"Install failed: {e}", error=True)

            btn = app.make_button(row, "Install", command=on_click,
                                   bg=ACCENT, fg="#0a0a0a",
                                   padx=14, pady=7)
            btn.pack(side="right", padx=10)

    def refresh_list():
        def worker():
            ev = getattr(app, "mainloop_started", None)
            if ev is not None:
                ev.wait(timeout=10)
            items = mkt.fetch_store()
            icons = {}
            for item in items:
                if item.get("type") == "mod" and item.get("icon"):
                    path = mkt.fetch_icon(item.get("name", ""),
                                           item["icon"])
                    if path:
                        icons[item["name"]] = str(path)
            app.after(0, lambda: render(items, icons))
        threading.Thread(target=worker, daemon=True).start()

    def on_page_shown(page_name):
        if page_name == "Marketplace":
            refresh_list()

    try:
        app.page_shown_listeners.append(on_page_shown)
    except AttributeError:
        pass

    btn_row = tk.Frame(parent, bg=parent["bg"])
    btn_row.pack(anchor="w", fill="x", padx=pad, pady=(0, 14))
    app.make_button(btn_row, "Refresh Store", command=refresh_list,
                      padx=12, pady=6).pack(side="left")

    refresh_list()

def build_versionlabel(app, parent, pad):
    tk.Label(parent, text=f"Lution v{updater.VERSION}",
             bg=parent["bg"], fg=ACCENT,
             font=("TkDefaultFont", 16, "bold"),
             anchor="w").pack(anchor="w", padx=pad, pady=(0, 4))

    status = tk.Label(parent, text="Checking for updates...",
                       bg=parent["bg"], fg=FG_DIM,
                       font=("TkDefaultFont", 10), anchor="w")
    status.pack(anchor="w", padx=pad, pady=(0, 6))

    def check():
        outdated, latest, url = updater.check_for_update()
        if outdated:
            status.configure(text=f"Update available: v{latest}", fg=ACCENT)
            def open_url():
                webbrowser.open(url)
            app.make_button(parent, "Download Update", command=open_url,
                              padx=14, pady=6).pack(anchor="w", padx=pad, pady=(0, 6))
        else:
            status.configure(text="Up to date", fg=FG_DIM)

    app.after(100, check)

def build_soberversion(app, parent, pad):
    version = "Unknown"
    try:
        result = subprocess.run(
            ["flatpak", "info", "org.vinegarhq.Sober"],
            capture_output=True, text=True, timeout=5
        )
        for line in result.stdout.splitlines():
            if line.strip().startswith("Version:"):
                version = line.split(":", 1)[1].strip()
                break
    except Exception:
        pass
    tk.Label(parent, text=f"Sober version: {version}",
             bg=parent["bg"], fg=FG_DIM,
             font=("TkDefaultFont", 11), anchor="w"
             ).pack(anchor="w", padx=pad, pady=(0, 6))

def build_soberlauncher(app, parent, pad):
    import log

    def run():
        log.info("Launch Sober clicked")
        bootstrapper.open_in(app)

    app.make_button(parent, "Launch Sober", command=run
                     ).pack(anchor="w", padx=pad, pady=(4, 4))

def build_sobersettings(app, parent, pad):
    import log

    def open_settings():
        log.info("Opening Sober settings")
        subprocess.Popen(["flatpak", "run", "org.vinegarhq.Sober", "config"])

    app.make_button(parent, "Open Sober Settings", command=open_settings
                     ).pack(anchor="w", padx=pad, pady=(4, 4))

def build_bootstrapper(app, parent, pad):
    cfg = bootstrapper.get_config()

    status = tk.Label(parent, text="", bg=parent["bg"], fg=FG_DIM,
                       font=("TkDefaultFont", 10), anchor="w",
                       wraplength=500, justify="left")
    status.pack(anchor="w", padx=pad, pady=(0, 6))

    form = tk.Frame(parent, bg=parent["bg"])
    form.pack(anchor="w", fill="x", padx=pad, pady=(0, 6))
    form.columnconfigure(1, weight=1)

    row = [0]
    def add_field(label):
        r = row[0]; row[0] += 1
        tk.Label(form, text=label, bg=parent["bg"], fg=FG,
                 font=BODY_FONT).grid(row=r, column=0, sticky="w",
                                       padx=(0, 10), pady=3)
        holder = tk.Frame(form, bg=parent["bg"])
        holder.grid(row=r, column=1, sticky="ew", pady=2)
        return holder

    def add_combo(holder, values, initial):
        var = tk.StringVar(value=initial)
        ttk.Combobox(holder, values=values, textvariable=var,
                      font=("TkDefaultFont", 11), state="readonly",
                      width=12).pack(side="left")
        return var

    def add_spin(holder, frm, to, initial):
        var = tk.IntVar(value=int(initial))
        tk.Spinbox(holder, from_=frm, to=to, textvariable=var, width=6,
                    font=("TkDefaultFont", 11), bg=BG, fg=FG,
                    buttonbackground=BG_SIDEBAR,
                    insertbackground=FG, relief="flat").pack(side="left")
        return var

    def add_color(holder, initial):
        var = tk.StringVar(value=initial)
        e = tk.Entry(holder, bg=BG, fg=FG, insertbackground=FG, width=10,
                      font=("TkDefaultFont", 11), relief="flat",
                      highlightthickness=1,
                      highlightbackground=BG_SIDEBAR,
                      highlightcolor=ACCENT, textvariable=var)
        e.pack(side="left", ipady=4, padx=(0, 8))

        swatch = tk.Label(holder, bg=initial, width=3)
        swatch.pack(side="left")

        def sync(*_):
            val = var.get().strip()
            if len(val) == 7 and val.startswith("#"):
                try:
                    int(val[1:], 16)
                    swatch.configure(bg=val)
                    return
                except ValueError:
                    pass
            swatch.configure(bg=BG_SIDEBAR)
        var.trace_add("write", sync)
        return var

    def browse_image(var):
        chosen = filedialog.askopenfilename(
            title="Choose an image",
            filetypes=[("Images", "*.png *.gif *.jpg *.jpeg *.bmp"),
                       ("All files", "*.*")])
        if chosen:
            var.set(chosen)

    h = add_field("Theme")
    theme_var = add_combo(h, ["dark", "light"], cfg.get("theme", "dark"))

    def on_theme(*_):
        base = bootstrapper.apply_theme_defaults(theme_var.get())
        for var, key in ((bg_type_var, "bg_type"), (bg_color_var, "bg_color"),
                          (text_color_var, "text_color"), (bar_color_var, "bar_color"),
                          (bar_track_var, "bar_track_color")):
            var.set(str(base[key]))
    theme_var.trace_add("write", on_theme)

    h = add_field("Background")
    bg_type_var = add_combo(h, ["color", "image"], cfg.get("bg_type", "color"))
    bg_color_var = add_color(h, cfg.get("bg_color", "#232527"))

    h = add_field("BG Image")
    bg_image_var = tk.StringVar(value=cfg.get("bg_image", ""))
    tk.Entry(h, bg=BG, fg=FG, insertbackground=FG, width=32,
              font=("TkDefaultFont", 11), relief="flat",
              highlightthickness=1, highlightbackground=BG_SIDEBAR,
              highlightcolor=ACCENT,
              textvariable=bg_image_var).pack(side="left", fill="x",
                                               expand=True, ipady=4,
                                               padx=(0, 6))
    app.make_button(h, "Browse", command=lambda: browse_image(bg_image_var),
                     padx=10, pady=5).pack(side="left", padx=(0, 6))
    app.make_button(h, "Clear", command=lambda: bg_image_var.set(""),
                     padx=10, pady=5, bg=BG_SIDEBAR, fg=FG_DIM
                     ).pack(side="left")

    h = add_field("Logo Image")
    logo_var = tk.StringVar(value=cfg.get("logo_path", ""))
    tk.Entry(h, bg=BG, fg=FG, insertbackground=FG, width=32,
              font=("TkDefaultFont", 11), relief="flat",
              highlightthickness=1, highlightbackground=BG_SIDEBAR,
              highlightcolor=ACCENT,
              textvariable=logo_var).pack(side="left", fill="x",
                                           expand=True, ipady=4,
                                           padx=(0, 6))
    app.make_button(h, "Browse", command=lambda: browse_image(logo_var),
                     padx=10, pady=5).pack(side="left", padx=(0, 6))
    app.make_button(h, "Default", command=lambda: logo_var.set(""),
                     padx=10, pady=5, bg=BG_SIDEBAR, fg=FG_DIM
                     ).pack(side="left")

    h = add_field("Logo Size")
    logo_size_var = add_spin(h, 48, 420, cfg.get("logo_size", 200))
    h = add_field("Logo Align")
    logo_align_var = add_combo(h, ["left", "center", "right"],
                                cfg.get("logo_align", "center"))
    h = add_field("Logo Position")
    logo_pos_var = add_combo(h, ["top", "middle", "bottom"],
                              cfg.get("logo_pos_y", "middle"))

    h = add_field("Text Color")
    text_color_var = add_color(h, cfg.get("text_color", "#ffffff"))
    h = add_field("Text Size")
    text_size_var = add_spin(h, 8, 24, cfg.get("text_size", 11))
    h = add_field("Text Align")
    text_align_var = add_combo(h, ["left", "center", "right"],
                                cfg.get("text_align", "center"))

    h = add_field("Bar Color")
    bar_color_var = add_color(h, cfg.get("bar_color", "#ffffff"))
    h = add_field("Bar Track")
    bar_track_var = add_color(h, cfg.get("bar_track_color", "#3c3f41"))
    h = add_field("Bar Width")
    bar_width_var = add_spin(h, 120, 520, cfg.get("bar_width", 280))
    h = add_field("Bar Height")
    bar_height_var = add_spin(h, 3, 30, cfg.get("bar_height", 7))
    h = add_field("Bar Shape")
    rounded_var = tk.BooleanVar(value=bool(cfg.get("bar_rounded", True)))
    tk.Checkbutton(h, text="Rounded", variable=rounded_var, bg=parent["bg"],
                    fg=FG, activebackground=parent["bg"],
                    activeforeground=FG, selectcolor=BG_ACTIVE,
                    font=("TkDefaultFont", 11)).pack(side="left")
    h = add_field("Bar Align")
    bar_align_var = add_combo(h, ["left", "center", "right"],
                               cfg.get("bar_align", "center"))
    h = add_field("Bar Mode")
    mode_var = add_combo(h, ["auto", "bounce", "progress"],
                          cfg.get("progress_mode", "auto"))

    h = add_field("Updates")
    updates_var = tk.BooleanVar(value=bool(cfg.get("check_updates", True)))
    tk.Checkbutton(h, text="Check for Sober updates before launching",
                    variable=updates_var, bg=parent["bg"], fg=FG,
                    activebackground=parent["bg"], activeforeground=FG,
                    selectcolor=BG_ACTIVE,
                    font=("TkDefaultFont", 11)).pack(side="left")

    def collect():
        return {
            "theme": theme_var.get(),
            "bg_type": bg_type_var.get(),
            "bg_color": bg_color_var.get().strip(),
            "bg_image": bg_image_var.get().strip(),
            "logo_path": logo_var.get().strip(),
            "logo_size": logo_size_var.get(),
            "logo_align": logo_align_var.get(),
            "logo_pos_y": logo_pos_var.get(),
            "text_color": text_color_var.get().strip(),
            "text_size": text_size_var.get(),
            "text_align": text_align_var.get(),
            "bar_color": bar_color_var.get().strip(),
            "bar_track_color": bar_track_var.get().strip(),
            "bar_width": bar_width_var.get(),
            "bar_height": bar_height_var.get(),
            "bar_rounded": rounded_var.get(),
            "bar_align": bar_align_var.get(),
            "progress_mode": mode_var.get(),
            "check_updates": updates_var.get(),
        }

    def do_preview():
        c = collect()
        win = tk.Toplevel(app, bg=c.get("bg_color", "#232527"))
        win.title("Launcher Preview")
        win.resizable(False, False)

        import threading
        import time
        ui = bootstrapper.BootstrapperWindow(win, win, c, menu=True)
        ui.pack(fill="both", expand=True)

        def demo():
            steps = [(0.08, "Checking for updates..."),
                     (0.35, "Preparing Roblox..."),
                     (0.62, "Loading assets..."),
                     (1.0, "Started!")]
            for frac, text in steps:
                if ui.closed:
                    return
                time.sleep(0.9)
                ui.progress(frac)
                ui.status(text)
            time.sleep(1.4)
            ui.close()

        def on_play():
            ui.start_progress()
            threading.Thread(target=demo, daemon=True).start()

        ui.on_play = on_play
        ui.on_configure = lambda: ui.close()

    def do_save():
        c = collect()
        try:
            bootstrapper.save_config(c)
            status.configure(
                text="Saved. The 'Sober with Lution' shortcut now uses this launcher.",
                fg=FG_DIM)
        except Exception as e:
            status.configure(text=f"Save failed: {e}", fg=ERROR)

    btn_row = tk.Frame(parent, bg=parent["bg"])
    btn_row.pack(anchor="w", fill="x", padx=pad, pady=(6, 14))
    app.make_button(btn_row, "Preview", command=do_preview, padx=14,
                     pady=8).pack(side="left", padx=(0, 6))
    app.make_button(btn_row, "Save & Install Shortcut", command=do_save
                     ).pack(side="left")

def build_sobermanager(app, parent, pad):
    import re
    import threading

    import sober

    idle_text = "Install / Update Sober"
    btn = app.make_button(parent, idle_text)
    btn.pack(anchor="w", padx=pad, pady=(4, 4))

    busy = {"flag": False}

    def worker(win, log_text, bar, status_label):
        pct_re = re.compile(r"(\d{1,3})\s*%")
        state = {"pct": -1}

        def safe(fn):
            try:
                if win.winfo_exists():
                    fn()
            except tk.TclError:
                pass

        def set_bar(value):
            def do():
                if bar["mode"] != "determinate":
                    bar.stop()
                    bar.configure(mode="determinate", maximum=100)
                bar.configure(value=value)
            safe(do)

        def append_line(line):
            def do():
                log_text.configure(state="normal")
                log_text.insert("end", line + "\n")
                log_text.see("end")
                log_text.configure(state="disabled")
            safe(do)

        def cb(line):
            m = pct_re.search(line)
            if m:
                value = int(m.group(1))
                app.after(0, lambda v=value: set_bar(v))
                words = re.sub(r"[-\\|/.\s#=\[\]()>*•+=…\d%]", "", line)
                jumped = state["pct"] == -1 or value == 100 or value - state["pct"] >= 10
                state["pct"] = value
                if words or jumped:
                    app.after(0, lambda l=line: append_line(l))
            else:
                state["pct"] = -1
                app.after(0, lambda l=line: append_line(l))

        ok, _msg = sober.ensure_sober(cb)

        def reset_btn():
            btn.configure(text=idle_text)
            busy["flag"] = False

        def finish():
            try:
                alive = win.winfo_exists()
            except tk.TclError:
                alive = False
            if alive:
                try:
                    bar.stop()
                    if ok:
                        bar.configure(mode="determinate", maximum=100,
                                       value=100)
                    status_label.configure(
                        text="Finished successfully." if ok else "Something went wrong.",
                        fg=ACCENT if ok else ERROR)
                except tk.TclError:
                    pass
            btn.configure(text="Done" if ok else "Failed")
            app.after(4000, reset_btn)

        app.after(0, finish)

    def open_window():
        win = tk.Toplevel(app, bg=BG)
        win.title("Install / Update Sober")
        win.geometry("560x380")
        win.configure(bg=BG)
        win.resizable(False, False)

        bar = ttk.Progressbar(win, mode="indeterminate", length=100)
        bar.pack(fill="x", padx=16, pady=(16, 8))
        bar.start(12)

        log_frame = tk.Frame(win, bg=BG_SIDEBAR, highlightthickness=1,
                              highlightbackground=BG_SIDEBAR)
        log_frame.pack(fill="both", expand=True, padx=16, pady=(0, 10))

        log_text = tk.Text(log_frame, bg=BG_ACTIVE, fg=FG,
                            font=("TkDefaultFont", 10), relief="flat",
                            highlightthickness=0, wrap="word",
                            state="disabled")
        log_scroll = tk.Scrollbar(log_frame, orient="vertical",
                                   command=log_text.yview,
                                   bg=BG_SIDEBAR, troughcolor=BG_SIDEBAR,
                                   activebackground=FG_DIM, width=10)
        log_text.configure(yscrollcommand=log_scroll.set)
        log_scroll.pack(side="right", fill="y")
        log_text.pack(side="left", fill="both", expand=True, padx=(2, 0),
                       pady=2)

        bottom = tk.Frame(win, bg=BG)
        bottom.pack(fill="x", padx=16, pady=(0, 14))

        status_label = tk.Label(bottom, text="Working...", bg=BG, fg=FG_DIM,
                                 font=("TkDefaultFont", 10), anchor="w")
        status_label.pack(side="left")

        close_btn = app.make_button(bottom, "Close", command=win.destroy,
                                     bg=BG_SIDEBAR, fg=FG_DIM,
                                     padx=14, pady=6)
        close_btn.pack(side="right")

        return win, log_text, bar, status_label

    def run():
        if busy["flag"]:
            return
        busy["flag"] = True
        btn.configure(text="Working...")
        win, log_text, bar, status_label = open_window()
        threading.Thread(target=worker,
                          args=(win, log_text, bar, status_label),
                          daemon=True).start()

def build_soberuninstall(app, parent, pad):
    import threading

    import log
    import sober

    idle_text = "Uninstall Sober Completely"
    busy = {"flag": False}

    def worker():
        log.info("Uninstalling Sober completely")
        ok_flatpak, _msg = sober.uninstall()

        if ok_flatpak:
            if not sober.delete_sober_data():
                log.error("Could not fully delete Sober data folder")
        else:
            log.warning("Flatpak uninstall failed, wiping data anyway")
            sober.delete_sober_data()

        ok = ok_flatpak

        def reset():
            btn.configure(text=idle_text)
            busy["flag"] = False

        def finish():
            if ok:
                log.info("Sober uninstalled")
                btn.configure(text="Done")
            else:
                log.error("Sober uninstall failed")
                btn.configure(text="Failed")
            app.after(4000, reset)

        app.after(0, finish)

    def do_uninstall():
        if busy["flag"]:
            return
        win = tk.Toplevel(app, bg=BG)
        win.title("Uninstall Sober")
        win.geometry("480x250")
        win.configure(bg=BG)
        win.resizable(False, False)

        tk.Label(win, text="Completely remove Sober?",
                 bg=BG, fg=FG, font=BODY_FONT,
                 anchor="w").pack(anchor="w", padx=16, pady=(16, 8))

        tk.Label(win,
                 text=("This uninstalls Sober via flatpak AND deletes ALL of its "
                       "data:\n~/.var/app/org.vinegarhq.Sober\n\n"
                       "Your mods, fonts, cursors, sounds and every Sober "
                       "setting will be gone forever. This cannot be undone."),
                 bg=BG, fg=ERROR, font=("TkDefaultFont", 10),
                 anchor="w", justify="left",
                 wraplength=420).pack(anchor="w", padx=16, pady=(0, 12))

        btn_row = tk.Frame(win, bg=BG)
        btn_row.pack(anchor="w", padx=16, pady=(0, 16))

        def confirm():
            win.destroy()
            busy["flag"] = True
            btn.configure(text="Working...")
            threading.Thread(target=worker, daemon=True).start()

        app.make_button(btn_row, "Delete Everything", command=confirm,
                          bg=ERROR, fg="#0a0a0a", padx=12, pady=6
                          ).pack(side="left", padx=(0, 8))
        app.make_button(btn_row, "Cancel", command=win.destroy,
                          padx=12, pady=6).pack(side="left")

    btn = app.make_button(parent, idle_text, command=do_uninstall)
    btn.pack(anchor="w", padx=pad, pady=(4, 4))

def build_resetall(app, parent, pad):
    status = tk.Label(parent, text="", bg=parent["bg"], fg=FG_DIM,
                       font=("TkDefaultFont", 10), anchor="w",
                       wraplength=500, justify="left")
    status.pack(anchor="w", padx=pad, pady=(0, 6))

    def do_reset():
        win = tk.Toplevel(app, bg=BG)
        win.title("Confirm Reset")
        win.geometry("400x160")
        win.configure(bg=BG)
        win.resizable(False, False)

        tk.Label(win, text="This will remove all Lution customizations.\nAre you sure?",
                 bg=BG, fg=FG, font=BODY_FONT,
                 justify="center").pack(pady=(20, 14))

        btn_row = tk.Frame(win, bg=BG)
        btn_row.pack()

        def confirm():
            removed = backup.reset_all()
            status.configure(text=f"Reset complete. Removed: {', '.join(removed)}", fg=FG_DIM)
            win.destroy()

        app.make_button(btn_row, "Yes, reset", command=confirm,
                          bg=ERROR, fg="#0a0a0a", padx=12, pady=6
                          ).pack(side="left", padx=(0, 8))
        app.make_button(btn_row, "Cancel", command=win.destroy,
                          padx=12, pady=6).pack(side="left")

    app.make_button(parent, "Reset Everything", command=do_reset,
                      bg=ERROR, fg="#0a0a0a"
                      ).pack(anchor="w", padx=pad, pady=(0, 14))

def build_backupmanager(app, parent, pad):
    status = tk.Label(parent, text="", bg=parent["bg"], fg=FG_DIM,
                       font=("TkDefaultFont", 10), anchor="w",
                       wraplength=500, justify="left")
    status.pack(anchor="w", padx=pad, pady=(0, 6))

    def do_export():
        path = filedialog.asksaveasfilename(
            title="Save Backup",
            defaultextension=".zip",
            filetypes=[("ZIP Archives", "*.zip")],
            initialfile="lution_backup.zip"
        )
        if path:
            try:
                backup.export_backup(path)
                status.configure(text=f"Backup saved to {path.split('/')[-1]}", fg=FG_DIM)
            except Exception as e:
                status.configure(text=str(e), fg=ERROR)

    app.make_button(parent, "Export Backup", command=do_export
                     ).pack(anchor="w", padx=pad, pady=(0, 6))

    def do_import():
        path = filedialog.askopenfilename(
            title="Open Backup",
            filetypes=[("ZIP Archives", "*.zip")]
        )
        if path:
            try:
                restored = backup.import_backup(path)
                status.configure(text=f"Restored {len(restored)} file(s). Restart Lution.", fg=FG_DIM)
            except Exception as e:
                status.configure(text=str(e), fg=ERROR)

    app.make_button(parent, "Import Backup", command=do_import
                     ).pack(anchor="w", padx=pad, pady=(0, 14))
