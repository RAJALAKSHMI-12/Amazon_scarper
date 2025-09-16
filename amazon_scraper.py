# amazon_scraper_limit.py

import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


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
        time.sleep(3)  # wait for content to load

        items = driver.find_elements(By.XPATH, "//div[@data-component-type='s-search-result']")

        for item in items:
            if len(products) >= num_products:  # stop if we reached limit
                break

            try:
                title = item.find_element(By.TAG_NAME, "h2").text
            except:
                title = None

            try:
                price = item.find_element(By.CLASS_NAME, "a-price-whole").text
            except:
                price = None

            try:
                rating = item.find_element(By.XPATH, ".//span[@class='a-icon-alt']").text
            except:
                rating = None

            try:
                reviews = item.find_element(By.XPATH, ".//span[@class='a-size-base']").text
            except:
                reviews = None

            try:
                image = item.find_element(By.TAG_NAME, "img").get_attribute("src")
            except:
                image = None

            products.append({
                "Title": title,
                "Price": price,
                "Rating": rating,
                "Reviews": reviews,
                "Image_URL": image
            })

        page += 1  # go to next page if needed

    driver.quit()

    # Save results to Excel
    df = pd.DataFrame(products)
    file_name = f"amazon_{search_query.replace(' ', '_')}_{num_products}_products.xlsx"
    df.to_excel(file_name, index=False)
    print(f"✅ Scraped {len(products)} products and saved to {file_name}")


if __name__ == "__main__":
    search = input("Enter the product to search on Amazon: ")
    num_products = int(input("Enter number of products to scrape: "))
    amazon_scraper(search, num_products)
