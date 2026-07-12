# this for changing fps cap

from pathlib import Path
import xml.etree.ElementTree as ET

SOBER_APP_ID = "org.vinegarhq.Sober"
FPS_XML = (Path.home() / ".var/app" / SOBER_APP_ID /
           "data/sober/appData/GlobalBasicSettings_13.xml")


def load_framerate_cap():
    if not FPS_XML.exists():
        return None
    tree = ET.parse(FPS_XML)
    node = tree.getroot().find(".//int[@name='FramerateCap']")
    return node.text if node is not None else None


def save_framerate_cap(value):
    tree = ET.parse(FPS_XML)
    node = tree.getroot().find(".//int[@name='FramerateCap']")
    if node is None:
        raise ValueError("FramerateCap node not found in XML")
    node.text = str(value)
    tree.write(FPS_XML, xml_declaration=True, encoding="UTF-8")


def validate_digits(new_value):
    return new_value == "" or (new_value.isdigit() and len(new_value) <= 6)
