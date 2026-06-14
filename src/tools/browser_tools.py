from langchain.tools import tool
from playwright.sync_api import sync_playwright
import pytesseract
from PIL import Image
import structlog

logger = structlog.get_logger()

@tool
def screenshot_and_ocr(url: str, username: str, password: str, css_selector: str = "body") -> str:
    """Navigate to a URL, login, take screenshot of element and extract text via OCR. Only use as fallback."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.fill('input[name="username"]', username)
        page.fill('input[name="password"]', password)
        page.click('button[type="submit"]')
        page.wait_for_load_state("networkidle")
        element = page.query_selector(css_selector)
        if element:
            element.screenshot(path="/tmp/screenshot.png")
        browser.close()
    text = pytesseract.image_to_string(Image.open("/tmp/screenshot.png"))
    logger.info("OCR extraction completed", length=len(text))
    return text