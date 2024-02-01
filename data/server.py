from http.server import HTTPServer, SimpleHTTPRequestHandler, test as test_orig
import sys


def test(*args):
    test_orig(*args, port=int(sys.argv[1]) if len(sys.argv) > 1 else 3333)


class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Origin, Content-Type, Accept')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Origin, Content-Type, Accept')
        self.end_headers()


if __name__ == '__main__':
    test(CORSRequestHandler, HTTPServer)
