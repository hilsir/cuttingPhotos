import cv2, os
import logging
from pathlib import Path
from ultralytics import YOLO
from datetime import datetime
from dotenv import load_dotenv
from shelf_sorter import ShelfSorter
load_dotenv()

logger = logging.getLogger(__name__)

# Планируется, что эта система будет работать на файловом сервере
# Поэтому должно работать на cpu

class ImageCutter:
    def __init__(self):
        model_path = os.getenv("MODEL_PATH")
        self.model = YOLO(model_path)
        self.shelf_sorter = ShelfSorter(os.getenv("MARKUP_PATH"), os.getenv("DATA_ROUTER_PATH"))

    def process_image(self, image_path: str, output_path: str) -> bool:
        img = cv2.imread(image_path)

        if img is None:
            logger.warning(f"Не удалось загрузить {image_path}")
            return False

        detected_goods = self.model(img)

        if not detected_goods or len(detected_goods[0].boxes) == 0:
            logger.info(f"Объекты на {image_path} не обнаружены.")
            return False

        cut_count = 0

        # Нарезка найденных объектов
        for detected_good in detected_goods:
            for box in detected_good.boxes:
                # Координаты товара на фотографии
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                # Обрезаем изображение
                cutting_img = img[y1:y2, x1:x2]

                # Определяем полку по центру бокса
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                save_path = self.shelf_sorter.resolve_shelf_path(output_path, image_path, cx, cy)

                # parents=True создаст всю цепочку папок, exist_ok=True не выдаст ошибку если папка уже есть
                # Создаём только сейчас - когда точно есть что сохранить
                Path(save_path).mkdir(parents=True, exist_ok=True)

                # Формируем имя файла по времени
                times = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                cutting_img_name = f"{save_path}/img_{times}.png"

                cv2.imwrite(str(cutting_img_name), cutting_img)
                cut_count += 1

        logger.info(f"Нарезано {cut_count} товаров из {image_path}")
        return cut_count > 0

