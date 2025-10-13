from pathlib import Path
from typing import Optional

from lxml import etree


def read_xml(file_path: Path) -> Optional[etree._ElementTree]:
    try:
        with open(file_path, "rb") as f:
            return etree.parse(f)
    except Exception:
        return None


def write_xml(root: etree._Element, file_path: Path) -> None:
    tree = etree.ElementTree(root)
    tree.write(str(file_path), pretty_print=True, xml_declaration=True, encoding="utf-8")