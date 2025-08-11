import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw
import json

from modules.mod.clientsettings import ClientSettings
from modules.utils.lang import LANG
from modules.utils.logging import log
from modules.utils.files import FilesFunctions
from modules.config.genconfig import Config
from modules.config.applyfun import ApplyFunctions

class PageFFlags(Adw.Bin):
    def __init__(self):
        super().__init__()
        self.cf = Config()
        self.ff = FilesFunctions()
        self.af = ApplyFunctions()
        self.cs = ClientSettings()

        try:
            builder = Gtk.Builder.new_from_file("files/uis/page_fflags.ui")
            self.root = builder.get_object("page_fflags")
            self.set_child(self.root)
        except Exception as e:
            log.error(f"Failed to load UI file: {e}")
            self.set_child(Gtk.Label(label="Error loading UI"))
            return

        self.oof_toggle = builder.get_object("oof_toggle")
        self.rpc_toggle = builder.get_object("rpc_toggle")
        self.fpslimit_entry = builder.get_object("fpslimit_entry")
        self.render_dropdown = builder.get_object("render_dropdown")
        self.lightingtech_dropdown = builder.get_object("lightingtech_dropdown")
        self.disablechat_toggle = builder.get_object("disablechat_toggle")
        self.disableplayersh_toggle = builder.get_object("disableplayersh_toggle")
        self.fontsize_entry = builder.get_object("fontsize_entry")
        self.msaa_dropdown = builder.get_object("msaa_dropdown")
        self.texturequality_dropdown = builder.get_object("texturequality_dropdown")
        self.fflags_textarea = builder.get_object("fflags_textarea")

        builder.get_object("applyfflags_button").connect("clicked", self.on_apply_clicked)
        builder.get_object("reseteditor_button").connect("clicked", self.on_reset_clicked)
        builder.get_object("setupoverlay_button").connect("clicked", self.on_setup_overlay_clicked)
        builder.get_object("apply_header_button").connect("clicked", self.on_apply_clicked)

        self.load_config()

    def load_config(self):
        # Load all configurations from files
        self.rpc = self.cf.ReadSoberConfig("discord_rpc_enabled") or False
        self.fpslimit = str(self.cf.ReadFflagsConfig("DFIntTaskSchedulerTargetFps") or "60")
        self.render = "OpenGL" if self.af.UsingOpenGl() else "Vulkan"
        self.oof_toggle.set_active(self.cf.ReadSoberConfig("bring_back_oof") or False)
        self.lightingtech = self.af.LoadLightTechConfig()
        self.disablechat = self.cf.ReadFflagsConfig("FFlagEnableBubbleChatFromChatService") or False
        self.disableplayersh = self.cf.Read("lution", "disableplayersh") or False
        self.useoldrobloxsounds = self.cf.Read("lution", "OldRlbxSd") or False
        self.fontsize = str(self.cf.ReadFflagsConfig("FIntFontSizePadding") or "1")
        self.msaa = self.af.LoadMSAA() or "Auto"
        self.texturequality = self.af.LoadTextureQuality() or "Level 2 (Medium)"
        self.fflagseditor = json.loads(self.cs.SplitClientSettingsContent() or "{}")

        # Update the UI widgets
        self.rpc_toggle.set_active(self.rpc)
        self.fpslimit_entry.set_text(self.fpslimit)
        self.render_dropdown.set_selected(0 if self.render == "OpenGL" else 1)
        self.lightingtech_dropdown.set_selected(["Voxel Lighting (Phase 1)", "Shadowmap Lighting (Phase 2)", "Future Lighting (Phase 3)"].index(self.lightingtech))
        self.disablechat_toggle.set_active(self.disablechat)
        self.disableplayersh_toggle.set_active(self.disableplayersh)
        self.fontsize_entry.set_text(self.fontsize)
        self.msaa_dropdown.set_selected(["Off","Auto","x1","x2","x4"].index(self.msaa))
        self.texturequality_dropdown.set_selected(["Off","Level 0 (potato)", "Level 1 (Low)","Level 2 (Medium)","Level 3 (High)","Level 4 (Ultra)"].index(self.texturequality))
        self.fflags_textarea.get_buffer().set_text(json.dumps(self.fflagseditor, indent=4))
        
    def on_apply_clicked(self, button):
            # 1. Get values from UI and validate them
            rpc_val = self.rpc_toggle.get_active()
            fpslimit_val = self.fpslimit_entry.get_text().strip()
            fontsize_val = self.fontsize_entry.get_text().strip()

            try:
                fpslimit_val_int = int(fpslimit_val)
                fontsize_val_int = int(fontsize_val)
            except ValueError:
                log.warn("Invalid FPS or font size value entered. Must be a number.")
                dialog = Adw.MessageDialog.new(self.get_child().get_root(), "Invalid Input", "FPS Limit and Font Size must be whole numbers.")
                dialog.add_response("ok", "OK")
                dialog.connect("response", lambda d, r: d.close())
                dialog.present()
                return

            render_val = self.render_dropdown.get_selected_item().get_string()
            lightingtech_val = self.lightingtech_dropdown.get_selected_item().get_string()
            disablechat_val = self.disablechat_toggle.get_active()
            disableplayersh_val = self.disableplayersh_toggle.get_active()
            msaa_val = self.msaa_dropdown.get_selected_item().get_string()
            texturequality_val = self.texturequality_dropdown.get_selected_item().get_string()
            # useoldrobloxsounds_val is likely not an fflag, so we can ignore it for the dictionary.

            # 2. Update the FFlags editor content
            fflags_text = self.fflags_textarea.get_buffer().get_text(
                self.fflags_textarea.get_buffer().get_start_iter(),
                self.fflags_textarea.get_buffer().get_end_iter(),
                False
            )

            try:
                # First, load the user's manual edits
                self.fflagseditor = json.loads(fflags_text)
            except json.JSONDecodeError as e:
                log.warn(f"Invalid fflags config: {e}")
                dialog = Adw.MessageDialog.new(self.get_child().get_root(), "Invalid FFlags", "The FFlags editor contains invalid JSON.")
                dialog.add_response("ok", "OK")
                dialog.connect("response", lambda d, r: d.close())
                dialog.present()
                return
            
            # Now, explicitly add/override values from the other UI controls
            self.fflagseditor["DFIntTaskSchedulerTargetFps"] = fpslimit_val_int
            self.fflagseditor["FIntFontSizePadding"] = fontsize_val_int
            # This is the key part that was missing: adding the other FFlags
            # These FFlag names are examples and might need to be verified.
            self.fflagseditor["FFlagEnableBubbleChatFromChatService"] = disablechat_val
            self.fflagseditor["DFFlagEnableExperimentalRenderDevice"] = True if render_val == "Vulkan" else False
            
            # Mapping the dropdown values to their respective FFlag names/values
            lightingtech_map = {
                "Voxel Lighting (Phase 1)": "Voxel", 
                "Shadowmap Lighting (Phase 2)": "ShadowMap", 
                "Future Lighting (Phase 3)": "Future"
            }
            self.fflagseditor["FFlagLightingTechnology"] = lightingtech_map.get(lightingtech_val)
            
            msaa_map = {
                "Off": 0, "Auto": 0, "x1": 1, "x2": 2, "x4": 4
            }
            self.fflagseditor["FFlagD3D11DisableMSAA"] = True if msaa_val == "Off" else False
            self.fflagseditor["FFlagD3D11MSAASamples"] = msaa_map.get(msaa_val)

            texturequality_map = {
                "Off": "Disabled", 
                "Level 0 (potato)": "Low", 
                "Level 1 (Low)": "Low",
                "Level 2 (Medium)": "Medium",
                "Level 3 (High)": "High",
                "Level 4 (Ultra)": "Ultra"
            }
            self.fflagseditor["FFlagTextureQuality"] = texturequality_map.get(texturequality_val)

            # 3. Apply the changes to the configuration files
            # The Applyfflags method should write the entire self.fflagseditor dictionary to the ClientSettings.json
            self.af.Applyfflags(self.fflagseditor)
            
            # You may want to keep this to handle non-fflag settings like discord RPC
            self.af.ApplyChanges(
                fpslimit_val,
                lightingtech_val,
                rpc_val,
                render_val,
                disablechat_val,
                fontsize_val,
                False, # This is a placeholder since we're now handling it differently.
                disableplayersh_val,
                texturequality_val,
                msaa_val
            )
            
            # 4. Reload the configuration to update the GUI
            self.load_config()

    def on_reset_clicked(self, button):
        self.load_config()

    def on_setup_overlay_clicked(self, button):
        self.ff.OverlaySetup()
        dialog = Adw.MessageDialog.new(self.get_child().get_root(), LANG["lution.dialog.overlay.title"], LANG["lution.dialog.overlay.body"])
        dialog.add_response("ok", "OK")
        dialog.connect("response", lambda d, r: d.close())
        dialog.present()