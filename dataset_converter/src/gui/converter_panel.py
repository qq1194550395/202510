from pathlib import Path

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QTextEdit,
    QFileDialog,
    QMessageBox,
    QScrollArea,
    QGroupBox,
    QGridLayout,
)

from ..core.converter import convert
from ..utils.logger import get_logger
from ..utils.label_utils import parse_label_map_txt


class ConverterPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger()

        main_layout = QVBoxLayout(self)

        # 输入输出路径 - 固定在顶部
        path_group = QWidget()
        path_layout = QVBoxLayout(path_group)
        
        # 输入目录
        input_layout = QHBoxLayout()
        self.input_label = QLabel("输入目录: 未选择")
        self.input_label.setWordWrap(True)
        btn_in = QPushButton("选择输入目录")
        btn_in.setMaximumWidth(120)
        input_layout.addWidget(self.input_label, 1)
        input_layout.addWidget(btn_in)
        
        # 输出目录
        output_layout = QHBoxLayout()
        self.output_label = QLabel("输出目录: 未选择")
        self.output_label.setWordWrap(True)
        btn_out = QPushButton("选择输出目录")
        btn_out.setMaximumWidth(120)
        output_layout.addWidget(self.output_label, 1)
        output_layout.addWidget(btn_out)
        
        btn_in.clicked.connect(self.choose_input)
        btn_out.clicked.connect(self.choose_output)
        
        path_layout.addLayout(input_layout)
        path_layout.addLayout(output_layout)
        main_layout.addWidget(path_group)

        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(2)  # 总是显示垂直滚动条
        scroll_area.setHorizontalScrollBarPolicy(1)  # 根据需要显示水平滚动条
        
        # 创建滚动内容容器
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # 当前格式显示
        self.label_fmt = QLabel("当前格式: YOLO检测 → VOC")
        self.label_fmt.setWordWrap(True)
        scroll_layout.addWidget(self.label_fmt)
        
        # 基础格式转换组
        basic_group = self.create_conversion_group("基础格式转换", [
            ("YOLO检测 → VOC", "yolo", "voc"),
            ("VOC → YOLO检测", "voc", "yolo"),
            ("YOLO检测 → JSON", "yolo", "json"),
            ("JSON → YOLO检测", "json", "yolo"),
            ("JSON → VOC", "json", "voc"),
        ])
        scroll_layout.addWidget(basic_group)
        
        # 分割格式转换组
        seg_group = self.create_conversion_group("分割格式转换", [
            ("YOLO分割 → JSON", "yolo_seg", "json"),
            ("JSON → YOLO分割", "json", "yolo_seg"),
            ("YOLO分割 → YOLO检测", "yolo_seg", "yolo"),
        ])
        scroll_layout.addWidget(seg_group)

        # 工具按钮组
        tools_group = self.create_tools_group()
        scroll_layout.addWidget(tools_group)
        
        # 设置滚动内容
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # 日志输出 - 固定在底部
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMaximumHeight(150)  # 限制高度
        
        log_label = QLabel("日志输出:")
        main_layout.addWidget(log_label)
        main_layout.addWidget(self.log_view)

        self.input_dir = None
        self.output_dir = None
        self.input_fmt = "yolo"
        self.output_fmt = "voc"
        self.label_map = {}
    
    def create_conversion_group(self, title, conversions):
        """创建转换按钮组"""
        group = QGroupBox(title)
        layout = QGridLayout(group)
        
        # 每行最多2个按钮，防止超出窗口
        for i, (text, inp_fmt, out_fmt) in enumerate(conversions):
            btn = QPushButton(text)
            btn.setMaximumWidth(200)  # 限制按钮宽度
            btn.clicked.connect(lambda checked, i=inp_fmt, o=out_fmt: self.set_formats(i, o))
            
            row = i // 2
            col = i % 2
            layout.addWidget(btn, row, col)
        
        return group
    
    def create_tools_group(self):
        """创建工具按钮组"""
        group = QGroupBox("工具")
        layout = QVBoxLayout(group)
        
        # 标签字典按钮
        btn_label_map = QPushButton("加载标签字典")
        btn_label_map.setMaximumWidth(200)
        btn_label_map.setProperty("buttonType", "warning")
        btn_label_map.clicked.connect(self.on_load_label_map)
        layout.addWidget(btn_label_map)
        
        # 转换按钮
        btn_convert = QPushButton("开始转换")
        btn_convert.setMaximumWidth(200)
        btn_convert.setProperty("buttonType", "success")
        btn_convert.clicked.connect(self.on_convert)
        layout.addWidget(btn_convert)
        
        return group

    def choose_input(self):
        d = QFileDialog.getExistingDirectory(self, "选择输入目录", str(Path.cwd()))
        if d:
            self.input_dir = Path(d)
            self.input_label.setText(f"输入目录: {d}")

    def choose_output(self):
        d = QFileDialog.getExistingDirectory(self, "选择输出目录", str(Path.cwd()))
        if d:
            self.output_dir = Path(d)
            self.output_label.setText(f"输出目录: {d}")

    def set_formats(self, inp: str, outp: str):
        self.input_fmt = inp
        self.output_fmt = outp
        
        # 格式名称映射
        format_names = {
            "yolo": "YOLO检测",
            "yolo_seg": "YOLO分割", 
            "voc": "VOC",
            "json": "JSON"
        }
        
        inp_name = format_names.get(inp, inp.upper())
        outp_name = format_names.get(outp, outp.upper())
        self.label_fmt.setText(f"当前格式: {inp_name} → {outp_name}")

    def append_log(self, msg: str):
        self.log_view.append(msg)
        self.logger.info(msg)

    def on_convert(self):
        if not self.input_dir or not self.output_dir:
            QMessageBox.warning(self, "提示", "请先选择输入与输出目录")
            return
        try:
            format_names = {
                "yolo": "YOLO检测",
                "yolo_seg": "YOLO分割", 
                "voc": "VOC",
                "json": "JSON"
            }
            inp_name = format_names.get(self.input_fmt, self.input_fmt)
            outp_name = format_names.get(self.output_fmt, self.output_fmt)
            
            self.append_log(f"开始转换: {inp_name} → {outp_name}")
            if self.output_fmt == "json":
                self.append_log("导出说明：将为每张图片生成一个独立的 JSON 文件，命名为 <stem>.json")
            elif self.input_fmt == "yolo_seg":
                self.append_log("输入说明：YOLO分割格式支持矩形框(5个值)和多边形(>5个值)混合标注")
            elif self.output_fmt == "yolo_seg":
                self.append_log("输出说明：YOLO分割格式将保留原有的矩形框和多边形标注")
                
            convert(self.input_dir, self.input_fmt, self.output_dir, self.output_fmt, label_map=self.label_map)
            self.append_log("转换完成")
            QMessageBox.information(self, "完成", "转换完成！")
        except Exception as e:
            self.append_log(f"发生错误: {e}")
            QMessageBox.critical(self, "错误", str(e))

    def on_load_label_map(self):
        fp, _ = QFileDialog.getOpenFileName(self, "选择标签字典 txt", str(Path.cwd()), "Text Files (*.txt)")
        if not fp:
            return
        try:
            self.label_map = parse_label_map_txt(Path(fp))
            if not self.label_map:
                QMessageBox.warning(self, "提示", "未解析到有效标签映射")
                return
            self.append_log(f"已加载标签映射：{len(self.label_map)}项（将在解析与导出阶段生效）")
            self.label_fmt.setText(self.label_fmt.text() + "（已加载标签映射）")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"解析失败: {e}")