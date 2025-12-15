from pathlib import Path
from typing import List

from .base_parser import BaseParser, ImageAnnotation
from ..utils.xml_utils import read_xml


class VOCParser(BaseParser):
    format_name = "voc"

    def parse(self, input_dir: Path) -> List[ImageAnnotation]:
        # 占位：读取 XML 标注，示例返回空
        _ = read_xml(Path(input_dir) / "sample.xml")
        return []

    def export(self, annotations: List[ImageAnnotation], output_dir: Path) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        # 占位：写出 VOC XML（注意：VOC格式不支持分割标注，只导出矩形框）
        for ann in annotations:
            # 只处理矩形框，忽略分割标注
            for _ in ann.boxes:
                pass