
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup


IMPORTANT_TAGS = ["a", "button", "input", "select", "textarea"]


async def extract_dom(page):
    try:
        await page.wait_for_load_state("networkidle", timeout=8000)
    except:
        pass

    html = await page.content()
    soup = BeautifulSoup(html, "html.parser")

    elements = []

    for el in soup.find_all(IMPORTANT_TAGS):
        text = el.get_text(strip=True)
        el_id = el.get("id")
        name = el.get("name")
        placeholder = el.get("placeholder")

        elements.append({
            "tag": el.name,
            "text": text,
            "id": el_id,
            "name": name,
            "placeholder": placeholder
        })

    return elements


async def print_live_visible_elements(page):
    print("\n🔵 LIVE VISIBLE BUTTONS:")
    button_locator = page.locator("button")
    button_count = await button_locator.count()

    for i in range(button_count):
        el = button_locator.nth(i)
        if await el.is_visible():
            print(
                f"[Button {i}] "
                f"ID={await el.get_attribute('id')} | "
                f"Text='{await el.inner_text()}' | "
                f"Aria={await el.get_attribute('aria-label')}"
            )

    print("\n🟢 LIVE VISIBLE INPUTS:")
    input_locator = page.locator("input")
    input_count = await input_locator.count()

    for i in range(input_count):
        el = input_locator.nth(i)
        if await el.is_visible():
            print(
                f"[Input {i}] "
                f"ID={await el.get_attribute('id')} | "
                f"Name={await el.get_attribute('name')} | "
                f"Placeholder={await el.get_attribute('placeholder')}"
            )


# ✅ Properly defined outside run()
async def print_live_clickable_elements(page):
    print("\n🟣 LIVE CLICKABLE ELEMENTS:")

    locator = page.locator(
        "button, input[type=submit], input[type=button]"
    )

    count = await locator.count()

    for i in range(count):
        el = locator.nth(i)

        if await el.is_visible():
            print(
                f"[{i}] "
                f"Tag={await el.evaluate('el => el.tagName')} | "
                f"ID={await el.get_attribute('id')} | "
                f"Type={await el.get_attribute('type')} | "
                f"Text='{await el.inner_text()}' | "
                f"Value={await el.get_attribute('value')}"
            )


async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await page.goto("https://grid.ds.ascentt.ai")

        while True:
            print("\n==============================")
            print("📄 CURRENT PAGE:", page.url)
            print("==============================")

            # BeautifulSoup DOM
            dom = await extract_dom(page)

            print("\n🟡 BeautifulSoup Extracted Elements:")
            for i, el in enumerate(dom[:30]):
                print(
                    f"[{i}] {el['tag']} | "
                    f"text='{el['text']}' | "
                    f"id={el['id']} | "
                    f"name={el['name']} | "
                    f"placeholder={el['placeholder']}"
                )

            print(f"\nTotal Elements Found (BeautifulSoup): {len(dom)}")

            # Live input count
            locator = page.locator("input")
            print("Total input elements in real browser:", await locator.count())

            # Live visible elements
            await print_live_visible_elements(page)

            # 🔥 New clickable elements section
            await print_live_clickable_elements(page)

            print("\n⏳ Waiting 10 seconds before next DOM capture...\n")
            await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(run())
