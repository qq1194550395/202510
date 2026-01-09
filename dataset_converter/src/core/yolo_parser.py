from pathlib import Path
from typing import List, Dict

from .base_parser import BaseParser, ImageAnnotation, BBox
from ..utils.file_utils import list_files_by_ext, find_image_by_stem
from PIL import Image


class YOLOParser(BaseParser):
    format_name = "yolo"
    _external_label_map: Dict[str, int] = {}

    def set_label_map(self, mapping: Dict[str, int]):
        self._external_label_map = dict(mapping or {})

    def parse(self, input_dir: Path) -> List[ImageAnnotation]:
        """
        解析标准目录结构的YOLO数据集:
        dataset/
        ├── images/
        │   ├── train/
        │   ├── test/
        │   └── val/
        └── labels/
            ├── train/
            ├── test/
            └── val/
        """
        results: List[ImageAnnotation] = []
        id_to_label = {v: k for k, v in self._external_label_map.items()} if self._external_label_map else {}
        
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
            
            # 获取所有标签文件
            txt_files = list_files_by_ext(label_subset_dir, [".txt"])
            
            for txt_file in txt_files:
                stem = txt_file.stem
                
                # 在对应的图片目录中查找同名图片
                img_file = self._find_image_in_dir(img_subset_dir, stem)
                if img_file is None:
                    continue
                
                try:
                    with Image.open(img_file) as im:
                        width, height = im.size
                except Exception:
                    width, height = 0, 0
                
                # 解析标注
                boxes: List[BBox] = []
                try:
                    for line in txt_file.read_text(encoding="utf-8").splitlines():
                        line = line.strip()
                        if not line:
                            continue
                        parts = line.split()
                        if len(parts) != 5:
                            continue
                        try:
                            cid = int(parts[0])
                            cx = float(parts[1])
                            cy = float(parts[2])
                            w = float(parts[3])
                            h = float(parts[4])
                        except ValueError:
                            continue
                        
                        label = id_to_label.get(cid, str(cid))
                        if width > 0 and height > 0:
                            # 反归一化：从中心点换算到像素框
                            box_w = w * width
                            box_h = h * height
                            x_center = cx * width
                            y_center = cy * height
                            xmin = int(round(x_center - box_w / 2.0))
                            ymin = int(round(y_center - box_h / 2.0))
                            xmax = int(round(x_center + box_w / 2.0))
                            ymax = int(round(y_center + box_h / 2.0))
                        else:
                            xmin = ymin = xmax = ymax = 0
                        boxes.append(BBox(xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax, label=label))
                except Exception:
                    # 标注文件读取失败，跳过
                    continue
                
                results.append(ImageAnnotation(image_path=img_file, width=width, height=height, boxes=boxes, polygons=None))
        
        return results
    
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
        将统一结构写出为 YOLO 格式：每张图片一个 .txt 文件，行格式：
        class_id cx cy w h （归一化到 [0,1]）。
        这里使用简单的 label→id 的映射：按出现顺序分配递增 id。
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        label_to_id: Dict[str, int] = dict(self._external_label_map)
        next_id = (max(label_to_id.values()) + 1) if label_to_id else 0
        for ann in annotations:
            if ann.width <= 0 or ann.height <= 0:
                # 缺少尺寸信息无法归一化，跳过写出
                continue
            txt_name = Path(ann.image_path).with_suffix(".txt").name or "annotations.txt"
            out_fp = output_dir / txt_name
            lines = []
            for b in ann.boxes:
                if b.label not in label_to_id:
                    label_to_id[b.label] = next_id
                    next_id += 1
                cid = label_to_id[b.label]
                # 像素框转 YOLO：中心点与宽高（归一化）
                x_center = ((b.xmin + b.xmax) / 2.0) / ann.width
                y_center = ((b.ymin + b.ymax) / 2.0) / ann.height
                w = (b.xmax - b.xmin) / ann.width
                h = (b.ymax - b.ymin) / ann.height
                lines.append(f"{cid} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}")
            out_fp.write_text("\n".join(lines), encoding="utf-8")