from flask import Flask, render_template, send_from_directory
import sqlite3
import os
from collections import defaultdict

app = Flask(__name__)

ARCHIVE_DIR = "emails"

@app.route("/")
def index():
    conn = sqlite3.connect("emails.db")
    c = conn.cursor()
    c.execute("SELECT received_date, subject, filename FROM emails ORDER BY received_date DESC")
    emails = c.fetchall()
    conn.close()

    # Organize emails by month
    email_dict = defaultdict(list)
    for date, subject, filename in emails:
        month = date[:7]  # Extract YYYY-MM
        email_dict[month].append((date, subject, filename))

    return render_template("index.html", email_dict=email_dict)

@app.route("/email/<filename>")
def view_email(filename):
    return send_from_directory(ARCHIVE_DIR, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
