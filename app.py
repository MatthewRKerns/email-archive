import os
import psycopg2
from flask import Flask, render_template, send_from_directory
from collections import defaultdict

app = Flask(__name__)

# Get database URL from Render's environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Connect to PostgreSQL
conn = psycopg2.connect(DATABASE_URL)
c = conn.cursor()

# Ensure the emails table exists
c.execute("""
    CREATE TABLE IF NOT EXISTS emails (
        id SERIAL PRIMARY KEY,
        received_date TEXT,
        subject TEXT,
        filename TEXT
    )
""")
conn.commit()

@app.route("/")
def index():
    try:
        c.execute("SELECT received_date, subject, filename FROM emails ORDER BY received_date DESC")
        emails = c.fetchall()

        if not emails:
            print("📭 No emails found in database.")

        # Organize emails by month
        email_dict = defaultdict(list)
        for date, subject, filename in emails:
            month = date[:7]  # Extract YYYY-MM
            email_dict[month].append((date, subject, filename))

        return render_template("index.html", email_dict=email_dict)

    except psycopg2.Error as e:
        print(f"❌ Database query error: {e}")
        return "Internal Server Error", 500

@app.route("/email/<filename>")
def view_email(filename):
    return send_from_directory("emails", filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
