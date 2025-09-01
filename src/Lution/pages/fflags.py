import streamlit as st
import json
from modules.mod.clientsettings import ClientSettings
from modules.utils.lang import LANG
from modules.utils.logging import log
from modules.utils.files import FilesFunctions
from modules.config.genconfig import Config
from modules.config.applyfun import ApplyFunctions
from modules.utils.sidebar import InitSidebar

InitSidebar()

cf = Config()
ff = FilesFunctions()
af = ApplyFunctions()
cs = ClientSettings()

log.info("Page : Fflags")

gen, log = st.tabs(["Genaral Fflags", "Player logs/Chat logs"])


with gen:
    st.header(LANG["lution.tab.fflags"])
    st.session_state.rpc = st.toggle(LANG["lution.fflags.toggle.rpc"], value=st.session_state.rpc)
    st.session_state.fpslimit = st.text_input(LANG["lution.fflags.textbox.fpslimit"], st.session_state.fpslimit, max_chars=3)
    st.session_state.render = st.selectbox(
        LANG["lution.fflags.mutichoices.render"],
        ["OpenGL", "Vulkan"],
        index=0 if st.session_state.render else 1
    )
    st.session_state.lightingtech = st.selectbox(
        LANG["lution.fflags.mutichoices.lighting"],
        ["Voxel Lighting (Phase 1)", "Shadowmap Lighting (Phase 2)", "Future Lighting (Phase 3)"],
        index=["Voxel Lighting (Phase 1)", "Shadowmap Lighting (Phase 2)", "Future Lighting (Phase 3)"].index(st.session_state.lightingtech)
    )
    # fflags presets
    st.write("fflags presets")
    st.session_state.disablechat = st.toggle(LANG["lution.fflags.toggle.bbchat"], value=st.session_state.disablechat)
    st.toggle("Disable player shadows", value=st.session_state.disableplayersh)
    st.session_state.fontsize = st.text_input(LANG["lution.appearance.textbox.fontsize"], value=st.session_state.fontsize, max_chars=2)
    st.session_state.msaa = st.selectbox(
        "MSSA (Multisample Anti-Aliasing)",
        ["Off","Auto","x1","x2","x4"],
        index=["Off","Auto","x1","x2","x4"].index(st.session_state.msaa)
    )
    st.caption("NOTE : Not all devices respect MSAA, and some GPUs may still auto-adjust. The flag works best on Windows with Direct3D.")
    st.session_state.texturequality = st.selectbox(
        "Texture quality",
        ["Off","Level 0 (potato)", "Level 1 (Low)","Level 2 (Medium)","Level 3 (High)","Level 4 (Ultra)"],
        index=["Off","Level 0 (potato)", "Level 1 (Low)","Level 2 (Medium)","Level 3 (High)","Level 4 (Ultra)"].index(st.session_state.texturequality)
    )

    # advanded
    st.write(LANG["lution.fflags.text.advanded"])


    def reload_fflags():
        st.session_state.fflagseditor = json.loads(cs.SplitClientSettingsContent() or "{}")
        st.session_state.fflags_text = json.dumps(st.session_state.fflagseditor, indent=4)

    st.button(LANG["lution.fflags.button.reloadfflag"], on_click=reload_fflags)

    # fflags editor
    if "fflags_text" not in st.session_state:
        st.session_state.fflags_text = json.dumps(st.session_state.fflagseditor, indent=4)

    fflags_text = st.text_area(
        LANG["lution.fflags.texterea.fflagseditor"],
        value=st.session_state.fflags_text,
        height=400
    )

    try:
        parsed = json.loads(fflags_text)
        st.session_state.fflagseditor = parsed
        print(st.session_state.fflagseditor)
    except Exception:
        log.warn("Invalid fflags config")
        st.warning(LANG["lution.message.warning.fflags.invalid"])

    lf, mid ,rgt = st.columns(3)
    st.caption("The fflags editor slow to update with the config, recommend restart lution then try again")
    with mid:
        st.button(
            "Apply FFlags",
            on_click=lambda : af.Applyfflags(st.session_state.fflagseditor),
            use_container_width=True
        )

    st.write(LANG["lution.fflags.text.mics"])
    st.button(
        LANG["lution.fflags.button.setupoverlay"],
        on_click=ff.OverlaySetup
    )

with log:
    st.header("Player Log / Player Chat Log")
    st.write("To order to use this feature, you have to create a desktop shortcut to Lution.")

    st.session_state.plrlogs = st.toggle(
        "Turn on",
        value=st.session_state.plrlogs
    )
    if st.session_state.plrlogs:
        lf, mid ,rgt = st.columns(3)
        with lf:
            st.button("Setup")
        with mid:
            st.button("Remove")