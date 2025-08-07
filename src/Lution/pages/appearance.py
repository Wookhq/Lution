import streamlit as st
from modules.utils.files import FilesFunctions
from modules.config.applyfun import ApplyFunctions
from modules.utils.lang import LANG
from modules.config.genconfig import Config
from modules.utils.logging import log
from modules.utils.sidebar import InitSidebar

InitSidebar()

ff = FilesFunctions()
cf = Config()
af = ApplyFunctions()

log.info('Page : Apperance')

ff.JsonSetup()
curcf = cf.Read("lution", "CursorType")

if "cursor" not in st.session_state:
    st.session_state.cursor = "Default"

if curcf == "Old 2007 Cursor":
    st.session_state.cursor = "Old 2007 Cursor"
elif curcf == "Old 2013 Cursor":
    st.session_state.cursor = "Old 2013 Cursor"

st.header(LANG["lution.tab.appearance"])


st.session_state.customfont = st.file_uploader(
    LANG["lution.appearance.uploader.customfont"],
    type=["ttf", "otf"],
    key="custom_font_uploader"
)
st.button(
    LANG["lution.appearance.button.applyfont"],
    on_click=lambda : ff.ApplyFont()
    )
st.session_state.cursor = st.selectbox(
        LANG["lution.appearance.mutichoices.cursor"],
        ["Default", "Old 2007 Cursor", "Old 2013 Cursor"],
        index=["Default", "Old 2007 Cursor", "Old 2013 Cursor"].index(st.session_state.cursor)
    )
st.button(
        LANG["lution.appearance.button.applycursor"],
        on_click=lambda: af.UpdateCursor(st.session_state.cursor),
        key="apply_cursor_button"
    )




st.markdown(LANG["lution.appearance.text.laucher"])
st.markdown("""
no im not gonna do that 
""")
