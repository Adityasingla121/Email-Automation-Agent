import gradio as gr
from email_utils import get_token, fetch_unread_emails, send_email
from agent import categorize_and_draft
from dotenv import load_dotenv
load_dotenv()

emails_data = []
access_token = None
drafts_cache = {}

def start_login():
    global access_token
    access_token = get_token()
    return "Login successful. Please select how many unread emails you want to analyze."

def load_emails_ui(n):
    global emails_data, drafts_cache
    emails_data = fetch_unread_emails(access_token, int(n))
    display = []
    drafts_cache = {}

    for idx, msg in enumerate(emails_data):
        subject = msg.get("subject", "No subject")
        body = msg.get("body", {}).get("content", "No body content")
        sender = msg.get("from", {}).get("emailAddress", {}).get("address", "Unknown sender")

        category, drafts = categorize_and_draft(subject, body)
        drafts_cache[idx] = {
            "category": category,
            "drafts": drafts
        }

        display.append(
            f"Email {idx}\nFrom: {sender}\nSubject: {subject}\n\nContent:\n{body[:300]}..."
        )

    return display

def get_drafts_for_email(index):
    index = int(index)
    if index in drafts_cache:
        drafts = drafts_cache[index]["drafts"]
        return drafts + ["", "", ""][:3-len(drafts)]  # Ensure 3 outputs
    return ["", "", ""]

def send_selected_email(index, body):
    email = emails_data[int(index)]
    to_addr = email.get("from", {}).get("emailAddress", {}).get("address")
    subject = email.get("subject", "No subject")
    result = send_email(access_token, to_addr, subject, body)
    return result

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("## ✉️ **Email Automation Agent**")
    gr.Markdown("Login, analyze your unread Outlook emails, and reply with AI assistance.")

    with gr.Row():
        login_btn = gr.Button("Login to Outlook")
        status = gr.Textbox(label="Status", interactive=False, show_label=False)

    login_btn.click(start_login, outputs=status)

    gr.Markdown("### Step 2: Choose number of unread emails to analyze")
    n_input = gr.Slider(1, 20, step=1, value=3, label="Number of unread emails")
    load_btn = gr.Button("Load and Analyze Emails")

    email_list = gr.List(label="Emails", interactive=False)

    load_btn.click(load_emails_ui, inputs=n_input, outputs=email_list)

    gr.Markdown("### Step 3: Select email and draft")
    idx_input = gr.Number(label="Email index", value=0)

    draft1 = gr.Textbox(label="Draft 1", interactive=False, lines=3)
    draft2 = gr.Textbox(label="Draft 2", interactive=False, lines=3)
    draft3 = gr.Textbox(label="Draft 3", interactive=False, lines=3)

    def update_drafts(index):
        d1, d2, d3 = get_drafts_for_email(index)
        return d1, d2, d3

    idx_input.change(update_drafts, inputs=idx_input, outputs=[draft1, draft2, draft3])

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

    def confirm_send(index, body):
        confirm1 = gr.update(visible=True)
        confirm2 = gr.update(visible=True)
        if gr.Confirm("Are you sure you want to send this email?"):
            if gr.Confirm("Please confirm again to proceed."):
                return send_selected_email(index, body)
        return "Send cancelled."

    send_btn.click(send_selected_email, inputs=[idx_input, reply_box], outputs=gr.Textbox(label="Send status"))

demo.launch()
