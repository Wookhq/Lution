import streamlit as st
from modules.utils.logging import log
from modules.config.applyfun import ApplyFunctions
from modules.config.genconfig import Config
from modules.utils.lang import LANG
from modules.utils.sidebar import InitSidebar

cg = ApplyFunctions()
cf = Config()

InitSidebar()


def AppyAndUpdate():
    cg.ApplyChanges(
        st.session_state.fpslimit,
        st.session_state.lightingtech,
        st.session_state.rpc,
        st.session_state.render,
        st.session_state.disablechat,
        st.session_state.fontsize,
        st.session_state.useoldrobloxsounds,
        st.session_state.disableplayersh,
        st.session_state.texturequality,
        st.session_state.msaa,
    )
    Currfflags = cf.ReadSoberConfig("fflags")
    log.info("Applying changes...")
    st.session_state.fflagseditor = Currfflags


Currfflags = cf.ReadSoberConfig("fflags")
st.session_state.fflagseditor = Currfflags

left, mid, right = st.columns(3)
mid.button(
    LANG["lution.save.button.apply"],
    on_click=lambda: AppyAndUpdate(),
    key="apply_changes_button",
)
