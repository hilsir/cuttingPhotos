from datetime import datetime
from pathlib import Path
import json
import os

from dotenv import load_dotenv
load_dotenv()

class PathCollector:
    def __init__(self):
        # Оставляем оригинальное получение пути из окружения
        self.img_base_path = os.getenv("IMG_BASE_PATH")
        self.output_path = os.getenv("OUTPUT_PATH")
        self.known_cameras = self._load_known_cameras(os.getenv("DATA_ROUTER_PATH"))

    @staticmethod
    def _load_known_cameras(data_router_path: str):
        # Обрабатываем только папки, для которых есть разметка стеллажей в data_router.json
        if not data_router_path:
            return set()

        path = Path(data_router_path)
        if not path.exists():
            return set()

        with open(path) as f:
            data = json.load(f)

        return set(data.get("images", {}).keys())

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

        # "_final" файлы могут быть ещё недописаны — берём их только если больше ничего нет
        non_final_files = [f for f in files if not f.stem.endswith('_final')]
        candidates = non_final_files if non_final_files else files

        # Находим файл с максимальным временем создания (st_ctime)
        latest_file = max(candidates, key=lambda f: f.stat().st_ctime)
        return latest_file

    @staticmethod
    def _find_product_dirs(base_dir: Path):
        # Ищем сами, без конфига: папка-товар - любая папка, где лежат файлы фото
        product_dirs = []
        for root, _, filenames in os.walk(base_dir):
            if filenames:
                product_dirs.append(Path(root))
        return product_dirs

    def get_path_list(self):
        # Нынешнаяя дата - формат 01.05.2026
        current_date = datetime.now().strftime("%d.%m.%Y")
        # Путь с датой
        base_dated_path = Path(self.img_base_path) / current_date

        final_image_paths = []
        final_output_paths = []

        if not base_dated_path.exists():
            return final_image_paths, final_output_paths

        for product_dir in self._find_product_dirs(base_dated_path):

            # Папка без разметки в data_router.json - пропускаем
            if product_dir.name not in self.known_cameras:
                continue

            # Путь товара относительно папки с датой, например "БАКАЛЕЯ/Соль_1"
            product_path = product_dir.relative_to(base_dated_path)
            # Путь для вывода обработанного изображения - создастся сам при нарезке
            full_category_dir_output = Path(self.output_path) / product_path

            # Ищем самый свежий файл
            latest_img = self._get_latest_file(product_dir)

            if latest_img:
                # Превращаем объект Path обратно в строку и добавляем в массив
                final_image_paths.append(str(latest_img))
                final_output_paths.append(str(full_category_dir_output))

        return final_image_paths, final_output_paths


img_paths = PathCollector()
images, outputs = img_paths.get_path_list()
print("Список картинок:", images)
print("Куда сохранять:", outputs)
