from pathlib import Path
from typing import List, Dict

from .base_parser import BaseParser, ImageAnnotation, BBox, Polygon
from ..utils.file_utils import list_files_by_ext, find_image_by_stem
from PIL import Image


class YOLOSegParser(BaseParser):
    """YOLO分割格式解析器，支持多边形标注"""
    format_name = "yolo_seg"
    _external_label_map: Dict[str, int] = {}

    def set_label_map(self, mapping: Dict[str, int]):
        self._external_label_map = dict(mapping or {})

    def parse(self, input_dir: Path) -> List[ImageAnnotation]:
        txt_files = list_files_by_ext(input_dir, [".txt"])
        id_to_label = {v: k for k, v in self._external_label_map.items()} if self._external_label_map else {}
        results: List[ImageAnnotation] = []
        
        for txt in txt_files:
            stem = txt.stem
            img_fp = find_image_by_stem(txt.parent, stem)
            if img_fp is None:
                continue
                
            try:
                with Image.open(img_fp) as im:
                    width, height = im.size
            except Exception:
                width, height = 0, 0

            boxes: List[BBox] = []
            polygons: List[Polygon] = []
            
            for line in txt.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                    
                parts = line.split()
                if len(parts) < 5:
                    continue
                    
                try:
                    cid = int(parts[0])
                    label = id_to_label.get(cid, str(cid))
                    
                    if len(parts) == 5:
                        # 目标检测格式: class cx cy w h
                        cx = float(parts[1])
                        cy = float(parts[2])
                        w = float(parts[3])
                        h = float(parts[4])
                        
                        if width > 0 and height > 0:
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
                        
                    else:
                        # 分割格式: class x1 y1 x2 y2 ... xn yn
                        coords = [float(x) for x in parts[1:]]
                        if len(coords) % 2 == 0 and len(coords) >= 6:  # 至少3个点
                            polygons.append(Polygon(points=coords, label=label))
                            
                except ValueError:
                    continue

            results.append(ImageAnnotation(
                image_path=img_fp, 
                width=width, 
                height=height, 
                boxes=boxes,
                polygons=polygons
            ))
            
        return results

    def export(self, annotations: List[ImageAnnotation], output_dir: Path) -> None:
        """导出为YOLO分割格式"""
        output_dir.mkdir(parents=True, exist_ok=True)
        label_to_id: Dict[str, int] = dict(self._external_label_map)
        next_id = (max(label_to_id.values()) + 1) if label_to_id else 0
        
        for ann in annotations:
            # 跳过没有尺寸信息的标注（但允许只有多边形的情况）
            if ann.width <= 0 or ann.height <= 0:
                # 如果有多边形但没有尺寸信息，使用默认尺寸
                if ann.polygons:
                    print(f"警告: 图片 {ann.image_path} 缺少尺寸信息，使用默认尺寸 800x600")
                    ann.width = 800
                    ann.height = 600
                else:
                    continue
                
            # 从图片路径提取文件名，生成对应的txt文件名
            if ann.image_path and ann.image_path != Path("") and ann.image_path.name:
                txt_name = Path(ann.image_path).stem + ".txt"
            else:
                txt_name = "annotation.txt"
            
            out_fp = output_dir / txt_name
            lines = []
            
            # 导出矩形框
            for b in ann.boxes:
                if b.label not in label_to_id:
                    label_to_id[b.label] = next_id
                    next_id += 1
                cid = label_to_id[b.label]
                
                x_center = ((b.xmin + b.xmax) / 2.0) / ann.width
                y_center = ((b.ymin + b.ymax) / 2.0) / ann.height
                w = (b.xmax - b.xmin) / ann.width
                h = (b.ymax - b.ymin) / ann.height
                lines.append(f"{cid} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}")
            
            # 导出多边形
            if ann.polygons:
                for poly in ann.polygons:
                    if poly.label not in label_to_id:
                        label_to_id[poly.label] = next_id
                        next_id += 1
                    cid = label_to_id[poly.label]
                    
                    coords_str = " ".join(f"{coord:.6f}" for coord in poly.points)
                    lines.append(f"{cid} {coords_str}")
            
            # 只有在有标注的情况下才写文件
            if lines:
                out_fp.write_text("\n".join(lines), encoding="utf-8")
                print(f"已生成文件: {out_fp} ({len(lines)} 行标注)")