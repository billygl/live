
from playwright.sync_api import sync_playwright

def main():
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.tiktok.com/@mashi_gaming/live")
    print("Waiting for 30 seconds before starting...")
    page.wait_for_timeout(60000) # Wait for 30 seconds (in milliseconds)
    for _ in range(30):
        page.keyboard.press("L")
        page.wait_for_timeout(100) # Use sync wait for small delay (in milliseconds)
        
        browser.close()

if __name__ == "__main__":
    main()
