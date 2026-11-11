
import pytest

from coupon_validator import (
    coupon_discount,
    best_discount,
    is_expired
)


# WELCOME10 tests
def test_welcome10_new_user():
    assert coupon_discount("WELCOME10", 200, True, "mon") == 20


def test_welcome10_existing_user():
    assert coupon_discount("WELCOME10", 200, False, "mon") == 0


# WEEKEND20 tests
def test_weekend20_saturday_large_cart():
    assert coupon_discount("WEEKEND20", 600, True, "sat") == 120


def test_weekend20_sunday_large_cart():
    assert coupon_discount("WEEKEND20", 700, False, "sun") == 140


def test_weekend20_small_cart():
    assert coupon_discount("WEEKEND20", 300, False, "sat") == 50


def test_weekend20_weekday():
    assert coupon_discount("WEEKEND20", 600, True, "mon") == 0


# FLAT100 tests
def test_flat100_eligible_cart():
    assert coupon_discount("FLAT100", 500, False, "mon") == 100


def test_flat100_ineligible_cart():
    assert coupon_discount("FLAT100", 300, False, "mon") == 0


# Invalid and boundary inputs
def test_unknown_coupon():
    assert coupon_discount("INVALID", 500, True, "sat") == 0


def test_empty_cart():
    with pytest.raises(ValueError):
        coupon_discount("WELCOME10", 0, True, "mon")


def test_negative_cart():
    with pytest.raises(ValueError):
        coupon_discount("WELCOME10", -100, True, "mon")


# best_discount tests
def test_best_discount_multiple_coupons():
    result = best_discount(
        ["WELCOME10", "WEEKEND20", "FLAT100"],
        1000, True, "sat"
    )
    assert result == 200


def test_best_discount_no_coupons():
    assert best_discount([], 500, True, "mon") == 0


def test_best_discount_unknown_coupons():
    assert best_discount(["INVALID"], 500, True, "mon") == 0



def test_best_discount_applies_cap(monkeypatch):
    monkeypatch.setattr(
        "coupon_validator.coupon_discount",
        lambda *args: 500
    )

    result = best_discount(
        ["TEST"], 1000, True, "mon"
    )

    assert result == 400

# Expiry tests
def test_coupon_expired():
    assert is_expired(20, 5, 10) is True


def test_coupon_not_expired():
    assert is_expired(10, 5, 10) is False


def test_zero_validity():
    assert is_expired(10, 5, 0) is True


def test_negative_validity():
    assert is_expired(10, 5, -5) is True
