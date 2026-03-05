"""
PDF Tax Return Generator

Creates a simplified 1040-style tax return form using reportlab.
Generates a professional-looking PDF with the calculated tax results.
"""

import os
import tempfile
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_RIGHT


# Colors
GREEN = HexColor("#1a5632")
LIGHT_GREEN = HexColor("#e8f5e9")
DARK = HexColor("#1a1a2e")
GRAY = HexColor("#5a6474")
LIGHT_GRAY = HexColor("#f0f0f0")
LINE_COLOR = HexColor("#cccccc")


def create_tax_return_pdf(result: dict, taxpayer_name: str = "Taxpayer",
                          ssn_last4: str = "XXXX") -> str:
    """
    Generate a simplified 1040-style tax return PDF.

    Args:
        result: Tax calculation result dict from tax_engine.calculate_tax().
        taxpayer_name: Name of the taxpayer.
        ssn_last4: Last 4 digits of SSN.

    Returns:
        Path to the generated PDF file.
    """
    # Create temp file
    fd, pdf_path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)

    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    # Header 
    # Green header bar
    c.setFillColor(GREEN)
    c.rect(0, height - 80, width, 80, fill=True, stroke=False)

    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 40, "Simplified Form 1040")
    c.setFont("Helvetica", 11)
    c.drawCentredString(width / 2, height - 58, "U.S. Individual Income Tax Return (Simplified) — 2024 Tax Year")
    c.setFont("Helvetica", 8)
    c.drawCentredString(width / 2, height - 72, "AI Tax Agent Prototype — For Demonstration Purposes Only")

    y = height - 110

    # Personal Info Section
    c.setFillColor(LIGHT_GREEN)
    c.rect(40, y - 50, width - 80, 50, fill=True, stroke=False)
    c.setStrokeColor(GREEN)
    c.rect(40, y - 50, width - 80, 50, fill=False, stroke=True)

    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(55, y - 18, "Taxpayer Name:")
    c.setFont("Helvetica", 10)
    c.drawString(160, y - 18, taxpayer_name)

    c.setFont("Helvetica-Bold", 10)
    c.drawString(350, y - 18, "SSN (last 4):")
    c.setFont("Helvetica", 10)
    c.drawString(440, y - 18, f"XXX-XX-{ssn_last4}")

    c.setFont("Helvetica-Bold", 10)
    c.drawString(55, y - 38, "Filing Status:")
    c.setFont("Helvetica", 10)
    c.drawString(160, y - 38, result["filing_status_label"])

    c.setFont("Helvetica-Bold", 10)
    c.drawString(350, y - 38, "Tax Year:")
    c.setFont("Helvetica", 10)
    c.drawString(440, y - 38, "2024")

    y -= 80

    # Helper: draw a labeled row
    def draw_row(y_pos, line_num, label, value, bold=False, highlight=False):
        if highlight:
            c.setFillColor(LIGHT_GREEN)
            c.rect(40, y_pos - 5, width - 80, 22, fill=True, stroke=False)

        c.setFillColor(GRAY)
        c.setFont("Helvetica", 9)
        c.drawString(50, y_pos, f"Line {line_num}")

        c.setFillColor(DARK)
        font = "Helvetica-Bold" if bold else "Helvetica"
        c.setFont(font, 10)
        c.drawString(100, y_pos, label)

        c.setFont(font, 10)
        c.drawRightString(width - 55, y_pos, value)

        # Dotted line
        c.setStrokeColor(LINE_COLOR)
        c.setDash(1, 2)
        text_width = c.stringWidth(label, font, 10)
        value_width = c.stringWidth(value, font, 10)
        c.line(105 + text_width + 5, y_pos - 2, width - 60 - value_width, y_pos - 2)
        c.setDash()

        return y_pos - 26

    # Section: Income
    c.setFillColor(GREEN)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Income")
    c.setStrokeColor(GREEN)
    c.line(50, y - 4, width - 50, y - 4)
    y -= 28

    y = draw_row(y, "1", "Wages, salaries, tips (W-2)",
                 f"${result['gross_income']:,.2f}")
    y = draw_row(y, "9", "Total income",
                 f"${result['gross_income']:,.2f}", bold=True, highlight=True)

    y -= 10

    # Section: Deductions
    c.setFillColor(GREEN)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Adjustments & Deductions")
    c.setStrokeColor(GREEN)
    c.line(50, y - 4, width - 50, y - 4)
    y -= 28

    deduction_label = (f"Standard deduction ({result['filing_status_label']})"
                       if result["deduction_type"] == "standard"
                       else "Itemized deductions")
    y = draw_row(y, "12", deduction_label,
                 f"${result['applied_deduction']:,.2f}")
    y = draw_row(y, "15", "Taxable income",
                 f"${result['taxable_income']:,.2f}", bold=True, highlight=True)

    y -= 10

    # Section: Tax Computation
    c.setFillColor(GREEN)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Tax Computation")
    c.setStrokeColor(GREEN)
    c.line(50, y - 4, width - 50, y - 4)
    y -= 28

    y = draw_row(y, "16", "Tax (from tax brackets)",
                 f"${result['tax_owed']:,.2f}")
    y = draw_row(y, "24", "Total tax",
                 f"${result['tax_owed']:,.2f}", bold=True, highlight=True)

    y -= 10

    # Section: Payments
    c.setFillColor(GREEN)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Payments")
    c.setStrokeColor(GREEN)
    c.line(50, y - 4, width - 50, y - 4)
    y -= 28

    y = draw_row(y, "25a", "Federal income tax withheld (W-2)",
                 f"${result['withholdings']:,.2f}")
    y = draw_row(y, "33", "Total payments",
                 f"${result['withholdings']:,.2f}", bold=True, highlight=True)

    y -= 10

    # Section: Refund or Amount Owed
    c.setFillColor(GREEN)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Refund or Amount You Owe")
    c.setStrokeColor(GREEN)
    c.line(50, y - 4, width - 50, y - 4)
    y -= 28

    if result["refund_or_owed"] == "refund":
        y = draw_row(y, "34", "Amount overpaid",
                     f"${result['balance']:,.2f}")
        y = draw_row(y, "35a", "Refund",
                     f"${result['balance']:,.2f}", bold=True, highlight=True)
    else:
        y = draw_row(y, "37", "Amount you owe",
                     f"${result['balance']:,.2f}", bold=True, highlight=True)

    y -= 10

    # Tax Rate Summary Box
    c.setFillColor(LIGHT_GREEN)
    c.roundRect(40, y - 60, width - 80, 55, 6, fill=True, stroke=False)
    c.setStrokeColor(GREEN)
    c.roundRect(40, y - 60, width - 80, 55, 6, fill=False, stroke=True)

    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(60, y - 22, f"Effective Tax Rate: {result['effective_rate']}%")
    c.drawString(300, y - 22, f"Marginal Tax Rate: {result['marginal_rate']}%")

    c.setFont("Helvetica", 9)
    c.setFillColor(GRAY)
    c.drawString(60, y - 42,
                 f"Generated by AI Tax Agent on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")

    y -= 85

    # Bracket Breakdown Table
    if y > 200 and result.get("bracket_breakdown"):
        c.setFillColor(GREEN)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, "Tax Bracket Breakdown")
        c.setStrokeColor(GREEN)
        c.line(50, y - 4, width - 50, y - 4)
        y -= 24

        # Table header
        c.setFillColor(GREEN)
        c.rect(40, y - 4, width - 80, 18, fill=True, stroke=False)
        c.setFillColor(HexColor("#ffffff"))
        c.setFont("Helvetica-Bold", 9)
        c.drawString(55, y, "Bracket Range")
        c.drawString(220, y, "Rate")
        c.drawString(310, y, "Income in Bracket")
        c.drawRightString(width - 55, y, "Tax")
        y -= 22

        for b in result["bracket_breakdown"]:
            c.setFillColor(DARK)
            c.setFont("Helvetica", 9)
            c.drawString(55, y, f"${b['range_low']:,.0f} — ${b['range_high']:,.0f}")
            c.drawString(220, y, f"{b['rate'] * 100:.0f}%")
            c.drawString(310, y, f"${b['income_in_bracket']:,.2f}")
            c.drawRightString(width - 55, y, f"${b['tax_in_bracket']:,.2f}")

            c.setStrokeColor(LINE_COLOR)
            c.line(50, y - 5, width - 50, y - 5)
            y -= 18

    # Disclaimer
    c.setFillColor(GRAY)
    c.setFont("Helvetica-Oblique", 7)
    c.drawCentredString(width / 2, 35,
                        "This is a simplified tax return generated by an AI prototype for demonstration purposes only.")
    c.drawCentredString(width / 2, 25,
                        "It is not a substitute for professional tax advice. Consult a CPA for your actual tax filing.")

    c.save()
    return pdf_path
