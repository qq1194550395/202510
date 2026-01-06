from pathlib import Path
from typing import List, Tuple
import random
import math
from PIL import Image, ImageEnhance, ImageFilter

class DataAugmentor:
    """数据增强器"""
    
    def __init__(self):
        self.augmentation_methods = {
            'brightness': self._adjust_brightness,
            'contrast': self._adjust_contrast,
            'saturation': self._adjust_saturation,
            'blur': self._apply_blur,
            'noise': self._add_noise,
            'flip_horizontal': self._flip_horizontal,
            'rotate': self._rotate_image
        }
    
    def augment_dataset(self, input_dir: Path, output_dir: Path, 
                       augmentations: List[str], multiplier: int = 2):
        """对数据集进行增强"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 获取所有图片文件
        image_files = list(input_dir.glob('*.jpg')) + list(input_dir.glob('*.png'))
        
        for img_file in image_files:
            # 复制原始文件
            self._copy_original(img_file, input_dir, output_dir)
            
            # 生成增强版本
            for i in range(multiplier - 1):
                self._create_augmented_version(img_file, input_dir, output_dir, 
                                             augmentations, i + 1)
    
    def _copy_original(self, img_file: Path, input_dir: Path, output_dir: Path):
        """复制原始文件"""
        # 复制图片
        img = Image.open(img_file)
        img.save(output_dir / img_file.name)
        
        # 复制标注文件
        txt_file = img_file.with_suffix('.txt')
        if txt_file.exists():
            content = txt_file.read_text(encoding='utf-8')
            (output_dir / txt_file.name).write_text(content, encoding='utf-8')
    
    def _create_augmented_version(self, img_file: Path, input_dir: Path, 
                                output_dir: Path, augmentations: List[str], version: int):
        """创建增强版本"""
        img = Image.open(img_file)
        
        # 随机选择增强方法
        selected_augs = random.sample(augmentations, 
                                    min(len(augmentations), random.randint(1, 3)))
        
        # 应用增强
        for aug in selected_augs:
            if aug in self.augmentation_methods:
                img = self.augmentation_methods[aug](img)
        
        # 保存增强后的图片
        stem = img_file.stem
        suffix = img_file.suffix
        new_name = f"{stem}_aug{version}{suffix}"
        img.save(output_dir / new_name)
        
        # 复制对应的标注文件
        txt_file = img_file.with_suffix('.txt')
        if txt_file.exists():
            content = txt_file.read_text(encoding='utf-8')
            new_txt_name = f"{stem}_aug{version}.txt"
            (output_dir / new_txt_name).write_text(content, encoding='utf-8')
    
    def _adjust_brightness(self, img: Image.Image) -> Image.Image:
        enhancer = ImageEnhance.Brightness(img)
        factor = random.uniform(0.7, 1.3)
        return enhancer.enhance(factor)
    
    def _adjust_contrast(self, img: Image.Image) -> Image.Image:
        enhancer = ImageEnhance.Contrast(img)
        factor = random.uniform(0.8, 1.2)
        return enhancer.enhance(factor)
    
    def _adjust_saturation(self, img: Image.Image) -> Image.Image:
        enhancer = ImageEnhance.Color(img)
        factor = random.uniform(0.8, 1.2)
        return enhancer.enhance(factor)
    
    def _apply_blur(self, img: Image.Image) -> Image.Image:
        radius = random.uniform(0.5, 2.0)
        return img.filter(ImageFilter.GaussianBlur(radius=radius))
    
    def _add_noise(self, img: Image.Image) -> Image.Image:
        # 简单的噪声添加（实际实现可能需要numpy）
        return img
    
    def _flip_horizontal(self, img: Image.Image) -> Image.Image:
        return img.transpose(Image.FLIP_LEFT_RIGHT)
    
    def _rotate_image(self, img: Image.Image) -> Image.Image:
        angle = random.uniform(-15, 15)
        return img.rotate(angle, expand=True, fillcolor=(0, 0, 0))