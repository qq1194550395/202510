import json
from pathlib import Path
from typing import List

from .base_parser import BaseParser, ImageAnnotation, BBox, Polygon


class JSONParser(BaseParser):
    format_name = "json"

    def parse(self, input_dir: Path) -> List[ImageAnnotation]:
        """
        支持两种 JSON 结构：
        1. 批量格式：{"images": [{"file_name": "...", "width": ..., "annotations": [...]}]}
        2. 单文件格式：{"file_name": "...", "width": ..., "annotations": [...]}
        """
        results: List[ImageAnnotation] = []
        
        # 首先尝试读取 annotations.json (批量格式)
        batch_fp = Path(input_dir) / "annotations.json"
        if batch_fp.exists():
            data = json.loads(batch_fp.read_text(encoding="utf-8"))
            images = data.get("images", [])
            for im in images:
                ann = self._parse_single_image(im)
                if ann:
                    results.append(ann)
        
        # 然后扫描目录中的所有 .json 文件 (单文件格式)
        json_files = list(Path(input_dir).glob("*.json"))
        for json_file in json_files:
            if json_file.name == "annotations.json":
                continue  # 跳过批量文件
            try:
                data = json.loads(json_file.read_text(encoding="utf-8"))
                ann = self._parse_single_image(data)
                if ann:
                    results.append(ann)
            except Exception:
                continue
        
        return results
    
    def _parse_single_image(self, im_data: dict) -> ImageAnnotation:
        """解析单个图片的标注数据"""
        file_name = im_data.get("file_name")
        width = int(im_data.get("width", 0))
        height = int(im_data.get("height", 0))
        annos = im_data.get("annotations", [])
        boxes: List[BBox] = []
        polygons: List[Polygon] = []
        
        for a in annos:
            label = str(a.get("label", "")).strip()
            if "bbox" in a:
                bbox = a.get("bbox", [0, 0, 0, 0])
                xmin, ymin, xmax, ymax = map(int, bbox)
                boxes.append(BBox(xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax, label=label))
            elif "polygon" in a:
                polygon = a.get("polygon", [])
                if len(polygon) >= 6 and len(polygon) % 2 == 0:
                    polygons.append(Polygon(points=polygon, label=label))
        
        # 确保返回有效的ImageAnnotation，即使没有file_name
        if not file_name:
            file_name = "unknown.jpg"
        
        return ImageAnnotation(
            image_path=Path(file_name),
            width=width, 
            height=height, 
            boxes=boxes, 
            polygons=polygons
        )

    def export(self, annotations: List[ImageAnnotation], output_dir: Path) -> None:
        """
        导出为每张图片一个独立的 JSON 文件：<stem>.json。
        结构与单张图片条目一致，包含 file_name/width/height/annotations。
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        for ann in annotations:
            annotations_list = []
            # 添加矩形框标注
            for b in ann.boxes:
                annotations_list.append({"label": b.label, "bbox": [b.xmin, b.ymin, b.xmax, b.ymax]})
            # 添加分割标注
            if ann.polygons:
                for p in ann.polygons:
                    annotations_list.append({"label": p.label, "polygon": p.points})
            
            entry = {
                "file_name": str(ann.image_path),
                "width": ann.width,
                "height": ann.height,
                "annotations": annotations_list,
            }
            out_name = Path(ann.image_path).with_suffix(".json").name or "annotation.json"
            (output_dir / out_name).write_text(
                json.dumps(entry, ensure_ascii=False, indent=2), encoding="utf-8"
            )