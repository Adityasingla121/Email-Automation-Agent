from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import re

llm = Ollama(model="mistral", verbose=True)  # verbose=True to see more LangChain logs

prompt_template = """
You are an email assistant.

Given this email:
Subject: {subject}
Body: {body}

First, categorize this email into one of these categories:
- Meeting
- Follow-up
- Request
- Spam
- Other

Then, generate 3 polite, appropriate draft replies to this email.

Return the output in this format:
Category: <category>
Reply 1: <reply text>
Reply 2: <reply text>
Reply 3: <reply text>
"""

prompt = PromptTemplate(input_variables=["subject", "body"], template=prompt_template)
email_chain = LLMChain(llm=llm, prompt=prompt, verbose=True)  # verbose=True here too

def categorize_and_draft(subject, body):
    raw_output = email_chain.run({"subject": subject, "body": body})
    
    # Parse the output
    category_match = re.search(r"Category:\s*(.*)", raw_output)
    reply_matches = re.findall(r"Reply \d+:\s*(.*)", raw_output)

    category = category_match.group(1).strip() if category_match else "Unknown"
    drafts = [reply.strip() for reply in reply_matches]

    return category, drafts
