import http.server
import socketserver
import threading
import os
import mimetypes

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')  # 允许跨域访问
        super().end_headers()

class FontServer:
    def __init__(self, directory: str, port: int = 2288):
        self.directory = directory
        self.port = port
        self.httpd = None
        self.thread = None

        # 注册字体 MIME 类型
        mimetypes.add_type("font/ttf", ".ttf")
        mimetypes.add_type("font/otf", ".otf")
        mimetypes.add_type("font/woff", ".woff")
        mimetypes.add_type("font/woff2", ".woff2")

    def start(self):
        def run():
            os.chdir(self.directory)
            with socketserver.ThreadingTCPServer(("", self.port), CORSRequestHandler) as httpd:
                self.httpd = httpd
                print(f"🟢 Font server running at http://localhost:{self.port}/ (from: {self.directory})")
                httpd.serve_forever()

        self.thread = threading.Thread(target=run, daemon=True)
        self.thread.start()

    def stop(self):
        if self.httpd:
            print("🛑 Shutting down font server...")
            self.httpd.shutdown()
            self.httpd.server_close()
            self.thread.join()
