from pathlib import Path
from typing import List, Dict
import shutil
import random

class DatasetOrganizer:
    """数据集整理器"""
    
    def rename_files(self, dataset_dir: Path, prefix: str = "img", start_index: int = 0):
        """批量重命名文件"""
        image_files = list(dataset_dir.glob('*.jpg')) + list(dataset_dir.glob('*.png'))
        
        for i, img_file in enumerate(image_files):
            new_name = f"{prefix}_{start_index + i:06d}{img_file.suffix}"
            new_img_path = dataset_dir / new_name
            
            # 重命名图片
            img_file.rename(new_img_path)
            
            # 重命名对应的标注文件
            txt_file = img_file.with_suffix('.txt')
            if txt_file.exists():
                new_txt_name = f"{prefix}_{start_index + i:06d}.txt"
                txt_file.rename(dataset_dir / new_txt_name)
    
    def split_dataset(self, dataset_dir: Path, output_dir: Path, 
                     train_ratio: float = 0.7, val_ratio: float = 0.2, 
                     test_ratio: float = 0.1):
        """划分数据集为训练/验证/测试集"""
        
        # 创建输出目录
        train_dir = output_dir / 'train'
        val_dir = output_dir / 'val' 
        test_dir = output_dir / 'test'
        
        for dir_path in [train_dir, val_dir, test_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # 获取所有图片文件
        image_files = list(dataset_dir.glob('*.jpg')) + list(dataset_dir.glob('*.png'))
        random.shuffle(image_files)
        
        total = len(image_files)
        train_count = int(total * train_ratio)
        val_count = int(total * val_ratio)
        
        # 分配文件
        train_files = image_files[:train_count]
        val_files = image_files[train_count:train_count + val_count]
        test_files = image_files[train_count + val_count:]
        
        # 复制文件
        self._copy_files(train_files, dataset_dir, train_dir)
        self._copy_files(val_files, dataset_dir, val_dir)
        self._copy_files(test_files, dataset_dir, test_dir)
        
        return {
            'train': len(train_files),
            'val': len(val_files),
            'test': len(test_files)
        }
    
    def _copy_files(self, file_list: List[Path], src_dir: Path, dst_dir: Path):
        """复制文件列表"""
        for img_file in file_list:
            # 复制图片
            shutil.copy2(img_file, dst_dir / img_file.name)
            
            # 复制标注文件
            txt_file = img_file.with_suffix('.txt')
            if txt_file.exists():
                shutil.copy2(txt_file, dst_dir / txt_file.name)
    
    def merge_datasets(self, dataset_dirs: List[Path], output_dir: Path):
        """合并多个数据集"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        file_counter = 0
        
        for dataset_dir in dataset_dirs:
            image_files = list(dataset_dir.glob('*.jpg')) + list(dataset_dir.glob('*.png'))
            
            for img_file in image_files:
                # 生成新文件名
                new_name = f"merged_{file_counter:06d}{img_file.suffix}"
                
                # 复制图片
                shutil.copy2(img_file, output_dir / new_name)
                
                # 复制标注文件
                txt_file = img_file.with_suffix('.txt')
                if txt_file.exists():
                    new_txt_name = f"merged_{file_counter:06d}.txt"
                    shutil.copy2(txt_file, output_dir / new_txt_name)
                
                file_counter += 1
        
        return file_counter