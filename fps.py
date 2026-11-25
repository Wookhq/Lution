# this for changing fps cap simple enough

from pathlib import Path
import io
import xml.etree.ElementTree as ET

import atomic

SOBER_APP_ID = "org.vinegarhq.Sober"
FPS_XML = (Path.home() / ".var/app" / SOBER_APP_ID /
           "data/sober/appData/GlobalBasicSettings_13.xml")


def load_framerate_cap():
    if not FPS_XML.exists():
        return None
    try:
        tree = ET.parse(FPS_XML)
    except (ET.ParseError, OSError):
        return None
    node = tree.getroot().find(".//int[@name='FramerateCap']")
    return node.text if node is not None else None


def save_framerate_cap(value):
    if not FPS_XML.exists():
        raise ValueError(
            "Sober hasn't written its settings file yet - open Roblox once, "
            "set the in-game cap to 60, close it, then try again")
    tree = ET.parse(FPS_XML)
    node = tree.getroot().find(".//int[@name='FramerateCap']")
    if node is None:
        raise ValueError("FramerateCap node not found in XML")
    node.text = str(value)
    buffer = io.BytesIO()
    tree.write(buffer, xml_declaration=True, encoding="UTF-8")
    atomic.write_bytes(FPS_XML, buffer.getvalue())


def validate_digits(new_value):
    return new_value == "" or (new_value.isdigit() and len(new_value) <= 6)
