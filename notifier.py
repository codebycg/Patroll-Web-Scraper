import json
import os
import smtplib
from email.mime.text import MIMEText

data = "won_patent_contests.json"       
snapshot_data = "last_known_won_patent_contests.json"  

sender_email = os.getenv("") 
receiver_email = os.getenv("") 
email_password = os.getenv("") 

def load_contests(filepath):
    # Load contests list from a JSON file
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f).get("contests", [])
    else:
        return []

def detect_new_contests(current_contests, last_known_contests):
    # Find contests in current data that are not in the last snapshot
    known_links = set(c['contestLink'] for c in last_known_contests)
    new_contests = [c for c in current_contests if c['contestLink'] not in known_links]
    return new_contests

def send_email(new_contests):
    if not new_contests:
        return

    # Compose the email body with new contest details
    subject = f"New Won Patents Detected ({len(new_contests)})"
    body = "The following new won patent contests were detected:\n\n"

    for c in new_contests:
        body += f"- {c['contestTitle']} ({c['patentID']})\n  Link: {c['contestLink']}\n\n"

    msg = MIMEText(body, "plain")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    # Send email using Gmail SMTP server
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, email_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())

    print(f"Sent email for {len(new_contests)} new contests.")

def main():
    # Load current and last known contests
    current_contests = load_contests(data)
    last_known_contests = load_contests(snapshot_data)

    # Detect new contests not in last snapshot
    new_contests = detect_new_contests(current_contests, last_known_contests)

    # Send notification email if new contests found
    if new_contests:
        send_email(new_contests)
    else:
        print("No new contests found.")

    # Update the snapshot file with current contests
    with open(snapshot_data, 'w') as f:
        json.dump({"contests": current_contests}, f, indent=2)

if __name__ == "__main__":
    main()
