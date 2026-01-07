"""
统一的GUI样式管理器
"""

class AppStyles:
    """应用程序样式定义"""
    
    # 颜色定义
    PRIMARY_COLOR = "#2196F3"      # 主色调 - 蓝色
    SUCCESS_COLOR = "#4CAF50"      # 成功色 - 绿色
    WARNING_COLOR = "#FF9800"      # 警告色 - 橙色
    DANGER_COLOR = "#F44336"       # 危险色 - 红色
    BACKGROUND_COLOR = "#F5F5F5"   # 背景色 - 浅灰
    CARD_COLOR = "#FFFFFF"         # 卡片色 - 白色
    TEXT_COLOR = "#212121"         # 文本色 - 深灰
    SECONDARY_TEXT = "#757575"     # 次要文本 - 中灰
    BORDER_COLOR = "#E0E0E0"       # 边框色 - 浅灰
    
    @staticmethod
    def get_main_window_style():
        """主窗口样式"""
        return f"""
        QMainWindow {{
            background-color: {AppStyles.BACKGROUND_COLOR};
        }}
        
        QListWidget {{
            background-color: {AppStyles.CARD_COLOR};
            border: 1px solid {AppStyles.BORDER_COLOR};
            border-radius: 8px;
            padding: 8px;
            font-size: 14px;
        }}
        
        QListWidget::item {{
            height: 45px;
            padding: 8px 12px;
            border-radius: 6px;
            margin: 2px 0px;
        }}
        
        QListWidget::item:selected {{
            background-color: {AppStyles.PRIMARY_COLOR};
            color: white;
        }}
        
        QListWidget::item:hover {{
            background-color: #E3F2FD;
        }}
        
        QFrame {{
            border: 1px solid {AppStyles.BORDER_COLOR};
        }}
        """
    
    @staticmethod
    def get_panel_style():
        """面板通用样式"""
        return f"""
        QWidget {{
            background-color: {AppStyles.BACKGROUND_COLOR};
            color: {AppStyles.TEXT_COLOR};
            font-family: "Microsoft YaHei", "Segoe UI", Arial, sans-serif;
            font-size: 12px;
        }}
        
        QGroupBox {{
            background-color: {AppStyles.CARD_COLOR};
            border: 2px solid {AppStyles.BORDER_COLOR};
            border-radius: 10px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
            font-size: 13px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 8px 0 8px;
            color: {AppStyles.PRIMARY_COLOR};
        }}
        
        QScrollArea {{
            border: none;
            background-color: transparent;
        }}
        
        QScrollBar:vertical {{
            background-color: {AppStyles.BACKGROUND_COLOR};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {AppStyles.BORDER_COLOR};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {AppStyles.SECONDARY_TEXT};
        }}
        """
    
    @staticmethod
    def get_button_style(button_type="default"):
        """按钮样式"""
        styles = {
            "default": f"""
                QPushButton {{
                    background-color: {AppStyles.CARD_COLOR};
                    border: 2px solid {AppStyles.BORDER_COLOR};
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-size: 12px;
                    font-weight: 500;
                    color: {AppStyles.TEXT_COLOR};
                }}
                
                QPushButton:hover {{
                    background-color: #E3F2FD;
                    border-color: {AppStyles.PRIMARY_COLOR};
                }}
                
                QPushButton:pressed {{
                    background-color: {AppStyles.PRIMARY_COLOR};
                    color: white;
                }}
            """,
            
            "primary": f"""
                QPushButton {{
                    background-color: {AppStyles.PRIMARY_COLOR};
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-size: 13px;
                    font-weight: bold;
                    color: white;
                }}
                
                QPushButton:hover {{
                    background-color: #1976D2;
                }}
                
                QPushButton:pressed {{
                    background-color: #0D47A1;
                }}
            """,
            
            "success": f"""
                QPushButton {{
                    background-color: {AppStyles.SUCCESS_COLOR};
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-size: 13px;
                    font-weight: bold;
                    color: white;
                }}
                
                QPushButton:hover {{
                    background-color: #388E3C;
                }}
                
                QPushButton:pressed {{
                    background-color: #1B5E20;
                }}
            """,
            
            "warning": f"""
                QPushButton {{
                    background-color: {AppStyles.WARNING_COLOR};
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-size: 12px;
                    font-weight: 500;
                    color: white;
                }}
                
                QPushButton:hover {{
                    background-color: #F57C00;
                }}
            """,
            
            "danger": f"""
                QPushButton {{
                    background-color: {AppStyles.DANGER_COLOR};
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-size: 12px;
                    font-weight: 500;
                    color: white;
                }}
                
                QPushButton:hover {{
                    background-color: #D32F2F;
                }}
            """
        }
        
        return styles.get(button_type, styles["default"])
    
    @staticmethod
    def get_label_style(label_type="default"):
        """标签样式"""
        styles = {
            "default": f"""
                QLabel {{
                    color: {AppStyles.TEXT_COLOR};
                    font-size: 12px;
                }}
            """,
            
            "title": f"""
                QLabel {{
                    color: {AppStyles.PRIMARY_COLOR};
                    font-size: 14px;
                    font-weight: bold;
                    padding: 5px;
                }}
            """,
            
            "subtitle": f"""
                QLabel {{
                    color: {AppStyles.SECONDARY_TEXT};
                    font-size: 11px;
                    font-style: italic;
                }}
            """,
            
            "status": f"""
                QLabel {{
                    background-color: {AppStyles.CARD_COLOR};
                    border: 1px solid {AppStyles.BORDER_COLOR};
                    border-radius: 6px;
                    padding: 6px 10px;
                    font-size: 12px;
                }}
            """
        }
        
        return styles.get(label_type, styles["default"])
    
    @staticmethod
    def get_textedit_style():
        """文本编辑框样式"""
        return f"""
        QTextEdit {{
            background-color: {AppStyles.CARD_COLOR};
            border: 2px solid {AppStyles.BORDER_COLOR};
            border-radius: 8px;
            padding: 8px;
            font-family: "Consolas", "Monaco", monospace;
            font-size: 11px;
            line-height: 1.4;
        }}
        
        QTextEdit:focus {{
            border-color: {AppStyles.PRIMARY_COLOR};
        }}
        """
    
    @staticmethod
    def get_progressbar_style():
        """进度条样式"""
        return f"""
        QProgressBar {{
            background-color: {AppStyles.BACKGROUND_COLOR};
            border: 2px solid {AppStyles.BORDER_COLOR};
            border-radius: 8px;
            text-align: center;
            font-size: 11px;
            font-weight: bold;
        }}
        
        QProgressBar::chunk {{
            background-color: {AppStyles.PRIMARY_COLOR};
            border-radius: 6px;
        }}
        """
    
    @staticmethod
    def get_combobox_style():
        """下拉框样式"""
        return f"""
        QComboBox {{
            background-color: {AppStyles.CARD_COLOR};
            border: 2px solid {AppStyles.BORDER_COLOR};
            border-radius: 6px;
            padding: 6px 10px;
            font-size: 12px;
        }}
        
        QComboBox:hover {{
            border-color: {AppStyles.PRIMARY_COLOR};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {AppStyles.SECONDARY_TEXT};
        }}
        """
    
    @staticmethod
    def get_checkbox_style():
        """复选框样式"""
        return f"""
        QCheckBox {{
            font-size: 12px;
            color: {AppStyles.TEXT_COLOR};
            spacing: 8px;
        }}
        
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 2px solid {AppStyles.BORDER_COLOR};
            border-radius: 3px;
            background-color: {AppStyles.CARD_COLOR};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {AppStyles.PRIMARY_COLOR};
            border-color: {AppStyles.PRIMARY_COLOR};
        }}
        
        QCheckBox::indicator:hover {{
            border-color: {AppStyles.PRIMARY_COLOR};
        }}
        """
    
    @staticmethod
    def get_spinbox_style():
        """数字输入框样式"""
        return f"""
        QSpinBox {{
            background-color: {AppStyles.CARD_COLOR};
            border: 2px solid {AppStyles.BORDER_COLOR};
            border-radius: 6px;
            padding: 6px;
            font-size: 12px;
        }}
        
        QSpinBox:focus {{
            border-color: {AppStyles.PRIMARY_COLOR};
        }}
        """