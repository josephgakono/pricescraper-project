"""Scrape book prices and convert them to another currency."""

import requests
from bs4 import BeautifulSoup


BOOKS_URL = "https://books.toscrape.com/"
BOOK_LIMIT = 10


def scrape_books():
    response = requests.get(BOOKS_URL, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    book_cards = soup.select("article.product_pod")
    books = []

    for card in book_cards[:BOOK_LIMIT]:
        title = card.h3.a["title"]
        price_text = card.select_one(".price_color").get_text(strip=True)
        price = float(price_text.replace("£", ""))

        books.append({
            "title": title,
            "price": price,
        })

    return books


def main():
    print("Price Scraper + Currency Converter")
    books = scrape_books()

    for book in books:
        print(f"{book['title']} - {book['price']:.2f}")


if __name__ == "__main__":
    main()
