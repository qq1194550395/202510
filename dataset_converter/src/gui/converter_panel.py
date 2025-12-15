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
)

from ..core.converter import convert
from ..utils.logger import get_logger
from ..utils.label_utils import parse_label_map_txt


class ConverterPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger()

        layout = QVBoxLayout(self)

        # 输入输出路径
        path_bar = QHBoxLayout()
        self.input_label = QLabel("输入目录: 未选择")
        self.output_label = QLabel("输出目录: 未选择")
        btn_in = QPushButton("选择输入目录")
        btn_out = QPushButton("选择输出目录")
        btn_in.clicked.connect(self.choose_input)
        btn_out.clicked.connect(self.choose_output)
        path_bar.addWidget(self.input_label)
        path_bar.addWidget(btn_in)
        path_bar.addSpacing(8)
        path_bar.addWidget(self.output_label)
        path_bar.addWidget(btn_out)
        layout.addLayout(path_bar)

        # 格式选择
        fmt_bar1 = QHBoxLayout()
        fmt_bar2 = QHBoxLayout()
        self.label_fmt = QLabel("当前格式: YOLO → VOC（说明：JSON 导出为每图一个 .json）")
        
        # 第一行按钮
        btn_yolo_to_voc = QPushButton("YOLO检测 → VOC")
        btn_voc_to_yolo = QPushButton("VOC → YOLO检测")
        btn_json_to_voc = QPushButton("JSON → VOC")
        btn_yolo_to_json = QPushButton("YOLO检测 → JSON")
        btn_yolo_to_voc.clicked.connect(lambda: self.set_formats("yolo", "voc"))
        btn_voc_to_yolo.clicked.connect(lambda: self.set_formats("voc", "yolo"))
        btn_json_to_voc.clicked.connect(lambda: self.set_formats("json", "voc"))
        btn_yolo_to_json.clicked.connect(lambda: self.set_formats("yolo", "json"))
        
        # 第二行按钮 - YOLO分割相关
        btn_yolo_seg_to_json = QPushButton("YOLO分割 → JSON")
        btn_json_to_yolo = QPushButton("JSON → YOLO检测")
        btn_json_to_yolo_seg = QPushButton("JSON → YOLO分割")
        btn_yolo_seg_to_yolo = QPushButton("YOLO分割 → YOLO检测")
        btn_yolo_seg_to_json.clicked.connect(lambda: self.set_formats("yolo_seg", "json"))
        btn_json_to_yolo.clicked.connect(lambda: self.set_formats("json", "yolo"))
        btn_json_to_yolo_seg.clicked.connect(lambda: self.set_formats("json", "yolo_seg"))
        btn_yolo_seg_to_yolo.clicked.connect(lambda: self.set_formats("yolo_seg", "yolo"))
        
        fmt_bar1.addWidget(self.label_fmt)
        fmt_bar1.addWidget(btn_yolo_to_voc)
        fmt_bar1.addWidget(btn_voc_to_yolo)
        fmt_bar1.addWidget(btn_json_to_voc)
        fmt_bar1.addWidget(btn_yolo_to_json)
        
        fmt_bar2.addWidget(QLabel("分割格式转换:"))
        fmt_bar2.addWidget(btn_yolo_seg_to_json)
        fmt_bar2.addWidget(btn_json_to_yolo)
        fmt_bar2.addWidget(btn_json_to_yolo_seg)
        fmt_bar2.addWidget(btn_yolo_seg_to_yolo)
        
        layout.addLayout(fmt_bar1)
        layout.addLayout(fmt_bar2)

        # 标签字典与转换按钮、日志
        btn_convert = QPushButton("开始转换")
        btn_convert.clicked.connect(self.on_convert)
        btn_label_map = QPushButton("加载标签字典")
        btn_label_map.clicked.connect(self.on_load_label_map)
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        layout.addWidget(btn_label_map)
        layout.addWidget(btn_convert)
        layout.addWidget(QLabel("日志输出"))
        layout.addWidget(self.log_view)

        self.input_dir = None
        self.output_dir = None
        self.input_fmt = "yolo"
        self.output_fmt = "voc"
        self.label_map = {}

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