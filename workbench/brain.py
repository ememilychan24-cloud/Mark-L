#!/usr/bin/env python3
"""
把一個客嘅品牌知識庫，砌成一段**逐個 byte 都穩定**嘅前綴。

點解要逐個 byte 穩定：呢段嘢係 prompt cache 嘅前綴。快取係前綴比對 ——
前面改一個字元，後面全部作廢。一個客一星期出十幾篇，每篇經研究、文案、
QA 三步，即係一星期要讀呢堆嘢幾十次。快取命中同唔命中，帳單爭好遠。

所以呢度**唔准**出現：時間戳、隨機 id、未排序嘅 dict、路徑（會因機器而異）。
只有檔案內容，固定次序。

檔案次序寫死喺 ORDER 度。唔好改成 glob 排序 —— glob 喺唔同檔案系統次序可以唔同，
而次序一變，快取就成個失效而冇人會發現（因為輸出照樣啱，只係貴咗）。
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

# 固定次序。加新檔案就加喺尾 —— 插入中間會令所有現存快取失效一次。
ORDER = [
    ("brand/BIBLE.md", "品牌憲法（紅線喺呢度，違反即退回）"),
    ("brand/brain/01-positioning.md", "定位"),
    ("brand/brain/02-voice-profile.md", "語氣（呢啲數字係觀察到嘅現況，唔係目標）"),
    ("brand/brain/03-audience-language.md", "受眾原話"),
    ("brand/brain/04-approved-claims.md", "已批准主張／證據"),
    ("brand/brain/05-hook-library.md", "有效開場"),
    ("brand/brain/06-platform-rules.md", "平台規格"),
    ("style/brand-visual.md", "品牌視覺"),
    ("CHECKLIST.md", "交付前驗收"),
]

EMPTY_MARK = "（空）"


@dataclass
class Brain:
    slug: str
    brand: str
    platforms: list[str]
    redlines: list[str]
    prefix: str                  # 要快取嗰段
    empty_buckets: list[str]     # 邊幾格係空 —— 決定咗唔可以寫咩
    chars: int

    @property
    def has_claims(self) -> bool:
        """有冇已批准證據。冇 = 全篇唔可以出任何數字、個案、資格。"""
        return "04-approved-claims.md" not in self.empty_buckets

    @property
    def has_audience(self) -> bool:
        return "03-audience-language.md" not in self.empty_buckets


def load(cdir: Path) -> Brain:
    cdir = Path(cdir)
    meta = json.loads((cdir / "workspace.json").read_text(encoding="utf-8"))

    parts: list[str] = []
    empty: list[str] = []

    for rel, label in ORDER:
        p = cdir / rel
        if not p.is_file():
            continue
        body = p.read_text(encoding="utf-8").strip()
        if EMPTY_MARK in body[:400]:
            empty.append(Path(rel).name)
        parts.append(f"<<<{rel} — {label}>>>\n{body}\n<<<end {rel}>>>")

    prefix = "\n\n".join(parts)
    return Brain(
        slug=cdir.name,
        brand=meta.get("brand", cdir.name),
        platforms=meta.get("platforms", []),
        redlines=meta.get("redlines", []),
        prefix=prefix,
        empty_buckets=empty,
        chars=len(prefix),
    )


# 呢段係 system prompt 嘅頭。同樣要 byte 穩定 —— 唔好塞日期入去。
ROLE_HEADER = """你係一個品牌內容生產線入面嘅 AI 崗位。下面係呢個品牌嘅完整知識庫。

三條規矩，任何情況都適用：

1. **空係一個明確狀態。** 有啲櫃桶會寫住「（空）」。嗰啲代表**未有資料**，
   唔係代表你可以自己補。空嘅櫃桶入面嘅嘢，你一律唔可以引用、推斷、或者
   「合理估計」。

2. **04-approved-claims.md 為空時，你唔可以寫任何數字、個案、資格認證、
   成效宣稱。** 一句都唔可以。寧願交一篇冇數字嘅稿。
   一句冇出處嘅宣稱出咗街係收唔返嘅。

3. **BIBLE.md 入面每一條紅線都係硬規矩。** 違反即退回，唔需要討論。

語氣要跟 02-voice-profile.md 嘅**數字**（句長、開場類型分佈、標點頻率、
稱呼），唔係跟感覺。嗰啲數字係由品牌自己出過嘅帖算返出嚟嘅現況。

---

"""


def system_blocks(b: Brain) -> list[dict]:
    """砌 system 參數。**快取斷點放喺最尾一格。**

    前面兩格（角色 ＋ 知識庫）對同一個客嘅每一次呼叫都完全一樣，所以整段
    都食得到快取。每次唔同嘅嘢（今次做咩、邊個平台）要放去 messages，
    唔可以放喺呢度 —— 放咗就等於每次都 cache miss。
    """
    return [
        {"type": "text", "text": ROLE_HEADER},
        {
            "type": "text",
            "text": b.prefix,
            # 1 小時 TTL：一個 campaign 通常喺一兩個鐘內跑晒研究→文案→QA，
            # 5 分鐘預設會喺中間過期。
            "cache_control": {"type": "ephemeral", "ttl": "1h"},
        },
    ]


def constraints_note(b: Brain) -> str:
    """今次呢個客實際上受咩限制。放喺 user message，唔放 system ——
    因為佢會隨住客戶補料而變，變咗就唔應該連累個快取。"""
    lines = []
    if not b.has_claims:
        lines.append(
            "⚠️ 已批准證據係**空**。所以呢篇稿：唔可以出任何數字、百分比、"
            "年期、服務人數、個案、證書、資格。如果你覺得冇數字就寫唔到，"
            "咁就講清楚「呢個角度需要證據，而家未有」，唔好自己作一個。"
        )
    if not b.has_audience:
        lines.append(
            "⚠️ 受眾原話係空。所以你只可以用品牌自己嘅講法，"
            "唔好扮引用客人講過嘅嘢。"
        )
    return "\n".join(lines)
