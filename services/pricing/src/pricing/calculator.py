"""Core pricing calculation logic."""

from __future__ import annotations


BASE_RATE = 100.0
AGE_FACTOR = 1.5
RISK_MULTIPLIERS = {
    "low": 1.0,
    "medium": 1.25,
    "high": 1.75,
}


def calculate_premium(age: int, risk_level: str) -> float:
    """Calculate an insurance premium.

    Args:
        age: Age of the insured person (must be >= 0).
        risk_level: One of 'low', 'medium', 'high'.

    Returns:
        Premium amount as a float.

    Raises:
        ValueError: If age is negative or risk_level is invalid.
    """
    if age < 0:
        raise ValueError(f"age must be >= 0, got {age}")
    if risk_level not in RISK_MULTIPLIERS:
        raise ValueError(
            f"risk_level must be one of {list(RISK_MULTIPLIERS)}, got '{risk_level}'"
        )
    multiplier = RISK_MULTIPLIERS[risk_level]
    return round(BASE_RATE + age * AGE_FACTOR * multiplier, 2)


def apply_discount(premium: float, discount_pct: float) -> float:
    """Apply a percentage discount to a premium.

    Args:
        premium: Base premium amount.
        discount_pct: Discount percentage (0–100).

    Returns:
        Discounted premium.

    Raises:
        ValueError: If discount_pct is outside [0, 100].
    """
    if not 0 <= discount_pct <= 100:
        raise ValueError(f"discount_pct must be in [0, 100], got {discount_pct}")
    return round(premium * (1 - discount_pct / 100), 2)
