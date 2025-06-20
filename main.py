from email_utils import get_token, fetch_unread_emails
from agent import categorize_and_draft

def main():
    token = get_token()
    n = 1  # or prompt user for input
    emails = fetch_unread_emails(token, n)

    print(f"Found {len(emails)} unread emails.")

    for msg in emails:
        subject = msg.get("subject", "No subject")
        sender = msg.get("from", {}).get("emailAddress", {}).get("address", "Unknown sender")
        body = msg.get("body", {}).get("content", "No body content")

        print(f"From: {sender}\nSubject: {subject}")
        result = categorize_and_draft(subject, body)
        print(result)
        print("-" * 40)

if __name__ == "__main__":
    main()
