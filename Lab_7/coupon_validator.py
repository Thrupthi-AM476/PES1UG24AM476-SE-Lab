
from datetime import datetime
import math


def split_code(code):
    if not isinstance(code, str):
        return None

    code = code.strip().upper()

    if code.count("-") != 1:
        return None

    prefix, value = code.split("-")

    if not prefix or not value.isdecimal():
        return None

    return prefix, int(value)


def most_expensive(prices_csv):
    if not isinstance(prices_csv, str):
        return None

    try:
        parts = prices_csv.split(",")

        if not parts or any(not p.strip() for p in parts):
            return None

        prices = [float(p.strip()) for p in parts]

        if any(
            not math.isfinite(price) or price < 0
            for price in prices
        ):
            return None

        return max(prices)

    except (ValueError, OverflowError):
        return None


def expiry_days(date_text):
    if not isinstance(date_text, str):
        return None

    try:
        parsed = datetime.strptime(date_text, "%Y-%m-%d")

        if parsed.strftime("%Y-%m-%d") != date_text:
            return None

        year = parsed.year
        month = parsed.month
        day = parsed.day

        return (
            (year - 2024) * 365
            + (month - 1) * 30
            + day
        )

    except ValueError:
        return None


def main():
    print("==== Running split_code ====")
    user_input = input("Enter a coupon code (e.g. save-20): ")
    result = split_code(user_input)
    print("Prefix and Value:", result)

    print("\n==== Running most_expensive ====")
    user_input = input(
        "Enter item prices as CSV (e.g. 199,49.5,320): "
    )
    result = most_expensive(user_input)
    print("Most Expensive Item:", result)

    print("\n==== Running expiry_days ====")
    user_input = input("Enter an expiry date as YYYY-MM-DD: ")
    result = expiry_days(user_input)
    print("Days Since 2024:", result)


if __name__ == "__main__":
    main()
