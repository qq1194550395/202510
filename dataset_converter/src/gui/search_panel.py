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
        # 为按钮设置属性
        for btn in self.findChildren(QPushButton):
            if "导出" in btn.text() or "生成" in btn.text():
                btn.setProperty("buttonType", "success")
            elif "重置" in btn.text():
                btn.setProperty("buttonType", "warning")
            else:
                btn.setProperty("buttonType", "default")
    
    def load_dataset(self):
        """加载数据集"""
        directory = QFileDialog.getExistingDirectory(self, "选择数据集目录")
        if not directory:
            return
        
        try:
            # 验证数据集结构
            from ..core.dataset_validator import DatasetValidator
            dataset_info = DatasetValidator.get_dataset_info(Path(directory))
            
            if not dataset_info["is_valid"]:
                QMessageBox.critical(self, "数据集格式错误", 
                    f"数据集格式不符合要求:\n{dataset_info['message']}\n\n"
                    f"请确保数据集采用以下结构:\n"
                    f"数据集名称/\n"
                    f"├── images/\n"
                    f"│   ├── train/\n"
                    f"│   ├── test/\n"
                    f"│   └── val/\n"
                    f"└── labels/\n"
                    f"    ├── train/\n"
                    f"    ├── test/\n"
                    f"    └── val/")
                return
            
            self.dataset_dir = Path(directory)
            self.dataset_label.setText(f"数据集: {directory}")
            
            # 自动检测格式或使用用户选择的格式
            detected_format = dataset_info["detected_format"]
            if detected_format:
                # 更新格式选择框
                format_index = self.format_combo.findText(detected_format)
                if format_index >= 0:
                    self.format_combo.setCurrentIndex(format_index)
                format_name = detected_format
            else:
                format_name = self.format_combo.currentText()
            
            # 解析数据集
            parser = PARSERS[format_name]
            
            # 如果解析器支持标签映射，设置空映射避免错误
            if hasattr(parser, "set_label_map"):
                parser.set_label_map({})
            
            self.annotations = parser.parse(self.dataset_dir)
            
            if self.annotations:
                self.filtered_annotations = self.annotations.copy()
                self.update_results()
                
                stats = dataset_info["statistics"]
                QMessageBox.information(self, "加载成功", 
                    f"数据集加载成功！\n"
                    f"格式: {format_name.upper()}\n"
                    f"图片总数: {stats['total_images']}\n"
                    f"标签总数: {stats['total_labels']}\n"
                    f"子集: {', '.join(stats['subsets'].keys())}\n"
                    f"解析到 {len(self.annotations)} 个有效标注")
            else:
                QMessageBox.warning(self, "警告", "数据集结构正确，但未找到有效的标注数据，请检查标签文件内容")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载数据集失败: {str(e)}")
            print(f"详细错误信息: {e}")  # 调试用
    
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
            from ..core.converter import PARSERS
            
            # 获取当前格式
            format_name = self.format_combo.currentText()
            
            # 创建输出目录结构
            output_path = Path(output_dir) / "filtered_dataset"
            output_path.mkdir(parents=True, exist_ok=True)
            
            # 创建标准目录结构
            for subset in ["train"]:  # 筛选结果统一放在train目录
                (output_path / "images" / subset).mkdir(parents=True, exist_ok=True)
                (output_path / "labels" / subset).mkdir(parents=True, exist_ok=True)
            
            # 复制图片文件
            import shutil
            copied_images = 0
            
            for ann in self.filtered_annotations:
                if ann.image_path.exists():
                    # 复制图片到新位置
                    dest_img = output_path / "images" / "train" / ann.image_path.name
                    shutil.copy2(ann.image_path, dest_img)
                    copied_images += 1
            
            # 导出标签
            exporter = PARSERS[format_name]
            if hasattr(exporter, "set_label_map"):
                exporter.set_label_map({})
            
            # 导出到labels/train目录
            exporter.export(self.filtered_annotations, output_path / "labels" / "train")
            
            # 创建说明文件
            readme_content = f"""# 筛选后的数据集

## 筛选条件
- 原始数据集: {self.dataset_dir}
- 筛选结果: {len(self.filtered_annotations)} / {len(self.annotations)} 张图片
- 格式: {format_name.upper()}

## 目录结构
```
filtered_dataset/
├── images/
│   └── train/          # 筛选后的图片
└── labels/
    └── train/          # 筛选后的标签
```

## 统计信息
- 图片数量: {copied_images}
- 标注数量: {sum(len(ann.boxes) + (len(ann.polygons) if ann.polygons else 0) for ann in self.filtered_annotations)}
"""
            
            (output_path / "README.md").write_text(readme_content, encoding="utf-8")
            
            QMessageBox.information(self, "导出成功", 
                f"筛选结果已导出到: {output_path}\n"
                f"图片数量: {copied_images}\n"
                f"标注数量: {len(self.filtered_annotations)}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败: {str(e)}")
            print(f"导出错误详情: {e}")  # 调试用
    
    def generate_stats(self):
        """生成统计报告"""
        if not self.filtered_annotations:
            QMessageBox.warning(self, "提示", "没有数据可统计")
            return
        
        try:
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
            
            # 尺寸统计
            widths = [ann.width for ann in self.filtered_annotations if ann.width > 0]
            heights = [ann.height for ann in self.filtered_annotations if ann.height > 0]
            
            # 标注数量统计
            annotations_per_image = [len(ann.boxes) + (len(ann.polygons) if ann.polygons else 0) 
                                   for ann in self.filtered_annotations]
            
            # 生成详细报告
            report = f"DataForge 数据集统计报告\n"
            report += f"=" * 50 + "\n"
            report += f"生成时间: {Path().cwd()}\n"
            report += f"数据集路径: {self.dataset_dir}\n"
            report += f"筛选条件: 已应用\n\n"
            
            report += f"基本统计:\n"
            report += f"-" * 20 + "\n"
            report += f"图片总数: {total_images:,}\n"
            report += f"矩形框总数: {total_boxes:,}\n"
            report += f"多边形总数: {total_polygons:,}\n"
            report += f"类别数量: {len(class_counts)}\n\n"
            
            if widths and heights:
                import statistics
                report += f"图片尺寸统计:\n"
                report += f"-" * 20 + "\n"
                report += f"平均宽度: {statistics.mean(widths):.1f} 像素\n"
                report += f"平均高度: {statistics.mean(heights):.1f} 像素\n"
                report += f"最大尺寸: {max(widths)} x {max(heights)}\n"
                report += f"最小尺寸: {min(widths)} x {min(heights)}\n\n"
            
            if annotations_per_image:
                import statistics
                report += f"标注密度统计:\n"
                report += f"-" * 20 + "\n"
                report += f"平均每图标注数: {statistics.mean(annotations_per_image):.2f}\n"
                report += f"最多标注数: {max(annotations_per_image)}\n"
                report += f"最少标注数: {min(annotations_per_image)}\n\n"
            
            report += f"类别分布:\n"
            report += f"-" * 20 + "\n"
            for class_name, count in sorted(class_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / (total_boxes + total_polygons)) * 100 if (total_boxes + total_polygons) > 0 else 0
                report += f"  {class_name}: {count:,} ({percentage:.1f}%)\n"
            
            # 询问是否保存到文件
            reply = QMessageBox.question(self, "统计报告", 
                f"统计报告生成完成！\n\n{report[:500]}...\n\n是否保存到文件？",
                QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                from PyQt5.QtWidgets import QFileDialog
                file_path, _ = QFileDialog.getSaveFileName(
                    self, "保存统计报告", 
                    f"dataset_stats_report.txt", 
                    "文本文件 (*.txt);;所有文件 (*)")
                
                if file_path:
                    Path(file_path).write_text(report, encoding="utf-8")
                    QMessageBox.information(self, "保存成功", f"统计报告已保存到: {file_path}")
            else:
                # 显示简化版本
                short_report = f"数据集统计报告\n"
                short_report += f"=" * 30 + "\n"
                short_report += f"图片总数: {total_images}\n"
                short_report += f"矩形框总数: {total_boxes}\n"
                short_report += f"多边形总数: {total_polygons}\n"
                short_report += f"类别数量: {len(class_counts)}\n\n"
                
                short_report += "类别分布 (前10个):\n"
                for class_name, count in list(sorted(class_counts.items(), key=lambda x: x[1], reverse=True))[:10]:
                    short_report += f"  {class_name}: {count}\n"
                
                QMessageBox.information(self, "统计报告", short_report)
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成统计报告失败: {str(e)}")
            print(f"统计报告错误详情: {e}")  # 调试用