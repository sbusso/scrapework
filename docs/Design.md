# Scrapework Design

This document outlines the design and components of the Scraperwork Framework, a Python-based framework inspired by Scrapy but designed to be more in-process oriented and accessible.

## Overview

The Scraperwork Framework follows a layered architecture that separates the scraping process into distinct stages. Each stage is responsible for a specific task and can be customized and extended to meet the requirements of different scraping scenarios.

The main components of the framework are:

1. Request
2. Parsers
3. Validators
4. Item Processors
5. Output Handlers
6. Observers

These components work together to fetch web pages, extract structured data, process and validate the extracted data, and handle the output or storage of the scraped data.

## Request

The Request Layer is responsible for handling HTTP requests and managing the request flow. It consists of the following components:

### Client

The Client is the core component that sends HTTP requests and receives responses. By default, the framework uses the `httpx` library as the HTTP client, but it can be easily overridden or customized.

### RequestMiddleware

RequestMiddleware are components that sit between the Client and the request flow. They can intercept and modify the requests before they are sent. Middleware can be used to add functionality such as caching, header manipulation, proxy support, or authentication.

The framework provides a `Scraper.use(RequestMiddleware, **kwargs)` method to add middleware to the request flow. Multiple middleware can be added, and they are executed in the order they are registered.

Examples of RequestMiddleware:

- `CacheMiddleware`: Caches the responses to avoid redundant requests.
- `HeaderMiddleware`: Adds custom headers to the requests.
- `ProxyMiddleware`: Enables the use of proxies for requests.

## Parsers

Parsers are responsible for extracting structured data from the HTML or XML responses. They take the raw response and extract relevant information based on defined rules or patterns.

The framework provides a `Scraper.use(Parser, **kwargs)` method to add parsers to the scraping flow. Multiple parsers can be used to extract different types of data from the same response.

Examples of Parsers:

- `ProductExtractor`: Extracts product information from an e-commerce website.
- `PriceExtractor`: Extracts price data from a webpage.
- `LinkExtractor`: Extracts URLs from a webpage for further crawling.

## Validators

Validators are components that validate the extracted and processed data. They ensure data integrity, format consistency, and perform data quality checks. Validators can verify data types, check field formats, validate constraints, and identify any discrepancies or anomalies in the extracted data.

The framework provides a `Scraper.use(Validator, **kwargs)` method to add validators to the scraping flow. Multiple validators can be used to perform different types of validations.

Examples of Validators:

- `FormatValidator`: Validates the format of extracted data fields, such as dates, URLs, or email addresses.
- `RangeValidator`: Checks if the extracted numeric values fall within a specified range.
- `RequiredFieldValidator`: Ensures that required fields are present and not empty.
- `UniqueValidator`: Verifies the uniqueness of extracted items based on specified fields.

Validators can raise exceptions or log warnings when validation fails, allowing the scraping process to handle and report errors appropriately.

## Item Processors

Item Processors are components that take the extracted data items and perform additional processing, transformation, or validation. They can modify the data, enrich it with additional information, or filter out unwanted items.

The framework provides a `Scraper.use(Processor, **kwargs)` method to add item processors to the pipeline. Multiple processors can be chained together to perform a series of processing steps.

Examples of Item Processors:

- `PriceConverter`: Converts prices from one currency to another.
- `ImageDownloader`: Downloads and saves images associated with the scraped items.
- `DuplicateFilter`: Filters out duplicate items based on certain criteria.

## Output Handlers

Output Handlers are responsible for handling the output or storage of the scraped data. They take the processed data items and save them to various destinations such as files, databases, or cloud storage services.

The framework provides a `Scraper.use(OutputHandler, **kwargs)` method to add output handlers to the pipeline. Multiple handlers can be used to store the data in different formats or locations.

Examples of Output Handlers:

- `JsonFileHandler`: Saves the scraped data as a JSON file.
- `CsvFileHandler`: Saves the scraped data as a CSV file.
- `DatabaseHandler`: Stores the scraped data in a database.
- `S3Handler`: Uploads the scraped data to Amazon S3.

