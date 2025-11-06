import sys
import os

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QCheckBox, QLabel,
                             QFileDialog, QMessageBox, QProgressBar, QComboBox,
                             QGroupBox, QRadioButton)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty, QThread, pyqtSignal

try:
    from mcv import MediaConverter

    class CompatibleMediaConverter:
        def __init__(self):
            self.converter = MediaConverter()
            self.supported_video_formats = self.converter.supported_video_formats
            self.supported_audio_formats = self.converter.supported_audio_formats
            self.ffmpeg_available = self.converter.ffmpeg_available

        def convert_video(self, input_file, output_format='mp4', output_path=None):
            success = self.converter.convert_video(
                input_file, output_format, output_path)
            if success:
                base_name = os.path.splitext(os.path.basename(input_file))[0]
                if output_path:
                    output_file = os.path.join(
                        output_path, f"{base_name}.{output_format}")
                else:
                    output_file = os.path.join(os.path.dirname(
                        input_file), f"{base_name}.{output_format}")
                return True, f"Конвертация успешно завершена: {output_file}"
            else:
                return False, "Ошибка конвертации видео"

        def extract_audio(self, input_file, output_format='mp3', output_path=None):
            success = self.converter.extract_audio(
                input_file, output_format, output_path)
            if success:
                base_name = os.path.splitext(os.path.basename(input_file))[0]
                if output_path:
                    output_file = os.path.join(
                        output_path, f"{base_name}.{output_format}")
                else:
                    output_file = os.path.join(os.path.dirname(
                        input_file), f"{base_name}.{output_format}")
                return True, f"Аудио извлечено успешно: {output_file}"
            else:
                return False, "Ошибка извлечения аудио"

except ImportError:
    print('[FATAL_ERROR] Не удалось импортировать mcv')


class ConversionThread(QThread):
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(int)

    def __init__(self, converter, input_file, output_format, output_path, operation_type):
        super().__init__()
        self.converter = converter
        self.input_file = input_file
        self.output_format = output_format
        self.output_path = output_path
        self.operation_type = operation_type

    def run(self):
        try:
            if self.operation_type == 'video':
                success, message = self.converter.convert_video(
                    self.input_file, self.output_format, self.output_path
                )
            else:
                success, message = self.converter.extract_audio(
                    self.input_file, self.output_format, self.output_path
                )

            self.finished.emit(success, message)

        except Exception as e:
            self.finished.emit(False, f"Неожиданная ошибка: {str(e)}")


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


class MediaConverterGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.converter = CompatibleMediaConverter()
        self.selected_file = ""
        self.output_path = ""
        self.operation_type = "video"
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Media Converter")
        self.setGeometry(100, 100, 500, 550)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 10px;
            }
        """)

        central_widget = QWidget()
        central_widget.setStyleSheet("""
            QWidget {
                background: white;
                border-radius: 10px;
                margin: 1px;
            }
        """)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.title_bar = TitleBar(self)
        main_layout.addWidget(self.title_bar)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(30, 20, 30, 30)
        content_layout.setSpacing(15)

        title = QLabel("Media Converter")
        title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 28px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        ffmpeg_status_text = "FFmpeg: ✅ Доступен" if self.converter.ffmpeg_available else "FFmpeg: ❌ Не найден"
        ffmpeg_status = QLabel(ffmpeg_status_text)
        ffmpeg_status.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 12px;
                padding: 5px;
                background: #f8f9fa;
                border-radius: 5px;
            }
        """)
        ffmpeg_status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        operation_group = QGroupBox("Тип операции")
        operation_group.setStyleSheet("""
            QGroupBox {
                color: #2c3e50;
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

        operation_layout = QHBoxLayout()

        self.radio_video = QRadioButton("Конвертировать видео")
        self.radio_audio = QRadioButton("Извлечь аудио")
        self.radio_video.setChecked(True)

        self.radio_video.setStyleSheet("""
            QRadioButton {
                color: #2c3e50;
                font-size: 13px;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background: white;
            }
            QRadioButton::indicator:checked {
                background: #3498db;
                border: 2px solid #3498db;
            }
        """)

        self.radio_audio.setStyleSheet(self.radio_video.styleSheet())

        self.radio_video.toggled.connect(self.on_operation_changed)
        self.radio_audio.toggled.connect(self.on_operation_changed)

        operation_layout.addWidget(self.radio_video)
        operation_layout.addWidget(self.radio_audio)
        operation_layout.addStretch()

        operation_group.setLayout(operation_layout)

        self.btn_select_file = AnimatedButton("📁 Выбрать файл")
        self.btn_select_file.setStyleSheet("""
            AnimatedButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            AnimatedButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #5a6fd8, stop:1 #6a4190);
            }
            AnimatedButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4c5bc6, stop:1 #58357e);
            }
        """)
        self.btn_select_file.clicked.connect(self.select_file)

        self.file_label = QLabel("Файл не выбран")
        self.file_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 12px;
                padding: 8px;
                background: #f8f9fa;
                border-radius: 5px;
                border: 1px dashed #bdc3c7;
            }
        """)
        self.file_label.setWordWrap(True)

        format_group = QGroupBox("Выходной формат")
        format_group.setStyleSheet("""
            QGroupBox {
                color: #2c3e50;
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

        format_layout = QHBoxLayout()

        self.format_combo = QComboBox()

        self.format_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 8px;
                background: white;
                min-width: 120px;
                font-size: 14px;
                color: #2c3e50;
            }
            QComboBox:focus {
                border: 2px solid #3498db;
            }
            QComboBox::drop-down {
                border: none;
                width: 25px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #2c3e50;
                width: 0px;
                height: 0px;
            }
            QComboBox QAbstractItemView {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background: white;
                selection-background-color: #3498db;
                selection-color: white;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                padding: 5px;
                color: #2c3e50;
                background: white;
            }
            QComboBox QAbstractItemView::item:selected {
                background: #3498db;
                color: white;
            }
            QComboBox QAbstractItemView::item:hover {
                background: #5dade2;
                color: white;
            }
        """)

        self.update_format_options()

        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()

        format_group.setLayout(format_layout)

        self.cb_custom_output = QCheckBox("Выбрать OUTPUT папку")
        self.cb_custom_output.setStyleSheet("""
            QCheckBox {
                color: #2c3e50;
                font-size: 14px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                background: white;
            }
            QCheckBox::indicator:checked {
                background: #3498db;
                border: 2px solid #3498db;
            }
        """)
        self.cb_custom_output.stateChanged.connect(
            self.toggle_output_selection)

        self.btn_select_output = AnimatedButton("📁 Выбрать папку")
        self.btn_select_output.setStyleSheet("""
            AnimatedButton {
                background: #95a5a6;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            AnimatedButton:hover {
                background: #7f8c8d;
            }
        """)
        self.btn_select_output.clicked.connect(self.select_output_folder)
        self.btn_select_output.hide()

        self.output_label = QLabel("Папка не выбрана")
        self.output_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 12px;
                padding: 8px;
                background: #f8f9fa;
                border-radius: 5px;
                border: 1px dashed #bdc3c7;
            }
        """)
        self.output_label.setWordWrap(True)
        self.output_label.hide()

        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                background: white;
                height: 20px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 3px;
            }
        """)
        self.progress_bar.hide()

        self.btn_convert = AnimatedButton("🔄 Конвертировать видео")
        self.btn_convert.setStyleSheet("""
            AnimatedButton {
                background: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                height: 45px;
            }
            AnimatedButton:hover {
                background: #219a52;
            }
            AnimatedButton:pressed {
                background: #1e8449;
            }
            AnimatedButton:disabled {
                background: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        self.btn_convert.clicked.connect(self.convert_media)
        self.btn_convert.setEnabled(False)

        content_layout.addWidget(title)
        content_layout.addWidget(ffmpeg_status)
        content_layout.addSpacing(5)
        content_layout.addWidget(operation_group)
        content_layout.addSpacing(5)
        content_layout.addWidget(self.btn_select_file)
        content_layout.addWidget(self.file_label)
        content_layout.addSpacing(5)
        content_layout.addWidget(format_group)
        content_layout.addSpacing(5)
        content_layout.addWidget(self.cb_custom_output)
        content_layout.addWidget(self.btn_select_output)
        content_layout.addWidget(self.output_label)
        content_layout.addSpacing(10)
        content_layout.addWidget(self.progress_bar)
        content_layout.addWidget(self.btn_convert)
        content_layout.addStretch()

        main_layout.addLayout(content_layout)

        self.on_operation_changed()

    def on_operation_changed(self):
        if self.radio_video.isChecked():
            self.operation_type = "video"
            self.btn_convert.setText("🔄 Конвертировать видео")
        else:
            self.operation_type = "audio"
            self.btn_convert.setText("🎵 Извлечь аудио")

        self.update_format_options()

    def update_format_options(self):
        self.format_combo.clear()
        if self.operation_type == "video":
            formats = self.converter.supported_video_formats
        else:
            formats = self.converter.supported_audio_formats

        self.format_combo.addItems(formats)

        if self.operation_type == "video":
            self.format_combo.setCurrentText("mp4")
        else:
            self.format_combo.setCurrentText("mp3")

    def toggle_output_selection(self, state):
        if state == Qt.CheckState.Checked.value:
            self.btn_select_output.show()
            self.output_label.show()
        else:
            self.btn_select_output.hide()
            self.output_label.hide()
            self.output_path = ""
            self.output_label.setText("Папка не выбрана")

    def select_file(self):
        file_filter = "Video Files (*.mp4 *.avi *.mkv *.mov *.webm *.flv *.wmv);;All Files (*)" if self.operation_type == "video" else "All Files (*)"

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл",
            "",
            file_filter
        )

        if file_path:
            self.selected_file = file_path
            filename = os.path.basename(file_path)
            self.file_label.setText(f"📄 {filename}")
            self.btn_convert.setEnabled(True)

    def select_output_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку для сохранения"
        )

        if folder_path:
            self.output_path = folder_path
            self.output_label.setText(f"📁 {folder_path}")

    def convert_media(self):
        if not self.selected_file:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите файл")
            return

        if not self.converter.ffmpeg_available:
            QMessageBox.critical(self, "Ошибка",
                                 "FFmpeg не найден в системе!\n\n"
                                 "Установите FFmpeg:\n"
                                 "• Windows: скачайте с ffmpeg.org\n"
                                 "• Linux: sudo apt install ffmpeg\n"
                                 "• macOS: brew install ffmpeg")
            return

        if self.cb_custom_output.isChecked() and self.output_path:
            output_dir = self.output_path
        else:
            output_dir = os.path.dirname(self.selected_file)

        output_format = self.format_combo.currentText()

        self.progress_bar.show()
        self.progress_bar.setRange(0, 0)
        self.btn_convert.setEnabled(False)

        self.conversion_thread = ConversionThread(
            self.converter,
            self.selected_file,
            output_format,
            output_dir,
            self.operation_type
        )
        self.conversion_thread.finished.connect(self.on_conversion_finished)
        self.conversion_thread.start()

    def on_conversion_finished(self, success, message):
        self.progress_bar.hide()
        self.btn_convert.setEnabled(True)

        if success:
            QMessageBox.information(self, "Успех", message)
        else:
            QMessageBox.critical(self, "Ошибка", message)

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


def main():
    app = QApplication(sys.argv)

    app.setStyleSheet("""
        QMainWindow {
            background: transparent;
        }
    """)

    converter = MediaConverterGUI()
    converter.show()

    sys.exit(app.exec())


if __name__ == "__main__":

    main()
