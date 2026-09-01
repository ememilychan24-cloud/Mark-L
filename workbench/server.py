#!/usr/bin/env python3
"""
Dashboard ＋ 設定精靈 server。用 stdlib，冇依賴 ——
客戶部電腦淨係要有 Python 就行得到。

兩個設計決定：

**每次 request 都重新讀檔案系統。** 慢少少，但保證畫面同硬碟一致 ——
一個 dashboard 最壞嘅情況唔係慢，係顯示緊一個已經唔存在嘅狀態。

**精靈係無狀態嘅。** 瀏覽器每次帶住成份 draft 過嚟，server 唔記住任何嘢。
咁樣 refresh、開多個 tab、返上一步全部唔會出事，亦都唔使處理 session 過期。
"""

from __future__ import annotations

import json
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .pipeline import onboard_brief
from .state import read_agency
from .taxonomy import ARCHETYPE_BY_KEY, MODIFIER_BY_KEY, slugify
from .visual import write as write_visual
from .wizard import (
    PLATFORM_LABELS, SKILL_LABELS, Draft, apply_archetype_defaults,
    brief_from_draft, options, seed_from_sentence,
)

STATIC = Path(__file__).resolve().parent / "static"
MAX_BODY = 4 * 1024 * 1024   # 4MB —— 精靈只會 POST 分析結果，唔會 POST 原圖


def _draft(data: dict) -> Draft:
    """由 JSON 砌返 Draft。

    **未知嘅 id 一律丟走，唔係報錯，係當佢冇揀過。**
    唔淨係為咗安全：一個未知嘅 archetype 之前會令 apply_archetype_defaults
    喺 try 之外掟 KeyError，個 request handler 直接死，瀏覽器收到一個空回應 ——
    畫面就會靜靜雞卡死，冇任何訊息。喺入口洗乾淨，後面就唔使逐個位防。
    """
    known_a = set(ARCHETYPE_BY_KEY)
    known_m = set(MODIFIER_BY_KEY)
    known_p = set(PLATFORM_LABELS)
    known_s = set(SKILL_LABELS)

    a = data.get("archetype")
    d = Draft(
        archetype=a if a in known_a else None,
        modifiers=[str(x) for x in data.get("modifiers") or [] if x in known_m],
        platforms=[str(x) for x in data.get("platforms") or [] if x in known_p],
        skills=[str(x) for x in data.get("skills") or [] if x in known_s],
        brand_name=str(data.get("brand_name") or "")[:80],
        handles=[str(x)[:40] for x in data.get("handles") or []][:10],
        sites=[str(x)[:120] for x in data.get("sites") or []][:10],
        visual=data.get("visual") if isinstance(data.get("visual"), dict) else {},
        sentence=str(data.get("sentence") or "")[:600],
    )
    return d


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

    def _json(self, data: dict, code: int = 200) -> None:
        self._send(code, json.dumps(data, ensure_ascii=False).encode(),
                   "application/json; charset=utf-8")

    def _page(self, name: str) -> None:
        f = STATIC / name
        if not f.is_file():
            self._send(500, f"{name} missing".encode(), "text/plain; charset=utf-8")
            return
        self._send(200, f.read_bytes(), "text/html; charset=utf-8")

    def _body(self) -> dict:
        n = int(self.headers.get("Content-Length") or 0)
        if n <= 0 or n > MAX_BODY:
            return {}
        try:
            return json.loads(self.rfile.read(n).decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}

    # ── GET ────────────────────────────────────────────────────────────
    def do_GET(self) -> None:
        path = self.path.split("?")[0]
        if path == "/api/state":
            try:
                data = read_agency(self.root).to_dict()
            except Exception as e:   # dashboard 唔可以因為一個壞檔案就白畫面
                data = {"error": str(e), "clients": [], "totals": {}}
            self._json(data)
            return
        if path in ("/", "/index.html"):
            self._page("dashboard.html")
            return
        if path in ("/setup", "/setup.html"):
            self._page("setup.html")
            return
        self._send(404, b"not found", "text/plain; charset=utf-8")

    # ── POST ───────────────────────────────────────────────────────────
    def do_POST(self) -> None:
        path = self.path.split("?")[0]
        body = self._body()

        if path == "/api/wizard/start":
            # 有句子就用分類器起個頭；冇就交白卷，一樣行得
            d = seed_from_sentence(str(body.get("sentence") or ""))
            d = apply_archetype_defaults(d)
            self._json({"draft": d.to_dict()})
            return

        if path == "/api/wizard/options":
            step = str(body.get("step") or "industry")
            d = apply_archetype_defaults(_draft(body.get("draft") or {}))
            try:
                self._json({"options": options(step, d), "draft": d.to_dict()})
            except ValueError:
                self._json({"error": f"未知步驟：{step}"}, 400)
            return

        if path == "/api/wizard/create":
            d = apply_archetype_defaults(_draft(body.get("draft") or {}))
            if not d.archetype:
                self._json({"error": "未揀行業"}, 400)
                return
            if not d.platforms:
                self._json({"error": "未揀平台"}, 400)
                return
            try:
                b = brief_from_draft(d)
                # 帳號優先做 slug：佢本身已經係乾淨嘅識別碼。品牌名係俾人睇嘅，
                # 入面通常有空格同標點（「Mami's Sunshine」→「mami-s-sunshine」，好核突）。
                slug = slugify(d.handles[0] if d.handles else (d.brand_name or d.archetype))

                # 撞名就停手，唔好靜靜雞寫入去。onboard 本身係「已存在就跳過」，
                # 呢個對重跑同一個客係啱嘅，但對「兩個唔同嘅客撞咗同一個 slug」
                # 就係災難：兩個品牌嘅紅線同證據會撈埋一齊，而且冇任何錯誤訊息。
                if (self.root / "clients" / slug).exists():
                    self._json({"error": f"已經有一個客叫「{slug}」。"
                                         "改個唔同嘅品牌名或者帳號再試 —— "
                                         "兩個客用同一個資料夾，紅線同證據會撈埋一齊。"}, 409)
                    return

                cdir, b = onboard_brief(self.root, b, slug=slug)
                wrote_visual = write_visual(cdir, {**d.visual, "handles": d.handles})
            except Exception as e:
                self._json({"error": f"建立失敗：{e}"}, 500)
                return
            self._json({
                "slug": cdir.name,
                "path": str(cdir),
                "visual": wrote_visual,
                "agents": len(b.agents),
                "redlines": len(b.redlines),
                # 呢兩樣機器補唔到，一定要人交料。唔講就變成一個「睇落完成」嘅假工作台。
                "still_needed": [
                    "已批准證據（證書、個案、數據）—— 冇呢個，所有稿都唔可以落數字",
                    "真實客戶查詢紀錄 —— 冇呢個，內容會用你嘅講法而唔係客人嘅講法",
                ],
            })
            return

        self._send(404, b"not found", "text/plain; charset=utf-8")

    def log_message(self, fmt, *args):   # 唔好污染 terminal
        pass


def serve(root: Path, port: int = 8787, host: str = "127.0.0.1",
          open_browser: bool = False) -> int:
    root = Path(root).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)   # 第一次用嘅人，個資料夾仲未存在
    srv = ThreadingHTTPServer((host, port), partial(Handler, root=root))
    url = f"http://{host}:{port}"
    print(f"\n  工作台開咗喺：{url}")
    print(f"  開新客：      {url}/setup")
    print(f"  （讀緊 {root}）\n  Ctrl-C 停止。\n")
    if open_browser:
        import threading
        import webbrowser
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n停咗。")
    finally:
        srv.server_close()
    return 0
