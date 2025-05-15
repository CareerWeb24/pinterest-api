
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from playwright.sync_api import sync_playwright

app = FastAPI()

# CORS settings (allow all origins for testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/pin-count")
def get_pin_count(keyword: str = Query(..., min_length=1)):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        search_url = f"https://www.pinterest.com/search/pins/?q={keyword}"
        page.goto(search_url, timeout=60000)

        page.wait_for_timeout(3000)  # wait for pins to load

        # Scroll to load more pins
        for _ in range(5):
            page.mouse.wheel(0, 3000)
            page.wait_for_timeout(1000)

        pins = page.query_selector_all('div[data-test-id="pin"]')
        count = len(pins)
        browser.close()

        return JSONResponse(content={"keyword": keyword, "pin_count": count})
