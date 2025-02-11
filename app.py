import sqlite3
from flask import Flask, render_template, send_from_directory, jsonify
import os
from collections import defaultdict

app = Flask(__name__)

# Ensure the database and table exist
def init_db():
    try:
        conn = sqlite3.connect("emails.db")
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                received_date TEXT,
                subject TEXT,
                filename TEXT
            )
        """)
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully.")
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")

# Initialize database on startup
init_db()

ARCHIVE_DIR = "emails"

@app.route("/")
def index():
    try:
        conn = sqlite3.connect("emails.db")
        c = conn.cursor()
        c.execute("SELECT received_date, subject, filename FROM emails ORDER BY received_date DESC")
        emails = c.fetchall()
        conn.close()

        if not emails:
            print("📭 No emails found in database.")

        # Organize emails by month
        email_dict = defaultdict(list)
        for date, subject, filename in emails:
            month = date[:7]  # Extract YYYY-MM
            email_dict[month].append((date, subject, filename))

        return render_template("index.html", email_dict=email_dict)

    except sqlite3.Error as e:
        print(f"❌ Database query error: {e}")
        return jsonify({"error": "Database error", "details": str(e)}), 500  # Return JSON error response

@app.route("/email/<filename>")
def view_email(filename):
    return send_from_directory(ARCHIVE_DIR, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
