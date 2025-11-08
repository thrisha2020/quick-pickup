from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser
import os

PORT = 8000

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler):
    server_address = ('', PORT)
    httpd = server_class(server_address, handler_class)
    print(f"Server running at http://localhost:{PORT}")
    webbrowser.open(f'http://localhost:{PORT}/index.html')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
