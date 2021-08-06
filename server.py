"""

DFR API Server.


"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import argparse
from io import BytesIO
import logging


class SERVER_Cli:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="DFR Api Server")
        self.parser.add_argument('-p', '--port', type=int,
                                 help='Port to bind to')
        self.parser.add_argument('-h', '--host', type=str,
                                 help='Host to bind to')

    def parse_args(self, args):
        args = self.parser.parse_args(args)
        if args.port:
            self.set_server_port(args.port)
        if args.host:
            self.set_host(args.host)


class web_server(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.path = "/index.html"
            try:
                # Read the file
                file_to_open = open(self.path[1:]).read()
                self.send_response(200)
            except:
                file_to_open = "File Not Found"
                self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes(file_to_open, 'utf-8'))
        else:

            self.log_error("REQUEST NOT ROOT")

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        response = BytesIO()
        response.write(b'This is a POST request. ')
        response.write(b'Received: ')
        response.write(body)
        self.wfile.write(response.getvalue())


httpd = HTTPServer(('0.0.0.0', 8800), web_server)
logging.info("Hello World!")
httpd.serve_forever()
