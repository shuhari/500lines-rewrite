from http.server import BaseHTTPRequestHandler, HTTPServer


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        resp_text = f"""<h1>Hello World!</h1>
            <p>Client address: {self.client_address}</p>
            <p>Command: {self.command}</p>
            <p>Path: {self.path}</p>
            <p>Headers: {self.headers}</p>
        """
        resp_data = resp_text.encode('utf8')
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", len(resp_data))
        self.end_headers()
        self.wfile.write(resp_data)


def main():
    addr = ('', 8080)
    server = HTTPServer(addr, RequestHandler)
    server.serve_forever()


if __name__ == '__main__':
    main()
