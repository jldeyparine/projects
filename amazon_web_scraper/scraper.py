"""
scraper.py
A web scraping script for extracting product information from Amazon search results using Selenium and BeautifulSoup.
Functions:
-----------
get_url(search_text):
    Generate an Amazon search URL for the given search text, with a page query placeholder.
extract_record(item):
    Extracts product details (description, price, rating, review count, and URL) from a BeautifulSoup tag representing a single search result item.
main(search_term):
    Main routine to scrape multiple pages of Amazon search results for the given search term, extract product data, and save it to a CSV file.
Usage:
------
Run the script directly to scrape Amazon for a specified search term (default: 'ultrawide monitor') and save results to 'results.csv'.
Requirements:
-------------
- Selenium
- BeautifulSoup (bs4)
- Microsoft Edge WebDriver
"""

import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def get_url(search_text):
    """Generate a url from search text"""
    template = "https://www.amazon.com/s?k={}&ref=nb_sb_noss_1"
    search_term = search_text.replace(" ", "+")

    # add term query to url
    url = template.format(search_term)

    # add page query placeholder
    url += "&page={}"

    return url


def extract_record(item):
    """Extract and return data from a single record"""

    try:
        # Description is in h2 > span
        h2_tag = item.find("h2")
        if not h2_tag:
            return None

        description = h2_tag.get_text(strip=True)

        # URL is in the parent link of h2
        atag = item.find("a", {"class": "a-link-normal s-no-outline"})
        if not atag:
            # Alternative: find any link in the item
            atag = item.find("a", href=True)

        if not atag:
            return None

        url = "https://www.amazon.com" + atag.get("href")

    except (AttributeError, TypeError):
        return None

    try:
        # product price
        price_parent = item.find("span", "a-price")
        price = price_parent.find("span", "a-offscreen").text
    except (AttributeError, TypeError):
        return None

    try:
        # rating
        rating_tag = item.find("span", {"class": "a-icon-alt"})
        rating = rating_tag.text if rating_tag else ""

        # review count - look for the span with review count inside
        review_span = item.find("span", {"class": "a-size-base s-underline-text"})
        if not review_span:
            # Alternative selector
            review_span = item.find(
                "span",
                {"class": "a-size-mini puis-normal-weight-text s-underline-text"},
            )

        review_count = review_span.text.strip() if review_span else ""

    except (AttributeError, TypeError):
        rating = ""
        review_count = ""

    result = (description, price, rating, review_count, url)

    return result


def main(search_term):
    """Run main program routine"""

    # Setup Edge options
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
    )

    # Suppress console logs
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_experimental_option("useAutomationExtension", False)

    # Use your manually downloaded driver
    service = Service(r"C:\EdgeDriver\msedgedriver.exe")
    driver = webdriver.Edge(service=service, options=options)

    records = []
    url = get_url(search_term)

    for page in range(1, 5):
        print(f"Scraping page {page}...")
        driver.get(url.format(page))

        # Wait for search results to load
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div[data-" "component-type='s-search-result']")
                )
            )
        except:
            print("  ⚠️ Timeout waiting for results")

        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        results = soup.find_all("div", {"data-component-type": "s-search-result"})

        page_count = 0
        for item in results:
            record = extract_record(item)
            if record:
                records.append(record)
                page_count += 1

        print(f"  ✅ Extracted {page_count} products on page {page}")

        # Break if no results found (reached end of results)
        if page_count == 0:
            print("No more results found. Stopping...")
            break

    driver.quit()

    # save data to csv file
    with open("results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Description", "Price", "Rating", "ReviewCount", "Url"])
        writer.writerows(records)

    print(f"\n✅ Total: {len(records)} products scraped. Saved to results.csv")


if __name__ == "__main__":
    main("ultrawide monitor")
