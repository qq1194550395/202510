from pathlib import Path
from typing import List, Tuple, Dict
import random
from PIL import Image, ImageDraw, ImageFont
import colorsys

class AnnotationVisualizer:
    """标注可视化器"""
    
    def __init__(self):
        self.colors = self._generate_colors(50)  # 生成50种不同颜色
        self.class_colors = {}
    
    def _generate_colors(self, num_colors: int) -> List[Tuple[int, int, int]]:
        """生成不同的颜色"""
        colors = []
        for i in range(num_colors):
            hue = i / num_colors
            saturation = 0.7 + (i % 3) * 0.1  # 0.7, 0.8, 0.9
            value = 0.8 + (i % 2) * 0.2       # 0.8, 1.0
            rgb = colorsys.hsv_to_rgb(hue, saturation, value)
            colors.append(tuple(int(c * 255) for c in rgb))
        return colors
    
    def get_class_color(self, class_name: str) -> Tuple[int, int, int]:
        """获取类别对应的颜色"""
        if class_name not in self.class_colors:
            color_idx = len(self.class_colors) % len(self.colors)
            self.class_colors[class_name] = self.colors[color_idx]
        return self.class_colors[class_name]
    
    def visualize_yolo_annotations(self, image_path: Path, annotation_path: Path, 
                                 output_path: Path, show_labels: bool = True):
        """可视化YOLO格式标注"""
        try:
            # 读取图片
            image = Image.open(image_path)
            width, height = image.size
            draw = ImageDraw.Draw(image)
            
            # 尝试加载字体
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except:
                font = ImageFont.load_default()
            
            # 读取标注
            if annotation_path.exists():
                content = annotation_path.read_text(encoding='utf-8').strip()
                if content:
                    for line in content.split('\n'):
                        parts = line.strip().split()
                        if len(parts) < 5:
                            continue
                        
                        class_id = parts[0]
                        color = self.get_class_color(class_id)
                        
                        if len(parts) == 5:
                            # 矩形框
                            self._draw_bbox(draw, parts[1:], width, height, color, class_id, font, show_labels)
                        else:
                            # 多边形
                            self._draw_polygon(draw, parts[1:], width, height, color, class_id, font, show_labels)
            
            # 保存结果
            image.save(output_path)
            return True
            
        except Exception as e:
            print(f"可视化失败: {e}")
            return False
    
    def _draw_bbox(self, draw: ImageDraw.Draw, coords: List[str], width: int, height: int,
                   color: Tuple[int, int, int], class_id: str, font, show_labels: bool):
        """绘制矩形框"""
        cx, cy, w, h = map(float, coords)
        
        # 转换为像素坐标
        x1 = int((cx - w/2) * width)
        y1 = int((cy - h/2) * height)
        x2 = int((cx + w/2) * width)
        y2 = int((cy + h/2) * height)
        
        # 绘制矩形框
        draw.rectangle([x1, y1, x2, y2], outline=color, width=2)
        
        # 绘制标签
        if show_labels:
            label_bg = [x1, y1-20, x1+len(class_id)*10, y1]
            draw.rectangle(label_bg, fill=color)
            draw.text((x1+2, y1-18), class_id, fill='white', font=font)
    
    def _draw_polygon(self, draw: ImageDraw.Draw, coords: List[str], width: int, height: int,
                      color: Tuple[int, int, int], class_id: str, font, show_labels: bool):
        """绘制多边形"""
        coords_float = [float(x) for x in coords]
        if len(coords_float) % 2 != 0 or len(coords_float) < 6:
            return
        
        # 转换为像素坐标
        points = []
        for i in range(0, len(coords_float), 2):
            x = int(coords_float[i] * width)
            y = int(coords_float[i+1] * height)
            points.append((x, y))
        
        # 绘制多边形
        draw.polygon(points, outline=color, width=2)
        
        # 绘制标签（在多边形中心）
        if show_labels and points:
            center_x = sum(p[0] for p in points) // len(points)
            center_y = sum(p[1] for p in points) // len(points)
            
            label_bg = [center_x-20, center_y-10, center_x+20, center_y+10]
            draw.rectangle(label_bg, fill=color)
            draw.text((center_x-15, center_y-8), class_id, fill='white', font=font)
    
    def create_dataset_preview(self, dataset_dir: Path, output_dir: Path, 
                             max_images: int = 20, grid_size: Tuple[int, int] = (4, 5)):
        """创建数据集预览图"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 获取图片文件
        image_files = list(dataset_dir.glob('*.jpg')) + list(dataset_dir.glob('*.png'))
        selected_files = random.sample(image_files, min(len(image_files), max_images))
        
        # 创建网格预览
        grid_width, grid_height = grid_size
        cell_size = 200
        
        preview_img = Image.new('RGB', 
                               (grid_width * cell_size, grid_height * cell_size), 
                               'white')
        
        for i, img_file in enumerate(selected_files[:grid_width * grid_height]):
            row = i // grid_width
            col = i % grid_width
            
            # 加载并调整图片大小
            img = Image.open(img_file)
            img.thumbnail((cell_size-10, cell_size-10), Image.Resampling.LANCZOS)
            
            # 可视化标注
            txt_file = img_file.with_suffix('.txt')
            if txt_file.exists():
                temp_path = output_dir / f"temp_{i}.jpg"
                self.visualize_yolo_annotations(img_file, txt_file, temp_path, show_labels=False)
                img = Image.open(temp_path)
                img.thumbnail((cell_size-10, cell_size-10), Image.Resampling.LANCZOS)
                temp_path.unlink()  # 删除临时文件
            
            # 粘贴到预览图
            x = col * cell_size + 5
            y = row * cell_size + 5
            preview_img.paste(img, (x, y))
        
        # 保存预览图
        preview_path = output_dir / "dataset_preview.jpg"
        preview_img.save(preview_path)
        return preview_path