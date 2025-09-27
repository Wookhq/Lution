import streamlit as st
import os
from modules.utils.files import FilesFunctions
from modules.utils.lang import LANG
from modules.utils.logging import log
from modules.utils.sidebar import InitSidebar

InitSidebar()

log.info("Page : Mods")

ff = FilesFunctions()


st.header(LANG["lution.tab.mods"])
st.session_state.useoldrobloxsounds = st.toggle(
    LANG["lution.mods.toggle.useoldsound"],
    value=st.session_state.useoldrobloxsounds,
    key="toogle old roblox sounds",
)

mods = os.path.expanduser("~/Documents/Lution/Mods")
st.button(
    LANG["lution.mods.button.openmods"],
    on_click=lambda: ff.ModsFolder(),
    key="mod_button",
)
st.caption(LANG["lution.mods.caption.bloxstrapsupport"])
st.button(
    LANG["lution.mods.button.applymods"],
    on_click=lambda: ff.ApplyMods(),
    key="apply_mods_button",
)

st.button(
    LANG["lution.mods.button.resetmods"],
    on_click=lambda: ff.ResetMods(),
    key="reset_mods_button",
)

# yay
