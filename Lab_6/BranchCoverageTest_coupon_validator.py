
import pytest

from coupon_validator import (
    coupon_discount,
    best_discount,
    is_expired
)


# 1. Cart validation branches
@pytest.mark.parametrize("cart_total", [0, -100])
def test_invalid_cart(cart_total):
    with pytest.raises(ValueError):
        coupon_discount(
            "WELCOME10", cart_total, True, "mon"
        )


def test_valid_cart():
    assert coupon_discount(
        "WELCOME10", 200, True, "mon"
    ) == 20


# 2. WELCOME10 branches
@pytest.mark.parametrize(
    "is_new_user, expected",
    [
        (True, 20),
        (False, 0)
    ]
)
def test_welcome10_branches(is_new_user, expected):
    assert coupon_discount(
        "WELCOME10", 200, is_new_user, "mon"
    ) == expected


# 3. WEEKEND20 branches
@pytest.mark.parametrize(
    "day, cart_total, expected",
    [
        ("sat", 600, 120),
        ("sun", 600, 120),
        ("sat", 300, 50),
        ("sun", 300, 50),
        ("mon", 600, 0),
        ("tue", 300, 0)
    ]
)
def test_weekend20_branches(day, cart_total, expected):
    assert coupon_discount(
        "WEEKEND20", cart_total, False, day
    ) == expected


# 4. FLAT100 branches
@pytest.mark.parametrize(
    "cart_total, expected",
    [
        (500, 100),
        (301, 100),
        (300, 0),
        (100, 0)
    ]
)
def test_flat100_branches(cart_total, expected):
    assert coupon_discount(
        "FLAT100", cart_total, False, "mon"
    ) == expected


# 5. Unknown coupon branch
def test_unknown_coupon():
    assert coupon_discount(
        "UNKNOWN", 500, True, "sat"
    ) == 0


# 6. best_discount loop and comparison branches
def test_best_discount_empty_list():
    assert best_discount([], 500, True, "mon") == 0


def test_best_discount_updates_best():
    assert best_discount(
        ["WELCOME10", "WEEKEND20"],
        1000, True, "sat"
    ) == 200


def test_best_discount_does_not_update_best():
    assert best_discount(
        ["UNKNOWN"],
        500, False, "mon"
    ) == 0


# 7. Discount cap branches
def test_best_discount_cap_branch(monkeypatch):
    monkeypatch.setattr(
        "coupon_validator.coupon_discount",
        lambda *args: 500
    )

    result = best_discount(
        ["TEST"], 1000, True, "mon"
    )

    assert result == 400


def test_best_discount_no_cap_branch():
    result = best_discount(
        ["WELCOME10"], 1000, True, "mon"
    )

    assert result == 100


# 8. Expiry branches

@pytest.mark.parametrize(
    "days_valid, expected",
    [
        (0, True),
        (-5, True),
        (10, True),
        (20, False)
    ]
)

def test_expiry_validity_branches(days_valid, expected):
    assert is_expired(
        20, 5, days_valid
    ) is expected


def test_expiry_elapsed_days_exceeds_validity():
    assert is_expired(20, 5, 10) is True


def test_expiry_elapsed_days_equal_validity():
    assert is_expired(15, 5, 10) is False


def test_expiry_elapsed_days_below_validity():
    assert is_expired(10, 5, 10) is False
