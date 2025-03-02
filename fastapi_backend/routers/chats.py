from uuid import uuid4
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List
import os
from dotenv import load_dotenv
from fastapi import APIRouter
from openai import OpenAI
import validators
import requests
from checks import analyse_website


system_prompt = '''You are an AI Accessibility Auditor specializing in web compliance and usability. Your task is to analyze accessibility audit results and generate a **detailed, insightful, and structured report**. The goal is to ensure websites are **fully compliant with accessibility standards (WCAG, ARIA, and usability best practices)**.

Your report should:
1️⃣ Clearly identify **violations and missing accessibility features**.  
2️⃣ Provide **context and severity** for each issue.  
3️⃣ Offer **actionable recommendations** to improve compliance.  
4️⃣ Assess **content clarity and structure** for readability.  
5️⃣ Evaluate **usability for users with disabilities**, particularly screen reader users and keyboard-only navigation.

Keep the tone **professional, detailed, and structured**. Avoid unnecessary jargon but ensure technical accuracy. The output should be **easy to understand for developers, designers, and compliance officers** You can also provide code for improvements.
'''

additonal_instructions = '''📌 **Task:**  
Analyze the following **accessibility audit results** and generate a **detailed accessibility compliance report**.  
Each section should include:
- **Key observations** based on the audit findings.
- **Potential user impact** (especially for visually impaired users, keyboard-only users, etc.).
- **Best practices** for resolving issues.
- **Overall compliance score** based on severity.

📌 **Key Points to Cover:**
✅ **Keyboard Accessibility** - Are interactive elements reachable via keyboard?  
✅ **ALT Text & Images** - Are images missing descriptions?  
✅ **Form Accessibility** - Do inputs lack labels or placeholders?  
✅ **Color Contrast** - Is the text readable against backgrounds?  
✅ **ARIA & Roles** - Are ARIA attributes correctly used?  
✅ **Content Clarity & Readability** - Is the text clear and well-structured?  
✅ **Skip Links & Navigation** - Is quick access to content available for assistive tech users?  

🔹 **Final Output:**  
Your response should be **structured, with bullet points and sections**. Provide **concrete recommendations** and **suggestions for improvement**.
'''

load_dotenv()  # Load API key from .env file

router = APIRouter()

def is_url(message):
    return validators.url(message)


def is_safe_url(url):
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except:
        return False

class ChatMessage(BaseModel):
    message: str

# Store chats in memory
chats: Dict[str, List[Dict[str, str]]] = {}

# Set OpenAI API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@router.post('/chats')
async def create_new_chat():
    """Create a new chat session"""
    chat_id = str(uuid4())[:8]
    chats[chat_id] = []  # Initialize empty chat history
    return {'id': chat_id}

@router.post('/chats/{chat_id}')
async def chat(chat_id: str, chat_in: ChatMessage):
    """Send a message and get response from OpenAI API"""
    if chat_id not in chats:
        raise HTTPException(status_code=404, detail=f'Chat {chat_id} does not exist')

    # OpenAI API call
    try:
        client = OpenAI()

        input_prompt = chat_in.message
        if is_url(input_prompt):
        # Perform your extra URL-specific checks
            if not is_safe_url(input_prompt):
                return {"error": "Unsafe or invalid URL!"}
            input_prompt = analyse_website(input_prompt)
            input_prompt = additonal_instructions + "/n" + input_prompt
            

        response = client.chat.completions.create(
            model="gpt-4o",  # Change to gpt-4 if needed
            messages=[
                {"role": "system", "content": system_prompt},
                *chats[chat_id],  # Include chat history
                {"role": "user", "content": input_prompt}
            ]
        )
        bot_response = response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error from OpenAI: {str(e)}")

    # Store chat history
    chats[chat_id].append({"role": "user", "content": chat_in.message})
    chats[chat_id].append({"role": "assistant", "content": bot_response})

    return {"message": bot_response}

@router.get('/chats/{chat_id}/history')
async def get_chat_history(chat_id: str):
    """Retrieve chat history"""
    if chat_id not in chats:
        raise HTTPException(status_code=404, detail=f'Chat {chat_id} does not exist')

    return {"messages": chats[chat_id]}
