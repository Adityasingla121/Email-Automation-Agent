import os
import requests
import msal
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
TENANT_ID = os.getenv("TENANT_ID")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["Mail.Read", "Mail.Send"]

app = msal.PublicClientApplication(
    CLIENT_ID,
    authority=AUTHORITY
)

token_result = None

def get_token():
    global token_result
    accounts = app.get_accounts()
    if accounts:
        token_result = app.acquire_token_silent(SCOPE, account=accounts[0])
    if not token_result:
        token_result = app.acquire_token_interactive(scopes=SCOPE)
    if "access_token" in token_result:
        return token_result["access_token"]
    else:
        raise Exception(f"Token error: {token_result.get('error_description', token_result)}")

def fetch_unread_emails(access_token, n):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    url = f"https://graph.microsoft.com/v1.0/me/messages?$filter=isRead eq false&$top={n}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("value", [])
    else:
        raise Exception(f"Fetch failed: {response.status_code}, {response.text}")

def send_email(access_token, to_address, subject, body):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "HTML",
                "content": body
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": to_address
                    }
                }
            ]
        }
    }
    url = "https://graph.microsoft.com/v1.0/me/sendMail"
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 202:
        return "Email sent successfully."
    else:
        return f"Send failed: {response.status_code}, {response.text}"
