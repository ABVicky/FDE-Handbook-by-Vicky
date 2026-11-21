"""AdmitFlow status server (Module 02 break & fix).

A tiny web server that reports how many leads are in the sample file.
Uses only the Python standard library.
"""
import csv
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

PORT = int(os.environ.get("APP_PORT", "8000"))
DATA_DIR = Path(os.environ["ADMITFLOW_DATA_DIR"])
LEADS_FILE = DATA_DIR / "leads_sample.csv"


def count_leads():
    with open(LEADS_FILE, newline="") as fh:
        return sum(1 for row in csv.DictReader(fh) if row.get("enquiry_id"))


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            body = {"status": "ok"}
        elif self.path == "/leads/count":
            body = {"leads": count_leads()}
        else:
            self.send_response(404)
            self.end_headers()
            return
        data = json.dumps(body).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == "__main__":
    print(f"AdmitFlow status server listening on http://localhost:{PORT}")
    HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
