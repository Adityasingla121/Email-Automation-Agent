import os
import requests
import msal

# Load env
CLIENT_ID = os.getenv("CLIENT_ID")
TENANT_ID = os.getenv("TENANT_ID")
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["Mail.Read", "Mail.Send"]

# Initialize MSAL public client app
app = msal.PublicClientApplication(
    client_id=CLIENT_ID,
    authority=AUTHORITY
)

# Attempt to use cached token
accounts = app.get_accounts()
result = None

if accounts:
    print(f"✅ Found cached account: {accounts[0]['username']}")
    result = app.acquire_token_silent(SCOPE, account=accounts[0])

# If no valid cached token, do interactive login
if not result:
    print("🔑 No valid cached token — opening browser for login...")
    result = app.acquire_token_interactive(
        scopes=SCOPE,
        prompt="login"
    )

# Handle result
if "access_token" in result:
    headers = {
        "Authorization": f"Bearer {result['access_token']}"
    }
    graph_endpoint = "https://graph.microsoft.com/v1.0/me/messages?$filter=isRead eq false"
    response = requests.get(graph_endpoint, headers=headers)

    if response.status_code == 200:
        messages = response.json().get("value", [])
        print(f" Found {len(messages)} unread emails.\n")
        for msg in messages:
            subject = msg.get("subject", "No subject")
            sender = msg.get("from", {}).get("emailAddress", {}).get("address", "Unknown sender")
            print(f"From: {sender}\nSubject: {subject}\n")
    else:
        print(f"API call failed: {response.status_code}")
        print(response.json())
else:
    print(f"Could not obtain token.")
    print(result.get('error_description', result.get('error')))
