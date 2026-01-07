from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import Counter
import json

class DatasetComparator:
    """数据集比较器"""
    
    def compare_datasets(self, dataset1_dir: Path, dataset2_dir: Path, 
                        format_type: str = 'yolo') -> Dict:
        """比较两个数据集"""
        
        if format_type == 'yolo':
            stats1 = self._analyze_yolo_dataset(dataset1_dir)
            stats2 = self._analyze_yolo_dataset(dataset2_dir)
        else:
            return {'error': f'不支持的格式: {format_type}'}
        
        comparison = {
            'dataset1': stats1,
            'dataset2': stats2,
            'differences': self._calculate_differences(stats1, stats2),
            'recommendations': self._generate_recommendations(stats1, stats2)
        }
        
        return comparison
    
    def _analyze_yolo_dataset(self, dataset_dir: Path) -> Dict:
        """分析YOLO数据集"""
        stats = {
            'total_images': 0,
            'total_annotations': 0,
            'class_distribution': Counter(),
            'image_files': set(),
            'annotation_files': set(),
            'missing_annotations': [],
            'empty_annotations': []
        }
        
        # 获取所有文件
        image_files = list(dataset_dir.glob('*.jpg')) + list(dataset_dir.glob('*.png'))
        txt_files = list(dataset_dir.glob('*.txt'))
        
        stats['image_files'] = {f.stem for f in image_files}
        stats['annotation_files'] = {f.stem for f in txt_files}
        stats['total_images'] = len(image_files)
        
        # 分析标注
        for img_file in image_files:
            txt_file = img_file.with_suffix('.txt')
            
            if not txt_file.exists():
                stats['missing_annotations'].append(img_file.stem)
                continue
            
            try:
                content = txt_file.read_text(encoding='utf-8').strip()
                if not content:
                    stats['empty_annotations'].append(img_file.stem)
                    continue
                
                lines = content.split('\n')
                stats['total_annotations'] += len(lines)
                
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        class_id = parts[0]
                        stats['class_distribution'][class_id] += 1
                        
            except Exception:
                continue
        
        return stats
    
    def _calculate_differences(self, stats1: Dict, stats2: Dict) -> Dict:
        """计算两个数据集的差异"""
        differences = {}
        
        # 基本统计差异
        differences['image_count_diff'] = stats2['total_images'] - stats1['total_images']
        differences['annotation_count_diff'] = stats2['total_annotations'] - stats1['total_annotations']
        
        # 文件差异
        files1 = stats1['image_files']
        files2 = stats2['image_files']
        
        differences['common_files'] = len(files1 & files2)
        differences['unique_to_dataset1'] = len(files1 - files2)
        differences['unique_to_dataset2'] = len(files2 - files1)
        differences['files_only_in_dataset1'] = list(files1 - files2)[:10]  # 只显示前10个
        differences['files_only_in_dataset2'] = list(files2 - files1)[:10]
        
        # 类别差异
        classes1 = set(stats1['class_distribution'].keys())
        classes2 = set(stats2['class_distribution'].keys())
        
        differences['common_classes'] = list(classes1 & classes2)
        differences['classes_only_in_dataset1'] = list(classes1 - classes2)
        differences['classes_only_in_dataset2'] = list(classes2 - classes1)
        
        # 类别分布差异
        class_diff = {}
        for class_id in classes1 | classes2:
            count1 = stats1['class_distribution'].get(class_id, 0)
            count2 = stats2['class_distribution'].get(class_id, 0)
            if count1 > 0 or count2 > 0:
                class_diff[class_id] = {
                    'dataset1': count1,
                    'dataset2': count2,
                    'difference': count2 - count1,
                    'ratio': count2 / count1 if count1 > 0 else float('inf')
                }
        
        differences['class_distribution_diff'] = class_diff
        
        return differences
    
    def _generate_recommendations(self, stats1: Dict, stats2: Dict) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 数据量建议
        if stats1['total_images'] < stats2['total_images']:
            recommendations.append(f"数据集1的图片数量较少，建议增加 {stats2['total_images'] - stats1['total_images']} 张图片")
        
        # 标注质量建议
        missing1 = len(stats1['missing_annotations'])
        missing2 = len(stats2['missing_annotations'])
        
        if missing1 > missing2:
            recommendations.append(f"数据集1有 {missing1} 个文件缺少标注，建议补充标注")
        elif missing2 > missing1:
            recommendations.append(f"数据集2有 {missing2} 个文件缺少标注，建议补充标注")
        
        # 类别平衡建议
        classes1 = set(stats1['class_distribution'].keys())
        classes2 = set(stats2['class_distribution'].keys())
        
        if len(classes1) != len(classes2):
            recommendations.append("两个数据集的类别数量不同，建议统一类别定义")
        
        # 数据分布建议
        for class_id in classes1 & classes2:
            count1 = stats1['class_distribution'][class_id]
            count2 = stats2['class_distribution'][class_id]
            ratio = count2 / count1 if count1 > 0 else float('inf')
            
            if ratio > 2:
                recommendations.append(f"类别 '{class_id}' 在数据集2中数量过多，建议平衡")
            elif ratio < 0.5:
                recommendations.append(f"类别 '{class_id}' 在数据集1中数量过多，建议平衡")
        
        return recommendations
    
    def find_duplicate_images(self, dataset_dir: Path) -> List[Tuple[str, str]]:
        """查找重复图片（基于文件大小）"""
        from collections import defaultdict
        
        size_groups = defaultdict(list)
        image_files = list(dataset_dir.glob('*.jpg')) + list(dataset_dir.glob('*.png'))
        
        # 按文件大小分组
        for img_file in image_files:
            try:
                size = img_file.stat().st_size
                size_groups[size].append(img_file.name)
            except:
                continue
        
        # 找出可能的重复文件
        duplicates = []
        for size, files in size_groups.items():
            if len(files) > 1:
                for i in range(len(files)):
                    for j in range(i+1, len(files)):
                        duplicates.append((files[i], files[j]))
        
        return duplicates
    
    def merge_class_mappings(self, mapping1: Dict[str, int], mapping2: Dict[str, int]) -> Dict[str, int]:
        """合并两个类别映射"""
        merged = dict(mapping1)
        next_id = max(mapping1.values()) + 1 if mapping1 else 0
        
        for class_name, class_id in mapping2.items():
            if class_name not in merged:
                merged[class_name] = next_id
                next_id += 1
        
        return merged