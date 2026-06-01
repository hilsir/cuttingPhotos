import json
from pathlib import Path

# этот костыль сгенерирован - работает
class ShelfSorter:
    def __init__(self, markup_folder: str):
        self.markup_folder = Path(markup_folder)

    def _load_lines(self, camera_id: str):
        markup_path = self.markup_folder / f"{camera_id}.json"
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

    def resolve_shelf_path(self, output_path: str, image_path: str, cx: int, cy: int) -> str:
        # ID камеры — часть имени файла до первого подчёркивания (без расширения)
        camera_id = Path(image_path).stem.split('_')[0]
        lines = self._load_lines(camera_id)

        if lines is None:
            return output_path

        lines_above = sum(1 for line in lines if self._y_at_x(line, cx) < cy)

        # Товар ниже всех линий — неопознанная полка
        if lines_above >= len(lines):
            shelf_path = Path(output_path) / "неопознанная полка"
        else:
            shelf_path = Path(output_path) / f"полка{lines_above + 1}"
        shelf_path.mkdir(parents=True, exist_ok=True)
        return str(shelf_path)
