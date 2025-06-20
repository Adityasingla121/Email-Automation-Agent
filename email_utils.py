import os
import requests
import msal

CLIENT_ID = os.getenv("CLIENT_ID")
TENANT_ID = os.getenv("TENANT_ID")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["Mail.Read", "Mail.Send"]

def get_access_token():
    app = msal.PublicClientApplication(
        client_id=CLIENT_ID,
        authority=AUTHORITY
    )

    accounts = app.get_accounts()
    result = None

    if accounts:
        print(f"Found cached account: {accounts[0]['username']}")
        result = app.acquire_token_silent(SCOPE, account=accounts[0])

    if not result:
        print("No valid cached token — opening browser for login...")
        result = app.acquire_token_interactive(
            scopes=SCOPE,
            prompt="login"
        )

    if "access_token" in result:
        return result["access_token"]
    else:
        raise Exception(f"Token acquisition failed: {result.get('error_description', result.get('error'))}")

def fetch_unread_emails(token):
    headers = {"Authorization": f"Bearer {token}"}
    graph_endpoint = "https://graph.microsoft.com/v1.0/me/messages?$filter=isRead eq false"
    response = requests.get(graph_endpoint, headers=headers)

    if response.status_code == 200:
        messages = response.json().get("value", [])
        return messages
    else:
        raise Exception(f"API call failed: {response.status_code} {response.text}")
    
def send_email(token, to_address, subject, body):
    headers = {
        "Authorization": f"Bearer {token}",
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
    graph_endpoint = "https://graph.microsoft.com/v1.0/me/sendMail"
    response = requests.post(graph_endpoint, headers=headers, json=data)
    
    if response.status_code == 202:
        return "Email sent successfully."
    else:
        return f"Failed to send email: {response.status_code}, {response.text}"

