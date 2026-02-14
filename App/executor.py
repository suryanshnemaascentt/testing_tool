# async def execute_step(page, dom, step):

#     index = step.get("index")
#     action = step.get("action")
#     value = step.get("text") or step.get("value")

#     if index is None or index >= len(dom):
#         return False

#     element = dom[index]

#     try:
#         # Get all matching elements on the page
#         locator = page.locator(
#             "input, button, select, textarea, a, [role='button'], [role='link']"
#         )

#         # Use the playwright_index to select the correct element
#         playwright_index = element.get("playwright_index", index)
#         target_locator = locator.nth(playwright_index)

#         if action == "click":
#             await target_locator.click()

#         elif action == "type":
#             await target_locator.fill(value or "")
#             await target_locator.press("Tab")   # 🔥 trigger blur
#             await page.wait_for_timeout(500)    # 🔥 allow DOM update


#         elif action == "wait":
#             await page.wait_for_timeout(step.get("seconds", 2) * 1000)

#         elif action == "done":
#             return True

#         else:
#             return False

#         await page.wait_for_timeout(500)
#         return True

#     except Exception as e:
#         print("Executor error:", e)
#         return False


# async def execute_step(page, dom, step):

#     index = step.get("index")
#     action = step.get("action")
#     value = step.get("text") or step.get("value")

#     if index is None or index >= len(dom):
#         return False

#     element = dom[index]

#     try:
#         locator = page.locator(
#             "input, button, select, textarea, a, [role='button'], [role='link']"
#         )

#         playwright_index = element.get("playwright_index", index)
#         target_locator = locator.nth(playwright_index)

#         if action == "click":
#             await target_locator.click()

#         elif action == "type":
#             await target_locator.fill(value or "")
#             await target_locator.press("Tab")
#             await page.wait_for_timeout(300)

#         elif action == "wait":
#             await page.wait_for_timeout(step.get("seconds", 2) * 1000)

#         elif action == "done":
#             return True

#         else:
#             return False

#         return True

#     except Exception as e:
#         print("Executor error:", e)
#         return False
# async def execute_step(page, dom, step):

#     action = step.get("action")
#     selector = step.get("selector")
#     value = step.get("text") or step.get("value")

#     if not action:
#         return False

#     try:
#         # WAIT ACTION
#         if action == "wait":
#             await page.wait_for_timeout(step.get("seconds", 2) * 1000)
#             return True

#         # DONE ACTION
#         if action == "done":
#             return True

#         # For click & type, selector is required
#         if not selector:
#             print("❌ No selector provided")
#             return False

#         target_locator = page.locator(selector)

#         # Ensure element exists
#         await target_locator.wait_for(state="visible", timeout=5000)

#         if action == "click":
#             await target_locator.click()

#         elif action == "type":
#             await target_locator.fill(value or "")
#             await page.wait_for_timeout(300)

#         else:
#             return False

#         return True

#     except Exception as e:
#         print("Executor error:", e)
#         return False
# executor.py
async def execute_step(page, dom, step):

    action = step.get("action")
    selector = step.get("selector")
    value = step.get("text") or step.get("value")

    try:
        if action == "wait":
            await page.wait_for_timeout(step.get("seconds", 2) * 1000)
            return True

        if action == "done":
            return True

        if not selector:
            print("❌ No selector provided")
            return False

        target_locator = page.locator(selector)
        await target_locator.wait_for(state="visible", timeout=5000)

        if action == "click":
            await target_locator.click()

        elif action == "type":
            await target_locator.fill(value or "")
            await page.keyboard.press("Enter")   # helpful for login
            await page.wait_for_timeout(500)

        else:
            return False

        return True

    except Exception as e:
        print("Executor error:", e)
        return False
