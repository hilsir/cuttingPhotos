from datetime import datetime
from pathlib import Path
import json
import logging
import os

import cv2

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)


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
    def _is_valid_image(file_path: Path) -> bool:
        # Полноценно декодируем файл, чтобы отсеять битые/недописанные снимки
        img = cv2.imread(str(file_path))
        return img is not None

    @classmethod
    def _get_latest_valid_file(cls, directory_path):

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

        # От самого нового к самому старому (по времени создания st_ctime)
        candidates_by_age = sorted(candidates, key=lambda f: f.stat().st_ctime, reverse=True)

        for candidate in candidates_by_age:
            if cls._is_valid_image(candidate):
                return candidate
            logger.warning(f"Битое/нечитаемое изображение пропущено: {candidate}")

        logger.warning(f"В папке {directory_path} не найдено ни одного читаемого изображения")
        return None

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
            logger.warning(f"Папка за сегодня не найдена: {base_dated_path}")
            return final_image_paths, final_output_paths

        product_dirs = self._find_product_dirs(base_dated_path)
        skipped_unknown = 0

        for product_dir in product_dirs:

            # Папка без разметки в data_router.json - пропускаем
            if product_dir.name not in self.known_cameras:
                skipped_unknown += 1
                continue

            # Путь товара относительно папки с датой, например "БАКАЛЕЯ/Соль_1"
            product_path = product_dir.relative_to(base_dated_path)
            # Путь для вывода обработанного изображения - создастся сам при нарезке
            full_category_dir_output = Path(self.output_path) / product_path

            # Ищем самый свежий читаемый файл
            latest_img = self._get_latest_valid_file(product_dir)

            if latest_img:
                # Превращаем объект Path обратно в строку и добавляем в массив
                final_image_paths.append(str(latest_img))
                final_output_paths.append(str(full_category_dir_output))
                logger.info(f"Найдено изображение: {latest_img} -> {full_category_dir_output}")
            else:
                logger.warning(f"Нет пригодного изображения в папке: {product_dir}")

        if skipped_unknown:
            logger.info(f"Пропущено папок без разметки в data_router.json: {skipped_unknown}")

        return final_image_paths, final_output_paths


img_paths = PathCollector()
images, outputs = img_paths.get_path_list()
print("Список картинок:", images)
print("Куда сохранять:", outputs)
