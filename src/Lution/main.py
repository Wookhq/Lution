# src/Lution/app.py
import streamlit as st
import os
import json
from modules.config.genconfig import Config
from modules.utils.sidebar import InitSidebar
from modules.utils.logging import log
from modules.config.applyfun import ApplyFunctions
from modules.mod.clientsettings import ClientSettings

InitSidebar()

file_path = os.path.expanduser(
    "~/.var/app/org.vinegarhq.Sober/config/sober/config.json"
)

log.info("Page : Home")

cg = Config()
cg.ConvertOldConfigs()
af = ApplyFunctions()
client_settings = ClientSettings()

# Set default values so they're always defined
if "fpslimit" not in st.session_state:
    log.info("Reading fpslimit")
    fpslimit = cg.ReadFflagsConfig("DFIntTaskSchedulerTargetFps")
    st.session_state.fpslimit = fpslimit
if "lightingtech" not in st.session_state:
    log.info("Reading Lighting technology")
    tech = af.LoadLightTechConfig()
    st.session_state.lightingtech = tech
if "texturequality" not in st.session_state:
    log.info("Reading Texture Quality")
    qua = af.LoadTextureQuality()
    st.session_state.texturequality = qua
if "mssa" not in st.session_state:
    log.info("Reading msaa")
    msaa = af.LoadMSAA()
    st.session_state.msaa = msaa
if "rpc" not in st.session_state:
    log.info("Reading Discord RPC")
    drpc = cg.ReadSoberConfig("discord_rpc_enabled")
    st.session_state.rpc = drpc
if "render" not in st.session_state:
    log.info("Reading Render technology")
    st.session_state.render = af.UsingOpenGl()
if "disablechat" not in st.session_state:
    log.info("Reading FFlag Disnable chat service")
    disablechat = cg.ReadFflagsConfig("FFlagEnableBubbleChatFromChatService")
    st.session_state.disablechat = disablechat
if "customfont" not in st.session_state:
    log.info("Reading custom font")
    st.session_state.customfont = None
if "language" not in st.session_state:
    log.info("Reading language")
    st.session_state.language = "en"
if "plrlogs" not in st.session_state:
    log.info("Reading language")
    zf = cg.Read("lution", "plrlogs")
    if zf is None:
        st.session_state.plrlogs = False
    else:
        st.session_state.plrlogs = zf
if "fflagseditor" not in st.session_state:
    log.info("Reading FFlags editor")
    spilted = client_settings.SplitClientSettingsContent()
    Currfflags = json.loads(spilted or "{}")
    st.session_state.fflagseditor = Currfflags
if "fontsize" not in st.session_state:
    log.info("Reading FFlag Fon size")
    st.session_state.fontsize = cg.ReadFflagsConfig("FIntFontSizePadding")
if "disableplayersh" not in st.session_state:
    log.info("Reading Disnable player shadows")
    dis = cg.Read("lution", "disableplayersh")
    if dis == None:
        st.session_state.disableplayersh = False
    else:
        st.session_state.disableplayersh = dis
if "useoldrobloxsounds" not in st.session_state:
    log.info("Reading Old roblox sounds")
    a = cg.Read("lution", "OldRlbxSd")
    if a is None:
        a = False
    st.session_state.useoldrobloxsounds = a


@st.dialog("Hey there!")
def notice():
    st.markdown(
        """# announcing *open alpha* release of **silver**- a rewritten version of lution in electron
you can get the dev build of silver [here](<https://github.com/Wookhq/silverr/actions/runs/18010305630>)
although this is not stable but if you want you can try it

## what about lution?
while chip is working on silver, lution is now maintained by @anamelessdude1

# docs for silver coming soon (build from source etc)
# STAR IT
"""
    )


if "notice" not in st.session_state:
    notice()
    st.session_state.notice = "done"


@st.dialog("Dialog")
def whatsnew():
    with open("./markdown/whatsnew.md", "r") as f:
        st.markdown(f.read())


st.header("Welcome to Lution!")
st.image("files/cooked.png")
if st.button("What's new?"):
    whatsnew()
st.write("Lution is a bootstrapper for Sober. Try out one of the features!")
st.write("Thank you for using Lution!")
st.write("-- Lution dev team")
