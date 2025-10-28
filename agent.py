from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence
import re

# Initialize the LLM (optimized for speed)
llm = OllamaLLM(model="mistral", verbose=False, num_predict=300)

# Define the prompt
prompt_template = """
You are an intelligent email assistant that helps draft professional replies.

Given this email:
Subject: {subject}
Body: {body}


1. Then, write **three complete and polite email reply bodies** (not just subject lines).
Each reply should sound natural, professional, and relevant to the email context.

Format your response exactly like this:

Reply 1:
<full reply body>

Reply 2:
<full reply body>

Reply 3:
<full reply body>
"""

prompt = PromptTemplate(input_variables=["subject", "body"], template=prompt_template)

# Create a runnable chain (modern replacement for LLMChain)
email_chain = RunnableSequence(prompt | llm | StrOutputParser())

# In-memory cache to avoid repeated LLM calls
cache = {}

def categorize_and_draft(subject, body):
    """Categorize the email and generate up to 3 draft replies."""
    key = (subject, hash(body))
    if key in cache:
        return cache[key]

    # Run the LLM chain
    response = email_chain.invoke({"subject": subject, "body": body})
    text = response.strip()
    
    # Debug: print raw response
    print("=" * 80)
    print("RAW LLM RESPONSE:")
    print(text)
    print("=" * 80)

    # Parse the category
    category = "Other"
    category_match = re.search(r'Category:\s*(.+)', text, re.IGNORECASE)
    if category_match:
        category = category_match.group(1).strip()

    # Parse the replies using regex to capture multi-line content
    drafts = []
    
    # Split by "Reply N:" markers
    reply_pattern = r'Reply\s+\d+:\s*\n?(.*?)(?=Reply\s+\d+:|$)'
    matches = re.findall(reply_pattern, text, re.DOTALL | re.IGNORECASE)
    
    for match in matches:
        draft = match.strip()
        if draft:  # Only add non-empty drafts
            drafts.append(draft)
    
    # If regex fails, try simple splitting
    if len(drafts) < 3:
        drafts = []
        parts = re.split(r'Reply\s+\d+:', text, flags=re.IGNORECASE)
        for part in parts[1:]:  # Skip first part (before first Reply)
            draft = part.strip()
            # Remove "Category:" line if it appears
            draft = re.sub(r'^Category:.*\n?', '', draft, flags=re.IGNORECASE | re.MULTILINE)
            if draft:
                drafts.append(draft)

    # Ensure exactly 3 drafts
    while len(drafts) < 3:
        drafts.append("No draft generated. Please try again or edit manually.")
    
    # Truncate to 3 drafts if more were generated
    drafts = drafts[:3]

    cache[key] = (category, drafts)
    return category, drafts