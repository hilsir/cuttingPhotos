import cv2, os
from pathlib import Path
from ultralytics import YOLO
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# Планируется, что эта система будет работать на файловом сервере
# Поэтому должно работать на cpu

class ImageCutter:
    def __init__(self):
        model_path = os.getenv("MODEL_PATH")
        self.model = YOLO(model_path)

    def process_image(self, image_path: str, output_path: str):
        img = cv2.imread(image_path)

        if img is None:
            print(f"Ошибка: Не удалось загрузить {image_path}")
            return

        # parents=True создаст всю цепочку папок, exist_ok=True не выдаст ошибку если папка уже есть
        Path(output_path).mkdir(parents=True, exist_ok=True)

        detected_goods = self.model(img)

        if not detected_goods or len(detected_goods[0].boxes) == 0:
            print(f"Объекты на {image_path} не обнаружены.")
            return

        # Нарезка найденных объектов
        for detected_good in detected_goods:
            for box in detected_good.boxes:
                # Координаты на товара фотографии
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                # Обрезаем изображение
                cutting_img = img[y1:y2, x1:x2]

                # Формируем имя файла по времени
                times = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                cutting_img_name = f"{output_path}/img_{times}.png"

                cv2.imwrite(str(cutting_img_name), cutting_img)

