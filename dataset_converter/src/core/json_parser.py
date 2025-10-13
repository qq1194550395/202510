import json
from pathlib import Path
from typing import List

from .base_parser import BaseParser, ImageAnnotation, BBox


class JSONParser(BaseParser):
    format_name = "json"

    def parse(self, input_dir: Path) -> List[ImageAnnotation]:
        """
        期望的简单 JSON 结构：
        {
          "images": [
            {
              "file_name": "path/to/img.jpg",
              "width": 1920,
              "height": 1080,
              "annotations": [
                {"label": "cat", "bbox": [xmin, ymin, xmax, ymax]}
              ]
            }
          ]
        }
        """
        fp = Path(input_dir) / "annotations.json"
        if not fp.exists():
            return []
        data = json.loads(fp.read_text(encoding="utf-8"))
        images = data.get("images", [])
        results: List[ImageAnnotation] = []
        for im in images:
            file_name = im.get("file_name")
            width = int(im.get("width", 0))
            height = int(im.get("height", 0))
            annos = im.get("annotations", [])
            boxes: List[BBox] = []
            for a in annos:
                label = str(a.get("label", "")).strip()
                bbox = a.get("bbox", [0, 0, 0, 0])
                xmin, ymin, xmax, ymax = map(int, bbox)
                boxes.append(BBox(xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax, label=label))
            results.append(ImageAnnotation(image_path=Path(file_name) if file_name else Path(""),
                                           width=width, height=height, boxes=boxes))
        return results

    def export(self, annotations: List[ImageAnnotation], output_dir: Path) -> None:
        """
        导出为每张图片一个独立的 JSON 文件：<stem>.json。
        结构与单张图片条目一致，包含 file_name/width/height/annotations。
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        for ann in annotations:
            entry = {
                "file_name": str(ann.image_path),
                "width": ann.width,
                "height": ann.height,
                "annotations": [
                    {"label": b.label, "bbox": [b.xmin, b.ymin, b.xmax, b.ymax]} for b in ann.boxes
                ],
            }
            out_name = Path(ann.image_path).with_suffix(".json").name or "annotation.json"
            (output_dir / out_name).write_text(
                json.dumps(entry, ensure_ascii=False, indent=2), encoding="utf-8"
            )