from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote
import json
import mimetypes
import re
import shutil
import time


ROOT_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = ROOT_DIR / "uploads"
HOST = "127.0.0.1"
PORT = 8000


class LocalFileHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        if self.path == "/":
            self.write_json({
                "code": 200,
                "message": "local file server is running",
                "uploadUrl": "http://%s:%s/upload" % (HOST, PORT),
                "filesUrl": "http://%s:%s/files/" % (HOST, PORT)
            })
            return

        if self.path.startswith("/files/"):
            filename = unquote(self.path[len("/files/"):]).split("?")[0]
            target = (UPLOAD_DIR / filename).resolve()
            if not str(target).startswith(str(UPLOAD_DIR.resolve())) or not target.exists():
                self.send_error(404, "file not found")
                return

            content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(target.stat().st_size))
            self.end_headers()
            with target.open("rb") as source:
                shutil.copyfileobj(source, self.wfile)
            return

        self.send_error(404, "not found")

    def do_POST(self):
        if self.path != "/upload":
            self.send_error(404, "not found")
            return

        content_type = self.headers.get("Content-Type", "")
        boundary = self.get_boundary(content_type)
        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length)
        upload = self.parse_upload(body, boundary)

        if upload is None:
            self.write_json({"code": 400, "message": "missing file"}, status=400)
            return

        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        original_name = Path(upload["filename"]).name
        saved_name = "%s_%s" % (int(time.time() * 1000), original_name)
        saved_path = UPLOAD_DIR / saved_name

        with saved_path.open("wb") as output:
            output.write(upload["content"])

        self.write_json({
            "code": 200,
            "message": "upload success",
            "data": {
                "name": original_name,
                "savedName": saved_name,
                "url": "http://%s:%s/files/%s" % (HOST, PORT, saved_name),
                "size": saved_path.stat().st_size
            }
        })

    def get_boundary(self, content_type):
        for part in content_type.split(";"):
            part = part.strip()
            if part.startswith("boundary="):
                return part.split("=", 1)[1].strip('"').encode("utf-8")
        return None

    def parse_upload(self, body, boundary):
        if not body or not boundary:
            return None

        marker = b"--" + boundary
        for part in body.split(marker):
            if b"Content-Disposition" not in part or b"filename=" not in part:
                continue

            header_end = part.find(b"\r\n\r\n")
            if header_end < 0:
                continue

            headers = part[:header_end].decode("utf-8", errors="ignore")
            content = part[header_end + 4:]
            if content.endswith(b"\r\n"):
                content = content[:-2]
            if content.endswith(b"--"):
                content = content[:-2]

            match = re.search(r'filename="([^"]+)"', headers)
            filename = match.group(1) if match else ""
            if filename:
                return {"filename": filename, "content": content}
        return None

    def write_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((HOST, PORT), LocalFileHandler)
    print("Local file server started: http://%s:%s" % (HOST, PORT))
    print("Upload endpoint: http://%s:%s/upload" % (HOST, PORT))
    print("Files directory: %s" % UPLOAD_DIR)
    server.serve_forever()
