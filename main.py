import os
import time
import logging
from datetime import datetime, timedelta, timezone
from path_collector import PathCollector
from cutting  import ImageCutter
from logging_setup import setup_logging
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)


def _parse_run_times(run_times_str: str):
    # Несколько времён через запятую, например "10:00,18:00"
    if not run_times_str:
        return []
    return [t.strip() for t in run_times_str.split(",") if t.strip()]


def start ():
    run_times = _parse_run_times(os.getenv("RUN_TIMES") or os.getenv("RUN_TIME"))
    irkutsk_tz = timezone(timedelta(hours=8))

    logger.info(f"Расписание нарезки (по Иркутску): {run_times}")

    # Бог машина не карай меня за такую ересь
    while True:
        current_time = datetime.now(irkutsk_tz).strftime("%H:%M")
        if current_time in run_times:
            try:
                processing()
            except Exception:
                logger.exception("Нарезка упала с необработанной ошибкой")
            # Чтобы не зайти в это же условие
            time.sleep(61)

        time.sleep(30)

def processing():
    started_at = datetime.now()
    logger.info("=== Запуск нарезки ===")

    # Загружаем модель
    cutter = ImageCutter()

    img_paths = PathCollector()
    images_list, outputs_list = img_paths.get_path_list()

    logger.info(f"Найдено изображений для нарезки: {len(images_list)}")

    cut_ok = 0
    cut_failed = 0

    for img_path, out_path in zip(images_list, outputs_list):
        try:
            success = cutter.process_image(img_path, out_path)
            if success:
                cut_ok += 1
            else:
                cut_failed += 1
        except Exception:
            cut_failed += 1
            logger.exception(f"Ошибка при нарезке {img_path}")

    duration = datetime.now() - started_at
    logger.info(
        f"=== Нарезка завершена: успешно {cut_ok}, без результата/с ошибкой {cut_failed}, "
        f"время выполнения {duration} ==="
    )

if __name__ == "__main__":
    setup_logging()
    print("start")
    logger.info("start")
    start()
