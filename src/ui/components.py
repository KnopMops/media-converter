from PyQt6.QtWidgets import QPushButton, QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty


class AnimatedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._opacity = 1.0
        self.setFixedHeight(40)

    def getOpacity(self):
        return self._opacity

    def setOpacity(self, value):
        self._opacity = value
        self.update()

    opacity = pyqtProperty(float, getOpacity, setOpacity)

    def enterEvent(self, event):
        self.animateHover(0.7)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.animateHover(1.0)
        super().leaveEvent(event)

    def animateHover(self, target_opacity):
        animation = QPropertyAnimation(self, b"opacity")
        animation.setDuration(200)
        animation.setStartValue(self._opacity)
        animation.setEndValue(target_opacity)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()


class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 5, 5)

        title_label = QLabel("Media Converter v2.0.0")
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
            }
        """)

        btn_minimize = QPushButton("─")
        btn_maximize = QPushButton("□")
        btn_close = QPushButton("×")

        buttons = [btn_minimize, btn_maximize, btn_close]

        for btn in buttons:
            btn.setFixedSize(30, 25)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    font-size: 16px;
                    font-weight: bold;
                    color: #2c3e50;
                }
                QPushButton:hover {
                    background: #e0e0e0;
                    border-radius: 3px;
                }
            """)

        btn_close.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
            }
            QPushButton:hover {
                background: #e74c3c;
                color: white;
                border-radius: 3px;
            }
        """)

        btn_minimize.clicked.connect(self.parent.showMinimized)
        btn_maximize.clicked.connect(self.toggle_maximize)
        btn_close.clicked.connect(self.parent.close)

        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(btn_minimize)
        layout.addWidget(btn_maximize)
        layout.addWidget(btn_close)

        self.setLayout(layout)
        self.setFixedHeight(35)

    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()
