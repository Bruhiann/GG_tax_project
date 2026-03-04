"""
AI Tax Return Agent — Flask Application
-----------------------------------------
Handles tax input form, calculation, results display, and PDF download.
"""

import os
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session, send_file
)
from tax_engine import calculate_tax, FILING_STATUS_LABELS

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key-change-in-production")


@app.route("/")
def index():
    """Render the tax input form."""
    return render_template("index.html", filing_statuses=FILING_STATUS_LABELS)


@app.route("/calculate", methods=["POST"])
def calculate():
    """
    Process the tax form submission.
    Validates input, runs the tax engine, and stores results in the session.
    """
    try:
        gross_income = float(request.form.get("gross_income", 0))
        filing_status = request.form.get("filing_status", "single")
        deductions = float(request.form.get("deductions", 0))
        withholdings = float(request.form.get("withholdings", 0))

        if gross_income < 0 or deductions < 0 or withholdings < 0:
            flash("Values cannot be negative.", "error")
            return redirect(url_for("index"))

        if filing_status not in FILING_STATUS_LABELS:
            flash("Invalid filing status selected.", "error")
            return redirect(url_for("index"))

        result = calculate_tax(gross_income, filing_status, deductions, withholdings)

        session["tax_result"] = result
        session["user_name"] = request.form.get("taxpayer_name", "Taxpayer")
        session["ssn_last4"] = request.form.get("ssn_last4", "XXXX")

        return render_template("results.html", result=result,
                               taxpayer_name=session["user_name"])

    except (ValueError, TypeError) as e:
        flash(f"Invalid input: {e}", "error")
        return redirect(url_for("index"))


@app.route("/download")
def download_pdf():
    """Generate a simplified 1040-style PDF and send it as a download."""
    result = session.get("tax_result")
    if not result:
        flash("No tax calculation found. Please fill out the form first.", "error")
        return redirect(url_for("index"))

    from generate_pdf import create_tax_return_pdf

    pdf_path = create_tax_return_pdf(
        result,
        taxpayer_name=session.get("user_name", "Taxpayer"),
        ssn_last4=session.get("ssn_last4", "XXXX"),
    )
    return send_file(pdf_path, as_attachment=True,
                     download_name="tax_return_1040.pdf")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
