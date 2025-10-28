import gradio as gr
from gmail_utils import get_token, fetch_unread_emails, send_email
from agent import categorize_and_draft
from dotenv import load_dotenv

load_dotenv()

emails_data = []
gmail_service = None
drafts_cache = {}

def start_login():
    """Authenticate with Gmail."""
    global gmail_service
    gmail_service = get_token()
    return "✅ Login successful! You can now choose how many unread emails to analyze."

def load_emails_ui(n):
    """Fetch and analyze unread emails."""
    global emails_data, drafts_cache
    emails_data = fetch_unread_emails(gmail_service, int(n))
    display = []
    drafts_cache = {}

    for idx, msg in enumerate(emails_data):
        subject = msg.get("subject", "No subject")
        sender = msg.get("from", "Unknown sender")

        body_raw = msg.get("body", "No body content")
        if isinstance(body_raw, dict):
            body = body_raw.get("data") or body_raw.get("text") or str(body_raw)
        else:
            body = str(body_raw)

        category, drafts = categorize_and_draft(subject, body)
        drafts_cache[idx] = {"category": category, "drafts": drafts}

        # Build nice email display for Gradio list
        display.append(
            f"📧 Email {idx}\nFrom: {sender}\nSubject: {subject}\n\nContent:\n{body[:300]}..."
        )

    return display

def get_drafts_for_email(index):
    """Return up to 3 draft replies for a selected email."""
    index = int(index)
    if index in drafts_cache:
        drafts = drafts_cache[index]["drafts"]
        return drafts + ["", "", ""][:3 - len(drafts)]
    return ["", "", ""]

def send_selected_email(index, body):
    """Send selected draft as a reply."""
    try:
        email = emails_data[int(index)]
        
        # Extract sender email - handle both string and dict formats
        sender = email.get("from", "")
        
        if isinstance(sender, dict):
            # Format: {"emailAddress": {"address": "email@example.com"}}
            to_addr = sender.get("emailAddress", {}).get("address")
            if not to_addr:
                # Alternative format: {"address": "email@example.com"}
                to_addr = sender.get("address")
        elif isinstance(sender, str):
            # Format: "email@example.com" or "Name <email@example.com>"
            to_addr = sender
            # Extract email from "Name <email@example.com>" format
            import re
            match = re.search(r'<(.+?)>', sender)
            if match:
                to_addr = match.group(1)
        else:
            return "❌ Error: Could not extract sender email address"
        
        if not to_addr:
            return "❌ Error: Sender email address is empty"
        
        # Extract subject
        subject = email.get("subject", "No subject")
        if not subject.startswith("Re: "):
            subject = "Re: " + subject
        
        # Send the email
        result = send_email(gmail_service, to_addr, subject, body)
        return f"✅ {result}"
        
    except IndexError:
        return "❌ Error: Invalid email index"
    except Exception as e:
        return f"❌ Error sending email: {str(e)}"


# ----------------- Gradio UI -----------------
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("## ✉️ **Gmail Automation Agent**")
    gr.Markdown("Authenticate with Gmail, analyze your unread emails, and draft AI-powered replies.")

    with gr.Row():
        login_btn = gr.Button("Login to Gmail")
        status = gr.Textbox(label="Status", interactive=False, show_label=False)

    login_btn.click(start_login, outputs=status)

    gr.Markdown("### Step 2: Choose number of unread emails to analyze")
    n_input = gr.Slider(1, 20, step=1, value=3, label="Number of unread emails")
    load_btn = gr.Button("Load and Analyze Emails")

    email_list = gr.List(label="Emails", interactive=False)
    load_btn.click(load_emails_ui, inputs=n_input, outputs=email_list)

    gr.Markdown("### Step 3: Select email and draft")
    idx_input = gr.Number(label="Email index", value=0)

    draft1 = gr.Textbox(label="Draft 1", interactive=False, lines=6)
    draft2 = gr.Textbox(label="Draft 2", interactive=False, lines=6)
    draft3 = gr.Textbox(label="Draft 3", interactive=False, lines=6)

    def update_drafts(index):
        drafts = get_drafts_for_email(index)
        # Always return exactly 3 drafts for consistency
        return tuple(drafts[:3])

    idx_input.change(fn=update_drafts, inputs=idx_input, outputs=[draft1, draft2, draft3])
    draft_choice = gr.Radio(["Draft 1", "Draft 2", "Draft 3"], label="Choose a draft")
    reply_box = gr.Textbox(label="Edit your reply", lines=10)

    def fill_reply_box(index, choice):
        drafts = get_drafts_for_email(index)
        if choice == "Draft 1":
            return drafts[0]
        elif choice == "Draft 2":
            return drafts[1]
        elif choice == "Draft 3":
            return drafts[2]
        return ""

    draft_choice.change(fill_reply_box, inputs=[idx_input, draft_choice], outputs=reply_box)

    send_btn = gr.Button("Send Email")
    send_status = gr.Textbox(label="Send status", interactive=False)

    def confirm_and_send(index, body):
        return send_selected_email(index, body)

    send_btn.click(confirm_and_send, inputs=[idx_input, reply_box], outputs=send_status)

demo.launch()