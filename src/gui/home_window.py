from pathlib import Path
import sys

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QFrame

# 复用内部实现的面板组件（dataset_converter/src/gui/*.py）
internal_root = Path(__file__).parents[2] / "dataset_converter"
if str(internal_root) not in sys.path:
    sys.path.append(str(internal_root))
from src.gui.converter_panel import ConverterPanel
from src.gui.splitting_panel import SplittingPanel


class HomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("图片处理软件v1.0")
        icon_path = Path(__file__).parent.parent.parent / "resources" / "icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # 固定窗口尺寸，避免过小
        self.setFixedSize(1024, 700)

        central = QWidget(self)
        self.setCentralWidget(central)

        outer = QHBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # 左侧功能列表
        self.menu = QListWidget()
        self.menu.setFixedWidth(260)
        self.menu.setIconSize(QSize(24, 24))
        self.menu.setAlternatingRowColors(True)
        self.menu.setStyleSheet(
            "QListWidget{background:#f7f8fa;border:0;padding:6px;}"
            "QListWidget::item{height:40px;padding:6px 10px;}"
            "QListWidget::item:selected{background:#e8f0fe;color:#1a73e8;}"
        )
        menu_icon = QIcon(str(icon_path)) if icon_path.exists() else None
        item_conv = QListWidgetItem("数据集格式转换")
        if menu_icon:
            item_conv.setIcon(menu_icon)
        self.menu.addItem(item_conv)
        item_split = QListWidgetItem("数据集划分")
        if menu_icon:
            item_split.setIcon(menu_icon)
        self.menu.addItem(item_split)
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
        self.content = QWidget()
        content_layout = QVBoxLayout(self.content)
        content_layout.setContentsMargins(16, 16, 16, 16)
        self.converter_panel = ConverterPanel(self)
        self.splitting_panel = SplittingPanel(self)
        content_layout.addWidget(self.converter_panel)
        outer.addWidget(self.content)

        # 切换逻辑
        self.menu.currentRowChanged.connect(self.on_menu_change)
        self.menu.setCurrentRow(0)

    def on_menu_change(self, idx: int):
        # 简单切换：只有第一个功能已实现，其它显示占位
        # 清空右侧内容
        for i in range(self.content.layout().count()):
            item = self.content.layout().itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)
        if idx == 0:
            self.content.layout().addWidget(self.converter_panel)
        elif idx == 1:
            self.content.layout().addWidget(self.splitting_panel)
        else:
            placeholder = QWidget()
            ph_layout = QVBoxLayout(placeholder)
            from PyQt5.QtWidgets import QLabel
            ph_layout.addWidget(QLabel("功能暂未实现，敬请期待"))
            self.content.layout().addWidget(placeholder)