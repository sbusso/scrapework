import logging
from typing import Dict

import httpx
from httpx import HTTPError, TimeoutException
from pydantic import BaseModel


class Request(BaseModel):
    url: str
    logger: logging.Logger
    headers: Dict[str, str] = {}
    timeout: int = 10
    follow_redirects: bool = False
    proxy: str | None = None
    retries: int = 0

    class Config:
        arbitrary_types_allowed = True

    def fetch(self) -> httpx.Response:
        """
        Fetches the HTML content of a given URL.

        :param cache: The cache object used for caching the fetched HTML content.
        :param url: The URL to fetch.

        :return: The fetched HTML content as a string, or None if there was an error.
        """
        if self.proxy:
            mounts = {
                "https://": httpx.HTTPTransport(proxy=self.proxy),
                "http://": httpx.HTTPTransport(proxy=self.proxy),
            }
        else:
            mounts = {}
        try:
            with httpx.Client(
                headers=self.headers,
                timeout=self.timeout,
                follow_redirects=self.follow_redirects,
                mounts=mounts,
            ) as client:

                request = client.build_request(
                    "GET",
                    self.url,
                )

                response = client.send(request)

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
