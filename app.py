"""
AI Tax Return Agent — Flask Application
"""

import os
import json
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session, jsonify, send_file
)
from tax_engine import calculate_tax, FILING_STATUS_LABELS

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key-change-in-production")


# ─── Routes ───────────────────────────────────────────────────────────────────

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
        # Pull and validate form data
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

        # Run the tax engine
        result = calculate_tax(gross_income, filing_status, deductions, withholdings)

        # Store in session so results and PDF download can access it
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

    # Generate PDF (imported here to keep startup fast)
    from generate_pdf import create_tax_return_pdf

    pdf_path = create_tax_return_pdf(
        result,
        taxpayer_name=session.get("user_name", "Taxpayer"),
        ssn_last4=session.get("ssn_last4", "XXXX"),
    )
    return send_file(pdf_path, as_attachment=True,
                     download_name="tax_return_1040.pdf")


@app.route("/chat")
def chat():
    """Render the AI tax assistant chat page."""
    return render_template("chat.html")


@app.route("/chat/ask", methods=["POST"])
def chat_ask():
    """
    API endpoint for the AI chat assistant.
    Sends user message to Claude API and returns the response.
    Requires ANTHROPIC_API_KEY environment variable.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return jsonify({
            "response": "AI chat is not configured. Set the ANTHROPIC_API_KEY "
                        "environment variable to enable this feature."
        })

    user_message = request.json.get("message", "")
    if not user_message.strip():
        return jsonify({"response": "Please enter a question."})

    # Include current tax result context if available
    tax_context = ""
    if session.get("tax_result"):
        r = session["tax_result"]
        tax_context = (
            f"\n\nThe user has already calculated their taxes with these results: "
            f"Gross income: ${r['gross_income']:,.2f}, "
            f"Filing status: {r['filing_status_label']}, "
            f"Taxable income: ${r['taxable_income']:,.2f}, "
            f"Tax owed: ${r['tax_owed']:,.2f}, "
            f"Effective rate: {r['effective_rate']}%. "
            f"After withholdings: {'Refund' if r['refund_or_owed'] == 'refund' else 'Amount owed'} "
            f"of ${r['balance']:,.2f}."
        )

    try:
        import requests as req

        response = req.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1000,
                "system": (
                    "You are a helpful tax assistant for a simplified tax preparation tool. "
                    "Answer questions about federal income tax clearly and concisely. "
                    "Always remind users that this is a simplified tool and they should "
                    "consult a tax professional for complex situations. "
                    "Keep responses under 200 words." + tax_context
                ),
                "messages": [{"role": "user", "content": user_message}],
            },
        )

        data = response.json()
        assistant_text = data.get("content", [{}])[0].get("text", "Sorry, I couldn't generate a response.")
        return jsonify({"response": assistant_text})

    except Exception as e:
        return jsonify({"response": f"Error connecting to AI service: {str(e)}"})


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=5000)
