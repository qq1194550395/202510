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
    QCheckBox,
)


class SplittingPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)

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
        btn_in = QPushButton("选择数据集目录")
        btn_in.clicked.connect(self.choose_input)
        input_layout.addWidget(self.input_label, 1)
        input_layout.addWidget(btn_in)
        
        # 输出路径
        output_layout = QHBoxLayout()
        self.output_label = QLabel("输出目录: 未选择")
        btn_out = QPushButton("选择输出目录")
        btn_out.clicked.connect(self.choose_output)
        output_layout.addWidget(self.output_label, 1)
        output_layout.addWidget(btn_out)
        
        path_layout.addLayout(input_layout)
        path_layout.addLayout(output_layout)
        layout.addWidget(path_group)

        # 数据集状态显示组
        status_group = QGroupBox("数据集状态")
        status_layout = QVBoxLayout(status_group)
        
        self.dataset_status_label = QLabel("请先选择数据集目录")
        status_layout.addWidget(self.dataset_status_label)
        
        # 重新划分选项
        self.resplit_checkbox = QCheckBox("重新划分已有数据集（合并所有子集后重新按比例划分）")
        self.resplit_checkbox.setChecked(False)
        status_layout.addWidget(self.resplit_checkbox)
        
        layout.addWidget(status_group)

        # 比例设置组
        ratio_group = QGroupBox("划分比例设置")
        ratio_layout = QGridLayout(ratio_group)
        
        ratio_layout.addWidget(QLabel("训练集 (%):"), 0, 0)
        self.train_ratio = QSpinBox()
        self.train_ratio.setRange(0, 100)
        self.train_ratio.setValue(70)
        ratio_layout.addWidget(self.train_ratio, 0, 1)
        
        ratio_layout.addWidget(QLabel("验证集 (%):"), 0, 2)
        self.val_ratio = QSpinBox()
        self.val_ratio.setRange(0, 100)
        self.val_ratio.setValue(20)
        ratio_layout.addWidget(self.val_ratio, 0, 3)
        
        ratio_layout.addWidget(QLabel("测试集 (%):"), 1, 0)
        self.test_ratio = QSpinBox()
        self.test_ratio.setRange(0, 100)
        self.test_ratio.setValue(10)
        self.test_ratio.setEnabled(False)
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
        btn_validate.setProperty("buttonType", "primary")
        btn_validate.clicked.connect(self.on_validate)
        
        btn_split = QPushButton("开始划分")
        btn_split.setProperty("buttonType", "success")
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
        main_layout.addWidget(self.progress)
        
        # 日志输出 - 固定在底部
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMaximumHeight(150)
        
        log_label = QLabel("划分日志:")
        main_layout.addWidget(log_label)
        main_layout.addWidget(self.log_view)

        self.input_dir = None
        self.output_dir = None
        self.is_standard_structure = False
        self.current_split_info = {}

        # 比例联动：前两个改变，第三个自动补齐为 100 - 前两者
        self.train_ratio.valueChanged.connect(self.on_ratio_change)
        self.val_ratio.valueChanged.connect(self.on_ratio_change)
        self.on_ratio_change()

    def choose_input(self):
        d = QFileDialog.getExistingDirectory(self, "选择数据集目录", str(Path.cwd()))
        if d:
            self.input_dir = Path(d)
            self.input_label.setText(f"数据集目录: {d}")
            self._analyze_dataset_structure()

    def _analyze_dataset_structure(self):
        """分析数据集结构并更新状态显示"""
        if not self.input_dir:
            return
            
        # 检查是否为标准目录结构
        images_dir = self.input_dir / "images"
        labels_dir = self.input_dir / "labels"
        
        self.is_standard_structure = (
            images_dir.exists() and images_dir.is_dir() and
            labels_dir.exists() and labels_dir.is_dir()
        )
        
        if self.is_standard_structure:
            # 分析各子集的数据量
            subsets = ["train", "test", "val"]
            self.current_split_info = {}
            total_images = 0
            
            for subset in subsets:
                img_subset_dir = images_dir / subset
                if img_subset_dir.exists():
                    imgs = self._gather_images(img_subset_dir)
                    self.current_split_info[subset] = len(imgs)
                    total_images += len(imgs)
                else:
                    self.current_split_info[subset] = 0
            
            # 计算当前比例
            if total_images > 0:
                train_pct = round(self.current_split_info.get("train", 0) * 100 / total_images, 1)
                test_pct = round(self.current_split_info.get("test", 0) * 100 / total_images, 1)
                val_pct = round(self.current_split_info.get("val", 0) * 100 / total_images, 1)
                
                status_text = f"检测到标准目录结构数据集\n"
                status_text += f"当前划分: 训练集 {self.current_split_info['train']} 张 ({train_pct}%), "
                status_text += f"测试集 {self.current_split_info['test']} 张 ({test_pct}%), "
                status_text += f"验证集 {self.current_split_info['val']} 张 ({val_pct}%)\n"
                status_text += f"总计: {total_images} 张图片"
                
                # 启用重新划分选项
                self.resplit_checkbox.setEnabled(True)
                self.resplit_checkbox.setChecked(True)
            else:
                status_text = "检测到标准目录结构，但未找到图片文件"
                self.resplit_checkbox.setEnabled(False)
        else:
            # 非标准结构，统计总图片数
            imgs = self._gather_images(self.input_dir)
            status_text = f"检测到非标准目录结构数据集\n总计: {len(imgs)} 张图片\n将按传统方式进行首次划分"
            self.resplit_checkbox.setEnabled(False)
            self.resplit_checkbox.setChecked(False)
        
        self.dataset_status_label.setText(status_text)
        self._append_log(f"数据集分析完成: {status_text.replace(chr(10), ' ')}")

    def choose_output(self):
        d = QFileDialog.getExistingDirectory(self, "选择输出目录", str(Path.cwd()))
        if d:
            self.output_dir = Path(d)
            self.output_label.setText(f"输出目录: {d}")

    def _gather_images_from_standard_structure(self):
        """从标准目录结构中收集所有图片"""
        all_images = []
        images_dir = self.input_dir / "images"
        
        for subset in ["train", "test", "val"]:
            subset_dir = images_dir / subset
            if subset_dir.exists():
                imgs = self._gather_images(subset_dir)
                # 为每个图片添加原始子集信息（用于调试）
                for img in imgs:
                    all_images.append(img)
        
        return all_images

    def _find_corresponding_label(self, img_path, labels_root):
        """在标准目录结构中查找对应的标签文件"""
        # 计算图片在images目录中的相对路径
        images_root = self.input_dir / "images"
        rel_path = img_path.relative_to(images_root)
        
        # 构造对应的标签路径
        label_base = labels_root / rel_path.parent / img_path.stem
        
        # 尝试不同的标签文件扩展名
        for ext in [".txt", ".json", ".xml"]:
            label_path = label_base.with_suffix(ext)
            if label_path.exists():
                return label_path
        
        return None

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
            
        if self.is_standard_structure and self.resplit_checkbox.isChecked():
            # 验证标准目录结构数据集
            self._validate_standard_structure()
        else:
            # 验证传统结构数据集
            self._validate_traditional_structure()

    def _validate_standard_structure(self):
        """验证标准目录结构数据集"""
        images_dir = self.input_dir / "images"
        labels_dir = self.input_dir / "labels"
        
        total_images = 0
        total_labels = 0
        missing_labels = []
        orphan_labels = []
        
        # 检查每个子集
        for subset in ["train", "test", "val"]:
            img_subset_dir = images_dir / subset
            label_subset_dir = labels_dir / subset
            
            if img_subset_dir.exists():
                imgs = self._gather_images(img_subset_dir)
                total_images += len(imgs)
                
                # 检查对应的标签
                for img in imgs:
                    label_path = self._find_corresponding_label(img, labels_dir)
                    if not label_path:
                        missing_labels.append(img)
            
            if label_subset_dir.exists():
                label_exts = {".txt", ".json", ".xml"}
                labels = [p for p in label_subset_dir.rglob("*") if p.suffix.lower() in label_exts]
                total_labels += len(labels)
                
                # 检查孤立的标签
                for label in labels:
                    # 构造对应的图片路径
                    rel_path = label.relative_to(labels_dir)
                    img_base = images_dir / rel_path.parent / label.stem
                    
                    found_img = False
                    for ext in [".jpg", ".jpeg", ".png", ".bmp"]:
                        if (img_base.with_suffix(ext)).exists():
                            found_img = True
                            break
                    
                    if not found_img:
                        orphan_labels.append(label)
        
        self._append_log(f"标准结构验证结果：总图片数={total_images}，总标签数={total_labels}")
        self._append_log(f"缺少标签的图片：{len(missing_labels)}；没有对应图片的标签：{len(orphan_labels)}")
        
        # 显示问题样本
        show_n = 5
        if missing_labels:
            self._append_log("缺少标签的图片示例：")
            for p in missing_labels[:show_n]:
                self._append_log(f"- {p}")
        if orphan_labels:
            self._append_log("没有对应图片的标签示例：")
            for p in orphan_labels[:show_n]:
                self._append_log(f"- {p}")
        
        if not missing_labels and not orphan_labels:
            QMessageBox.information(self, "验证通过", "标准结构数据集验证通过，图片与标签配对正常")
        else:
            QMessageBox.warning(self, "验证警告", "发现图片与标签不一致，请检查日志详情")

    def _validate_traditional_structure(self):
        """验证传统结构数据集"""
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

        self._append_log(f"传统结构验证结果：图片数={len(imgs)}，标签数={len(label_files)}")
        self._append_log(f"缺少标签的图片：{len(missing_labels)}；没有对应图片的标签：{len(orphan_labels)}")
        
        # 展示前若干个问题样本
        show_n = 5
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
            
        # 检查比例
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

        if self.is_standard_structure and self.resplit_checkbox.isChecked():
            # 重新划分标准结构数据集
            self._resplit_standard_dataset(tr, vr, te)
        else:
            # 传统方式划分
            self._split_traditional_dataset(tr, vr, te)

    def _resplit_standard_dataset(self, train_ratio, val_ratio, test_ratio):
        """重新划分标准结构数据集"""
        try:
            # 收集所有图片
            all_images = self._gather_images_from_standard_structure()
            if not all_images:
                QMessageBox.warning(self, "提示", "未在数据集中发现图片文件")
                return

            self._append_log(f"开始重新划分标准结构数据集...")
            self._append_log(f"原始划分: 训练集 {self.current_split_info.get('train', 0)} 张, "
                           f"测试集 {self.current_split_info.get('test', 0)} 张, "
                           f"验证集 {self.current_split_info.get('val', 0)} 张")
            self._append_log(f"目标比例: {train_ratio}% : {val_ratio}% : {test_ratio}%")
            
            # 设置随机种子
            seed_text = (self.seed_edit.text() or "").strip()
            if seed_text:
                try:
                    seed = int(seed_text)
                    random.seed(seed)
                    self._append_log(f"使用随机种子：{seed}")
                except ValueError:
                    self._append_log("随机种子无效，使用默认随机")
            
            # 打乱所有图片
            random.shuffle(all_images)
            
            # 计算新的数量分配
            n = len(all_images)
            n_train = int(n * train_ratio / 100)
            n_val = int(n * val_ratio / 100)
            n_test = n - n_train - n_val
            
            self._append_log(f"新划分: 训练集 {n_train} 张, 验证集 {n_val} 张, 测试集 {n_test} 张")
            
            # 创建输出目录结构
            output_images_dir = self.output_dir / "images"
            output_labels_dir = self.output_dir / "labels"
            
            for subset in ["train", "val", "test"]:
                (output_images_dir / subset).mkdir(parents=True, exist_ok=True)
                (output_labels_dir / subset).mkdir(parents=True, exist_ok=True)
            
            # 复制文件到新的划分
            labels_root = self.input_dir / "labels"
            
            for i, img in enumerate(all_images):
                # 确定目标子集
                if i < n_train:
                    target_subset = "train"
                elif i < n_train + n_val:
                    target_subset = "val"
                else:
                    target_subset = "test"
                
                # 复制图片
                target_img_dir = output_images_dir / target_subset
                target_img_path = target_img_dir / img.name
                
                # 处理同名文件
                if target_img_path.exists():
                    base = img.stem
                    suffix = img.suffix
                    k = 1
                    while True:
                        candidate = target_img_dir / f"{base}_{k}{suffix}"
                        if not candidate.exists():
                            target_img_path = candidate
                            break
                        k += 1
                
                shutil.copy2(img, target_img_path)
                
                # 复制对应的标签文件
                label_path = self._find_corresponding_label(img, labels_root)
                if label_path:
                    target_label_dir = output_labels_dir / target_subset
                    target_label_path = target_label_dir / label_path.name
                    
                    # 处理同名标签文件
                    if target_label_path.exists():
                        base = label_path.stem
                        suffix = label_path.suffix
                        k = 1
                        while True:
                            candidate = target_label_dir / f"{base}_{k}{suffix}"
                            if not candidate.exists():
                                target_label_path = candidate
                                break
                            k += 1
                    
                    shutil.copy2(label_path, target_label_path)
                
                # 更新进度
                progress = int((i + 1) * 100 / len(all_images))
                self.progress.setValue(progress)
            
            self._append_log(f"重新划分完成！输出目录：{self.output_dir}")
            QMessageBox.information(self, "完成", "数据集重新划分完成！")
            
        except Exception as e:
            self._append_log(f"重新划分失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"重新划分失败: {str(e)}")

    def _split_traditional_dataset(self, train_ratio, val_ratio, test_ratio):
        """传统方式划分数据集"""
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

        if not imgs:
            QMessageBox.warning(self, "提示", "未在数据集目录中发现图片文件")
            return

        self._append_log(f"发现图片文件 {len(imgs)} 个，开始传统方式划分...")
        
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
        n_train = int(n * train_ratio / 100)
        n_val = int(n * val_ratio / 100)
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
            f"传统划分完成：train={n_train}, val={n_val}, test={n_test}，输出目录：{self.output_dir}"
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
        
        # 只在有数据集时显示比例更新日志
        if hasattr(self, 'input_dir') and self.input_dir:
            self._append_log(f"比例更新：训练={tr}% 验证={vr}% 测试={te}%（合计100%）")