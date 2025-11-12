import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import logging

# Set up basic logging for better feedback
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def scrap():
    """
    Launches a browser, navigates to billygrados.com, and scrapes blog post data.
    """
    posts_data = []
    BASE_URL = "https://billygrados.com"
    
    logging.info("Starting the scraping process...")
    p = await async_playwright().start()
    browser = await p.chromium.launch(headless=False) # Set headless=False to watch the browser
    page = await browser.new_page()
    
    try:
        logging.info(f"Navigating to {BASE_URL}...")
        await page.goto(BASE_URL, wait_until="domcontentloaded")
        logging.info("Page loaded successfully.")

        # Wait for the post feed container to be visible to ensure content is loaded
        await page.locator('div.post-feed').wait_for(timeout=10000)

        # Locate all the article elements that represent a blog post
        post_cards = await page.locator('article.post-card').all()
        logging.info(f"Found {len(post_cards)} posts on the page.")

        for post in post_cards:
            # Use locators to find elements within each post card
            title_element = post.locator('h2.post-card-title')
            link_element = post.locator('a.post-card-image-link')
            excerpt_element = post.locator('div.post-card-excerpt')

            # Extract the data
            title = await title_element.inner_text()
            relative_url = await link_element.get_attribute('href')
            excerpt = await excerpt_element.inner_text()

            # Clean up and format the data
            url = f"{BASE_URL}{relative_url}" if relative_url else "No URL Found"
            
            posts_data.append({
                "title": title.strip(),
                "url": url,
                "excerpt": excerpt.strip()
            })

    except Exception as e:
        logging.error(f"An error occurred during scraping: {e}")
    finally:
        logging.info("Closing the browser.")
        await browser.close()
            
    logging.info(f"Scraping finished. Extracted {len(posts_data)} posts.")
    return posts_data

# If you were running this as a .py script, you would use:
scraped_data = asyncio.run(scrap())

# Now, let's use pandas to display the data neatly
if scraped_data:
    df = pd.DataFrame(scraped_data)
    print("\n--- Scraped Data ---")
    print(df)
else:
    print("No data was scraped.")

if scraped_data:
    try:
        df.to_csv("billygrados_posts_playwright.csv", index=False, encoding='utf-8')
        logging.info("Data successfully saved to billygrados_posts_playwright.csv")
    except Exception as e:
        logging.error(f"Error saving data to CSV: {e}")
