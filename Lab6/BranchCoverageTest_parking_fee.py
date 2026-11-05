import pytest
from parking_fee import parking_fee, find_slot, monthly_pass


# ---------- parking_fee: validation branches ----------
def test_unknown_vehicle():
    with pytest.raises(ValueError, match="unknown vehicle"):
        parking_fee("bus", 60, False, False)


def test_negative_duration():
    with pytest.raises(ValueError, match="invalid duration"):
        parking_fee("car", -1, False, False)


def test_zero_minutes_is_free():
    assert parking_fee("car", 0, False, False) == 0


# ---------- parking_fee: grace period boundary (minutes <= 30) ----------
def test_free_short_stay():
    assert parking_fee("car", 20, False, False) == 0


def test_boundary_30_minutes_free():
    assert parking_fee("truck", 30, False, False) == 0


def test_boundary_31_minutes_charged():
    assert parking_fee("car", 31, False, False) == 30


# ---------- parking_fee: minutes % 60 branch ----------
def test_exact_hour_no_roundup():
    assert parking_fee("car", 60, False, False) == 30


def test_one_minute_over_hour_rounds_up():
    assert parking_fee("car", 61, False, False) == 60


def test_bike_partial_hour():
    assert parking_fee("bike", 90, False, False) == 20


def test_truck_exact_two_hours():
    assert parking_fee("truck", 120, False, False) == 120


# ---------- parking_fee: EV branch (true/false, truck exclusion) ----------
def test_ev_car_discount():
    assert parking_fee("car", 61, True, False) == 30


def test_ev_bike_discount():
    assert parking_fee("bike", 60, True, False) == 5


def test_ev_truck_no_discount():
    assert parking_fee("truck", 61, True, False) == 120


def test_non_ev_no_discount():
    assert parking_fee("car", 61, False, False) == 60


# ---------- parking_fee: lost ticket branch ----------
def test_lost_ticket_adds_penalty():
    assert parking_fee("car", 20, False, True) == 200


def test_lost_ticket_with_ev_and_charge():
    # 31 min bike -> 10, EV -> 5, lost ticket -> 205
    assert parking_fee("bike", 31, True, True) == 205


def test_ticket_not_lost():
    assert parking_fee("bike", 60, False, False) == 10


# ---------- find_slot: every branch ----------
def test_slot_full_zero():
    assert find_slot("car", 0, False) == "full"


def test_slot_full_negative():
    assert find_slot("car", -1, True) == "full"


def test_slot_disabled():
    assert find_slot("car", 3, True) == "ground floor"


def test_slot_truck():
    assert find_slot("truck", 3, False) == "basement"


def test_any_floor():
    assert find_slot("car", 5, False) == "any floor"


def test_slot_bike_any_floor():
    assert find_slot("bike", 1, False) == "any floor"


def test_disabled_truck_gets_ground_floor():
    # disabled check comes before the truck check
    assert find_slot("truck", 2, True) == "ground floor"


# ---------- monthly_pass: every branch ----------
def test_pass_bike_non_resident():
    assert monthly_pass("bike", False) == 500


def test_pass_bike_resident():
    assert monthly_pass("bike", True) == 400


def test_pass_car_non_resident():
    assert monthly_pass("car", False) == 1500


def test_pass_car_resident():
    assert monthly_pass("car", True) == 1200


def test_pass_truck_not_allowed():
    with pytest.raises(ValueError, match="no pass"):
        monthly_pass("truck", True)
