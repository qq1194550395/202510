from pathlib import Path
from typing import Dict, List, Optional
import json
import yaml
import zipfile
import shutil
from datetime import datetime

class DatasetExporter:
    """数据集导出器"""
    
    def export_to_zip(self, dataset_dir: Path, output_path: Path, 
                     include_metadata: bool = True) -> bool:
        """导出数据集为ZIP文件"""
        try:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 添加所有文件
                for file_path in dataset_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(dataset_dir)
                        zipf.write(file_path, arcname)
                
                # 添加元数据
                if include_metadata:
                    metadata = self._generate_metadata(dataset_dir)
                    zipf.writestr('dataset_metadata.json', 
                                json.dumps(metadata, indent=2, ensure_ascii=False))
            
            return True
        except Exception as e:
            print(f"导出ZIP失败: {e}")
            return False
    
    def export_coco_format(self, dataset_dir: Path, output_path: Path, 
                          dataset_name: str = "Custom Dataset") -> bool:
        """导出为COCO格式"""
        try:
            coco_data = {
                "info": {
                    "description": dataset_name,
                    "version": "1.0",
                    "year": datetime.now().year,
                    "date_created": datetime.now().isoformat()
                },
                "licenses": [],
                "images": [],
                "annotations": [],
                "categories": []
            }
            
            # 收集类别信息
            categories = self._collect_categories(dataset_dir)
            category_map = {}
            for i, cat_name in enumerate(categories):
                cat_id = i + 1
                category_map[cat_name] = cat_id
                coco_data["categories"].append({
                    "id": cat_id,
                    "name": cat_name,
                    "supercategory": ""
                })
            
            # 处理图片和标注
            image_id = 1
            annotation_id = 1
            
            image_files = list(dataset_dir.glob('*.jpg')) + list(dataset_dir.glob('*.png'))
            
            for img_file in image_files:
                # 添加图片信息
                try:
                    from PIL import Image
                    with Image.open(img_file) as img:
                        width, height = img.size
                except:
                    continue
                
                coco_data["images"].append({
                    "id": image_id,
                    "width": width,
                    "height": height,
                    "file_name": img_file.name
                })
                
                # 处理标注
                txt_file = img_file.with_suffix('.txt')
                if txt_file.exists():
                    annotations = self._convert_yolo_to_coco(
                        txt_file, image_id, width, height, category_map
                    )
                    for ann in annotations:
                        ann["id"] = annotation_id
                        coco_data["annotations"].append(ann)
                        annotation_id += 1
                
                image_id += 1
            
            # 保存COCO格式文件
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(coco_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"导出COCO格式失败: {e}")
            return False
    
    def export_yolo_config(self, dataset_dir: Path, output_dir: Path, 
                          train_ratio: float = 0.8) -> bool:
        """导出YOLO训练配置"""
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 收集类别信息
            categories = self._collect_categories(dataset_dir)
            
            # 生成classes.txt
            classes_file = output_dir / 'classes.txt'
            classes_file.write_text('\n'.join(categories), encoding='utf-8')
            
            # 生成data.yaml
            data_config = {
                'train': str(output_dir / 'train'),
                'val': str(output_dir / 'val'),
                'nc': len(categories),
                'names': categories
            }
            
            with open(output_dir / 'data.yaml', 'w', encoding='utf-8') as f:
                yaml.dump(data_config, f, default_flow_style=False, allow_unicode=True)
            
            # 生成训练脚本模板
            train_script = f"""#!/usr/bin/env python3
# YOLO训练脚本模板

import torch
from ultralytics import YOLO

def train_model():
    # 加载预训练模型
    model = YOLO('yolov8n.pt')  # 可选: yolov8s.pt, yolov8m.pt, yolov8l.pt, yolov8x.pt
    
    # 训练模型
    results = model.train(
        data='{output_dir / 'data.yaml'}',
        epochs=100,
        imgsz=640,
        batch=16,
        device='0' if torch.cuda.is_available() else 'cpu'
    )
    
    return results

if __name__ == '__main__':
    train_model()
"""
            
            (output_dir / 'train.py').write_text(train_script, encoding='utf-8')
            
            return True
            
        except Exception as e:
            print(f"导出YOLO配置失败: {e}")
            return False
    
    def _generate_metadata(self, dataset_dir: Path) -> Dict:
        """生成数据集元数据"""
        # 简化版本，避免循环导入
        metadata = {
            "dataset_name": dataset_dir.name,
            "export_time": datetime.now().isoformat(),
            "format": "YOLO",
            "description": "Exported dataset with metadata"
        }
        
        # 简单统计
        image_files = list(dataset_dir.glob('*.jpg')) + list(dataset_dir.glob('*.png'))
        txt_files = list(dataset_dir.glob('*.txt'))
        
        metadata["total_images"] = len(image_files)
        metadata["total_txt_files"] = len(txt_files)
        
        return metadata
    
    def _collect_categories(self, dataset_dir: Path) -> List[str]:
        """收集所有类别"""
        categories = set()
        txt_files = list(dataset_dir.glob('*.txt'))
        
        for txt_file in txt_files:
            try:
                content = txt_file.read_text(encoding='utf-8').strip()
                if content:
                    for line in content.split('\n'):
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            categories.add(parts[0])
            except:
                continue
        
        return sorted(list(categories))
    
    def _convert_yolo_to_coco(self, txt_file: Path, image_id: int, 
                             width: int, height: int, category_map: Dict) -> List[Dict]:
        """将YOLO标注转换为COCO格式"""
        annotations = []
        
        try:
            content = txt_file.read_text(encoding='utf-8').strip()
            if not content:
                return annotations
            
            for line in content.split('\n'):
                parts = line.strip().split()
                if len(parts) < 5:
                    continue
                
                class_name = parts[0]
                if class_name not in category_map:
                    continue
                
                category_id = category_map[class_name]
                
                if len(parts) == 5:
                    # 矩形框
                    _, cx, cy, w, h = map(float, parts)
                    
                    # 转换为COCO格式 (x, y, width, height)
                    x = (cx - w/2) * width
                    y = (cy - h/2) * height
                    bbox_width = w * width
                    bbox_height = h * height
                    
                    annotations.append({
                        "image_id": image_id,
                        "category_id": category_id,
                        "bbox": [x, y, bbox_width, bbox_height],
                        "area": bbox_width * bbox_height,
                        "iscrowd": 0
                    })
                else:
                    # 多边形 - 转换为分割格式
                    coords = [float(x) for x in parts[1:]]
                    if len(coords) % 2 == 0 and len(coords) >= 6:
                        # 转换为像素坐标
                        pixel_coords = []
                        for i in range(0, len(coords), 2):
                            pixel_coords.extend([coords[i] * width, coords[i+1] * height])
                        
                        # 计算边界框
                        x_coords = pixel_coords[::2]
                        y_coords = pixel_coords[1::2]
                        x_min, x_max = min(x_coords), max(x_coords)
                        y_min, y_max = min(y_coords), max(y_coords)
                        
                        annotations.append({
                            "image_id": image_id,
                            "category_id": category_id,
                            "segmentation": [pixel_coords],
                            "bbox": [x_min, y_min, x_max - x_min, y_max - y_min],
                            "area": (x_max - x_min) * (y_max - y_min),
                            "iscrowd": 0
                        })
        
        except Exception:
            pass
        
        return annotations
    
    def create_dataset_report(self, dataset_dir: Path, output_path: Path) -> bool:
        """创建数据集报告"""
        try:
            # 简化版本，避免循环导入
            # 基本统计
            image_files = list(dataset_dir.glob('*.jpg')) + list(dataset_dir.glob('*.png'))
            txt_files = list(dataset_dir.glob('*.txt'))
            
            basic_stats = {
                'total_images': len(image_files),
                'total_txt_files': len(txt_files),
                'class_distribution': {}
            }
            
            # 简单的类别统计
            for txt_file in txt_files:
                try:
                    content = txt_file.read_text(encoding='utf-8').strip()
                    if content:
                        for line in content.split('\n'):
                            parts = line.strip().split()
                            if len(parts) >= 5:
                                class_id = parts[0]
                                basic_stats['class_distribution'][class_id] = basic_stats['class_distribution'].get(class_id, 0) + 1
                except:
                    continue
            
            # 生成简化的HTML报告
            html_content = self._generate_simple_html_report(dataset_dir.name, basic_stats)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return True
            
        except Exception as e:
            print(f"生成报告失败: {e}")
            return False
    
    def _generate_simple_html_report(self, dataset_name: str, stats: Dict) -> str:
        """生成简化的HTML报告"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>数据集报告 - {dataset_name}</title>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .stats {{ display: flex; justify-content: space-around; }}
        .stat-item {{ text-align: center; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #007bff; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>数据集报告: {dataset_name}</h1>
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="section">
        <h2>基本统计</h2>
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{stats.get('total_images', 0)}</div>
                <div>总图片数</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{stats.get('total_txt_files', 0)}</div>
                <div>标注文件数</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{len(stats.get('class_distribution', {}))}</div>
                <div>类别数</div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>类别分布</h2>
        <table>
            <tr><th>类别</th><th>数量</th></tr>
"""
        
        for class_id, count in stats.get('class_distribution', {}).items():
            html += f"<tr><td>{class_id}</td><td>{count}</td></tr>"
        
        html += """
        </table>
    </div>
</body>
</html>
"""
        
        return html