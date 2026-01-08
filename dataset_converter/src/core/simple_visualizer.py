"""
简化的数据可视化器（不依赖matplotlib）
"""
from pathlib import Path
from typing import List, Dict, Optional
import json
from collections import Counter
import colorsys

from .base_parser import ImageAnnotation


class SimpleVisualizer:
    """简化的数据可视化器"""
    
    def __init__(self):
        self.colors = self._generate_colors(50)
        self.class_colors = {}
    
    def _generate_colors(self, num_colors: int) -> List[str]:
        """生成不同的颜色"""
        colors = []
        for i in range(num_colors):
            hue = i / num_colors
            saturation = 0.7 + (i % 3) * 0.1
            value = 0.8 + (i % 2) * 0.2
            rgb = colorsys.hsv_to_rgb(hue, saturation, value)
            hex_color = '#{:02x}{:02x}{:02x}'.format(
                int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)
            )
            colors.append(hex_color)
        return colors
    
    def get_class_color(self, class_name: str) -> str:
        """获取类别对应的颜色"""
        if class_name not in self.class_colors:
            color_idx = len(self.class_colors) % len(self.colors)
            self.class_colors[class_name] = self.colors[color_idx]
        return self.class_colors[class_name]
    
    def create_statistics_report(self, annotations: List[ImageAnnotation], 
                               output_dir: Path) -> None:
        """创建统计报告"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 收集统计数据
        stats = self._collect_statistics(annotations)
        
        # 生成HTML报告
        html_content = self._generate_html_report(stats)
        
        # 保存HTML文件
        html_file = output_dir / "statistics_report.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # 保存JSON数据
        json_file = output_dir / "statistics_data.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"统计报告已保存: {html_file}")
        print(f"统计数据已保存: {json_file}")
    
    def _collect_statistics(self, annotations: List[ImageAnnotation]) -> Dict:
        """收集统计数据"""
        stats = {
            'total_images': len(annotations),
            'total_boxes': 0,
            'total_polygons': 0,
            'class_counts': {},
            'image_sizes': [],
            'bbox_sizes': [],
            'annotations_per_image': [],
            'aspect_ratios': []
        }
        
        class_counter = Counter()
        
        for ann in annotations:
            # 图片尺寸
            stats['image_sizes'].append({'width': ann.width, 'height': ann.height})
            if ann.height > 0:
                stats['aspect_ratios'].append(ann.width / ann.height)
            
            # 标注数量
            box_count = len(ann.boxes) if ann.boxes else 0
            poly_count = len(ann.polygons) if ann.polygons else 0
            stats['annotations_per_image'].append(box_count + poly_count)
            
            # 矩形框统计
            if ann.boxes:
                stats['total_boxes'] += len(ann.boxes)
                for box in ann.boxes:
                    class_counter[box.label] += 1
                    width = box.xmax - box.xmin
                    height = box.ymax - box.ymin
                    stats['bbox_sizes'].append({'width': width, 'height': height})
            
            # 多边形统计
            if ann.polygons:
                stats['total_polygons'] += len(ann.polygons)
                for poly in ann.polygons:
                    class_counter[poly.label] += 1
        
        # 转换Counter为普通字典
        stats['class_counts'] = dict(class_counter)
        
        return stats
    
    def _generate_html_report(self, stats: Dict) -> str:
        """生成HTML报告"""
        # 准备图表数据
        class_labels = list(stats['class_counts'].keys())
        class_counts = list(stats['class_counts'].values())
        class_colors = [self.get_class_color(label) for label in class_labels]
        
        # 计算统计指标
        avg_annotations = sum(stats['annotations_per_image']) / len(stats['annotations_per_image']) if stats['annotations_per_image'] else 0
        avg_aspect_ratio = sum(stats['aspect_ratios']) / len(stats['aspect_ratios']) if stats['aspect_ratios'] else 0
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>数据集统计报告</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{ 
                    font-family: 'Microsoft YaHei', Arial, sans-serif; 
                    margin: 20px; 
                    background-color: #f5f5f5; 
                }}
                .container {{ 
                    max-width: 1200px; 
                    margin: 0 auto; 
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{ 
                    text-align: center; 
                    margin-bottom: 30px; 
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border-radius: 10px;
                }}
                .stats-grid {{ 
                    display: grid; 
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                    gap: 20px; 
                    margin: 30px 0; 
                }}
                .stat-card {{ 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 25px; 
                    border-radius: 10px; 
                    text-align: center; 
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                    transition: transform 0.3s ease;
                }}
                .stat-card:hover {{
                    transform: translateY(-5px);
                }}
                .stat-number {{ 
                    font-size: 2.5em; 
                    font-weight: bold; 
                    margin-bottom: 10px;
                }}
                .stat-label {{ 
                    font-size: 1.1em;
                    opacity: 0.9;
                }}
                .chart-container {{ 
                    background: white; 
                    margin: 30px 0; 
                    padding: 25px; 
                    border-radius: 10px; 
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
                }}
                .chart-title {{
                    font-size: 1.5em;
                    font-weight: bold;
                    margin-bottom: 20px;
                    color: #333;
                    text-align: center;
                }}
                .class-list {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin: 20px 0;
                }}
                .class-item {{
                    display: flex;
                    align-items: center;
                    padding: 10px;
                    background: #f8f9fa;
                    border-radius: 8px;
                    border-left: 4px solid;
                }}
                .class-color {{
                    width: 20px;
                    height: 20px;
                    border-radius: 50%;
                    margin-right: 10px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 40px;
                    padding: 20px;
                    color: #666;
                    border-top: 1px solid #eee;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 数据集统计报告</h1>
                    <p>全面的数据集分析与可视化</p>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">{stats['total_images']:,}</div>
                        <div class="stat-label">📷 总图片数</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{stats['total_boxes']:,}</div>
                        <div class="stat-label">📦 总矩形框数</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{stats['total_polygons']:,}</div>
                        <div class="stat-label">🔷 总多边形数</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{len(stats['class_counts']):,}</div>
                        <div class="stat-label">🏷️ 类别数量</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{avg_annotations:.1f}</div>
                        <div class="stat-label">📊 平均标注数</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{avg_aspect_ratio:.2f}</div>
                        <div class="stat-label">📐 平均宽高比</div>
                    </div>
                </div>
                
                <div class="chart-container">
                    <div class="chart-title">🎯 类别分布</div>
                    <div class="class-list">
        """
        
        # 添加类别列表
        for i, (label, count) in enumerate(stats['class_counts'].items()):
            color = class_colors[i] if i < len(class_colors) else '#666'
            percentage = (count / sum(class_counts)) * 100 if class_counts else 0
            html += f"""
                        <div class="class-item" style="border-left-color: {color}">
                            <div class="class-color" style="background-color: {color}"></div>
                            <div>
                                <strong>{label}</strong><br>
                                <small>{count} 个 ({percentage:.1f}%)</small>
                            </div>
                        </div>
            """
        
        html += """
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
                
                <div class="footer">
                    <p>📅 报告生成时间: <span id="current-time"></span></p>
                    <p>🛠️ 由DataForge生成</p>
                </div>
            </div>
            
            <script>
                // 设置当前时间
                document.getElementById('current-time').textContent = new Date().toLocaleString('zh-CN');
                
                // 类别分布饼图
                var pieData = [{
                    values: """ + str(class_counts) + """,
                    labels: """ + str(class_labels) + """,
                    type: 'pie',
                    hole: 0.4,
                    textinfo: 'label+percent',
                    textposition: 'outside',
                    marker: {
                        colors: """ + str(class_colors) + """
                    }
                }];
                
                var pieLayout = {
                    title: {
                        text: '类别分布饼图',
                        font: { size: 18, family: 'Microsoft YaHei' }
                    },
                    font: { family: 'Microsoft YaHei' },
                    showlegend: true,
                    legend: { orientation: 'h', y: -0.2 }
                };
                
                Plotly.newPlot('class-distribution-pie', pieData, pieLayout, {responsive: true});
                
                // 类别分布柱状图
                var barData = [{
                    x: """ + str(class_labels) + """,
                    y: """ + str(class_counts) + """,
                    type: 'bar',
                    marker: { 
                        color: """ + str(class_colors) + """,
                        line: { color: 'rgba(0,0,0,0.2)', width: 1 }
                    }
                }];
                
                var barLayout = {
                    title: {
                        text: '类别统计柱状图',
                        font: { size: 18, family: 'Microsoft YaHei' }
                    },
                    xaxis: { 
                        title: '类别',
                        font: { family: 'Microsoft YaHei' }
                    },
                    yaxis: { 
                        title: '数量',
                        font: { family: 'Microsoft YaHei' }
                    },
                    font: { family: 'Microsoft YaHei' }
                };
                
                Plotly.newPlot('class-distribution-bar', barData, barLayout, {responsive: true});
                
                // 标注数量分布直方图
                var histData = [{
                    x: """ + str(stats['annotations_per_image']) + """,
                    type: 'histogram',
                    nbinsx: 20,
                    marker: { 
                        color: 'rgba(76, 175, 80, 0.8)',
                        line: { color: 'rgba(76, 175, 80, 1)', width: 1 }
                    }
                }];
                
                var histLayout = {
                    title: {
                        text: '每张图片标注数量分布',
                        font: { size: 18, family: 'Microsoft YaHei' }
                    },
                    xaxis: { 
                        title: '标注数量',
                        font: { family: 'Microsoft YaHei' }
                    },
                    yaxis: { 
                        title: '图片数量',
                        font: { family: 'Microsoft YaHei' }
                    },
                    font: { family: 'Microsoft YaHei' }
                };
                
                Plotly.newPlot('annotations-histogram', histData, histLayout, {responsive: true});
            </script>
        </body>
        </html>
        """
        
        return html