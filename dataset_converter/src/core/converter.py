from pathlib import Path
from typing import List, Dict, Optional

from .base_parser import BaseParser, ImageAnnotation
from .yolo_parser import YOLOParser
from .yolo_seg_parser import YOLOSegParser
from .voc_parser import VOCParser
from .json_parser import JSONParser


PARSERS: Dict[str, BaseParser] = {
    "yolo": YOLOParser(),
    "yolo_seg": YOLOSegParser(),
    "voc": VOCParser(),
    "json": JSONParser(),
}


def convert(input_dir: Path, input_format: str, output_dir: Path, output_format: str, label_map: Optional[Dict[str, int]] = None) -> None:
    if input_format not in PARSERS:
        raise ValueError(f"Unsupported input format: {input_format}")
    if output_format not in PARSERS:
        raise ValueError(f"Unsupported output format: {output_format}")

    # 先为解析器设置标签映射（如支持），以便在解析阶段将 id→label 反解
    parser = PARSERS[input_format]
    if hasattr(parser, "set_label_map") and label_map is not None:
        getattr(parser, "set_label_map")(label_map)

    annotations: List[ImageAnnotation] = parser.parse(input_dir)

    # 若导出器也支持标签映射（如 YOLO），同样传递以固定 label→id
    exporter = PARSERS[output_format]
    if hasattr(exporter, "set_label_map") and label_map is not None:
        getattr(exporter, "set_label_map")(label_map)
    exporter.export(annotations, output_dir)