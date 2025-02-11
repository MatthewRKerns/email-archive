import sqlite3
from flask import Flask, render_template, send_from_directory
import os
from collections import defaultdict

app = Flask(__name__)

# Ensure the database and table exist
def init_db():
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

# Initialize database on startup
init_db()

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
       
