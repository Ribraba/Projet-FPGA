import logging
import os

def setup_logging(config):
    level = getattr(logging, config['level'].upper(), logging.INFO)
    folder = config['folder']

    if not os.path.exists(folder):
        os.makedirs(folder)

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(folder, 'ecg_processing.log')),
            logging.StreamHandler()
        ]
    )
