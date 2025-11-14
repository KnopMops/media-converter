import os
import sys
import subprocess
import logging
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QRadioButton, QLabel, QFileDialog, QMessageBox,
                             QGroupBox, QComboBox, QProgressBar)
from PyQt6.QtCore import Qt

from mcv import ConversionThread
from utils import get_file_size
from ui.components import AnimatedButton


class ConverterTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.selected_file = ""
        self.output_path = ""
        self.operation_type = "video"
        self.logger = logging.getLogger(__name__)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("Конвертер медиафайлов")
        title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 24px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        ffmpeg_status = QLabel(self.get_ffmpeg_status())
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
        ffmpeg_status.setToolTip("Нажмите для детальной информации о FFmpeg")
        ffmpeg_status.mousePressEvent = self.show_ffmpeg_details

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
        format_group.setStyleSheet(operation_group.styleSheet())

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
            QComboBox::drop-down {
                border: none;
                width: 20px;
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
                color: #2c3e50;
            }
        """)

        self.update_format_options()

        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()

        format_group.setLayout(format_layout)

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

        layout.addWidget(title)
        layout.addWidget(ffmpeg_status)
        layout.addSpacing(10)
        layout.addWidget(operation_group)
        layout.addSpacing(10)
        layout.addWidget(self.btn_select_file)
        layout.addWidget(self.file_label)
        layout.addSpacing(10)
        layout.addWidget(format_group)
        layout.addSpacing(10)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.btn_convert)
        layout.addStretch()

        self.setLayout(layout)

    def get_ffmpeg_status(self):
        if self.parent.converter.ffmpeg_available:
            try:
                result = subprocess.run(
                    ['ffmpeg', '-version'], capture_output=True, text=True, encoding='utf-8')
                if result.returncode == 0:
                    first_line = result.stdout.split('\n')[0]
                    return f"FFmpeg: ✅ Доступен ({first_line})"
            except:
                pass
            return "FFmpeg: ✅ Доступен"
        else:
            return "FFmpeg: ❌ Не найден (установите FFmpeg для работы)"

    def show_ffmpeg_details(self, event):
        if self.parent.converter.ffmpeg_available:
            try:
                result = subprocess.run(
                    ['ffmpeg', '-version'], capture_output=True, text=True, encoding='utf-8')
                details = result.stdout[:500]
            except:
                details = "Не удалось получить информацию о версии"
        else:
            details = "FFmpeg не установлен или не найден в PATH\n\nУстановите FFmpeg:\n• Windows: скачайте с ffmpeg.org\n• Linux: sudo apt install ffmpeg\n• macOS: brew install ffmpeg"

        QMessageBox.information(self, "Информация о FFmpeg", details)

    def on_operation_changed(self):
        if self.radio_video.isChecked():
            self.operation_type = "video"
            self.btn_convert.setText("🔄 Конвертировать видео")
        else:
            self.operation_type = "audio"
            self.btn_convert.setText("🎵 Извлечь аудио")

        self.update_format_options()
        self.logger.info(f"Тип операции изменен на: {self.operation_type}")

    def update_format_options(self):
        self.format_combo.clear()
        if self.operation_type == "video":
            formats = self.parent.converter.supported_video_formats
        else:
            formats = self.parent.converter.supported_audio_formats

        self.format_combo.addItems(formats)
        if self.operation_type == "video":
            self.format_combo.setCurrentText("mp4")
        else:
            self.format_combo.setCurrentText("mp3")

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
            self.logger.info(f"Выбран файл: {file_path}")

    def convert_media(self):
        if not self.selected_file:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите файл")
            return

        if not self.parent.converter.ffmpeg_available:
            QMessageBox.critical(self, "Ошибка",
                                 "FFmpeg не найден в системе!\n\n"
                                 "Установите FFmpeg:\n"
                                 "• Windows: скачайте с ffmpeg.org\n"
                                 "• Linux: sudo apt install ffmpeg\n"
                                 "• macOS: brew install ffmpeg")
            return

        settings = self.parent.settings_db
        use_constant_output = settings.get_bool("use_constant_output", False)
        constant_output_folder = settings.get_value("output_folder", "")

        if use_constant_output and constant_output_folder:
            output_dir = constant_output_folder
            os.makedirs(output_dir, exist_ok=True)
            self.logger.info(f"Используется постоянная папка: {output_dir}")
        else:
            output_dir = os.path.dirname(self.selected_file)
            self.logger.info(
                f"Используется папка исходного файла: {output_dir}")

        output_format = self.format_combo.currentText()
        quality = settings.get_int("quality", 8)

        self.logger.info(
            f"Начало конвертации: {self.selected_file} -> {output_format}, качество: {quality}")

        self.progress_bar.show()
        self.progress_bar.setRange(0, 0)
        self.btn_convert.setEnabled(False)

        self.conversion_thread = ConversionThread(
            self.parent.converter,
            self.selected_file,
            output_format,
            output_dir,
            self.operation_type,
            quality
        )
        self.conversion_thread.finished.connect(self.on_conversion_finished)
        self.conversion_thread.start()

    def on_conversion_finished(self, success, message):
        self.progress_bar.hide()
        self.btn_convert.setEnabled(True)

        output_format = self.format_combo.currentText()
        base_name = os.path.splitext(os.path.basename(self.selected_file))[0]

        settings = self.parent.settings_db
        use_constant_output = settings.get_bool("use_constant_output", False)
        constant_output_folder = settings.get_value("output_folder", "")

        if use_constant_output and constant_output_folder:
            output_dir = constant_output_folder
        else:
            output_dir = os.path.dirname(self.selected_file)

        output_file = os.path.join(output_dir, f"{base_name}.{output_format}")

        if success:
            if settings.get_bool("save_history", False):
                file_size_before = get_file_size(self.selected_file)
                file_size_after = get_file_size(
                    output_file) if os.path.exists(output_file) else None

                self.parent.settings_db.add_conversion_record(
                    input_file=self.selected_file,
                    output_file=output_file,
                    operation_type=self.operation_type,
                    format=output_format,
                    quality=settings.get_int("quality", 8),
                    status='success',
                    message=message,
                    file_size_before=file_size_before,
                    file_size_after=file_size_after
                )
                self.logger.info("Запись добавлена в историю конвертаций")

            if settings.get_bool("delete_original", False) and self.selected_file:
                try:
                    os.remove(self.selected_file)
                    message += "\n\n🗑️ Исходный файл был удален."
                    self.logger.info(
                        f"Исходный файл удален: {self.selected_file}")
                except Exception as e:
                    error_msg = f"Не удалось удалить исходный файл: {str(e)}"
                    message += f"\n\n⚠️ {error_msg}"
                    self.logger.error(error_msg)

            self.show_detailed_message("✅ Успех", message, success=True)

            if settings.get_bool("auto_open", False):
                try:
                    if sys.platform == "win32":
                        os.startfile(output_dir)
                    elif sys.platform == "darwin":
                        subprocess.Popen(["open", output_dir])
                    else:
                        subprocess.Popen(["xdg-open", output_dir])
                    self.logger.info(f"Открыта папка: {output_dir}")
                except Exception as e:
                    self.logger.error(f"Не удалось открыть папку: {e}")
        else:
            if settings.get_bool("save_history", False):
                file_size_before = get_file_size(self.selected_file)

                self.parent.settings_db.add_conversion_record(
                    input_file=self.selected_file,
                    output_file=None,
                    operation_type=self.operation_type,
                    format=output_format,
                    quality=settings.get_int("quality", 8),
                    status='error',
                    message=message,
                    file_size_before=file_size_before,
                    file_size_after=None
                )
                self.logger.info(
                    "Запись об ошибке добавлена в историю конвертаций")

            self.show_detailed_message("❌ Ошибка", message, success=False)

    def show_detailed_message(self, title, message, success=True):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)

        msg_box.setText(message.split('\n')[0])

        if len(message.split('\n')) > 1:
            detailed_text = '\n'.join(message.split('\n')[1:])
            msg_box.setDetailedText(detailed_text)

        if success:
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        else:
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

            log_button = msg_box.addButton(
                "📋 Показать лог ошибок", QMessageBox.ButtonRole.ActionRole)
            log_button.clicked.connect(self.show_error_log)

        msg_box.exec()

    def show_error_log(self):
        log_file = 'media_converter.log'
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_content = f.read()

                log_window = QMessageBox(self)
                log_window.setWindowTitle("📋 Лог ошибок")
                log_window.setText("Последние ошибки из лог-файла:")
                log_window.setDetailedText(log_content[-5000:])
                log_window.exec()
            except Exception as e:
                QMessageBox.warning(
                    self, "Ошибка", f"Не удалось прочитать лог-файл: {str(e)}")
        else:
            QMessageBox.information(self, "Лог", "Лог-файл не найден")
