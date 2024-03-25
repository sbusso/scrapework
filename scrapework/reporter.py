from abc import abstractmethod

import httpx

from scrapework.core.context import Context
from scrapework.module import Module


class Reporter(Module):

    @abstractmethod
    def report(self, ctx: Context):
        pass


class LoggerReporter(Reporter):
    def report(self, ctx: Context):
        self.logger.info(
            f"Processed {ctx.collector.get('items_count')} items in {ctx.collector.get('duration')}s."
        )


class SlackReporter(Reporter):
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def report(self, data):
        message = self._format_message(data)
        self._send_to_slack(message)

    def _format_message(self, data):
        # Format the data into a Slack-compatible message
        message = {
            "text": "Web Scraper Report",
            "attachments": [
                {
                    "title": "Scraping Results",
                    "color": "#36a64f",
                    "fields": [
                        {
                            "title": "Pages Visited",
                            "value": str(data.get("pages_visited", 0)),
                            "short": True,
                        },
                        {
                            "title": "Items Extracted",
                            "value": str(data.get("items_extracted", 0)),
                            "short": True,
                        },
                        {
                            "title": "Errors Encountered",
                            "value": str(data.get("errors_encountered", 0)),
                            "short": True,
                        },
                    ],
                }
            ],
        }
        return message

    def _send_to_slack(self, message):
        # Send the formatted message to Slack using the webhook URL
        response = httpx.post(self.webhook_url, json=message)
        if response.status_code != 200:
            print(
                f"Failed to send report to Slack. Status code: {response.status_code}"
            )
