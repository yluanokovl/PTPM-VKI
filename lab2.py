import math
import logging
import unittest
class TestCalculateTriangle(unittest.TestCase):

    # 1. Валидный разносторонний треугольник (классический египетский 3-4-5)
    def test_scalene_triangle_valid(self):
        t_type, coords = calculate_triangle("3", "4", "5")
        self.assertEqual(t_type, "разносторонний")
        # Проверяем, что координаты вписались в рамки 0..100
        for x, y in coords:
            self.assertTrue(0 <= x <= 100)
            self.assertTrue(0 <= y <= 100)

    # 2. Валидный равносторонний треугольник
    def test_equilateral_triangle_valid(self):
        t_type, coords = calculate_triangle("10", "10", "100")  # Ой, это тест на ошибку. Настоящий ниже:
        t_type, coords = calculate_triangle("60", "60", "60")
        self.assertEqual(t_type, "равносторонний")

    # 3. Валидный равнобедренный треугольник
    def test_isosceles_triangle_valid(self):
        t_type, coords = calculate_triangle("5", "5", "3")
        self.assertEqual(t_type, "равнобедренный")

    # 4. Нечисловые данные на входе (буквы)
    def test_invalid_string_input(self):
        t_type, coords = calculate_triangle("abc", "10", "10")
        self.assertEqual(t_type, "")
        self.assertEqual(coords, [(-2, -2), (-2, -2), (-2, -2)])

    # 5. Пустые строки на входе
    def test_empty_string_input(self):
        t_type, coords = calculate_triangle("", "5", "5")
        self.assertEqual(t_type, "")
        self.assertEqual(coords, [(-2, -2), (-2, -2), (-2, -2)])

    # 6. Одна из сторон равна нулю
    def test_zero_side(self):
        t_type, coords = calculate_triangle("0", "5", "5")
        self.assertEqual(t_type, "не треугольник")
        self.assertEqual(coords, [(-1, -1), (-1, -1), (-1, -1)])

    # 7. Одна из сторон отрицательная
    def test_negative_side(self):
        t_type, coords = calculate_triangle("5", "-5", "5")
        self.assertEqual(t_type, "не треугольник")
        self.assertEqual(coords, [(-1, -1), (-1, -1), (-1, -1)])

    # 8. Нарушение неравенства треугольника (одна сторона слишком велика)
    def test_invalid_triangle_inequality(self):
        t_type, coords = calculate_triangle("1", "1", "10")
        self.assertEqual(t_type, "не треугольник")
        self.assertEqual(coords, [(-1, -1), (-1, -1), (-1, -1)])

    # 9. Вырожденный треугольник (сумма двух сторон ровно равна третьей — отрезок)
    def test_degenerate_triangle(self):
        t_type, coords = calculate_triangle("5", "5", "10")
        self.assertEqual(t_type, "не треугольник")
        self.assertEqual(coords, [(-1, -1), (-1, -1), (-1, -1)])

    # 10. Проверка float-значений в виде строк (например, с точкой)
    def test_float_string_input(self):
        t_type, coords = calculate_triangle("3.5", "4.5", "5.5")
        self.assertEqual(t_type, "разносторонний")

    # 11. Проверка границ масштабирования (минимум одна координата должна коснуться 0 и 100)
    def test_bounding_box_edges(self):
        _, coords = calculate_triangle("30", "40", "50")
        all_x = [pt[0] for pt in coords]
        all_y = [pt[1] for pt in coords]

        # Так как масштаб идет по максимальной стороне, границы 0 и 100 должны быть достигнуты
        self.assertTrue(min(all_x) == 0 or min(all_y) == 0)
        self.assertTrue(max(all_x) == 100 or max(all_y) == 100)


if __name__ == "__main__":
    # Запуск юнит-тестов
    unittest.main()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s'
)


def calculate_triangle(str_a: str, str_b: str, str_c: str):
    """
    Вычисляет вид треугольника и координаты его вершин (0..100 px).
    """
    logging.info("Старт обработки входных данных.")
    logging.debug(f"Полученные строки: A='{str_a}', B='{str_b}', C='{str_c}'")

    # 1. Валидация типов данных
    try:
        a = float(str_a)
        b = float(str_b)
        c = float(str_c)
        logging.info("Входные данные успешно приведены к типу float.")
    except ValueError as e:
        logging.error(f"Ошибка приведения типов (нечисловые данные): {e}")
        return "", [(-2, -2), (-2, -2), (-2, -2)]

    # 2. Проверка на положительные числа и существование треугольника
    if a <= 0 or b <= 0 or c <= 0:
        logging.warning("Одна или несколько сторон меньше или равны нулю.")
        return "не треугольник", [(-1, -1), (-1, -1), (-1, -1)]

    if (a + b <= c) or (a + c <= b) or (b + c <= a):
        logging.warning("Нарушено неравенство треугольника.")
        return "не треугольник", [(-1, -1), (-1, -1), (-1, -1)]

    # 3. Определение вида треугольника
    if a == b == c:
        triangle_type = "равносторонний"
    elif a == b or b == c or a == c:
        triangle_type = "равнобедренный"
    else:
        triangle_type = "разносторонний"

    logging.info(f"Определен вид треугольника: {triangle_type}")

    # 4. Расчет координат вершин
    # Вершина 1: (0, 0)
    # Вершина 2: (c, 0) - лежит на оси X, длина стороны = c
    # Вершина 3: рассчет через угол Alpha (между сторонами b и c, напротив стороны a)
    try:
        cos_alpha = (b ** 2 + c ** 2 - a ** 2) / (2 * b * c)
        cos_alpha = max(-1.0, min(1.0, cos_alpha))
        sin_alpha = math.sqrt(1.0 - cos_alpha ** 2)

        x1, y1 = 0.0, 0.0
        x2, y2 = float(c), 0.0
        x3, y3 = b * cos_alpha, b * sin_alpha
    except Exception as e:
        logging.error(f"Непредвиденная математическая ошибка: {e}")
        return "не треугольник", [(-1, -1), (-1, -1), (-1, -1)]

    # 5. Масштабирование под поле 100x100 px с сохранением пропорций
    min_x = min(x1, x2, x3)
    max_x = max(x1, x2, x3)
    min_y = min(y1, y2, y3)
    max_y = max(y1, y2, y3)

    width = max_x - min_x
    height = max_y - min_y

    max_dim = max(width, height)
    scale = 100.0 / max_dim if max_dim > 0 else 1.0

    def fit(x, y):
        # Центрирование по меньшей стороне
        offset_x = (100.0 - width * scale) / 2
        offset_y = (100.0 - height * scale) / 2

        new_x = int(round((x - min_x) * scale + offset_x))
        new_y = int(round((y - min_y) * scale + offset_y))
        return new_x, new_y

    v1_res = fit(x1, y1)
    v2_res = fit(x2, y2)
    v3_res = fit(x3, y3)

    return triangle_type, [v1_res, v2_res, v3_res]