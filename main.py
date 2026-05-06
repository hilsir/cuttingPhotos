import os
from pathlib import Path
import time
from datetime import datetime, timedelta, timezone
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
    img_paths = os.getenv("IMG_PATHS")
    output_dir = os.getenv("OUTPUT_DIR")
    list_img_paths = [p.strip() for p in img_paths.split("|") if p.strip()]

    # Загружаем модель
    cutter = ImageCutter()

    for path_str in list_img_paths:

        input_path_obj = Path(path_str)
        input_folder_name = input_path_obj.name
        output_path = f"{output_dir}/{input_folder_name}"
        output_path_obj = Path(output_path)

        if not output_path_obj.exists():
            output_path_obj.mkdir(parents=True, exist_ok=True)
            print(f"Создана отсутствующая папка: {output_path}")

        # Получаем файл с присмтавкой _final
        file_path = next(input_path_obj.glob("*_final.*"), None)

        if not file_path:
            print(f"В папке {input_path_obj} нет файлов с пометкой '_final'")
            return

        cutter.process_image(file_path, output_path)

if __name__ == "__main__":
    print("start")
    processing()
    # пока без старта - в стерте выполняется свё по таймеру
    # start()