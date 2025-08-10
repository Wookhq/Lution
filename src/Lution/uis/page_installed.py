import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib

from modules.config.genconfig import Config
from modules.marketplace.downloadandinstall import MarketplaceManager
from modules.utils.logging import log

@Gtk.Template(filename="files/uis/page_installed.ui")
class PageInstalled(Adw.PreferencesPage):
    __gtype_name__ = "PageInstalled"

    themes_expander = Gtk.Template.Child()
    themes_box = Gtk.Template.Child()
    mods_expander = Gtk.Template.Child()
    mods_box = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cf = Config()
        self.mm = MarketplaceManager()
        self.populate_installed_items()

    def populate_installed_items(self):
        self.clear_box(self.themes_box)
        self.clear_box(self.mods_box)

        installed_themes = self.cf.Read("marketplace", "InstalledThemes")
        if installed_themes:
            for theme in installed_themes.split(','):
                if theme:
                    self.add_item_to_box(self.themes_box, theme, "theme")

        installed_mods = self.cf.Read("marketplace", "InstalledMods")
        if installed_mods:
            for mod in installed_mods.split(','):
                if mod:
                    self.add_item_to_box(self.mods_box, mod, "mod")

    def clear_box(self, box):
        children = []
        for child in box:
            children.append(child)
        for child in children:
            box.remove(child)

    def add_item_to_box(self, box, item_name, item_type):
        item_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        label = Gtk.Label(label=item_name)
        item_box.append(label)

        apply_button = Gtk.Button(label="Apply")
        apply_button.connect("clicked", self.on_apply_button_clicked, item_name, item_type)
        item_box.append(apply_button)

        remove_button = Gtk.Button(label="Remove")
        remove_button.connect("clicked", self.on_remove_button_clicked, item_name, item_type)
        item_box.append(remove_button)

        box.append(item_box)

    def on_apply_button_clicked(self, button, item_name, item_type):
        log.info(f"Applying {item_name} of type {item_type}")
        self.mm.ApplyMarketplace(item_name, item_type)

    def on_remove_button_clicked(self, button, item_name, item_type):
        log.info(f"Removing {item_name} of type {item_type}")
        self.mm.RemoveMarketplace(item_name, item_type)
        self.populate_installed_items()
