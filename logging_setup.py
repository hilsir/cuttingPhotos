import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent


def setup_logging():
    # По умолчанию — папка logs прямо внутри проекта, независимо от того,
    # какой WorkingDirectory задан в systemd-юните
    default_log_path = PROJECT_DIR / "logs" / "cutting.log"
    log_path = Path(os.getenv("LOG_PATH", str(default_log_path)))
    log_path.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    file_handler = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(file_handler)
    root.addHandler(stream_handler)
