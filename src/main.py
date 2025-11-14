from database import SettingsDB
from utils import setup_logging
from ui.main_window import MediaConverterGUI
import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    settings_db = SettingsDB()
    enable_logging_setting = settings_db.get_bool("enable_logging", True)
    setup_logging(enable_logging_setting)

    logger = logging.getLogger(__name__)
    logger.info("Запуск Media Converter")

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    app.setApplicationName("Media Converter")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("MediaConverter")

    converter_gui = MediaConverterGUI()
    converter_gui.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
