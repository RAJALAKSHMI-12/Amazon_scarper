# amazon_scraper_with_rating.py

import time
import random
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def amazon_scraper(search_query, num_products):
    # Selenium setup
    options = Options()
    options.add_argument("--headless")   # run without opening browser
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    base_url = "https://www.amazon.in/s?k=" + search_query.replace(" ", "+")
    products = []
    page = 1

    while len(products) < num_products:
        url = f"{base_url}&page={page}"
        print(f"🔎 Scraping page {page}... {url}")
        driver.get(url)

        # wait until product results are loaded
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[@data-component-type='s-search-result']"))
            )
        except:
            print("⚠️ No products found on this page, stopping...")
            break

        items = driver.find_elements(By.XPATH, "//div[@data-component-type='s-search-result']")

        if not items:
            break

        for item in items:
            if len(products) >= num_products:
                break

            try:
                title = item.find_element(By.TAG_NAME, "h2").text
            except:
                title = None

            try:
                price = item.find_element(By.CLASS_NAME, "a-price-whole").text
            except:
                price = None

            # ✅ FIXED: Always fill rating
            try:
                rating_element = item.find_element(By.XPATH, ".//span[@class='a-icon-alt']")
                rating_text = rating_element.text.strip()
                rating_match = re.search(r"[\d.]+", rating_text)
                rating = rating_match.group(0) if rating_match else rating_text
            except:
                rating = "No Rating"

            try:
                reviews = item.find_element(By.XPATH, ".//span[@class='a-size-base s-underline-text']").text
            except:
                reviews = "No Reviews"

            try:
                image = item.find_element(By.TAG_NAME, "img").get_attribute("src")
            except:
                image = None

            try:
                link = item.find_element(By.TAG_NAME, "a").get_attribute("href")
            except:
                link = None

            products.append({
                "Title": title,
                "Price": price,
                "Rating": rating,
                "Reviews": reviews,
                "Image_URL": image,
                "Product_Link": link
            })

        page += 1
        time.sleep(random.uniform(2, 5))  # small random delay

    driver.quit()

    # Save results to Excel (with Rating)
    df = pd.DataFrame(products, columns=["Title", "Price", "Rating", "Reviews", "Image_URL", "Product_Link"])
    file_name = f"amazon_{search_query.replace(' ', '_')}_{num_products}_products.xlsx"
    df.to_excel(file_name, index=False)
    print(f"✅ Scraped {len(products)} products and saved to {file_name}")


if __name__ == "__main__":
    search = input("Enter the product to search on Amazon: ")
    num_products = int(input("Enter number of products to scrape: "))
    amazon_scraper(search, num_products)