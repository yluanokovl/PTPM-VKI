
import datetime

MIN_WEIGHT = 0.1
MAX_WEIGHT = 50.0
MIN_DISTANCE = 1
MAX_DISTANCE = 5000

VALID_PACKAGE_TYPES = ("обычный", "хрупкий", "опасный")

BASE_COST = 200
COST_PER_KM = 5

WEIGHT_THRESHOLD_MEDIUM = 5.0
WEIGHT_THRESHOLD_HEAVY = 20.0
MEDIUM_WEIGHT_MULTIPLIER = 1.2
HEAVY_WEIGHT_MULTIPLIER = 1.5

TYPE_SURCHARGE = {
    "обычный": 0,
    "хрупкий": 300,
    "опасный": 1000,
}

EXPRESS_COST_MULTIPLIER = 0.5
EXPRESS_TIME_DIVISOR = 2

KM_PER_DAY = 500
MIN_DELIVERY_DAYS = 1

SEND_DATE = datetime.date(2026, 9, 3)
ERROR_RESULT = (-1, "0000-00-00")


def calculate_delivery_cost(
    weight: float,
    distance: int,
    package_type: str,
    is_express: bool = False,
) -> tuple:

    # 1. Валидация веса и дистанции
    if weight < MIN_WEIGHT or weight > MAX_WEIGHT:
        return ERROR_RESULT
    if distance < MIN_DISTANCE or distance > MAX_DISTANCE:
        return ERROR_RESULT

    # 2. Валидация типа
    if package_type not in VALID_PACKAGE_TYPES:
        return ERROR_RESULT

    # 3. Базовая стоимость
    total_cost = BASE_COST + distance * COST_PER_KM

    # 4. Весовой коэффициент
    if WEIGHT_THRESHOLD_MEDIUM < weight < WEIGHT_THRESHOLD_HEAVY:
        total_cost *= MEDIUM_WEIGHT_MULTIPLIER
    elif weight >= WEIGHT_THRESHOLD_HEAVY:
        total_cost *= HEAVY_WEIGHT_MULTIPLIER

    # 5. Надбавка за тип
    total_cost += TYPE_SURCHARGE[package_type]

    # 6. Экспресс-множитель
    if is_express:
        total_cost *= EXPRESS_COST_MULTIPLIER

    # 7. Срок доставки
    days_needed = max(MIN_DELIVERY_DAYS, distance // KM_PER_DAY)
    if is_express:
        days_needed //= EXPRESS_TIME_DIVISOR

    delivery_date = SEND_DATE + datetime.timedelta(days=days_needed)

    return int(total_cost), delivery_date.strftime("%Y-%m-%d")


# тесты

class TestWeightValidation:
    """Границы веса: [0.1; 50.0] кг."""

    def test_weight_below_minimum_is_rejected(self):
        assert calculate_delivery_cost(0.05, 100, "обычный") == ERROR_RESULT

    def test_weight_zero_is_rejected(self):
        assert calculate_delivery_cost(0, 100, "обычный") == ERROR_RESULT

    def test_weight_negative_is_rejected(self):
        assert calculate_delivery_cost(-1.0, 100, "обычный") == ERROR_RESULT

    def test_weight_above_maximum_is_rejected(self):
        assert calculate_delivery_cost(50.1, 100, "обычный") == ERROR_RESULT

    def test_weight_at_minimum_boundary_is_accepted(self):
        cost, _ = calculate_delivery_cost(0.1, 100, "обычный")
        assert cost == BASE_COST + 100 * COST_PER_KM

    def test_weight_at_maximum_boundary_is_accepted(self):
        cost, _ = calculate_delivery_cost(50.0, 100, "обычный")
        expected = int((BASE_COST + 100 * COST_PER_KM) * HEAVY_WEIGHT_MULTIPLIER)
        assert cost == expected


class TestDistanceValidation:
    """Границы дистанции: [1; 5000] км."""

    def test_distance_zero_is_rejected(self):
        assert calculate_delivery_cost(1.0, 0, "обычный") == ERROR_RESULT

    def test_distance_negative_is_rejected(self):
        assert calculate_delivery_cost(1.0, -10, "обычный") == ERROR_RESULT

    def test_distance_above_maximum_is_rejected(self):
        assert calculate_delivery_cost(1.0, 5001, "обычный") == ERROR_RESULT

    def test_distance_at_boundaries_is_accepted(self):
        assert calculate_delivery_cost(1.0, 1, "обычный")[0] > 0
        assert calculate_delivery_cost(1.0, 5000, "обычный")[0] > 0


class TestPackageTypeValidation:
    def test_valid_types_are_accepted(self, ptype):
        cost, _ = calculate_delivery_cost(1.0, 100, ptype)
        assert cost > 0

    def test_invalid_types_are_rejected(self, ptype):
        assert calculate_delivery_cost(1.0, 100, ptype) == ERROR_RESULT


class TestCostCalculation:

    def test_base_cost_for_light_package_short_distance(self):
        """1 кг, 10 км, обычный: 200 + 50 = 250."""
        cost, _ = calculate_delivery_cost(1.0, 10, "обычный")
        assert cost == 250

    def test_medium_weight_multiplier(self):
        """10 кг, 100 км: int(700 * 1.2) = 840."""
        cost, _ = calculate_delivery_cost(10.0, 100, "обычный")
        assert cost == int((BASE_COST + 500) * MEDIUM_WEIGHT_MULTIPLIER)

    def test_heavy_weight_multiplier(self):
        """25 кг, 100 км: int(700 * 1.5) = 1050."""
        cost, _ = calculate_delivery_cost(25.0, 100, "обычный")
        assert cost == int((BASE_COST + 500) * HEAVY_WEIGHT_MULTIPLIER)

    def test_boundary_weight_5kg_uses_base_rate(self):
        """Вес ровно 5 кг → коэффициент не применяется."""
        cost, _ = calculate_delivery_cost(5.0, 100, "обычный")
        assert cost == BASE_COST + 500

    def test_boundary_weight_20kg_uses_heavy_rate(self):
        """Вес ровно 20 кг → ×1.5."""
        cost, _ = calculate_delivery_cost(20.0, 100, "обычный")
        assert cost == int((BASE_COST + 500) * HEAVY_WEIGHT_MULTIPLIER)

    def test_type_surcharges(self, ptype):
        """Надбавка добавляется после весового коэффициента."""
        base = BASE_COST + 100 * COST_PER_KM
        cost, _ = calculate_delivery_cost(1.0, 100, ptype)
        assert cost == base + TYPE_SURCHARGE[ptype]

    def test_express_halves_cost(self):
        """Бизнес-правило из ТЗ: экспресс-множитель стоимости = 0.5."""
        normal, _ = calculate_delivery_cost(1.0, 100, "обычный", is_express=False)
        express, _ = calculate_delivery_cost(1.0, 100, "обычный", is_express=True)
        assert express == int(normal * EXPRESS_COST_MULTIPLIER)

    def test_cost_is_integer(self):
        cost, _ = calculate_delivery_cost(3.3, 77, "хрупкий")
        assert isinstance(cost, int)


class TestDeliveryDate:

    def test_minimum_one_day_for_short_distance(self):
        """Дистанция < 500 км → 1 день."""
        _, date = calculate_delivery_cost(1.0, 100, "обычный")
        expected = (SEND_DATE + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        assert date == expected

    def test_days_scale_with_distance(self):
        """1500 км → 1500 // 500 = 3 дня."""
        _, date = calculate_delivery_cost(1.0, 1500, "обычный")
        expected_days = 1500 // KM_PER_DAY
        expected = (SEND_DATE + datetime.timedelta(days=expected_days)).strftime("%Y-%m-%d")
        assert date == expected

    def test_rounding_down_for_partial_distance(self):
        """700 км → 700 // 500 = 1 день (округление вниз — как в коде)."""
        _, date = calculate_delivery_cost(1.0, 700, "обычный")
        expected = (SEND_DATE + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        assert date == expected

    def test_express_halves_delivery_days(self):
        """2000 км → 4 дня, экспресс → 4 // 2 = 2 дня."""
        _, date = calculate_delivery_cost(1.0, 2000, "обычный", is_express=True)
        expected_days = (2000 // KM_PER_DAY) // EXPRESS_TIME_DIVISOR
        expected = (SEND_DATE + datetime.timedelta(days=expected_days)).strftime("%Y-%m-%d")
        assert date == expected

    def test_date_format_is_iso(self):
        _, date = calculate_delivery_cost(1.0, 100, "обычный")
        assert len(date) == 10
        assert date[4] == "-" and date[7] == "-"
        datetime.date.fromisoformat(date)


class TestIntegration:

    def test_all_params_combined(self):
        """
        25 кг (×1.5), 5000 км, опасный (+1000), экспресс (×0.5).
        base = 200 + 25000 = 25200
        * 1.5 = 37800
        + 1000 = 38800
        * 0.5 = 19400
        дни = 5000 // 500 = 10, экспресс → 5
        """
        cost, date = calculate_delivery_cost(25.0, 5000, "опасный", is_express=True)
        assert cost == 19400
        expected_date = (SEND_DATE + datetime.timedelta(days=5)).strftime("%Y-%m-%d")
        assert date == expected_date

    def test_error_result_is_consistent_tuple(self):
        result = calculate_delivery_cost(100, 100, "обычный")
        assert result == ERROR_RESULT
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_success_result_is_consistent_tuple(self):
        result = calculate_delivery_cost(1.0, 100, "обычный")
        assert isinstance(result, tuple)
        assert isinstance(result[0], int)
        assert isinstance(result[1], str)

    def test_default_express_is_false(self):
        """is_express по умолчанию False."""
        without = calculate_delivery_cost(1.0, 100, "обычный")
        explicit = calculate_delivery_cost(1.0, 100, "обычный", is_express=False)
        assert without == explicit


# демо

if __name__ == "__main__":
    samples = [
        (1.0, 100, "обычный", False),
        (10.0, 100, "хрупкий", False),
        (25.0, 5000, "опасный", True),
        (100.0, 100, "обычный", False),
    ]
    for w, d, t, e in samples:
        cost, date = calculate_delivery_cost(w, d, t, e)
        print(f"weight={w:>5}, dist={d:>5}, type={t:<10}, express={e!s:<5} "
              f"→ ({cost}, {date!r})")