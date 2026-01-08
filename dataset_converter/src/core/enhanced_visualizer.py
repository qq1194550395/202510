"""
增强的数据可视化器
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from PIL import Image, ImageDraw, ImageFont
import json
from collections import Counter, defaultdict
import colorsys

from .base_parser import ImageAnnotation

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class EnhancedVisualizer:
    """增强的数据可视化器"""
    
    def __init__(self):
        self.colors = self._generate_colors(50)
        self.class_colors = {}
        
        # 设置matplotlib样式
        plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
        sns.set_palette("husl")
    
    def _generate_colors(self, num_colors: int) -> List[Tuple[int, int, int]]:
        """生成不同的颜色"""
        colors = []
        for i in range(num_colors):
            hue = i / num_colors
            saturation = 0.7 + (i % 3) * 0.1
            value = 0.8 + (i % 2) * 0.2
            rgb = colorsys.hsv_to_rgb(hue, saturation, value)
            colors.append(tuple(int(c * 255) for c in rgb))
        return colors
    
    def get_class_color(self, class_name: str) -> Tuple[int, int, int]:
        """获取类别对应的颜色"""
        if class_name not in self.class_colors:
            color_idx = len(self.class_colors) % len(self.colors)
            self.class_colors[class_name] = self.colors[color_idx]
        return self.class_colors[class_name]
    
    def create_statistics_dashboard(self, annotations: List[ImageAnnotation], 
                                  output_dir: Path, theme: str = "light") -> None:
        """创建统计仪表板"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置主题
        if theme == "dark":
            plt.style.use('dark_background')
            bg_color = '#2E2E2E'
            text_color = 'white'
        else:
            plt.style.use('default')
            bg_color = 'white'
            text_color = 'black'
        
        # 收集统计数据
        stats = self._collect_statistics(annotations)
        
        # 创建多子图仪表板
        fig = plt.figure(figsize=(20, 16))
        fig.suptitle('数据集统计仪表板', fontsize=24, fontweight='bold', color=text_color)
        
        # 1. 类别分布饼图
        ax1 = plt.subplot(3, 3, 1)
        self._plot_class_distribution_pie(stats['class_counts'], ax1, theme)
        
        # 2. 类别分布柱状图
        ax2 = plt.subplot(3, 3, 2)
        self._plot_class_distribution_bar(stats['class_counts'], ax2, theme)
        
        # 3. 图片尺寸分布
        ax3 = plt.subplot(3, 3, 3)
        self._plot_image_size_distribution(stats['image_sizes'], ax3, theme)
        
        # 4. 标注框尺寸分布
        ax4 = plt.subplot(3, 3, 4)
        self._plot_bbox_size_distribution(stats['bbox_sizes'], ax4, theme)
        
        # 5. 每张图片标注数量分布
        ax5 = plt.subplot(3, 3, 5)
        self._plot_annotations_per_image(stats['annotations_per_image'], ax5, theme)
        
        # 6. 标注密度热力图
        ax6 = plt.subplot(3, 3, 6)
        self._plot_annotation_density_heatmap(annotations, ax6, theme)
        
        # 7. 宽高比分布
        ax7 = plt.subplot(3, 3, 7)
        self._plot_aspect_ratio_distribution(stats['aspect_ratios'], ax7, theme)
        
        # 8. 数据集概览表格
        ax8 = plt.subplot(3, 3, 8)
        self._plot_dataset_summary_table(stats, ax8, theme)
        
        # 9. 类别共现矩阵
        ax9 = plt.subplot(3, 3, 9)
        self._plot_class_cooccurrence_matrix(annotations, ax9, theme)
        
        plt.tight_layout()
        
        # 保存图表
        dashboard_file = output_dir / f"statistics_dashboard_{theme}.png"
        plt.savefig(dashboard_file, dpi=300, bbox_inches='tight', 
                   facecolor=bg_color, edgecolor='none')
        plt.close()
        
        print(f"统计仪表板已保存: {dashboard_file}")
    
    def _collect_statistics(self, annotations: List[ImageAnnotation]) -> Dict:
        """收集统计数据"""
        stats = {
            'total_images': len(annotations),
            'total_boxes': 0,
            'total_polygons': 0,
            'class_counts': Counter(),
            'image_sizes': [],
            'bbox_sizes': [],
            'annotations_per_image': [],
            'aspect_ratios': []
        }
        
        for ann in annotations:
            # 图片尺寸
            stats['image_sizes'].append((ann.width, ann.height))
            stats['aspect_ratios'].append(ann.width / ann.height if ann.height > 0 else 1.0)
            
            # 标注数量
            box_count = len(ann.boxes) if ann.boxes else 0
            poly_count = len(ann.polygons) if ann.polygons else 0
            stats['annotations_per_image'].append(box_count + poly_count)
            
            # 矩形框统计
            if ann.boxes:
                stats['total_boxes'] += len(ann.boxes)
                for box in ann.boxes:
                    stats['class_counts'][box.label] += 1
                    width = box.xmax - box.xmin
                    height = box.ymax - box.ymin
                    stats['bbox_sizes'].append((width, height))
            
            # 多边形统计
            if ann.polygons:
                stats['total_polygons'] += len(ann.polygons)
                for poly in ann.polygons:
                    stats['class_counts'][poly.label] += 1
        
        return stats
    
    def _plot_class_distribution_pie(self, class_counts: Counter, ax, theme: str):
        """绘制类别分布饼图"""
        if not class_counts:
            ax.text(0.5, 0.5, '无数据', ha='center', va='center', transform=ax.transAxes)
            return
        
        labels = list(class_counts.keys())
        sizes = list(class_counts.values())
        colors = [f'C{i}' for i in range(len(labels))]
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                         colors=colors, startangle=90)
        
        ax.set_title('类别分布', fontsize=14, fontweight='bold')
        
        # 调整文本颜色
        text_color = 'white' if theme == 'dark' else 'black'
        for text in texts + autotexts:
            text.set_color(text_color)
    
    def _plot_class_distribution_bar(self, class_counts: Counter, ax, theme: str):
        """绘制类别分布柱状图"""
        if not class_counts:
            ax.text(0.5, 0.5, '无数据', ha='center', va='center', transform=ax.transAxes)
            return
        
        labels = list(class_counts.keys())
        counts = list(class_counts.values())
        
        bars = ax.bar(range(len(labels)), counts, color=sns.color_palette("husl", len(labels)))
        ax.set_xlabel('类别')
        ax.set_ylabel('数量')
        ax.set_title('类别统计', fontsize=14, fontweight='bold')
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha='right')
        
        # 在柱子上显示数值
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(counts)*0.01,
                   f'{count}', ha='center', va='bottom')
    
    def _plot_image_size_distribution(self, image_sizes: List[Tuple[int, int]], ax, theme: str):
        """绘制图片尺寸分布"""
        if not image_sizes:
            ax.text(0.5, 0.5, '无数据', ha='center', va='center', transform=ax.transAxes)
            return
        
        widths, heights = zip(*image_sizes)
        
        # 创建2D直方图
        ax.hist2d(widths, heights, bins=20, cmap='Blues', alpha=0.7)
        ax.set_xlabel('宽度 (像素)')
        ax.set_ylabel('高度 (像素)')
        ax.set_title('图片尺寸分布', fontsize=14, fontweight='bold')
        
        # 添加颜色条
        plt.colorbar(ax.collections[0], ax=ax, label='图片数量')
    
    def _plot_bbox_size_distribution(self, bbox_sizes: List[Tuple[int, int]], ax, theme: str):
        """绘制标注框尺寸分布"""
        if not bbox_sizes:
            ax.text(0.5, 0.5, '无数据', ha='center', va='center', transform=ax.transAxes)
            return
        
        widths, heights = zip(*bbox_sizes)
        
        ax.scatter(widths, heights, alpha=0.6, s=10)
        ax.set_xlabel('标注框宽度')
        ax.set_ylabel('标注框高度')
        ax.set_title('标注框尺寸分布', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
    
    def _plot_annotations_per_image(self, annotations_per_image: List[int], ax, theme: str):
        """绘制每张图片标注数量分布"""
        if not annotations_per_image:
            ax.text(0.5, 0.5, '无数据', ha='center', va='center', transform=ax.transAxes)
            return
        
        ax.hist(annotations_per_image, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        ax.set_xlabel('每张图片标注数量')
        ax.set_ylabel('图片数量')
        ax.set_title('标注数量分布', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # 添加统计信息
        mean_annotations = np.mean(annotations_per_image)
        ax.axvline(mean_annotations, color='red', linestyle='--', 
                  label=f'平均值: {mean_annotations:.1f}')
        ax.legend()
    
    def _plot_annotation_density_heatmap(self, annotations: List[ImageAnnotation], ax, theme: str):
        """绘制标注密度热力图"""
        if not annotations:
            ax.text(0.5, 0.5, '无数据', ha='center', va='center', transform=ax.transAxes)
            return
        
        # 创建密度网格
        grid_size = 20
        density_grid = np.zeros((grid_size, grid_size))
        
        for ann in annotations:
            if not ann.boxes or ann.width <= 0 or ann.height <= 0:
                continue
                
            for box in ann.boxes:
                # 计算标注框中心点的归一化坐标
                center_x = (box.xmin + box.xmax) / 2 / ann.width
                center_y = (box.ymin + box.ymax) / 2 / ann.height
                
                # 映射到网格
                grid_x = int(center_x * (grid_size - 1))
                grid_y = int(center_y * (grid_size - 1))
                
                if 0 <= grid_x < grid_size and 0 <= grid_y < grid_size:
                    density_grid[grid_y, grid_x] += 1
        
        # 绘制热力图
        im = ax.imshow(density_grid, cmap='hot', interpolation='bilinear')
        ax.set_title('标注密度热力图', fontsize=14, fontweight='bold')
        ax.set_xlabel('图片宽度方向')
        ax.set_ylabel('图片高度方向')
        
        # 添加颜色条
        plt.colorbar(im, ax=ax, label='标注密度')
    
    def _plot_aspect_ratio_distribution(self, aspect_ratios: List[float], ax, theme: str):
        """绘制宽高比分布"""
        if not aspect_ratios:
            ax.text(0.5, 0.5, '无数据', ha='center', va='center', transform=ax.transAxes)
            return
        
        ax.hist(aspect_ratios, bins=30, alpha=0.7, color='lightgreen', edgecolor='black')
        ax.set_xlabel('宽高比')
        ax.set_ylabel('图片数量')
        ax.set_title('图片宽高比分布', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # 标记常见比例
        common_ratios = [1.0, 4/3, 16/9, 3/2]
        ratio_names = ['1:1', '4:3', '16:9', '3:2']
        
        for ratio, name in zip(common_ratios, ratio_names):
            if min(aspect_ratios) <= ratio <= max(aspect_ratios):
                ax.axvline(ratio, color='red', linestyle='--', alpha=0.7)
                ax.text(ratio, ax.get_ylim()[1] * 0.9, name, 
                       rotation=90, ha='right', va='top')
    
    def _plot_dataset_summary_table(self, stats: Dict, ax, theme: str):
        """绘制数据集概览表格"""
        ax.axis('off')
        
        # 准备表格数据
        table_data = [
            ['总图片数', f"{stats['total_images']:,}"],
            ['总矩形框数', f"{stats['total_boxes']:,}"],
            ['总多边形数', f"{stats['total_polygons']:,}"],
            ['类别数量', f"{len(stats['class_counts']):,}"],
            ['平均每图标注数', f"{np.mean(stats['annotations_per_image']):.1f}" if stats['annotations_per_image'] else "0"],
            ['最大图片尺寸', f"{max(w for w, h in stats['image_sizes'])}x{max(h for w, h in stats['image_sizes'])}" if stats['image_sizes'] else "N/A"],
            ['最小图片尺寸', f"{min(w for w, h in stats['image_sizes'])}x{min(h for w, h in stats['image_sizes'])}" if stats['image_sizes'] else "N/A"]
        ]
        
        # 创建表格
        table = ax.table(cellText=table_data,
                        colLabels=['指标', '数值'],
                        cellLoc='center',
                        loc='center',
                        colWidths=[0.6, 0.4])
        
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        # 设置表格样式
        table[(0, 0)].set_facecolor('#4CAF50')
        table[(0, 1)].set_facecolor('#4CAF50')
        
        for i in range(1, len(table_data) + 1):
            table[(i, 0)].set_facecolor('#E8F5E8')
            table[(i, 1)].set_facecolor('#F5F5F5')
        
        ax.set_title('数据集概览', fontsize=14, fontweight='bold')
    
    def _plot_class_cooccurrence_matrix(self, annotations: List[ImageAnnotation], ax, theme: str):
        """绘制类别共现矩阵"""
        # 收集类别共现数据
        class_names = set()
        for ann in annotations:
            for box in ann.boxes:
                class_names.add(box.label)
            if ann.polygons:
                for poly in ann.polygons:
                    class_names.add(poly.label)
        
        class_names = sorted(list(class_names))
        
        if len(class_names) < 2:
            ax.text(0.5, 0.5, '类别数量不足', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('类别共现矩阵', fontsize=14, fontweight='bold')
            return
        
        # 创建共现矩阵
        cooccurrence_matrix = np.zeros((len(class_names), len(class_names)))
        
        for ann in annotations:
            image_classes = set()
            for box in ann.boxes:
                image_classes.add(box.label)
            if ann.polygons:
                for poly in ann.polygons:
                    image_classes.add(poly.label)
            
            # 更新共现矩阵
            for class1 in image_classes:
                for class2 in image_classes:
                    i = class_names.index(class1)
                    j = class_names.index(class2)
                    cooccurrence_matrix[i, j] += 1
        
        # 绘制热力图
        sns.heatmap(cooccurrence_matrix, 
                   xticklabels=class_names, 
                   yticklabels=class_names,
                   annot=True, 
                   fmt='.0f',
                   cmap='Blues',
                   ax=ax)
        
        ax.set_title('类别共现矩阵', fontsize=14, fontweight='bold')
        ax.set_xlabel('类别')
        ax.set_ylabel('类别')
    
    def create_interactive_visualization(self, annotations: List[ImageAnnotation], 
                                       output_dir: Path) -> None:
        """创建交互式可视化HTML页面"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 收集数据
        stats = self._collect_statistics(annotations)
        
        # 生成HTML内容
        html_content = self._generate_interactive_html(stats)
        
        # 保存HTML文件
        html_file = output_dir / "interactive_visualization.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"交互式可视化页面已保存: {html_file}")
    
    def _generate_interactive_html(self, stats: Dict) -> str:
        """生成交互式HTML页面"""
        # 准备数据
        class_labels = list(stats['class_counts'].keys())
        class_counts = list(stats['class_counts'].values())
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>数据集可视化仪表板</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .chart-container {{ background: white; margin: 20px 0; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
                .stat-card {{ background: white; padding: 20px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .stat-number {{ font-size: 2em; font-weight: bold; color: #2196F3; }}
                .stat-label {{ color: #666; margin-top: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>数据集可视化仪表板</h1>
                    <p>交互式数据分析与统计</p>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">{stats['total_images']:,}</div>
                        <div class="stat-label">总图片数</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{stats['total_boxes']:,}</div>
                        <div class="stat-label">总矩形框数</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{stats['total_polygons']:,}</div>
                        <div class="stat-label">总多边形数</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{len(stats['class_counts']):,}</div>
                        <div class="stat-label">类别数量</div>
                    </div>
                </div>
                
                <div class="chart-container">
                    <div id="class-distribution-pie"></div>
                </div>
                
                <div class="chart-container">
                    <div id="class-distribution-bar"></div>
                </div>
                
                <div class="chart-container">
                    <div id="annotations-histogram"></div>
                </div>
            </div>
            
            <script>
                // 类别分布饼图
                var pieData = [{{
                    values: {class_counts},
                    labels: {class_labels},
                    type: 'pie',
                    hole: 0.4,
                    textinfo: 'label+percent',
                    textposition: 'outside'
                }}];
                
                var pieLayout = {{
                    title: '类别分布饼图',
                    font: {{ size: 14 }}
                }};
                
                Plotly.newPlot('class-distribution-pie', pieData, pieLayout);
                
                // 类别分布柱状图
                var barData = [{{
                    x: {class_labels},
                    y: {class_counts},
                    type: 'bar',
                    marker: {{ color: 'rgba(33, 150, 243, 0.8)' }}
                }}];
                
                var barLayout = {{
                    title: '类别统计柱状图',
                    xaxis: {{ title: '类别' }},
                    yaxis: {{ title: '数量' }}
                }};
                
                Plotly.newPlot('class-distribution-bar', barData, barLayout);
                
                // 标注数量分布直方图
                var histData = [{{
                    x: {stats['annotations_per_image']},
                    type: 'histogram',
                    nbinsx: 20,
                    marker: {{ color: 'rgba(76, 175, 80, 0.8)' }}
                }}];
                
                var histLayout = {{
                    title: '每张图片标注数量分布',
                    xaxis: {{ title: '标注数量' }},
                    yaxis: {{ title: '图片数量' }}
                }};
                
                Plotly.newPlot('annotations-histogram', histData, histLayout);
            </script>
        </body>
        </html>
        """
        
        return html