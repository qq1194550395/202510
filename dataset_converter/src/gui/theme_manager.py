"""
主题管理器
"""
from PyQt5.QtCore import QSettings, pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication
from typing import Dict, Any
import json
from pathlib import Path


class ThemeManager(QObject):
    """主题管理器"""
    
    theme_changed = pyqtSignal(str)  # 主题改变信号
    
    def __init__(self):
        super().__init__()
        self.settings = QSettings("DatasetConverter", "Theme")
        self.current_theme = self.settings.value("current_theme", "light")
        self.themes = self._load_themes()
    
    def _load_themes(self) -> Dict[str, Dict[str, Any]]:
        """加载主题配置"""
        return {
            "light": {
                "name": "浅色主题",
                "colors": {
                    "primary": "#2196F3",
                    "success": "#4CAF50",
                    "warning": "#FF9800",
                    "danger": "#F44336",
                    "background": "#F5F5F5",
                    "card": "#FFFFFF",
                    "text": "#212121",
                    "secondary_text": "#757575",
                    "border": "#E0E0E0",
                    "hover": "#E3F2FD",
                    "selected": "#BBDEFB"
                },
                "fonts": {
                    "family": "SimSun, 宋体, serif",
                    "size_small": 10,
                    "size_normal": 12,
                    "size_large": 14,
                    "size_title": 16
                },
                "spacing": {
                    "small": 4,
                    "normal": 8,
                    "large": 16,
                    "xlarge": 24
                },
                "border_radius": 8,
                "shadow": "0 2px 4px rgba(0,0,0,0.1)"
            },
            
            "dark": {
                "name": "深色主题",
                "colors": {
                    "primary": "#64B5F6",
                    "success": "#81C784",
                    "warning": "#FFB74D",
                    "danger": "#E57373",
                    "background": "#121212",
                    "card": "#1E1E1E",
                    "text": "#FFFFFF",
                    "secondary_text": "#B0B0B0",
                    "border": "#333333",
                    "hover": "#2C2C2C",
                    "selected": "#404040"
                },
                "fonts": {
                    "family": "SimSun, 宋体, serif",
                    "size_small": 10,
                    "size_normal": 12,
                    "size_large": 14,
                    "size_title": 16
                },
                "spacing": {
                    "small": 4,
                    "normal": 8,
                    "large": 16,
                    "xlarge": 24
                },
                "border_radius": 8,
                "shadow": "0 2px 8px rgba(0,0,0,0.3)"
            },
            
            "blue": {
                "name": "蓝色主题",
                "colors": {
                    "primary": "#1976D2",
                    "success": "#388E3C",
                    "warning": "#F57C00",
                    "danger": "#D32F2F",
                    "background": "#E3F2FD",
                    "card": "#FFFFFF",
                    "text": "#0D47A1",
                    "secondary_text": "#1565C0",
                    "border": "#90CAF9",
                    "hover": "#BBDEFB",
                    "selected": "#2196F3"
                },
                "fonts": {
                    "family": "SimSun, 宋体, serif",
                    "size_small": 10,
                    "size_normal": 12,
                    "size_large": 14,
                    "size_title": 16
                },
                "spacing": {
                    "small": 4,
                    "normal": 8,
                    "large": 16,
                    "xlarge": 24
                },
                "border_radius": 10,
                "shadow": "0 2px 6px rgba(25,118,210,0.2)"
            },
            
            "green": {
                "name": "绿色主题",
                "colors": {
                    "primary": "#388E3C",
                    "success": "#4CAF50",
                    "warning": "#FF9800",
                    "danger": "#F44336",
                    "background": "#E8F5E8",
                    "card": "#FFFFFF",
                    "text": "#1B5E20",
                    "secondary_text": "#2E7D32",
                    "border": "#A5D6A7",
                    "hover": "#C8E6C9",
                    "selected": "#4CAF50"
                },
                "fonts": {
                    "family": "SimSun, 宋体, serif",
                    "size_small": 10,
                    "size_normal": 12,
                    "size_large": 14,
                    "size_title": 16
                },
                "spacing": {
                    "small": 4,
                    "normal": 8,
                    "large": 16,
                    "xlarge": 24
                },
                "border_radius": 8,
                "shadow": "0 2px 6px rgba(56,142,60,0.2)"
            }
        }
    
    def get_current_theme(self) -> str:
        """获取当前主题名称"""
        return self.current_theme
    
    def get_theme_config(self, theme_name: str = None) -> Dict[str, Any]:
        """获取主题配置"""
        if theme_name is None:
            theme_name = self.current_theme
        return self.themes.get(theme_name, self.themes["light"])
    
    def set_theme(self, theme_name: str):
        """设置主题"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            self.settings.setValue("current_theme", theme_name)
            self.theme_changed.emit(theme_name)
    
    def get_available_themes(self) -> Dict[str, str]:
        """获取可用主题列表"""
        return {name: config["name"] for name, config in self.themes.items()}
    
    def generate_stylesheet(self, theme_name: str = None) -> str:
        """生成完整的样式表"""
        config = self.get_theme_config(theme_name)
        colors = config["colors"]
        fonts = config["fonts"]
        spacing = config["spacing"]
        
        return f"""
        /* 全局样式 */
        QWidget {{
            background-color: {colors['background']};
            color: {colors['text']};
            font-family: {fonts['family']};
            font-size: {fonts['size_normal']}px;
        }}
        
        /* 主窗口 */
        QMainWindow {{
            background-color: {colors['background']};
        }}
        
        /* 按钮样式 */
        QPushButton {{
            background-color: {colors['card']};
            border: 2px solid {colors['border']};
            border-radius: {config['border_radius']}px;
            padding: {spacing['normal']}px {spacing['large']}px;
            font-size: {fonts['size_normal']}px;
            font-weight: 500;
            color: {colors['text']};
            min-height: 20px;
        }}
        
        QPushButton:hover {{
            background-color: {colors['hover']};
            border-color: {colors['primary']};
        }}
        
        QPushButton:pressed {{
            background-color: {colors['primary']};
            color: white;
        }}
        
        QPushButton:disabled {{
            background-color: {colors['border']};
            color: {colors['secondary_text']};
            border-color: {colors['border']};
        }}
        
        /* 主要按钮 */
        QPushButton[buttonType="primary"] {{
            background-color: {colors['primary']};
            border: none;
            color: white;
            font-weight: bold;
        }}
        
        QPushButton[buttonType="primary"]:hover {{
            background-color: {colors['selected']};
        }}
        
        /* 成功按钮 */
        QPushButton[buttonType="success"] {{
            background-color: {colors['success']};
            border: none;
            color: white;
            font-weight: bold;
        }}
        
        /* 警告按钮 */
        QPushButton[buttonType="warning"] {{
            background-color: {colors['warning']};
            border: none;
            color: white;
        }}
        
        /* 危险按钮 */
        QPushButton[buttonType="danger"] {{
            background-color: {colors['danger']};
            border: none;
            color: white;
        }}
        
        /* 标签样式 */
        QLabel {{
            color: {colors['text']};
            font-size: {fonts['size_normal']}px;
        }}
        
        QLabel[labelType="title"] {{
            color: {colors['primary']};
            font-size: {fonts['size_title']}px;
            font-weight: bold;
            padding: {spacing['small']}px;
        }}
        
        QLabel[labelType="subtitle"] {{
            color: {colors['secondary_text']};
            font-size: {fonts['size_small']}px;
            font-style: italic;
        }}
        
        QLabel[labelType="status"] {{
            background-color: {colors['card']};
            border: 1px solid {colors['border']};
            border-radius: {config['border_radius'] // 2}px;
            padding: {spacing['small']}px {spacing['normal']}px;
        }}
        
        /* 组框样式 */
        QGroupBox {{
            background-color: {colors['card']};
            border: 2px solid {colors['border']};
            border-radius: {config['border_radius']}px;
            margin-top: {spacing['normal']}px;
            padding-top: {spacing['normal']}px;
            font-weight: bold;
            font-size: {fonts['size_large']}px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: {spacing['large']}px;
            padding: 0 {spacing['normal']}px 0 {spacing['normal']}px;
            color: {colors['primary']};
        }}
        
        /* 列表控件 */
        QListWidget {{
            background-color: {colors['card']};
            border: 1px solid {colors['border']};
            border-radius: {config['border_radius']}px;
            padding: {spacing['normal']}px;
            font-size: {fonts['size_normal']}px;
        }}
        
        QListWidget::item {{
            height: 45px;
            padding: {spacing['normal']}px {spacing['large']}px;
            border-radius: {config['border_radius'] // 2}px;
            margin: 2px 0px;
        }}
        
        QListWidget::item:selected {{
            background-color: {colors['primary']};
            color: white;
        }}
        
        QListWidget::item:hover {{
            background-color: {colors['hover']};
        }}
        
        /* 文本编辑框 */
        QTextEdit {{
            background-color: {colors['card']};
            border: 2px solid {colors['border']};
            border-radius: {config['border_radius']}px;
            padding: {spacing['normal']}px;
            font-family: "Consolas", "Monaco", monospace;
            font-size: {fonts['size_small']}px;
            line-height: 1.4;
        }}
        
        QTextEdit:focus {{
            border-color: {colors['primary']};
        }}
        
        QLineEdit {{
            background-color: {colors['card']};
            border: 2px solid {colors['border']};
            border-radius: {config['border_radius'] // 2}px;
            padding: {spacing['small']}px {spacing['normal']}px;
            font-size: {fonts['size_normal']}px;
        }}
        
        QLineEdit:focus {{
            border-color: {colors['primary']};
        }}
        
        /* 下拉框 */
        QComboBox {{
            background-color: {colors['card']};
            border: 2px solid {colors['border']};
            border-radius: {config['border_radius'] // 2}px;
            padding: {spacing['small']}px {spacing['normal']}px;
            font-size: {fonts['size_normal']}px;
        }}
        
        QComboBox:hover {{
            border-color: {colors['primary']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {colors['secondary_text']};
        }}
        
        /* 复选框 */
        QCheckBox {{
            font-size: {fonts['size_normal']}px;
            color: {colors['text']};
            spacing: {spacing['normal']}px;
        }}
        
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 2px solid {colors['border']};
            border-radius: 3px;
            background-color: {colors['card']};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {colors['primary']};
            border-color: {colors['primary']};
        }}
        
        QCheckBox::indicator:hover {{
            border-color: {colors['primary']};
        }}
        
        /* 数字输入框 */
        QSpinBox {{
            background-color: {colors['card']};
            border: 2px solid {colors['border']};
            border-radius: {config['border_radius'] // 2}px;
            padding: {spacing['small']}px;
            font-size: {fonts['size_normal']}px;
        }}
        
        QSpinBox:focus {{
            border-color: {colors['primary']};
        }}
        
        /* 进度条 */
        QProgressBar {{
            background-color: {colors['background']};
            border: 2px solid {colors['border']};
            border-radius: {config['border_radius']}px;
            text-align: center;
            font-size: {fonts['size_small']}px;
            font-weight: bold;
        }}
        
        QProgressBar::chunk {{
            background-color: {colors['primary']};
            border-radius: {config['border_radius'] - 2}px;
        }}
        
        /* 滚动条 */
        QScrollBar:vertical {{
            background-color: {colors['background']};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {colors['border']};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {colors['secondary_text']};
        }}
        
        QScrollBar:horizontal {{
            background-color: {colors['background']};
            height: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {colors['border']};
            border-radius: 6px;
            min-width: 20px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {colors['secondary_text']};
        }}
        
        /* 菜单栏 */
        QMenuBar {{
            background-color: {colors['card']};
            border-bottom: 1px solid {colors['border']};
        }}
        
        QMenuBar::item {{
            background-color: transparent;
            padding: {spacing['normal']}px {spacing['large']}px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {colors['hover']};
        }}
        
        /* 工具栏 */
        QToolBar {{
            background-color: {colors['card']};
            border: 1px solid {colors['border']};
            spacing: {spacing['small']}px;
        }}
        
        /* 状态栏 */
        QStatusBar {{
            background-color: {colors['card']};
            border-top: 1px solid {colors['border']};
        }}
        
        /* 分隔符 */
        QFrame[frameShape="4"] {{
            background-color: {colors['border']};
            max-width: 1px;
        }}
        
        QFrame[frameShape="5"] {{
            background-color: {colors['border']};
            max-height: 1px;
        }}
        """


# 全局主题管理器实例
theme_manager = ThemeManager()