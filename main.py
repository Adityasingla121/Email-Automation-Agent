from gmail_utils import get_token, fetch_unread_emails, send_email
from agent import categorize_and_draft


def main():
    # Step 1: Authenticate and get Gmail service
    service = get_token()

    # Step 2: Fetch unread emails (you can change 'n' to any number)
    n = 1
    emails = fetch_unread_emails(service, n)

    print(f"✅ Found {len(emails)} unread email(s).\n")

    # Step 3: Analyze each email
    for idx, msg in enumerate(emails, 1):
        subject = msg.get("subject", "No subject")
        sender = msg.get("from", {}).get("emailAddress", {}).get("address", "Unknown sender")
        body = msg.get("body", {}).get("content", "No body content")

        print(f"📧 Email {idx}")
        print(f"From: {sender}")
        print(f"Subject: {subject}")
        print(f"Body (preview):\n{body[:300]}...\n")

        # Step 4: Categorize and draft reply
        category, drafts = categorize_and_draft(subject, body)
        print(f"📂 Category: {category}")
        print("💬 Draft Suggestions:")
        for i, draft in enumerate(drafts, start=1):
            print(f"  Draft {i}: {draft}\n")

        print("-" * 80)


if __name__ == "__main__":
    main()
