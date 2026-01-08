"""
设置面板
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QComboBox, QGroupBox, QCheckBox, QSpinBox, QSlider,
    QColorDialog, QFontDialog, QMessageBox, QTabWidget,
    QGridLayout, QLineEdit, QTextEdit, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette

from .theme_manager import theme_manager
from .styles import AppStyles


class SettingsPanel(QWidget):
    """设置面板"""
    
    settings_changed = pyqtSignal()  # 设置改变信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.connect_signals()
        self.load_settings()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 创建标签页
        tab_widget = QTabWidget()
        
        # 主题设置标签页
        theme_tab = self.create_theme_tab()
        tab_widget.addTab(theme_tab, "主题设置")
        
        # 界面设置标签页
        ui_tab = self.create_ui_tab()
        tab_widget.addTab(ui_tab, "界面设置")
        
        # 快捷键设置标签页
        shortcuts_tab = self.create_shortcuts_tab()
        tab_widget.addTab(shortcuts_tab, "快捷键")
        
        # 高级设置标签页
        advanced_tab = self.create_advanced_tab()
        tab_widget.addTab(advanced_tab, "高级设置")
        
        layout.addWidget(tab_widget)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        
        self.apply_btn = QPushButton("应用设置")
        self.apply_btn.clicked.connect(self.apply_settings)
        
        self.reset_btn = QPushButton("恢复默认")
        self.reset_btn.clicked.connect(self.reset_settings)
        
        self.preview_btn = QPushButton("预览主题")
        self.preview_btn.clicked.connect(self.preview_theme)
        
        button_layout.addStretch()
        button_layout.addWidget(self.preview_btn)
        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(self.apply_btn)
        
        layout.addLayout(button_layout)
    
    def create_theme_tab(self) -> QWidget:
        """创建主题设置标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 主题选择组
        theme_group = QGroupBox("主题选择")
        theme_layout = QGridLayout(theme_group)
        
        theme_layout.addWidget(QLabel("当前主题:"), 0, 0)
        self.theme_combo = QComboBox()
        themes = theme_manager.get_available_themes()
        for theme_id, theme_name in themes.items():
            self.theme_combo.addItem(theme_name, theme_id)
        theme_layout.addWidget(self.theme_combo, 0, 1)
        
        # 主题预览
        self.theme_preview = QLabel("主题预览")
        self.theme_preview.setMinimumHeight(100)
        self.theme_preview.setStyleSheet("""
            QLabel {
                border: 2px solid #ccc;
                border-radius: 8px;
                background-color: #f0f0f0;
                padding: 20px;
                text-align: center;
            }
        """)
        theme_layout.addWidget(self.theme_preview, 1, 0, 1, 2)
        
        layout.addWidget(theme_group)
        
        # 自定义颜色组
        color_group = QGroupBox("自定义颜色")
        color_layout = QGridLayout(color_group)
        
        self.color_buttons = {}
        color_names = [
            ("primary", "主色调"),
            ("success", "成功色"),
            ("warning", "警告色"),
            ("danger", "危险色"),
            ("background", "背景色"),
            ("card", "卡片色")
        ]
        
        for i, (color_key, color_name) in enumerate(color_names):
            row = i // 2
            col = (i % 2) * 2
            
            color_layout.addWidget(QLabel(f"{color_name}:"), row, col)
            
            color_btn = QPushButton()
            color_btn.setFixedSize(50, 30)
            color_btn.clicked.connect(lambda checked, key=color_key: self.choose_color(key))
            self.color_buttons[color_key] = color_btn
            color_layout.addWidget(color_btn, row, col + 1)
        
        layout.addWidget(color_group)
        
        # 字体设置组
        font_group = QGroupBox("字体设置")
        font_layout = QGridLayout(font_group)
        
        font_layout.addWidget(QLabel("字体族:"), 0, 0)
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems([
            "SimSun, 宋体, serif",
            "Microsoft YaHei, 微软雅黑, sans-serif",
            "SimHei, 黑体, sans-serif",
            "KaiTi, 楷体, serif",
            "FangSong, 仿宋, serif"
        ])
        font_layout.addWidget(self.font_family_combo, 0, 1)
        
        font_layout.addWidget(QLabel("字体大小:"), 1, 0)
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(12)
        font_layout.addWidget(self.font_size_spin, 1, 1)
        
        layout.addWidget(font_group)
        
        layout.addStretch()
        return tab
    
    def create_ui_tab(self) -> QWidget:
        """创建界面设置标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 窗口设置组
        window_group = QGroupBox("窗口设置")
        window_layout = QGridLayout(window_group)
        
        window_layout.addWidget(QLabel("窗口透明度:"), 0, 0)
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(70, 100)
        self.opacity_slider.setValue(100)
        self.opacity_label = QLabel("100%")
        self.opacity_slider.valueChanged.connect(
            lambda v: self.opacity_label.setText(f"{v}%")
        )
        window_layout.addWidget(self.opacity_slider, 0, 1)
        window_layout.addWidget(self.opacity_label, 0, 2)
        
        window_layout.addWidget(QLabel("启动时最大化:"), 1, 0)
        self.maximize_check = QCheckBox()
        window_layout.addWidget(self.maximize_check, 1, 1)
        
        window_layout.addWidget(QLabel("记住窗口位置:"), 2, 0)
        self.remember_position_check = QCheckBox()
        window_layout.addWidget(self.remember_position_check, 2, 1)
        
        layout.addWidget(window_group)
        
        # 界面元素设置组
        ui_group = QGroupBox("界面元素")
        ui_layout = QGridLayout(ui_group)
        
        ui_layout.addWidget(QLabel("显示工具栏:"), 0, 0)
        self.toolbar_check = QCheckBox()
        self.toolbar_check.setChecked(True)
        ui_layout.addWidget(self.toolbar_check, 0, 1)
        
        ui_layout.addWidget(QLabel("显示状态栏:"), 1, 0)
        self.statusbar_check = QCheckBox()
        self.statusbar_check.setChecked(True)
        ui_layout.addWidget(self.statusbar_check, 1, 1)
        
        ui_layout.addWidget(QLabel("显示侧边栏:"), 2, 0)
        self.sidebar_check = QCheckBox()
        self.sidebar_check.setChecked(True)
        ui_layout.addWidget(self.sidebar_check, 2, 1)
        
        ui_layout.addWidget(QLabel("动画效果:"), 3, 0)
        self.animation_check = QCheckBox()
        self.animation_check.setChecked(True)
        ui_layout.addWidget(self.animation_check, 3, 1)
        
        layout.addWidget(ui_group)
        
        # 日志设置组
        log_group = QGroupBox("日志设置")
        log_layout = QGridLayout(log_group)
        
        log_layout.addWidget(QLabel("日志级别:"), 0, 0)
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level_combo.setCurrentText("INFO")
        log_layout.addWidget(self.log_level_combo, 0, 1)
        
        log_layout.addWidget(QLabel("最大日志行数:"), 1, 0)
        self.max_log_lines_spin = QSpinBox()
        self.max_log_lines_spin.setRange(100, 10000)
        self.max_log_lines_spin.setValue(1000)
        log_layout.addWidget(self.max_log_lines_spin, 1, 1)
        
        layout.addWidget(log_group)
        
        layout.addStretch()
        return tab
    
    def create_shortcuts_tab(self) -> QWidget:
        """创建快捷键设置标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        shortcuts_group = QGroupBox("快捷键设置")
        shortcuts_layout = QGridLayout(shortcuts_group)
        
        # 快捷键列表
        shortcuts = [
            ("新建项目", "Ctrl+N"),
            ("打开项目", "Ctrl+O"),
            ("保存", "Ctrl+S"),
            ("退出", "Ctrl+Q"),
            ("转换", "F5"),
            ("分析", "F6"),
            ("设置", "F12"),
            ("全屏", "F11"),
            ("帮助", "F1")
        ]
        
        self.shortcut_edits = {}
        
        for i, (action, shortcut) in enumerate(shortcuts):
            shortcuts_layout.addWidget(QLabel(f"{action}:"), i, 0)
            
            shortcut_edit = QLineEdit(shortcut)
            shortcut_edit.setReadOnly(True)  # 暂时只读，后续可以实现编辑功能
            self.shortcut_edits[action] = shortcut_edit
            shortcuts_layout.addWidget(shortcut_edit, i, 1)
            
            reset_btn = QPushButton("重置")
            reset_btn.clicked.connect(lambda checked, a=action, s=shortcut: 
                                    self.shortcut_edits[a].setText(s))
            shortcuts_layout.addWidget(reset_btn, i, 2)
        
        layout.addWidget(shortcuts_group)
        
        # 说明文本
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(100)
        info_text.setText("""
快捷键说明：
• Ctrl+N: 新建项目
• Ctrl+O: 打开项目
• F5: 开始转换
• F6: 数据分析
• F11: 全屏模式
• F12: 打开设置
        """)
        layout.addWidget(info_text)
        
        layout.addStretch()
        return tab
    
    def create_advanced_tab(self) -> QWidget:
        """创建高级设置标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 性能设置组
        performance_group = QGroupBox("性能设置")
        performance_layout = QGridLayout(performance_group)
        
        performance_layout.addWidget(QLabel("多线程处理:"), 0, 0)
        self.multithread_check = QCheckBox()
        self.multithread_check.setChecked(True)
        performance_layout.addWidget(self.multithread_check, 0, 1)
        
        performance_layout.addWidget(QLabel("线程数量:"), 1, 0)
        self.thread_count_spin = QSpinBox()
        self.thread_count_spin.setRange(1, 16)
        self.thread_count_spin.setValue(4)
        performance_layout.addWidget(self.thread_count_spin, 1, 1)
        
        performance_layout.addWidget(QLabel("内存缓存大小(MB):"), 2, 0)
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(64, 2048)
        self.cache_size_spin.setValue(256)
        performance_layout.addWidget(self.cache_size_spin, 2, 1)
        
        layout.addWidget(performance_group)
        
        # 数据处理设置组
        data_group = QGroupBox("数据处理设置")
        data_layout = QGridLayout(data_group)
        
        data_layout.addWidget(QLabel("自动备份:"), 0, 0)
        self.auto_backup_check = QCheckBox()
        self.auto_backup_check.setChecked(True)
        data_layout.addWidget(self.auto_backup_check, 0, 1)
        
        data_layout.addWidget(QLabel("备份间隔(分钟):"), 1, 0)
        self.backup_interval_spin = QSpinBox()
        self.backup_interval_spin.setRange(5, 120)
        self.backup_interval_spin.setValue(30)
        data_layout.addWidget(self.backup_interval_spin, 1, 1)
        
        data_layout.addWidget(QLabel("验证数据完整性:"), 2, 0)
        self.validate_data_check = QCheckBox()
        self.validate_data_check.setChecked(True)
        data_layout.addWidget(self.validate_data_check, 2, 1)
        
        layout.addWidget(data_group)
        
        # 实验性功能组
        experimental_group = QGroupBox("实验性功能")
        experimental_layout = QGridLayout(experimental_group)
        
        experimental_layout.addWidget(QLabel("启用GPU加速:"), 0, 0)
        self.gpu_acceleration_check = QCheckBox()
        experimental_layout.addWidget(self.gpu_acceleration_check, 0, 1)
        
        experimental_layout.addWidget(QLabel("启用AI辅助:"), 1, 0)
        self.ai_assist_check = QCheckBox()
        experimental_layout.addWidget(self.ai_assist_check, 1, 1)
        
        experimental_layout.addWidget(QLabel("云端同步:"), 2, 0)
        self.cloud_sync_check = QCheckBox()
        experimental_layout.addWidget(self.cloud_sync_check, 2, 1)
        
        layout.addWidget(experimental_group)
        
        layout.addStretch()
        return tab
    
    def connect_signals(self):
        """连接信号"""
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        theme_manager.theme_changed.connect(self.update_theme_preview)
    
    def load_settings(self):
        """加载设置"""
        # 设置当前主题
        current_theme = theme_manager.get_current_theme()
        for i in range(self.theme_combo.count()):
            if self.theme_combo.itemData(i) == current_theme:
                self.theme_combo.setCurrentIndex(i)
                break
        
        # 更新主题预览
        self.update_theme_preview(current_theme)
        
        # 更新颜色按钮
        self.update_color_buttons()
    
    def on_theme_changed(self):
        """主题改变时的处理"""
        theme_id = self.theme_combo.currentData()
        if theme_id:
            self.update_theme_preview(theme_id)
            self.update_color_buttons()
    
    def update_theme_preview(self, theme_name: str):
        """更新主题预览"""
        config = theme_manager.get_theme_config(theme_name)
        colors = config["colors"]
        
        preview_style = f"""
        QLabel {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {colors['background']}, stop:1 {colors['card']});
            border: 2px solid {colors['primary']};
            border-radius: 8px;
            color: {colors['text']};
            font-weight: bold;
        }}
        """
        
        self.theme_preview.setStyleSheet(preview_style)
        self.theme_preview.setText(f"主题预览 - {config['name']}")
    
    def update_color_buttons(self):
        """更新颜色按钮"""
        theme_id = self.theme_combo.currentData()
        if not theme_id:
            return
        
        config = theme_manager.get_theme_config(theme_id)
        colors = config["colors"]
        
        for color_key, button in self.color_buttons.items():
            if color_key in colors:
                color = colors[color_key]
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {color};
                        border: 2px solid #333;
                        border-radius: 4px;
                    }}
                """)
    
    def choose_color(self, color_key: str):
        """选择颜色"""
        color = QColorDialog.getColor()
        if color.isValid():
            button = self.color_buttons[color_key]
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color.name()};
                    border: 2px solid #333;
                    border-radius: 4px;
                }}
            """)
    
    def apply_settings(self):
        """应用设置"""
        # 应用主题
        theme_id = self.theme_combo.currentData()
        if theme_id:
            theme_manager.set_theme(theme_id)
        
        # 应用窗口透明度
        if hasattr(self.parent(), 'setWindowOpacity'):
            opacity = self.opacity_slider.value() / 100.0
            self.parent().setWindowOpacity(opacity)
        
        self.settings_changed.emit()
        QMessageBox.information(self, "设置", "设置已应用！")
    
    def reset_settings(self):
        """重置设置"""
        reply = QMessageBox.question(self, "确认", "确定要恢复默认设置吗？",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            # 重置主题
            self.theme_combo.setCurrentIndex(0)
            
            # 重置其他设置
            self.opacity_slider.setValue(100)
            self.maximize_check.setChecked(False)
            self.remember_position_check.setChecked(False)
            self.font_size_spin.setValue(12)
            
            QMessageBox.information(self, "设置", "已恢复默认设置！")
    
    def preview_theme(self):
        """预览主题"""
        theme_id = self.theme_combo.currentData()
        if theme_id:
            # 临时应用主题进行预览
            stylesheet = theme_manager.generate_stylesheet(theme_id)
            self.parent().setStyleSheet(stylesheet)
            
            QMessageBox.information(self, "预览", f"正在预览主题: {self.theme_combo.currentText()}")
    
    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet(AppStyles.get_panel_style())
        
        # 为按钮应用样式
        self.apply_btn.setStyleSheet(AppStyles.get_button_style("success"))
        self.reset_btn.setStyleSheet(AppStyles.get_button_style("warning"))
        self.preview_btn.setStyleSheet(AppStyles.get_button_style("primary"))