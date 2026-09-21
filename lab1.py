import math
import logging

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

    # 1. Валидация типов данных
    try:
        a = float(str_a)
        b = float(str_b)
        c = float(str_c)
        logging.info("Входные данные успешно приведены к типу float.")
    except ValueError as e:
        logging.error(f"Ошибка приведения типов (нечисловые данные): {e}")
        # При невалидных (нечисловых) данных возвращаем пустую строку и (-2, -2)
        return "", [(-2, -2), (-2, -2), (-2, -2)]

    # 2. Проверка на положительные числа и существование треугольника
    logging.debug(f"Проверка геометрических ограничений для: a={a}, b={b}, c={c}")
    if a <= 0 or b <= 0 or c <= 0:
        logging.warning("Одна или несколько сторон меньше или равны нулю.")
        return "не треугольник", [(-1, -1), (-1, -1), (-1, -1)]

    if (a + b <= c) or (a + c <= b) or (b + c <= a):
        logging.warning("Нарушено неравенство треугольника (сумма двух сторон меньше или равна третьей).")
        return "не треугольник", [(-1, -1), (-1, -1), (-1, -1)]

    # 3. Определение вида треугольника
    if a == b == c:
        triangle_type = "равносторонний"
    elif a == b or b == c or a == c:
        triangle_type = "равнобедренный"
    else:
        triangle_type = "разносторонний"

    logging.info(f"Определен вид треугольника: {triangle_type}")

    # 4. Расчет координат вершин (тригонометрия)
    # A (0, 0)
    # B (c, 0)
    # C: cos(Alpha) = (b^2 + c^2 - a^2) / (2 * b * c)
    logging.debug("Старт вычисления сырых координат вершин...")
    try:
        cos_alpha = (b ** 2 + c ** 2 - a ** 2) / (2 * b * c)
        # Ограничиваем из-за погрешности float
        cos_alpha = max(-1.0, min(1.0, cos_alpha))
        sin_alpha = math.sin(math.acos(cos_alpha))

        x1, y1 = 0.0, 0.0
        x2, y2 = float(c), 0.0
        x3, y3 = b * cos_alpha, b * sin_alpha

        logging.debug(f"Сырые координаты: V1({x1}, {y1}), V2({x2}, {y2}), V3({x3}, {y3})")
    except Exception as e:
        logging.error(f"Непредвиденная математическая ошибка: {e}")
        return "не треугольник", [(-1, -1), (-1, -1), (-1, -1)]

    # 5. Масштабирование под поле 100x100 px (Bounding Box)
    logging.debug("Масштабирование координат под поле 100x100 px.")
    min_x = min(x1, x2, x3)
    max_x = max(x1, x2, x3)
    min_y = min(y1, y2, y3)
    max_y = max(y1, y2, y3)

    width = max_x - min_x
    height = max_y - min_y

    # Находим максимальный размер, чтобы сохранить пропорции (aspect ratio)
    max_dim = max(width, height)

    # Коэффициент масштабирования (оставляем 100% заполнение по большей стороне)
    scale = 100.0 / max_dim if max_dim > 0 else 1.0

    # Сдвигаем к 0 и умножаем на scale, затем округляем до int
    def fit(x, y):
        # Центрирование внутри 100x100 по меньшей стороне (опционально, но делает отрисовку красивой)
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

#www

if __name__ == "__main__":
    print("-" * 50)
    print("Тест 1: Валидный разносторонний треугольник")
    res_type, res_coords = calculate_triangle("30", "40", "50")
    print(f"ИТОГ: Тип: {res_type}, Координаты: {res_coords}\n")

    print("-" * 50)
    print("Тест 2: Ошибочные числовые данные (не треугольник)")
    res_type, res_coords = calculate_triangle("10", "10", "100")
    print(f"ИТОГ: Тип: {res_type}, Координаты: {res_coords}\n")

    print("-" * 50)
    print("Тест 3: Невалидные (нечисловые) данные")
    res_type, res_coords = calculate_triangle("abc", "10", "10")
    print(f"ИТОГ: Тип: {res_type}, Координаты: {res_coords}\n")