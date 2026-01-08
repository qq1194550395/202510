"""
数据集搜索与过滤面板
"""
from pathlib import Path
from typing import List, Dict, Any

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QSpinBox, QComboBox, QListWidget, QGroupBox,
    QCheckBox, QSlider, QFileDialog, QMessageBox, QListWidgetItem
)
from PyQt5.QtCore import Qt

from ..core.base_parser import ImageAnnotation
from ..core.converter import PARSERS
from .styles import AppStyles


class SearchPanel(QWidget):
    """数据集搜索与过滤面板"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.annotations: List[ImageAnnotation] = []
        self.filtered_annotations: List[ImageAnnotation] = []
        self.dataset_dir = None
        
        self.init_ui()
        self.apply_styles()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 数据集加载区域
        load_group = QGroupBox("数据集加载")
        load_layout = QHBoxLayout(load_group)
        
        self.dataset_label = QLabel("数据集: 未选择")
        self.dataset_label.setWordWrap(True)
        
        btn_load = QPushButton("选择数据集目录")
        btn_load.clicked.connect(self.load_dataset)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["yolo", "yolo_seg", "voc", "json"])
        
        load_layout.addWidget(self.dataset_label, 1)
        load_layout.addWidget(QLabel("格式:"))
        load_layout.addWidget(self.format_combo)
        load_layout.addWidget(btn_load)
        
        layout.addWidget(load_group)
        
        # 搜索过滤区域
        filter_group = QGroupBox("搜索与过滤")
        filter_layout = QVBoxLayout(filter_group)
        
        # 文本搜索
        text_layout = QHBoxLayout()
        text_layout.addWidget(QLabel("文件名搜索:"))
        self.filename_edit = QLineEdit()
        self.filename_edit.setPlaceholderText("输入文件名关键词...")
        self.filename_edit.textChanged.connect(self.apply_filters)
        text_layout.addWidget(self.filename_edit)
        filter_layout.addLayout(text_layout)
        
        # 类别搜索
        class_layout = QHBoxLayout()
        class_layout.addWidget(QLabel("类别搜索:"))
        self.class_edit = QLineEdit()
        self.class_edit.setPlaceholderText("输入类别名称...")
        self.class_edit.textChanged.connect(self.apply_filters)
        class_layout.addWidget(self.class_edit)
        filter_layout.addLayout(class_layout)
        
        # 图片尺寸过滤
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("图片宽度:"))
        self.width_min = QSpinBox()
        self.width_min.setRange(0, 10000)
        self.width_min.setValue(0)
        self.width_min.valueChanged.connect(self.apply_filters)
        size_layout.addWidget(self.width_min)
        size_layout.addWidget(QLabel("-"))
        self.width_max = QSpinBox()
        self.width_max.setRange(0, 10000)
        self.width_max.setValue(10000)
        self.width_max.valueChanged.connect(self.apply_filters)
        size_layout.addWidget(self.width_max)
        
        size_layout.addWidget(QLabel("高度:"))
        self.height_min = QSpinBox()
        self.height_min.setRange(0, 10000)
        self.height_min.setValue(0)
        self.height_min.valueChanged.connect(self.apply_filters)
        size_layout.addWidget(self.height_min)
        size_layout.addWidget(QLabel("-"))
        self.height_max = QSpinBox()
        self.height_max.setRange(0, 10000)
        self.height_max.setValue(10000)
        self.height_max.valueChanged.connect(self.apply_filters)
        size_layout.addWidget(self.height_max)
        
        filter_layout.addLayout(size_layout)
        
        # 标注数量过滤
        bbox_layout = QHBoxLayout()
        bbox_layout.addWidget(QLabel("标注框数量:"))
        self.bbox_min = QSpinBox()
        self.bbox_min.setRange(0, 1000)
        self.bbox_min.setValue(0)
        self.bbox_min.valueChanged.connect(self.apply_filters)
        bbox_layout.addWidget(self.bbox_min)
        bbox_layout.addWidget(QLabel("-"))
        self.bbox_max = QSpinBox()
        self.bbox_max.setRange(0, 1000)
        self.bbox_max.setValue(1000)
        self.bbox_max.valueChanged.connect(self.apply_filters)
        bbox_layout.addWidget(self.bbox_max)
        
        # 重置按钮
        btn_reset = QPushButton("重置过滤条件")
        btn_reset.clicked.connect(self.reset_filters)
        bbox_layout.addWidget(btn_reset)
        
        filter_layout.addLayout(bbox_layout)
        layout.addWidget(filter_group)
        
        # 结果显示区域
        result_group = QGroupBox("搜索结果")
        result_layout = QVBoxLayout(result_group)
        
        self.result_label = QLabel("结果: 0 / 0 张图片")
        result_layout.addWidget(self.result_label)
        
        self.result_list = QListWidget()
        self.result_list.itemDoubleClicked.connect(self.show_image_info)
        result_layout.addWidget(self.result_list)
        
        # 导出按钮
        export_layout = QHBoxLayout()
        btn_export_filtered = QPushButton("导出筛选结果")
        btn_export_filtered.clicked.connect(self.export_filtered)
        btn_export_stats = QPushButton("生成统计报告")
        btn_export_stats.clicked.connect(self.generate_stats)
        
        export_layout.addWidget(btn_export_filtered)
        export_layout.addWidget(btn_export_stats)
        result_layout.addLayout(export_layout)
        
        layout.addWidget(result_group)
    
    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet(AppStyles.get_panel_style())
        
        # 为按钮应用样式
        for btn in self.findChildren(QPushButton):
            if "导出" in btn.text() or "生成" in btn.text():
                btn.setStyleSheet(AppStyles.get_button_style("success"))
            elif "重置" in btn.text():
                btn.setStyleSheet(AppStyles.get_button_style("warning"))
            else:
                btn.setStyleSheet(AppStyles.get_button_style("default"))
    
    def load_dataset(self):
        """加载数据集"""
        directory = QFileDialog.getExistingDirectory(self, "选择数据集目录")
        if not directory:
            return
        
        self.dataset_dir = Path(directory)
        self.dataset_label.setText(f"数据集: {directory}")
        
        # 解析数据集
        try:
            format_name = self.format_combo.currentText()
            parser = PARSERS[format_name]
            self.annotations = parser.parse(self.dataset_dir)
            
            self.filtered_annotations = self.annotations.copy()
            self.update_results()
            
            QMessageBox.information(self, "成功", f"已加载 {len(self.annotations)} 张图片")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载数据集失败: {e}")
    
    def apply_filters(self):
        """应用过滤条件"""
        if not self.annotations:
            return
        
        filtered = []
        
        filename_filter = self.filename_edit.text().lower()
        class_filter = self.class_edit.text().lower()
        
        for ann in self.annotations:
            # 文件名过滤
            if filename_filter and filename_filter not in ann.image_path.name.lower():
                continue
            
            # 尺寸过滤
            if not (self.width_min.value() <= ann.width <= self.width_max.value()):
                continue
            if not (self.height_min.value() <= ann.height <= self.height_max.value()):
                continue
            
            # 标注数量过滤
            bbox_count = len(ann.boxes) + (len(ann.polygons) if ann.polygons else 0)
            if not (self.bbox_min.value() <= bbox_count <= self.bbox_max.value()):
                continue
            
            # 类别过滤
            if class_filter:
                has_class = any(class_filter in box.label.lower() for box in ann.boxes)
                if ann.polygons:
                    has_class = has_class or any(class_filter in poly.label.lower() for poly in ann.polygons)
                if not has_class:
                    continue
            
            filtered.append(ann)
        
        self.filtered_annotations = filtered
        self.update_results()
    
    def update_results(self):
        """更新结果显示"""
        total = len(self.annotations)
        filtered = len(self.filtered_annotations)
        
        self.result_label.setText(f"结果: {filtered} / {total} 张图片")
        
        # 更新列表
        self.result_list.clear()
        for ann in self.filtered_annotations:
            bbox_count = len(ann.boxes) + (len(ann.polygons) if ann.polygons else 0)
            item_text = f"{ann.image_path.name} ({ann.width}x{ann.height}, {bbox_count}个标注)"
            self.result_list.addItem(item_text)
    
    def reset_filters(self):
        """重置过滤条件"""
        self.filename_edit.clear()
        self.class_edit.clear()
        self.width_min.setValue(0)
        self.width_max.setValue(10000)
        self.height_min.setValue(0)
        self.height_max.setValue(10000)
        self.bbox_min.setValue(0)
        self.bbox_max.setValue(1000)
        
        self.filtered_annotations = self.annotations.copy()
        self.update_results()
    
    def show_image_info(self, item: QListWidgetItem):
        """显示图片详细信息"""
        row = self.result_list.row(item)
        if row < len(self.filtered_annotations):
            ann = self.filtered_annotations[row]
            
            info = f"文件: {ann.image_path.name}\n"
            info += f"尺寸: {ann.width} x {ann.height}\n"
            info += f"矩形框: {len(ann.boxes)} 个\n"
            if ann.polygons:
                info += f"多边形: {len(ann.polygons)} 个\n"
            
            if ann.boxes:
                info += "\n类别列表:\n"
                classes = set(box.label for box in ann.boxes)
                if ann.polygons:
                    classes.update(poly.label for poly in ann.polygons)
                info += ", ".join(sorted(classes))
            
            QMessageBox.information(self, "图片信息", info)
    
    def export_filtered(self):
        """导出筛选结果"""
        if not self.filtered_annotations:
            QMessageBox.warning(self, "提示", "没有筛选结果可导出")
            return
        
        output_dir = QFileDialog.getExistingDirectory(self, "选择导出目录")
        if not output_dir:
            return
        
        try:
            # 这里可以调用现有的导出功能
            QMessageBox.information(self, "提示", f"筛选结果导出功能待实现\n筛选出 {len(self.filtered_annotations)} 张图片")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败: {e}")
    
    def generate_stats(self):
        """生成统计报告"""
        if not self.filtered_annotations:
            QMessageBox.warning(self, "提示", "没有数据可统计")
            return
        
        # 统计信息
        total_images = len(self.filtered_annotations)
        total_boxes = sum(len(ann.boxes) for ann in self.filtered_annotations)
        total_polygons = sum(len(ann.polygons) if ann.polygons else 0 for ann in self.filtered_annotations)
        
        # 类别统计
        class_counts = {}
        for ann in self.filtered_annotations:
            for box in ann.boxes:
                class_counts[box.label] = class_counts.get(box.label, 0) + 1
            if ann.polygons:
                for poly in ann.polygons:
                    class_counts[poly.label] = class_counts.get(poly.label, 0) + 1
        
        # 生成报告
        report = f"数据集统计报告\n"
        report += f"=" * 30 + "\n"
        report += f"图片总数: {total_images}\n"
        report += f"矩形框总数: {total_boxes}\n"
        report += f"多边形总数: {total_polygons}\n"
        report += f"类别数量: {len(class_counts)}\n\n"
        
        report += "类别分布:\n"
        for class_name, count in sorted(class_counts.items(), key=lambda x: x[1], reverse=True):
            report += f"  {class_name}: {count}\n"
        
        QMessageBox.information(self, "统计报告", report)