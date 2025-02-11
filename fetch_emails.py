import os
import imaplib
import email
import psycopg2
import sqlite3
from email.header import decode_header
from datetime import datetime

# Email Credentials
EMAIL_HOST = "imap.gmail.com"  
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

# Manually set DATABASE_URL (Replace with your actual Internal Database URL from Render)
DATABASE_URL = "postgresql://emailarchive_user:0PWYwwVi0vGOiCe64ofQDEQ6W63sJFhV@dpg-culbi55svqrc73cb9kq0-a/emailarchive"

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

# Archive Directory
ARCHIVE_DIR = "emails"
os.makedirs(ARCHIVE_DIR, exist_ok=True)

def fetch_emails():
    print("📡 Connecting to IMAP Server...")
    mail = imaplib.IMAP4_SSL(EMAIL_HOST)

    try:
        mail.login(EMAIL_USER, EMAIL_PASS)
        print("✅ Logged into Email Server!")
    except imaplib.IMAP4.error:
        print("❌ Authentication Failed! Check EMAIL_USER and EMAIL_PASS.")
        return

    mail.select("inbox")

    # Fetch emails from any subdomain of natchezss.com
    status, messages = mail.search(None, 'FROM', 'natchezss.com')

    if messages[0] == b'':
        print("📭 No new emails found from @natchezss.com.")
        return

    print(f"📩 Found {len(messages[0].split())} emails from natchezss.com")

    for num in messages[0].split():
        _, msg_data = mail.fetch(num, "(RFC822)")
        raw_email = msg_data[0][1]

        msg = email.message_from_bytes(raw_email)
        
        # Get sender info
        sender = msg.get("From")

        # Decode subject
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or "utf-8")

        # Extract received date
        date_tuple = email.utils.parsedate_tz(msg["Date"])
        received_date = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple)).strftime("%Y-%m-%d")

        # Generate unique filename
        filename = f"{received_date}_{num.decode()}.html"
        filepath = os.path.join(ARCHIVE_DIR, filename)

        # Save email content as HTML
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"<h1>{subject}</h1><hr>")
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    f.write(part.get_payload(decode=True).decode("utf-8"))

        # Save email info to PostgreSQL
        try:
            print(f"📝 Saving to database: {received_date}, {subject}, {filename}")
            c.execute("INSERT INTO emails (received_date, subject, filename) VALUES (%s, %s, %s)",
                      (received_date, subject, filename))
            conn.commit()
            print("✅ Email successfully saved to database!")
        except Exception as e:
            print(f"❌ Error saving email to database: {e}")

    mail.logout()
    print("📬 Fetching Complete!")

if __name__ == "__main__":
    fetch_emails()
