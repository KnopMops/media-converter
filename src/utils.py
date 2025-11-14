import logging
import os


def setup_logging(enable_logging=True):
    if enable_logging:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('media_converter.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    else:
        logging.basicConfig(level=logging.WARNING, handlers=[])


def get_file_size(file_path):
    try:
        return os.path.getsize(file_path) if os.path.exists(file_path) else None
    except:
        return None
