from datetime import datetime
from pathlib import Path
from config import paths_to_product_arr
import os

from dotenv import load_dotenv
load_dotenv()

class PathCollector:
    def __init__(self):
        # Оставляем оригинальное получение пути из окружения
        self.img_base_path = os.getenv("IMG_BASE_PATH")
        self.output_path = os.getenv("OUTPUT_PATH")
        self.paths_to_product_arr = paths_to_product_arr

    @staticmethod
    def _get_latest_file(directory_path):

        path = Path(directory_path)

        # Существует ли папка
        if not path.exists() or not path.is_dir():
            return None

        # Список всех файлов в директории
        files = [f for f in path.iterdir() if f.is_file()]

        if not files:
            return None

        # Находим файл с максимальным временем создания (st_ctime)
        latest_file = max(files, key=lambda f: f.stat().st_ctime)
        return latest_file

    def get_path_list(self):
        # Нынешнаяя дата - формат 01.05.2026
        current_date = datetime.now().strftime("%d.%m.%Y")
        # Путь с датой
        base_dated_path = Path(self.img_base_path) / current_date

        final_image_paths = []
        final_output_paths = []

        for product_path in paths_to_product_arr:

            # Полный путь к папке категории
            full_category_dir = base_dated_path / product_path
            full_category_dir_output = Path(self.output_path)/product_path

            # Ищем самый свежий файл
            latest_img = self._get_latest_file(full_category_dir)

            if latest_img:
                # Превращаем объект Path обратно в строку и добавляем в массив
                final_image_paths.append(str(latest_img))
                # Путь для вывода обработанного изображения
                final_output_paths.append(str(full_category_dir_output))

        return final_image_paths, final_output_paths


img_paths = PathCollector()
images, outputs = img_paths.get_path_list()
print("Список картинок:", images)
print("Куда сохранять:", outputs)