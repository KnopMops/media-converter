import logging
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QCheckBox, QLabel, QFileDialog, QMessageBox,
                             QGroupBox, QComboBox, QLineEdit, QSlider)
from PyQt6.QtCore import Qt

from utils import setup_logging
from ui.components import AnimatedButton


class SettingsTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.settings = self.parent.settings_db
        self.logger = logging.getLogger(__name__)
        self.initUI()
        self.loadSettings()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        output_group = QGroupBox("Настройки выходной папки")
        output_group.setStyleSheet("""
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

        output_layout = QVBoxLayout()

        self.cb_constant_output = QCheckBox(
            "Использовать постоянную выходную папку")
        self.cb_constant_output.setStyleSheet("""
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
        self.cb_constant_output.stateChanged.connect(
            self.toggle_constant_output)

        folder_layout = QHBoxLayout()
        self.folder_path = QLineEdit()
        self.folder_path.setPlaceholderText(
            "Выберите папку для сохранения файлов...")
        self.folder_path.setStyleSheet("""
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 8px;
                background: white;
                font-size: 14px;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)

        self.btn_browse_folder = AnimatedButton("📁 Обзор")
        self.btn_browse_folder.setStyleSheet("""
            AnimatedButton {
                background: #95a5a6;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                min-width: 80px;
            }
            AnimatedButton:hover {
                background: #7f8c8d;
            }
        """)
        self.btn_browse_folder.clicked.connect(self.select_output_folder)

        folder_layout.addWidget(self.folder_path)
        folder_layout.addWidget(self.btn_browse_folder)

        output_layout.addWidget(self.cb_constant_output)
        output_layout.addLayout(folder_layout)
        output_group.setLayout(output_layout)

        quality_group = QGroupBox("Настройки качества")
        quality_group.setStyleSheet(output_group.styleSheet())

        quality_layout = QVBoxLayout()

        quality_slider_layout = QHBoxLayout()
        quality_label = QLabel("Качество конвертации:")
        quality_label.setStyleSheet("color: #2c3e50; font-size: 14px;")

        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setMinimum(1)
        self.quality_slider.setMaximum(10)
        self.quality_slider.setValue(8)
        self.quality_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.quality_slider.setTickInterval(1)
        self.quality_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #bdc3c7;
                height: 8px;
                background: #ecf0f1;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #3498db;
                border: 1px solid #2980b9;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::sub-page:horizontal {
                background: #3498db;
                border-radius: 4px;
            }
        """)

        self.quality_value = QLabel("8/10")
        self.quality_value.setStyleSheet(
            "color: #2c3e50; font-size: 14px; font-weight: bold; min-width: 40px;")

        self.quality_slider.valueChanged.connect(self.update_quality_label)

        quality_slider_layout.addWidget(quality_label)
        quality_slider_layout.addWidget(self.quality_slider)
        quality_slider_layout.addWidget(self.quality_value)

        quality_layout.addLayout(quality_slider_layout)

        quality_desc = QLabel(
            "1 - Наименьший размер (низкое качество)\n10 - Наилучшее качество (большой размер)")
        quality_desc.setStyleSheet(
            "color: #7f8c8d; font-size: 12px; background: #f8f9fa; padding: 8px; border-radius: 5px;")
        quality_desc.setWordWrap(True)

        quality_layout.addWidget(quality_desc)
        quality_group.setLayout(quality_layout)

        theme_group = QGroupBox("Настройки темы")
        theme_group.setStyleSheet(output_group.styleSheet())

        theme_layout = QVBoxLayout()

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Светлая тема", "Темная тема", "Авто тема"])
        self.theme_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 8px;
                background: white;
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
        self.theme_combo.currentTextChanged.connect(self.change_theme)

        theme_layout.addWidget(self.theme_combo)
        theme_group.setLayout(theme_layout)

        advanced_group = QGroupBox("Дополнительные настройки")
        advanced_group.setStyleSheet(output_group.styleSheet())

        advanced_layout = QVBoxLayout()

        self.cb_enable_logging = QCheckBox("Включить логирование")
        self.cb_enable_logging.setStyleSheet(
            self.cb_constant_output.styleSheet())

        self.cb_auto_open = QCheckBox(
            "Автоматически открывать папку после конвертации")
        self.cb_auto_open.setStyleSheet(self.cb_constant_output.styleSheet())

        self.cb_show_details = QCheckBox(
            "Показывать подробности процесса конвертации")
        self.cb_show_details.setStyleSheet(
            self.cb_constant_output.styleSheet())

        self.cb_save_history = QCheckBox("Сохранять историю конвертаций")
        self.cb_save_history.setStyleSheet(
            self.cb_constant_output.styleSheet())

        self.cb_delete_original = QCheckBox(
            "Удалять исходные файлы после успешной конвертации")
        self.cb_delete_original.setStyleSheet(
            self.cb_constant_output.styleSheet())

        advanced_layout.addWidget(self.cb_enable_logging)
        advanced_layout.addWidget(self.cb_auto_open)
        advanced_layout.addWidget(self.cb_show_details)
        advanced_layout.addWidget(self.cb_save_history)
        advanced_layout.addWidget(self.cb_delete_original)
        advanced_group.setLayout(advanced_layout)

        buttons_layout = QHBoxLayout()

        self.btn_save_settings = AnimatedButton("💾 Сохранить настройки")
        self.btn_save_settings.setStyleSheet("""
            AnimatedButton {
                background: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            AnimatedButton:hover {
                background: #219a52;
            }
        """)
        self.btn_save_settings.clicked.connect(self.saveSettings)

        self.btn_reset_settings = AnimatedButton("🔄 Сбросить настройки")
        self.btn_reset_settings.setStyleSheet("""
            AnimatedButton {
                background: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            AnimatedButton:hover {
                background: #c0392b;
            }
        """)
        self.btn_reset_settings.clicked.connect(self.resetSettings)

        buttons_layout.addWidget(self.btn_save_settings)
        buttons_layout.addWidget(self.btn_reset_settings)

        layout.addWidget(output_group)
        layout.addWidget(quality_group)
        layout.addWidget(theme_group)
        layout.addWidget(advanced_group)
        layout.addLayout(buttons_layout)
        layout.addStretch()

        self.setLayout(layout)

    def toggle_constant_output(self, state):
        enabled = state == Qt.CheckState.Checked.value
        self.folder_path.setEnabled(enabled)
        self.btn_browse_folder.setEnabled(enabled)
        self.logger.info(
            f"Постоянная выходная папка: {'включена' if enabled else 'выключена'}")

    def select_output_folder(self):
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку для сохранения"
        )

        if folder_path:
            self.folder_path.setText(folder_path)
            self.logger.info(f"Выбрана выходная папка: {folder_path}")

    def update_quality_label(self, value):
        self.quality_value.setText(f"{value}/10")

    def change_theme(self, theme_name):
        self.logger.info(f"Смена темы на: {theme_name}")
        self.parent.apply_theme(theme_name)

    def saveSettings(self):
        self.settings.set_value("use_constant_output",
                                self.cb_constant_output.isChecked())
        self.settings.set_value("output_folder", self.folder_path.text())
        self.settings.set_value("quality", self.quality_slider.value())
        self.settings.set_value("theme", self.theme_combo.currentText())
        self.settings.set_value(
            "enable_logging", self.cb_enable_logging.isChecked())
        self.settings.set_value("auto_open", self.cb_auto_open.isChecked())
        self.settings.set_value(
            "show_details", self.cb_show_details.isChecked())
        self.settings.set_value(
            "save_history", self.cb_save_history.isChecked())
        self.settings.set_value(
            "delete_original", self.cb_delete_original.isChecked())

        setup_logging(self.cb_enable_logging.isChecked())

        self.logger.info("Настройки сохранены")
        QMessageBox.information(
            self, "Настройки", "Настройки успешно сохранены!")

    def loadSettings(self):
        self.cb_constant_output.setChecked(
            self.settings.get_bool("use_constant_output", False))
        self.folder_path.setText(self.settings.get_value("output_folder", ""))
        self.quality_slider.setValue(self.settings.get_int("quality", 8))
        self.theme_combo.setCurrentText(
            self.settings.get_value("theme", "Светлая тема"))
        self.cb_enable_logging.setChecked(
            self.settings.get_bool("enable_logging", True))
        self.cb_auto_open.setChecked(
            self.settings.get_bool("auto_open", False))
        self.cb_show_details.setChecked(
            self.settings.get_bool("show_details", False))
        self.cb_save_history.setChecked(
            self.settings.get_bool("save_history", False))
        self.cb_delete_original.setChecked(
            self.settings.get_bool("delete_original", False))

        self.toggle_constant_output(self.cb_constant_output.isChecked())
        self.update_quality_label(self.quality_slider.value())

        self.parent.apply_theme(
            self.settings.get_value("theme", "Светлая тема"))
        self.logger.info("Настройки загружены")

    def resetSettings(self):
        reply = QMessageBox.question(self, "Сброс настроек",
                                     "Вы уверены, что хотите сбросить все настройки к значениям по умолчанию?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.settings.clear()
            self.loadSettings()
            self.logger.info("Настройки сброшены к значениям по умолчанию")
            QMessageBox.information(
                self, "Настройки", "Настройки сброшены к значениям по умолчанию!")
