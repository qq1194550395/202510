from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTextEdit, QFileDialog, QMessageBox, QProgressBar, QComboBox,
    QSpinBox, QCheckBox, QGroupBox, QGridLayout, QInputDialog,
    QScrollArea
)
from PyQt5.QtCore import QThread, pyqtSignal
from pathlib import Path
import json

from ..core.dataset_analyzer import DatasetAnalyzer
from ..core.dataset_validator import DatasetValidator
from ..core.data_augmentation import DataAugmentor
from ..core.dataset_organizer import DatasetOrganizer
from ..core.annotation_visualizer import AnnotationVisualizer
from ..core.dataset_comparator import DatasetComparator
from ..core.annotation_fixer import AnnotationFixer
from ..core.dataset_exporter import DatasetExporter
from .styles import AppStyles


class AnalysisPanel(QWidget):
    """数据集分析面板"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
        self.analyzer = DatasetAnalyzer()
        self.validator = DatasetValidator()
        self.augmentor = DataAugmentor()
        self.organizer = DatasetOrganizer()
        self.visualizer = AnnotationVisualizer()
        self.comparator = DatasetComparator()
        self.fixer = AnnotationFixer()
        self.exporter = DatasetExporter()
        
        self.dataset_dir = None
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # 应用主题管理器样式
        from .theme_manager import theme_manager
        self.setStyleSheet(theme_manager.generate_stylesheet())
        
        # 数据集选择 - 固定在顶部
        path_layout = QHBoxLayout()
        self.path_label = QLabel("数据集目录: 未选择")
        self.path_label.setProperty("labelType", "status")
        btn_select = QPushButton("选择数据集目录")
        btn_select.setProperty("buttonType", "primary")
        btn_select.clicked.connect(self.select_dataset)
        path_layout.addWidget(self.path_label)
        path_layout.addWidget(btn_select)
        main_layout.addLayout(path_layout)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(2)  # 总是显示垂直滚动条
        scroll_area.setHorizontalScrollBarPolicy(1)  # 根据需要显示水平滚动条
        
        # 创建滚动内容容器
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # 功能按钮组 - 放在滚动区域内
        self.setup_analysis_group(scroll_layout)
        self.setup_validation_group(scroll_layout)
        self.setup_visualization_group(scroll_layout)
        self.setup_fixing_group(scroll_layout)
        self.setup_augmentation_group(scroll_layout)
        self.setup_organization_group(scroll_layout)
        self.setup_export_group(scroll_layout)
        
        # 设置滚动内容
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        # 结果显示 - 固定在底部
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMaximumHeight(200)  # 限制高度
        
        result_label = QLabel("分析结果:")
        result_label.setProperty("labelType", "subtitle")
        main_layout.addWidget(result_label)
        main_layout.addWidget(self.result_text)
        
        # 进度条 - 固定在底部
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
    
    def setup_analysis_group(self, layout):
        """设置分析功能组"""
        group = QGroupBox("数据集分析")
        group_layout = QHBoxLayout(group)
        
        btn_analyze = QPushButton("统计分析")
        btn_analyze.setProperty("buttonType", "primary")
        btn_analyze.clicked.connect(self.analyze_dataset)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["yolo", "yolo_seg", "voc", "json"])
        
        group_layout.addWidget(QLabel("格式:"))
        group_layout.addWidget(self.format_combo)
        group_layout.addWidget(btn_analyze)
        
        layout.addWidget(group)
    
    def setup_validation_group(self, layout):
        """设置验证功能组"""
        group = QGroupBox("数据集验证与修复")
        group_layout = QHBoxLayout(group)
        
        btn_validate = QPushButton("质量检查")
        btn_validate.setProperty("buttonType", "primary")
        btn_validate.clicked.connect(self.validate_dataset)
        
        btn_fix = QPushButton("自动修复")
        btn_fix.setProperty("buttonType", "warning")
        btn_fix.clicked.connect(self.fix_dataset)
        
        btn_compare = QPushButton("数据集比较")
        btn_compare.setProperty("buttonType", "default")
        btn_compare.clicked.connect(self.compare_datasets)
        
        group_layout.addWidget(btn_validate)
        group_layout.addWidget(btn_fix)
        group_layout.addWidget(btn_compare)
        layout.addWidget(group)
    
    def setup_visualization_group(self, layout):
        """设置可视化功能组"""
        group = QGroupBox("标注可视化")
        group_layout = QHBoxLayout(group)
        
        btn_visualize = QPushButton("可视化标注")
        btn_visualize.setProperty("buttonType", "primary")
        btn_visualize.clicked.connect(self.visualize_annotations)
        
        btn_preview = QPushButton("生成预览图")
        btn_preview.setProperty("buttonType", "default")
        btn_preview.clicked.connect(self.create_preview)
        
        group_layout.addWidget(btn_visualize)
        group_layout.addWidget(btn_preview)
        layout.addWidget(group)
    
    def setup_fixing_group(self, layout):
        """设置修复功能组"""
        group = QGroupBox("数据清理")
        group_layout = QGridLayout(group)
        
        btn_remove_small = QPushButton("移除小标注")
        btn_remove_small.setProperty("buttonType", "warning")
        btn_remove_small.clicked.connect(self.remove_small_annotations)
        
        btn_normalize_ids = QPushButton("标准化类别ID")
        btn_normalize_ids.setProperty("buttonType", "default")
        btn_normalize_ids.clicked.connect(self.normalize_class_ids)
        
        btn_find_duplicates = QPushButton("查找重复文件")
        btn_find_duplicates.setProperty("buttonType", "default")
        btn_find_duplicates.clicked.connect(self.find_duplicates)
        
        group_layout.addWidget(btn_remove_small, 0, 0)
        group_layout.addWidget(btn_normalize_ids, 0, 1)
        group_layout.addWidget(btn_find_duplicates, 0, 2)
        
        layout.addWidget(group)
    
    def setup_export_group(self, layout):
        """设置导出功能组"""
        group = QGroupBox("数据集导出")
        group_layout = QGridLayout(group)
        
        btn_export_zip = QPushButton("导出ZIP")
        btn_export_zip.setProperty("buttonType", "primary")
        btn_export_zip.clicked.connect(self.export_zip)
        
        btn_export_coco = QPushButton("导出COCO")
        btn_export_coco.setProperty("buttonType", "default")
        btn_export_coco.clicked.connect(self.export_coco)
        
        btn_export_config = QPushButton("生成训练配置")
        btn_export_config.setProperty("buttonType", "default")
        btn_export_config.clicked.connect(self.export_yolo_config)
        
        btn_generate_report = QPushButton("生成报告")
        btn_generate_report.setProperty("buttonType", "success")
        btn_generate_report.clicked.connect(self.generate_report)
        
        group_layout.addWidget(btn_export_zip, 0, 0)
        group_layout.addWidget(btn_export_coco, 0, 1)
        group_layout.addWidget(btn_export_config, 1, 0)
        group_layout.addWidget(btn_generate_report, 1, 1)
        
        layout.addWidget(group)
    
    def setup_augmentation_group(self, layout):
        """设置数据增强功能组"""
        group = QGroupBox("数据增强")
        group_layout = QGridLayout(group)
        
        # 增强选项
        self.aug_checkboxes = {}
        aug_options = ['brightness', 'contrast', 'saturation', 'blur', 'flip_horizontal', 'rotate']
        
        for i, option in enumerate(aug_options):
            checkbox = QCheckBox(option)
            checkbox.setChecked(True)
            self.aug_checkboxes[option] = checkbox
            group_layout.addWidget(checkbox, i // 3, i % 3)
        
        # 倍数选择
        group_layout.addWidget(QLabel("增强倍数:"), 2, 0)
        self.multiplier_spin = QSpinBox()
        self.multiplier_spin.setRange(2, 10)
        self.multiplier_spin.setValue(3)
        group_layout.addWidget(self.multiplier_spin, 2, 1)
        
        btn_augment = QPushButton("开始增强")
        btn_augment.setProperty("buttonType", "success")
        btn_augment.clicked.connect(self.augment_dataset)
        group_layout.addWidget(btn_augment, 2, 2)
        
        layout.addWidget(group)
    
    def setup_organization_group(self, layout):
        """设置整理功能组"""
        group = QGroupBox("数据集整理")
        group_layout = QGridLayout(group)
        
        # 重命名
        btn_rename = QPushButton("批量重命名")
        btn_rename.setProperty("buttonType", "default")
        btn_rename.clicked.connect(self.rename_files)
        group_layout.addWidget(btn_rename, 0, 0)
        
        # 数据集划分
        btn_split = QPushButton("划分数据集")
        btn_split.setProperty("buttonType", "primary")
        btn_split.clicked.connect(self.split_dataset)
        group_layout.addWidget(btn_split, 0, 1)
        
        # 合并数据集
        btn_merge = QPushButton("合并数据集")
        btn_merge.setProperty("buttonType", "default")
        btn_merge.clicked.connect(self.merge_datasets)
        group_layout.addWidget(btn_merge, 0, 2)
        
        layout.addWidget(group)
    
    def select_dataset(self):
        """选择数据集目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择数据集目录")
        if not dir_path:
            return
        
        try:
            # 验证数据集结构
            from ..core.dataset_validator import DatasetValidator
            dataset_info = DatasetValidator.get_dataset_info(Path(dir_path))
            
            if not dataset_info["is_valid"]:
                reply = QMessageBox.question(self, "数据集格式警告", 
                    f"数据集格式可能不符合标准:\n{dataset_info['message']}\n\n是否继续使用此目录？",
                    QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.No:
                    return
            
            self.dataset_dir = Path(dir_path)
            self.path_label.setText(f"数据集目录: {dir_path}")
            
            # 如果检测到格式，自动设置格式选择框
            detected_format = dataset_info.get("detected_format")
            if detected_format:
                format_index = self.format_combo.findText(detected_format)
                if format_index >= 0:
                    self.format_combo.setCurrentIndex(format_index)
            
            # 显示基本信息
            if dataset_info["is_valid"]:
                stats = dataset_info["statistics"]
                info_text = f"数据集加载成功\n"
                info_text += f"检测格式: {detected_format or '未知'}\n"
                info_text += f"图片总数: {stats['total_images']}\n"
                info_text += f"标签总数: {stats['total_labels']}\n"
                info_text += f"子集: {', '.join(stats['subsets'].keys())}"
                self.result_text.setText(info_text)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"选择数据集失败: {str(e)}")
            print(f"选择数据集错误详情: {e}")  # 调试用
    
    def analyze_dataset(self):
        """分析数据集"""
        if not self.dataset_dir:
            QMessageBox.warning(self, "警告", "请先选择数据集目录")
            return
        
        try:
            # 验证数据集结构
            from ..core.dataset_validator import DatasetValidator
            dataset_info = DatasetValidator.get_dataset_info(self.dataset_dir)
            
            if not dataset_info["is_valid"]:
                QMessageBox.critical(self, "数据集格式错误", 
                    f"数据集格式不符合要求:\n{dataset_info['message']}\n\n"
                    f"请确保数据集采用标准结构")
                return
            
            # 使用检测到的格式或用户选择的格式
            detected_format = dataset_info["detected_format"]
            if detected_format:
                format_type = detected_format
                # 更新格式选择框
                format_index = self.format_combo.findText(detected_format)
                if format_index >= 0:
                    self.format_combo.setCurrentIndex(format_index)
            else:
                format_type = self.format_combo.currentText()
            
            # 解析数据集
            from ..core.converter import PARSERS
            parser = PARSERS[format_type]
            
            # 如果解析器支持标签映射，设置空映射避免错误
            if hasattr(parser, "set_label_map"):
                parser.set_label_map({})
            
            annotations = parser.parse(self.dataset_dir)
            
            if not annotations:
                QMessageBox.warning(self, "警告", "未找到有效的标注数据")
                return
            
            # 分析数据集
            result = self.analyze_annotations(annotations, dataset_info["statistics"])
            
            # 格式化显示结果
            output = self.format_analysis_result(result)
            self.result_text.setText(output)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"分析失败: {str(e)}")
            print(f"分析错误详情: {e}")  # 调试用
    
    def analyze_annotations(self, annotations, dataset_stats):
        """分析标注数据"""
        result = {}
        
        # 基本统计
        result['total_images'] = len(annotations)
        result['total_annotations'] = sum(len(ann.boxes) + (len(ann.polygons) if ann.polygons else 0) 
                                        for ann in annotations)
        
        # 类别分布
        class_counts = {}
        for ann in annotations:
            for box in ann.boxes:
                class_counts[box.label] = class_counts.get(box.label, 0) + 1
            if ann.polygons:
                for poly in ann.polygons:
                    class_counts[poly.label] = class_counts.get(poly.label, 0) + 1
        
        result['class_distribution'] = class_counts
        
        # 图片尺寸统计
        widths = [ann.width for ann in annotations if ann.width > 0]
        heights = [ann.height for ann in annotations if ann.height > 0]
        
        if widths and heights:
            result['image_size_stats'] = {
                'avg_width': sum(widths) / len(widths),
                'avg_height': sum(heights) / len(heights),
                'min_width': min(widths),
                'max_width': max(widths),
                'min_height': min(heights),
                'max_height': max(heights)
            }
        
        # 标注统计
        annotations_per_image = [len(ann.boxes) + (len(ann.polygons) if ann.polygons else 0) 
                               for ann in annotations]
        
        if annotations_per_image:
            result['annotation_stats'] = {
                'avg_per_image': sum(annotations_per_image) / len(annotations_per_image),
                'min_per_image': min(annotations_per_image),
                'max_per_image': max(annotations_per_image),
                'images_without_annotations': annotations_per_image.count(0)
            }
        
        # 添加数据集统计信息
        result['dataset_stats'] = dataset_stats
        
        return result
    
    def validate_dataset(self):
        """验证数据集质量"""
        if not self.dataset_dir:
            QMessageBox.warning(self, "警告", "请先选择数据集目录")
            return
        
        try:
            # 使用新的数据集验证器
            from ..core.dataset_validator import DatasetValidator
            dataset_info = DatasetValidator.get_dataset_info(self.dataset_dir)
            
            if not dataset_info["is_valid"]:
                output = f"数据集验证失败\n"
                output += f"错误: {dataset_info['message']}\n\n"
                output += "请确保数据集采用标准目录结构"
                self.result_text.setText(output)
                return
            
            # 解析数据集进行详细验证
            from ..core.converter import PARSERS
            detected_format = dataset_info["detected_format"]
            if not detected_format:
                detected_format = self.format_combo.currentText()
            
            parser = PARSERS[detected_format]
            if hasattr(parser, "set_label_map"):
                parser.set_label_map({})
            
            annotations = parser.parse(self.dataset_dir)
            
            # 计算健康度评分
            health_score = self.calculate_health_score(annotations, dataset_info["statistics"])
            
            # 检查问题
            issues = self.check_dataset_issues(annotations, dataset_info["statistics"])
            
            # 格式化输出
            output = f"数据集健康度评分: {health_score:.1f}/100\n\n"
            
            stats = dataset_info["statistics"]
            output += f"统计信息:\n"
            output += f"  总图片数: {stats['total_images']}\n"
            output += f"  总标签数: {stats['total_labels']}\n"
            output += f"  有效标注数: {len(annotations)}\n"
            output += f"  子集数量: {len(stats['subsets'])}\n"
            output += f"  类别数量: {len(set(box.label for ann in annotations for box in ann.boxes))}\n\n"
            
            if issues:
                output += f"发现的问题 ({len(issues)} 个):\n"
                for issue in issues[:20]:  # 只显示前20个问题
                    output += f"  - {issue}\n"
                if len(issues) > 20:
                    output += f"  ... 还有 {len(issues) - 20} 个问题\n"
            else:
                output += "未发现明显问题，数据集质量良好！\n"
            
            self.result_text.setText(output)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"验证失败: {str(e)}")
            print(f"验证错误详情: {e}")  # 调试用
    
    def calculate_health_score(self, annotations, stats):
        """计算数据集健康度评分"""
        score = 100.0
        
        if not annotations:
            return 0.0
        
        # 检查标注密度 (30分)
        total_annotations = sum(len(ann.boxes) + (len(ann.polygons) if ann.polygons else 0) 
                              for ann in annotations)
        avg_annotations = total_annotations / len(annotations) if annotations else 0
        
        if avg_annotations >= 3:
            annotation_score = 30
        elif avg_annotations >= 1:
            annotation_score = 20
        elif avg_annotations >= 0.5:
            annotation_score = 10
        else:
            annotation_score = 0
        
        # 检查类别平衡性 (25分)
        class_counts = {}
        for ann in annotations:
            for box in ann.boxes:
                class_counts[box.label] = class_counts.get(box.label, 0) + 1
            if ann.polygons:
                for poly in ann.polygons:
                    class_counts[poly.label] = class_counts.get(poly.label, 0) + 1
        
        if class_counts:
            counts = list(class_counts.values())
            max_count = max(counts)
            min_count = min(counts)
            balance_ratio = min_count / max_count if max_count > 0 else 0
            
            if balance_ratio >= 0.5:
                balance_score = 25
            elif balance_ratio >= 0.2:
                balance_score = 15
            elif balance_ratio >= 0.1:
                balance_score = 10
            else:
                balance_score = 5
        else:
            balance_score = 0
        
        # 检查图片质量 (20分)
        valid_images = sum(1 for ann in annotations if ann.width > 0 and ann.height > 0)
        image_quality_ratio = valid_images / len(annotations) if annotations else 0
        image_score = image_quality_ratio * 20
        
        # 检查数据完整性 (15分)
        complete_annotations = sum(1 for ann in annotations 
                                 if len(ann.boxes) > 0 or (ann.polygons and len(ann.polygons) > 0))
        completeness_ratio = complete_annotations / len(annotations) if annotations else 0
        completeness_score = completeness_ratio * 15
        
        # 检查子集分布 (10分)
        subset_count = len(stats.get('subsets', {}))
        if subset_count >= 3:
            subset_score = 10
        elif subset_count >= 2:
            subset_score = 7
        elif subset_count >= 1:
            subset_score = 5
        else:
            subset_score = 0
        
        total_score = annotation_score + balance_score + image_score + completeness_score + subset_score
        return min(100.0, total_score)
    
    def check_dataset_issues(self, annotations, stats):
        """检查数据集问题"""
        issues = []
        
        if not annotations:
            issues.append("未找到有效的标注数据")
            return issues
        
        # 检查空标注
        empty_annotations = sum(1 for ann in annotations 
                              if len(ann.boxes) == 0 and (not ann.polygons or len(ann.polygons) == 0))
        if empty_annotations > 0:
            issues.append(f"发现 {empty_annotations} 个空标注文件")
        
        # 检查图片尺寸问题
        invalid_size = sum(1 for ann in annotations if ann.width <= 0 or ann.height <= 0)
        if invalid_size > 0:
            issues.append(f"发现 {invalid_size} 个图片尺寸信息缺失")
        
        # 检查类别不平衡
        class_counts = {}
        for ann in annotations:
            for box in ann.boxes:
                class_counts[box.label] = class_counts.get(box.label, 0) + 1
            if ann.polygons:
                for poly in ann.polygons:
                    class_counts[poly.label] = class_counts.get(poly.label, 0) + 1
        
        if class_counts:
            counts = list(class_counts.values())
            max_count = max(counts)
            min_count = min(counts)
            if max_count > min_count * 10:  # 最大类别是最小类别的10倍以上
                issues.append(f"类别分布不平衡，最多类别有 {max_count} 个样本，最少类别只有 {min_count} 个样本")
        
        # 检查子集分布
        subset_count = len(stats.get('subsets', {}))
        if subset_count < 2:
            issues.append("建议至少包含训练集和验证集两个子集")
        
        return issues
    
    def augment_dataset(self):
        """数据增强"""
        if not self.dataset_dir:
            QMessageBox.warning(self, "警告", "请先选择数据集目录")
            return
        
        # 选择输出目录
        output_dir = QFileDialog.getExistingDirectory(self, "选择增强后数据集保存目录")
        if not output_dir:
            return
        
        # 获取选中的增强方法
        selected_augs = [name for name, checkbox in self.aug_checkboxes.items() 
                        if checkbox.isChecked()]
        
        if not selected_augs:
            QMessageBox.warning(self, "警告", "请至少选择一种增强方法")
            return
        
        multiplier = self.multiplier_spin.value()
        
        try:
            # 验证数据集格式
            from ..core.dataset_validator import DatasetValidator
            dataset_info = DatasetValidator.get_dataset_info(self.dataset_dir)
            
            if not dataset_info["is_valid"]:
                QMessageBox.critical(self, "错误", f"数据集格式不正确: {dataset_info['message']}")
                return
            
            # 解析数据集
            from ..core.converter import PARSERS
            detected_format = dataset_info["detected_format"] or self.format_combo.currentText()
            parser = PARSERS[detected_format]
            
            if hasattr(parser, "set_label_map"):
                parser.set_label_map({})
            
            annotations = parser.parse(self.dataset_dir)
            
            if not annotations:
                QMessageBox.warning(self, "警告", "未找到有效的标注数据")
                return
            
            # 执行数据增强
            output_path = Path(output_dir)
            augmented_count = self.perform_augmentation(annotations, output_path, selected_augs, multiplier, detected_format)
            
            QMessageBox.information(self, "完成", f"数据增强完成！生成了 {augmented_count} 个增强样本")
            self.result_text.setText(f"数据增强完成\n输出目录: {output_dir}\n增强倍数: {multiplier}\n生成样本: {augmented_count}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"数据增强失败: {str(e)}")
            print(f"数据增强错误详情: {e}")  # 调试用
    
    def perform_augmentation(self, annotations, output_path, selected_augs, multiplier, format_type):
        """执行数据增强"""
        from PIL import Image, ImageEnhance, ImageFilter
        import random
        import shutil
        
        # 创建输出目录结构
        for subset in ["train"]:  # 增强后的数据统一放在train目录
            (output_path / "images" / subset).mkdir(parents=True, exist_ok=True)
            (output_path / "labels" / subset).mkdir(parents=True, exist_ok=True)
        
        augmented_annotations = []
        augmented_count = 0
        
        for i, ann in enumerate(annotations):
            # 复制原始文件
            if ann.image_path.exists():
                original_img_dest = output_path / "images" / "train" / ann.image_path.name
                shutil.copy2(ann.image_path, original_img_dest)
                
                # 更新标注路径
                new_ann = ann
                new_ann.image_path = original_img_dest
                augmented_annotations.append(new_ann)
            
            # 生成增强版本
            for aug_idx in range(multiplier - 1):  # -1 因为已经复制了原始文件
                try:
                    if not ann.image_path.exists():
                        continue
                    
                    # 加载图片
                    with Image.open(ann.image_path) as img:
                        augmented_img = img.copy()
                        
                        # 应用增强
                        if 'brightness' in selected_augs:
                            enhancer = ImageEnhance.Brightness(augmented_img)
                            augmented_img = enhancer.enhance(random.uniform(0.7, 1.3))
                        
                        if 'contrast' in selected_augs:
                            enhancer = ImageEnhance.Contrast(augmented_img)
                            augmented_img = enhancer.enhance(random.uniform(0.8, 1.2))
                        
                        if 'saturation' in selected_augs:
                            enhancer = ImageEnhance.Color(augmented_img)
                            augmented_img = enhancer.enhance(random.uniform(0.8, 1.2))
                        
                        if 'blur' in selected_augs and random.random() < 0.3:
                            augmented_img = augmented_img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5, 1.5)))
                        
                        if 'flip_horizontal' in selected_augs and random.random() < 0.5:
                            augmented_img = augmented_img.transpose(Image.FLIP_LEFT_RIGHT)
                        
                        # 保存增强图片
                        aug_name = f"aug_{aug_idx}_{ann.image_path.stem}{ann.image_path.suffix}"
                        aug_img_path = output_path / "images" / "train" / aug_name
                        augmented_img.save(aug_img_path)
                        
                        # 创建对应的标注
                        aug_ann = ann
                        aug_ann.image_path = aug_img_path
                        augmented_annotations.append(aug_ann)
                        augmented_count += 1
                
                except Exception as e:
                    print(f"增强图片 {ann.image_path} 失败: {e}")
                    continue
        
        # 导出标注
        from ..core.converter import PARSERS
        exporter = PARSERS[format_type]
        if hasattr(exporter, "set_label_map"):
            exporter.set_label_map({})
        
        exporter.export(augmented_annotations, output_path / "labels" / "train")
        
        return augmented_count
    
    def rename_files(self):
        """批量重命名"""
        if not self.dataset_dir:
            QMessageBox.warning(self, "警告", "请先选择数据集目录")
            return
        
        try:
            # 验证数据集格式
            from ..core.dataset_validator import DatasetValidator
            dataset_info = DatasetValidator.get_dataset_info(self.dataset_dir)
            
            if not dataset_info["is_valid"]:
                QMessageBox.critical(self, "错误", f"数据集格式不正确: {dataset_info['message']}")
                return
            
            # 获取重命名参数
            prefix, ok1 = QInputDialog.getText(self, "设置前缀", "文件名前缀:", text="img")
            if not ok1:
                return
            
            start_num, ok2 = QInputDialog.getInt(self, "设置起始编号", "起始编号:", 0, 0, 999999)
            if not ok2:
                return
            
            # 执行重命名
            renamed_count = self.perform_rename(dataset_info["statistics"], prefix, start_num)
            
            QMessageBox.information(self, "完成", f"文件重命名完成！重命名了 {renamed_count} 个文件")
            self.result_text.setText(f"批量重命名完成\n重命名文件数: {renamed_count}\n前缀: {prefix}\n起始编号: {start_num}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"重命名失败: {str(e)}")
            print(f"重命名错误详情: {e}")  # 调试用
    
    def perform_rename(self, stats, prefix, start_num):
        """执行文件重命名"""
        renamed_count = 0
        current_num = start_num
        
        # 遍历所有子集
        for subset in stats.get('subsets', {}):
            img_dir = self.dataset_dir / "images" / subset
            label_dir = self.dataset_dir / "labels" / subset
            
            if not img_dir.exists() or not label_dir.exists():
                continue
            
            # 获取所有图片文件
            img_files = []
            for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']:
                img_files.extend(img_dir.glob(f"*{ext}"))
            
            # 重命名文件
            for img_file in img_files:
                try:
                    # 新文件名
                    new_name = f"{prefix}_{current_num:06d}{img_file.suffix}"
                    new_img_path = img_dir / new_name
                    
                    # 查找对应的标签文件
                    label_files = []
                    for ext in ['.txt', '.xml', '.json']:
                        label_file = label_dir / f"{img_file.stem}{ext}"
                        if label_file.exists():
                            label_files.append((label_file, ext))
                    
                    # 重命名图片文件
                    img_file.rename(new_img_path)
                    
                    # 重命名标签文件
                    for label_file, ext in label_files:
                        new_label_path = label_dir / f"{prefix}_{current_num:06d}{ext}"
                        label_file.rename(new_label_path)
                    
                    renamed_count += 1
                    current_num += 1
                    
                except Exception as e:
                    print(f"重命名文件 {img_file} 失败: {e}")
                    continue
        
        return renamed_count
    
    def split_dataset(self):
        """划分数据集"""
        if not self.dataset_dir:
            QMessageBox.warning(self, "警告", "请先选择数据集目录")
            return
        
        output_dir = QFileDialog.getExistingDirectory(self, "选择划分后数据集保存目录")
        if not output_dir:
            return
        
        try:
            # 验证数据集格式
            from ..core.dataset_validator import DatasetValidator
            dataset_info = DatasetValidator.get_dataset_info(self.dataset_dir)
            
            if not dataset_info["is_valid"]:
                QMessageBox.critical(self, "错误", f"数据集格式不正确: {dataset_info['message']}")
                return
            
            # 获取划分比例
            train_ratio, ok1 = QInputDialog.getDouble(self, "训练集比例", "训练集比例 (0-1):", 0.7, 0.1, 0.9, 2)
            if not ok1:
                return
            
            val_ratio, ok2 = QInputDialog.getDouble(self, "验证集比例", "验证集比例 (0-1):", 0.2, 0.05, 0.8, 2)
            if not ok2:
                return
            
            test_ratio = 1.0 - train_ratio - val_ratio
            if test_ratio < 0:
                QMessageBox.warning(self, "警告", "比例设置不正确，训练集和验证集比例之和不能超过1")
                return
            
            # 解析数据集
            from ..core.converter import PARSERS
            detected_format = dataset_info["detected_format"] or self.format_combo.currentText()
            parser = PARSERS[detected_format]
            
            if hasattr(parser, "set_label_map"):
                parser.set_label_map({})
            
            annotations = parser.parse(self.dataset_dir)
            
            if not annotations:
                QMessageBox.warning(self, "警告", "未找到有效的标注数据")
                return
            
            # 执行数据集划分
            result = self.perform_split(annotations, Path(output_dir), train_ratio, val_ratio, test_ratio, detected_format)
            
            QMessageBox.information(self, "完成", "数据集划分完成！")
            
            output = f"数据集划分完成\n"
            output += f"训练集: {result['train']} 张\n"
            output += f"验证集: {result['val']} 张\n"
            output += f"测试集: {result['test']} 张\n"
            output += f"输出目录: {output_dir}"
            self.result_text.setText(output)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"数据集划分失败: {str(e)}")
            print(f"划分错误详情: {e}")  # 调试用
    
    def perform_split(self, annotations, output_path, train_ratio, val_ratio, test_ratio, format_type):
        """执行数据集划分"""
        import random
        import shutil
        
        # 创建输出目录结构
        for subset in ["train", "val", "test"]:
            (output_path / "images" / subset).mkdir(parents=True, exist_ok=True)
            (output_path / "labels" / subset).mkdir(parents=True, exist_ok=True)
        
        # 随机打乱数据
        random.shuffle(annotations)
        
        # 计算划分点
        total = len(annotations)
        train_end = int(total * train_ratio)
        val_end = train_end + int(total * val_ratio)
        
        # 划分数据
        splits = {
            'train': annotations[:train_end],
            'val': annotations[train_end:val_end],
            'test': annotations[val_end:]
        }
        
        result = {}
        
        # 复制文件并导出标注
        from ..core.converter import PARSERS
        exporter = PARSERS[format_type]
        if hasattr(exporter, "set_label_map"):
            exporter.set_label_map({})
        
        for subset, subset_annotations in splits.items():
            result[subset] = len(subset_annotations)
            
            # 复制图片文件
            for ann in subset_annotations:
                if ann.image_path.exists():
                    dest_path = output_path / "images" / subset / ann.image_path.name
                    shutil.copy2(ann.image_path, dest_path)
                    # 更新标注中的图片路径
                    ann.image_path = dest_path
            
            # 导出标注
            if subset_annotations:
                exporter.export(subset_annotations, output_path / "labels" / subset)
        
        return result
    
    def merge_datasets(self):
        """合并数据集"""
        # 选择多个数据集目录
        dirs = []
        while True:
            dir_path = QFileDialog.getExistingDirectory(self, f"选择要合并的数据集目录 (已选择 {len(dirs)} 个)")
            if not dir_path:
                break
            dirs.append(Path(dir_path))
            
            reply = QMessageBox.question(self, "继续选择", "是否继续选择其他数据集？", 
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                break
        
        if len(dirs) < 2:
            QMessageBox.warning(self, "警告", "至少需要选择2个数据集进行合并")
            return
        
        output_dir = QFileDialog.getExistingDirectory(self, "选择合并后数据集保存目录")
        if not output_dir:
            return
        
        try:
            # 验证所有数据集
            all_annotations = []
            format_type = None
            
            for i, dataset_dir in enumerate(dirs):
                from ..core.dataset_validator import DatasetValidator
                dataset_info = DatasetValidator.get_dataset_info(dataset_dir)
                
                if not dataset_info["is_valid"]:
                    QMessageBox.critical(self, "错误", f"数据集 {i+1} 格式不正确: {dataset_info['message']}")
                    return
                
                # 使用第一个数据集的格式
                if format_type is None:
                    format_type = dataset_info["detected_format"] or self.format_combo.currentText()
                
                # 解析数据集
                from ..core.converter import PARSERS
                parser = PARSERS[format_type]
                if hasattr(parser, "set_label_map"):
                    parser.set_label_map({})
                
                annotations = parser.parse(dataset_dir)
                all_annotations.extend(annotations)
            
            if not all_annotations:
                QMessageBox.warning(self, "警告", "未找到有效的标注数据")
                return
            
            # 执行合并
            merged_count = self.perform_merge(all_annotations, Path(output_dir), format_type)
            
            QMessageBox.information(self, "完成", f"数据集合并完成！共处理 {merged_count} 个文件")
            self.result_text.setText(f"数据集合并完成\n合并数据集数: {len(dirs)}\n处理文件数: {merged_count}\n输出目录: {output_dir}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"数据集合并失败: {str(e)}")
            print(f"合并错误详情: {e}")  # 调试用
    
    def perform_merge(self, all_annotations, output_path, format_type):
        """执行数据集合并"""
        import shutil
        
        # 创建输出目录结构
        for subset in ["train"]:  # 合并后的数据统一放在train目录
            (output_path / "images" / subset).mkdir(parents=True, exist_ok=True)
            (output_path / "labels" / subset).mkdir(parents=True, exist_ok=True)
        
        merged_annotations = []
        file_counter = 0
        
        # 处理文件名冲突
        used_names = set()
        
        for ann in all_annotations:
            if not ann.image_path.exists():
                continue
            
            # 生成唯一文件名
            base_name = ann.image_path.stem
            extension = ann.image_path.suffix
            
            if base_name in used_names:
                counter = 1
                while f"{base_name}_{counter}" in used_names:
                    counter += 1
                new_name = f"{base_name}_{counter}{extension}"
            else:
                new_name = f"{base_name}{extension}"
            
            used_names.add(new_name.replace(extension, ''))
            
            # 复制图片文件
            dest_img_path = output_path / "images" / "train" / new_name
            shutil.copy2(ann.image_path, dest_img_path)
            
            # 更新标注路径
            ann.image_path = dest_img_path
            merged_annotations.append(ann)
            file_counter += 1
        
        # 导出标注
        from ..core.converter import PARSERS
        exporter = PARSERS[format_type]
        if hasattr(exporter, "set_label_map"):
            exporter.set_label_map({})
        
        exporter.export(merged_annotations, output_path / "labels" / "train")
        
        return file_counter
    
    def format_analysis_result(self, result: dict) -> str:
        """格式化分析结果"""
        if 'error' in result:
            return f"错误: {result['error']}"
        
        output = f"数据集统计分析\n{'='*50}\n\n"
        
        # 基本统计
        output += f"总图片数: {result.get('total_images', 0):,}\n"
        output += f"总标注数: {result.get('total_annotations', 0):,}\n\n"
        
        # 数据集结构信息
        if 'dataset_stats' in result:
            stats = result['dataset_stats']
            output += f"数据集结构信息:\n"
            output += f"  子集: {', '.join(stats.get('subsets', {}).keys())}\n"
            output += f"  图片格式: {', '.join(stats.get('image_formats', []))}\n"
            output += f"  标签格式: {', '.join(stats.get('label_formats', []))}\n\n"
            
            # 子集分布
            if 'subsets' in stats:
                output += f"子集分布:\n"
                for subset, counts in stats['subsets'].items():
                    output += f"  {subset}: {counts['images']} 图片, {counts['labels']} 标签\n"
                output += "\n"
        
        # 类别分布
        if 'class_distribution' in result and result['class_distribution']:
            output += "类别分布:\n"
            class_dist = result['class_distribution']
            total_annotations = sum(class_dist.values())
            
            # 按数量排序
            sorted_classes = sorted(class_dist.items(), key=lambda x: x[1], reverse=True)
            
            for class_name, count in sorted_classes:
                percentage = (count / total_annotations) * 100 if total_annotations > 0 else 0
                output += f"  {class_name}: {count:,} ({percentage:.1f}%)\n"
            output += "\n"
        
        # 图片尺寸统计
        if 'image_size_stats' in result:
            stats = result['image_size_stats']
            output += "图片尺寸统计:\n"
            output += f"  平均尺寸: {stats['avg_width']:.0f} x {stats['avg_height']:.0f}\n"
            output += f"  尺寸范围: {stats['min_width']} x {stats['min_height']} ~ {stats['max_width']} x {stats['max_height']}\n\n"
        
        # 标注统计
        if 'annotation_stats' in result:
            stats = result['annotation_stats']
            output += "标注统计:\n"
            output += f"  平均每张图片标注数: {stats['avg_per_image']:.2f}\n"
            output += f"  标注数范围: {stats['min_per_image']} ~ {stats['max_per_image']}\n"
            output += f"  无标注图片数: {stats['images_without_annotations']:,}\n\n"
        
        # 数据质量评估
        if result.get('total_images', 0) > 0 and result.get('total_annotations', 0) > 0:
            avg_annotations = result['total_annotations'] / result['total_images']
            output += "数据质量评估:\n"
            
            if avg_annotations >= 5:
                quality = "优秀"
            elif avg_annotations >= 2:
                quality = "良好"
            elif avg_annotations >= 1:
                quality = "一般"
            else:
                quality = "需要改进"
            
            output += f"  标注密度: {quality} (平均 {avg_annotations:.2f} 个/图)\n"
            
            if 'class_distribution' in result:
                class_count = len(result['class_distribution'])
                if class_count >= 10:
                    diversity = "丰富"
                elif class_count >= 5:
                    diversity = "适中"
                else:
                    diversity = "较少"
                output += f"  类别多样性: {diversity} ({class_count} 个类别)\n"
        
        return output
    
    def fix_dataset(self):
        """自动修复数据集"""
        if not self.dataset_dir:
            QMessageBox.warning(self, "警告", "请先选择数据集目录")
            return
        
        reply = QMessageBox.question(self, "确认", "是否创建备份？修复操作将直接修改原文件。", 
                                   QMessageBox.Yes | QMessageBox.No)
        create_backup = reply == QMessageBox.Yes
        
        try:
            # 验证数据集格式
            from ..core.dataset_validator import DatasetValidator
            dataset_info = DatasetValidator.get_dataset_info(self.dataset_dir)
            
            if not dataset_info["is_valid"]:
                QMessageBox.critical(self, "错误", f"数据集格式不正确: {dataset_info['message']}")
                return
            
            # 解析数据集
            from ..core.converter import PARSERS
            detected_format = dataset_info["detected_format"] or self.format_combo.currentText()
            parser = PARSERS[detected_format]
            
            if hasattr(parser, "set_label_map"):
                parser.set_label_map({})
            
            annotations = parser.parse(self.dataset_dir)
            
            # 执行修复
            fixes = self.perform_fixes(annotations, dataset_info["statistics"], create_backup, detected_format)
            
            output = "数据集修复完成:\n"
            output += f"- 坐标修复: {fixes['coordinate_fixes']} 个文件\n"
            output += f"- 创建缺失标注: {fixes['missing_annotations_created']} 个\n"
            output += f"- 移除无效文件: {fixes['invalid_files_removed']} 个\n"
            output += f"- 移除重复文件: {fixes['duplicate_files_removed']} 个\n"
            
            self.result_text.setText(output)
            QMessageBox.information(self, "完成", "数据集修复完成！")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"修复失败: {str(e)}")
            print(f"修复错误详情: {e}")  # 调试用
    
    def perform_fixes(self, annotations, stats, create_backup, format_type):
        """执行数据集修复"""
        import shutil
        
        fixes = {
            'coordinate_fixes': 0,
            'missing_annotations_created': 0,
            'invalid_files_removed': 0,
            'duplicate_files_removed': 0
        }
        
        if create_backup:
            backup_dir = self.dataset_dir.parent / f"{self.dataset_dir.name}_backup"
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            shutil.copytree(self.dataset_dir, backup_dir)
        
        # 修复坐标超出边界的问题
        for ann in annotations:
            if ann.width <= 0 or ann.height <= 0:
                continue
            
            fixed = False
            for box in ann.boxes:
                # 修复边界框坐标
                if box.xmin < 0 or box.ymin < 0 or box.xmax > ann.width or box.ymax > ann.height:
                    box.xmin = max(0, box.xmin)
                    box.ymin = max(0, box.ymin)
                    box.xmax = min(ann.width, box.xmax)
                    box.ymax = min(ann.height, box.ymax)
                    fixed = True
            
            if ann.polygons:
                for poly in ann.polygons:
                    # 修复多边形坐标
                    for i in range(0, len(poly.points), 2):
                        if i + 1 < len(poly.points):
                            x, y = poly.points[i], poly.points[i + 1]
                            if x < 0 or x > 1 or y < 0 or y > 1:  # 假设是归一化坐标
                                poly.points[i] = max(0, min(1, x))
                                poly.points[i + 1] = max(0, min(1, y))
                                fixed = True
            
            if fixed:
                fixes['coordinate_fixes'] += 1
        
        # 查找缺失标注的图片并创建空标注
        for subset in stats.get('subsets', {}):
            img_dir = self.dataset_dir / "images" / subset
            label_dir = self.dataset_dir / "labels" / subset
            
            if not img_dir.exists() or not label_dir.exists():
                continue
            
            # 获取所有图片文件
            img_files = []
            for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']:
                img_files.extend(img_dir.glob(f"*{ext}"))
            
            for img_file in img_files:
                # 检查是否有对应的标签文件
                has_label = False
                for ext in ['.txt', '.xml', '.json']:
                    label_file = label_dir / f"{img_file.stem}{ext}"
                    if label_file.exists():
                        has_label = True
                        break
                
                if not has_label:
                    # 创建空标注文件
                    if format_type in ['yolo', 'yolo_seg']:
                        empty_label = label_dir / f"{img_file.stem}.txt"
                        empty_label.write_text("", encoding="utf-8")
                        fixes['missing_annotations_created'] += 1
        
        # 移除无效文件（无对应图片的标签文件）
        for subset in stats.get('subsets', {}):
            img_dir = self.dataset_dir / "images" / subset
            label_dir = self.dataset_dir / "labels" / subset
            
            if not img_dir.exists() or not label_dir.exists():
                continue
            
            # 获取所有标签文件
            label_files = []
            for ext in ['.txt', '.xml', '.json']:
                label_files.extend(label_dir.glob(f"*{ext}"))
            
            for label_file in label_files:
                # 检查是否有对应的图片文件
                has_image = False
                for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']:
                    img_file = img_dir / f"{label_file.stem}{ext}"
                    if img_file.exists():
                        has_image = True
                        break
                
                if not has_image:
                    label_file.unlink()
                    fixes['invalid_files_removed'] += 1
        
        return fixes
    
    def compare_datasets(self):
        """比较数据集"""
        if not self.dataset_dir:
            QMessageBox.warning(self, "警告", "请先选择第一个数据集目录")
            return
        
        dataset2_dir = QFileDialog.getExistingDirectory(self, "选择第二个数据集目录")
        if not dataset2_dir:
            return
        
        try:
            # 验证两个数据集
            from ..core.dataset_validator import DatasetValidator
            
            dataset1_info = DatasetValidator.get_dataset_info(self.dataset_dir)
            dataset2_info = DatasetValidator.get_dataset_info(Path(dataset2_dir))
            
            if not dataset1_info["is_valid"]:
                QMessageBox.critical(self, "错误", f"第一个数据集格式不正确: {dataset1_info['message']}")
                return
            
            if not dataset2_info["is_valid"]:
                QMessageBox.critical(self, "错误", f"第二个数据集格式不正确: {dataset2_info['message']}")
                return
            
            # 解析两个数据集
            from ..core.converter import PARSERS
            
            format1 = dataset1_info["detected_format"] or self.format_combo.currentText()
            format2 = dataset2_info["detected_format"] or format1
            
            parser1 = PARSERS[format1]
            parser2 = PARSERS[format2]
            
            if hasattr(parser1, "set_label_map"):
                parser1.set_label_map({})
            if hasattr(parser2, "set_label_map"):
                parser2.set_label_map({})
            
            annotations1 = parser1.parse(self.dataset_dir)
            annotations2 = parser2.parse(Path(dataset2_dir))
            
            # 执行比较
            result = self.perform_comparison(annotations1, annotations2, dataset1_info["statistics"], dataset2_info["statistics"])
            
            # 格式化输出
            output = "数据集比较结果:\n" + "="*50 + "\n\n"
            
            # 基本差异
            diff = result['differences']
            output += f"图片数量差异: {diff['image_count_diff']}\n"
            output += f"标注数量差异: {diff['annotation_count_diff']}\n"
            output += f"共同文件: {diff['common_files']}\n"
            output += f"数据集1独有: {diff['unique_to_dataset1']}\n"
            output += f"数据集2独有: {diff['unique_to_dataset2']}\n\n"
            
            # 类别差异
            output += f"共同类别: {', '.join(diff['common_classes'])}\n"
            if diff['classes_only_in_dataset1']:
                output += f"数据集1独有类别: {', '.join(diff['classes_only_in_dataset1'])}\n"
            if diff['classes_only_in_dataset2']:
                output += f"数据集2独有类别: {', '.join(diff['classes_only_in_dataset2'])}\n"
            
            # 建议
            if result['recommendations']:
                output += "\n改进建议:\n"
                for rec in result['recommendations']:
                    output += f"- {rec}\n"
            
            self.result_text.setText(output)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"比较失败: {str(e)}")
            print(f"比较错误详情: {e}")  # 调试用
    
    def perform_comparison(self, annotations1, annotations2, stats1, stats2):
        """执行数据集比较"""
        result = {'differences': {}, 'recommendations': []}
        
        # 基本统计比较
        total_annotations1 = sum(len(ann.boxes) + (len(ann.polygons) if ann.polygons else 0) for ann in annotations1)
        total_annotations2 = sum(len(ann.boxes) + (len(ann.polygons) if ann.polygons else 0) for ann in annotations2)
        
        result['differences']['image_count_diff'] = len(annotations1) - len(annotations2)
        result['differences']['annotation_count_diff'] = total_annotations1 - total_annotations2
        
        # 文件名比较
        files1 = set(ann.image_path.name for ann in annotations1)
        files2 = set(ann.image_path.name for ann in annotations2)
        
        result['differences']['common_files'] = len(files1 & files2)
        result['differences']['unique_to_dataset1'] = len(files1 - files2)
        result['differences']['unique_to_dataset2'] = len(files2 - files1)
        
        # 类别比较
        classes1 = set()
        classes2 = set()
        
        for ann in annotations1:
            for box in ann.boxes:
                classes1.add(box.label)
            if ann.polygons:
                for poly in ann.polygons:
                    classes1.add(poly.label)
        
        for ann in annotations2:
            for box in ann.boxes:
                classes2.add(box.label)
            if ann.polygons:
                for poly in ann.polygons:
                    classes2.add(poly.label)
        
        result['differences']['common_classes'] = list(classes1 & classes2)
        result['differences']['classes_only_in_dataset1'] = list(classes1 - classes2)
        result['differences']['classes_only_in_dataset2'] = list(classes2 - classes1)
        
        # 生成建议
        if abs(result['differences']['image_count_diff']) > len(annotations1) * 0.2:
            result['recommendations'].append("两个数据集的图片数量差异较大，建议检查数据完整性")
        
        if len(result['differences']['classes_only_in_dataset1']) > 0:
            result['recommendations'].append("数据集1包含数据集2没有的类别，可能需要统一类别定义")
        
        if len(result['differences']['classes_only_in_dataset2']) > 0:
            result['recommendations'].append("数据集2包含数据集1没有的类别，可能需要统一类别定义")
        
        if result['differences']['common_files'] < min(len(files1), len(files2)) * 0.1:
            result['recommendations'].append("两个数据集的重叠度很低，可能是完全不同的数据集")
        
        return result
    
    def visualize_annotations(self):
        """可视化标注"""
        if not self.dataset_dir:
            QMessageBox.warning(self, "警告", "请先选择数据集目录")
            return
        
        output_dir = QFileDialog.getExistingDirectory(self, "选择可视化结果保存目录")
        if not output_dir:
            return
        
        try:
            # 验证数据集格式
            from ..core.dataset_validator import DatasetValidator
            dataset_info = DatasetValidator.get_dataset_info(self.dataset_dir)
            
            if not dataset_info["is_valid"]:
                QMessageBox.critical(self, "错误", f"数据集格式不正确: {dataset_info['message']}")
                return
            
            # 解析数据集
            from ..core.converter import PARSERS
            detected_format = dataset_info["detected_format"] or self.format_combo.currentText()
            parser = PARSERS[detected_format]
            
            if hasattr(parser, "set_label_map"):
                parser.set_label_map({})
            
            annotations = parser.parse(self.dataset_dir)
            
            if not annotations:
                QMessageBox.warning(self, "警告", "未找到有效的标注数据")
                return
            
            # 执行可视化
            processed = self.perform_visualization(annotations[:20], Path(output_dir))  # 只处理前20张
            
            QMessageBox.information(self, "完成", f"已可视化 {processed} 张图片")
            self.result_text.setText(f"标注可视化完成\n处理图片: {processed} 张\n输出目录: {output_dir}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"可视化失败: {str(e)}")
            print(f"可视化错误详情: {e}")  # 调试用
    
    def perform_visualization(self, annotations, output_path):
        """执行标注可视化"""
        from PIL import Image, ImageDraw, ImageFont
        import random
        
        output_path.mkdir(parents=True, exist_ok=True)
        processed = 0
        
        # 生成颜色
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), 
                 (255, 0, 255), (0, 255, 255), (128, 0, 128), (255, 165, 0)]
        
        for ann in annotations:
            if not ann.image_path.exists():
                continue
            
            try:
                with Image.open(ann.image_path) as img:
                    draw = ImageDraw.Draw(img)
                    
                    # 绘制边界框
                    for i, box in enumerate(ann.boxes):
                        color = colors[i % len(colors)]
                        
                        # 绘制矩形
                        draw.rectangle([box.xmin, box.ymin, box.xmax, box.ymax], 
                                     outline=color, width=2)
                        
                        # 绘制标签
                        draw.text((box.xmin, box.ymin - 15), box.label, 
                                fill=color)
                    
                    # 绘制多边形
                    if ann.polygons:
                        for i, poly in enumerate(ann.polygons):
                            color = colors[(i + len(ann.boxes)) % len(colors)]
                            
                            # 转换归一化坐标到像素坐标
                            points = []
                            for j in range(0, len(poly.points), 2):
                                if j + 1 < len(poly.points):
                                    x = poly.points[j] * ann.width
                                    y = poly.points[j + 1] * ann.height
                                    points.append((x, y))
                            
                            if len(points) >= 3:
                                draw.polygon(points, outline=color, width=2)
                    
                    # 保存可视化结果
                    output_file = output_path / f"vis_{ann.image_path.name}"
                    img.save(output_file)
                    processed += 1
            
            except Exception as e:
                print(f"可视化图片 {ann.image_path} 失败: {e}")
                continue
        
        return processed
    
    def create_preview(self):
        """创建预览图"""
        if not self.dataset_dir:
            QMessageBox.warning(self, "警告", "请先选择数据集目录")
            return
        
        output_dir = QFileDialog.getExistingDirectory(self, "选择预览图保存目录")
        if not output_dir:
            return
        
        try:
            # 验证数据集格式
            from ..core.dataset_validator import DatasetValidator
            dataset_info = DatasetValidator.get_dataset_info(self.dataset_dir)
            
            if not dataset_info["is_valid"]:
                QMessageBox.critical(self, "错误", f"数据集格式不正确: {dataset_info['message']}")
                return
            
            # 解析数据集
            from ..core.converter import PARSERS
            detected_format = dataset_info["detected_format"] or self.format_combo.currentText()
            parser = PARSERS[detected_format]
            
            if hasattr(parser, "set_label_map"):
                parser.set_label_map({})
            
            annotations = parser.parse(self.dataset_dir)
            
            if not annotations:
                QMessageBox.warning(self, "警告", "未找到有效的标注数据")
                return
            
            # 创建预览图
            preview_path = self.create_dataset_preview(annotations, Path(output_dir))
            
            QMessageBox.information(self, "完成", f"预览图已生成: {preview_path}")
            self.result_text.setText(f"数据集预览图生成完成\n保存位置: {preview_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成预览图失败: {str(e)}")
            print(f"预览图错误详情: {e}")  # 调试用
    
    def create_dataset_preview(self, annotations, output_path):
        """创建数据集预览图"""
        from PIL import Image, ImageDraw, ImageFont
        import math
        
        # 选择前16张图片创建预览
        preview_annotations = annotations[:16]
        
        if not preview_annotations:
            return None
        
        # 计算网格尺寸
        grid_size = math.ceil(math.sqrt(len(preview_annotations)))
        thumbnail_size = 200
        
        # 创建预览图
        preview_width = grid_size * thumbnail_size
        preview_height = grid_size * thumbnail_size
        preview_img = Image.new('RGB', (preview_width, preview_height), (255, 255, 255))
        
        for i, ann in enumerate(preview_annotations):
            if not ann.image_path.exists():
                continue
            
            try:
                # 计算位置
                row = i // grid_size
                col = i % grid_size
                x = col * thumbnail_size
                y = row * thumbnail_size
                
                # 加载并缩放图片
                with Image.open(ann.image_path) as img:
                    img.thumbnail((thumbnail_size, thumbnail_size), Image.Resampling.LANCZOS)
                    
                    # 粘贴到预览图
                    preview_img.paste(img, (x, y))
                    
                    # 添加标注信息
                    draw = ImageDraw.Draw(preview_img)
                    info_text = f"{ann.image_path.name}\n{len(ann.boxes)} boxes"
                    if ann.polygons:
                        info_text += f", {len(ann.polygons)} polys"
                    
                    draw.text((x + 5, y + 5), info_text, fill=(255, 0, 0))
            
            except Exception as e:
                print(f"处理预览图片 {ann.image_path} 失败: {e}")
                continue
        
        # 保存预览图
        preview_path = output_path / "dataset_preview.jpg"
        preview_img.save(preview_path, quality=90)
        
        return preview_path
    
    def remove_small_annotations(self):
        """移除小标注"""
        if not self.dataset_dir:
            QMessageBox.warning(self, "警告", "请先选择数据集目录")
            return
        
        min_area, ok = QInputDialog.getDouble(self, "设置最小面积", 
                                            "最小标注面积 (像素):", 100, 1, 10000, 0)
        if not ok:
            return
        
        try:
            # 验证数据集格式
            from ..core.dataset_validator import DatasetValidator
            dataset_info = DatasetValidator.get_dataset_info(self.dataset_dir)
            
            if not dataset_info["is_valid"]:
                QMessageBox.critical(self, "错误", f"数据集格式不正确: {dataset_info['message']}")
                return
            
            # 解析数据集
            from ..core.converter import PARSERS
            detected_format = dataset_info["detected_format"] or self.format_combo.currentText()
            parser = PARSERS[detected_format]
            
            if hasattr(parser, "set_label_map"):
                parser.set_label_map({})
            
            annotations = parser.parse(self.dataset_dir)
            
            # 移除小标注
            removed_count = self.perform_small_annotation_removal(annotations, min_area, detected_format)
            
            QMessageBox.information(self, "完成", f"已移除 {removed_count} 个小标注")
            self.result_text.setText(f"小标注清理完成\n移除数量: {removed_count}\n最小面积: {min_area} 像素")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"清理失败: {str(e)}")
            print(f"清理错误详情: {e}")  # 调试用
    
    def perform_small_annotation_removal(self, annotations, min_area, format_type):
        """执行小标注移除"""
        removed_count = 0
        
        for ann in annotations:
            if ann.width <= 0 or ann.height <= 0:
                continue
            
            # 过滤边界框
            original_box_count = len(ann.boxes)
            ann.boxes = [box for box in ann.boxes 
                        if (box.xmax - box.xmin) * (box.ymax - box.ymin) >= min_area]
            removed_count += original_box_count - len(ann.boxes)
            
            # 过滤多边形（简化处理，基于边界框面积）
            if ann.polygons:
                original_poly_count = len(ann.polygons)
                filtered_polygons = []
                
                for poly in ann.polygons:
                    # 计算多边形的边界框
                    if len(poly.points) >= 6:  # 至少3个点
                        x_coords = [poly.points[i] * ann.width for i in range(0, len(poly.points), 2)]
                        y_coords = [poly.points[i + 1] * ann.height for i in range(0, len(poly.points), 2)]
                        
                        if x_coords and y_coords:
                            bbox_area = (max(x_coords) - min(x_coords)) * (max(y_coords) - min(y_coords))
                            if bbox_area >= min_area:
                                filtered_polygons.append(poly)
                
                ann.polygons = filtered_polygons
                removed_count += original_poly_count - len(ann.polygons)
        
        # 重新导出标注
        from ..core.converter import PARSERS
        exporter = PARSERS[format_type]
        if hasattr(exporter, "set_label_map"):
            exporter.set_label_map({})
        
        # 导出到各个子集
        for subset in ["train", "test", "val"]:
            label_dir = self.dataset_dir / "labels" / subset
            if label_dir.exists():
                subset_annotations = [ann for ann in annotations 
                                    if subset in str(ann.image_path)]
                if subset_annotations:
                    exporter.export(subset_annotations, label_dir)
        
        return removed_count
    
    def normalize_class_ids(self):
        """标准化类别ID"""
        if not self.dataset_dir:
            QMessageBox.warning(self, "警告", "请先选择数据集目录")
            return
        
        try:
            # 验证数据集格式
            from ..core.dataset_validator import DatasetValidator
            dataset_info = DatasetValidator.get_dataset_info(self.dataset_dir)
            
            if not dataset_info["is_valid"]:
                QMessageBox.critical(self, "错误", f"数据集格式不正确: {dataset_info['message']}")
                return
            
            # 解析数据集
            from ..core.converter import PARSERS
            detected_format = dataset_info["detected_format"] or self.format_combo.currentText()
            
            if detected_format not in ['yolo', 'yolo_seg']:
                QMessageBox.warning(self, "提示", "类别ID标准化仅支持YOLO格式")
                return
            
            parser = PARSERS[detected_format]
            if hasattr(parser, "set_label_map"):
                parser.set_label_map({})
            
            annotations = parser.parse(self.dataset_dir)
            
            if not annotations:
                QMessageBox.warning(self, "警告", "未找到有效的标注数据")
                return
            
            # 收集所有类别并创建映射
            categories = set()
            for ann in annotations:
                for box in ann.boxes:
                    categories.add(box.label)
                if ann.polygons:
                    for poly in ann.polygons:
                        categories.add(poly.label)
            
            # 创建标准化映射 (按字母顺序)
            sorted_categories = sorted(list(categories))
            class_mapping = {name: i for i, name in enumerate(sorted_categories)}
            
            # 应用映射并重新导出
            normalized_count = self.apply_class_normalization(annotations, class_mapping, detected_format)
            
            # 保存类别映射文件
            mapping_file = self.dataset_dir / "class_mapping.txt"
            mapping_content = "\n".join(f"{i}: {name}" for name, i in class_mapping.items())
            mapping_file.write_text(mapping_content, encoding="utf-8")
            
            QMessageBox.information(self, "完成", f"类别ID标准化完成！处理了 {normalized_count} 个标注文件")
            self.result_text.setText(f"类别ID标准化完成\n处理文件数: {normalized_count}\n类别数量: {len(class_mapping)}\n映射文件: {mapping_file}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"标准化失败: {str(e)}")
            print(f"标准化错误详情: {e}")  # 调试用
    
    def apply_class_normalization(self, annotations, class_mapping, format_type):
        """应用类别标准化"""
        # 更新标注中的类别标签
        for ann in annotations:
            for box in ann.boxes:
                if box.label in class_mapping:
                    box.label = str(class_mapping[box.label])
            
            if ann.polygons:
                for poly in ann.polygons:
                    if poly.label in class_mapping:
                        poly.label = str(class_mapping[poly.label])
        
        # 重新导出标注
        from ..core.converter import PARSERS
        exporter = PARSERS[format_type]
        if hasattr(exporter, "set_label_map"):
            exporter.set_label_map(class_mapping)
        
        # 导出到各个子集
        normalized_count = 0
        for subset in ["train", "test", "val"]:
            label_dir = self.dataset_dir / "labels" / subset
            if label_dir.exists():
                subset_annotations = [ann for ann in annotations 
                                    if subset in str(ann.image_path)]
                if subset_annotations:
                    exporter.export(subset_annotations, label_dir)
                    normalized_count += len(subset_annotations)
        
        return normalized_count
    
    def find_duplicates(self):
        """查找重复文件"""
        if not self.dataset_dir:
            QMessageBox.warning(self, "警告", "请先选择数据集目录")
            return
        
        try:
            # 验证数据集格式
            from ..core.dataset_validator import DatasetValidator
            dataset_info = DatasetValidator.get_dataset_info(self.dataset_dir)
            
            if not dataset_info["is_valid"]:
                QMessageBox.critical(self, "错误", f"数据集格式不正确: {dataset_info['message']}")
                return
            
            # 查找重复文件
            duplicates = self.find_duplicate_images()
            
            if duplicates:
                output = f"发现 {len(duplicates)} 组可能的重复文件:\n\n"
                for i, (file1, file2, similarity) in enumerate(duplicates[:20]):  # 只显示前20组
                    output += f"{i+1}. {file1.name} <-> {file2.name} (相似度: {similarity:.2f})\n"
                if len(duplicates) > 20:
                    output += f"\n... 还有 {len(duplicates) - 20} 组重复文件"
            else:
                output = "未发现重复文件"
            
            self.result_text.setText(output)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"查找失败: {str(e)}")
            print(f"查找重复文件错误详情: {e}")  # 调试用
    
    def find_duplicate_images(self):
        """查找重复图片"""
        import hashlib
        from PIL import Image
        
        duplicates = []
        file_hashes = {}
        
        # 遍历所有子集
        for subset in ["train", "test", "val"]:
            img_dir = self.dataset_dir / "images" / subset
            if not img_dir.exists():
                continue
            
            # 获取所有图片文件
            img_files = []
            for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']:
                img_files.extend(img_dir.glob(f"*{ext}"))
            
            for img_file in img_files:
                try:
                    # 计算文件哈希
                    with open(img_file, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                    
                    if file_hash in file_hashes:
                        # 发现重复文件
                        duplicates.append((file_hashes[file_hash], img_file, 1.0))
                    else:
                        file_hashes[file_hash] = img_file
                
                except Exception as e:
                    print(f"处理文件 {img_file} 失败: {e}")
                    continue
        
        return duplicates
    
    def export_zip(self):
        """导出ZIP"""
        if not self.dataset_dir:
            QMessageBox.warning(self, "警告", "请先选择数据集目录")
            return
        
        output_file, _ = QFileDialog.getSaveFileName(self, "保存ZIP文件", 
                                                   f"{self.dataset_dir.name}.zip", 
                                                   "ZIP Files (*.zip)")
        if not output_file:
            return
        
        try:
            # 验证数据集格式
            from ..core.dataset_validator import DatasetValidator
            dataset_info = DatasetValidator.get_dataset_info(self.dataset_dir)
            
            if not dataset_info["is_valid"]:
                QMessageBox.critical(self, "错误", f"数据集格式不正确: {dataset_info['message']}")
                return
            
            # 创建ZIP文件
            success = self.create_zip_export(Path(output_file))
            
            if success:
                QMessageBox.information(self, "完成", "ZIP导出完成！")
                self.result_text.setText(f"数据集已导出为ZIP\n文件位置: {output_file}")
            else:
                QMessageBox.critical(self, "错误", "ZIP导出失败")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")
            print(f"ZIP导出错误详情: {e}")  # 调试用
    
    def create_zip_export(self, output_file):
        """创建ZIP导出"""
        import zipfile
        
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 添加所有文件到ZIP
            for root, dirs, files in self.dataset_dir.rglob('*'):
                if root.is_file():
                    # 计算相对路径
                    arcname = root.relative_to(self.dataset_dir)
                    zipf.write(root, arcname)
        
        return True
    
    def export_coco(self):
        """导出COCO格式"""
        if not self.dataset_dir:
            QMessageBox.warning(self, "警告", "请先选择数据集目录")
            return
        
        output_file, _ = QFileDialog.getSaveFileName(self, "保存COCO文件", 
                                                   "annotations.json", 
                                                   "JSON Files (*.json)")
        if not output_file:
            return
        
        try:
            # 验证数据集格式
            from ..core.dataset_validator import DatasetValidator
            dataset_info = DatasetValidator.get_dataset_info(self.dataset_dir)
            
            if not dataset_info["is_valid"]:
                QMessageBox.critical(self, "错误", f"数据集格式不正确: {dataset_info['message']}")
                return
            
            # 解析数据集
            from ..core.converter import PARSERS
            detected_format = dataset_info["detected_format"] or self.format_combo.currentText()
            parser = PARSERS[detected_format]
            
            if hasattr(parser, "set_label_map"):
                parser.set_label_map({})
            
            annotations = parser.parse(self.dataset_dir)
            
            if not annotations:
                QMessageBox.warning(self, "警告", "未找到有效的标注数据")
                return
            
            # 导出COCO格式
            success = self.create_coco_export(annotations, Path(output_file))
            
            if success:
                QMessageBox.information(self, "完成", "COCO格式导出完成！")
                self.result_text.setText(f"数据集已导出为COCO格式\n文件位置: {output_file}")
            else:
                QMessageBox.critical(self, "错误", "COCO导出失败")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")
            print(f"COCO导出错误详情: {e}")  # 调试用
    
    def create_coco_export(self, annotations, output_file):
        """创建COCO格式导出"""
        import json
        from datetime import datetime
        
        # 创建COCO格式数据结构
        coco_data = {
            "info": {
                "description": "Dataset exported by DataForge",
                "version": "2.0",
                "year": datetime.now().year,
                "contributor": "DataForge",
                "date_created": datetime.now().isoformat()
            },
            "licenses": [],
            "images": [],
            "annotations": [],
            "categories": []
        }
        
        # 收集所有类别
        categories = set()
        for ann in annotations:
            for box in ann.boxes:
                categories.add(box.label)
            if ann.polygons:
                for poly in ann.polygons:
                    categories.add(poly.label)
        
        # 创建类别映射
        category_map = {}
        for i, cat_name in enumerate(sorted(categories)):
            category_id = i + 1
            category_map[cat_name] = category_id
            coco_data["categories"].append({
                "id": category_id,
                "name": cat_name,
                "supercategory": "object"
            })
        
        # 处理图片和标注
        annotation_id = 1
        
        for image_id, ann in enumerate(annotations, 1):
            # 添加图片信息
            coco_data["images"].append({
                "id": image_id,
                "width": ann.width,
                "height": ann.height,
                "file_name": ann.image_path.name
            })
            
            # 添加边界框标注
            for box in ann.boxes:
                coco_data["annotations"].append({
                    "id": annotation_id,
                    "image_id": image_id,
                    "category_id": category_map[box.label],
                    "bbox": [box.xmin, box.ymin, box.xmax - box.xmin, box.ymax - box.ymin],
                    "area": (box.xmax - box.xmin) * (box.ymax - box.ymin),
                    "iscrowd": 0
                })
                annotation_id += 1
            
            # 添加分割标注
            if ann.polygons:
                for poly in ann.polygons:
                    # 转换归一化坐标到像素坐标
                    segmentation = []
                    for i in range(0, len(poly.points), 2):
                        if i + 1 < len(poly.points):
                            x = poly.points[i] * ann.width
                            y = poly.points[i + 1] * ann.height
                            segmentation.extend([x, y])
                    
                    if len(segmentation) >= 6:  # 至少3个点
                        # 计算边界框
                        x_coords = segmentation[::2]
                        y_coords = segmentation[1::2]
                        bbox = [min(x_coords), min(y_coords), 
                               max(x_coords) - min(x_coords), 
                               max(y_coords) - min(y_coords)]
                        
                        coco_data["annotations"].append({
                            "id": annotation_id,
                            "image_id": image_id,
                            "category_id": category_map[poly.label],
                            "segmentation": [segmentation],
                            "bbox": bbox,
                            "area": bbox[2] * bbox[3],
                            "iscrowd": 0
                        })
                        annotation_id += 1
        
        # 保存COCO文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(coco_data, f, indent=2, ensure_ascii=False)
        
        return True
    
    def export_yolo_config(self):
        """导出YOLO训练配置"""
        if not self.dataset_dir:
            QMessageBox.warning(self, "警告", "请先选择数据集目录")
            return
        
        output_dir = QFileDialog.getExistingDirectory(self, "选择配置文件保存目录")
        if not output_dir:
            return
        
        try:
            # 验证数据集格式
            from ..core.dataset_validator import DatasetValidator
            dataset_info = DatasetValidator.get_dataset_info(self.dataset_dir)
            
            if not dataset_info["is_valid"]:
                QMessageBox.critical(self, "错误", f"数据集格式不正确: {dataset_info['message']}")
                return
            
            # 解析数据集获取类别信息
            from ..core.converter import PARSERS
            detected_format = dataset_info["detected_format"] or self.format_combo.currentText()
            parser = PARSERS[detected_format]
            
            if hasattr(parser, "set_label_map"):
                parser.set_label_map({})
            
            annotations = parser.parse(self.dataset_dir)
            
            if not annotations:
                QMessageBox.warning(self, "警告", "未找到有效的标注数据")
                return
            
            # 生成YOLO配置
            success = self.create_yolo_config(annotations, dataset_info["statistics"], Path(output_dir))
            
            if success:
                QMessageBox.information(self, "完成", "YOLO训练配置生成完成！")
                self.result_text.setText(f"YOLO训练配置已生成\n保存目录: {output_dir}")
            else:
                QMessageBox.critical(self, "错误", "配置生成失败")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成失败: {str(e)}")
            print(f"YOLO配置生成错误详情: {e}")  # 调试用
    
    def create_yolo_config(self, annotations, stats, output_dir):
        """创建YOLO训练配置"""
        # 收集所有类别
        categories = set()
        for ann in annotations:
            for box in ann.boxes:
                categories.add(box.label)
            if ann.polygons:
                for poly in ann.polygons:
                    categories.add(poly.label)
        
        class_names = sorted(list(categories))
        
        # 生成data.yaml文件
        data_yaml = f"""# DataForge生成的YOLO训练配置
path: {self.dataset_dir.absolute()}  # 数据集根目录
train: images/train  # 训练图片路径
val: images/val      # 验证图片路径
test: images/test    # 测试图片路径（可选）

# 类别数量
nc: {len(class_names)}

# 类别名称
names: {class_names}
"""
        
        # 保存data.yaml
        data_yaml_path = output_dir / "data.yaml"
        data_yaml_path.write_text(data_yaml, encoding="utf-8")
        
        # 生成classes.txt文件
        classes_txt_path = output_dir / "classes.txt"
        classes_txt_path.write_text("\n".join(class_names), encoding="utf-8")
        
        # 生成训练脚本示例
        train_script = f"""#!/usr/bin/env python3
# DataForge生成的YOLO训练脚本示例

import torch
from ultralytics import YOLO

def main():
    # 加载预训练模型
    model = YOLO('yolov8n.pt')  # 可选: yolov8s.pt, yolov8m.pt, yolov8l.pt, yolov8x.pt
    
    # 训练模型
    results = model.train(
        data='{data_yaml_path.absolute()}',
        epochs=100,
        imgsz=640,
        batch=16,
        device='0',  # GPU设备，使用'cpu'进行CPU训练
        workers=8,
        project='runs/train',
        name='exp'
    )
    
    # 验证模型
    metrics = model.val()
    
    # 导出模型
    model.export(format='onnx')

if __name__ == '__main__':
    main()
"""
        
        train_script_path = output_dir / "train.py"
        train_script_path.write_text(train_script, encoding="utf-8")
        
        # 生成README文件
        readme_content = f"""# YOLO训练配置

## 数据集信息
- 数据集路径: {self.dataset_dir}
- 类别数量: {len(class_names)}
- 图片总数: {stats['total_images']}
- 标签总数: {stats['total_labels']}

## 类别列表
{chr(10).join(f"{i}: {name}" for i, name in enumerate(class_names))}

## 使用方法

### 1. 安装依赖
```bash
pip install ultralytics
```

### 2. 开始训练
```bash
python train.py
```

### 3. 自定义训练参数
编辑 `train.py` 文件中的参数：
- epochs: 训练轮数
- imgsz: 输入图片尺寸
- batch: 批次大小
- device: 设备选择 ('0', '1', 'cpu')

## 文件说明
- `data.yaml`: YOLO数据集配置文件
- `classes.txt`: 类别名称列表
- `train.py`: 训练脚本示例
- `README.md`: 使用说明
"""
        
        readme_path = output_dir / "README.md"
        readme_path.write_text(readme_content, encoding="utf-8")
        
        return True
    
    def generate_report(self):
        """生成数据集报告"""
        if not self.dataset_dir:
            QMessageBox.warning(self, "警告", "请先选择数据集目录")
            return
        
        output_file, _ = QFileDialog.getSaveFileName(self, "保存报告文件", 
                                                   f"{self.dataset_dir.name}_report.html", 
                                                   "HTML Files (*.html)")
        if not output_file:
            return
        
        try:
            # 验证数据集格式
            from ..core.dataset_validator import DatasetValidator
            dataset_info = DatasetValidator.get_dataset_info(self.dataset_dir)
            
            if not dataset_info["is_valid"]:
                QMessageBox.critical(self, "错误", f"数据集格式不正确: {dataset_info['message']}")
                return
            
            # 解析数据集
            from ..core.converter import PARSERS
            detected_format = dataset_info["detected_format"] or self.format_combo.currentText()
            parser = PARSERS[detected_format]
            
            if hasattr(parser, "set_label_map"):
                parser.set_label_map({})
            
            annotations = parser.parse(self.dataset_dir)
            
            # 生成报告
            success = self.create_html_report(annotations, dataset_info, Path(output_file))
            
            if success:
                QMessageBox.information(self, "完成", "数据集报告生成完成！")
                self.result_text.setText(f"数据集报告已生成\n文件位置: {output_file}")
            else:
                QMessageBox.critical(self, "错误", "报告生成失败")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成失败: {str(e)}")
            print(f"报告生成错误详情: {e}")  # 调试用
    
    def create_html_report(self, annotations, dataset_info, output_file):
        """创建HTML报告"""
        from datetime import datetime
        
        # 计算统计信息
        total_annotations = sum(len(ann.boxes) + (len(ann.polygons) if ann.polygons else 0) 
                              for ann in annotations)
        
        # 类别统计
        class_counts = {}
        for ann in annotations:
            for box in ann.boxes:
                class_counts[box.label] = class_counts.get(box.label, 0) + 1
            if ann.polygons:
                for poly in ann.polygons:
                    class_counts[poly.label] = class_counts.get(poly.label, 0) + 1
        
        # 图片尺寸统计
        widths = [ann.width for ann in annotations if ann.width > 0]
        heights = [ann.height for ann in annotations if ann.height > 0]
        
        # 生成HTML报告
        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DataForge 数据集分析报告</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2196F3; text-align: center; margin-bottom: 30px; }}
        h2 {{ color: #333; border-bottom: 2px solid #2196F3; padding-bottom: 10px; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #2196F3; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #2196F3; }}
        .stat-label {{ color: #666; margin-top: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #2196F3; color: white; }}
        tr:hover {{ background-color: #f5f5f5; }}
        .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 DataForge 数据集分析报告</h1>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{len(annotations):,}</div>
                <div class="stat-label">总图片数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_annotations:,}</div>
                <div class="stat-label">总标注数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(class_counts)}</div>
                <div class="stat-label">类别数量</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(dataset_info['statistics']['subsets'])}</div>
                <div class="stat-label">数据子集</div>
            </div>
        </div>
        
        <h2>📁 数据集基本信息</h2>
        <table>
            <tr><th>项目</th><th>值</th></tr>
            <tr><td>数据集路径</td><td>{self.dataset_dir}</td></tr>
            <tr><td>检测格式</td><td>{dataset_info.get('detected_format', '未知')}</td></tr>
            <tr><td>验证状态</td><td>{'✅ 有效' if dataset_info['is_valid'] else '❌ 无效'}</td></tr>
            <tr><td>图片格式</td><td>{', '.join(dataset_info['statistics']['image_formats'])}</td></tr>
            <tr><td>标签格式</td><td>{', '.join(dataset_info['statistics']['label_formats'])}</td></tr>
        </table>
        
        <h2>📊 子集分布</h2>
        <table>
            <tr><th>子集</th><th>图片数量</th><th>标签数量</th></tr>"""
        
        for subset, counts in dataset_info['statistics']['subsets'].items():
            html_content += f"""
            <tr><td>{subset}</td><td>{counts['images']:,}</td><td>{counts['labels']:,}</td></tr>"""
        
        html_content += f"""
        </table>
        
        <h2>🏷️ 类别分布</h2>
        <table>
            <tr><th>类别名称</th><th>标注数量</th><th>占比</th></tr>"""
        
        for class_name, count in sorted(class_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_annotations) * 100 if total_annotations > 0 else 0
            html_content += f"""
            <tr><td>{class_name}</td><td>{count:,}</td><td>{percentage:.1f}%</td></tr>"""
        
        if widths and heights:
            avg_width = sum(widths) / len(widths)
            avg_height = sum(heights) / len(heights)
            html_content += f"""
        </table>
        
        <h2>📐 图片尺寸统计</h2>
        <table>
            <tr><th>统计项</th><th>宽度</th><th>高度</th></tr>
            <tr><td>平均尺寸</td><td>{avg_width:.0f} px</td><td>{avg_height:.0f} px</td></tr>
            <tr><td>最大尺寸</td><td>{max(widths)} px</td><td>{max(heights)} px</td></tr>
            <tr><td>最小尺寸</td><td>{min(widths)} px</td><td>{min(heights)} px</td></tr>
        </table>"""
        
        html_content += f"""
        
        <div class="footer">
            <p>📅 报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>🛠️ 由 DataForge v2.0 生成</p>
        </div>
    </div>
</body>
</html>"""
        
        # 保存HTML文件
        output_file.write_text(html_content, encoding="utf-8")
        
        return True