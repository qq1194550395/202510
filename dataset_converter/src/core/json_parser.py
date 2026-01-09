import json
from pathlib import Path
from typing import List

from .base_parser import BaseParser, ImageAnnotation, BBox, Polygon


class JSONParser(BaseParser):
    format_name = "json"

    def parse(self, input_dir: Path) -> List[ImageAnnotation]:
        """
        解析标准目录结构的JSON数据集:
        dataset/
        ├── images/
        │   ├── train/
        │   ├── test/
        │   └── val/
        └── labels/
            ├── train/
            ├── test/
            └── val/
        
        支持两种 JSON 结构：
        1. 批量格式：{"images": [{"file_name": "...", "width": ..., "annotations": [...]}]}
        2. 单文件格式：{"file_name": "...", "width": ..., "annotations": [...]}
        """
        results: List[ImageAnnotation] = []
        
        # 检查标准目录结构
        images_dir = input_dir / "images"
        labels_dir = input_dir / "labels"
        
        if not images_dir.exists() or not labels_dir.exists():
            raise ValueError(f"数据集目录结构不正确。需要包含 'images' 和 'labels' 文件夹。\n当前目录: {input_dir}")
        
        # 处理所有子集 (train, test, val)
        subsets = ["train", "test", "val"]
        
        for subset in subsets:
            img_subset_dir = images_dir / subset
            label_subset_dir = labels_dir / subset
            
            # 如果子集目录不存在，跳过
            if not img_subset_dir.exists() or not label_subset_dir.exists():
                continue
            
            # 首先尝试读取 annotations.json (批量格式)
            batch_fp = label_subset_dir / "annotations.json"
            if batch_fp.exists():
                try:
                    data = json.loads(batch_fp.read_text(encoding="utf-8"))
                    images = data.get("images", [])
                    for im in images:
                        ann = self._parse_single_image(im, img_subset_dir)
                        if ann:
                            results.append(ann)
                except Exception:
                    pass
            
            # 然后扫描目录中的所有 .json 文件 (单文件格式)
            json_files = list(label_subset_dir.glob("*.json"))
            for json_file in json_files:
                if json_file.name == "annotations.json":
                    continue  # 跳过批量文件
                try:
                    data = json.loads(json_file.read_text(encoding="utf-8"))
                    ann = self._parse_single_image(data, img_subset_dir)
                    if ann:
                        results.append(ann)
                except Exception:
                    continue
        
        return results
    
    def _parse_single_image(self, im_data: dict, img_dir: Path = None) -> ImageAnnotation:
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
        
        # 构建完整的图片路径
        if file_name and img_dir:
            img_path = img_dir / file_name
            if not img_path.exists():
                # 如果指定的文件不存在，尝试查找同名文件
                stem = Path(file_name).stem
                img_path = self._find_image_in_dir(img_dir, stem)
                if img_path is None:
                    img_path = Path(file_name)  # 使用原始文件名
        else:
            img_path = Path(file_name) if file_name else Path("unknown.jpg")
        
        return ImageAnnotation(
            image_path=img_path,
            width=width, 
            height=height, 
            boxes=boxes, 
            polygons=polygons
        )
    
    def _find_image_in_dir(self, img_dir: Path, stem: str) -> Path:
        """在指定目录中查找同名图片文件"""
        exts = [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"]
        for ext in exts:
            img_path = img_dir / f"{stem}{ext}"
            if img_path.exists():
                return img_path
        return None

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