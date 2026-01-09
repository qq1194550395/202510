"""
数据集格式验证器
"""
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json


class DatasetValidator:
    """数据集格式验证器"""
    
    @staticmethod
    def validate_dataset_structure(dataset_path: Path) -> Tuple[bool, str, Dict]:
        """
        验证数据集是否符合标准目录结构
        
        返回: (是否有效, 错误信息, 统计信息)
        """
        if not dataset_path.exists():
            return False, f"数据集路径不存在: {dataset_path}", {}
        
        if not dataset_path.is_dir():
            return False, f"数据集路径不是目录: {dataset_path}", {}
        
        # 检查必需的目录结构
        images_dir = dataset_path / "images"
        labels_dir = dataset_path / "labels"
        
        if not images_dir.exists():
            return False, "缺少 'images' 目录", {}
        
        if not labels_dir.exists():
            return False, "缺少 'labels' 目录", {}
        
        # 检查子集目录
        subsets = ["train", "test", "val"]
        found_subsets = []
        stats = {
            "total_images": 0,
            "total_labels": 0,
            "subsets": {},
            "image_formats": set(),
            "label_formats": set()
        }
        
        for subset in subsets:
            img_subset = images_dir / subset
            label_subset = labels_dir / subset
            
            if img_subset.exists() and label_subset.exists():
                found_subsets.append(subset)
                
                # 统计图片和标签文件
                img_files = list(img_subset.glob("*"))
                img_files = [f for f in img_files if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']]
                
                label_files = list(label_subset.glob("*"))
                label_files = [f for f in label_files if f.is_file() and f.suffix.lower() in ['.txt', '.xml', '.json']]
                
                stats["subsets"][subset] = {
                    "images": len(img_files),
                    "labels": len(label_files)
                }
                
                stats["total_images"] += len(img_files)
                stats["total_labels"] += len(label_files)
                
                # 记录文件格式
                for img in img_files:
                    stats["image_formats"].add(img.suffix.lower())
                for label in label_files:
                    stats["label_formats"].add(label.suffix.lower())
        
        if not found_subsets:
            return False, "未找到有效的子集目录 (train/test/val)", stats
        
        # 转换set为list以便JSON序列化
        stats["image_formats"] = list(stats["image_formats"])
        stats["label_formats"] = list(stats["label_formats"])
        
        success_msg = f"数据集结构有效。找到子集: {', '.join(found_subsets)}"
        return True, success_msg, stats
    
    @staticmethod
    def detect_dataset_format(dataset_path: Path) -> Optional[str]:
        """
        自动检测数据集格式
        
        返回: 格式名称 (yolo, yolo_seg, voc, json) 或 None
        """
        labels_dir = dataset_path / "labels"
        if not labels_dir.exists():
            return None
        
        # 检查所有子集目录
        subsets = ["train", "test", "val"]
        format_votes = {"yolo": 0, "yolo_seg": 0, "voc": 0, "json": 0}
        
        for subset in subsets:
            label_subset = labels_dir / subset
            if not label_subset.exists():
                continue
            
            # 检查文件扩展名
            txt_files = list(label_subset.glob("*.txt"))
            xml_files = list(label_subset.glob("*.xml"))
            json_files = list(label_subset.glob("*.json"))
            
            if xml_files:
                format_votes["voc"] += len(xml_files)
            
            if json_files:
                format_votes["json"] += len(json_files)
            
            if txt_files:
                # 检查txt文件内容来区分yolo和yolo_seg
                for txt_file in txt_files[:5]:  # 只检查前5个文件
                    try:
                        content = txt_file.read_text(encoding="utf-8").strip()
                        if not content:
                            continue
                        
                        lines = content.split('\n')
                        for line in lines[:3]:  # 只检查前3行
                            parts = line.strip().split()
                            if len(parts) == 5:
                                format_votes["yolo"] += 1
                            elif len(parts) > 5:
                                format_votes["yolo_seg"] += 1
                    except Exception:
                        continue
        
        # 返回得票最多的格式
        if max(format_votes.values()) == 0:
            return None
        
        return max(format_votes, key=format_votes.get)
    
    @staticmethod
    def get_dataset_info(dataset_path: Path) -> Dict:
        """获取数据集详细信息"""
        is_valid, message, stats = DatasetValidator.validate_dataset_structure(dataset_path)
        detected_format = DatasetValidator.detect_dataset_format(dataset_path)
        
        return {
            "path": str(dataset_path),
            "is_valid": is_valid,
            "message": message,
            "detected_format": detected_format,
            "statistics": stats
        }
    
    @staticmethod
    def create_sample_dataset_structure(output_path: Path, format_type: str = "yolo"):
        """创建示例数据集目录结构"""
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 创建目录结构
        for subset in ["train", "test", "val"]:
            (output_path / "images" / subset).mkdir(parents=True, exist_ok=True)
            (output_path / "labels" / subset).mkdir(parents=True, exist_ok=True)
        
        # 创建说明文件
        readme_content = f"""# 数据集目录结构说明

这是一个标准的{format_type.upper()}格式数据集目录结构。

## 目录结构
```
{output_path.name}/
├── images/
│   ├── train/          # 训练集图片
│   ├── test/           # 测试集图片
│   └── val/            # 验证集图片
└── labels/
    ├── train/          # 训练集标签
    ├── test/           # 测试集标签
    └── val/            # 验证集标签
```

## 使用说明
1. 将图片文件放入对应的 images/子集/ 目录
2. 将标签文件放入对应的 labels/子集/ 目录
3. 确保图片和标签文件名一致（扩展名除外）

## 支持的文件格式
- 图片: .jpg, .jpeg, .png, .bmp, .tiff, .webp
- 标签: .txt (YOLO), .xml (VOC), .json (JSON)
"""
        
        (output_path / "README.md").write_text(readme_content, encoding="utf-8")
        
        return True