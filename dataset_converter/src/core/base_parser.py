from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any


@dataclass
class BBox:
    xmin: int
    ymin: int
    xmax: int
    ymax: int
    label: str


@dataclass
class ImageAnnotation:
    image_path: Path
    width: int
    height: int
    boxes: List[BBox]


class BaseParser:
    """统一解析器接口：解析目录为标准注释结构、并可导出。"""

    format_name: str = "base"

    def parse(self, input_dir: Path) -> List[ImageAnnotation]:
        raise NotImplementedError

    def export(self, annotations: List[ImageAnnotation], output_dir: Path) -> None:
        raise NotImplementedError