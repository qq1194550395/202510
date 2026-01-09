from pathlib import Path

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QFrame

from .main_window import MainWindow
from .styles import AppStyles


class HomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DataForge v2.0")
        icon_path = Path(__file__).parent.parent.parent / "resources" / "icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # 设置窗口尺寸，适应更多内容
        self.setFixedSize(1200, 800)
        
        # 应用主题管理器样式
        from .theme_manager import theme_manager
        self.setStyleSheet(theme_manager.generate_stylesheet())

        central = QWidget(self)
        self.setCentralWidget(central)

        outer = QHBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # 左侧功能列表
        self.menu = QListWidget()
        self.menu.setFixedWidth(260)
        self.menu.setIconSize(QSize(24, 24))
        
        menu_icon = QIcon(str(icon_path)) if icon_path.exists() else None
        
        # 添加功能菜单项
        menu_items = [
            "数据集格式转换",
            "数据集划分", 
            "数据集分析",
            "数据可视化",
            "数据搜索",
            "设置"
        ]
        
        for item_text in menu_items:
            item = QListWidgetItem(item_text)
            if menu_icon:
                item.setIcon(menu_icon)
            self.menu.addItem(item)
            
        outer.addWidget(self.menu)

        # 分隔线
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setFrameShadow(QFrame.Sunken)
        outer.addWidget(sep)

        # 右侧内容区
        from .converter_panel import ConverterPanel
        from .splitting_panel import SplittingPanel
        from .analysis_panel import AnalysisPanel
        from .settings_panel import SettingsPanel
        from .search_panel import SearchPanel
        
        self.content = QWidget()
        content_layout = QVBoxLayout(self.content)
        content_layout.setContentsMargins(16, 16, 16, 16)
        
        # 初始化所有面板
        self.converter_panel = ConverterPanel(self)
        self.splitting_panel = SplittingPanel(self)
        self.analysis_panel = AnalysisPanel(self)
        self.settings_panel = SettingsPanel(self)
        self.search_panel = SearchPanel(self)
        self.visualization_panel = self.create_visualization_panel()
        
        content_layout.addWidget(self.converter_panel)
        outer.addWidget(self.content)
        
        # 连接主题管理器信号
        from .theme_manager import theme_manager
        theme_manager.theme_changed.connect(self.apply_theme)
        self.settings_panel.settings_changed.connect(self.apply_theme)

        # 切换逻辑
        self.menu.currentRowChanged.connect(self.on_menu_change)
        self.menu.setCurrentRow(0)

    def on_menu_change(self, idx: int):
        # 清空右侧内容
        for i in range(self.content.layout().count()):
            item = self.content.layout().itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)
        
        # 根据选择显示对应面板
        if idx == 0:  # 数据集格式转换
            self.content.layout().addWidget(self.converter_panel)
        elif idx == 1:  # 数据集划分
            self.content.layout().addWidget(self.splitting_panel)
        elif idx == 2:  # 数据集分析
            self.content.layout().addWidget(self.analysis_panel)
        elif idx == 3:  # 数据可视化
            self.content.layout().addWidget(self.visualization_panel)
        elif idx == 4:  # 数据搜索
            self.content.layout().addWidget(self.search_panel)
        elif idx == 5:  # 设置
            self.content.layout().addWidget(self.settings_panel)
        else:
            placeholder = QWidget()
            ph_layout = QVBoxLayout(placeholder)
            from PyQt5.QtWidgets import QLabel
            ph_layout.addWidget(QLabel("功能暂未实现，敬请期待"))
            self.content.layout().addWidget(placeholder)
    
    def create_visualization_panel(self) -> QWidget:
        """创建可视化面板"""
        from PyQt5.QtWidgets import QLabel, QPushButton, QFileDialog, QMessageBox
        
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 应用主题管理器样式
        from .theme_manager import theme_manager
        panel.setStyleSheet(theme_manager.generate_stylesheet())
        
        # 标题
        title = QLabel("数据可视化")
        title.setProperty("labelType", "title")
        layout.addWidget(title)
        
        # 数据集选择
        dataset_layout = QHBoxLayout()
        self.viz_dataset_label = QLabel("数据集: 未选择")
        self.viz_dataset_label.setProperty("labelType", "status")
        
        btn_select_dataset = QPushButton("选择数据集")
        btn_select_dataset.setProperty("buttonType", "default")
        btn_select_dataset.clicked.connect(self.select_visualization_dataset)
        
        dataset_layout.addWidget(self.viz_dataset_label, 1)
        dataset_layout.addWidget(btn_select_dataset)
        layout.addLayout(dataset_layout)
        
        # 可视化选项
        from PyQt5.QtWidgets import QGroupBox, QGridLayout
        
        viz_group = QGroupBox("可视化选项")
        viz_layout = QGridLayout(viz_group)
        
        # 统计仪表板按钮
        btn_dashboard = QPushButton("生成统计仪表板")
        btn_dashboard.setProperty("buttonType", "primary")
        btn_dashboard.clicked.connect(self.create_dashboard)
        viz_layout.addWidget(btn_dashboard, 0, 0)
        
        # 交互式可视化按钮
        btn_interactive = QPushButton("生成交互式图表")
        btn_interactive.setProperty("buttonType", "success")
        btn_interactive.clicked.connect(self.create_interactive_viz)
        viz_layout.addWidget(btn_interactive, 0, 1)
        
        # 主题选择
        from PyQt5.QtWidgets import QComboBox
        viz_layout.addWidget(QLabel("图表主题:"), 1, 0)
        self.viz_theme_combo = QComboBox()
        self.viz_theme_combo.addItems(["light", "dark"])
        viz_layout.addWidget(self.viz_theme_combo, 1, 1)
        
        layout.addWidget(viz_group)
        
        # 结果显示
        self.viz_result_label = QLabel("请选择数据集并生成可视化")
        self.viz_result_label.setProperty("labelType", "subtitle")
        layout.addWidget(self.viz_result_label)
        
        layout.addStretch()
        
        # 存储数据
        self.viz_annotations = []
        self.viz_dataset_dir = None
        self.visualizer = None  # 延迟初始化
        
        return panel
    
    def select_visualization_dataset(self):
        """选择可视化数据集"""
        from PyQt5.QtWidgets import QFileDialog, QMessageBox, QInputDialog
        
        try:
            directory = QFileDialog.getExistingDirectory(self, "选择数据集目录")
            if not directory:
                return
            
            # 显示验证状态
            self.viz_result_label.setText("正在验证数据集格式...")
            
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
                self.viz_result_label.setText("数据集格式验证失败")
                return
            
            # 自动检测格式或让用户选择
            detected_format = dataset_info["detected_format"]
            if detected_format:
                # 询问用户是否使用检测到的格式
                reply = QMessageBox.question(self, "格式检测", 
                    f"检测到数据集格式为: {detected_format.upper()}\n是否使用此格式？",
                    QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    format_name = detected_format
                else:
                    # 让用户手动选择
                    from ..core.converter import PARSERS
                    formats = list(PARSERS.keys())
                    format_name, ok = QInputDialog.getItem(self, "选择格式", "数据集格式:", formats, 0, False)
                    if not ok:
                        return
            else:
                # 无法自动检测，让用户选择
                from ..core.converter import PARSERS
                formats = list(PARSERS.keys())
                format_name, ok = QInputDialog.getItem(self, "选择格式", "数据集格式:", formats, 0, False)
                if not ok:
                    return
            
            # 显示加载状态
            self.viz_result_label.setText("正在加载数据集...")
            
            # 解析数据集
            self.viz_dataset_dir = Path(directory)
            self.viz_dataset_label.setText(f"数据集: {directory}")
            
            from ..core.converter import PARSERS
            parser = PARSERS[format_name]
            
            # 如果解析器支持标签映射，设置空映射避免错误
            if hasattr(parser, "set_label_map"):
                parser.set_label_map({})
            
            self.viz_annotations = parser.parse(self.viz_dataset_dir)
            
            if self.viz_annotations:
                stats = dataset_info["statistics"]
                self.viz_result_label.setText(
                    f"数据集加载成功！\n"
                    f"格式: {format_name.upper()}\n"
                    f"图片总数: {stats['total_images']}\n"
                    f"标签总数: {stats['total_labels']}\n"
                    f"子集: {', '.join(stats['subsets'].keys())}\n"
                    f"解析到 {len(self.viz_annotations)} 个有效标注"
                )
            else:
                self.viz_result_label.setText("数据集结构正确，但未找到有效的标注数据")
                QMessageBox.warning(self, "警告", "数据集结构正确，但未找到有效的标注数据，请检查标签文件内容")
            
        except ImportError as e:
            QMessageBox.critical(self, "导入错误", f"模块导入失败: {e}")
            self.viz_result_label.setText("模块导入失败")
        except FileNotFoundError as e:
            QMessageBox.critical(self, "文件错误", f"找不到文件: {e}")
            self.viz_result_label.setText("文件未找到")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载数据集失败: {str(e)}")
            self.viz_result_label.setText("数据集加载失败")
            print(f"详细错误信息: {e}")  # 调试用
    
    def create_dashboard(self):
        """创建统计仪表板"""
        if not self.viz_annotations:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "提示", "请先选择数据集")
            return
        
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        
        output_dir = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if not output_dir:
            return
        
        try:
            # 显示处理状态
            self.viz_result_label.setText("正在生成统计仪表板...")
            
            # 延迟初始化可视化器
            if self.visualizer is None:
                from ..core.enhanced_visualizer import EnhancedVisualizer
                self.visualizer = EnhancedVisualizer()
            
            theme = self.viz_theme_combo.currentText()
            self.visualizer.create_statistics_dashboard(
                self.viz_annotations, Path(output_dir), theme
            )
            
            self.viz_result_label.setText(f"统计仪表板已生成到: {output_dir}")
            QMessageBox.information(self, "完成", "统计仪表板生成完成！")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成失败: {str(e)}")
            self.viz_result_label.setText("仪表板生成失败")
            print(f"仪表板生成错误: {e}")  # 调试用
    
    def create_interactive_viz(self):
        """创建交互式可视化"""
        if not self.viz_annotations:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "提示", "请先选择数据集")
            return
        
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        
        output_dir = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if not output_dir:
            return
        
        try:
            # 显示处理状态
            self.viz_result_label.setText("正在生成交互式图表...")
            
            # 延迟初始化可视化器
            if self.visualizer is None:
                from ..core.enhanced_visualizer import EnhancedVisualizer
                self.visualizer = EnhancedVisualizer()
            
            self.visualizer.create_interactive_visualization(
                self.viz_annotations, Path(output_dir)
            )
            
            self.viz_result_label.setText(f"交互式图表已生成到: {output_dir}")
            QMessageBox.information(self, "完成", "交互式可视化生成完成！")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成失败: {str(e)}")
            self.viz_result_label.setText("交互式图表生成失败")
            print(f"交互式图表生成错误: {e}")  # 调试用
    
    def apply_theme(self, theme_name: str = None):
        """应用主题"""
        from .theme_manager import theme_manager
        
        if theme_name is None:
            theme_name = theme_manager.get_current_theme()
        
        # 生成并应用样式表
        stylesheet = theme_manager.generate_stylesheet(theme_name)
        self.setStyleSheet(stylesheet)
