from pathlib import Path
from typing import List, Dict, Tuple
import json
from PIL import Image

class DatasetValidator:
    """数据集质量检查器"""
    
    def __init__(self):
        self.issues = []
    
    def validate_yolo_dataset(self, dataset_dir: Path) -> Dict:
        """验证YOLO格式数据集"""
        issues = []
        stats = {
            'total_images': 0,
            'total_annotations': 0,
            'missing_annotations': 0,
            'invalid_annotations': 0,
            'empty_annotations': 0,
            'coordinate_errors': 0
        }
        
        # 检查图片和标注文件匹配
        image_files = list(dataset_dir.glob('*.jpg')) + list(dataset_dir.glob('*.png'))
        
        for img_file in image_files:
            stats['total_images'] += 1
            txt_file = img_file.with_suffix('.txt')
            
            if not txt_file.exists():
                issues.append(f"缺少标注文件: {txt_file.name}")
                stats['missing_annotations'] += 1
                continue
            
            # 检查标注文件内容
            try:
                content = txt_file.read_text(encoding='utf-8').strip()
                if not content:
                    issues.append(f"空标注文件: {txt_file.name}")
                    stats['empty_annotations'] += 1
                    continue
                
                lines = content.split('\n')
                stats['total_annotations'] += len(lines)
                
                # 检查每行格式
                for i, line in enumerate(lines):
                    parts = line.strip().split()
                    if len(parts) < 5:
                        issues.append(f"标注格式错误 {txt_file.name}:{i+1} - 参数不足")
                        stats['invalid_annotations'] += 1
                        continue
                    
                    # 检查坐标范围
                    try:
                        coords = [float(x) for x in parts[1:]]
                        for coord in coords:
                            if coord < 0 or coord > 1:
                                issues.append(f"坐标超出范围 {txt_file.name}:{i+1}")
                                stats['coordinate_errors'] += 1
                                break
                    except ValueError:
                        issues.append(f"坐标格式错误 {txt_file.name}:{i+1}")
                        stats['invalid_annotations'] += 1
                        
            except Exception as e:
                issues.append(f"读取标注文件失败 {txt_file.name}: {e}")
                stats['invalid_annotations'] += 1
        
        return {
            'issues': issues,
            'stats': stats,
            'health_score': self._calculate_health_score(stats)
        }
    
    def _calculate_health_score(self, stats: Dict) -> float:
        """计算数据集健康度评分 (0-100)"""
        if stats['total_images'] == 0:
            return 0
        
        error_rate = (stats['missing_annotations'] + stats['invalid_annotations'] + 
                     stats['coordinate_errors']) / stats['total_images']
        return max(0, 100 - error_rate * 100)