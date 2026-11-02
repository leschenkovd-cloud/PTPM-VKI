import unittest
import sys
import os

# Добавляем путь к исходному коду
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from delivery_service import calculate_delivery_cost


class TestDeliveryValidation(unittest.TestCase):
    """Тесты валидации входных параметров"""

    def test_weight_below_minimum_rejected(self):
        """Вес менее 0.1 кг должен отклоняться"""
        cost, date = calculate_delivery_cost(0.05, 100, "обычный")
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    def test_weight_above_maximum_rejected(self):
        """Вес более 50.0 кг должен отклоняться"""
        cost, date = calculate_delivery_cost(55.0, 100, "обычный")
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    def test_distance_below_minimum_rejected(self):
        """Дистанция менее 1 км должна отклоняться"""
        cost, date = calculate_delivery_cost(5.0, 0, "обычный")
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    def test_distance_above_maximum_rejected(self):
        """Дистанция более 5000 км должна отклоняться"""
        cost, date = calculate_delivery_cost(5.0, 5001, "обычный")
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    def test_invalid_package_type_rejected(self):
        """Недопустимый тип посылки должен отклоняться"""
        cost, date = calculate_delivery_cost(5.0, 100, "скоропортящийся")
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")


class TestDeliveryCostCalculation(unittest.TestCase):
    """Тесты расчета стоимости доставки"""

    def test_standard_delivery_base_cost(self):
        """Базовая стоимость для легкого обычного груза"""
        # 200 (база) + 100 * 5 (дистанция) = 700
        cost, date = calculate_delivery_cost(3.0, 100, "обычный")
        self.assertEqual(cost, 700)

    def test_medium_weight_multiplier_applied(self):
        """Вес от 5.0 до 19.9 кг должен увеличивать стоимость на 20%"""
        # 200 + 100*5 = 700. 700 * 1.2 = 840
        cost, date = calculate_delivery_cost(5.0, 100, "обычный")
        self.assertEqual(cost, 840)

    def test_heavy_weight_multiplier_applied(self):
        """Вес от 20.0 кг должен увеличивать стоимость на 50%"""
        # 200 + 100*5 = 700. 700 * 1.5 = 1050
        cost, date = calculate_delivery_cost(25.0, 100, "обычный")
        self.assertEqual(cost, 1050)

    def test_fragile_package_surcharge(self):
        """Хрупкий груз должен добавлять 300 руб к стоимости"""
        # (200 + 100*5) * 1.2 (вес 5кг) + 300 = 840 + 300 = 1140
        cost, date = calculate_delivery_cost(5.0, 100, "хрупкий")
        self.assertEqual(cost, 1140)

    def test_dangerous_package_surcharge(self):
        """Опасный груз должен добавлять 1000 руб к стоимости"""
        # (200 + 100*5) + 1000 = 1700
        cost, date = calculate_delivery_cost(3.0, 100, "опасный")
        self.assertEqual(cost, 1700)

    def test_express_delivery_increases_cost(self):
        """Экспресс-доставка должна УВЕЛИЧИВАТЬ стоимость (например, в 1.5 раза)"""
        # Базовая 700. Экспресс: 700 * 1.5 = 1050
        # (Этот тест УПАДЕТ на исходном коде, так как там стоит * 0.5)
        cost, date = calculate_delivery_cost(3.0, 100, "обычный", is_express=True)
        self.assertEqual(cost, 1050)


class TestDeliveryTimeCalculation(unittest.TestCase):
    """Тесты расчета сроков доставки"""

    def test_standard_delivery_time_calculation(self):
        """Стандартный расчет времени: дистанция // 500, минимум 1 день"""
        # 400 // 500 = 0 -> max(1, 0) = 1 день. Дата: 2026-09-04
        cost, date = calculate_delivery_cost(3.0, 400, "обычный")
        self.assertEqual(date, "2026-09-04")

    def test_express_delivery_minimum_one_day(self):
        """Экспресс-доставка не может быть осуществлена в тот же день (0 дней)"""
        # Базовое время для 400 км = 1 день.
        # Экспресс должен быть минимум 1 день, а не 1 // 2 = 0 дней.
        # (Этот тест УПАДЕТ на исходном коде, так как там дата останется 2026-09-03)
        cost, date = calculate_delivery_cost(3.0, 400, "обычный", is_express=True)
        self.assertEqual(date, "2026-09-04")  # Ожидаем минимум 1 день, даже для экспресса


if __name__ == '__main__':
    unittest.main(verbosity=2)