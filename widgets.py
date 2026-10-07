# yep it's literally all the widgets every textbox, menu, window, dropdown menu, everything bro
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
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
import log
import sober
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

def _auto_resize(win):
    try:
        win.update_idletasks()
        rw, rh = win.winfo_reqwidth(), win.winfo_reqheight()
        win.minsize(min(rw, 380), min(rh, 320))
        win.resizable(True, True)
    except tk.TclError:
        pass

def _fit(win, w, h, ratio=0.85):
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    w = max(260, min(w, sw))
    h = max(120, min(h, int(sh * ratio)))
    x = max(0, (sw - w) // 2)
    y = max(0, (sh - h) // 3)
    win.geometry(f"{w}x{h}+{x}+{y}")
    win.after(20, lambda: _auto_resize(win))

def _clear_all_fflags(app, reload_fn, status):
    win = tk.Toplevel(app, bg=BG)
    win.title("Delete all FFlags")
    _fit(win, 400, 120)
    win.configure(bg=BG)
    win.resizable(False, False)

    tk.Label(win, text="remove all your fflags?", bg=BG, fg=FG,
             font=BODY_FONT).pack(pady=(20, 14))

    btn_row = tk.Frame(win, bg=BG)
    btn_row.pack()

    def confirm():
        fflags.save_fflags({})
        reload_fn()
        status.configure(text="All fflags deleted", fg=FG_DIM)
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

def _clean_disallowed(app, reload_fn, status):
    _ok, bad = fflags.validate(fflags.get_fflags())
    if not bad:
        status.configure(text="every fflag is on the allowlist :D", fg=FG_DIM)
        return

    win = tk.Toplevel(app, bg=BG)
    win.title("Remove non-working fflags")
    _fit(win, 500, 240)
    win.configure(bg=BG)
    win.resizable(False, False)

    shown = ", ".join(bad[:8])
    more = f"\nand {len(bad) - 8} more" if len(bad) > 8 else ""
    tk.Label(win,
             text=(f"Remove {len(bad)} flag(s) that are not on Roblox's "
                   f"allowlist?\n\n{shown}{more}"),
             bg=BG, fg=FG, font=BODY_FONT, justify="left",
             wraplength=460).pack(anchor="w", padx=16, pady=(16, 14))

    btn_row2 = tk.Frame(win, bg=BG)
    btn_row2.pack(pady=(0, 16))

    def confirm():
        kept, removed = fflags.clean(fflags.get_fflags())
        fflags.save_fflags(kept)
        win.destroy()
        reload_fn()
        status.configure(text=f"Removed {len(removed)} flag(s) not on the "
                              f"allowlist.", fg=FG_DIM)

    app.make_button(btn_row2, "remove them", command=confirm,
                    bg=ERROR, fg="#0a0a0a", padx=12, pady=6
                    ).pack(side="left", padx=(0, 8))
    app.make_button(btn_row2, "cancel", command=win.destroy,
                    padx=12, pady=6).pack(side="left")

def _update_allowlist(app, reload_fn, status):
    import threading

    status.configure(text="Updating fflag allowlist...", fg=FG_DIM)

    def worker():
        ok, msg = fflags.refresh_allowlist()

        def done():
            if ok:
                status.configure(text=f"Allowlist updated: {msg}.", fg=FG_DIM)
            else:
                status.configure(text=f"Allowlist update failed: {msg}",
                                 fg=ERROR)
            reload_fn()

        app.after(0, done)

    threading.Thread(target=worker, daemon=True).start()

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

    allow_label = tk.Label(parent, text="", bg=parent["bg"], fg=FG_DIM,
                           font=("TkDefaultFont", 10), anchor="w",
                           wraplength=500, justify="left")
    allow_label.pack(anchor="w", padx=pad, pady=(0, 6))

    btn_row = tk.Frame(parent, bg=parent["bg"])
    btn_row.pack(anchor="w", fill="x", padx=pad, pady=(0, 6))
    allow_row = tk.Frame(parent, bg=parent["bg"])
    allow_row.pack(anchor="w", fill="x", padx=pad, pady=(0, 14))

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

    def _update_warning(key_entry):
        warn = getattr(key_entry, "_warn_lbl", None)
        if warn is None:
            return
        name = key_entry.get().strip()
        denied = bool(name) and name not in fflags.allowlist()
        if denied:
            warn.pack(side="left", padx=(0, 6))
        else:
            warn.pack_forget()

    def refresh_warnings():
        denied = []
        for key_entry, _, _row in app.fflag_rows:
            name = key_entry.get().strip()
            if name and name not in fflags.allowlist():
                denied.append(name)
            _update_warning(key_entry)

        if not app.fflag_rows:
            allow_label.configure(text="", fg=FG_DIM)
        elif denied:
            shown = ", ".join(denied[:3])
            more = f" (+{len(denied) - 3} more)" if len(denied) > 3 else ""
            allow_label.configure(
                text=f"{len(denied)} flag(s) not on Roblox's allowlist and will "
                     f"be ignored: {shown}{more}",
                fg=ERROR)
        else:
            data = fflags.allowlist_file()
            updated = data.get("updated") or "bundled copy"
            allow_label.configure(
                text=f"All flags are on Roblox's allowlist "
                     f"({len(fflags.allowlist())} allowed, updated {updated}).",
                fg=FG_DIM)

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

        warn_lbl = tk.Label(row, text="not on allowlist", bg=parent["bg"],
                            fg=ERROR, font=("TkDefaultFont", 9))
        key_entry._warn_lbl = warn_lbl
        key_entry.bind("<KeyRelease>",
                       lambda e, ke=key_entry: _update_warning(ke))

        remove_btn = app.make_button(row, "x", command=lambda: remove_row(row),
                                      bg=BG_SIDEBAR, fg=FG_DIM,
                                      padx=10, pady=4)
        warn_lbl.pack(side="left", padx=(0, 6))
        remove_btn.pack(side="left")

        app.fflag_rows.append((key_entry, value_entry, row))
        apply_filter()

    def open_add_flag():
        win = tk.Toplevel(app, bg=BG)
        win.title("Add FFlag")
        _fit(win, 500, 300)
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
        refresh_warnings()
        parent.event_generate("<Configure>")

    def _confirm_disallowed(new_fflags, proceed):
        _ok, bad = fflags.validate(new_fflags)
        if not bad:
            proceed(list(bad))
            return

        win = tk.Toplevel(app, bg=BG)
        win.title("Flags not on the allowlist")
        _fit(win, 500, 240)
        win.configure(bg=BG)
        win.resizable(False, False)

        shown = ", ".join(bad[:8])
        more = f"\nand {len(bad) - 8} more" if len(bad) > 8 else ""
        tk.Label(
            win,
            text=(f"{len(bad)} of these flags are not on Roblox's allowlist "
                  f"and will be ignored by the client:\n\n{shown}{more}"),
            bg=BG, fg=FG, font=BODY_FONT, justify="left",
            wraplength=460).pack(anchor="w", padx=16, pady=(16, 14))

        btn_row2 = tk.Frame(win, bg=BG)
        btn_row2.pack(pady=(0, 16))

        def save_without_bad():
            kept, _removed = fflags.clean(new_fflags)
            win.destroy()
            proceed(list(_removed), saved=kept)

        app.make_button(btn_row2, "remove them & save",
                        command=save_without_bad, padx=12, pady=6
                        ).pack(side="left", padx=(0, 8))
        app.make_button(btn_row2, "save anyway",
                        command=lambda: (win.destroy(), proceed(list(bad))),
                        padx=12, pady=6).pack(side="left", padx=(0, 8))
        app.make_button(btn_row2, "cancel", command=win.destroy,
                        padx=12, pady=6).pack(side="left")

    def save_rows():
        new_fflags = {}
        for key_entry, value_entry, _ in app.fflag_rows:
            key = key_entry.get().strip()
            if not key:
                continue
            new_fflags[key] = fflags.parse_value(value_entry.get())

        def proceed(bad, saved=None):
            to_save = saved if saved is not None else new_fflags
            fflags.save_fflags(to_save)
            reload_rows()
            if saved is not None and bad:
                status.configure(
                    text=f"Flags saved — dropped {len(bad)} not on the "
                         f"allowlist.", fg=FG_DIM)
            elif bad:
                status.configure(
                    text=f"Flags saved — {len(bad)} of them will be ignored "
                         f"by roblox.", fg=ERROR)
            else:
                status.configure(text="Flags saved.", fg=FG_DIM)

        _confirm_disallowed(new_fflags, proceed)

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

    app.make_button(allow_row, "Remove non-working fflags",
                     command=lambda: _clean_disallowed(app, reload_rows, status)
                     ).pack(side="left", padx=(0, 6))
    app.make_button(allow_row, "Update fflag allowlist",
                     command=lambda: _update_allowlist(app, reload_rows, status)
                     ).pack(side="left", padx=(0, 6))


    reload_rows()

def _open_presets_window(app, reload_fn, status):
    win = tk.Toplevel(app, bg=BG)
    win.title("FFlag Presets")
    _fit(win, 600, 500)
    win.configure(bg=BG)
    win.resizable(True, True)

    builtins, user_presets = _load_fflag_presets()

    def apply_preset(name, flags, replace=False):
        current = {} if replace else fflags.get_fflags()
        current.update(flags)
        fflags.save_fflags(current)
        reload_fn()
        _ok, bad = fflags.validate(flags)
        note = (f" ({len(bad)} not on the allowlist)" if bad else "")
        verb = "Loaded profile" if replace else "Applied preset"
        status.configure(text=f"{verb}: {name}{note}",
                         fg=ERROR if bad else FG_DIM)

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

            app.make_button(row, "Replace",
                             command=lambda n=name, f=data["flags"]: apply_preset(n, f, replace=True),
                             padx=10, pady=4
                             ).pack(side="right")
            app.make_button(row, "Apply", command=lambda n=name, f=data["flags"]: apply_preset(n, f),
                             padx=10, pady=4
                             ).pack(side="right")

    tk.Label(body, text="Your fflag presets", bg=BG, fg=FG,
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
            tk.Label(user_frame, text="no custom presets", bg=BG_ACTIVE, fg=FG_DIM,
                     font=("TkDefaultFont", 10)).pack(anchor="w", padx=8, pady=8)
            return
        for name, data in up.items():
            row = tk.Frame(user_frame, bg=BG_ACTIVE)
            row.pack(anchor="w", fill="x", padx=8, pady=4)

            app.make_button(row, name,
                             command=lambda n=name, f=data["flags"]: apply_preset(n, f),
                             padx=10, pady=4
                             ).pack(side="left")

            app.make_button(row, "Replace",
                             command=lambda n=name, f=data["flags"]: apply_preset(n, f, replace=True),
                             padx=10, pady=4
                             ).pack(side="left", padx=(6, 0))

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
        _fit(save_win, 400, 160)
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

    app.make_button(body, "save current as a preset", command=save_as_preset,
                     padx=12, pady=6
                     ).pack(anchor="w", padx=16, pady=(0, 16))

def _open_paste_json(app):
    win = tk.Toplevel(app, bg=BG)
    win.title("Paste FFlags JSON")
    win.configure(bg=BG)

    _fit(win, 600, 820)

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
    btn_row.pack(side="bottom", fill="x", anchor="w", padx=16, pady=(0, 16))
    app.make_button(btn_row, "Apply", command=apply_json).pack(side="left")

    status = tk.Label(win, text="", bg=BG, fg=FG_DIM,
                       font=("TkDefaultFont", 10), anchor="w")
    status.pack(side="bottom", anchor="w", fill="x", padx=16, pady=(0, 8))

    tk.Label(win, text="Paste FFlags JSON", bg=BG, fg=FG,
             font=("TkDefaultFont", 14, "bold"), anchor="w"
             ).pack(anchor="w", padx=16, pady=(16, 8))

    text_frame = tk.Frame(win, bg=BG_ACTIVE)
    text_frame.pack(fill="both", expand=True, padx=16, pady=(0, 8))

    text = tk.Text(text_frame, bg=BG_ACTIVE, fg=FG, insertbackground=FG,
                    font=BODY_FONT, relief="flat", wrap="word",
                    highlightthickness=1, highlightbackground=BG_SIDEBAR,
                    height=12)
    text_scroll = tk.Scrollbar(text_frame, orient="vertical",
                                command=text.yview,
                                bg=BG_SIDEBAR, troughcolor=BG_SIDEBAR,
                                activebackground=FG_DIM, width=10)
    text.configure(yscrollcommand=text_scroll.set)
    text_scroll.pack(side="right", fill="y")
    text.pack(side="left", fill="both", expand=True)
    text.focus_set()

    text.bind("<Return>", lambda e: apply_json())
    text.bind("<KP_Enter>", lambda e: apply_json())

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

    app.make_button(row, "browse", command=browse, padx=14, pady=8
                     ).pack(side="left")

    status = tk.Label(parent, text="", bg=parent["bg"], fg=FG_DIM,
                       font=("TkDefaultFont", 10), anchor="w",
                       wraplength=500, justify="left")
    status.pack(anchor="w", padx=pad, pady=(0, 6))

    def apply_font():
        source = path_entry.get().strip()
        if not source:
            status.configure(text="js pick a font file first", fg=ERROR)
            return
        try:
            replaced = fonts.apply_font(source)
            fonts.save_installed_font(source)
        except FileNotFoundError as e:
            status.configure(text=str(e), fg=ERROR)
            return
        if not replaced:
            status.configure(
                text="no font files to replace",
                fg=ERROR)
            return
        status.configure(
            text=f"Replaced {len(replaced)} font file(s).", fg=FG_DIM)

    app.make_button(parent, "Apply font", command=apply_font
                     ).pack(anchor="w", padx=pad, pady=(0, 6))

    def restore_default():
        removed = fonts.restore_fonts()
        if removed:
            status.configure(text="default fonts restored", fg=FG_DIM)
        else:
            status.configure(text="no custom font to restore", fg=ERROR)

    app.make_button(parent, "Restore default fonts", command=restore_default,
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
        win.title("Add environment variable")
        _fit(win, 500, 300)
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
                    text="name cannot be empty or have spaces / '='.")
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

    app.make_button(btn_row, "Add variable", command=open_add_var
                     ).pack(side="left", padx=(0, 6))
    app.make_button(btn_row, "Save variable", command=save_vars_action
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

        app.make_button(row, "browse", command=browse_cursor,
                          padx=14, pady=8).pack(side="left")

    def apply_cursors_action():
        cursors_dict = {}
        for name, entry in cursor_entries.items():
            path = entry.get().strip()
            if path:
                cursors_dict[name] = path
        if not cursors_dict:
            status.configure(text="select atleast one cursor file first", fg=ERROR)
            return
        applied = cursors.apply_cursors(cursors_dict)
        cursors.save_installed_cursors(cursors_dict)
        status.configure(text=f"Applied {len(applied)} cursor file(s).", fg=FG_DIM)

    app.make_button(parent, "Apply cursors", command=apply_cursors_action
                      ).pack(anchor="w", padx=pad, pady=(0, 6))

    def restore_default():
        removed = cursors.restore_cursors()
        if removed:
            status.configure(text="default cursors are restored", fg=FG_DIM)
        else:
            status.configure(text="no custom cursors to restore", fg=ERROR)

    app.make_button(parent, "Restore default cursors", command=restore_default,
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
        status.configure(text="theme saved. restart lution to apply", fg=FG_DIM)

    app.make_button(parent, "Save theme", command=apply_theme
                     ).pack(anchor="w", padx=pad, pady=(0, 6))

    def restore_default():
        themes.save_theme(dict(themes.DEFAULTS))
        for key in themes.COLOR_KEYS:
            entries[key].delete(0, "end")
            entries[key].insert(0, themes.DEFAULTS[key])
        status.configure(text="default theme restored. restart lution to apply", fg=FG_DIM)

    app.make_button(parent, "Restore default theme", command=restore_default,
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

    browse_btn = tk.Label(custom_row, text="browse", bg=ACCENT, fg="#0a0a0a",
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
            status.configure(text="select an emoji font first", fg=ERROR)
            return
        try:
            replaced = emoji.apply_emoji(path)
        except FileNotFoundError as e:
            status.configure(text=str(e), fg=ERROR)
            return
        if not replaced:
            status.configure(text="no emoji font found to replace", fg=ERROR)
            return
        emoji.save_installed_emoji(path)
        status.configure(text=f"Replaced {len(replaced)} emoji file(s).", fg=FG_DIM)

    app.make_button(parent, "Apply emoji font", command=apply_emoji_font
                     ).pack(anchor="w", padx=pad, pady=(0, 6))

    def restore_default():
        removed = emoji.restore_emoji()
        if removed:
            status.configure(text="default emoji fonts are restored", fg=FG_DIM)
        else:
            status.configure(text="no custom emoji font to restore", fg=ERROR)

    app.make_button(parent, "Restore default emoji", command=restore_default,
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
            status.configure(text="select a mod by clicking on the mod's name or import one", fg=ERROR)
            return
        name = mod_listbox.get(sel[0])
        mod_path = mods.MODS_DIR / f"{name}.zip"
        conflicts = mods.check_mod_conflicts(mod_path)
        if conflicts:
            first = conflicts[0]
            status.configure(
                text=f"Overlaps another mod on {len(conflicts)} file(s), e.g. {first}. Installing anyway.",
                fg="#e0c252")
        ok, msg = mods.install_mod(mod_path)
        status.configure(text=msg, fg=FG_DIM if ok else ERROR)

    def remove_selected():
        sel = mod_listbox.curselection()
        if not sel:
            status.configure(text="select a mod first by clicking on it (delete all mods clears the entire overlay)", fg=ERROR)
            return
        name = mod_listbox.get(sel[0])
        mod_path = mods.MODS_DIR / f"{name}.zip"
        mods.delete_mod(mod_path)
        status.configure(text=f"Deleted: {name} from mod manager. click delete all mods to fully remove the mod.", fg=FG_DIM)
        refresh_list()

    def cleanup_all():
        win = tk.Toplevel(app, bg=BG)
        win.title("Delete all mods")
        _fit(win, 440, 220)
        win.configure(bg=BG)
        win.resizable(False, False)

        tk.Label(win, text="Delete all mod content from Sober?",
                 bg=BG, fg=FG, font=BODY_FONT,
                 anchor="w").pack(anchor="w", padx=16, pady=(16, 8))

        tk.Label(win, text="this removes mod files from the overlay.\nyour custom cursors, fonts and emoji fonts won't be deleted",
                 bg=BG, fg=FG_DIM, font=("TkDefaultFont", 10),
                 anchor="w", justify="left", wraplength=380).pack(anchor="w", padx=16, pady=(0, 10))

        also_var = tk.BooleanVar(value=False)
        cb = tk.Checkbutton(win, text="also delete cursors, fonts and emoji fonts",
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

    app.make_button(btn_row, "Import mod", command=import_mod
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
        win.title("mods")
        _fit(win, 560, 460)
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
            tk.Label(conflict_list, text="no conflicts found",
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

    app.make_button(parent, "Scan for conflicts", command=scan
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

        app.make_button(row, "browse", command=browse_sound,
                          padx=14, pady=8).pack(side="left")

    def apply_sounds_action():
        sounds_dict = {}
        for name, entry in sound_entries.items():
            path = entry.get().strip()
            if path:
                sounds_dict[name] = path
        if not sounds_dict:
            status.configure(text="pick atleast one sound file first", fg=ERROR)
            return
        applied = sound_mods.apply_sounds(sounds_dict)
        sound_mods.save_installed_sounds(sounds_dict)
        status.configure(text=f"Applied {len(applied)} sound file(s).",
                         fg=FG_DIM)

    app.make_button(parent, "Apply sounds", command=apply_sounds_action
                      ).pack(anchor="w", padx=pad, pady=(0, 6))

    def restore_default():
        removed = sound_mods.restore_sounds()
        if removed:
            status.configure(text="default sounds restored", fg=FG_DIM)
        else:
            status.configure(text="no custom sounds to restore", fg=ERROR)

    app.make_button(parent, "Restore default sounds", command=restore_default,
                      bg=ERROR, fg="#0a0a0a"
                      ).pack(anchor="w", padx=pad, pady=(0, 14))

def build_playhistory(app, parent, pad):
    import threading

    import history
    import log
    import playtime

    status = tk.Label(parent, text="", bg=parent["bg"], fg=FG_DIM,
                       font=("TkDefaultFont", 10), anchor="w",
                       wraplength=500, justify="left")
    status.pack(anchor="w", padx=pad, pady=(0, 6))

    summary = tk.Label(parent, text="Counting playtime...", bg=parent["bg"],
                       fg=FG_DIM, font=("TkDefaultFont", 11, "bold"),
                       anchor="w")
    summary.pack(anchor="w", padx=pad, pady=(0, 6))

    list_frame = tk.Frame(parent, bg=parent["bg"])
    list_frame.pack(anchor="w", fill="x", padx=pad, pady=(0, 6))

    def render(entries, names, times=None, total=None):
        times = times or {}
        for w in list_frame.winfo_children():
            w.destroy()

        if total:
            summary.configure(
                text=f"Total {playtime.format_duration(total[1])} in "
                     f"{total[2]} sessions", fg=FG_DIM)
        elif total is None:
            summary.configure(text="i can't see playtime from sober's logs :(", fg=ERROR)

        if not entries:
            tk.Label(list_frame,
                     text="no games played",
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

            played = times.get(place_id)
            
            def play(p=place_id, n=name_text):
                log.info(f"play history: launching place {p}")
                bootstrapper.open_in(app,
                                      url=f"roblox://experiences/start?placeId={p}")

            app.make_button(row, "Play", command=play,
                              padx=16, pady=7).pack(side="right",
                                                     padx=(0, 10))

            if played:
                time_lbl = tk.Label(row,
                                     text=f"{history.rel_time(ts)} · "
                                          f"{playtime.format_duration(played)} played",
                                     bg=BG_ACTIVE, fg=FG_DIM,
                                     font=("TkDefaultFont", 10), padx=10)
                time_lbl.pack(side="right")
            else:
                time_lbl = tk.Label(row, text=history.rel_time(ts),
                                     bg=BG_ACTIVE, fg=FG_DIM,
                                     font=("TkDefaultFont", 10), padx=10)
                time_lbl.pack(side="right")

    def refresh():
        entries = history.get_history()
        ids = [pid for pid, _ts in entries]

        render(entries, history.load_name_cache())

        def worker():
            ev = getattr(app, "mainloop_started", None)
            if ev is not None:
                ev.wait(timeout=10)
            try:
                total = playtime.scan()
                times = total[0]
            except Exception as e:
                log.warning(f"i can't scan your playtime: {e}")
                times, total = None, None
            names = history.resolve_names(ids)
            app.after(0, lambda: render(entries, names, times, total))

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
            msg = "you can now apply this mod in the mods section!"
        else:
            msg = ("you can apply this fflag by going in fflags presets and clicking the one you installed!")
        tk.Label(win, text=msg, bg=BG, fg=FG_DIM,
                 font=("TkDefaultFont", 10), anchor="w", justify="left",
                 wraplength=430).pack(anchor="w", padx=16, pady=(0, 12))

        _fit(win, 480, 170)
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
                     text="marketplace is unreachable and there is no cached copy",
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
            items, from_cache = mkt.fetch_store()
            icons = {}
            for item in items:
                if item.get("type") == "mod" and item.get("icon"):
                    path = mkt.fetch_icon(item.get("name", ""),
                                           item["icon"])
                    if path:
                        icons[item["name"]] = str(path)
            if from_cache:
                set_status("can't fetch marketplace, using cached copy",
                           error=True)
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
    app.make_button(btn_row, "Refresh", command=refresh_list,
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
            app.make_button(parent, "see the new lution update", command=open_url,
                              padx=14, pady=6).pack(anchor="w", padx=pad, pady=(0, 6))
        else:
            status.configure(text="Up to date", fg=FG_DIM)

    app.after(100, check)

def build_soberversion(app, parent, pad):
    version_lbl = tk.Label(parent, text="Sober version: Checking...",
                           bg=parent["bg"], fg=FG_DIM,
                           font=("TkDefaultFont", 11), anchor="w")
    version_lbl.pack(anchor="w", padx=pad, pady=(0, 6))

    def fetch(attempt=0):
        try:
            result = subprocess.run(
                ["flatpak", "info", "org.vinegarhq.Sober"],
                capture_output=True, text=True, timeout=8,
                env=sober.clean_env()
            )
            version = "Unknown"
            for line in result.stdout.splitlines():
                log.debug(f"flatpak info: {line}")
                if line.strip().startswith("Version:"):
                    version = line.split(":", 1)[1].strip()
                    break
            for line in result.stderr.splitlines():
                log.debug(f"flatpak info stderr: {line}")
            if version != "Unknown":
                log.info(f"Sober version: {version}")
                version_lbl.configure(text=f"Sober version: {version}")
                return
            log.warning(f"Sober version not in flatpak output (rc={result.returncode})")
            if attempt < 2:
                version_lbl.configure(text="Sober version: ... (retrying)")
                app.after(1500, lambda: fetch(attempt + 1))
            else:
                version_lbl.configure(text="Sober version: idk bro")
        except Exception as e:
            log.error(f"i can't see sober's version :(: {e}")
            if attempt < 2:
                version_lbl.configure(text="Sober version: ... (retrying)")
                app.after(1500, lambda: fetch(attempt + 1))
            else:
                version_lbl.configure(text="Sober version: idk bro")

    app.after(300, fetch)

def build_soberlauncher(app, parent, pad):
    import log

    def run():
        log.info("Launch Sober clicked")
        bootstrapper.open_in(app)

    def run_vanilla():
        import launcher
        log.info("Launch vanilla Sober clicked")
        try:
            if launcher.sober_is_running():
                raise launcher.LaunchError(
                    "Sober is already running, so it keeps the files it was "
                    "started with.")
            launcher.launch_plain()
        except launcher.LaunchError as e:
            log.error(f"lauching sober without customizations failed: {e}")
            messagebox.showerror("Lution", str(e), parent=parent)

    app.make_button(parent, "Launch Sober", command=run
                    ).pack(anchor="w", padx=pad, pady=(4, 4))
    app.make_button(parent, "Launch Sober without customizations",
                    command=run_vanilla
                    ).pack(anchor="w", padx=pad, pady=(4, 4))

def build_sobersettings(app, parent, pad):
    import log

    def open_settings():
        log.info("Opening Sober settings")
        subprocess.Popen(["flatpak", "run", "org.vinegarhq.Sober", "config"],
                         env=sober.clean_env())

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
    app.make_button(h, "browse", command=lambda: browse_image(bg_image_var),
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
    app.make_button(h, "browse", command=lambda: browse_image(logo_var),
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
        _fit(win, 680, 520)
        win.configure(bg=c.get("bg_color", "#232527"))

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
                text="saved",
                fg=FG_DIM)
        except Exception as e:
            status.configure(text=f"Save failed: {e}", fg=ERROR)

    btn_row = tk.Frame(parent, bg=parent["bg"])
    btn_row.pack(anchor="w", fill="x", padx=pad, pady=(6, 14))
    app.make_button(btn_row, "Preview", command=do_preview, padx=14,
                     pady=8).pack(side="left", padx=(0, 6))
    app.make_button(btn_row, "Save", command=do_save
                     ).pack(side="left")

def build_soberguide(app, parent, pad):
    GUIDE = (
        "Sober is installed and managed via Flatpak.\n\n"
        "Lution keeps its customizations in\n"
        "~/.local/share/Lution/overlay and only applies them when it launches\n"
        "Sober itself. Launching Sober any other way gives you vanilla Sober,\n"
        "so nothing here is modified behind your back.\n\n"
        "how to install sober:\n"
        "$ flatpak update org.vinegarhq.Sober\n\n"
        "how to uninstall sober:\n"
        "$ flatpak uninstall org.vinegarhq.Sober\n\n"
        "how to fully uninstall sober:\n"
        "$ flatpak uninstall --delete-data org.vinegarhq.Sober\n\n"
        "how to delete sober's data:\n"
        "$ rm -rf ~/.var/app/org.vinegarhq.Sober/\n\n"
        "how to delete lution's customizations:\n"
        "use Reset All on the Backup page, or\n"
        "$ rm -rf ~/.local/share/Lution\n\n"
        "how to update sober:\n"
        "$ flatpak update org.vinegarhq.Sober\n\n"
        "you also might aswell run flatpak update if sober is not using your dedicated graphics card or it feels laggy "
    )

    def open_guide():
        win = tk.Toplevel(app, bg=BG)
        win.title("Sober Guide")
        _fit(win, 520, 440)
        win.configure(bg=BG)
        win.resizable(False, False)

        txt = tk.Text(win, bg=BG_ACTIVE, fg=FG,
                       font=("TkDefaultFont", 12), relief="flat",
                       highlightthickness=0, wrap="word",
                       padx=16, pady=16, cursor="xterm")
        txt.insert("1.0", GUIDE)
        txt.configure(state="normal")
        txt.pack(fill="both", expand=True)

    btn = app.make_button(parent, "How to uninstall / update / install Sober",
                          command=open_guide)
    btn.pack(anchor="w", padx=pad, pady=(4, 4))

def build_resetall(app, parent, pad):
    status = tk.Label(parent, text="", bg=parent["bg"], fg=FG_DIM,
                       font=("TkDefaultFont", 10), anchor="w",
                       wraplength=500, justify="left")
    status.pack(anchor="w", padx=pad, pady=(0, 6))

    def do_reset():
        win = tk.Toplevel(app, bg=BG)
        win.title("Confirm Reset")
        _fit(win, 400, 160)
        win.configure(bg=BG)
        win.resizable(False, False)

        tk.Label(win, text="this WILL remove all lution customizations.\nare you sure?",
                 bg=BG, fg=FG, font=BODY_FONT,
                 justify="center").pack(pady=(20, 14))

        btn_row = tk.Frame(win, bg=BG)
        btn_row.pack()

        def confirm():
            removed = backup.reset_all()
            status.configure(text=f"Removed: {', '.join(removed)}", fg=FG_DIM)
            win.destroy()

        app.make_button(btn_row, "yes pls", command=confirm,
                          bg=ERROR, fg="#0a0a0a", padx=12, pady=6
                          ).pack(side="left", padx=(0, 8))
        app.make_button(btn_row, "Cancel", command=win.destroy,
                          padx=12, pady=6).pack(side="left")

    app.make_button(parent, "Reset everything", command=do_reset,
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

def build_serversel(app, parent, pad):
    import threading

    import bootstrapper
    import history
    import regions

    status = tk.Label(parent, text="", bg=parent["bg"], fg=FG_DIM,
                      font=("TkDefaultFont", 10), anchor="w",
                      wraplength=560, justify="left")
    status.pack(anchor="w", padx=pad, pady=(0, 6))

    place_row = tk.Frame(parent, bg=parent["bg"])
    place_row.pack(anchor="w", fill="x", padx=pad, pady=(0, 6))

    tk.Label(place_row, text="Place ID", bg=parent["bg"], fg=FG,
             font=BODY_FONT).pack(side="left", padx=(0, 8))

    place_var = tk.StringVar()
    place_entry = tk.Entry(place_row, textvariable=place_var, bg=BG, fg=FG,
                           insertbackground=FG, font=BODY_FONT, relief="flat",
                           highlightthickness=1,
                           highlightbackground=BG_SIDEBAR,
                           highlightcolor=ACCENT)
    place_entry.pack(side="left", fill="x", expand=True, ipady=6)

    history_map = {}
    history_box = ttk.Combobox(place_row, values=[], state="readonly",
                               font=BODY_FONT, width=28)
    history_box.pack(side="left", padx=(8, 0))

    def on_history_pick(_event):
        pid = history_map.get(history_box.get())
        if pid:
            place_var.set(pid)
            refresh_regions()

    history_box.bind("<<ComboboxSelected>>", on_history_pick)

    region_row = tk.Frame(parent, bg=parent["bg"])
    region_row.pack(anchor="w", fill="x", padx=pad, pady=(0, 6))

    tk.Label(region_row, text="Region", bg=parent["bg"], fg=FG,
             font=BODY_FONT).pack(side="left", padx=(0, 8))

    region_box = ttk.Combobox(region_row, state="readonly", font=BODY_FONT,
                              width=32,
                              values=[regions.ANY_REGION, regions.AUTO_REGION])
    region_box.set(regions.ANY_REGION)
    region_box.pack(side="left")

    list_frame = tk.Frame(parent, bg=parent["bg"])
    list_frame.pack(anchor="w", fill="x", padx=pad, pady=(6, 6))

    busy = {"find": False}

    def render_history():
        entries = history.get_history()
        names = history.load_name_cache()
        labels = []
        history_map.clear()
        for place_id, _ts in entries:
            label = f"{names.get(place_id, f'Place {place_id}')} ({place_id})"
            labels.append(label)
            history_map[label] = place_id
        history_box.configure(values=labels)

    def clear_rows():
        for w in list_frame.winfo_children():
            w.destroy()

    def render(place, rows):
        clear_rows()

        header = tk.Frame(list_frame, bg=parent["bg"])
        header.pack(anchor="w", fill="x", pady=(0, 2))
        for text, width in (("Region", 26), ("Players", 9), ("Ping", 8),
                            ("Uptime", 10)):
            tk.Label(header, text=text, bg=parent["bg"], fg=FG_DIM,
                     font=("TkDefaultFont", 10, "bold"), width=width,
                     anchor="w").pack(side="left", padx=(0, 6))

        for row in rows:
            frame = tk.Frame(list_frame, bg=BG_ACTIVE, highlightthickness=1,
                             highlightbackground=BG_SIDEBAR)
            frame.pack(anchor="w", fill="x", pady=2)

            tk.Label(frame, text=row["region"], bg=BG_ACTIVE, fg=FG,
                     font=("TkDefaultFont", 11), width=26, anchor="w",
                     padx=10).pack(side="left", ipady=5)

            players = ("-" if row["playing"] is None
                       else f"{row['playing']}/{row['max']}")
            ping = "-" if row["ping"] is None else f"{row['ping']} ms"
            for text, width in ((players, 9), (ping, 8),
                                (regions.age_text(row["first_seen"]), 10)):
                tk.Label(frame, text=text, bg=BG_ACTIVE,
                         fg=ERROR if text.endswith("ms") and row["ping"] and row["ping"] > 200 else FG_DIM,
                         font=("TkDefaultFont", 10), width=width,
                         anchor="w").pack(side="left", padx=(0, 6))

            def join(p=place, job=row["id"], r=row["region"]):
                log.info(f"Servers: joining place {p} in {r} ({job})")
                bootstrapper.open_in(app, url=regions.join_url(p, job))

            app.make_button(frame, "Join", command=join, padx=14, pady=5
                            ).pack(side="right", padx=(0, 8))

    def find():
        if busy["find"]:
            return
        place = place_var.get().strip()
        if not place.isdigit():
            status.configure(text="enter a place id or pick from your play history to the right", fg=ERROR)
            return

        region = regions.strip_count(region_box.get() or regions.ANY_REGION)
        busy["find"] = True
        clear_rows()
        status.configure(text="Looking for servers...", fg=FG_DIM)

        def worker():
            try:
                rows = regions.find_servers(place, region)
                err = None
            except Exception as e:
                log.warning(f"Servers: lookup failed: {e}")
                rows, err = [], str(e)

            def done():
                busy["find"] = False
                if err:
                    status.configure(text=f"Could not fetch servers: {err}",
                                     fg=ERROR)
                    return
                if not rows:
                    status.configure(
                        text="no servers found for that place and region, game is probably deleted or inactive in some way",
                        fg=FG_DIM)
                    return
                render(place, rows)
                where = region if region != regions.ANY_REGION else "everywhere"
                status.configure(
                    text=f"{len(rows)} servers from {where} best ping "
                         f"first", fg=FG_DIM)

            app.after(0, done)

        threading.Thread(target=worker, daemon=True).start()

    def refresh_regions():
        place = place_var.get().strip()
        place = place if place.isdigit() else ""
        current = region_box.get()

        def worker():
            try:
                options = regions.region_options(place)
                err = None
            except Exception as e:
                log.debug(f"Servers: region list failed: {e}")
                options, err = None, str(e)

            def done():
                if options is None:
                    status.configure(text=f"Could not load regions: {err}",
                                     fg=ERROR)
                    return
                region_box.configure(values=options)
                if current in options:
                    region_box.set(current)
                elif options:
                    region_box.set(options[0])

            app.after(0, done)

        threading.Thread(target=worker, daemon=True).start()

    def on_page_shown(page_name):
        if page_name == "Servers":
            render_history()
            refresh_regions()

    try:
        app.page_shown_listeners.append(on_page_shown)
    except AttributeError:
        pass

    app.make_button(region_row, "Find servers", command=find
                    ).pack(side="left", padx=(10, 0))

    render_history()
    status.configure(text="choose a game and region", fg=FG_DIM)


def build_shortcuts(app, parent, pad):
    import threading

    import history
    import shortcuts as game_shortcuts

    status = tk.Label(parent, text="", bg=parent["bg"], fg=FG_DIM,
                      font=("TkDefaultFont", 10), anchor="w",
                      wraplength=500, justify="left")
    status.pack(anchor="w", padx=pad, pady=(0, 6))

    create_row = tk.Frame(parent, bg=parent["bg"])
    create_row.pack(anchor="w", fill="x", padx=pad, pady=(0, 8))

    tk.Label(create_row, text="Place ID", bg=parent["bg"], fg=FG,
             font=BODY_FONT).pack(side="left", padx=(0, 8))

    place_var = tk.StringVar()
    entry = tk.Entry(create_row, textvariable=place_var, bg=BG, fg=FG,
                     insertbackground=FG, font=BODY_FONT, relief="flat",
                     highlightthickness=1,
                     highlightbackground=BG_SIDEBAR,
                     highlightcolor=ACCENT)
    entry.pack(side="left", fill="x", expand=True, ipady=6)

    busy = {"on": False}
    list_frame = tk.Frame(parent, bg=parent["bg"])
    list_frame.pack(anchor="w", fill="x", padx=pad, pady=(0, 8))
    history_frame = tk.Frame(parent, bg=parent["bg"])
    history_frame.pack(anchor="w", fill="x", padx=pad, pady=(0, 8))

    def create(place_id, name=None):
        if busy["on"]:
            return
        place_id = str(place_id).strip()
        if not place_id.isdigit():
            status.configure(text="letters found!!!! the id must be all numbers", fg=ERROR)
            return
        if game_shortcuts.exists(place_id):
            status.configure(text="that game already has a shortcut", fg=FG_DIM)
            render_all()
            return

        busy["on"] = True
        status.configure(text="Creating shortcut...", fg=FG_DIM)

        def worker():
            try:
                made = game_shortcuts.create(place_id, name=name)
                err = None
            except Exception as e:
                log.warning(f"Shortcuts: create failed: {e}")
                made, err = None, str(e)

            def done():
                busy["on"] = False
                if err:
                    status.configure(text=f"Could not create shortcut: {err}",
                                     fg=ERROR)
                else:
                    status.configure(
                        text=f'Created "{made["name"]} (Sober)" in your '
                             f"applications menu.", fg=FG_DIM)
                    render_all()

            app.after(0, done)

        threading.Thread(target=worker, daemon=True).start()

    def remove(place_id):
        try:
            game_shortcuts.remove(place_id)
            status.configure(text="shortcut removed", fg=FG_DIM)
        except OSError as e:
            status.configure(text=str(e), fg=ERROR)
        render_all()

    def render_shortcuts():
        for w in list_frame.winfo_children():
            w.destroy()

        rows = game_shortcuts.list_shortcuts()
        tk.Label(list_frame, text="Your shortcuts", bg=parent["bg"], fg=FG,
                 font=("TkDefaultFont", 13, "bold"), anchor="w"
                 ).pack(anchor="w", pady=(0, 4))

        if not rows:
            tk.Label(list_frame,
                     text="no shortcuts.",
                     bg=parent["bg"], fg=FG_DIM,
                     font=("TkDefaultFont", 10)
                     ).pack(anchor="w", padx=4, pady=(0, 6))
            return

        for row in rows:
            frame = tk.Frame(list_frame, bg=BG_ACTIVE, highlightthickness=1,
                             highlightbackground=BG_SIDEBAR)
            frame.pack(anchor="w", fill="x", pady=2)

            tk.Label(frame, text=f'{row["name"]} (Sober)', bg=BG_ACTIVE, fg=FG,
                     font=("TkDefaultFont", 11, "bold"), anchor="w",
                     padx=12).pack(side="left", fill="x", expand=True,
                                   ipady=6)

            tk.Label(frame, text=row["place_id"], bg=BG_ACTIVE, fg=FG_DIM,
                     font=("TkDefaultFont", 10), padx=10
                     ).pack(side="right")

            app.make_button(frame, "Remove",
                            command=lambda p=row["place_id"]: remove(p),
                            bg=BG_SIDEBAR, fg=ERROR, padx=12, pady=5
                            ).pack(side="right", padx=(0, 8))

    def render_history():
        for w in history_frame.winfo_children():
            w.destroy()

        entries = history.get_history()
        if not entries:
            return

        names = history.load_name_cache()
        have = {row["place_id"] for row in game_shortcuts.list_shortcuts()}
        missing = [pid for pid, _ts in entries if pid not in have]
        if not missing:
            return

        tk.Label(history_frame, text="From play history", bg=parent["bg"],
                 fg=FG, font=("TkDefaultFont", 13, "bold"), anchor="w"
                 ).pack(anchor="w", pady=(6, 4))

        for place_id in missing:
            frame = tk.Frame(history_frame, bg=BG_ACTIVE,
                             highlightthickness=1,
                             highlightbackground=BG_SIDEBAR)
            frame.pack(anchor="w", fill="x", pady=2)

            tk.Label(frame, text=names.get(place_id, f"Place {place_id}"),
                     bg=BG_ACTIVE, fg=FG, font=("TkDefaultFont", 11),
                     anchor="w", padx=12).pack(side="left", fill="x",
                                               expand=True, ipady=5)

            def add(p=place_id, n=names.get(place_id)):
                create(p, name=n)

            app.make_button(frame, "Add", command=add, padx=12, pady=5
                            ).pack(side="right", padx=(0, 8))

    def render_all():
        render_shortcuts()
        render_history()

    def on_page_shown(page_name):
        if page_name == "Home":
            render_all()

    try:
        app.page_shown_listeners.append(on_page_shown)
    except AttributeError:
        pass

    def create_from_entry():
        create(place_var.get())
        place_var.set("")

    entry.bind("<Return>", lambda e: create_from_entry())
    app.make_button(create_row, "Create shortcut", command=create_from_entry
                    ).pack(side="left", padx=(8, 0))

    render_all()

def _load_avatar(path, size=48):
    if not path:
        return None
    try:
        img = tk.PhotoImage(file=path)
    except tk.TclError:
        return None
    factor = max(1, (img.width() + size - 1) // size)
    img = img.subsample(factor, factor)
    return img

def build_account(app, parent, pad):
    import threading

    import accounts
    import bootstrapper
    import log

    status = tk.Label(parent, text="reading account...", bg=parent["bg"],
                      fg=FG_DIM, font=("TkDefaultFont", 10), anchor="w",
                      wraplength=560, justify="left")
    status.pack(anchor="w", padx=pad, pady=(0, 6))

    holder = {"images": []}

    card = tk.Frame(parent, bg=BG_ACTIVE, highlightthickness=1,
                    highlightbackground=BG_SIDEBAR)
    card.pack(anchor="w", fill="x", padx=pad, pady=(0, 8))

    accounts_frame = tk.Frame(parent, bg=parent["bg"])
    accounts_frame.pack(anchor="w", fill="x", padx=pad, pady=(0, 8))

    friends_frame = tk.Frame(parent, bg=parent["bg"])
    friends_frame.pack(anchor="w", fill="x", padx=pad, pady=(0, 8))

    def clear(widget):
        for w in widget.winfo_children():
            w.destroy()

    def render(data):
        holder["images"].clear()
        user = data["user"]
        avatars = data.get("avatars") or {}
        presence = data.get("presence") or {}

        clear(card)
        inner = tk.Frame(card, bg=BG_ACTIVE)
        inner.pack(anchor="w", fill="x", padx=14, pady=12)

        avatar = _load_avatar(avatars.get(str(user["id"])), size=64)
        if avatar:
            holder["images"].append(avatar)
            tk.Label(inner, image=avatar, bg=BG_ACTIVE).pack(side="left",
                                                              padx=(0, 12))
        info = tk.Frame(inner, bg=BG_ACTIVE)
        info.pack(side="left", anchor="w")
        tk.Label(info, text=user["display_name"] or user["name"],
                 bg=BG_ACTIVE, fg=FG,
                 font=("TkDefaultFont", 15, "bold"), anchor="w"
                 ).pack(anchor="w")
        tk.Label(info, text=f"@{user['name']} · signed in",
                 bg=BG_ACTIVE, fg=ACCENT, font=("TkDefaultFont", 11),
                 anchor="w").pack(anchor="w")
        tk.Label(info, text=f"user id {user['id']}", bg=BG_ACTIVE, fg=FG_DIM,
                 font=("TkDefaultFont", 10), anchor="w").pack(anchor="w")

        clear(accounts_frame)
        rows = data.get("accounts") or []
        if rows:
            tk.Label(accounts_frame, text="Accounts in the \"switch accounts\" menu",
                     bg=parent["bg"], fg=FG,
                     font=("TkDefaultFont", 13, "bold"), anchor="w"
                     ).pack(anchor="w", pady=(0, 4))
            box = tk.Frame(accounts_frame, bg=BG_ACTIVE, highlightthickness=1,
                           highlightbackground=BG_SIDEBAR)
            box.pack(anchor="w", fill="x", pady=(0, 4))

            for account in rows:
                row = tk.Frame(box, bg=BG_ACTIVE)
                row.pack(anchor="w", fill="x", padx=10, pady=3)

                avatar = _load_avatar(avatars.get(str(account["id"])), size=36)
                if avatar:
                    holder["images"].append(avatar)
                    tk.Label(row, image=avatar, bg=BG_ACTIVE).pack(
                        side="left", padx=(0, 10))

                name = account["display_name"] or account["name"]
                text = name if name == account["name"] \
                    else f"{name} (@{account['name']})"
                tk.Label(row, text=text, bg=BG_ACTIVE, fg=FG,
                         font=("TkDefaultFont", 11, "bold"), anchor="w"
                         ).pack(side="left", anchor="w", ipady=4)

                if account.get("active"):
                    tk.Label(row, text="in use", bg=BG_ACTIVE, fg=ACCENT,
                             font=("TkDefaultFont", 10, "bold"),
                             padx=8).pack(side="right")
                elif account.get("signed_out"):
                    tk.Label(row, text="signed out", bg=BG_ACTIVE, fg=FG_DIM,
                             font=("TkDefaultFont", 10), padx=8
                             ).pack(side="right")
                else:
                    tk.Label(row, text="saved", bg=BG_ACTIVE, fg=FG_DIM,
                             font=("TkDefaultFont", 10), padx=8
                             ).pack(side="right")

        clear(friends_frame)
        friends = list(data.get("friends") or [])

        def rank(friend):
            kind = (presence.get(friend["id"]) or {}).get("type",
                                                          accounts.OFFLINE)
            return {accounts.IN_GAME: 0, accounts.ONLINE: 1}.get(kind, 2)

        friends.sort(key=lambda f: (rank(f), f["display_name"].lower()))

        tk.Label(friends_frame, text="Friends", bg=parent["bg"], fg=FG,
                 font=("TkDefaultFont", 13, "bold"), anchor="w"
                 ).pack(anchor="w", pady=(0, 4))

        if not friends:
            tk.Label(friends_frame, text="haha you have no friends L bozo",
                     bg=parent["bg"], fg=FG_DIM,
                     font=("TkDefaultFont", 10)).pack(anchor="w", padx=4)
            return

        box = tk.Frame(friends_frame, bg=BG_ACTIVE, highlightthickness=1,
                       highlightbackground=BG_SIDEBAR)
        box.pack(anchor="w", fill="x")

        for friend in friends:
            here = presence.get(friend["id"]) or {}
            label, kind = accounts.status_text(here)

            row = tk.Frame(box, bg=BG_ACTIVE)
            row.pack(anchor="w", fill="x", padx=10, pady=3)

            avatar = _load_avatar(avatars.get(str(friend["id"])), size=36)
            if avatar:
                holder["images"].append(avatar)
                tk.Label(row, image=avatar, bg=BG_ACTIVE).pack(
                    side="left", padx=(0, 10))

            text = friend["display_name"]
            if friend["name"] and friend["name"] != friend["display_name"]:
                text += f" (@{friend['name']})"

            info = tk.Frame(row, bg=BG_ACTIVE)
            info.pack(side="left", anchor="w", pady=2)
            tk.Label(info, text=text, bg=BG_ACTIVE, fg=FG,
                     font=("TkDefaultFont", 11, "bold"), anchor="w"
                     ).pack(anchor="w")
            tk.Label(info, text=label, bg=BG_ACTIVE,
                     fg=ACCENT if kind == accounts.IN_GAME else FG_DIM,
                     font=("TkDefaultFont", 10), anchor="w").pack(anchor="w")

            if kind == accounts.IN_GAME:
                url = accounts.join_url(here)

                def join(target=url, who=friend["display_name"]):
                    if not target:
                        return
                    log.info(f"Friends: joining {who}")
                    bootstrapper.open_in(app, url=target)

                app.make_button(row, "Join", command=join, padx=14, pady=5
                                ).pack(side="right", padx=(0, 4))
            elif kind == accounts.IN_STUDIO:
                tk.Label(row, text="studio", bg=BG_ACTIVE, fg=FG_DIM,
                         font=("TkDefaultFont", 10), padx=8
                         ).pack(side="right")
            else:
                tk.Label(row, text="", bg=BG_ACTIVE, width=6
                         ).pack(side="right")

    def load(refresh=False):
        status.configure(text="fetching account...", fg=FG_DIM)

        def worker():
            try:
                data = accounts.fetch_all(refresh=refresh)
                err = None
            except Exception as e:
                log.warning(f"Account page failed: {e}")
                data, err = None, str(e)

            def done():
                if err:
                    status.configure(text=err, fg=ERROR)
                    clear(card)
                    clear(accounts_frame)
                    clear(friends_frame)
                    return
                status.configure(text="", fg=FG_DIM)
                render(data)

            app.after(0, done)

        threading.Thread(target=worker, daemon=True).start()

    app.make_button(parent, "Refresh", command=lambda: load(refresh=True),
                     padx=14, pady=6).pack(anchor="w", padx=pad, pady=(0, 8))

    def on_page_shown(page_name):
        if page_name == "Account":
            load()

    try:
        app.page_shown_listeners.append(on_page_shown)
    except AttributeError:
        pass

    load()
