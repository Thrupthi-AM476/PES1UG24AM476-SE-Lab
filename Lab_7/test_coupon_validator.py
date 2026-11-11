
import math
from datetime import datetime

from hypothesis import given, strategies as st

from coupon_validator import (
    split_code,
    most_expensive,
    expiry_days
)


# Test 1: Coupon code fuzzing
@given(st.one_of(st.text(), st.none()))
def test_split_code_no_crash(s):
    result = split_code(s)

    if isinstance(s, str):
        parts = s.strip().upper().split("-")

        valid = (
            len(parts) == 2
            and bool(parts[0])
            and parts[1].isdigit()
        )

        if valid:
            assert result == (parts[0], int(parts[1]))
        else:
            assert result is None
    else:
        assert result is None


# Test 2: Price list fuzzing
@given(st.one_of(st.text(), st.none()))
def test_most_expensive_no_crash(s):
    result = most_expensive(s)

    if isinstance(s, str):
        try:
            values = [float(p.strip()) for p in s.split(",")]

            valid = (
                len(values) > 0
                and all(math.isfinite(v) and v >= 0 for v in values)
            )
        except (ValueError, OverflowError):
            valid = False
    else:
        valid = False

    if valid:
        assert result == max(values)
    else:
        assert result is None


# Test 3: Date fuzzing
@given(st.one_of(st.text(), st.none()))
def test_expiry_days_no_crash(s):
    result = expiry_days(s)

    if isinstance(s, str):
        try:
            parsed = datetime.strptime(s, "%Y-%m-%d")
            valid = parsed.strftime("%Y-%m-%d") == s
        except ValueError:
            valid = False
    else:
        valid = False

    if valid:
        expected = (
            (parsed.year - 2024) * 365
            + (parsed.month - 1) * 30
            + parsed.day
        )
        assert result == expected
    else:
        assert result is None
