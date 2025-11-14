import os
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
                             QMessageBox, QGroupBox, QTextEdit, QSplitter)
from PyQt6.QtCore import Qt


class HistoryTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.settings = self.parent.settings_db
        self.initUI()
        self.load_history()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("История конвертаций")
        title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 24px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 14px;
                padding: 8px;
                background: #f8f9fa;
                border-radius: 5px;
                border: 1px solid #bdc3c7;
            }
        """)
        self.update_statistics()

        controls_layout = QHBoxLayout()

        self.btn_refresh = QPushButton("🔄 Обновить")
        self.btn_clear = QPushButton("🗑️ Очистить историю")
        self.btn_export = QPushButton("📊 Экспорт статистики")

        for btn in [self.btn_refresh, self.btn_clear, self.btn_export]:
            btn.setStyleSheet("""
                QPushButton {
                    background: #3498db;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: #2980b9;
                }
            """)

        self.btn_refresh.clicked.connect(self.load_history)
        self.btn_clear.clicked.connect(self.clear_history)
        self.btn_export.clicked.connect(self.export_statistics)

        controls_layout.addWidget(self.btn_refresh)
        controls_layout.addWidget(self.btn_clear)
        controls_layout.addWidget(self.btn_export)
        controls_layout.addStretch()

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Дата и время", "Операция", "Исходный файл", "Формат",
            "Качество", "Статус", "Размер файла"
        ])

        self.table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background: white;
                gridline-color: #bdc3c7;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QTableWidget::item:selected {
                background: #3498db;
                color: white;
            }
            QHeaderView::section {
                background: #34495e;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.doubleClicked.connect(self.show_details)

        details_group = QGroupBox("Детали операции")
        details_group.setStyleSheet("""
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

        details_layout = QVBoxLayout()
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 8px;
                background: white;
                font-family: 'Courier New';
                font-size: 12px;
            }
        """)
        details_layout.addWidget(self.details_text)
        details_group.setLayout(details_layout)

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(self.table)
        splitter.addWidget(details_group)
        splitter.setSizes([400, 200])

        layout.addWidget(title)
        layout.addWidget(self.stats_label)
        layout.addLayout(controls_layout)
        layout.addWidget(splitter)

        self.setLayout(layout)

    def load_history(self):
        history = self.settings.get_conversion_history()
        self.table.setRowCount(len(history))

        for row, record in enumerate(history):
            dt = datetime.fromisoformat(record['timestamp'])
            date_item = QTableWidgetItem(dt.strftime("%Y-%m-%d %H:%M:%S"))

            operation_text = "🎥 Видео" if record['operation_type'] == 'video' else "🎵 Аудио"
            operation_item = QTableWidgetItem(operation_text)

            input_file = os.path.basename(record['input_file'])
            input_item = QTableWidgetItem(input_file)
            input_item.setToolTip(record['input_file'])

            format_item = QTableWidgetItem(record['format'].upper())

            quality_item = QTableWidgetItem(str(record['quality']))

            status_text = "✅ Успех" if record['status'] == 'success' else "❌ Ошибка"
            status_item = QTableWidgetItem(status_text)

            size_before = record['file_size_before']
            size_after = record['file_size_after']
            if size_before and size_after:
                size_text = f"{self.format_size(size_before)} → {self.format_size(size_after)}"
                compression = ((size_before - size_after) / size_before) * 100
                if compression > 0:
                    size_text += f" (-{compression:.1f}%)"
            elif size_before:
                size_text = self.format_size(size_before)
            else:
                size_text = "N/A"
            size_item = QTableWidgetItem(size_text)

            items = [date_item, operation_item, input_item, format_item,
                     quality_item, status_item, size_item]

            for col, item in enumerate(items):
                item.setData(Qt.ItemDataRole.UserRole, record)
                self.table.setItem(row, col, item)

        self.table.resizeColumnsToContents()

    def format_size(self, size_bytes):
        if size_bytes is None:
            return "N/A"

        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def update_statistics(self):
        stats = self.settings.get_statistics()
        self.stats_label.setText(
            f"Всего операций: {stats['total']} | "
            f"Успешно: {stats['success']} | "
            f"Ошибок: {stats['error']} | "
            f"Успешность: {stats['success_rate']:.1f}%"
        )

    def show_details(self, index):
        item = self.table.item(index.row(), 0)
        if item:
            record = item.data(Qt.ItemDataRole.UserRole)
            details = f"""
Операция: {'Конвертация видео' if record['operation_type'] == 'video' else 'Извлечение аудио'}
Дата и время: {datetime.fromisoformat(record['timestamp']).strftime("%Y-%m-%d %H:%M:%S")}
Исходный файл: {record['input_file']}
Выходной файл: {record['output_file'] or 'N/A'}
Формат: {record['format'].upper()}
Качество: {record['quality']}/10
Статус: {'✅ Успешно' if record['status'] == 'success' else '❌ Ошибка'}

Размеры файлов:
  • Исходный: {self.format_size(record['file_size_before']) if record['file_size_before'] else 'N/A'}
  • Выходной: {self.format_size(record['file_size_after']) if record['file_size_after'] else 'N/A'}

Сообщение:
{record['message']}
            """
            self.details_text.setPlainText(details.strip())

    def clear_history(self):
        reply = QMessageBox.question(
            self,
            "Очистка истории",
            "Вы уверены, что хотите очистить всю историю конвертаций?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.settings.clear_history()
            self.load_history()
            self.update_statistics()
            self.details_text.clear()

    def export_statistics(self):
        stats = self.settings.get_statistics()
        history = self.settings.get_conversion_history(1000)

        report = f"""
ОТЧЕТ ПО КОНВЕРТАЦИЯМ
Сгенерирован: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

СТАТИСТИКА:
-----------
Всего операций: {stats['total']}
Успешных: {stats['success']}
Ошибок: {stats['error']}
Процент успеха: {stats['success_rate']:.1f}%

Распределение по типам операций:
"""

        for op_type, count in stats['by_operation'].items():
            report += f"  • {op_type}: {count}\n"

        report += "\nРаспределение по форматам:\n"
        for fmt, count in stats['by_format'].items():
            report += f"  • {fmt.upper()}: {count}\n"

        report += "\nПОСЛЕДНИЕ ОПЕРАЦИИ:\n----------------\n"

        for record in history[:50]:
            dt = datetime.fromisoformat(record['timestamp'])
            status = "УСПЕХ" if record['status'] == 'success' else "ОШИБКА"
            report += f"{dt.strftime('%Y-%m-%d %H:%M')} | {record['operation_type']:6} | {record['format']:4} | {status:6} | {os.path.basename(record['input_file'])}\n"

        dialog = QMessageBox(self)
        dialog.setWindowTitle("Статистика конвертаций")
        dialog.setText("Отчет сгенерирован")
        dialog.setDetailedText(report.strip())
        dialog.exec()
