#!/usr/bin/env python3
"""
每個崗位用邊個模型、幾多 effort、洗唔洗快。

點解要有呢張表，而唔係全部用同一個模型：
呢個工作台入面，唔同崗位嘅工作性質差好遠。QA 係「對住清單逐條檢查」，
研究係「由零諗角度」。用同一個模型做兩樣，唔係貴咗就係差咗。

同樣重要：**唔好為咗慳錢而降級判斷型嘅工作**。QA 判斷錯 → 錯嘢出街 →
品牌信任冇得回頭。呢度慳嘅錢，一次出事就蝕返晒。所以下面標咗 `never_downgrade`
嘅崗位，唔准為咗成本而降。

價格：Anthropic 第一方 API，每 1M token（2026-06 快照，會變，用前核返）。
  claude-opus-5    $5 / $25
  claude-sonnet-5  $2 / $10
  claude-haiku-4-5 $1 / $5
"""

from __future__ import annotations

import os as _os
from dataclasses import dataclass


@dataclass(frozen=True)
class Route:
    job: str
    model: str                  # standard 檔次用嘅（預設）
    effort: str                 # low | medium | high | xhigh | max
    why: str
    batch: bool = False         # 交 Batch API：慢啲，平一半
    cache: bool = True          # 品牌知識庫做 cached prefix
    never_downgrade: bool = False
    economy: str = ""           # economy 檔次用邊個（空 = 唔降）
    economy_effort: str = ""


# 兩個檔次：
#   standard（預設）—— 全部 claude-opus-5。降級係你嘅決定，唔係工具幫你做。
#   economy         —— 按工作性質分層，見下面每個 Route 嘅 economy 欄。
#
# 開 economy：export WORKBENCH_TIER=economy
#
# 分層唔係「平就好」。判斷型嘅工作（研究、文案、QA）留喺 opus-5；
# 受約束嘅工作（抽取、改寫、分類）先落。QA 無論邊個檔次都唔降 ——
# 佢係最後一道攔截，攔唔到就出街，而出街咗嘅嘢收唔返。
TIER = "economy" if _os.environ.get("WORKBENCH_TIER") == "economy" else "standard"


# 順序＝一條內容由頭到尾行過嘅次序
ROUTES: tuple[Route, ...] = (
    Route(
        job="爬取／抽取",
        model="claude-opus-5", effort="low",
        economy="claude-haiku-4-5", economy_effort="low",
        why="由 HTML 抽正文係機械工，唔需要判斷。呢步 token 量最大（成個頁面），"
            "所以係最值得用平模型嘅一步。",
        batch=True, cache=False,
    ),
    Route(
        job="語氣蒸餾",
        model="—（唔用模型）", effort="—",
        why="句長、標點、開場分佈係**數**出嚟嘅，唔係估出嚟嘅。"
            "scripts/distill.py 直接算。呢步用模型唔止貴，仲會出唔可驗證嘅描述"
            "（「語氣親切專業」）—— 呢類描述兩個寫手睇完會寫出兩種嘢。",
        cache=False,
    ),
    Route(
        job="研究／選題",
        model="claude-opus-5", effort="high",
        why="由市場訊號提煉角度係開放性判斷，冇標準答案。呢度出錯，"
            "下游成條線做嘅都係錯題目 —— 慳唔起。",
        batch=True,
    ),
    Route(
        job="文案（Master）",
        model="claude-opus-5", effort="high",
        why="要同時滿足語氣數字、紅線、證據限制。呢個係客戶真正買嘅嘢。",
        batch=True,
    ),
    Route(
        job="平台改寫",
        model="claude-opus-5", effort="medium",
        economy="claude-sonnet-5", economy_effort="medium",
        why="Master 已經定咗觀點同證據，改寫係**受約束**嘅工作，唔使再判斷。"
            "四個平台 ×  每週 ×  N 個客，呢步係量最大嘅重複工作，"
            "所以係第二值得降級嘅位。",
        batch=True,
    ),
    Route(
        job="QA／紅線檢查",
        model="claude-opus-5", effort="high",
        why="睇落似「對清單」，實際係判斷「呢句算唔算功效宣稱」。"
            "呢個係最後一道攔截，錯咗就出街。",
        never_downgrade=True,
    ),
    Route(
        job="留言／私訊分流",
        model="claude-opus-5", effort="low",
        economy="claude-haiku-4-5", economy_effort="low",
        why="分成 FAQ／反對理由／內容缺口／潛在查詢四類，係分類工作。"
            "量大、重複、有明確類別 —— Haiku 嘅正路用途。",
        batch=False,  # 要即時
    ),
    Route(
        job="回覆草稿",
        model="claude-opus-5", effort="medium",
        economy="claude-sonnet-5", economy_effort="medium",
        why="有已批准講法做底，唔係由零寫。但要照顧語氣，所以唔用 Haiku。",
    ),
    Route(
        job="週報／覆盤",
        model="claude-opus-5", effort="high",
        why="要由數字睇出「邊層掉失」同埋建議下一輪改咩。呢個係策略判斷。"
            "一週一次，量細，慳呢度冇意義。",
        batch=True,
    ),
    Route(
        job="生圖",
        model="（圖像模型，見 docs/API-MODULES.md）", effort="—",
        why="唔用 code 砌版 —— 用 code 排出嚟每個元素數學上啱位，但一睇就知係機器砌。"
            "有免責聲明嘅圖行 image-plus-text-layer：底圖生成，文字用圖層疊，"
            "因為圖像模型出唔到準確文字。",
        cache=False,
    ),
)

ROUTE_BY_JOB = {r.job: r for r in ROUTES}


def summary() -> str:
    lines = ["| 崗位 | 模型 | Effort | Batch | 快取 |", "|---|---|---|---|---|"]
    for r in ROUTES:
        lines.append(
            f"| {r.job} | `{r.model}` | {r.effort} | "
            f"{'✓' if r.batch else '—'} | {'✓' if r.cache else '—'} |"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    print(summary())
    print("\n唔准為成本降級：",
          "、".join(r.job for r in ROUTES if r.never_downgrade))


ECONOMY_NOTE = (
    "而家行緊 standard（全部 claude-opus-5）。"
    "想試分層慳錢：export WORKBENCH_TIER=economy —— "
    "抽取同分流落 Haiku，平台改寫落 Sonnet，研究／文案／QA 唔郁。"
)


def route_for(job: str) -> Route:
    """攞一個崗位嘅路由。跟 TIER 決定用邊個模型。

    搵唔到就用 standard 嘅文案設定 —— 寧願貴少少，唔好靜靜雞用咗個平模型
    去做一件我哋冇考慮過嘅工作。
    """
    r = ROUTE_BY_JOB.get(job)
    if r is None:
        return Route(job=job, model="claude-opus-5", effort="high",
                     why="未分類嘅工作，用返最穩陣嗰個。")
    if TIER == "economy" and r.economy and not r.never_downgrade:
        return Route(**{**r.__dict__, "model": r.economy,
                        "effort": r.economy_effort or r.effort})
    return r
