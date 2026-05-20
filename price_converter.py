"""Scrape book prices and convert them to another currency."""

import csv
import json
from datetime import datetime

import requests
from bs4 import BeautifulSoup


BOOKS_URL = "https://books.toscrape.com/"
RATES_URL = "https://open.er-api.com/v6/latest/"
BOOK_LIMIT = 10
COMMON_CURRENCIES = "KES, EUR, USD, GBP, CAD, AUD, JPY, CHF, NOK, SEK"


def scrape_books():
    response = requests.get(BOOKS_URL, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    book_cards = soup.select("article.product_pod")
    books = []

    for card in book_cards[:BOOK_LIMIT]:
        title = card.h3.a["title"]
        price_text = card.select_one(".price_color").get_text(strip=True)
        price = clean_price(price_text)

        books.append({
            "title": title,
            "price": price,
        })

    if len(books) == 0:
        raise ValueError("No books were found on the page.")

    return books


def clean_price(price_text):
    number_text = ""

    for character in price_text:
        if character.isdigit() or character == ".":
            number_text += character

    return float(number_text)


def get_exchange_rate(from_currency, to_currency):
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    if from_currency == to_currency:
        return 1.0

    response = requests.get(RATES_URL + from_currency, timeout=10)
    response.raise_for_status()

    data = response.json()

    if data.get("result") != "success":
        raise ValueError("The exchange-rate API did not return a rate.")

    if "rates" not in data or to_currency not in data["rates"]:
        raise ValueError("That currency could not be converted by the rate API.")

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


def ask_for_currency(label, default):
    answer = input(f"{label} currency ({COMMON_CURRENCIES}) [{default}]: ").strip()

    if answer == "":
        return default

    return answer.upper()


def ask_for_save_type():
    answer = input("Save as CSV or JSON? [csv]: ").strip().lower()

    if answer == "":
        return "csv"

    if answer not in ("csv", "json"):
        print("Unknown choice, saving as CSV.")
        return "csv"

    return answer


def shorten_title(title, limit=42):
    if len(title) <= limit:
        return title

    return title[:limit - 3] + "..."


def print_table(books, from_currency, to_currency, timestamp):
    print()
    print(f"Converted at: {timestamp}")
    print()
    print(f"{'No.':<4} {'Book':<45} {from_currency:>10} {to_currency:>10}")
    print("-" * 73)

    for number, book in enumerate(books, start=1):
        title = shorten_title(book["title"])
        print(
            f"{number:<4} "
            f"{title:<45} "
            f"{book['price']:>10.2f} "
            f"{book['converted_price']:>10.2f}"
        )


def save_as_csv(books, from_currency, to_currency, timestamp, filename):
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "title", from_currency, to_currency])

        for book in books:
            writer.writerow([
                timestamp,
                book["title"],
                f"{book['price']:.2f}",
                f"{book['converted_price']:.2f}",
            ])


def save_as_json(books, from_currency, to_currency, timestamp, filename):
    saved_books = []

    for book in books:
        saved_books.append({
            "timestamp": timestamp,
            "title": book["title"],
            from_currency: round(book["price"], 2),
            to_currency: round(book["converted_price"], 2),
        })

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(saved_books, file, indent=2)


def save_results(books, from_currency, to_currency, timestamp, save_type):
    filename = f"results.{save_type}"

    if save_type == "json":
        save_as_json(books, from_currency, to_currency, timestamp, filename)
    else:
        save_as_csv(books, from_currency, to_currency, timestamp, filename)

    print()
    print(f"Saved results to {filename}")


def main():
    print("Price Scraper + Currency Converter")
    print("Books to Scrape uses GBP prices.")

    from_currency = ask_for_currency("Source", "GBP")
    to_currency = ask_for_currency("Target", "USD")
    save_type = ask_for_save_type()

    try:
        books = scrape_books()
        rate = get_exchange_rate(from_currency, to_currency)
        converted_books = convert_books(books, rate)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print_table(converted_books, from_currency, to_currency, timestamp)
        save_results(converted_books, from_currency, to_currency, timestamp, save_type)
    except requests.exceptions.RequestException:
        print()
        print("Could not connect to the book site or exchange-rate API.")
        print("Check your internet connection and try again.")
    except ValueError as error:
        print()
        print(f"Problem: {error}")


if __name__ == "__main__":
    main()
