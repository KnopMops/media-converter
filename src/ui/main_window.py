from ui.history_tab import HistoryTab
from ui.settings_tab import SettingsTab
from ui.converter_tab import ConverterTab
from ui.components import TitleBar
from mcv import MediaConverter
from database import SettingsDB
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QApplication
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class MediaConverterGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings_db = SettingsDB()
        self.converter = MediaConverter()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Media Converter")
        self.setGeometry(100, 100, 800, 700)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.title_bar = TitleBar(self)
        main_layout.addWidget(self.title_bar)

        self.tabs = QTabWidget()

        self.converter_tab = ConverterTab(self)
        self.history_tab = HistoryTab(self)
        self.settings_tab = SettingsTab(self)

        self.tabs.addTab(self.converter_tab, "🎥 Конвертер")
        self.tabs.addTab(self.history_tab, "📊 История")
        self.tabs.addTab(self.settings_tab, "⚙️ Настройки")

        main_layout.addWidget(self.tabs)

        self.apply_theme("Светлая тема")

    def apply_theme(self, theme_name):
        app = QApplication.instance()

        if theme_name == "Темная тема":
            dark_palette = QPalette()
            dark_palette.setColor(
                QPalette.ColorRole.Window, QColor(53, 53, 53))
            dark_palette.setColor(
                QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
            dark_palette.setColor(
                QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
            dark_palette.setColor(
                QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
            dark_palette.setColor(
                QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.Text,
                                  Qt.GlobalColor.white)
            dark_palette.setColor(
                QPalette.ColorRole.Button, QColor(53, 53, 53))
            dark_palette.setColor(
                QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
            dark_palette.setColor(
                QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
            dark_palette.setColor(QPalette.ColorRole.Link,
                                  QColor(42, 130, 218))
            dark_palette.setColor(
                QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            dark_palette.setColor(
                QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
            app.setPalette(dark_palette)

            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background: #2c3e50;
                    color: #ecf0f1;
                }
                QTabWidget::pane {
                    border: 1px solid #5a6c7d;
                    border-radius: 0px 0px 8px 8px;
                    background: #2c3e50;
                }
                QTabBar::tab {
                    background: #5a6c7d;
                    border: 1px solid #5a6c7d;
                    border-bottom: none;
                    padding: 8px 16px;
                    margin-right: 2px;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    color: #ecf0f1;
                    font-weight: bold;
                }
                QTabBar::tab:selected {
                    background: #34495e;
                    border-bottom: none;
                }
                QTabBar::tab:hover:!selected {
                    background: #4a5a6a;
                }
            """)
        else:
            app.setPalette(app.style().standardPalette())
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background: white;
                    color: #2c3e50;
                }
                QTabWidget::pane {
                    border: 1px solid #bdc3c7;
                    border-radius: 0px 0px 8px 8px;
                    background: white;
                }
                QTabBar::tab {
                    background: #ecf0f1;
                    border: 1px solid #bdc3c7;
                    border-bottom: none;
                    padding: 8px 16px;
                    margin-right: 2px;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    color: #2c3e50;
                    font-weight: bold;
                }
                QTabBar::tab:selected {
                    background: white;
                    border-bottom: none;
                }
                QTabBar::tab:hover:!selected {
                    background: #d5dbdb;
                }
            """)

        self.update()
        self.repaint()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.globalPosition().toPoint() - \
                self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, 'drag_start_position'):
            self.move(event.globalPosition().toPoint() -
                      self.drag_start_position)
            event.accept()
