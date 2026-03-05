"""
Tax Calculation Engine

Implements 2024 federal income tax logic including:
- Progressive tax brackets for all filing statuses
- Standard deductions
- Taxable income computation
- Effective tax rate calculation

"""

# 2024 Federal Tax Brackets
# Source: IRS Revenue Procedure 2023-34
TAX_BRACKETS = {
    "single": [
        (11600, 0.10),
        (47150, 0.12),
        (100525, 0.22),
        (191950, 0.24),
        (243725, 0.32),
        (609350, 0.35),
        (float("inf"), 0.37),
    ],
    "married_filing_jointly": [
        (23200, 0.10),
        (94300, 0.12),
        (201050, 0.22),
        (383900, 0.24),
        (487450, 0.32),
        (731200, 0.35),
        (float("inf"), 0.37),
    ],
    "married_filing_separately": [
        (11600, 0.10),
        (47150, 0.12),
        (100525, 0.22),
        (191950, 0.24),
        (243725, 0.32),
        (365600, 0.35),
        (float("inf"), 0.37),
    ],
    "head_of_household": [
        (16550, 0.10),
        (63100, 0.12),
        (100500, 0.22),
        (191950, 0.24),
        (243700, 0.32),
        (609350, 0.35),
        (float("inf"), 0.37),
    ],
}

# 2024 Standard Deductions
STANDARD_DEDUCTIONS = {
    "single": 14600,
    "married_filing_jointly": 29200,
    "married_filing_separately": 14600,
    "head_of_household": 21900,
}

# Human-readable labels for filing statuses
FILING_STATUS_LABELS = {
    "single": "Single",
    "married_filing_jointly": "Married Filing Jointly",
    "married_filing_separately": "Married Filing Separately",
    "head_of_household": "Head of Household",
}


def calculate_tax(gross_income: float, filing_status: str, deductions: float = 0.0,
                  withholdings: float = 0.0) -> dict:
    """
    Calculate federal income tax for a given tax scenario.

    Args:
        gross_income: Total gross income before deductions.
        filing_status: One of the keys in TAX_BRACKETS.
        deductions: Additional deductions beyond the standard deduction.
                    If less than the standard deduction, the standard deduction is used.
        withholdings: Total federal tax already withheld (from W-2, etc.).

    Returns:
        A dict with a full breakdown of the tax calculation.
    """
    if filing_status not in TAX_BRACKETS:
        raise ValueError(f"Invalid filing status: {filing_status}")

    if gross_income < 0:
        raise ValueError("Gross income cannot be negative")

    # Determine which deduction to use (standard vs. itemized)
    standard_deduction = STANDARD_DEDUCTIONS[filing_status]
    applied_deduction = max(standard_deduction, deductions)
    deduction_type = "itemized" if deductions > standard_deduction else "standard"

    # Calculate taxable income (floor at 0)
    taxable_income = max(0, gross_income - applied_deduction)

    # Apply progressive tax brackets
    brackets = TAX_BRACKETS[filing_status]
    tax_owed = 0.0
    bracket_breakdown = []
    prev_limit = 0

    for limit, rate in brackets:
        if taxable_income <= 0:
            break

        # How much income falls in this bracket
        bracket_income = min(taxable_income, limit) - prev_limit
        if bracket_income <= 0:
            prev_limit = limit
            continue

        bracket_tax = bracket_income * rate
        tax_owed += bracket_tax

        bracket_breakdown.append({
            "range_low": prev_limit,
            "range_high": min(limit, taxable_income),
            "rate": rate,
            "income_in_bracket": round(bracket_income, 2),
            "tax_in_bracket": round(bracket_tax, 2),
        })

        prev_limit = limit
        if taxable_income <= limit:
            break

    # Effective tax rate
    effective_rate = (tax_owed / gross_income * 100) if gross_income > 0 else 0

    # Refund or amount owed after withholdings
    balance = tax_owed - withholdings
    refund_or_owed = "refund" if balance < 0 else "owed"

    return {
        "gross_income": round(gross_income, 2),
        "filing_status": filing_status,
        "filing_status_label": FILING_STATUS_LABELS[filing_status],
        "standard_deduction": round(standard_deduction, 2),
        "applied_deduction": round(applied_deduction, 2),
        "deduction_type": deduction_type,
        "taxable_income": round(taxable_income, 2),
        "tax_owed": round(tax_owed, 2),
        "effective_rate": round(effective_rate, 2),
        "withholdings": round(withholdings, 2),
        "balance": round(abs(balance), 2),
        "refund_or_owed": refund_or_owed,
        "bracket_breakdown": bracket_breakdown,
        "marginal_rate": bracket_breakdown[-1]["rate"] * 100 if bracket_breakdown else 0,
    }
