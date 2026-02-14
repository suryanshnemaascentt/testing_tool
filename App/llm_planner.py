# llm_planner.py (Ollama Version with llama3.1:8b)

import json
import aiohttp
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
print("🔥 NEW SELECTOR PLANNER LOADED")

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.1:8b"


def safe_json_parse(text: str) -> dict:
    text = text.strip()

    # Remove markdown blocks
    if "```" in text:
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text

    # Find first JSON object
    import re
    match = re.search(r"\{.*?\}", text, re.DOTALL)

    if not match:
        return {"action": "error"}

    try:
        data = json.loads(match.group())

        if "index" in data:
            print("❌ LLM returned index — rejecting")
            return {"action": "error"}

        return data

    except Exception:
        return {"action": "error"}


# Function that matches the 3-parameter call from agent
async def decide_action(goal, dom, url):
    # Call the main function with default empty failed_indices
    return await decide_action_with_failed_indices(goal, dom, url, [])


# Main function with all parameters
async def decide_action_with_failed_indices(goal, dom, url, failed_indices=None):
    failed_indices = failed_indices or []

    # 🔥 Optimization 1: Limit DOM size (reduce tokens)
    dom = dom[:30]

    system_prompt = """
You are a browser automation agent.

Your task is to perform the SINGLE NEXT best action to achieve login.

STRICT RULES:
- NEVER use index.
- ALWAYS use selector.
- Prefer id selector (#id).
- Perform ONLY one action.
- Return ONLY valid JSON.
- No explanation.

LOGIN STRATEGY:

LOGIN STRATEGY (GENERIC):

- If an input field of type "email" or with label containing "email" exists and is empty → type the provided email.
- If an input field of type "password" or with label containing "password" exists and is empty → type the provided password.
If a confirmation page is shown (for example "Stay signed in?") and a visible button labeled "Yes" exists → click it.
Never return "wait" when a confirmation button is visible.
- If a submit button is visible and required inputs are filled → click it.
- Never return "wait" if a visible password input exists.
- Only return "wait" if no visible input or button exists.


NEVER type the same value again if already filled.

JSON format:
{
  "action": "click" | "type" | "wait" | "done",
  "selector": "CSS selector",
  "text": "string (only for type)",
  "seconds": number (only for wait)
}
"""

    # 🔥 Optimization 2: Remove indent (reduce token size)
    user_prompt = f"""
Goal: {goal}
URL: {url}

Failed indices (do not reuse): {failed_indices}

Available Elements:
{json.dumps(dom)}
"""

    payload = {
        "model": MODEL_NAME,
        "format": "json",   # ← ADD THIS
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "options": {
            "temperature": 0,
            "num_predict": 200,
            "num_ctx": 2048
        },
    }

    # First try Ollama
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(OLLAMA_URL, json=payload, timeout=aiohttp.ClientTimeout(total=120)) as response:
                if response.status != 200:
                    print(f"❌ Ollama API error: HTTP {response.status}")
                else:
                    result = await response.json()
                    print("RAW RESULT:", result)
                    if "message" in result:
                        content = result["message"]["content"]
                        return safe_json_parse(content)
    except Exception as e:
        print(f"❌ Ollama failed: {e}")
    
    # If Ollama fails, try Gemini as fallback
    
    # If both fail, return error
    return {"action": "error"}