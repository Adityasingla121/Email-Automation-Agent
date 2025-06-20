from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

llm = Ollama(model="mistral")

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
email_chain = LLMChain(llm=llm, prompt=prompt)

def categorize_and_draft(subject, body):
    return email_chain.run({"subject": subject, "body": body})
