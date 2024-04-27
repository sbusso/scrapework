# Scrapework

Scrapework is a simple and opiniatated framework to extract data from the web. It is inspired by Scrapy and designed for simple tasks and easy management, allowing you to focus on the scraping logic. It is built on top of `parsel` (used by Scrapy) and `httpx` libraries. Some of the key differences are:

- No CLI
- No twisted framework
- Designed for in-process usage

## Installation

First, clone the repository or install as a dependencies:

With pip:

```sh
pip install scrapework
```

With poetry:

```sh
poetry add scrapework
```

## Quick Start

### Create a Scraper

First, create a Scraper class to define how extract data and optionally navigate a website. Here's how you can create a simple Scraper:

```python
from scrapework.scraper import Scraper

class SimpleScraper(Scraper):
    name = "simple_scraper"

    def extract(self, ctx, selector):
        for quote in selector.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').get(),
                'author': quote.css('span small::text').get(),
            }

    def process(self, items, config):
        for item in items:
            print(f"Quote: {item['text']}, Author: {item['author']}")


scraper = SimpleScraper()
scraper.run(['http://quotes.toscrape.com'])

```

Similar to Scrapy `parse`, the `extract` method is an expected and this is where you define your scraping logic. It's called with the HTTP response of the initial URL. You can use the `parsel.Selector` object to extract data from the HTML using `css` or `xpath`.

To run the Scraper, you need to create an instance and call the `run` method passing the URLs to scrape:

```python
scraper = SimpleScraper()
scraper.run(['http://quotes.toscrape.com'])
```

### Modules Configuration

Scrapework can be extended using modules:

- `middleware` to configure the request handling (chache, proxy, ...).
- `handlers`: to export the data, save them to file or database.
- `reporters`: to export and log the scraping events and metadata.

## Flow

The scraping flow consists of the following steps:

1. **Webpage downloading**: Fetch the webpages using `httpx`. Optionally, use `middleware` to handle requests.
2. **Extract data**: Extract structured data from the HTML using `parsers`.
3. **Export data**: Use `handlers` to store or export the structured data.
4. **Reporting**: Generate reports and logs of the scraping process using `reporters`.

For more details see [Design](docs/Design.md).

## Advanced Usage

For more advanced usage, you can override other methods in the Scraper, Parser, and Pipeline classes. Check the source code for more details.

### Add Parser

Alternatively, you can create a Parser class to define how to extract data from a webpage. Here's how you can create an Parser and configure it in the Scraper:

```python
from scrapework.parsers import Parser, Scraper

class SimpleScraper(Scraper):
    name = "simple_scraper"
    parser = SimpleParser()

class SimpleParser(Parser):
    def extract(self, ctx, selector):
        return {
            'text': selector.css('span.text::text').get(),
            'author': selector.css('span small::text').get(),
        }
```

The `extract` method is where you define your extraction logic. It's called passing a `parsel.Selector` object that you can use to extract data from the HTML using `css` or `xpath`.

### Add a data handler

Similar to a pipeline, an `handler` defines how to process and store the data:

```python
from scrapework.handlers import Handler

class SimpleHandler(Handler):
    def process_items(self, items, config):
        for item in items:
            print(f"Quote: {item['text']}, Author: {item['author']}")
```

The `process_items` method is where you define your processing logic. It's called with the items extracted by the Parser and a `PipelineConfig` object.

```python
scraper = SimpleScraper()

scraper.use(SimpleHandler())
```

## Testing

To run the tests, use the following command:

```sh
pytest tests/
```

using playwright:

```sh
playwright install
```

## Contributing

Contributions are welcome! Please read the contributing guidelines first.

## License

Scrapework is licensed under the MIT License.
