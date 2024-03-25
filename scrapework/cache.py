import os
from pathlib import Path
from typing import Optional

import hishel

from scrapework.core.context import Context
from scrapework.core.logger import Logger
from scrapework.middleware import RequestMiddleware
from scrapework.request import HTTPClient, Request


class HishelClient(HTTPClient):
    @classmethod
    def build_client(cls, **kwargs) -> hishel.CacheClient:
        Logger().get_logger().debug("Building cache http client.")
        return hishel.CacheClient(**kwargs)


class CacheMiddleware(RequestMiddleware):
    controller: Optional[hishel.Controller] = None
    storage: Optional[hishel.FileStorage] = None
    cache_dir: Optional[str] = None

    def __init__(self, cache_dir: str, ttl: int = 3600):
        super().__init__()
        self.controller = hishel.Controller(
            # Cache only GET and POST methods
            cacheable_methods=["GET", "POST"],
            # Cache only 200 status codes
            cacheable_status_codes=[200],
            # Use the stale response if there is a connection issue and the new response cannot be obtained.
            allow_stale=True,
            # First, revalidate the response and then utilize it.
            # If the response has not changed, do not download the
            # entire response data from the server; instead,
            # use the one you have because you know it has not been modified.
            always_revalidate=True,
        )
        cache_dir_path = os.path.join(os.getcwd(), cache_dir)

        if not os.path.exists(cache_dir_path):
            os.mkdir(cache_dir_path)

        serializer = hishel.PickleSerializer()

        self.storage = hishel.FileStorage(
            serializer=serializer, base_path=Path(cache_dir_path), check_ttl_every=ttl
        )

        self.cache_dir = cache_dir

    class Config:
        arbitrary_types_allowed = True

    def process_request(self, ctx: Context, request: Request):
        self.logger.debug(f"Using cache middleware with cache dir: {self.cache_dir}")
        request.cls_client = HishelClient
        request.client_kwargs["controller"] = self.controller
        request.client_kwargs["storage"] = self.storage
        request.request_kwargs["extensions"] = {"force_cache": True}
        return request
