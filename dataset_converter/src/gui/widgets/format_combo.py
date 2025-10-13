from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox


class FormatCombo(QWidget):
    def __init__(self, title: str = "格式选择"):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.addWidget(QLabel(title))
        self.input = QComboBox()
        self.output = QComboBox()
        for fmt in ["yolo", "voc", "json"]:
            self.input.addItem(fmt)
            self.output.addItem(fmt)
        layout.addWidget(QLabel("输入"))
        layout.addWidget(self.input)
        layout.addWidget(QLabel("输出"))
        layout.addWidget(self.output)

    def get_formats(self):
        return self.input.currentText(), self.output.currentText()