"""
数据质量检查工具
"""
import hashlib
from pathlib import Path
from typing import List, Dict, Set, Tuple
from PIL import Image
import json

from .base_parser import ImageAnnotation


class QualityChecker:
    """数据质量检查器"""
    
    def __init__(self):
        self.issues = []
        self.stats = {}
    
    def check_dataset(self, annotations: List[ImageAnnotation]) -> Dict:
        """全面检查数据集质量"""
        self.issues = []
        self.stats = {
            'total_images': len(annotations),
            'total_boxes': 0,
            'total_polygons': 0,
            'classes': set(),
            'image_sizes': [],
            'box_sizes': []
        }
        
        print("开始数据质量检查...")
        
        # 1. 检查重复图片
        duplicates = self._check_duplicates(annotations)
        
        # 2. 检查空标注
        empty_annotations = self._check_empty_annotations(annotations)
        
        # 3. 检查异常标注
        invalid_annotations = self._check_invalid_annotations(annotations)
        
        # 4. 检查图片完整性
        corrupted_images = self._check_image_integrity(annotations)
        
        # 5. 检查标注一致性
        inconsistent_labels = self._check_label_consistency(annotations)
        
        # 6. 统计信息
        self._collect_statistics(annotations)
        
        # 生成报告
        report = {
            'summary': {
                'total_images': self.stats['total_images'],
                'total_issues': len(self.issues),
                'health_score': self._calculate_health_score()
            },
            'issues': {
                'duplicates': duplicates,
                'empty_annotations': empty_annotations,
                'invalid_annotations': invalid_annotations,
                'corrupted_images': corrupted_images,
                'inconsistent_labels': inconsistent_labels
            },
            'statistics': self.stats,
            'recommendations': self._generate_recommendations()
        }
        
        print(f"质量检查完成，发现 {len(self.issues)} 个问题")
        return report
    
    def _check_duplicates(self, annotations: List[ImageAnnotation]) -> List[Dict]:
        """检查重复图片"""
        print("检查重复图片...")
        duplicates = []
        hash_to_files = {}
        
        for ann in annotations:
            if not ann.image_path.exists():
                continue
                
            try:
                # 计算文件哈希
                with open(ann.image_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                
                if file_hash in hash_to_files:
                    duplicates.append({
                        'type': 'duplicate_image',
                        'files': [hash_to_files[file_hash], str(ann.image_path)],
                        'hash': file_hash
                    })
                    self.issues.append(f"重复图片: {ann.image_path.name}")
                else:
                    hash_to_files[file_hash] = str(ann.image_path)
                    
            except Exception as e:
                self.issues.append(f"无法读取图片: {ann.image_path.name} - {e}")
        
        return duplicates
    
    def _check_empty_annotations(self, annotations: List[ImageAnnotation]) -> List[Dict]:
        """检查空标注"""
        print("检查空标注...")
        empty_annotations = []
        
        for ann in annotations:
            box_count = len(ann.boxes) if ann.boxes else 0
            poly_count = len(ann.polygons) if ann.polygons else 0
            
            if box_count == 0 and poly_count == 0:
                empty_annotations.append({
                    'type': 'empty_annotation',
                    'file': str(ann.image_path),
                    'message': '没有标注信息'
                })
                self.issues.append(f"空标注: {ann.image_path.name}")
        
        return empty_annotations
    
    def _check_invalid_annotations(self, annotations: List[ImageAnnotation]) -> List[Dict]:
        """检查异常标注"""
        print("检查异常标注...")
        invalid_annotations = []
        
        for ann in annotations:
            # 检查矩形框
            for i, box in enumerate(ann.boxes):
                issues = []
                
                # 检查坐标范围
                if box.xmin < 0 or box.ymin < 0:
                    issues.append("坐标为负数")
                if box.xmax > ann.width or box.ymax > ann.height:
                    issues.append("坐标超出图片边界")
                if box.xmin >= box.xmax or box.ymin >= box.ymax:
                    issues.append("无效的矩形框尺寸")
                
                # 检查标注框大小
                width = box.xmax - box.xmin
                height = box.ymax - box.ymin
                if width < 5 or height < 5:
                    issues.append("标注框过小")
                if width > ann.width * 0.9 or height > ann.height * 0.9:
                    issues.append("标注框过大")
                
                if issues:
                    invalid_annotations.append({
                        'type': 'invalid_bbox',
                        'file': str(ann.image_path),
                        'bbox_index': i,
                        'bbox': [box.xmin, box.ymin, box.xmax, box.ymax],
                        'issues': issues
                    })
                    self.issues.append(f"异常标注: {ann.image_path.name} - {', '.join(issues)}")
            
            # 检查多边形
            if ann.polygons:
                for i, poly in enumerate(ann.polygons):
                    if len(poly.points) < 6:  # 至少3个点
                        invalid_annotations.append({
                            'type': 'invalid_polygon',
                            'file': str(ann.image_path),
                            'polygon_index': i,
                            'issues': ['多边形点数不足']
                        })
                        self.issues.append(f"异常多边形: {ann.image_path.name} - 点数不足")
        
        return invalid_annotations
    
    def _check_image_integrity(self, annotations: List[ImageAnnotation]) -> List[Dict]:
        """检查图片完整性"""
        print("检查图片完整性...")
        corrupted_images = []
        
        for ann in annotations:
            if not ann.image_path.exists():
                corrupted_images.append({
                    'type': 'missing_image',
                    'file': str(ann.image_path),
                    'message': '图片文件不存在'
                })
                self.issues.append(f"缺失图片: {ann.image_path.name}")
                continue
            
            try:
                with Image.open(ann.image_path) as img:
                    # 尝试加载图片
                    img.verify()
                    
                    # 检查图片尺寸
                    if img.size != (ann.width, ann.height):
                        corrupted_images.append({
                            'type': 'size_mismatch',
                            'file': str(ann.image_path),
                            'expected_size': (ann.width, ann.height),
                            'actual_size': img.size
                        })
                        self.issues.append(f"尺寸不匹配: {ann.image_path.name}")
                        
            except Exception as e:
                corrupted_images.append({
                    'type': 'corrupted_image',
                    'file': str(ann.image_path),
                    'error': str(e)
                })
                self.issues.append(f"损坏图片: {ann.image_path.name} - {e}")
        
        return corrupted_images
    
    def _check_label_consistency(self, annotations: List[ImageAnnotation]) -> List[Dict]:
        """检查标签一致性"""
        print("检查标签一致性...")
        inconsistent_labels = []
        
        # 收集所有标签的不同写法
        label_variants = {}
        for ann in annotations:
            for box in ann.boxes:
                label_lower = box.label.lower()
                if label_lower not in label_variants:
                    label_variants[label_lower] = set()
                label_variants[label_lower].add(box.label)
        
        # 检查是否有多种写法
        for label_lower, variants in label_variants.items():
            if len(variants) > 1:
                inconsistent_labels.append({
                    'type': 'inconsistent_label',
                    'label_variants': list(variants),
                    'suggested_label': max(variants, key=len)  # 选择最长的作为建议
                })
                self.issues.append(f"标签不一致: {', '.join(variants)}")
        
        return inconsistent_labels
    
    def _collect_statistics(self, annotations: List[ImageAnnotation]):
        """收集统计信息"""
        print("收集统计信息...")
        
        for ann in annotations:
            # 图片尺寸统计
            self.stats['image_sizes'].append((ann.width, ann.height))
            
            # 标注统计
            self.stats['total_boxes'] += len(ann.boxes)
            if ann.polygons:
                self.stats['total_polygons'] += len(ann.polygons)
            
            # 类别统计
            for box in ann.boxes:
                self.stats['classes'].add(box.label)
                # 标注框尺寸统计
                width = box.xmax - box.xmin
                height = box.ymax - box.ymin
                self.stats['box_sizes'].append((width, height))
            
            if ann.polygons:
                for poly in ann.polygons:
                    self.stats['classes'].add(poly.label)
        
        # 转换set为list以便JSON序列化
        self.stats['classes'] = list(self.stats['classes'])
    
    def _calculate_health_score(self) -> float:
        """计算数据集健康度评分"""
        if self.stats['total_images'] == 0:
            return 0.0
        
        # 基础分数
        score = 100.0
        
        # 根据问题数量扣分
        issue_penalty = min(len(self.issues) * 2, 50)  # 每个问题扣2分，最多扣50分
        score -= issue_penalty
        
        # 根据空标注比例扣分
        empty_count = len([issue for issue in self.issues if "空标注" in issue])
        empty_ratio = empty_count / self.stats['total_images']
        score -= empty_ratio * 30  # 空标注比例扣分
        
        return max(score, 0.0)
    
    def _generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if len(self.issues) == 0:
            recommendations.append("数据集质量良好，无需特别处理")
            return recommendations
        
        # 根据问题类型生成建议
        issue_types = {}
        for issue in self.issues:
            if "重复图片" in issue:
                issue_types['duplicates'] = issue_types.get('duplicates', 0) + 1
            elif "空标注" in issue:
                issue_types['empty'] = issue_types.get('empty', 0) + 1
            elif "异常标注" in issue:
                issue_types['invalid'] = issue_types.get('invalid', 0) + 1
            elif "损坏图片" in issue:
                issue_types['corrupted'] = issue_types.get('corrupted', 0) + 1
            elif "标签不一致" in issue:
                issue_types['inconsistent'] = issue_types.get('inconsistent', 0) + 1
        
        if 'duplicates' in issue_types:
            recommendations.append(f"发现 {issue_types['duplicates']} 张重复图片，建议删除重复文件")
        
        if 'empty' in issue_types:
            recommendations.append(f"发现 {issue_types['empty']} 张空标注图片，建议补充标注或移除")
        
        if 'invalid' in issue_types:
            recommendations.append(f"发现 {issue_types['invalid']} 个异常标注，建议检查并修正")
        
        if 'corrupted' in issue_types:
            recommendations.append(f"发现 {issue_types['corrupted']} 张损坏图片，建议重新获取或移除")
        
        if 'inconsistent' in issue_types:
            recommendations.append(f"发现 {issue_types['inconsistent']} 个标签不一致问题，建议统一标签命名")
        
        return recommendations
    
    def save_report(self, report: Dict, output_file: Path):
        """保存质量检查报告"""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"质量检查报告已保存: {output_file}")
    
    def save_html_report(self, report: Dict, output_file: Path):
        """保存HTML格式的质量检查报告"""
        html_content = self._generate_html_report(report)
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML质量检查报告已保存: {output_file}")
    
    def _generate_html_report(self, report: Dict) -> str:
        """生成HTML格式报告"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>数据集质量检查报告</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                .issue {{ background-color: #ffe6e6; padding: 10px; margin: 5px 0; border-radius: 3px; }}
                .recommendation {{ background-color: #e6f3ff; padding: 10px; margin: 5px 0; border-radius: 3px; }}
                .stats {{ background-color: #f0f8f0; padding: 15px; border-radius: 5px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>数据集质量检查报告</h1>
                <p>总图片数: {report['summary']['total_images']}</p>
                <p>发现问题: {report['summary']['total_issues']}</p>
                <p>健康度评分: {report['summary']['health_score']:.1f}/100</p>
            </div>
            
            <div class="section">
                <h2>统计信息</h2>
                <div class="stats">
                    <p>总图片数: {report['statistics']['total_images']}</p>
                    <p>总矩形框数: {report['statistics']['total_boxes']}</p>
                    <p>总多边形数: {report['statistics']['total_polygons']}</p>
                    <p>类别数量: {len(report['statistics']['classes'])}</p>
                    <p>类别列表: {', '.join(report['statistics']['classes'])}</p>
                </div>
            </div>
            
            <div class="section">
                <h2>发现的问题</h2>
        """
        
        # 添加问题详情
        for issue_type, issues in report['issues'].items():
            if issues:
                html += f"<h3>{issue_type}</h3>"
                for issue in issues:
                    html += f'<div class="issue">{issue}</div>'
        
        # 添加建议
        html += """
            </div>
            
            <div class="section">
                <h2>改进建议</h2>
        """
        
        for rec in report['recommendations']:
            html += f'<div class="recommendation">{rec}</div>'
        
        html += """
            </div>
        </body>
        </html>
        """
        
        return html