import asyncio
def build_llm_payload(goal, dom):
    payload = {
        "goal": goal,
        "instructions": (
            "You are a browser automation agent.\n"
            "Choose the best element index and action (click or type).\n"
            "Return JSON only in this format:\n"
            '{ "action": "click" | "type", "index": number, "value": optional }'
        ),
        "available_elements": dom
    }
    return payload


# -------------------------------
# 🧠 Debug LLM Input
# -------------------------------
def debug_llm_payload(payload):
    print("\n🧠 ===== LLM INPUT PAYLOAD =====\n")
    print(json.dumps(payload, indent=2))
    print("\n📏 Payload Size (characters):", len(json.dumps(payload)))
    print("\n🧠 ===== END OF LLM INPUT =====\n")


# -------------------------------
# 🧠 Fake LLM Decision (for demo)
# -------------------------------
def fake_llm_decision(goal, dom):
    for el in dom:
        if el["type"] == "submit":
            return {"action": "click", "index": el["index"]}
    return None


# -------------------------------
# 🚀 Agent Loop
# -------------------------------
async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await page.goto("https://grid.ds.ascentt.ai")

        goal = "Login to the website"

        while True:
            print("\n==============================")
            print("📄 PAGE:", page.url)
            print("==============================")

            # 🥇 Minimal DOM
            dom = await build_dom_minimal(page)
            print("\nMinimal DOM elements:", len(dom))

            action = fake_llm_decision(goal, dom)

            # 🥈 Fallback if needed
            if not action:
                print("⚠ Minimal DOM insufficient. Switching to expanded DOM...")
                dom = await build_dom_expanded(page)
                print("Expanded DOM elements:", len(dom))
                action = fake_llm_decision(goal, dom)

            # 🔥 Build and debug LLM payload
            payload = build_llm_payload(goal, dom)
            debug_llm_payload(payload)

            print("\n🤖 LLM Decision:", action)

            await asyncio.sleep(10)
            break


if __name__ == "__main__":
    asyncio.run(run())