# # llm_planner.py (Ollama Version with llama3.1:8b)

# import json
# import aiohttp
# import asyncio
# import os
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

# OLLAMA_URL = "http://localhost:11434/api/chat"
# MODEL_NAME = "llama3.1:8b"


# def safe_json_parse(text: str) -> dict:
#     text = text.strip()

#     # Remove markdown blocks
#     if "```" in text:
#         parts = text.split("```")
#         text = parts[1] if len(parts) > 1 else text

#     # Find first JSON object
#     import re
#     match = re.search(r"\{.*?\}", text, re.DOTALL)

#     if not match:
#         return {"action": "error"}

#     try:
#         return json.loads(match.group())
#     except Exception:
#         return {"action": "error"}


# async def decide_action(goal, dom, url, failed_indices=None):

#     failed_indices = failed_indices or []

#     # 🔥 Optimization 1: Limit DOM size (reduce tokens)
#     dom = dom[:30]

#     system_prompt = """
# You are a browser automation agent.

# Analyze the current DOM and decide the SINGLE NEXT best action to achieve the goal.

# Rules:
# - Perform ONLY one action.
# - Never repeat failed indices.
# - If an input already contains the correct value, do NOT type again.
# - If a required input field is empty → type the appropriate value.
# - If required inputs are filled AND a submit/next/login button is visible → click it immediately.
# - Do NOT return "wait" if a clickable button is available.
# - Use "wait" ONLY if no actionable element is available or the page is clearly loading.
# - If the goal is achieved → return "done".
# - Return ONLY valid JSON.
# - Do NOT explain.

# JSON format:
# {
#   "action": "click" | "type" | "wait" | "done",
#   "index": number,
#   "text": string,
#   "seconds": number
# }

# """


#     # 🔥 Optimization 2: Remove indent (reduce token size)
#     user_prompt = f"""
# Goal: {goal}
# URL: {url}

# Failed indices (do not reuse): {failed_indices}

# Available Elements:
# {json.dumps(dom)}
# """

#     payload = {
#         "model": MODEL_NAME,
#         "format": "json",   # ← ADD THIS
#         "messages": [
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_prompt},
#         ],
#         "stream": False,
#         "options": {
#             "temperature": 0,
#             "num_predict": 200,
#             "num_ctx": 2048
#         },
#     }

#     # First try Ollama
#     try:
#         async with aiohttp.ClientSession() as session:
#             async with session.post(OLLAMA_URL, json=payload, timeout=aiohttp.ClientTimeout(total=120)) as response:
#                 if response.status != 200:
#                     print(f"❌ Ollama API error: HTTP {response.status}")
#                 else:
#                     result = await response.json()
#                     print("RAW RESULT:", result)
#                     if "message" in result:
#                         content = result["message"]["content"]
#                         return safe_json_parse(content)
#     except Exception as e:
#         print(f"❌ Ollama failed: {e}")
    
#     # If Ollama fails, try Gemini as fallback
    
#     # If both fail, return error
#     return {"action": "error"}




# # import json
# # import os
# # import google.generativeai as genai


# # MODEL_NAME = "gemini-1.5-flash"


# # def safe_json_parse(text: str) -> dict:
# #     text = text.strip()

# #     # Remove markdown blocks if present
# #     if "```" in text:
# #         parts = text.split("```")
# #         if len(parts) >= 2:
# #             text = parts[1]

# #     start = text.find("{")
# #     end = text.rfind("}") + 1

# #     if start == -1 or end == -1:
# #         return {"action": "error"}

# #     text = text[start:end]

# #     try:
# #         return json.loads(text)
# #     except Exception:
# #         return {"action": "error"}


# # async def decide_action(goal, dom, url, failed_indices=None):

# #     failed_indices = failed_indices or []

# #     genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
# #     model = genai.GenerativeModel(MODEL_NAME)

# #     system_prompt = """
# # You are an intelligent browser automation agent.

# # Your job:
# # 1. Analyze the current DOM carefully.
# # 2. Based on the user goal, determine relevant actions.
# # 3. Prioritize the most logical NEXT action.
# # 4. Return ONLY ONE action at a time.
# # 5. After each action, the DOM may change.
# # 6. Never repeat failed indices.

# # Action Strategy:
# # - If input fields required by the goal exist → type first.
# # - If submission/navigation required → click button.
# # - If loading required → return wait.
# # - If goal achieved → return done.
# # - If an email field exists → type the provided email.
# # - If a password field exists → type the provided password.
# # - After both are filled → click login button.
# # - Do NOT repeat failed indices.
# # - Only perform ONE action per step.

# # Rules:
# # - Do NOT return multiple actions.
# # - Do NOT explain.
# # - Return ONLY valid JSON.
# # - Use ONLY provided element indices.

# # Allowed JSON format:

# # {
# #   "action": "click" | "type" | "wait" | "done",
# #   "index": number,
# #   "text": string,
# #   "seconds": number
# # }
# # """

# #     user_prompt = f"""
# # Goal: {goal}
# # URL: {url}

# # Failed indices (do not reuse): {failed_indices}

# # Available Elements:
# # {json.dumps(dom, indent=2)}
# # """

# #     full_prompt = system_prompt + "\n\n" + user_prompt

# #     try:
# #         response = model.generate_content(
# #             full_prompt,
# #             generation_config={
# #                 "temperature": 0,
# #             },
# #         )

# #         content = response.text
# #         return safe_json_parse(content)

# #     except Exception as e:
# #         print("❌ Gemini Error:", e)
# #         return {"action": "error"}
# agent.py

import asyncio
from playwright.async_api import async_playwright
from dom_builder import extract_live_dom
from llm_planner import decide_action
from executor import execute_step


async def run(url, goal):

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await page.goto(url)

        for step_num in range(20):

            print(f"\n===== STEP {step_num+1} =====")
            print("Current URL:", page.url)

            dom = await extract_live_dom(page)

            action = await decide_action(goal, dom, page.url)
            print("🤖 ACTION:", action)

            if action.get("action") == "done":
                print("✅ Goal completed")
                break

            await execute_step(page, dom, action)

        await browser.close()


if __name__ == "__main__":
    url = "https://grid.ds.ascentt.ai/login"
    goal = "Login using email suryansh.nema@ascentt.com and password Sn94948988@"

    asyncio.run(run(url, goal))
