from pathlib import Path
from typing import Optional

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QTextEdit,
    QCheckBox,
    QSpinBox,
    QDoubleSpinBox,
)

from ..utils.logger import get_logger


class AugmentationPanel(QWidget):
    """数据增强面板：支持常见增强操作和日志输出。"""

    def __init__(self, parent: Optional[QWidget] = None):
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

        # 操作选择
        ops_bar1 = QHBoxLayout()
        self.cb_hflip = QCheckBox("水平翻转")
        self.cb_vflip = QCheckBox("垂直翻转")
        ops_bar1.addWidget(self.cb_hflip)
        ops_bar1.addWidget(self.cb_vflip)
        layout.addLayout(ops_bar1)

        ops_bar2 = QHBoxLayout()
        ops_bar2.addWidget(QLabel("旋转角度(°)"))
        self.sp_rotate = QSpinBox()
        self.sp_rotate.setRange(0, 180)
        self.sp_rotate.setValue(0)
        ops_bar2.addWidget(self.sp_rotate)
        ops_bar2.addSpacing(12)
        ops_bar2.addWidget(QLabel("随机裁剪比例(0.5-1.0)"))
        self.sp_crop = QDoubleSpinBox()
        self.sp_crop.setRange(0.5, 1.0)
        self.sp_crop.setSingleStep(0.05)
        self.sp_crop.setValue(1.0)
        ops_bar2.addWidget(self.sp_crop)
        ops_bar2.addSpacing(12)
        ops_bar2.addWidget(QLabel("缩放比例(0.5-2.0)"))
        self.sp_scale = QDoubleSpinBox()
        self.sp_scale.setRange(0.5, 2.0)
        self.sp_scale.setSingleStep(0.1)
        self.sp_scale.setValue(1.0)
        ops_bar2.addWidget(self.sp_scale)
        layout.addLayout(ops_bar2)

        ops_bar3 = QHBoxLayout()
        self.cb_jitter = QCheckBox("色彩抖动")
        ops_bar3.addWidget(self.cb_jitter)
        ops_bar3.addWidget(QLabel("亮度"))
        self.sp_brightness = QDoubleSpinBox()
        self.sp_brightness.setRange(0.5, 1.5)
        self.sp_brightness.setSingleStep(0.1)
        self.sp_brightness.setValue(1.0)
        ops_bar3.addWidget(self.sp_brightness)
        ops_bar3.addWidget(QLabel("对比度"))
        self.sp_contrast = QDoubleSpinBox()
        self.sp_contrast.setRange(0.5, 1.5)
        self.sp_contrast.setSingleStep(0.1)
        self.sp_contrast.setValue(1.0)
        ops_bar3.addWidget(self.sp_contrast)
        ops_bar3.addWidget(QLabel("饱和度"))
        self.sp_saturation = QDoubleSpinBox()
        self.sp_saturation.setRange(0.5, 1.5)
        self.sp_saturation.setSingleStep(0.1)
        self.sp_saturation.setValue(1.0)
        ops_bar3.addWidget(self.sp_saturation)
        layout.addLayout(ops_bar3)

        ops_bar4 = QHBoxLayout()
        self.cb_mosaic = QCheckBox("Mosaic (YOLO)")
        self.cb_mixup = QCheckBox("MixUp (YOLO)")
        ops_bar4.addWidget(self.cb_mosaic)
        ops_bar4.addWidget(self.cb_mixup)
        ops_bar4.addSpacing(12)
        ops_bar4.addWidget(QLabel("MixUp α"))
        self.sp_mix_alpha = QDoubleSpinBox()
        self.sp_mix_alpha.setRange(0.1, 0.9)
        self.sp_mix_alpha.setSingleStep(0.1)
        self.sp_mix_alpha.setValue(0.5)
        ops_bar4.addWidget(self.sp_mix_alpha)
        layout.addLayout(ops_bar4)

        # 运行与日志
        btn_run = QPushButton("开始增强")
        btn_run.clicked.connect(self.on_run)
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        layout.addWidget(btn_run)
        layout.addWidget(QLabel("日志输出"))
        layout.addWidget(self.log_view)

        self.input_dir: Optional[Path] = None
        self.output_dir: Optional[Path] = None

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

    def append_log(self, msg: str):
        self.log_view.append(msg)
        self.logger.info(msg)

    def on_run(self):
        if not self.input_dir or not self.output_dir:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "提示", "请先选择输入与输出目录")
            return
        try:
            self.append_log("开始数据增强…")
            # 延迟导入，避免 GUI 初始化耗时
            from ..core.augmentor import AugmentOptions, augment_dataset

            opts = AugmentOptions(
                hflip=self.cb_hflip.isChecked(),
                vflip=self.cb_vflip.isChecked(),
                rotate_deg=int(self.sp_rotate.value()),
                crop_ratio=float(self.sp_crop.value()),
                scale_ratio=float(self.sp_scale.value()),
                jitter=self.cb_jitter.isChecked(),
                brightness=float(self.sp_brightness.value()),
                contrast=float(self.sp_contrast.value()),
                saturation=float(self.sp_saturation.value()),
                mosaic=self.cb_mosaic.isChecked(),
                mixup=self.cb_mixup.isChecked(),
                mixup_alpha=float(self.sp_mix_alpha.value()),
            )
            augment_dataset(self.input_dir, self.output_dir, opts)
            self.append_log("增强完成")
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "完成", "数据增强完成！")
        except Exception as e:
            self.append_log(f"发生错误: {e}")
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "错误", str(e))