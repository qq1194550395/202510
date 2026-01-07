from pathlib import Path

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QFrame

from .main_window import MainWindow
from .styles import AppStyles


class HomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("图片处理软件v1.0")
        icon_path = Path(__file__).parent.parent.parent / "resources" / "icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # 设置窗口尺寸，适应更多内容
        self.setFixedSize(1200, 800)
        
        # 应用统一样式
        self.setStyleSheet(AppStyles.get_main_window_style())

        central = QWidget(self)
        self.setCentralWidget(central)

        outer = QHBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # 左侧功能列表
        self.menu = QListWidget()
        self.menu.setFixedWidth(260)
        self.menu.setIconSize(QSize(24, 24))
        # 移除旧的样式，使用统一样式
        menu_icon = QIcon(str(icon_path)) if icon_path.exists() else None
        item_conv = QListWidgetItem("数据集格式转换")
        if menu_icon:
            item_conv.setIcon(menu_icon)
        self.menu.addItem(item_conv)
        item_split = QListWidgetItem("数据集划分")
        if menu_icon:
            item_split.setIcon(menu_icon)
        self.menu.addItem(item_split)
        item_analysis = QListWidgetItem("数据集分析")
        if menu_icon:
            item_analysis.setIcon(menu_icon)
        self.menu.addItem(item_analysis)
        item_more = QListWidgetItem("其他功能（待定）")
        if menu_icon:
            item_more.setIcon(menu_icon)
        self.menu.addItem(item_more)
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
        self.content = QWidget()
        content_layout = QVBoxLayout(self.content)
        content_layout.setContentsMargins(16, 16, 16, 16)
        self.converter_panel = ConverterPanel(self)
        self.splitting_panel = SplittingPanel(self)
        self.analysis_panel = AnalysisPanel(self)
        content_layout.addWidget(self.converter_panel)
        outer.addWidget(self.content)

        # 切换逻辑
        self.menu.currentRowChanged.connect(self.on_menu_change)
        self.menu.setCurrentRow(0)

    def on_menu_change(self, idx: int):
        # 清空右侧内容
        for i in range(self.content.layout().count()):
            item = self.content.layout().itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)
        
        if idx == 0:
            self.content.layout().addWidget(self.converter_panel)
        elif idx == 1:
            self.content.layout().addWidget(self.splitting_panel)
        elif idx == 2:
            self.content.layout().addWidget(self.analysis_panel)
        else:
            placeholder = QWidget()
            ph_layout = QVBoxLayout(placeholder)
            from PyQt5.QtWidgets import QLabel
            ph_layout.addWidget(QLabel("功能暂未实现，敬请期待"))
            self.content.layout().addWidget(placeholder)
