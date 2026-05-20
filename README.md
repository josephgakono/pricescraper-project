# Price Scraper + Currency Converter

This project scrapes book names and prices from [Books to Scrape](https://books.toscrape.com/), converts the prices to another currency, prints a small table, and saves the results.

## Run

```bash
python price_converter.py
```

The program asks for:

- the currency used for the scraped prices
- the currency to convert into
- whether to save a CSV or JSON file

Books to Scrape lists prices in GBP, so `GBP` is the usual source currency.
The exchange rates come from a free exchange-rate API.

## Files

- `price_converter.py` - main program
- `requirements.txt` - packages used by the program
- `results.csv` or `results.json` - created after a successful run
