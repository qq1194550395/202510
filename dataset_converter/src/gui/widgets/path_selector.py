from pathlib import Path
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QFileDialog


class PathSelector(QWidget):
    def __init__(self, title: str):
        super().__init__()
        layout = QHBoxLayout(self)
        self.label = QLabel(f"{title}: 未选择")
        self.btn = QPushButton("选择")
        self.btn.clicked.connect(self.choose)
        layout.addWidget(self.label)
        layout.addWidget(self.btn)
        self._path = None

    def choose(self):
        d = QFileDialog.getExistingDirectory(self, "选择目录")
        if d:
            self._path = Path(d)
            self.label.setText(f"目录: {d}")

    @property
    def path(self) -> Path:
        return self._path