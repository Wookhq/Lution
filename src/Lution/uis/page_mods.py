import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio

from modules.utils.files import FilesFunctions
from modules.utils.lang import LANG
from modules.utils.logging import log
from modules.config.applyfun import ApplyFunctions
from modules.config.genconfig import Config

@Gtk.Template(filename="uis/page_mods.ui")
class PageMods(Adw.PreferencesPage):
    __gtype_name__ = "PageMods"

    switch_use_old_sounds = Gtk.Template.Child()
    btn_open_mods = Gtk.Template.Child()
    btn_apply_mods = Gtk.Template.Child()
    btn_reset_mods = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        log.info("Page : Mods")
        self.ff = FilesFunctions()
        self.af = ApplyFunctions()
        self.cg = Config()

        self.switch_use_old_sounds.set_active(self.cg.Read("lution", "OldRlbxSd") or False)
        self.switch_use_old_sounds.connect("notify::active", self.on_switch_use_old_sounds_toggled)

        self.btn_open_mods.connect("clicked", lambda btn: self.ff.ModsFolder())
        self.btn_apply_mods.connect("clicked", lambda btn: self.ff.ApplyMods())
        self.btn_reset_mods.connect("clicked", lambda btn: self.ff.ResetMods())
        
    def on_switch_use_old_sounds_toggled(self, switch, gparam):
        self.cg.Update("lution", "OldRlbxSd", switch.get_active())
        self.af.ApplyChanges(
            fpslimit=None, 
            lightingtech=None, 
            rpc1=None, 
            rendertech=None, 
            bbchat=None, 
            fontsize=None, 
            useoldrobloxsounds=switch.get_active(), 
            disableprsh=None, 
            texturequa=None, 
            msaa=None
        )