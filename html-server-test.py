import http.server
import socketserver

PORT = 7000
MESSAGE = "Hello, ESP8266 and Webpage!"

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/data":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(MESSAGE.encode())
        elif self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("index.html", "rb") as file:
                self.wfile.write(file.read())
        else:
            self.send_error(404, "Not Found")

with socketserver.TCPServer(("0.0.0.0", PORT), CustomHandler) as httpd:
    print(f"Serving on port {PORT}")
    httpd.serve_forever()
