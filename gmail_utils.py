from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_token():
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret_515054410421-5na56eoldv11kpof0m5omuqtcal5r4bn.apps.googleusercontent.com.json', SCOPES)
    creds = flow.run_local_server(port=8080)
    service = build('gmail', 'v1', credentials=creds)
    return service

def fetch_unread_emails(service, max_results=5):
    results = service.users().messages().list(userId="me", labelIds=["UNREAD"], maxResults=max_results).execute()
    messages = results.get("messages", [])
    emails = []

    for m in messages:
        msg = service.users().messages().get(userId="me", id=m["id"], format="full").execute()
        payload = msg.get("payload", {})
        headers = payload.get("headers", [])
        parts = payload.get("parts", [])
        
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No subject")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown sender")
        
        body = ""
        if parts:
            for part in parts:
                if part.get("mimeType") == "text/plain":
                    import base64
                    body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
                    break

        emails.append({
            "from": sender,
            "subject": subject,
            "body": body.strip() or "(No body content)"
        })

    return emails

def send_email(service, to, subject, body_text):
    message = MIMEText(body_text)
    message['to'] = to
    message['subject'] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    msg = {'raw': raw}
    service.users().messages().send(userId='me', body=msg).execute()
    return f"Email successfully sent to {to}"
