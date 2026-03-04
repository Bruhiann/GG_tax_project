"""
AI Tax Return Agent — Flask Application
-----------------------------------------
Handles the tax input form and serves templates.
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash

from tax_engine import FILING_STATUS_LABELS

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key-change-in-production")


@app.route("/")
def index():
    """Render the tax input form."""
    return render_template("index.html", filing_statuses=FILING_STATUS_LABELS)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
