#src/sostrapter/modules/json/json.py
from modules.config.genconfig import Config
from modules.mod.fontreplacer import *
from modules.utils.files import FilesFunctions
from modules.utils.messages import STMessages
import os
genconfig = Config()
ff = FilesFunctions()

st = STMessages()

class ApplyFunctions:
    def __init__(self):
        pass

    def ApplyChanges(self,fpslimit, lightingtech, rpc1, rendertech, bbchat, fontsize, useoldrobloxsounds, disableprsh, texturequa, msaa):
        """Apply changes based on user input."""
        # Lighting Tech
        if lightingtech == "Voxel Lighting (Phase 1)" : 
            genconfig.UpdateFflags("DFFlagDebugRenderForceTechnologyVoxel",True)
            genconfig.UpdateFflags("FFlagDebugForceFutureIsBrightPhase2",False)
            genconfig.UpdateFflags("FFlagDebugForceFutureIsBrightPhase3",False)
        if lightingtech == "Shadowmap Lighting (Phase 2)" :
            genconfig.UpdateFflags("DFFlagDebugRenderForceTechnologyVoxel",False)
            genconfig.UpdateFflags("FFlagDebugForceFutureIsBrightPhase2",True)
            genconfig.UpdateFflags("FFlagDebugForceFutureIsBrightPhase3",False)
        if lightingtech == "Future Lighting (Phase 3)" :
            genconfig.UpdateFflags("DFFlagDebugRenderForceTechnologyVoxel",False)
            genconfig.UpdateFflags("FFlagDebugForceFutureIsBrightPhase2",False)
            genconfig.UpdateFflags("FFlagDebugForceFutureIsBrightPhase3",True)
        # Texture quality
        def chektexture(texturequa1):
            genconfig.UpdateFflags("DFFlagTextureQualityOverrideEnabled", True)
            match texturequa1:
                case "Off" :
                    genconfig.DeleteFflag("DFFlagTextureQualityOverrideEnabled")
                    genconfig.DeleteFflag("DFIntTextureQualityOverride")
                case "Level 0 (potato)":
                    genconfig.UpdateFflags("DFIntTextureQualityOverride", 0)
                case "Level 1 (Low)":
                    genconfig.UpdateFflags("DFIntTextureQualityOverride", 1)
                case "Level 2 (Medium)":
                    genconfig.UpdateFflags("DFIntTextureQualityOverride", 2)
                case "Level 3 (High)":
                    genconfig.UpdateFflags("DFIntTextureQualityOverride", 3)
                case "Level 4 (Ultra)":
                    genconfig.UpdateFflags("DFIntTextureQualityOverride", 4)
        chektexture(texturequa)
            # Texture quality
        def msaaapply(msaa1):
            genconfig.UpdateFflags("FFlagDebugDisableMSAA", False)
            match msaa1:
                case "Off" :
                    genconfig.UpdateFflags("DFFlagTextureQualityOverrideEnabled", True)
                    genconfig.DeleteFflag("FIntMSAASampleCount")
                case "x1":
                    genconfig.UpdateFflags("FIntMSAASampleCount", 1)
                case "x2":
                    genconfig.UpdateFflags("FIntMSAASampleCount", 2)
                case "x4":
                    genconfig.UpdateFflags("FIntMSAASampleCount", 4)
                case "Auto":
                    pass

        msaaapply(msaa)
        # FPS limit
        genconfig.UpdateFflags("DFIntTaskSchedulerTargetFps",fpslimit)
        genconfig.UpdateFflags("FFlagGameBasicSettingsFramerateCap5",True)
        genconfig.UpdateFflags("FFlagTaskSchedulerLimitTargetFpsTo2402",False)
        # Disnabel Discord RPC
        genconfig.UpdateSoberConfig("discord_rpc_enabled",rpc1)
        # Disable Player shadows
        if disableprsh == True :
            genconfig.UpdateFflags("FIntRenderShadowIntensity", "0")
            genconfig.Update("lution", "disableplayersh", True)
        else:
            genconfig.UpdateFflags("FIntRenderShadowIntensity", "75")
            genconfig.Update("lution","disableplayersh", False)
        # Render Technology
        if rendertech == "OpenGL":
            genconfig.UpdateSoberConfig("use_opengl", True)
        elif rendertech == "Vulkan":
            genconfig.UpdateSoberConfig("use_opengl", False)
        # Bubble Chat
        genconfig.UpdateFflags("FFlagEnableBubbleChatFromChatService", bbchat)
        # Font Size
        genconfig.UpdateFflags("FIntFontSizePadding", fontsize)

        # force Overwrite meshes
        ff.OverwriteFiles(
            os.path.expanduser("~/.var/app/org.vinegarhq.Sober/data/sober/asset_overlay/content/avatar/meshes/"),
            [
                os.path.abspath(os.path.join(os.path.dirname(__file__), "../../files/mesh/leftarm.mesh")),
                os.path.abspath(os.path.join(os.path.dirname(__file__), "../../files/mesh/rightarm.mesh")),
                os.path.abspath(os.path.join(os.path.dirname(__file__), "../../files/mesh/leftleg.mesh")),
                os.path.abspath(os.path.join(os.path.dirname(__file__), "../../files/mesh/rightleg.mesh")),
                os.path.abspath(os.path.join(os.path.dirname(__file__), "../../files/mesh/torso.mesh")),
            ]
        )
        # use old roblox sounds
        genconfig.Update("lution","OldRlbxSd",useoldrobloxsounds)
        if useoldrobloxsounds:
            ff.OverwriteFiles(
                os.path.expanduser("~/.var/app/org.vinegarhq.Sober/data/sober/asset_overlay/content/sounds/"),
                [
                    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../files/sounds/action_footsteps_plastic.mp3")),
                    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../files/sounds/action_get_up.mp3")),
                    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../files/sounds/action_jump.mp3")),
                    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../files/sounds/ouch.ogg")),
                ]
            )

    def Applyfflags(self, fflags):
        # FFlags Editor
        Currfflags = genconfig.ReadSoberConfig("fflags")
        Combine = genconfig.CombineJson(Currfflags, fflags)
        genconfig.UpdateSoberConfig("fflags", Combine)

    def LoadLightTechConfig(self):
        """Load Lighting techs Sober configs into session state."""
        Voxel = genconfig.ReadFflagsConfig("DFFlagDebugRenderForceTechnologyVoxel")
        Phase2 = genconfig.ReadFflagsConfig("FFlagDebugForceFutureIsBrightPhase2")
        Phase3 = genconfig.ReadFflagsConfig("FFlagDebugForceFutureIsBrightPhase3")
        if Voxel:
            return "Voxel Lighting (Phase 1)"
        elif Phase2:
            return "Shadowmap Lighting (Phase 2)"
        elif Phase3:
            return "Future Lighting (Phase 3)"
        else:
            return "Voxel Lighting (Phase 1)"  # Default fallback

    def LoadMSAA(self):
        flag = genconfig.ReadFflagsConfig("FFlagDebugDisableMSAA")
        flag2 = genconfig.ReadFflagsConfig("FIntMSAASampleCount")
        if flag == False:
            return "Off"
        else:
            match flag2 :
                case 1 :
                    return "x1"
                case 2 : 
                    return "x2"
                case 4 :
                    return "x4"
                case _:
                    return "Auto"
                
    def LoadTextureQuality(self):
        flag = genconfig.ReadFflagsConfig("DFIntTextureQualityOverride")
        match flag :
            case 0 :
                return "Level 0 (potato)"
            case 1 :
                return "Level 1 (Low)"
            case 2 :
                return "Level 2 (Medium)"    
            case 3 :
                return "Level 3 (High)"
            case 4 :
                return "Level 4 (Ultra)"
            case _:
                return "Off"

    def UsingOpenGl(self):
        """Load Render Tech from Sober config."""
        Open_gl = genconfig.ReadSoberConfig("use_opengl")
        if Open_gl:
            return True
        else:
            return False


    def UpdateCursor(self, cursortype):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../files"))
        CursorFolder = os.path.expanduser("~/.var/app/org.vinegarhq.Sober/data/sober/asset_overlay/content/textures/Cursors/KeyboardMouse")

        def cursor_file(*parts):
            return os.path.join(base_dir, *parts)

        if cursortype == "Default":
            ff.OverwriteFiles(
                CursorFolder,
                [
                    cursor_file("customcursor", "new", "ArrowCursor.png"),
                    cursor_file("customcursor", "new", "ArrowFarCursor.png"),
                    cursor_file("customcursor", "new", "IBeamCursor.png"),
                ]
            )
            genconfig.Update("lution","CursorType", "Default")
        elif cursortype == "Old 2007 Cursor":
            ff.OverwriteFiles(
                CursorFolder,
                [
                    cursor_file("customcursor", "old2006", "ArrowCursor.png"),
                    cursor_file("customcursor", "old2006", "ArrowFarCursor.png"),
                    cursor_file("customcursor", "old2006", "IBeamCursor.png"),
                ]
            )
            genconfig.Update("lution","CursorType", "Old 2007 Cursor")
        elif cursortype == "Old 2013 Cursor":
            ff.OverwriteFiles(
                CursorFolder,
                [
                    cursor_file("customcursor", "old2013", "ArrowCursor.png"),
                    cursor_file("customcursor", "old2013", "ArrowFarCursor.png"),
                    cursor_file("customcursor", "old2013", "IBeamCursor.png"),
                ]
            )
            genconfig.Update("lution","CursorType", "Old 2013 Cursor")
        else:
            st.error("Invalid cursor type selected.")
    
    def createdesktopentry(self):
        boostrap = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../boostrap.sh"))
        icon = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../files/lution1.png"))
        desktopentrydir = os.path.expanduser("~/.local/share/applications")
        os.makedirs(desktopentrydir, exist_ok=True)

        desktopentrypath = os.path.join(desktopentrydir, "Lution.desktop")

        entrycontent = f"""[Desktop Entry]
Name=Lution with sober
Exec={boostrap}
Icon={icon}
Type=Application
Categories=Utility;
Terminal=false
    """

        with open(desktopentrypath, 'w') as f:
            f.write(entrycontent)

        os.chmod(desktopentrypath, 0o755)  # make it executable
    
    def removedesktopentry(self):
        desktopentrydir = os.path.expanduser("~/.local/share/applications/Lution.desktop")
        if os.path.exists(desktopentrydir):
            os.remove(desktopentrydir)