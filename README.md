# Scrapework

Scrapework is a simple and opiniatated scraping framework inspired by Scrapy. It's designed for simple tasks and easy management, allowing you to focus on the scraping logic and not on the boilerplate code.

- No CLI
- No twisted framework
- Designed for in-process usage

## Getting Started

### Installation

First, clone the repository or install as a dependencies:

```sh
poetry add scrapework
```

### Quick Start

Flow:

1. **Request Handling**: Use the `make_request` method to fetch web pages from `start_urls` with the help of `middlewares`.
2. **Data Extraction**: Implement the `extract` method to parse and extract structured data from the fetched pages using `HTMLBodyParser` or other custom logic.
3. **Data Processing**: Process and handle the structured data using `handlers` defined in the scraper.
4. **Reporting**: Generate reports of the scraping process using `reporters`.

For more details see [Design](docs/Design.md).

### Scraper Configuration

- `start_urls`: A list of URLs to start scraping from.
- request middleware to configure the request handling.
- parsers: comes with various extractors (plain body, smart extractors, markedown.)
- handlers: comes with various handlers (log, save to file, save to database.)
- reporters

### Creating a Spider

A Spider is a class that defines how to navigate a website and extract data. Here's how you can create a Spider:

```python
from scrapework.spider import Spider

class MyScraper(Scraper):
    start_urls = ['http://quotes.toscrape.com']

    def parse(self, response):
        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').get(),
                'author': quote.css('span small::text').get(),
            }
```

The `parse` method is where you define your scraping logic. It's called with the HTTP response of the initial URL.

### Creating an Extractor

An Extractor is a class that defines how to extract data from a webpage. Here's how you can create an Extractor:

```python
from scrapework.extractors import Extractor

class MyExtractor(Extractor):
    def extract(self, selector):
        return {
            'text': selector.css('span.text::text').get(),
            'author': selector.css('span small::text').get(),
        }
```

The `extract` method is where you define your extraction logic. It's called with a `parsel.Selector` object that you can use to extract data from the HTML.

### Creating a Pipeline

A Pipeline is a class that defines how to process and store the data. Here's how you can create a Pipeline:

```python
from scrapework.pipelines import ItemPipeline

class MyPipeline(ItemPipeline):
    def process_items(self, items, config):
        for item in items:
            print(f"Quote: {item['text']}, Author: {item['author']}")
```

The `process_items` method is where you define your processing logic. It's called with the items extracted by the Extractor and a `PipelineConfig` object.

### Running the Spider

To run the Spider, you need to create an instance of it and call the `start_requests` method:

```python
spider = MySpider()
spider.start_requests()
```

## Advanced Usage

For more advanced usage, you can override other methods in the Spider, Extractor, and Pipeline classes. Check the source code for more details.

## Testing

To run the tests, use the following command:

```sh
pytest tests/
```

## Contributing

Contributions are welcome! Please read the contributing guidelines first.

## License

Scrapework is licensed under the MIT License.
