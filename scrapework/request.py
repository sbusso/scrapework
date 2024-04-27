import logging
from typing import Any, Dict

import httpx
from httpx import URL, Client, HTTPError, TimeoutException
from playwright.sync_api import Request as pRequest
from playwright.sync_api import Route, sync_playwright

from scrapework.core.http_client import HTTPClient, HttpxClient


class Request:
    url: str
    request_url: str
    logger: logging.Logger
    headers: Dict[str, str] = {}
    timeout: int = 10
    follow_redirects: bool = False
    proxy: str | None = None
    retries: int = 0
    cls_client: type[HTTPClient] = HttpxClient
    client_kwargs: Dict[str, Any] = {}
    request_kwargs: Dict[str, Any] = {}
    playwright: bool = False

    def __init__(self, url: str, **kwargs):
        self.url = url
        self.request_url = url
        self.logger = kwargs.get("logger", logging.getLogger("request"))
        self.headers = kwargs.get("headers", {})
        self.timeout = kwargs.get("timeout", 10)
        self.follow_redirects = kwargs.get("follow_redirects", False)
        # self.proxy = kwargs.get("proxy", None)
        self.retries = kwargs.get("retries", 0)
        self.cls_client = kwargs.get("cls_client", HttpxClient)
        self.client_kwargs = kwargs.get("client_kwargs", {})
        self.request_kwargs = kwargs.get("request_kwargs", {})

    class Config:
        arbitrary_types_allowed = True

    def urljoin(self, url: str) -> str:
        return str(URL(self.url).join(URL(url)))

    def httpx_request_handler(
        self, route: Route, request: pRequest, client: httpx.Client
    ):

        # Extract request details from Playwright's Request object
        method = request.method
        url = request.url
        headers = dict(request.headers)
        # data = request.post_data

        try:
            # Perform the request using HTTPX client
            response = client.request(
                method,
                url,
                headers=headers,
                **self.request_kwargs,
            )

            # Return the response to Playwright

            route.fulfill(
                status=response.status_code,
                headers=dict(response.headers),
                body=response.content,
            )
        except Exception as e:
            self.logger.error(f"Error: {e} fetching {url}")
            route.abort()

    def fetch_playwright(self, httpx_client: Client) -> httpx.Response:

        with sync_playwright() as p:
            browser = p.chromium.launch()

            page = browser.new_page()

            page.route(
                "**/*",
                lambda route, request: self.httpx_request_handler(
                    route, request, httpx_client
                ),
            )

            page.goto(self.url)
            content = page.content()
            browser.close()

        return httpx.Response(
            200,
            request=httpx.Request("GET", self.url),
            content=content.encode("utf-8"),
            headers={},
        )

    def fetch(self) -> httpx.Response:
        """
        Fetches the HTML content of a given URL.

        :param cache: The cache object used for caching the fetched HTML content.
        :param url: The URL to fetch.

        :return: The fetched HTML content as a string, or None if there was an error.
        """

        if self.proxy:
            self.logger.debug(f"Using proxy: {self.proxy}")
            mounts = {
                "https://": httpx.HTTPTransport(proxy=self.proxy),
                "http://": httpx.HTTPTransport(proxy=self.proxy),
            }
        else:
            mounts = {}
        client = self.cls_client.build_client(
            headers=self.headers,
            timeout=self.timeout,
            follow_redirects=self.follow_redirects,
            mounts=mounts,
            **self.client_kwargs,
        )
        try:
            if self.playwright:
                return self.fetch_playwright(client)

            response: httpx.Response = client.get(
                self.request_url,
                **self.request_kwargs,
            )

            response.request.url = URL(self.url)
            return response

        except TimeoutException as err:
            self.logger.error(f"TimeoutError fetching {self.url}: {err}")  # type: ignore
            raise err

        except HTTPError as err:
            self.logger.error(f"HTTPError fetching {self.url}: {err}")  # type: ignore
            raise err

        except Exception as err:
            self.logger.error(f"Exception fetching {self.url}: {err}")  # type: ignore
            raise err

        finally:
            client.close()
