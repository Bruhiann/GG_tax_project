"""
AI Tax Return Agent — Flask Application
-----------------------------------------
Initial setup with basic Flask server.
"""

from flask import Flask

app = Flask(__name__)
app.secret_key = "dev-key-change-in-production"


@app.route("/")
def index():
    return "<h1>AI Tax Agent</h1><p>Coming soon...</p>"


if __name__ == "__main__":
    app.run(debug=True, port=5000)
