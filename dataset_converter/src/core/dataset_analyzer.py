from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter, defaultdict
import json
from PIL import Image

class DatasetAnalyzer:
    """数据集统计分析器"""
    
    def analyze_dataset(self, dataset_dir: Path, format_type: str = 'yolo') -> Dict:
        """分析数据集统计信息"""
        if format_type == 'yolo':
            return self._analyze_yolo_dataset(dataset_dir)
        elif format_type == 'json':
            return self._analyze_json_dataset(dataset_dir)
        else:
            return {'error': f'不支持的格式: {format_type}'}
    
    def _analyze_yolo_dataset(self, dataset_dir: Path) -> Dict:
        """分析YOLO格式数据集"""
        stats = {
            'total_images': 0,
            'total_annotations': 0,
            'class_distribution': Counter(),
            'image_sizes': [],
            'annotation_counts': [],
            'bbox_sizes': [],
            'polygon_point_counts': []
        }
        
        image_files = list(dataset_dir.glob('*.jpg')) + list(dataset_dir.glob('*.png'))
        
        for img_file in image_files:
            stats['total_images'] += 1
            
            # 获取图片尺寸
            try:
                with Image.open(img_file) as img:
                    stats['image_sizes'].append(img.size)
            except:
                continue
            
            # 分析标注文件
            txt_file = img_file.with_suffix('.txt')
            if not txt_file.exists():
                stats['annotation_counts'].append(0)
                continue
            
            try:
                content = txt_file.read_text(encoding='utf-8').strip()
                if not content:
                    stats['annotation_counts'].append(0)
                    continue
                
                lines = content.split('\n')
                stats['annotation_counts'].append(len(lines))
                stats['total_annotations'] += len(lines)
                
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) < 5:
                        continue
                    
                    class_id = parts[0]
                    stats['class_distribution'][class_id] += 1
                    
                    if len(parts) == 5:
                        # 矩形框
                        _, cx, cy, w, h = map(float, parts)
                        stats['bbox_sizes'].append((w, h))
                    else:
                        # 多边形
                        coords = [float(x) for x in parts[1:]]
                        stats['polygon_point_counts'].append(len(coords) // 2)
                        
            except Exception:
                continue
        
        # 计算统计摘要
        return self._calculate_summary(stats)
    
    def _analyze_json_dataset(self, dataset_dir: Path) -> Dict:
        """分析JSON格式数据集"""
        stats = {
            'total_images': 0,
            'total_annotations': 0,
            'class_distribution': Counter(),
            'image_sizes': [],
            'annotation_counts': []
        }
        
        json_files = list(dataset_dir.glob('*.json'))
        
        for json_file in json_files:
            try:
                data = json.loads(json_file.read_text(encoding='utf-8'))
                stats['total_images'] += 1
                
                width = data.get('width', 0)
                height = data.get('height', 0)
                stats['image_sizes'].append((width, height))
                
                annotations = data.get('annotations', [])
                stats['annotation_counts'].append(len(annotations))
                stats['total_annotations'] += len(annotations)
                
                for ann in annotations:
                    label = ann.get('label', 'unknown')
                    stats['class_distribution'][label] += 1
                    
            except Exception:
                continue
        
        return self._calculate_summary(stats)
    
    def _calculate_summary(self, stats: Dict) -> Dict:
        """计算统计摘要"""
        summary = dict(stats)
        
        # 图片尺寸统计
        if stats['image_sizes']:
            widths = [size[0] for size in stats['image_sizes']]
            heights = [size[1] for size in stats['image_sizes']]
            
            summary['image_size_stats'] = {
                'avg_width': sum(widths) / len(widths),
                'avg_height': sum(heights) / len(heights),
                'min_width': min(widths),
                'max_width': max(widths),
                'min_height': min(heights),
                'max_height': max(heights)
            }
        
        # 标注数量统计
        if stats['annotation_counts']:
            counts = stats['annotation_counts']
            summary['annotation_stats'] = {
                'avg_per_image': sum(counts) / len(counts),
                'min_per_image': min(counts),
                'max_per_image': max(counts),
                'images_without_annotations': counts.count(0)
            }
        
        # 类别平衡性分析
        if stats['class_distribution']:
            total = sum(stats['class_distribution'].values())
            summary['class_balance'] = {
                class_id: count / total 
                for class_id, count in stats['class_distribution'].items()
            }
        
        return summary