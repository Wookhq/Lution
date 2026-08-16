# lution developed by wookhq uhh hello
import tkinter as tk
from tkinter import ttk, filedialog
from pathlib import Path
import subprocess
import json
import fflags
import fps
import fonts
import mods
import sys

BASE = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))

CONFIG_FILE = BASE / "ui.md"

BG = "#1e1e1e"
BG_SIDEBAR = "#161616"
BG_ACTIVE = "#2a2a2a"
FG = "#e0e0e0"
FG_DIM = "#888888"
ACCENT = "#8D7EDC"
ERROR = "#e06c75"
BODY_FONT = ("TkDefaultFont", 13)

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

        elif line == "FontPicker":
            if current is not None:
                pages[current].append(("fontpicker",))

        elif line == "ModManager":
            if current is not None:
                pages[current].append(("modmanager",))

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


class Lution(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Lution")
        self.configure(bg=BG)
        self.minsize(1280, 720)

        self.setup_style()

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.pages_config = parse_config(CONFIG_FILE)
        self.nav_buttons = {}
        self.pages = {}
        self.fflag_rows = []
        self.reload_fflags_ui = lambda: None

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
            btn.configure(bg=bg)
            if command:
                command()

        btn.bind("<ButtonPress-1>", on_press)
        btn.bind("<ButtonRelease-1>", on_release)
        return btn

# sidebar

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

    def build_content(self):
        self.container = tk.Frame(self, bg=BG)
        self.container.grid(row=0, column=1, sticky="nsew", padx=24, pady=20)
        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)

        for name, widgets in self.pages_config.items():
            page = self.build_page(name, widgets)
            page.grid(row=0, column=0, sticky="nsew")
            self.pages[name] = page

        if self.pages_config:
            self.show_page(next(iter(self.pages_config)))

    def build_page(self, name, widgets):
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

        def on_mousewheel(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        def on_linux_scroll_up(e):
            canvas.yview_scroll(-1, "units")
        def on_linux_scroll_down(e):
            canvas.yview_scroll(1, "units")

        canvas.bind_all("<MouseWheel>", on_mousewheel)
        canvas.bind_all("<Button-4>", on_linux_scroll_up)
        canvas.bind_all("<Button-5>", on_linux_scroll_down)

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

        for widget in widgets:
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

            elif kind == "flaglist":
                target = group if group is not None else page
                pad = 14 if group is not None else 0
                self.build_flaglist(target, pad)

            elif kind == "fpsinput":
                target = group if group is not None else page
                pad = 14 if group is not None else 0
                self.build_fpsinput(target, pad)

            elif kind == "fontpicker":
                target = group if group is not None else page
                pad = 14 if group is not None else 0
                self.build_fontpicker(target, pad)

            elif kind == "modmanager":
                target = group if group is not None else page
                pad = 14 if group is not None else 0
                self.build_modmanager(target, pad)

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

# fflags list

    def build_flaglist(self, parent, pad):
        list_frame = tk.Frame(parent, bg=parent["bg"])
        list_frame.pack(anchor="w", fill="x", padx=pad, pady=(0, 6))

        btn_row = tk.Frame(parent, bg=parent["bg"])
        btn_row.pack(anchor="w", fill="x", padx=pad, pady=(0, 14))

        def add_row(key="", value=""):
            row = tk.Frame(list_frame, bg=parent["bg"])
            row.pack(anchor="w", fill="x", pady=3)

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

            remove_btn = self.make_button(row, "x", command=lambda: remove_row(row),
                                           bg=BG_SIDEBAR, fg=FG_DIM,
                                           padx=10, pady=4)
            remove_btn.pack(side="left")

            self.fflag_rows.append((key_entry, value_entry, row))

        def remove_row(row):
            self.fflag_rows = [r for r in self.fflag_rows if r[2] is not row]
            row.destroy()

        def reload_rows():
            for w in list_frame.winfo_children():
                w.destroy()
            self.fflag_rows = []
            for key, value in fflags.get_fflags().items():
                add_row(key, str(value))

        def save_rows():
            new_fflags = {}
            for key_entry, value_entry, _ in self.fflag_rows:
                key = key_entry.get().strip()
                if not key:
                    continue
                new_fflags[key] = fflags.parse_value(value_entry.get())
            fflags.save_fflags(new_fflags)

        self.reload_fflags_ui = reload_rows

        self.make_button(btn_row, "Add Flag", command=add_row
                          ).pack(side="left", padx=(0, 6))
        self.make_button(btn_row, "Save Flags", command=save_rows
                          ).pack(side="left", padx=(0, 6))
        self.make_button(btn_row, "Paste JSON",
                          command=self.open_paste_json_window
                          ).pack(side="left")

        reload_rows()

    def open_paste_json_window(self):
        win = tk.Toplevel(self, bg=BG)
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
            self.reload_fflags_ui()
            win.destroy()

        btn_row = tk.Frame(win, bg=BG)
        btn_row.pack(anchor="w", padx=16, pady=(0, 16))
        self.make_button(btn_row, "Apply", command=apply_json).pack(side="left")

# fps cap

    def build_fpsinput(self, parent, pad):
        tk.Label(parent, text="Framerate cap", bg=parent["bg"], fg=FG,
                 font=BODY_FONT).pack(anchor="w", padx=pad, pady=(0, 2))

        vcmd = (self.register(fps.validate_digits), "%P")
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
        self.make_button(parent, "Save FPS Limit", command=save_command
                          ).pack(anchor="w", padx=pad, pady=(0, 14))

# fonts

    def build_fontpicker(self, parent, pad):
        fonts.apply_font_updates()

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

        self.make_button(row, "Browse", command=browse, padx=14, pady=8
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

        self.make_button(parent, "Apply Font", command=apply_font
                          ).pack(anchor="w", padx=pad, pady=(0, 6))

        def restore_default():
            removed = fonts.restore_fonts()
            if removed:
                status.configure(text="Default fonts restored.", fg=FG_DIM)
            else:
                status.configure(text="No custom font to restore.", fg=ERROR)

        self.make_button(parent, "Restore Default Fonts", command=restore_default,
                          bg=ERROR, fg="#0a0a0a"
                          ).pack(anchor="w", padx=pad, pady=(0, 6))

        tk.Label(parent,
                 text=("NOTE: If Sober updates and removes your font, reopen Lution and we'll reapply it automatically"),
                 bg=parent["bg"], fg=FG_DIM, font=("TkDefaultFont", 10),
                 anchor="w", wraplength=500, justify="left"
                 ).pack(anchor="w", padx=pad, pady=(0, 14))

# mods

    def build_modmanager(self, parent, pad):
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
            removed = mods.remove_mod_content()
            if removed:
                status.configure(
                    text=f"Removed: {', '.join(removed)} from overlay.", fg=FG_DIM)
            else:
                status.configure(text="Nothing to clean up vro", fg=ERROR)

        self.make_button(btn_row, "Import Mod", command=import_mod
                          ).pack(side="left", padx=(0, 6))
        self.make_button(btn_row, "Install mod", command=install_selected
                          ).pack(side="left", padx=(0, 6))
        self.make_button(btn_row, "Delete mod", command=remove_selected,
                          bg=ERROR, fg="#0a0a0a"
                          ).pack(side="left", padx=(0, 6))
        self.make_button(btn_row, "Delete all mods from Sober", command=cleanup_all,
                          bg=BG_SIDEBAR, fg=FG_DIM
                          ).pack(side="left")

        tk.Label(parent,
                 text=("Import mod .zip files, then install them. "
                       "and the zip file has to contain content/ and ExtraContent/ for the mod to work. "
                       "and it's okay if content/ and ExtraContent/ are inside another folder (only one layer deep)"
                       ". oh also, if you're wondering why is there no option to change cursors in lution, well mods can just do that too."),
                 bg=parent["bg"], fg=FG_DIM, font=("TkDefaultFont", 10),
                 anchor="w", wraplength=500, justify="left"
                 ).pack(anchor="w", padx=pad, pady=(0, 14))

        refresh_list()

    def show_page(self, name):
        self.current_page = name
        self.pages[name].tkraise()
        for btn in self.nav_buttons.values():
            self.refresh_button(btn)


if __name__ == "__main__":
    app = Lution()
    app.mainloop()
