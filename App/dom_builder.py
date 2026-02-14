# # async def extract_live_dom(page):
# #     """Optimized DOM extraction with reduced waiting and better performance."""
# #     # Minimal wait for DOM content
# #     try:
# #         await page.wait_for_load_state("domcontentloaded", timeout=5000)
# #     except:
# #         pass  # Continue even if wait fails
    
# #     # Optimized JavaScript evaluation with early filtering
# #     elements = await page.evaluate("""
# #     () => {
# #         // Early exit if no elements found
# #         const selector = "button, a, input, select, textarea, [role='button'], [role='link']";
# #         const nodes = document.querySelectorAll(selector);
        
# #         if (nodes.length === 0) return [];
        
# #         const results = [];
# #         let index = 0;
        
# #         // Process nodes with early filtering
# #         for (let i = 0; i < nodes.length && results.length < 30; i++) {
# #             const el = nodes[i];
            
# #             // Skip invisible or disabled elements early
# #             if (el.disabled || el.offsetParent === null) continue;
            
# #             const tag = el.tagName.toLowerCase();
# #             const role = el.getAttribute("role");
# #             const type = el.getAttribute("type");
# #             const value = el.value || el.getAttribute("value");
# #             const placeholder = el.getAttribute("placeholder");
# #             const name = el.getAttribute("name");
# #             const text = el.innerText || "";
            
# #             // Create label with priority order
# #             const label = text.trim() || placeholder || value || name || role || "";
            
# #             results.push({
# #                 index: index++,
# #                 playwright_index: i,
# #                 tag: tag,
# #                 type: type,
# #                 role: role,
# #                 label: label,
# #                 value: value
# #             });
# #         }
        
# #         return results;
# #     }
# #     """)
    
# #     if elements:
# #         print(f"✅ Extracted {len(elements)} DOM elements")
# #     else:
# #         print("⚠️ No DOM elements found")
    
# #     return elements



# async def extract_live_dom(page):
#     try:
#         await page.wait_for_load_state("domcontentloaded", timeout=5000)
#     except:
#         pass

#     elements = await page.evaluate("""
#     () => {
#         const selector = "button, a, input, select, textarea, [role='button'], [role='link']";
#         const nodes = document.querySelectorAll(selector);

#         if (nodes.length === 0) return [];

#         const results = [];

#         for (let i = 0; i < nodes.length && results.length < 40; i++) {
#             const el = nodes[i];

#             if (el.disabled || el.offsetParent === null) continue;

#             const tag = el.tagName.toLowerCase();
#             const id = el.id || "";
#             const role = el.getAttribute("role") || "";
#             const type = el.getAttribute("type") || "";
#             const value = el.value || "";
#             const placeholder = el.getAttribute("placeholder") || "";
#             const name = el.getAttribute("name") || "";
#             const ariaLabel = el.getAttribute("aria-label") || "";
#             const text = el.innerText || "";

#             const label =
#                 text.trim() ||
#                 placeholder ||
#                 ariaLabel ||
#                 name ||
#                 value ||
#                 role ||
#                 "";

#             // Build stable selector
#             let selectorPath = "";
#             if (id) {
#                 selectorPath = "#" + id;
#             } else if (name) {
#                 selectorPath = tag + "[name='" + name + "']";
#             } else {
#                 selectorPath = tag + ":nth-of-type(" + (i + 1) + ")";
#             }

#             results.push({
#                 tag: tag,
#                 id: id,
#                 role: role,
#                 type: type,
#                 label: label,
#                 selector: selectorPath
#             });
#         }

#         return results;
#     }
#     """)

#     if elements:
#         print(f"✅ Extracted {len(elements)} DOM elements")
#     else:
#         print("⚠️ No DOM elements found")

#     return elements
# dom_builder.py
async def extract_live_dom(page):
    try:
        await page.wait_for_load_state("networkidle", timeout=7000)
    except:
        pass

    # 🔥 Retry mechanism added (without removing anything)
    for attempt in range(3):
        try:
            elements = await page.evaluate("""
            () => {
                const selector = "button, a, input, select, textarea, [role='button'], [role='link']";
                const nodes = document.querySelectorAll(selector);

                const results = [];

                for (let i = 0; i < nodes.length && results.length < 50; i++) {
                    const el = nodes[i];

                    const rect = el.getBoundingClientRect();

                    if (
                        el.disabled ||
                        el.getAttribute("aria-hidden") === "true" ||
                        rect.width === 0 ||
                        rect.height === 0
                    ) continue;

                    const tag = el.tagName.toLowerCase();
                    const id = el.id || "";
                    const role = el.getAttribute("role") || "";
                    const type = el.getAttribute("type") || "";
                    const value = el.value || "";
                    const placeholder = el.getAttribute("placeholder") || "";
                    const name = el.getAttribute("name") || "";
                    const ariaLabel = el.getAttribute("aria-label") || "";
                    const text = el.innerText || "";

                    const label =
                        text.trim() ||
                        placeholder ||
                        ariaLabel ||
                        name ||
                        value ||
                        role ||
                        "";

                    let selectorPath = "";
                    if (id) {
                        selectorPath = "#" + id;
                    } else if (name) {
                        selectorPath = tag + "[name='" + name + "']";
                    } else {
                        selectorPath = tag + ":nth-of-type(" + (i + 1) + ")";
                    }

                    results.push({
                        tag: tag,
                        id: id,
                        type: type,
                        label: label,
                        selector: selectorPath,
                        value: value
                    });
                }

                return results;
            }
            """)

            print("DOM CONTENT:", elements)
            print(f"✅ Extracted {len(elements)} DOM elements")
            return elements

        except Exception as e:
            print("⚠️ DOM extraction failed due to navigation. Retrying...")
            try:
                await page.wait_for_load_state("load", timeout=5000)
            except:
                pass

    # If still failing after retries
    print("❌ DOM extraction failed after 3 attempts.")
    return []
