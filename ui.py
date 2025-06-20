import gradio as gr
from email_utils import get_access_token, fetch_unread_emails, send_email
from agent import categorize_and_draft
from dotenv import load_dotenv
load_dotenv()

token = None
emails_data = []

def load_emails(n):
    global token, emails_data
    token = get_access_token()
    emails = fetch_unread_emails(token)[:n]
    emails_data = emails
    display = []
    for idx, msg in enumerate(emails):
        subject = msg.get("subject", "No subject")
        body = msg.get("body", {}).get("content", "No body content")
        category, drafts = categorize_and_draft(subject, body)
        display.append((f"Email {idx+1}: {subject}", category, drafts))
    return display

def prepare_reply(index, draft_choice):
    return draft_choice

def confirm_send(index, subject, body):
    email = emails_data[index]
    to_address = email.get("from", {}).get("emailAddress", {}).get("address", None)
    if not to_address:
        return "Invalid recipient."
    result = send_email(token, to_address, subject, body)
    return result

with gr.Blocks() as demo:
    gr.Markdown("# Email Automation Agent")
    
    n_input = gr.Number(label="How many unread emails do you want to analyze?", value=1)
    load_btn = gr.Button("Load Emails")
    email_gallery = gr.Dataframe(headers=["Subject", "Category", "Drafts"], datatype=["str", "str", "str"], interactive=False)
    
    selected_idx = gr.Number(label="Select Email Index (0-based)", value=0)
    draft_input = gr.Textbox(label="Draft Reply", lines=10)
    send_btn = gr.Button("Send Email")
    
    load_btn.click(load_emails, inputs=[n_input], outputs=[email_gallery])
    
    def update_draft(idx):
        idx = int(idx)
        email = emails_data[idx]
        subject = email.get("subject", "No subject")
        body = email.get("body", {}).get("content", "No body content")
        category, drafts = categorize_and_draft(subject, body)
        return drafts[0] if drafts else ""

    selected_idx.change(update_draft, inputs=[selected_idx], outputs=[draft_input])
    
    def double_confirm_send(index, body):
        index = int(index)
        email = emails_data[index]
        subject = email.get("subject", "No subject")
        confirmed = gr.update(visible=True)
        final_confirm = gr.update(visible=True)
        return f"First confirmation: Are you sure to send to {email.get('from', {}).get('emailAddress', {}).get('address')}?"
    
    send_btn.click(
        lambda idx, body: confirm_send(int(idx), emails_data[int(idx)].get("subject", "No subject"), body),
        inputs=[selected_idx, draft_input],
        outputs=gr.Textbox(label="Send Status")
    )

demo.launch()
