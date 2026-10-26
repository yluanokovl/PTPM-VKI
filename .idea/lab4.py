import unittest


class Converter:
    @staticmethod
    def do(x: float) -> int:

        if x >= 100.7:
            return 1000
        elif 0.0 < x < 100.7:
            return int(x)
        elif x == 0.0:
            raise ValueError("Значение x не может быть равным 0.0") #raise принудительно генерирует исключение
        elif -30.4 <= x < 0.0:
            return int(x) - 5
        else:  #x <= -30.5
            return -2000



class TestConverter(unittest.TestCase):

    # 1. Тесты для диапазона [100.7; +∞)
    def test_upper_bound_inclusive(self):
        self.assertEqual(Converter.do(100.7), 1000) #сравнивает результат работы функции с ожидаемым значением
        self.assertEqual(Converter.do(150.5), 1000) #принимает на вход вещественное число  и "округляет" в зависимости от условий
        self.assertEqual(Converter.do(1000.0), 1000)

    # 2. Тесты для диапазона (0; 100.7)
    def test_positive_range(self):
        self.assertEqual(Converter.do(100.6), 100)
        self.assertEqual(Converter.do(65.7), 65)
        self.assertEqual(Converter.do(0.1), 0)

    # 3. Тест на генерацию исключения при x == 0.0
    def test_zero_exception(self):
        with self.assertRaises(ValueError):
            Converter.do(0.0)

    # 4. Тесты для диапазона [-30.4; 0)
    def test_negative_range_close_to_zero(self):
        self.assertEqual(Converter.do(-0.1), -5)
        self.assertEqual(Converter.do(-15.3), -20)
        self.assertEqual(Converter.do(-30.4), -35)

    # 5. Тесты для диапазона (-∞; -30.5]
    def test_lower_bound_inclusive(self):
        self.assertEqual(Converter.do(-30.5), -2000)
        self.assertEqual(Converter.do(-94.5), -2000)
        self.assertEqual(Converter.do(-500.0), -2000)


if __name__ == '__main__':
    unittest.main(verbosity=2)