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
        
        # 应用统一样式
        self.setStyleSheet(AppStyles.get_panel_style())
        
        # 数据集选择 - 固定在顶部
        path_layout = QHBoxLayout()
        self.path_label = QLabel("数据集目录: 未选择")
        self.path_label.setStyleSheet(AppStyles.get_label_style("status"))
        btn_select = QPushButton("选择数据集目录")
        btn_select.setStyleSheet(AppStyles.get_button_style("primary"))
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
        self.result_text.setStyleSheet(AppStyles.get_textedit_style())
        
        result_label = QLabel("分析结果:")
        result_label.setStyleSheet(AppStyles.get_label_style("subtitle"))
        main_layout.addWidget(result_label)
        main_layout.addWidget(self.result_text)
        
        # 进度条 - 固定在底部
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(AppStyles.get_progressbar_style())
        main_layout.addWidget(self.progress_bar)
    
    def setup_analysis_group(self, layout):
        """设置分析功能组"""
        group = QGroupBox("数据集分析")
        group_layout = QHBoxLayout(group)
        
        btn_analyze = QPushButton("统计分析")
        btn_analyze.setStyleSheet(AppStyles.get_button_style("primary"))
        btn_analyze.clicked.connect(self.analyze_dataset)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["yolo", "json"])
        self.format_combo.setStyleSheet(AppStyles.get_combobox_style())
        
        group_layout.addWidget(QLabel("格式:"))
        group_layout.addWidget(self.format_combo)
        group_layout.addWidget(btn_analyze)
        
        layout.addWidget(group)
    
    def setup_validation_group(self, layout):
        """设置验证功能组"""
        group = QGroupBox("数据集验证与修复")
        group_layout = QHBoxLayout(group)
        
        btn_validate = QPushButton("质量检查")
        btn_validate.setStyleSheet(AppStyles.get_button_style("primary"))
        btn_validate.clicked.connect(self.validate_dataset)
        
        btn_fix = QPushButton("自动修复")
        btn_fix.setStyleSheet(AppStyles.get_button_style("warning"))
        btn_fix.clicked.connect(self.fix_dataset)
        
        btn_compare = QPushButton("数据集比较")
        btn_compare.setStyleSheet(AppStyles.get_button_style("default"))
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
        btn_visualize.setStyleSheet(AppStyles.get_button_style("primary"))
        btn_visualize.clicked.connect(self.visualize_annotations)
        
        btn_preview = QPushButton("生成预览图")
        btn_preview.setStyleSheet(AppStyles.get_button_style("default"))
        btn_preview.clicked.connect(self.create_preview)
        
        group_layout.addWidget(btn_visualize)
        group_layout.addWidget(btn_preview)
        layout.addWidget(group)
    
    def setup_fixing_group(self, layout):
        """设置修复功能组"""
        group = QGroupBox("数据清理")
        group_layout = QGridLayout(group)
        
        btn_remove_small = QPushButton("移除小标注")
        btn_remove_small.setStyleSheet(AppStyles.get_button_style("warning"))
        btn_remove_small.clicked.connect(self.remove_small_annotations)
        
        btn_normalize_ids = QPushButton("标准化类别ID")
        btn_normalize_ids.setStyleSheet(AppStyles.get_button_style("default"))
        btn_normalize_ids.clicked.connect(self.normalize_class_ids)
        
        btn_find_duplicates = QPushButton("查找重复文件")
        btn_find_duplicates.setStyleSheet(AppStyles.get_button_style("default"))
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
        btn_export_zip.setStyleSheet(AppStyles.get_button_style("primary"))
        btn_export_zip.clicked.connect(self.export_zip)
        
        btn_export_coco = QPushButton("导出COCO")
        btn_export_coco.setStyleSheet(AppStyles.get_button_style("default"))
        btn_export_coco.clicked.connect(self.export_coco)
        
        btn_export_config = QPushButton("生成训练配置")
        btn_export_config.setStyleSheet(AppStyles.get_button_style("default"))
        btn_export_config.clicked.connect(self.export_yolo_config)
        
        btn_generate_report = QPushButton("生成报告")
        btn_generate_report.setStyleSheet(AppStyles.get_button_style("success"))
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
            checkbox.setStyleSheet(AppStyles.get_checkbox_style())
            self.aug_checkboxes[option] = checkbox
            group_layout.addWidget(checkbox, i // 3, i % 3)
        
        # 倍数选择
        group_layout.addWidget(QLabel("增强倍数:"), 2, 0)
        self.multiplier_spin = QSpinBox()
        self.multiplier_spin.setRange(2, 10)
        self.multiplier_spin.setValue(3)
        self.multiplier_spin.setStyleSheet(AppStyles.get_spinbox_style())
        group_layout.addWidget(self.multiplier_spin, 2, 1)
        
        btn_augment = QPushButton("开始增强")
        btn_augment.setStyleSheet(AppStyles.get_button_style("success"))
        btn_augment.clicked.connect(self.augment_dataset)
        group_layout.addWidget(btn_augment, 2, 2)
        
        layout.addWidget(group)
    
    def setup_organization_group(self, layout):
        """设置整理功能组"""
        group = QGroupBox("数据集整理")
        group_layout = QGridLayout(group)
        
        # 重命名
        btn_rename = QPushButton("批量重命名")
        btn_rename.setStyleSheet(AppStyles.get_button_style("default"))
        btn_rename.clicked.connect(self.rename_files)
        group_layout.addWidget(btn_rename, 0, 0)
        
        # 数据集划分
        btn_split = QPushButton("划分数据集")
        btn_split.setStyleSheet(AppStyles.get_button_style("primary"))
        btn_split.clicked.connect(self.split_dataset)
        group_layout.addWidget(btn_split, 0, 1)
        
        # 合并数据集
        btn_merge = QPushButton("合并数据集")
        btn_merge.setStyleSheet(AppStyles.get_button_style("default"))
        btn_merge.clicked.connect(self.merge_datasets)
        group_layout.addWidget(btn_merge, 0, 2)
        
        layout.addWidget(group)
    
    def select_dataset(self):
        """选择数据集目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择数据集目录")
        if dir_path:
            self.dataset_dir = Path(dir_path)
            self.path_label.setText(f"数据集目录: {dir_path}")
    
    def analyze_dataset(self):
        """分析数据集"""
        if not self.dataset_dir:
            QMessageBox.warning(self, "警告", "请先选择数据集目录")
            return
        
        format_type = self.format_combo.currentText()
        result = self.analyzer.analyze_dataset(self.dataset_dir, format_type)
        
        # 格式化显示结果
        output = self.format_analysis_result(result)
        self.result_text.setText(output)
    
    def validate_dataset(self):
        """验证数据集质量"""
        if not self.dataset_dir:
            QMessageBox.warning(self, "警告", "请先选择数据集目录")
            return
        
        result = self.validator.validate_yolo_dataset(self.dataset_dir)
        
        output = f"数据集健康度评分: {result['health_score']:.1f}/100\n\n"
        output += f"统计信息:\n"
        for key, value in result['stats'].items():
            output += f"  {key}: {value}\n"
        
        if result['issues']:
            output += f"\n发现的问题 ({len(result['issues'])} 个):\n"
            for issue in result['issues'][:20]:  # 只显示前20个问题
                output += f"  - {issue}\n"
            if len(result['issues']) > 20:
                output += f"  ... 还有 {len(result['issues']) - 20} 个问题\n"
        
        self.result_text.setText(output)
    
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
            self.augmentor.augment_dataset(
                self.dataset_dir, Path(output_dir), selected_augs, multiplier
            )
            QMessageBox.information(self, "完成", "数据增强完成！")
            self.result_text.setText(f"数据增强完成\n输出目录: {output_dir}\n增强倍数: {multiplier}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"数据增强失败: {e}")
    
    def rename_files(self):
        """批量重命名"""
        if not self.dataset_dir:
            QMessageBox.warning(self, "警告", "请先选择数据集目录")
            return
        
        try:
            self.organizer.rename_files(self.dataset_dir, "img", 0)
            QMessageBox.information(self, "完成", "文件重命名完成！")
            self.result_text.setText("批量重命名完成")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"重命名失败: {e}")
    
    def split_dataset(self):
        """划分数据集"""
        if not self.dataset_dir:
            QMessageBox.warning(self, "警告", "请先选择数据集目录")
            return
        
        output_dir = QFileDialog.getExistingDirectory(self, "选择划分后数据集保存目录")
        if not output_dir:
            return
        
        try:
            result = self.organizer.split_dataset(self.dataset_dir, Path(output_dir))
            QMessageBox.information(self, "完成", "数据集划分完成！")
            
            output = f"数据集划分完成\n"
            output += f"训练集: {result['train']} 张\n"
            output += f"验证集: {result['val']} 张\n"
            output += f"测试集: {result['test']} 张\n"
            self.result_text.setText(output)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"数据集划分失败: {e}")
    
    def merge_datasets(self):
        """合并数据集"""
        dirs = QFileDialog.getExistingDirectory(self, "选择要合并的数据集目录")
        if not dirs:
            return
        
        # 这里简化处理，实际可以支持选择多个目录
        output_dir = QFileDialog.getExistingDirectory(self, "选择合并后数据集保存目录")
        if not output_dir:
            return
        
        try:
            count = self.organizer.merge_datasets([Path(dirs)], Path(output_dir))
            QMessageBox.information(self, "完成", f"数据集合并完成！共处理 {count} 个文件")
            self.result_text.setText(f"数据集合并完成\n处理文件数: {count}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"数据集合并失败: {e}")
    
    def format_analysis_result(self, result: dict) -> str:
        """格式化分析结果"""
        if 'error' in result:
            return f"错误: {result['error']}"
        
        output = f"数据集统计分析\n{'='*50}\n\n"
        
        # 基本统计
        output += f"总图片数: {result.get('total_images', 0)}\n"
        output += f"总标注数: {result.get('total_annotations', 0)}\n\n"
        
        # 类别分布
        if 'class_distribution' in result:
            output += "类别分布:\n"
            for class_id, count in result['class_distribution'].items():
                output += f"  {class_id}: {count}\n"
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
            output += f"  平均每张图片标注数: {stats['avg_per_image']:.1f}\n"
            output += f"  标注数范围: {stats['min_per_image']} ~ {stats['max_per_image']}\n"
            output += f"  无标注图片数: {stats['images_without_annotations']}\n\n"
        
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
            fixes = self.fixer.fix_dataset(self.dataset_dir, create_backup)
            
            output = "数据集修复完成:\n"
            output += f"- 坐标修复: {fixes['coordinate_fixes']} 个文件\n"
            output += f"- 创建缺失标注: {fixes['missing_annotations_created']} 个\n"
            output += f"- 移除无效文件: {fixes['invalid_files_removed']} 个\n"
            output += f"- 移除重复文件: {fixes['duplicate_files_removed']} 个\n"
            
            self.result_text.setText(output)
            QMessageBox.information(self, "完成", "数据集修复完成！")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"修复失败: {e}")
    
    def compare_datasets(self):
        """比较数据集"""
        if not self.dataset_dir:
            QMessageBox.warning(self, "警告", "请先选择第一个数据集目录")
            return
        
        dataset2_dir = QFileDialog.getExistingDirectory(self, "选择第二个数据集目录")
        if not dataset2_dir:
            return
        
        try:
            result = self.comparator.compare_datasets(self.dataset_dir, Path(dataset2_dir))
            
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
            QMessageBox.critical(self, "错误", f"比较失败: {e}")
    
    def visualize_annotations(self):
        """可视化标注"""
        if not self.dataset_dir:
            QMessageBox.warning(self, "警告", "请先选择数据集目录")
            return
        
        output_dir = QFileDialog.getExistingDirectory(self, "选择可视化结果保存目录")
        if not output_dir:
            return
        
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # 可视化前10张图片
            image_files = list(self.dataset_dir.glob('*.jpg')) + list(self.dataset_dir.glob('*.png'))
            processed = 0
            
            for img_file in image_files[:10]:
                txt_file = img_file.with_suffix('.txt')
                output_file = output_path / f"vis_{img_file.name}"
                
                if self.visualizer.visualize_yolo_annotations(img_file, txt_file, output_file):
                    processed += 1
            
            QMessageBox.information(self, "完成", f"已可视化 {processed} 张图片")
            self.result_text.setText(f"标注可视化完成\n处理图片: {processed} 张\n输出目录: {output_dir}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"可视化失败: {e}")
    
    def create_preview(self):
        """创建预览图"""
        if not self.dataset_dir:
            QMessageBox.warning(self, "警告", "请先选择数据集目录")
            return
        
        output_dir = QFileDialog.getExistingDirectory(self, "选择预览图保存目录")
        if not output_dir:
            return
        
        try:
            preview_path = self.visualizer.create_dataset_preview(
                self.dataset_dir, Path(output_dir)
            )
            QMessageBox.information(self, "完成", f"预览图已生成: {preview_path}")
            self.result_text.setText(f"数据集预览图生成完成\n保存位置: {preview_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成预览图失败: {e}")
    
    def remove_small_annotations(self):
        """移除小标注"""
        if not self.dataset_dir:
            QMessageBox.warning(self, "警告", "请先选择数据集目录")
            return
        
        min_area, ok = QInputDialog.getDouble(self, "设置最小面积", 
                                            "最小标注面积 (0-1):", 0.001, 0, 1, 4)
        if not ok:
            return
        
        try:
            removed_count = self.fixer.remove_small_annotations(self.dataset_dir, min_area)
            QMessageBox.information(self, "完成", f"已移除 {removed_count} 个小标注")
            self.result_text.setText(f"小标注清理完成\n移除数量: {removed_count}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"清理失败: {e}")
    
    def normalize_class_ids(self):
        """标准化类别ID"""
        if not self.dataset_dir:
            QMessageBox.warning(self, "警告", "请先选择数据集目录")
            return
        
        # 这里简化处理，实际可以提供更复杂的映射界面
        QMessageBox.information(self, "提示", "此功能需要提供类别映射文件")
    
    def find_duplicates(self):
        """查找重复文件"""
        if not self.dataset_dir:
            QMessageBox.warning(self, "警告", "请先选择数据集目录")
            return
        
        try:
            duplicates = self.comparator.find_duplicate_images(self.dataset_dir)
            
            if duplicates:
                output = f"发现 {len(duplicates)} 组可能的重复文件:\n\n"
                for i, (file1, file2) in enumerate(duplicates[:20]):  # 只显示前20组
                    output += f"{i+1}. {file1} <-> {file2}\n"
                if len(duplicates) > 20:
                    output += f"\n... 还有 {len(duplicates) - 20} 组重复文件"
            else:
                output = "未发现重复文件"
            
            self.result_text.setText(output)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"查找失败: {e}")
    
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
            success = self.exporter.export_to_zip(self.dataset_dir, Path(output_file))
            if success:
                QMessageBox.information(self, "完成", "ZIP导出完成！")
                self.result_text.setText(f"数据集已导出为ZIP\n文件位置: {output_file}")
            else:
                QMessageBox.critical(self, "错误", "ZIP导出失败")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败: {e}")
    
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
            success = self.exporter.export_coco_format(self.dataset_dir, Path(output_file))
            if success:
                QMessageBox.information(self, "完成", "COCO格式导出完成！")
                self.result_text.setText(f"数据集已导出为COCO格式\n文件位置: {output_file}")
            else:
                QMessageBox.critical(self, "错误", "COCO导出失败")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败: {e}")
    
    def export_yolo_config(self):
        """导出YOLO训练配置"""
        if not self.dataset_dir:
            QMessageBox.warning(self, "警告", "请先选择数据集目录")
            return
        
        output_dir = QFileDialog.getExistingDirectory(self, "选择配置文件保存目录")
        if not output_dir:
            return
        
        try:
            success = self.exporter.export_yolo_config(self.dataset_dir, Path(output_dir))
            if success:
                QMessageBox.information(self, "完成", "YOLO训练配置生成完成！")
                self.result_text.setText(f"YOLO训练配置已生成\n保存目录: {output_dir}")
            else:
                QMessageBox.critical(self, "错误", "配置生成失败")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成失败: {e}")
    
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
            success = self.exporter.create_dataset_report(self.dataset_dir, Path(output_file))
            if success:
                QMessageBox.information(self, "完成", "数据集报告生成完成！")
                self.result_text.setText(f"数据集报告已生成\n文件位置: {output_file}")
            else:
                QMessageBox.critical(self, "错误", "报告生成失败")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成失败: {e}")