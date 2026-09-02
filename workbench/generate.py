#!/usr/bin/env python3
"""
真正叫 Claude 寫嘢嗰層。

三步，每步一個 API call：
  1. 研究  → 3–6 個候選角度（人揀一個）
  2. 文案  → Master ＋ 每個平台版本
  3. QA    → 判定收唔收，退回要指明違反邊條

三步都共用同一段快取前綴（品牌知識庫）。呢個係整個成本設計嘅核心：
一個客一星期幾十次呼叫，讀嘅係同一堆嘢，唔快取就係喺度重複燒錢。

**QA 有兩層，唔係一層。**
  guard.py  機械式搵禁用詞同無出處數字 —— 唔靠模型自覺
  呢度      模型判斷語氣、暗示、有冇扮引用
兩層都要過。淨係得模型嗰層，等於叫模型審自己。

**冇嘢會自動出街。** 產出寫入 queue/，等人審。呢個唔係未做完，係設計。
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from . import brain as brain_mod
from . import guard
from .models import route_for

MAX_TOKENS = 16000


class NoCredentials(RuntimeError):
    pass


def client():
    """建 client。冇 SDK 或者冇憑證就講清楚點解，唔好掟一堆 traceback。"""
    try:
        import anthropic
    except ImportError as e:
        raise NoCredentials(
            "未裝 SDK。跑：pip install anthropic"
        ) from e
    if not (os.environ.get("ANTHROPIC_API_KEY")
            or os.environ.get("ANTHROPIC_AUTH_TOKEN")
            or Path.home().joinpath(".config/anthropic").exists()):
        raise NoCredentials(
            "搵唔到 API 憑證。兩個做法：\n"
            "  1. export ANTHROPIC_API_KEY=sk-ant-...\n"
            "  2. 裝 ant CLI 之後跑 `ant auth login`\n"
            "見 docs/API-MODULES.md。"
        )
    return anthropic.Anthropic()


@dataclass
class Call:
    """一次呼叫嘅結果 ＋ 實際用量。用量要留低 —— 冇佢就估唔到成本。"""
    job: str
    model: str
    text: str
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read: int = 0
    cache_write: int = 0
    stop_reason: str = ""

    @property
    def cache_hit(self) -> bool:
        return self.cache_read > 0


@dataclass
class Run:
    slug: str
    topic: str
    calls: list[Call] = field(default_factory=list)
    files: dict[str, str] = field(default_factory=dict)
    verdict: str = ""
    notes: list[str] = field(default_factory=list)

    def totals(self) -> dict:
        return {
            "calls": len(self.calls),
            "input": sum(c.input_tokens for c in self.calls),
            "output": sum(c.output_tokens for c in self.calls),
            "cache_read": sum(c.cache_read for c in self.calls),
            "cache_write": sum(c.cache_write for c in self.calls),
        }


def _ask(cli, b: brain_mod.Brain, job: str, prompt: str,
         schema: dict | None = None) -> Call:
    """一次呼叫。system = 快取前綴，messages = 今次要做嘅嘢。"""
    r = route_for(job)
    kw: dict = {
        "model": r.model,
        "max_tokens": MAX_TOKENS,
        "system": brain_mod.system_blocks(b),
        "messages": [{"role": "user", "content": prompt}],
        "thinking": {"type": "adaptive"},
        "output_config": {"effort": r.effort},
    }
    if schema:
        kw["output_config"]["format"] = {"type": "json_schema", "schema": schema}

    resp = cli.messages.create(**kw)
    text = next((blk.text for blk in resp.content if blk.type == "text"), "")
    u = resp.usage
    return Call(
        job=job, model=r.model, text=text,
        input_tokens=u.input_tokens, output_tokens=u.output_tokens,
        cache_read=getattr(u, "cache_read_input_tokens", 0) or 0,
        cache_write=getattr(u, "cache_creation_input_tokens", 0) or 0,
        stop_reason=resp.stop_reason or "",
    )


# ── 三步嘅指示 ────────────────────────────────────────────────────

ANGLES = """今個星期嘅主題：{topic}

出 3–6 個候選角度。**唔好自己揀，由人揀。**

每個角度要有：
- 受眾嘅張力（佢而家心入面嗰個未解決嘅嘢，用 03-audience-language.md 嘅原話講）
- 核心觀點（一句）
- 建議開場（跟 05-hook-library.md 入面 work 過嘅結構）
- 建議 CTA
- 風險（呢個角度最容易踩中邊條紅線）

{constraints}

唔好寫成稿。呢一步只係俾人揀方向。"""

DRAFT = """已批准嘅角度：{angle}

寫一份 Master Content，再改寫成每個平台嘅版本。

平台：{platforms}

Master 要有：受眾問題 / 核心觀點 / 3–5 個重點 / 證據（如果有）/ CTA

**平台版本唔係複製貼上改幾隻字。** 每個平台重新寫開場、重新排節奏、
重新諗 CTA —— 因為每個平台嘅人喺唔同心態下睇嘢。跟 06-platform-rules.md。

逐項對返 02-voice-profile.md 嘅數字：句長、開場類型、標點頻率、稱呼。

{constraints}

用 Markdown，每個平台一個 `## ` 標題。"""

QA = """下面係要審嘅稿。對照 BIBLE.md 嘅紅線同 CHECKLIST.md 判定。

機械式檢查（已經行咗，唔使你重做）：
{mech}

你要判斷機械檢查做唔到嘅嘢：
- 有冇**暗示**咗一個冇出處嘅宣稱（唔用數字，但令人以為有效果）
- 語氣同 02-voice-profile.md 嘅數字有幾遠
- 有冇扮引用客人講過嘅嘢
- 有冇踩到機械檢查抽唔到詞嗰幾條紅線

