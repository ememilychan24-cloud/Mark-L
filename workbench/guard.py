#!/usr/bin/env python3
"""
機械式紅線檢查。**唔靠模型自覺。**

點解要有呢層：QA agent 都係一個模型。叫模型檢查自己有冇違反紅線，
係一種自我審查，而自我審查唔滿足合規要求 —— 呢個係成個工作台由頭到尾嘅原則
（所以 QA 崗位永遠唔合併）。

呢度做嘅係最笨但最可靠嗰種：**由紅線抽出禁用詞，逐個字串搵。**
搵到就係搵到，冇得拗。模型嗰層 QA 係補呢層搵唔到嘅嘢（語氣、暗示、
無出處嘅暗示性宣稱），兩層一齊做先算數。

抽詞方法：紅線寫成「唔用『治療／根治／醫學證實／療效』呢類字眼」，
就抽出引號入面、用／分開嘅詞。抽唔到詞嘅紅線（例如「個案分享要有書面同意」）
呢層檢查唔到 —— 呢啲會明明白白列出嚟話你知「呢條要人睇」，
唔會扮已經檢查過。
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# 「…」『…』"…" 入面嘅內容
QUOTED = re.compile(r"[「『\"]([^」』\"]{1,60})[」』\"]")

# 抽詞用嘅分隔符
SPLIT = re.compile(r"[／/、,，]")

# 紅線寫成「唔用 X」「唔講 X」「唔可以用 X」先算禁用詞規則。
# 「要有書面同意」呢類唔係禁用詞，機械檢查唔到。
BAN_HINT = re.compile(r"唔(用|好用|講|可以用|可以講|會用)")

# 數字宣稱：證據庫為空嗰陣要攔嘅嘢
NUMERIC = re.compile(
    r"\d+\s*(%|％|成|倍|位|個案|人|次|日|週|星期|個月|年)"
    r"|超過\s*\d+|逾\s*\d+|第\s*\d+\s*名"
)


# 禁用詞前面如果有否定詞，好可能係「我哋唔會保證任何嘢」呢類合法文案。
# 唔可以直接放行（「唔係保證，但實際上一定得」都會過關），但要標示出嚟 ——
# 一個成日誤報嘅檢查，兩個星期之後就會被人當透明，等於冇做過。
# 允許中間隔一兩個字（「唔可以**講**必瘦」），但唔可以跨標點 ——
# 跨咗標點就已經係第二個子句，同前面嗰個否定冇關係。
# 呢張表故意保守：漏咗一個否定詞 = 多一個誤報（人望一望就算），
# 加錯一個 = 真違規變成軟警告。寧願誤報。
NEGATED = re.compile(r"(唔會|唔可以|唔好|唔係|唔用|唔講|唔提|不會|不可|沒有|冇)[^，。；、]{0,3}$")


@dataclass
class Hit:
    kind: str        # banned-word | numeric-claim
    term: str
    rule: str
    where: str       # 出現喺邊句
    negated: bool = False   # 前面有否定詞，可能係合法用法


@dataclass
class Report:
    hits: list[Hit]
    unchecked: list[str]        # 機械檢查唔到嘅紅線，要人／模型睇
    checked_terms: list[str]

    @property
    def hard(self) -> list[Hit]:
        """真違規 —— 唔係否定用法嗰啲。"""
        return [h for h in self.hits if not h.negated]

    @property
    def soft(self) -> list[Hit]:
        """前面有否定詞，可能合法，但要人望一眼。"""
        return [h for h in self.hits if h.negated]

    @property
    def clean(self) -> bool:
        """冇硬違規先算過。軟嘅唔擋，但會列出嚟。"""
        return not self.hard

    def summary(self) -> str:
        if not self.hits:
            return f"機械檢查通過（檢查咗 {len(self.checked_terms)} 個禁用詞）"
        bits = []
        if self.hard:
            bits.append(f"{len(self.hard)} 處違規")
        if self.soft:
            bits.append(f"{len(self.soft)} 處疑似否定用法（要人望）")
        return "機械檢查：" + "、".join(bits)


def banned_terms(redlines: list[str]) -> tuple[list[str], list[str]]:
    """由紅線抽出可以機械檢查嘅禁用詞。回 (詞, 檢查唔到嘅紅線)。"""
    terms: list[str] = []
    unchecked: list[str] = []
    for r in redlines:
        if not BAN_HINT.search(r):
            unchecked.append(r)
            continue
        found = QUOTED.findall(r)
        if not found:
            unchecked.append(r)
            continue
        for group in found:
            for t in SPLIT.split(group):
                t = t.strip()
                if t and t not in terms:
                    terms.append(t)
    return terms, unchecked


def check(text: str, redlines: list[str], allow_numbers: bool) -> Report:
    """掃一篇稿。

    allow_numbers=False 代表 04-approved-claims.md 係空 ——
    咁任何數字宣稱都係無出處嘅，一律攔。
    """
    terms, unchecked = banned_terms(redlines)
    hits: list[Hit] = []

    # 逐句掃，方便指返出邊句出事
    sentences = [s.strip() for s in re.split(r"[。！？\n]+", text) if s.strip()]

    for t in terms:
        for s in sentences:
            i = s.find(t)
            if i < 0:
                continue
            rule = next((r for r in redlines if t in r), t)
            hits.append(Hit("banned-word", t, rule, s[:60],
                            negated=bool(NEGATED.search(s[:i]))))
            break   # 同一個詞報一次就夠

    if not allow_numbers:
        for s in sentences:
            m = NUMERIC.search(s)
            if m:
                hits.append(Hit(
                    "numeric-claim", m.group(0),
                    "04-approved-claims.md 為空 —— 唔可以出任何數字宣稱",
                    s[:60],
                ))
    return Report(hits=hits, unchecked=unchecked, checked_terms=terms)


def render(r: Report) -> str:
    """寫成人睇得明嘅一段，會入 review 記錄。"""
    L = [f"## 機械式檢查\n\n{r.summary()}\n"]
    if r.hard:
        L.append("**違規（要改）**\n")
        L.append("| 類型 | 命中 | 違反 | 出現喺 |")
        L.append("|---|---|---|---|")
        for h in r.hard:
            L.append(f"| {h.kind} | `{h.term}` | {h.rule} | …{h.where}… |")
        L.append("")
    if r.soft:
        L.append("**疑似否定用法（例如「我哋唔會保證」）—— 唔擋，但人要望一眼**\n")
        for h in r.soft:
            L.append(f"- `{h.term}` ：…{h.where}…")
        L.append("")
    if r.unchecked:
        L.append("**呢幾條機械檢查唔到，要人睇：**")
        L += [f"- {u}" for u in r.unchecked]
        L.append("")
        L.append("> 列出嚟係故意嘅。唔列就會變成「檢查過」嘅假象。")
    return "\n".join(L)
