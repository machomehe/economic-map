#!/usr/bin/env python3
"""gzip 압축 + 멀티스레드 HTTP 서버"""
import gzip
import io
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn

os.chdir(os.path.dirname(os.path.abspath(__file__)))

class GzipHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'public, max-age=3600')
        super().end_headers()

    def do_GET(self):
        # Accept-Encoding 확인
        ae = self.headers.get('Accept-Encoding', '')
        if 'gzip' not in ae:
            return super().do_GET()

        # 파일 경로 결정
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            path = os.path.join(path, 'index.html')

        if not os.path.isfile(path):
            return super().do_GET()

        # Content-Type 결정
        ext = os.path.splitext(path)[1].lower()
        ct_map = {
            '.html': 'text/html; charset=utf-8',
            '.js': 'application/javascript; charset=utf-8',
            '.json': 'application/json; charset=utf-8',
            '.css': 'text/css; charset=utf-8',
            '.svg': 'image/svg+xml',
            '.png': 'image/png',
        }
        ct = ct_map.get(ext)
        if not ct:
            return super().do_GET()

        # 바이너리(이미지 등)는 gzip 안 함
        if not ct.startswith('text/') and 'javascript' not in ct and 'json' not in ct:
            return super().do_GET()

        try:
            with open(path, 'rb') as f:
                content = f.read()
        except OSError:
            return super().do_GET()

        # gzip 압축
        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode='wb', compresslevel=6) as gz:
            gz.write(content)
        compressed = buf.getvalue()

        self.send_response(200)
        self.send_header('Content-Type', ct)
        self.send_header('Content-Encoding', 'gzip')
        self.send_header('Content-Length', str(len(compressed)))
        self.end_headers()
        self.wfile.write(compressed)

    def log_message(self, *args):
        pass  # 로그 끄기

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

if __name__ == '__main__':
    server = ThreadedHTTPServer(('0.0.0.0', 8080), GzipHandler)
    print('Server running on :8080 (gzip + threaded)')
    server.serve_forever()
