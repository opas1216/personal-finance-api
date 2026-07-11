import logging
import os
from datetime import datetime
from pathlib import Path

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    BASE_DIR = Path(__file__).resolve().parent.parent
    log_dir = BASE_DIR / "Logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"app_{datetime.now().strftime('%Y-%m-%d')}.log"

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)



