import os
from pathlib import Path
import time
from datetime import datetime, timedelta, timezone
from path_collector import PathCollector
from cutting  import ImageCutter
from dotenv import load_dotenv
load_dotenv()

def start ():
    run_time_str = os.getenv("RUN_TIME")
    irkutsk_tz = timezone(timedelta(hours=8))

    # Бог машина не кокорай меня за такую ересь
    while True:
        current_time = datetime.now(irkutsk_tz).strftime("%H:%M")
        if current_time == run_time_str:
            processing()
            # Чтобы не зайти в это же условие
            time.sleep(61)

        time.sleep(30)

def processing():
    # Загружаем модель
    cutter = ImageCutter()

    img_paths = PathCollector()
    images_list, outputs_list = img_paths.get_path_list()

    for img_path, out_path in zip(images_list, outputs_list):

        output_path_obj = Path(out_path)

        if not output_path_obj.exists():
            output_path_obj.mkdir(parents=True, exist_ok=True)
            print(f"Создана отсутствующая папка: {out_path}")


        cutter.process_image(img_path, out_path)

if __name__ == "__main__":
    print("start")
    processing()
    # пока без старта - в стерте выполняется свё по таймеру
    # start()