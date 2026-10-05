import math
import logging
import unittest


# Настройка логирования: выводим уровень, имя функции и сообщение
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s'
)


def calculate_triangle(str_a: str, str_b: str, str_c: str):
    """
    Вычисляет вид треугольника и координаты его вершин (0..100 px).
    """
    logging.info("Старт обработки входных данных.")
    logging.debug(f"Полученные строки: A='{str_a}', B='{str_b}', C='{str_c}'")

    # 1. Валидация типов данных (ValueError + TypeError)
    try:
        a = float(str_a)
        b = float(str_b)
        c = float(str_c)
    except (ValueError, TypeError) as e:
        logging.error(f"Ошибка приведения типов: {e}")
        return "", [(-2, -2), (-2, -2), (-2, -2)]

    # 1.1 Проверка на nan / inf
    if not (math.isfinite(a) and math.isfinite(b) and math.isfinite(c)):
        logging.error("Обнаружены неконечные значения (nan/inf).")
        return "", [(-2, -2), (-2, -2), (-2, -2)]

    logging.info("Входные данные успешно приведены к типу float.")

    # 2. Проверка на положительные числа и существование треугольника
    if a <= 0 or b <= 0 or c <= 0:
        logging.warning("Одна или несколько сторон меньше или равны нулю.")
        return "не треугольник", [(-1, -1), (-1, -1), (-1, -1)]

    if (a + b <= c) or (a + c <= b) or (b + c <= a):
        logging.warning("Нарушено неравенство треугольника.")
        return "не треугольник", [(-1, -1), (-1, -1), (-1, -1)]

    # 3. Определение вида треугольника (с math.isclose для устойчивости)
    eps = 1e-9
    if math.isclose(a, b, rel_tol=eps) and math.isclose(b, c, rel_tol=eps):
        triangle_type = "равносторонний"
    elif (math.isclose(a, b, rel_tol=eps)
          or math.isclose(b, c, rel_tol=eps)
          or math.isclose(a, c, rel_tol=eps)):
        triangle_type = "равнобедренный"
    else:
        triangle_type = "разносторонний"

    logging.info(f"Определен вид треугольника: {triangle_type}")

    # 4. Расчет координат вершин
    try:
        cos_alpha = (b ** 2 + c ** 2 - a ** 2) / (2 * b * c)
        cos_alpha = max(-1.0, min(1.0, cos_alpha))
        sin_alpha = math.sin(math.acos(cos_alpha))

        x1, y1 = 0.0, 0.0
        x2, y2 = float(c), 0.0
        x3, y3 = b * cos_alpha, b * sin_alpha
    except Exception as e:
        logging.error(f"Непредвиденная математическая ошибка: {e}")
        return "не треугольник", [(-1, -1), (-1, -1), (-1, -1)]

    # 5. Масштабирование под поле 100x100 px
    min_x = min(x1, x2, x3)
    max_x = max(x1, x2, x3)
    min_y = min(y1, y2, y3)
    max_y = max(y1, y2, y3)

    width = max_x - min_x
    height = max_y - min_y
    max_dim = max(width, height)

    scale = 100.0 / max_dim if max_dim > 0 else 1.0

    def fit(x, y):
        offset_x = (100.0 - width * scale) / 2
        offset_y = (100.0 - height * scale) / 2
        new_x = int(round((x - min_x) * scale + offset_x))
        new_y = int(round((y - min_y) * scale + offset_y))
        return new_x, new_y

    v1_res = fit(x1, y1)
    v2_res = fit(x2, y2)
    v3_res = fit(x3, y3)

    coordinates = [v1_res, v2_res, v3_res]
    logging.info(f"Вычисления успешно завершены. Результат: {coordinates}")

    return triangle_type, coordinates


