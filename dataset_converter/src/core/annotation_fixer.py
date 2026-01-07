from pathlib import Path
from typing import List, Dict, Tuple
import shutil
from PIL import Image

class AnnotationFixer:
    """标注修复器"""
    
    def __init__(self):
        self.fixes_applied = []
        self.backup_dir = None
    
    def fix_dataset(self, dataset_dir: Path, create_backup: bool = True) -> Dict:
        """修复数据集中的问题"""
        if create_backup:
            self.backup_dir = dataset_dir.parent / f"{dataset_dir.name}_backup"
            self._create_backup(dataset_dir, self.backup_dir)
        
        fixes = {
            'coordinate_fixes': 0,
            'missing_annotations_created': 0,
            'invalid_files_removed': 0,
            'empty_annotations_fixed': 0,
            'duplicate_files_removed': 0
        }
        
        image_files = list(dataset_dir.glob('*.jpg')) + list(dataset_dir.glob('*.png'))
        
        for img_file in image_files:
            # 检查图片是否有效
            if not self._is_valid_image(img_file):
                img_file.unlink()
                txt_file = img_file.with_suffix('.txt')
                if txt_file.exists():
                    txt_file.unlink()
                fixes['invalid_files_removed'] += 1
                continue
            
            txt_file = img_file.with_suffix('.txt')
            
            # 创建缺失的标注文件
            if not txt_file.exists():
                txt_file.write_text('', encoding='utf-8')
                fixes['missing_annotations_created'] += 1
                continue
            
            # 修复标注文件
            fixed_content = self._fix_annotation_file(txt_file, img_file)
            if fixed_content is not None:
                txt_file.write_text(fixed_content, encoding='utf-8')
                fixes['coordinate_fixes'] += 1
        
        # 移除重复文件
        duplicates = self._find_and_remove_duplicates(dataset_dir)
        fixes['duplicate_files_removed'] = len(duplicates)
        
        return fixes
    
    def _create_backup(self, src_dir: Path, backup_dir: Path):
        """创建备份"""
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        shutil.copytree(src_dir, backup_dir)
    
    def _is_valid_image(self, img_file: Path) -> bool:
        """检查图片是否有效"""
        try:
            with Image.open(img_file) as img:
                img.verify()
            return True
        except:
            return False
    
    def _fix_annotation_file(self, txt_file: Path, img_file: Path) -> str:
        """修复标注文件"""
        try:
            content = txt_file.read_text(encoding='utf-8').strip()
            if not content:
                return ''  # 空文件保持空
            
            # 获取图片尺寸
            with Image.open(img_file) as img:
                width, height = img.size
            
            lines = content.split('\n')
            fixed_lines = []
            has_fixes = False
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split()
                if len(parts) < 5:
                    continue  # 跳过格式错误的行
                
                try:
                    class_id = parts[0]
                    coords = [float(x) for x in parts[1:]]
                    
                    # 修复坐标范围
                    fixed_coords = []
                    for coord in coords:
                        if coord < 0:
                            fixed_coords.append(0.0)
                            has_fixes = True
                        elif coord > 1:
                            fixed_coords.append(1.0)
                            has_fixes = True
                        else:
                            fixed_coords.append(coord)
                    
                    # 重建行
                    coord_str = ' '.join(f'{c:.6f}' for c in fixed_coords)
                    fixed_lines.append(f'{class_id} {coord_str}')
                    
                except ValueError:
                    continue  # 跳过无法解析的行
            
            if has_fixes:
                return '\n'.join(fixed_lines)
            else:
                return None  # 没有修复，不需要重写文件
                
        except Exception:
            return ''  # 出错时返回空内容
    
    def _find_and_remove_duplicates(self, dataset_dir: Path) -> List[str]:
        """查找并移除重复文件"""
        from collections import defaultdict
        import hashlib
        
        file_hashes = defaultdict(list)
        image_files = list(dataset_dir.glob('*.jpg')) + list(dataset_dir.glob('*.png'))
        
        # 计算文件哈希
        for img_file in image_files:
            try:
                with open(img_file, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                file_hashes[file_hash].append(img_file)
            except:
                continue
        
        # 移除重复文件
        removed_files = []
        for file_hash, files in file_hashes.items():
            if len(files) > 1:
                # 保留第一个，删除其余的
                for duplicate_file in files[1:]:
                    # 删除图片和对应的标注文件
                    duplicate_file.unlink()
                    txt_file = duplicate_file.with_suffix('.txt')
                    if txt_file.exists():
                        txt_file.unlink()
                    removed_files.append(duplicate_file.name)
        
        return removed_files
    
    def normalize_class_ids(self, dataset_dir: Path, class_mapping: Dict[str, str]) -> int:
        """标准化类别ID"""
        fixed_count = 0
        txt_files = list(dataset_dir.glob('*.txt'))
        
        for txt_file in txt_files:
            try:
                content = txt_file.read_text(encoding='utf-8').strip()
                if not content:
                    continue
                
                lines = content.split('\n')
                fixed_lines = []
                has_changes = False
                
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) < 5:
                        continue
                    
                    old_class_id = parts[0]
                    if old_class_id in class_mapping:
                        new_class_id = class_mapping[old_class_id]
                        parts[0] = new_class_id
                        has_changes = True
                    
                    fixed_lines.append(' '.join(parts))
                
                if has_changes:
                    txt_file.write_text('\n'.join(fixed_lines), encoding='utf-8')
                    fixed_count += 1
                    
            except Exception:
                continue
        
        return fixed_count
    
    def remove_small_annotations(self, dataset_dir: Path, min_area: float = 0.001) -> int:
        """移除过小的标注"""
        removed_count = 0
        txt_files = list(dataset_dir.glob('*.txt'))
        
        for txt_file in txt_files:
            try:
                content = txt_file.read_text(encoding='utf-8').strip()
                if not content:
                    continue
                
                lines = content.split('\n')
                filtered_lines = []
                
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) == 5:  # 矩形框
                        _, cx, cy, w, h = parts
                        area = float(w) * float(h)
                        if area >= min_area:
                            filtered_lines.append(line)
                        else:
                            removed_count += 1
                    else:
                        # 多边形暂时保留
                        filtered_lines.append(line)
                
                txt_file.write_text('\n'.join(filtered_lines), encoding='utf-8')
                
            except Exception:
                continue
        
        return removed_count
    
    def restore_from_backup(self, dataset_dir: Path) -> bool:
        """从备份恢复"""
        if not self.backup_dir or not self.backup_dir.exists():
            return False
        
        try:
            # 删除当前目录内容
            for item in dataset_dir.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            
            # 从备份恢复
            for item in self.backup_dir.iterdir():
                if item.is_file():
                    shutil.copy2(item, dataset_dir / item.name)
                elif item.is_dir():
                    shutil.copytree(item, dataset_dir / item.name)
            
            return True
        except Exception:
            return False