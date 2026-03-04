"""Unit tests for the pricing calculator."""

import pytest

from pricing.calculator import calculate_premium, apply_discount


class TestCalculatePremium:
    def test_low_risk_young(self):
        premium = calculate_premium(age=25, risk_level="low")
        assert premium == 137.5  # 100 + 25 * 1.5 * 1.0

    def test_medium_risk(self):
        premium = calculate_premium(age=30, risk_level="medium")
        assert premium == 156.25  # 100 + 30 * 1.5 * 1.25

    def test_high_risk(self):
        premium = calculate_premium(age=40, risk_level="high")
        assert premium == 205.0  # 100 + 40 * 1.5 * 1.75

    def test_zero_age(self):
        premium = calculate_premium(age=0, risk_level="low")
        assert premium == 100.0

    def test_negative_age_raises(self):
        with pytest.raises(ValueError, match="age must be"):
            calculate_premium(age=-1, risk_level="low")

    def test_invalid_risk_level_raises(self):
        with pytest.raises(ValueError, match="risk_level must be one of"):
            calculate_premium(age=30, risk_level="ultra")


class TestApplyDiscount:
    def test_no_discount(self):
        assert apply_discount(200.0, 0) == 200.0

    def test_fifty_percent_discount(self):
        assert apply_discount(200.0, 50) == 100.0

    def test_full_discount(self):
        assert apply_discount(200.0, 100) == 0.0

    def test_discount_out_of_range_raises(self):
        with pytest.raises(ValueError, match="discount_pct must be in"):
            apply_discount(200.0, 101)

    def test_negative_discount_raises(self):
        with pytest.raises(ValueError, match="discount_pct must be in"):
            apply_discount(200.0, -5)
