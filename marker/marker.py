import cv2
import os
import json

# Настройки
SOURCE_FOLDER = 'for_markup'
MARKUP_FOLDER = './markup'

os.makedirs(MARKUP_FOLDER, exist_ok=True)

# Глобальные переменные для рисования
lines = []           # Список всех готовых линий
current_points = []  # Точки текущей незавершённой линии
temp_img = None


def redraw(base_img):
    # Рисует все готовые линии и текущую незавершённую поверх чистого кадра
    img = base_img.copy()

    for line in lines:
        for i in range(len(line) - 1):
            cv2.line(img, tuple(line[i]), tuple(line[i + 1]), (0, 255, 0), 2)
        for pt in line:
            cv2.circle(img, tuple(pt), 4, (0, 255, 0), -1)

    for i in range(len(current_points) - 1):
        cv2.line(img, current_points[i], current_points[i + 1], (0, 200, 255), 2)
    for pt in current_points:
        cv2.circle(img, pt, 4, (0, 0, 255), -1)

    return img


def mouse_event(event, x, y, flags, param):
    global current_points, lines, temp_img

    if event == cv2.EVENT_MOUSEMOVE:
        # Показываем предварительную линию от последней точки к курсору
        if current_points:
            preview = redraw(param)
            cv2.line(preview, current_points[-1], (x, y), (0, 200, 255), 1)
            cv2.imshow("Drawer", preview)
        return

    if event == cv2.EVENT_LBUTTONDOWN:
        # Добавляем точку к текущей линии
        current_points.append((x, y))
        temp_img = redraw(param)
        cv2.imshow("Drawer", temp_img)

    elif event == cv2.EVENT_RBUTTONDOWN:
        # Правая кнопка — завершить текущую линию
        if len(current_points) >= 2:
            lines.append(list(current_points))
            current_points = []
            temp_img = redraw(param)
            cv2.imshow("Drawer", temp_img)
            print(f"Линия добавлена, всего: {len(lines)}")
        else:
            print("Нужно минимум 2 точки")


def process_images():
    global lines, current_points, temp_img

    files = [f for f in os.listdir(SOURCE_FOLDER) if f.endswith(('.jpg', '.png'))]

    for filename in files:
        # Извлекаем ID камеры (всё до первого подчёркивания)
        camera_id = filename.split('_')[0]

        img_path = os.path.join(SOURCE_FOLDER, filename)
        original_img = cv2.imread(img_path)
        if original_img is None:
            continue

        temp_img = original_img.copy()
        lines = []
        current_points = []

        cv2.namedWindow("Drawer")
        # Передаём original_img как param — нужен для чистой перерисовки
        cv2.setMouseCallback("Drawer", mouse_event, original_img)

        print(f"--- Разметка ID: {camera_id} ---")
        print("ЛКМ: добавить точку | ПКМ: завершить линию | S: сохранить | C: отмена линии | R: сброс всего | ESC: выход")

        while True:
            cv2.imshow("Drawer", temp_img)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('c'):
                # Отмена текущей незавершённой линии
                current_points = []
                temp_img = redraw(original_img)
                print("Линия отменена")

            elif key == ord('r'):
                # Полный сброс всех линий
                temp_img = original_img.copy()
                lines = []
                current_points = []
                print("Очищено всё")

            elif key == 13:
                # Enter — завершить текущую линию (альтернатива ПКМ)
                if len(current_points) >= 2:
                    lines.append(list(current_points))
                    current_points = []
                    temp_img = redraw(original_img)
                    print(f"Линия добавлена, всего: {len(lines)}")
                else:
                    print("Нужно минимум 2 точки")

            elif key == ord('s'):
                markup_path = os.path.join(MARKUP_FOLDER, f"{camera_id}.json")
                with open(markup_path, 'w') as f:
                    json.dump(lines, f)
                print(f"Сохранено {len(lines)} линий в {camera_id}.json")
                break

            elif key == 27:  # ESC
                cv2.destroyAllWindows()
                return

    cv2.destroyAllWindows()


if __name__ == "__main__":
    process_images()
