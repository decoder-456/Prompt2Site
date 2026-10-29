import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
from backend.config import MAX_BUTTONS_TO_TEST, MAX_LINKS_TO_CHECK, PREVIEW_ROOT
from backend.services.website_files import safe_id

async def _run_tests(html_path: Path) -> list[str]:
    errors = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1365, "height": 900})
        page.set_default_timeout(2500)
        page.on("pageerror", lambda exc: errors.append(f"JavaScript runtime error: {exc}"))
        try:
            await page.goto(html_path.resolve().as_uri(), wait_until="load", timeout=15000)
            await page.wait_for_timeout(250)
            if not (await page.title()).strip():
                errors.append("Page title is empty.")
            if not (await page.locator("body").inner_text()).strip():
                errors.append("Page body has no visible text.")
            buttons = page.locator("button")
            dangerous = ("delete", "remove account", "purchase", "buy now", "pay now", "logout", "log out", "unsubscribe")
            for i in range(min(await buttons.count(), MAX_BUTTONS_TO_TEST)):
                button = buttons.nth(i)
                try:
                    if not await button.is_visible() or not await button.is_enabled():
                        continue
                    label = (await button.inner_text()).strip().lower()
                    if any(word in label for word in dangerous):
                        continue
                    await button.click()
                    await page.wait_for_timeout(100)
                except Exception as exc:
                    errors.append(f"Button {i + 1} test failed: {exc}")
            links = page.locator("a[href]")
            for i in range(min(await links.count(), MAX_LINKS_TO_CHECK)):
                try:
                    href = (await links.nth(i).get_attribute("href") or "").strip()
                    if not href or href.startswith(("http://", "https://", "mailto:", "tel:", "javascript:")):
                        continue
                    if href.startswith("#"):
                        target = href[1:]
                        if target and not await page.locator(f'[id="{target}"]').count():
                            errors.append(f"Missing internal link target: {href}")
                    elif href.lower().split("?")[0].endswith((".html", ".htm")):
                        target = (html_path.parent / href.split("?")[0]).resolve()
                        if target.is_relative_to(html_path.parent.resolve()) and not target.exists():
                            errors.append(f"Local HTML page does not exist: {href}")
                except Exception as exc:
                    errors.append(f"Link {i + 1} test failed: {exc}")
            # Fill forms only; never submit forms automatically.
            forms = page.locator("form")
            for i in range(min(await forms.count(), 10)):
                form = forms.nth(i)
                try:
                    if not await form.is_visible():
                        continue
                    action = (await form.get_attribute("action") or "").lower()
                    if action.startswith(("http://", "https://", "//")):
                        continue
                    fields = form.locator("input:not([type=hidden]), textarea, select")
                    for j in range(min(await fields.count(), 15)):
                        field = fields.nth(j)
                        if not await field.is_visible() or not await field.is_enabled():
                            continue
                        kind = (await field.get_attribute("type") or "").lower()
                        if kind in ("submit", "button", "reset", "file", "password"):
                            continue
                        tag = await field.evaluate("el => el.tagName.toLowerCase()")
                        if kind in ("checkbox", "radio"):
                            if not await field.is_checked(): await field.check()
                        elif tag == "select":
                            options = field.locator("option")
                            for k in range(await options.count()):
                                value = await options.nth(k).get_attribute("value")
                                if value:
                                    await field.select_option(value=value)
                                    break
                        else:
                            await field.fill("test@example.com" if kind == "email" else "Test User")
                except Exception as exc:
                    errors.append(f"Form {i + 1} test failed: {exc}")
        except Exception as exc:
            errors.append(f"Browser test failed: {exc}")
        finally:
            await browser.close()
    return list(dict.fromkeys(errors))

def browser_test(project_id: str) -> list[str]:
    path = (PREVIEW_ROOT / safe_id(project_id) / "index.html").resolve()
    if not path.exists():
        return [f"Preview file not found: {path}"]
    try:
        return asyncio.run(_run_tests(path))
    except Exception as exc:
        return [f"Playwright failed: {exc}. Run: python -m playwright install chromium"]
