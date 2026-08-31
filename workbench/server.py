#!/usr/bin/env python3
"""
Dashboard server。用 stdlib，冇依賴 —— 客戶部電腦淨係要有 Python 就行得到。

每次 request 都重新讀檔案系統。慢少少，但保證畫面同硬碟一致 ——
一個 dashboard 最壞嘅情況唔係慢，係顯示緊一個已經唔存在嘅狀態。
"""

from __future__ import annotations

import json
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .state import read_agency

STATIC = Path(__file__).resolve().parent / "static"


class Handler(BaseHTTPRequestHandler):
    def __init__(self, *args, root: Path, **kw):
        self.root = root
        super().__init__(*args, **kw)

    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = self.path.split("?")[0]
        if path == "/api/state":
            try:
                data = read_agency(self.root).to_dict()
            except Exception as e:  # dashboard 唔可以因為一個壞檔案就白畫面
                data = {"error": str(e), "clients": [], "totals": {}}
            self._send(200, json.dumps(data, ensure_ascii=False).encode(), "application/json; charset=utf-8")
            return
        if path in ("/", "/index.html"):
            f = STATIC / "dashboard.html"
            if not f.is_file():
                self._send(500, b"dashboard.html missing", "text/plain; charset=utf-8")
                return
            self._send(200, f.read_bytes(), "text/html; charset=utf-8")
            return
        self._send(404, b"not found", "text/plain; charset=utf-8")

    def log_message(self, fmt, *args):  # 唔好污染 terminal
        pass


def serve(root: Path, port: int = 8787, host: str = "127.0.0.1") -> int:
    root = Path(root).expanduser().resolve()
    if not root.is_dir():
        print(f"✗ 搵唔到 {root}。先跑 `python -m workbench demo`。")
        return 2
    srv = ThreadingHTTPServer((host, port), partial(Handler, root=root))
    print(f"Dashboard: http://{host}:{port}   （讀緊 {root}）")
    print("Ctrl-C 停止。")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n停咗。")
    finally:
        srv.server_close()
    return 0
