import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from urllib.parse import urljoin

BASE_URL = "http://books.toscrape.com/"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_categories():
    """
    Extract all book categories from homepage.
    Returns dictionary: {category_name: category_url}
    """
    response = requests.get(BASE_URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    category_links = soup.select(".side_categories ul li ul li a")

    categories = {}
    for cat in category_links:
        name = cat.text.strip()
        link = urljoin(BASE_URL, cat["href"])
        categories[name] = link

    return categories


def scrape_category(category_name, category_url):
    """
    Scrapes all pages within a category.
    Returns list of product dictionaries.
    """
    data = []
    page = 1

    while True:
        if page == 1:
            url = category_url
        else:
            url = category_url.replace("index.html", f"page-{page}.html")

        print(f"Scraping {category_name} - Page {page}")

        response = requests.get(url, headers=HEADERS)

        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, "html.parser")
        books = soup.find_all("article", class_="product_pod")

        if not books:
            break

        for book in books:
            try:
                title = book.h3.a["title"]
                price_raw = book.find("p", class_="price_color").text
                rating_raw = book.find("p", class_="star-rating")["class"][1]

                data.append({
                    "Category": category_name,
                    "Title": title,
                    "Price": price_raw,
                    "Rating": rating_raw
                })

            except Exception:
                continue

        page += 1
        time.sleep(1)

    return data


def clean_data(df):
    """
    Cleans price and rating columns.
    """
    # Extract numeric price
    df["Price"] = df["Price"].str.extract(r'(\d+\.\d+)').astype(float)

    # Convert rating text to numeric
    rating_map = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }

    df["Rating"] = df["Rating"].map(rating_map)

    return df


def main():
    print("Starting Multi-Category Product Scraper...\n")

    all_data = []

    categories = get_categories()

    for name, link in categories.items():
        category_data = scrape_category(name, link)
        all_data.extend(category_data)

    df = pd.DataFrame(all_data)

    df = clean_data(df)

    df.to_csv("multi_category_books.csv", index=False)

    print("\nScraping completed successfully!")
    print(f"Total products scraped: {len(df)}")


if __name__ == "__main__":
    main()