退回嘅時候一定要指明**違反邊一條**，同**應該補去邊一層**
（BIBLE 紅線／語氣檔／證據庫／平台規格）。改一篇稿而唔改嗰一層，
下次一定會再犯。

---
{draft}"""

VERDICT_SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": ["pass", "revise", "block"]},
        "reason": {"type": "string"},
        "violations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "rule": {"type": "string"},
                    "where": {"type": "string"},
                    "fix_layer": {
                        "type": "string",
                        "enum": ["bible", "voice", "claims", "platform", "draft"],
                    },
                },
                "required": ["rule", "where", "fix_layer"],
                "additionalProperties": False,
            },
        },
        "voice_notes": {"type": "string"},
    },
    "required": ["verdict", "reason", "violations", "voice_notes"],
    "additionalProperties": False,
}


# ── 主流程 ────────────────────────────────────────────────────────

def angles(cdir: Path, topic: str, cli=None) -> Run:
    """第 1 步：出候選角度。停喺度等人揀 —— 呢個係第一道人手閘。"""
    b = brain_mod.load(cdir)
    cli = cli or client()
    run = Run(slug=b.slug, topic=topic)

    c = _ask(cli, b, "研究／選題",
             ANGLES.format(topic=topic, constraints=brain_mod.constraints_note(b)))
    run.calls.append(c)
    run.files[f"queue/01-insights/{date.today().isoformat()}-{_safe(topic)}.md"] = (
        f"# 候選角度 — {topic}\n\n"
        f"> {date.today().isoformat()} · {c.model} · 等人揀主角度\n\n"
        f"{c.text}\n"
    )
    run.notes.append("停咗喺呢度：要人揀一個角度先寫得稿。")
    return run


def draft(cdir: Path, topic: str, angle: str, cli=None) -> Run:
    """第 2、3 步：寫稿 → 兩層 QA。過到就入 03-approved 等人批。"""
    b = brain_mod.load(cdir)
    cli = cli or client()
    run = Run(slug=b.slug, topic=topic)
    stamp = date.today().isoformat()
    name = f"{stamp}-{_safe(topic)}"

    # ── 寫稿 ──
    d = _ask(cli, b, "文案（Master）", DRAFT.format(
        angle=angle,
        platforms="、".join(b.platforms) or "（未指定）",
        constraints=brain_mod.constraints_note(b),
    ))
    run.calls.append(d)

    # ── QA 第一層：機械式，唔靠模型 ──
    mech = guard.check(d.text, b.redlines, allow_numbers=b.has_claims)
    mech_md = guard.render(mech)

    # ── QA 第二層：模型判斷機械做唔到嘅嘢 ──
    q = _ask(cli, b, "QA／紅線檢查",
             QA.format(mech=mech.summary(), draft=d.text),
             schema=VERDICT_SCHEMA)
    run.calls.append(q)

    try:
        v = json.loads(q.text)
    except json.JSONDecodeError:
        v = {"verdict": "revise", "reason": "QA 回覆解析唔到，當退回處理。",
             "violations": [], "voice_notes": ""}

    # 兩層都要過。機械層有硬違規，模型話 pass 都唔算數 ——
    # 唔係唔信模型，係「兩個獨立檢查都要過」本身就係設計。
    #
    # 判定唔可以跌返去用模型嗰個。之前咁寫，機械層攔咗而模型話 pass 嘅時候，
    # 檔案正確咁入咗草稿，但 verdict 顯示「pass」—— dashboard 同硬碟講兩件事。
    model_verdict = v.get("verdict", "revise")
    passed = mech.clean and model_verdict == "pass"
    if passed:
        run.verdict = "pass"
    elif not mech.clean:
        run.verdict = "blocked-by-guard"      # 機械層攔嘅，同模型意見無關
    else:
        run.verdict = model_verdict

    body = [
        f"# {topic}", "",
        f"> {stamp} · 角度：{angle}", "",
        d.text, "", "---", "", mech_md, "",
        "## 模型 QA", "",
        f"**判定：{v.get('verdict')}** — {v.get('reason', '')}", "",
    ]
    if v.get("violations"):
        body += ["| 違反 | 出現喺 | 應該補去邊層 |", "|---|---|---|"]
        body += [f"| {x.get('rule','')} | {x.get('where','')} | {x.get('fix_layer','')} |"
                 for x in v["violations"]]
        body.append("")
    if v.get("voice_notes"):
        body += ["**語氣對照**", "", v["voice_notes"], ""]

    stage = "03-approved" if passed else "02-drafts"
    run.files[f"queue/{stage}/{name}.md"] = "\n".join(body)
    if passed:
        run.notes.append("兩層 QA 都過咗，入咗待人批。**仲未出街 —— 要你撳批准。**")
    elif run.verdict == "blocked-by-guard":
        run.notes.append(
            f"機械式檢查攔住咗（{len(mech.hard)} 處）。模型 QA 話「{model_verdict}」，"
            "但機械層搵到嘅嘢唔靠判斷 —— 搵到就係搵到。留喺草稿。"
        )
    else:
        run.notes.append(
            f"模型 QA 判定 {run.verdict}。留喺草稿，見檔案入面「應該補去邊層」。"
        )
    return run


def write(cdir: Path, run: Run) -> list[str]:
    """把產出寫落工作台。回寫咗邊幾個檔案。"""
    out = []
    for rel, body in run.files.items():
        p = Path(cdir) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
        out.append(rel)
    return out


def _safe(s: str) -> str:
    keep = [ch for ch in s.strip()[:24] if ch.isalnum() or "一" <= ch <= "鿿"]
    return "".join(keep) or "untitled"
