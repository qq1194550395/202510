from pathlib import Path
from typing import List

from .base_parser import BaseParser, ImageAnnotation
from ..utils.xml_utils import read_xml


class VOCParser(BaseParser):
    format_name = "voc"

    def parse(self, input_dir: Path) -> List[ImageAnnotation]:
        """
        解析标准目录结构的VOC数据集:
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
            
            # 获取所有XML标签文件
            xml_files = list(label_subset_dir.glob("*.xml"))
            
            for xml_file in xml_files:
                stem = xml_file.stem
                
                # 在对应的图片目录中查找同名图片
                img_file = self._find_image_in_dir(img_subset_dir, stem)
                if img_file is None:
                    continue
                
                try:
                    # 解析XML文件 (这里需要实现XML解析逻辑)
                    annotation_data = read_xml(xml_file)
                    
                    # 获取图片尺寸
                    try:
                        from PIL import Image
                        with Image.open(img_file) as im:
                            width, height = im.size
                    except Exception:
                        width, height = 0, 0
                    
                    # 这里应该根据XML内容创建BBox对象
                    # 暂时返回空的标注作为占位符
                    boxes = []
                    
                    results.append(ImageAnnotation(
                        image_path=img_file, 
                        width=width, 
                        height=height, 
                        boxes=boxes,
                        polygons=None
                    ))
                    
                except Exception:
                    # XML解析失败，跳过
                    continue
        
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
        output_dir.mkdir(parents=True, exist_ok=True)
        # 占位：写出 VOC XML（注意：VOC格式不支持分割标注，只导出矩形框）
        for ann in annotations:
            # 只处理矩形框，忽略分割标注
            for _ in ann.boxes:
                pass