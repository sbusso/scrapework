class Middleware:
    def process_request(self, request):
        raise NotImplementedError


class MiddlewareAnonymousHeader(Middleware):
    def process_request(self, request):
        request.headers.update({"User-Agent": "Anonymous"})
        return request


class MiddlewareDefaultHeaders(Middleware):
    def process_request(self, request):
        request.headers.update({"User-Agent": "Mozilla/5.0"})
        return request
