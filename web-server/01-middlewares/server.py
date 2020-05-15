import logging
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO


class Request:
    """Provider interface to visit HTTP request information"""
    def __init__(self, handler: BaseHTTPRequestHandler):
        self._handler = handler

    @property
    def path(self) -> str:
        path, _ = urllib.parse.splitquery(self._handler.path)
        return path

    def query_string(self, key: str, default: str = None) -> str:
        _, qs = urllib.parse.splitquery(self._handler.path)
        args = dict(urllib.parse.parse_qsl(qs))
        return args.get(key, default)


class Response:
    """Provide interface to write HTTP response"""
    def __init__(self, handler: BaseHTTPRequestHandler):
        self._handler = handler
        self._status = 200
        self._headers = {}
        self._data = BytesIO()

    def header(self, key: str, value: str):
        self._headers[key] = value
        return self

    def status(self, code: int):
        self._status = code
        return self

    def data(self, content: bytes):
        self._data.write(content)
        return self

    def html(self, text: str):
        self.data(text.encode('utf8'))
        self._headers.setdefault('Content-Type', 'text/html; charset=utf-8')
        return self

    def send(self):
        self._handler.send_response(self._status)
        resp_data = self._data.getvalue()
        self._headers.setdefault('Content-Length', len(resp_data))
        for k, v in self._headers.items():
            self._handler.send_header(k, v)
        self._handler.end_headers()
        self._handler.wfile.write(resp_data)


class HttpContext:
    """Bundle request/response information for each middleware to process"""
    def __init__(self, handler: BaseHTTPRequestHandler):
        self.request = Request(handler)
        self.response = Response(handler)
        self.error = None


class Middleware:
    """Base class to implement HTTP process middleware."""
    def handle(self, ctx: HttpContext) -> bool:
        """If implemented, it should output response headers & data, and return True.
           The process pipeline will stop iteration when any middleware handled the task."""
        raise NotImplementedError()


class ServerHeader(Middleware):
    """Output a generic header for all response"""
    def handle(self, ctx: HttpContext) -> bool:
        ctx.response.header('X-Server-Type', '500lines server (testonly)')
        return False


class Index(Middleware):
    """Provider a dummy index response.
       if request with query ?err=1, then raise an error (for test purpose)."""
    def handle(self, ctx: HttpContext) -> bool:
        if ctx.request.path == '/':
            if ctx.request.query_string('err', '0') == '1':
                raise Exception('test error')
            else:
                ctx.response.html('<h1>Index</h1>')
            return True
        return False


class NotFound(Middleware):
    """Response for HTTP Not Found Error(404)"""
    def handle(self, ctx: HttpContext) -> bool:
        ctx.response.status(404).html('<h1>File Not Found</h1>')
        return True


class GenericError(Middleware):
    """Response for generic pipeline error"""
    def handle(self, ctx: HttpContext) -> bool:
        if ctx.error:
            logging.getLogger('server').error(str(ctx.error))
        ctx.response.status(500).html('<h1>Internal Server Error</h1>')
        return True


class RequestDispatcher(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        """Define middleware process pipeline"""
        self._middlewares = [
            ServerHeader(),
            Index(),
            NotFound(),
        ]
        self._catchall = GenericError()
        super(RequestDispatcher, self).__init__(request, client_address, server)

    def do_GET(self):
        """call each middleware to process request.
           if any error occuried, then use _catchall to handle exception."""
        ctx = HttpContext(self)
        try:
            for middleware in self._middlewares:
                if middleware.handle(ctx):
                    ctx.response.send()
                    break
        except Exception as e:
            ctx.error = e
            self._catchall.handle(ctx)
            ctx.response.send()


if __name__ == '__main__':
    addr = ('', 8080)
    server = HTTPServer(addr, RequestDispatcher)
    server.serve_forever()