## Observers

Observers are components that monitor and observe the scraping process. They track various metrics, statistics, and events related to the scraping operation. Observers provide insights into the progress, performance, and health of the scraper.

The framework provides a `Scraper.use(Observer, **kwargs)` method to add observers to the scraping flow. Multiple observers can be used to monitor different aspects of the scraping process.

Examples of Observers:

- `ProgressObserver`: Tracks the progress of the scraping process, such as the number of pages visited and items extracted.
- `PerformanceObserver`: Measures the performance metrics of the scraper, such as request latency and processing time.
- `ErrorObserver`: Keeps track of any errors or exceptions encountered during the scraping process.
- `LoggingObserver`: Logs various events and statistics related to the scraping operation.

Observers can report metrics, statistics, and observations to external systems, dashboards, or logging platforms for monitoring, analysis, and alerting purposes.

## Reporters

Reporters are components that gather metadata, validation results, and other information from various parts of the scraper, including observers, validators, and pipelines. They process and format the collected data and push it to external channels for reporting and notification purposes.

The framework provides a `Scraper.use(Reporter, **kwargs)` method to add reporters to the scraping flow. Multiple reporters can be used to send data to different channels or destinations.

Examples of Reporters:

- `EmailReporter`: Collects metadata and sends a summary report via email.
- `SlackReporter`: Pushes real-time updates and notifications to a Slack channel.
- `DatabaseReporter`: Stores the collected metadata and reports in a database for further analysis.
- `LoggingReporter`: Logs the gathered information to a file or a logging service.

Reporters can be configured with specific settings, such as email addresses, Slack webhook URLs, database connections, or logging levels, depending on the reporting destination.

## Usage

To use the Web Scraper Framework, you need to create a subclass of the `Scraper` class and define a `configuration` method to set up the scraper's components. Here's an example:

```python
from scraper import Scraper
from middleware import CacheMiddleware
from validators import FormatValidator, RequiredFieldValidator
from observers import ProgressObserver, ErrorObserver
from handlers import MetadataHandler, JsonFileHandler

class Spidy(Scraper):
    name = "spidy"

    def __init__(self, start_urls):
        super().__init__(start_urls)

    def configuration(self):
        self.use(CacheMiddleware, cache_dir="cache")
        self.use(FormatValidator)
        self.use(RequiredFieldValidator, fields=["title", "price"])
        self.use(MetadataHandler)
        self.use(JsonFileHandler, output_file="output.json")
        self.use(ErrorObserver)
        self.use(EmailReporter, email_to="admin@example.com")
        self.use(SlackReporter, webhook_url="https://hooks.slack.com/...")
```

In this example, the `Spidy` class is defined as a subclass of `Scraper`. The `configuration` method is overridden to specify the components to be used by the scraper. The `use` method is called to add middleware, handlers, and other components to the scraper.

To start the scraper, create an instance of the `Spidy` class and call the `start` method:

```python
start_urls = ["https://example.com", "https://example.org"]
spidy = Spidy(starts_urls=start_urls)
spidy.run()
```

## Extending the Framework

The Web Scraper Framework is designed to be extensible and customizable. You can create your own middleware, parsers, item processors, and output handlers by implementing the corresponding base classes provided by the framework.

For example, to create a custom RequestMiddleware:

```python
from scraper import RequestMiddleware

class CustomMiddleware(RequestMiddleware):
    def process_request(self, request):
        # Modify the request
        request.headers["Custom-Header"] = "Value"
        return request
```

Similarly, you can create custom parsers, item processors, and output handlers by subclassing the respective base classes.

## Conclusion

The Web Scraper Framework provides a flexible and modular architecture for building web scrapers in Python. By separating the scraping process into distinct layers and providing extensibility through middleware, parsers, item processors, and output handlers, the framework allows developers to easily customize and adapt the scraping workflow to their specific needs.

With its intuitive design and powerful features, the Web Scraper Framework simplifies the task of web scraping and enables developers to focus on extracting valuable data efficiently.

For more detailed information and examples, please refer to the framework's API documentation and user guide.
