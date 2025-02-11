import imaplib
import email
import os
import sqlite3
from email.header import decode_header
from datetime import datetime

EMAIL_HOST = "imap.gmail.com"  # Change for your provider
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

if not EMAIL_USER or not EMAIL_PASS:
    raise ValueError("❌ Missing EMAIL_USER or EMAIL_PASS. Check your GitHub Secrets.")

ARCHIVE_DIR = "emails"
os.makedirs(ARCHIVE_DIR, exist_ok=True)

# Connect to SQLite
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

def fetch_emails():
    # Connect to IMAP
    mail = imaplib.IMAP4_SSL(EMAIL_HOST)
    mail.login(EMAIL_USER, EMAIL_PASS)
    mail.select("inbox")

    status, messages = mail.search(None, 'FROM', 'natchezss.com')

    if messages[0] == b'':
        print("📭 No emails found matching 'natchezss.com'")
        return  # ✅ Now properly inside the function

    print(f"📩 Found {len(messages[0].split())} emails from natchezss.com")

    for num in messages[0].split():
        _, msg_data = mail.fetch(num, "(RFC822)")
        raw_email = msg_data[0][1]

        msg = email.message_from_bytes(raw_email)
        sender = msg.get("From")
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or "utf-8")

        print(f"📥 Processing Email - From: {sender}, Subject: {subject}")

    for num in messages[0].split():
        _, msg_data = mail.fetch(num, "(RFC822)")
        raw_email = msg_data[0][1]

        msg = email.message_from_bytes(raw_email)
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or "utf-8")

        date_tuple = email.utils.parsedate_tz(msg["Date"])
        received_date = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple)).strftime("%Y-%m-%d")

        filename = f"{received_date}_{num.decode()}.html"
        filepath = os.path.join(ARCHIVE_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"<h1>{subject}</h1><hr>")
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    f.write(part.get_payload(decode=True).decode("utf-8"))

        c.execute("INSERT INTO emails (received_date, subject, filename) VALUES (?, ?, ?)",
                  (received_date, subject, filename))
        conn.commit()

    mail.logout()

if __name__ == "__main__":
    fetch_emails()
