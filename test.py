import http.server
import socketserver

PORT = 7000
MESSAGE = "21"
global i

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        i = 1
        if self.path == "/data":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            while(i<5):
                i = i+i
                MESSAGE = str(i)
                print(MESSAGE)
                if(i==5):
                    i=1
                self.wfile.write(MESSAGE.encode())
     
            
            self.wfile.write(MESSAGE.encode())
        elif self.path == "/":  # Serve the webpage
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
