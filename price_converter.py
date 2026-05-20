"""Scrape book prices and convert them to another currency."""

import requests
from bs4 import BeautifulSoup


BOOKS_URL = "https://books.toscrape.com/"
RATES_URL = "https://api.frankfurter.app/latest"
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


def get_exchange_rate(from_currency, to_currency):
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    if from_currency == to_currency:
        return 1.0

    params = {
        "from": from_currency,
        "to": to_currency,
    }
    response = requests.get(RATES_URL, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()
    return float(data["rates"][to_currency])


def convert_books(books, rate):
    converted_books = []

    for book in books:
        converted_books.append({
            "title": book["title"],
            "price": book["price"],
            "converted_price": book["price"] * rate,
        })

    return converted_books


def main():
    print("Price Scraper + Currency Converter")
    books = scrape_books()
    rate = get_exchange_rate("GBP", "USD")
    converted_books = convert_books(books, rate)

    for book in converted_books:
        print(f"{book['title']} - {book['converted_price']:.2f}")


if __name__ == "__main__":
    main()
