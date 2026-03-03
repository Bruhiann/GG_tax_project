"""
Test suite for the tax calculation engine.
Verifies correctness across different income levels and filing statuses.
"""

import sys
sys.path.insert(0, "..")

from tax_engine import calculate_tax


def test_single_filer_50k():
    """Single filer earning $50,000 — common scenario."""
    result = calculate_tax(50000, "single")
    # Taxable: 50000 - 14600 = 35400
    # Tax: 11600 * 0.10 + (35400 - 11600) * 0.12 = 1160 + 2856 = 4016
    assert result["taxable_income"] == 35400
    assert result["tax_owed"] == 4016.0
    assert result["deduction_type"] == "standard"
    print(f"  PASS: Single/$50k -> taxable={result['taxable_income']}, tax={result['tax_owed']}")


def test_married_joint_120k():
    """Married filing jointly at $120,000."""
    result = calculate_tax(120000, "married_filing_jointly")
    # Taxable: 120000 - 29200 = 90800
    # Tax: 23200 * 0.10 + (90800 - 23200) * 0.12 = 2320 + 8112 = 10432
    assert result["taxable_income"] == 90800
    assert result["tax_owed"] == 10432.0
    print(f"  PASS: MFJ/$120k -> taxable={result['taxable_income']}, tax={result['tax_owed']}")


def test_head_of_household_75k():
    """Head of household at $75,000."""
    result = calculate_tax(75000, "head_of_household")
    # Taxable: 75000 - 21900 = 53100
    # Tax: 16550 * 0.10 + (53100 - 16550) * 0.12 = 1655 + 4386 = 6041
    assert result["taxable_income"] == 53100
    assert result["tax_owed"] == 6041.0
    print(f"  PASS: HoH/$75k -> taxable={result['taxable_income']}, tax={result['tax_owed']}")


def test_withholdings_refund():
    """Single filer with withholdings exceeding tax owed -> refund."""
    result = calculate_tax(50000, "single", withholdings=6000)
    assert result["refund_or_owed"] == "refund"
    assert result["balance"] == 1984.0  # 6000 - 4016
    print(f"  PASS: Refund scenario -> balance={result['balance']} ({result['refund_or_owed']})")


def test_withholdings_owed():
    """Single filer with low withholdings -> owes more."""
    result = calculate_tax(50000, "single", withholdings=2000)
    assert result["refund_or_owed"] == "owed"
    assert result["balance"] == 2016.0  # 4016 - 2000
    print(f"  PASS: Owed scenario -> balance={result['balance']} ({result['refund_or_owed']})")


def test_itemized_deduction():
    """Itemized deductions exceed standard deduction."""
    result = calculate_tax(100000, "single", deductions=20000)
    # Taxable: 100000 - 20000 = 80000
    assert result["taxable_income"] == 80000
    assert result["deduction_type"] == "itemized"
    print(f"  PASS: Itemized -> taxable={result['taxable_income']}, type={result['deduction_type']}")


def test_zero_income():
    """Zero income edge case."""
    result = calculate_tax(0, "single")
    assert result["taxable_income"] == 0
    assert result["tax_owed"] == 0
    print(f"  PASS: Zero income -> tax={result['tax_owed']}")


def test_high_income():
    """High income hitting the 37% bracket."""
    result = calculate_tax(800000, "single")
    assert result["marginal_rate"] == 37.0
    print(f"  PASS: High income -> marginal_rate={result['marginal_rate']}%, tax={result['tax_owed']}")


if __name__ == "__main__":
    print("Running tax engine tests...\n")
    test_single_filer_50k()
    test_married_joint_120k()
    test_head_of_household_75k()
    test_withholdings_refund()
    test_withholdings_owed()
    test_itemized_deduction()
    test_zero_income()
    test_high_income()
    print("\nAll tests passed!")