# ТЕСТЫ
class TestCalculateTriangle(unittest.TestCase):

    # ---------- 1. Валидация входных данных ----------

    def test_01_non_numeric_returns_empty_string_and_minus_two(self):
        """Нечисловые данные → пустая строка и точки (-2,-2)."""
        t, coords = calculate_triangle("abc", "10", "10")
        self.assertEqual(t, "")
        self.assertEqual(coords, [(-2, -2), (-2, -2), (-2, -2)])

    def test_02_empty_string_returns_empty(self):
        """Пустая строка → ошибка типа данных."""
        t, coords = calculate_triangle("", "5", "5")
        self.assertEqual(t, "")
        self.assertEqual(coords, [(-2, -2)] * 3)

    def test_03_none_returns_empty(self):
        """None → TypeError должен быть перехвачен."""
        t, coords = calculate_triangle(None, "5", "5")
        self.assertEqual(t, "")
        self.assertEqual(coords, [(-2, -2)] * 3)

    def test_04_nan_returns_empty(self):
        """nan не должен проходить валидацию."""
        t, coords = calculate_triangle("nan", "5", "5")
        self.assertEqual(t, "")
        self.assertEqual(coords, [(-2, -2)] * 3)

    def test_05_inf_returns_empty(self):
        """inf не должен проходить валидацию."""
        t, coords = calculate_triangle("inf", "5", "5")
        self.assertEqual(t, "")
        self.assertEqual(coords, [(-2, -2)] * 3)

    def test_06_negative_side(self):
        """Отрицательная сторона → не треугольник."""
        t, coords = calculate_triangle("-3", "4", "5")
        self.assertEqual(t, "не треугольник")
        self.assertEqual(coords, [(-1, -1)] * 3)

    def test_07_zero_side(self):
        """Нулевая сторона → не треугольник."""
        t, coords = calculate_triangle("0", "4", "5")
        self.assertEqual(t, "не треугольник")
        self.assertEqual(coords, [(-1, -1)] * 3)

    # ---------- 2. Неравенство треугольника ----------

    def test_08_violates_inequality_a_plus_b(self):
        """a + b < c → не треугольник."""
        t, coords = calculate_triangle("3", "4", "100")
        self.assertEqual(t, "не треугольник")

    def test_09_violates_inequality_a_plus_c(self):
        """a + c < b → не треугольник."""
        t, coords = calculate_triangle("3", "100", "4")
        self.assertEqual(t, "не треугольник")

    def test_10_violates_inequality_b_plus_c(self):
        """b + c < a → не треугольник."""
        t, coords = calculate_triangle("100", "3", "4")
        self.assertEqual(t, "не треугольник")

    def test_11_degenerate_triangle_equal_sum(self):
        """a + b == c → вырожденный, не треугольник."""
        t, coords = calculate_triangle("3", "4", "7")
        self.assertEqual(t, "не треугольник")

    # ---------- 3. Определение типа ----------

    def test_12_equilateral(self):
        """Равносторонний треугольник."""
        t, _ = calculate_triangle("10", "10", "10")
        self.assertEqual(t, "равносторонний")

    def test_13_isosceles_ab(self):
        """Равнобедренный: a == b."""
        t, _ = calculate_triangle("5", "5", "6")
        self.assertEqual(t, "равнобедренный")

    def test_14_isosceles_bc(self):
        """Равнобедренный: b == c."""
        t, _ = calculate_triangle("6", "5", "5")
        self.assertEqual(t, "равнобедренный")

    def test_15_isosceles_ac(self):
        """Равнобедренный: a == c."""
        t, _ = calculate_triangle("5", "6", "5")
        self.assertEqual(t, "равнобедренный")

    def test_16_scalene(self):
        """Разносторонний треугольник."""
        t, _ = calculate_triangle("3", "4", "5")
        self.assertEqual(t, "разносторонний")

    def test_17_equilateral_float_artifact(self):
        """Почти равные стороны из-за float-погрешности → равносторонний."""
        t, _ = calculate_triangle("3", "3", "3.0000000000000004")
        self.assertEqual(t, "равносторонний")

    # ---------- 4. Координаты ----------

    def test_18_coordinates_within_bounds(self):
        """Все координаты в диапазоне [0, 100]."""
        _, coords = calculate_triangle("3", "4", "5")
        for (x, y) in coords:
            self.assertGreaterEqual(x, 0)
            self.assertLessEqual(x, 100)
            self.assertGreaterEqual(y, 0)
            self.assertLessEqual(y, 100)

    def test_19_three_distinct_points(self):
        """Три вершины не совпадают."""
        _, coords = calculate_triangle("3", "4", "5")
        self.assertEqual(len(set(coords)), 3)

    def test_20_bbox_fills_one_axis(self):
        """Одна из осей должна занимать 100 px."""
        _, coords = calculate_triangle("3", "4", "5")
        xs = [p[0] for p in coords]
        ys = [p[1] for p in coords]
        self.assertEqual(max(max(xs) - min(xs), max(ys) - min(ys)), 100)

    def test_21_equilateral_symmetric(self):
        """Равносторонний треугольник симметричен относительно центра."""
        _, coords = calculate_triangle("10", "10", "10")
        top = min(coords, key=lambda p: p[1])  # минимальный Y = верх
        bottom_points = [p for p in coords if p != top]
        if len(bottom_points) == 2:
            mid_x = (bottom_points[0][0] + bottom_points[1][0]) / 2
            self.assertAlmostEqual(top[0], mid_x, delta=1)

    def test_22_large_values_scaled(self):
        """Очень большие стороны → всё равно 0..100."""
        _, coords = calculate_triangle("10000", "10000", "10000")
        for (x, y) in coords:
            self.assertTrue(0 <= x <= 100 and 0 <= y <= 100)

    def test_23_small_values_scaled(self):
        """Очень маленькие стороны → масштабируются."""
        _, coords = calculate_triangle("0.001", "0.001", "0.001")
        for (x, y) in coords:
            self.assertTrue(0 <= x <= 100 and 0 <= y <= 100)
        xs = [p[0] for p in coords]
        ys = [p[1] for p in coords]
        self.assertEqual(max(max(xs) - min(xs), max(ys) - min(ys)), 100)



if __name__ == "__main__":
    # Демонстрация работы функции
    print("ДЕМОНСТРАЦИЯ РАБОТЫ ФУНКЦИИ")
    for args in [("30", "40", "50"), ("10", "10", "100"), ("abc", "10", "10")]:
        t, coords = calculate_triangle(*args)
        print(f"calculate_triangle{args} -> Тип: {t!r}, Координаты: {coords}")
    print()

    # Запуск юнит-тестов
    print("ЗАПУСК ЮНИТ-ТЕСТОВ")
    unittest.main(argv=["first-arg-is-ignored"], verbosity=2, exit=False)