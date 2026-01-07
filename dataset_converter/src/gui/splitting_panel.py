from pathlib import Path
import random
import shutil

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QTextEdit,
    QFileDialog,
    QMessageBox,
    QSpinBox,
    QLineEdit,
    QProgressBar,
    QScrollArea,
    QGroupBox,
    QGridLayout,
)

from .styles import AppStyles


class SplittingPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        
        # 应用统一样式
        self.setStyleSheet(AppStyles.get_panel_style())

        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(2)
        scroll_area.setHorizontalScrollBarPolicy(1)
        
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)

        # 路径选择组
        path_group = QGroupBox("数据集路径")
        path_layout = QVBoxLayout(path_group)
        
        # 输入路径
        input_layout = QHBoxLayout()
        self.input_label = QLabel("数据集目录: 未选择")
        self.input_label.setStyleSheet(AppStyles.get_label_style("status"))
        btn_in = QPushButton("选择数据集目录")
        btn_in.setStyleSheet(AppStyles.get_button_style("default"))
        btn_in.clicked.connect(self.choose_input)
        input_layout.addWidget(self.input_label, 1)
        input_layout.addWidget(btn_in)
        
        # 输出路径
        output_layout = QHBoxLayout()
        self.output_label = QLabel("输出目录: 未选择")
        self.output_label.setStyleSheet(AppStyles.get_label_style("status"))
        btn_out = QPushButton("选择输出目录")
        btn_out.setStyleSheet(AppStyles.get_button_style("default"))
        btn_out.clicked.connect(self.choose_output)
        output_layout.addWidget(self.output_label, 1)
        output_layout.addWidget(btn_out)
        
        path_layout.addLayout(input_layout)
        path_layout.addLayout(output_layout)
        layout.addWidget(path_group)

        # 比例设置组
        ratio_group = QGroupBox("划分比例设置")
        ratio_layout = QGridLayout(ratio_group)
        
        ratio_layout.addWidget(QLabel("训练集 (%):"), 0, 0)
        self.train_ratio = QSpinBox()
        self.train_ratio.setRange(0, 100)
        self.train_ratio.setValue(70)
        self.train_ratio.setStyleSheet(AppStyles.get_spinbox_style())
        ratio_layout.addWidget(self.train_ratio, 0, 1)
        
        ratio_layout.addWidget(QLabel("验证集 (%):"), 0, 2)
        self.val_ratio = QSpinBox()
        self.val_ratio.setRange(0, 100)
        self.val_ratio.setValue(20)
        self.val_ratio.setStyleSheet(AppStyles.get_spinbox_style())
        ratio_layout.addWidget(self.val_ratio, 0, 3)
        
        ratio_layout.addWidget(QLabel("测试集 (%):"), 1, 0)
        self.test_ratio = QSpinBox()
        self.test_ratio.setRange(0, 100)
        self.test_ratio.setValue(10)
        self.test_ratio.setEnabled(False)
        self.test_ratio.setStyleSheet(AppStyles.get_spinbox_style())
        ratio_layout.addWidget(self.test_ratio, 1, 1)
        
        # 随机种子
        ratio_layout.addWidget(QLabel("随机种子:"), 1, 2)
        self.seed_edit = QLineEdit()
        self.seed_edit.setPlaceholderText("例如：42，不填则随机")
        ratio_layout.addWidget(self.seed_edit, 1, 3)
        
        layout.addWidget(ratio_group)

        # 操作按钮组
        op_group = QGroupBox("操作")
        op_layout = QHBoxLayout(op_group)
        
        btn_validate = QPushButton("验证数据集")
        btn_validate.setStyleSheet(AppStyles.get_button_style("primary"))
        btn_validate.clicked.connect(self.on_validate)
        
        btn_split = QPushButton("开始划分")
        btn_split.setStyleSheet(AppStyles.get_button_style("success"))
        btn_split.clicked.connect(self.on_split)
        
        op_layout.addWidget(btn_validate)
        op_layout.addWidget(btn_split)
        layout.addWidget(op_group)
        
        # 设置滚动内容
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # 进度条 - 固定在底部
        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.progress.setStyleSheet(AppStyles.get_progressbar_style())
        main_layout.addWidget(self.progress)
        
        # 日志输出 - 固定在底部
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMaximumHeight(150)
        self.log_view.setStyleSheet(AppStyles.get_textedit_style())
        
        log_label = QLabel("划分日志:")
        log_label.setStyleSheet(AppStyles.get_label_style("subtitle"))
        main_layout.addWidget(log_label)
        main_layout.addWidget(self.log_view)

        self.input_dir = None
        self.output_dir = None

        # 比例联动：前两个改变，第三个自动补齐为 100 - 前两者
        self.train_ratio.valueChanged.connect(self.on_ratio_change)
        self.val_ratio.valueChanged.connect(self.on_ratio_change)
        self.on_ratio_change()

    def choose_input(self):
        d = QFileDialog.getExistingDirectory(self, "选择数据集目录", str(Path.cwd()))
        if d:
            self.input_dir = Path(d)
            self.input_label.setText(f"数据集目录: {d}")

    def choose_output(self):
        d = QFileDialog.getExistingDirectory(self, "选择输出目录", str(Path.cwd()))
        if d:
            self.output_dir = Path(d)
            self.output_label.setText(f"输出目录: {d}")

    def _append_log(self, msg: str):
        self.log_view.append(msg)

    def _relative_stem(self, p: Path, root: Path) -> str:
        rel = p.relative_to(root)
        return str(rel.parent / rel.stem)

    def _find_label_for_image(self, img: Path):
        stem = img.with_suffix("")
        for ext in (".txt", ".json", ".xml"):
            lab = stem.with_suffix(ext)
            if lab.exists():
                return lab
        return None

    def on_validate(self):
        if not self.input_dir:
            QMessageBox.information(self, "提示", "请先选择数据集目录")
            return
        imgs = self._gather_images(self.input_dir)
        if not imgs:
            QMessageBox.warning(self, "提示", "未在数据集目录中发现图片文件")
            return
        # 收集标签文件与映射
        label_exts = {".txt", ".json", ".xml"}
        label_files = [p for p in self.input_dir.rglob("*") if p.suffix.lower() in label_exts]
        img_stems = {self._relative_stem(p, self.input_dir) for p in imgs}
        lab_stems = {self._relative_stem(p, self.input_dir) for p in label_files}

        missing_labels = [p for p in imgs if self._relative_stem(p, self.input_dir) not in lab_stems]
        orphan_labels = [p for p in label_files if self._relative_stem(p, self.input_dir) not in img_stems]

        self._append_log(f"验证结果：图片数={len(imgs)}，标签数={len(label_files)}")
        self._append_log(f"缺少标签的图片：{len(missing_labels)}；没有对应图片的标签：{len(orphan_labels)}")
        # 展示前若干个问题样本
        show_n = 10
        if missing_labels:
            self._append_log("缺少标签的图片示例：")
            for p in missing_labels[:show_n]:
                self._append_log(f"- {p}")
        if orphan_labels:
            self._append_log("没有对应图片的标签示例：")
            for p in orphan_labels[:show_n]:
                self._append_log(f"- {p}")
        if not missing_labels and not orphan_labels:
            QMessageBox.information(self, "验证通过", "图片与标签数量与配对均正常")
        else:
            QMessageBox.warning(self, "验证警告", "发现图片与标签不一致，请检查日志详情")

    def _gather_images(self, root: Path):
        exts = {".jpg", ".jpeg", ".png", ".bmp"}
        files = []
        for p in root.rglob("*"):
            if p.suffix.lower() in exts:
                files.append(p)
        return files

    def _copy_pair(self, img: Path, out_subdir: Path, rel_root: Path):
        """复制图片及同名标注，保留相对目录结构，避免同名覆盖。

        rel_root: 输入数据集的根，用于计算相对路径。
        """
        rel = img.relative_to(rel_root)
        dest_img_dir = out_subdir / rel.parent
        dest_img_dir.mkdir(parents=True, exist_ok=True)
        dest_img = dest_img_dir / img.name
        # 如果存在同名文件，追加序号以避免覆盖
        if dest_img.exists():
            base = img.stem
            suffix = img.suffix
            k = 1
            while True:
                candidate = dest_img_dir / f"{base}_{k}{suffix}"
                if not candidate.exists():
                    dest_img = candidate
                    break
                k += 1
        shutil.copy2(img, dest_img)

        # 同步复制同名标注文件（常见格式），保持同目录结构
        stem = img.with_suffix("")
        for ext in (".txt", ".json", ".xml"):
            lab = stem.with_suffix(ext)
            if lab.exists():
                dest_lab = dest_img_dir / lab.name
                if dest_lab.exists():
                    base = lab.stem
                    k = 1
                    while True:
                        candidate = dest_img_dir / f"{base}_{k}{lab.suffix}"
                        if not candidate.exists():
                            dest_lab = candidate
                            break
                        k += 1
                shutil.copy2(lab, dest_lab)

    def on_split(self):
        if not self.input_dir or not self.output_dir:
            QMessageBox.warning(self, "提示", "请先选择数据集目录与输出目录")
            return
        # 开始前自动进行一次简单验证
        imgs = self._gather_images(self.input_dir)
        label_exts = {".txt", ".json", ".xml"}
        label_files = [p for p in self.input_dir.rglob("*") if p.suffix.lower() in label_exts]
        img_stems = {self._relative_stem(p, self.input_dir) for p in imgs}
        lab_stems = {self._relative_stem(p, self.input_dir) for p in label_files}
        missing_cnt = len([s for s in img_stems if s not in lab_stems])
        orphan_cnt = len([s for s in lab_stems if s not in img_stems])
        if missing_cnt or orphan_cnt:
            msg = f"检测到问题：缺少标签图片数={missing_cnt}；标签无对应图片数={orphan_cnt}。是否继续？"
            ret = QMessageBox.question(self, "验证警告", msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if ret != QMessageBox.Yes:
                return
        tr, vr, te = self.train_ratio.value(), self.val_ratio.value(), self.test_ratio.value()
        total_ratio = tr + vr + te
        if total_ratio != 100:
            # 自动调整为总和 100
            te = max(0, 100 - tr - vr)
            self.test_ratio.setValue(te)
            total_ratio = tr + vr + te
            if total_ratio != 100:
                QMessageBox.warning(self, "提示", "比例总和必须为 100")
                return

        imgs = self._gather_images(self.input_dir)
        if not imgs:
            QMessageBox.warning(self, "提示", "未在数据集目录中发现图片文件")
            return

        self._append_log(f"发现图片文件 {len(imgs)} 个，开始划分...")
        # 随机种子（可复现）与打乱
        seed_text = (self.seed_edit.text() or "").strip()
        if seed_text:
            try:
                seed = int(seed_text)
                random.seed(seed)
                self._append_log(f"使用随机种子：{seed}")
            except ValueError:
                self._append_log("随机种子无效，忽略并使用默认随机")
        random.shuffle(imgs)

        # 计算数量
        n = len(imgs)
        n_train = int(n * tr / 100)
        n_val = int(n * vr / 100)
        n_test = n - n_train - n_val

        train_dir = self.output_dir / "train"
        val_dir = self.output_dir / "val"
        test_dir = self.output_dir / "test"
        train_dir.mkdir(parents=True, exist_ok=True)
        val_dir.mkdir(parents=True, exist_ok=True)
        test_dir.mkdir(parents=True, exist_ok=True)

        # 进度条按已处理数量更新
        total = len(imgs)
        for i, img in enumerate(imgs):
            if i < n_train:
                self._copy_pair(img, train_dir, self.input_dir)
            elif i < n_train + n_val:
                self._copy_pair(img, val_dir, self.input_dir)
            else:
                self._copy_pair(img, test_dir, self.input_dir)
            # 更新进度
            pct = int((i + 1) * 100 / total)
            self.progress.setValue(pct)

        self._append_log(
            f"已划分完成：train={n_train}, val={n_val}, test={n_test}，输出目录：{self.output_dir}"
        )
        QMessageBox.information(self, "完成", "数据集划分完成！")

    def on_ratio_change(self):
        tr = self.train_ratio.value()
        # 验证最大值受训练值约束，保证 tr+vr <= 100
        self.val_ratio.blockSignals(True)
        self.val_ratio.setMaximum(100 - tr)
        self.val_ratio.blockSignals(False)

        vr = self.val_ratio.value()
        # 训练最大值受验证值约束，保证 tr+vr <= 100
        self.train_ratio.blockSignals(True)
        self.train_ratio.setMaximum(100 - vr)
        self.train_ratio.blockSignals(False)

        te = max(0, 100 - tr - vr)
        self.test_ratio.blockSignals(True)
        self.test_ratio.setValue(te)
        self.test_ratio.blockSignals(False)
        self._append_log(f"比例更新：训练={tr} 验证={vr} 测试={te}（合计100）")