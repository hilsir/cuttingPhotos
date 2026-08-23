import json
from pathlib import Path

# этот костыль сгенерирован - работает
class ShelfSorter:
    def __init__(self, markup_folder: str, data_router_path: str):
        self.markup_folder = Path(markup_folder)
        self.racks_by_image = self._load_data_router(Path(data_router_path))

    @staticmethod
    def _load_data_router(data_router_path: Path):
        if not data_router_path.exists():
            return {}
        with open(data_router_path) as f:
            data = json.load(f)
        return data.get("images", {})

    def _load_lines(self, rack_name: str):
        markup_path = self.markup_folder / f"{rack_name}.json"
        if not markup_path.exists():
            return None
        with open(markup_path) as f:
            return json.load(f)

    @staticmethod
    def _y_at_x(line: list, x: int) -> float:
        # Интерполирует Y полилинии при заданном X
        if x <= line[0][0]:
            return line[0][1]
        if x >= line[-1][0]:
            return line[-1][1]
        for i in range(len(line) - 1):
            x1, y1 = line[i]
            x2, y2 = line[i + 1]
            if x1 <= x <= x2:
                t = (x - x1) / (x2 - x1)
                return y1 + t * (y2 - y1)
        return line[-1][1]

    @staticmethod
    def _x_range(lines: list):
        # Стеллажи на фото стоят слева направо - берём общий диапазон X разметки
        xs = [point[0] for line in lines for point in line]
        return min(xs), max(xs)

    def _resolve_rack(self, camera_id: str, cx: int):
        rack_names = self.racks_by_image.get(camera_id)
        if not rack_names:
            return None, None

        # Если товар не попал ни в один диапазон - берём ближайший стеллаж
        nearest_name, nearest_lines, nearest_dist = None, None, None

        for rack_name in rack_names:
            lines = self._load_lines(rack_name)
            if not lines:
                continue

            x_min, x_max = self._x_range(lines)
            if x_min <= cx <= x_max:
                return rack_name, lines

            dist = (x_min - cx) if cx < x_min else (cx - x_max)
            if nearest_dist is None or dist < nearest_dist:
                nearest_name, nearest_lines, nearest_dist = rack_name, lines, dist

        return nearest_name, nearest_lines

    def resolve_shelf_path(self, output_path: str, image_path: str, cx: int, cy: int) -> str:
        # ID берём из имени папки с изображением, а не из имени файла
        # На сервере файлы называются по IP камеры, папка — по продукту
        camera_id = Path(image_path).parent.name
        rack_name, lines = self._resolve_rack(camera_id, cx)

        if lines is None:
            return output_path

        rack_path = Path(output_path) / rack_name

        lines_above = sum(1 for line in lines if self._y_at_x(line, cx) < cy)

        # Товар ниже всех линий — неопознанная полка
        if lines_above >= len(lines):
            shelf_path = rack_path / "неопознанная полка"
        else:
            shelf_path = rack_path / f"полка{lines_above + 1}"
        shelf_path.mkdir(parents=True, exist_ok=True)
        return str(shelf_path)
