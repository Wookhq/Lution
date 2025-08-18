import streamlit as st
import os
from modules.mod_generator import ModGenerator
from modules.mod_generator.dataclasses import GradientColor
from modules.utils.sidebar import InitSidebar

InitSidebar()

MG = ModGenerator

if "Color1" not in st.session_state:
    st.session_state["Color1"] = None
if "Color2" not in st.session_state:
    st.session_state["Color2"] = None
if "Stop1" not in st.session_state:
    st.session_state["Stop1"] = 0.0
if "Stop2" not in st.session_state:
    st.session_state["Stop2"] = 1.0
if "CustomLogo" not in st.session_state:
    st.session_state["CustomLogo"] = None


def hex_to_rgb(hex_code: str) -> tuple[int, int, int]:
    hex_code = hex_code.lstrip("#")
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))


@st.dialog("Mod Preview")
def verycool():
    if st.session_state.Color1 is None:
        return
    if gardient:
        gardientcolor = [
            GradientColor(color=hex_to_rgb(st.session_state.Color1), stop=st.session_state.Stop1),
            GradientColor(color=hex_to_rgb(st.session_state.Color2), stop=st.session_state.Stop2)
        ]
        if st.session_state.CustomLogo is not None:
            res = MG.generate_preview_image(mode="gradient", data=gardientcolor, custom_roblox_icon=st.session_state.CustomLogo)
        else:
            res = MG.generate_preview_image(mode="gradient", data=gardientcolor)
    else:
        color = hex_to_rgb(st.session_state.Color1)
        res = MG.generate_preview_image(mode="color", data=color)

    st.image(res, caption="Mod preview")


def verycooltoo():
    if st.session_state.Color1 is None:
        return

    out_dir = os.path.expanduser("~/Documents/Lution/Generated_mod")
    os.makedirs(out_dir, exist_ok=True)

    if gardient:
        gardientcolor = [
            GradientColor(color=hex_to_rgb(st.session_state.Color1), stop=st.session_state.Stop1),
            GradientColor(color=hex_to_rgb(st.session_state.Color2), stop=st.session_state.Stop2)
        ]
        if st.session_state.CustomLogo is not None:
            res = MG.generate_mod(mode="gradient", data=gardientcolor, custom_roblox_icon=st.session_state.CustomLogo, output_dir=out_dir)
        else:
            res = MG.generate_mod(mode="gradient", data=gardientcolor, output_dir=out_dir)
    else:
        color = hex_to_rgb(st.session_state.Color1)
        res = MG.generate_mod(mode="color", data=color, output_dir=out_dir)

    st.success(f"Mod generated at {out_dir}")


st.header("Mod Generator")
st.caption("please use this to generate mods only! don’t share generated mods because its cringy")


gardient = st.checkbox("Gradient ?")

st.session_state.Color1 = st.color_picker("Mod color")
if gardient:
    st.session_state.Color2 = st.color_picker("Mod color (Gradient Only)")
    st.session_state.Stop1 = float(st.session_state.Stop1)
    st.session_state.Stop2 = float(st.session_state.Stop2)

    st.session_state.Stop1 = st.number_input("Stop 1", value=st.session_state.Stop1, min_value=0.0, max_value=1.0, step=0.1)
    st.session_state.Stop2 = st.number_input("Stop 2", value=st.session_state.Stop2, min_value=0.0, max_value=1.0, step=0.1)

st.session_state.CustomLogo = st.file_uploader("Custom Logo", type=["png", "jpg", "jpeg"])

st.button("Preview", on_click=verycool)
st.button("Generate", on_click=verycooltoo)

