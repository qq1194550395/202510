from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTextEdit, QFileDialog, QMessageBox, QProgressBar, QComboBox,
    QSpinBox, QCheckBox, QGroupBox, QGridLayout
)
from PyQt5.QtCore import QThread, pyqtSignal
from pathlib import Path
import json

from ..core.dataset_analyzer import DatasetAnalyzer
from ..core.dataset_validator import DatasetValidator
from ..core.data_augmentation import DataAugmentor
from ..core.dataset_organizer import DatasetOrganizer


class AnalysisPanel(QWidget):
    """数据集分析面板"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
        self.analyzer = DatasetAnalyzer()
        self.validator = DatasetValidator()
        self.augmentor = DataAugmentor()
        self.organizer = DatasetOrganizer()
        
        self.dataset_dir = None
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 数据集选择
        path_layout = QHBoxLayout()
        self.path_label = QLabel("数据集目录: 未选择")
        btn_select = QPushButton("选择数据集目录")
        btn_select.clicked.connect(self.select_dataset)
        path_layout.addWidget(self.path_label)
        path_layout.addWidget(btn_select)
        layout.addLayout(path_layout)
        
        # 功能按钮组
        self.setup_analysis_group(layout)
        self.setup_validation_group(layout)
        self.setup_augmentation_group(layout)
        self.setup_organization_group(layout)
        
        # 结果显示
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(QLabel("分析结果:"))
        layout.addWidget(self.result_text)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
    
    def setup_analysis_group(self, layout):
        """设置分析功能组"""
        group = QGroupBox("数据集分析")
        group_layout = QHBoxLayout(group)
        
        btn_analyze = QPushButton("统计分析")
        btn_analyze.clicked.connect(self.analyze_dataset)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["yolo", "json"])
        
        group_layout.addWidget(QLabel("格式:"))
        group_layout.addWidget(self.format_combo)
        group_layout.addWidget(btn_analyze)
        
        layout.addWidget(group)
    
    def setup_validation_group(self, layout):
        """设置验证功能组"""
        group = QGroupBox("数据集验证")
        group_layout = QHBoxLayout(group)
        
        btn_validate = QPushButton("质量检查")
        btn_validate.clicked.connect(self.validate_dataset)
        
        group_layout.addWidget(btn_validate)
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
        btn_augment.clicked.connect(self.augment_dataset)
        group_layout.addWidget(btn_augment, 2, 2)
        
        layout.addWidget(group)
    
    def setup_organization_group(self, layout):
        """设置整理功能组"""
        group = QGroupBox("数据集整理")
        group_layout = QGridLayout(group)
        
        # 重命名
        btn_rename = QPushButton("批量重命名")
        btn_rename.clicked.connect(self.rename_files)
        group_layout.addWidget(btn_rename, 0, 0)
        
        # 数据集划分
        btn_split = QPushButton("划分数据集")
        btn_split.clicked.connect(self.split_dataset)
        group_layout.addWidget(btn_split, 0, 1)
        
        # 合并数据集
        btn_merge = QPushButton("合并数据集")
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