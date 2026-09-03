#!/usr/bin/env python3
"""
讀 agency 目錄 → 算出每個客嘅生產線狀態。

設計重點：**狀態由檔案系統推導，唔另外存一份 state.json。**
存多一份狀態就一定會同實際檔案脫節（同 CSV 索引一樣嘅問題），
而脫節嘅 dashboard 比冇 dashboard 更差 —— 因為人會信佢。

呢度唔會問「做咗幾多」，只會問三條：
  1. 依家塞喺邊一格
  2. 等緊邊個做嘢（人定 AI）
  3. 有咩嘢阻住咗，唔補就唔可以出街
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from pathlib import Path

# 生產線。每格：(目錄, 顯示名, 完成呢格之後等緊邊個)
STAGES: tuple[tuple[str, str, str], ...] = (
    ("00-briefs", "工作簡報", "ai"),
    ("01-insights", "候選角度", "human"),   # 人揀主角度
    ("02-drafts", "文案草稿", "ai"),        # QA 審
    ("03-approved", "已過品質", "human"),   # 人批文案
    ("04-assets", "視覺素材", "human"),     # 人批畫面
    ("05-scheduled", "已排程", "done"),
)
SIDE_STAGES = (("06-replies", "待回覆", "human"),)

EMPTY_MARK = "（空）"


@dataclass
class Blocker:
    """阻塞：唔補就唔可以出街嘅嘢。每條都要講到「唔補會點」。"""
    key: str
    what: str
    consequence: str
    fix: str
    severity: str = "block"      # block | warn
    owner: str = "client"        # client | agency


@dataclass
class ClientState:
    slug: str
    brand: str
    archetype: str
    modifiers: list[str] = field(default_factory=list)
    platforms: list[str] = field(default_factory=list)
    agents: list[str] = field(default_factory=list)
    publish_mode: str = "review-only"
    created: str | None = None
    voice_confidence: str = "待評估"
    visual_confidence: str = "未建立"
    counts: dict[str, int] = field(default_factory=dict)
    waiting_on: dict[str, str] = field(default_factory=dict)
    blockers: list[Blocker] = field(default_factory=list)
    empty_buckets: list[str] = field(default_factory=list)
    next_action: str = ""
    health: str = "unknown"      # ready | attention | blocked | setup

    def to_dict(self) -> dict:
        d = asdict(self)
        d["blockers"] = [asdict(b) for b in self.blockers]
        return d


def _count(d: Path) -> int:
    """數實際交付物 —— .gitkeep 同隱藏檔唔算。"""
    if not d.is_dir():
        return 0
    return sum(1 for p in d.iterdir()
               if p.is_file() and not p.name.startswith(".") and p.name != ".gitkeep")


def _is_empty_bucket(p: Path) -> bool:
    """判斷 brand brain 一格係咪明文標示「空」。

    留意：呢度唔係睇檔案大細。scaffold 會寫一段解釋落去，所以檔案有內容但係空狀態。
    空係一個明確狀態，唔係一個要填嘅空格 —— 呢個判斷要同 scaffold 嘅寫法對得上。
    """
    if not p.is_file():
        return True
    return EMPTY_MARK in p.read_text(encoding="utf-8")[:400]


def _confidence(p: Path, default: str) -> str:
    if not p.is_file():
        return default
    m = re.search(r"信心度：\*\*(.+?)\*\*", p.read_text(encoding="utf-8")[:600])
    return m.group(1) if m else default


def read_client(cdir: Path) -> ClientState:
    mf = cdir / "workspace.json"
    meta = json.loads(mf.read_text(encoding="utf-8")) if mf.is_file() else {}

    st = ClientState(
        slug=cdir.name,
        brand=meta.get("brand", cdir.name),
        archetype=meta.get("archetype", "unspecified"),
        modifiers=meta.get("modifiers", []),
        platforms=meta.get("platforms", []),
        agents=meta.get("agents", []),
        publish_mode=meta.get("publish_mode", "review-only"),
        created=meta.get("created"),
    )

    brain = cdir / "brand" / "brain"
    st.voice_confidence = _confidence(brain / "02-voice-profile.md", meta.get("voice_confidence", "待評估"))
    st.visual_confidence = _confidence(cdir / "style" / "brand-visual.md", meta.get("visual_confidence", "未建立"))

    for key, _, owner in STAGES + SIDE_STAGES:
        n = _count(cdir / "queue" / key)
        st.counts[key] = n
        if n and owner in ("human", "ai"):
            st.waiting_on[key] = owner

    if brain.is_dir():
        st.empty_buckets = sorted(p.name for p in brain.glob("*.md") if _is_empty_bucket(p))

    st.blockers = _blockers(cdir, st)
    st.next_action, st.health = _next_action(st)
    return st


def _blockers(cdir: Path, st: ClientState) -> list[Blocker]:
    out: list[Blocker] = []

    if "04-approved-claims.md" in st.empty_buckets:
        out.append(Blocker(
            key="no-claims",
            what="已批准主張／證據係空",
            consequence="所有稿都唔可以出任何數字、個案、資格認證 —— 出咗就係無出處嘅宣稱。",
            fix="客戶提供有書面同意嘅個案、有出處嘅數據、證書掃描件，人手加入 04-approved-claims.md。",
            owner="client",
        ))

    if "03-audience-language.md" in st.empty_buckets:
        out.append(Blocker(
            key="no-audience-language",
            what="受眾原話係空",
            consequence="內容會用品牌自己嘅講法寫，唔係客人搜尋同轉述時用嘅講法，觸及會偏低。",
            fix="交 20–30 條真實查詢紀錄（WhatsApp／DM／留言），去除個人資料後蒸餾。",
            severity="warn",
            owner="client",
        ))

    if st.voice_confidence in ("低", "未建立", "待評估"):
        out.append(Blocker(
            key="voice-weak",
            what=f"語氣檔信心度：{st.voice_confidence}",
            consequence="第一批稿唔會似品牌，改稿量會大過自己寫。",
            fix="補 30 條以上自家社交貼文原文，再跑 distill.py。",
            severity="warn" if st.voice_confidence == "待評估" else "block",
            owner="agency",
        ))

    if st.visual_confidence in ("未建立", "低"):
        out.append(Blocker(
            key="visual-unset",
            what="品牌視覺未建立",
            consequence="生圖模型會自己加漸變、金色點綴、bokeh —— 出嚟唔似品牌，而且每張唔同。",
            fix="交 20–30 張已出街嘅圖，跑 visual-identity-scan 填返畫風同「從來冇出現」欄。",
            owner="client",
        ))

    consent = cdir / "data" / "consent"
    if any(m in st.modifiers for m in ("health-adjacent", "minors", "beauty-efficacy")) and not consent.is_dir():
        out.append(Blocker(
            key="no-consent-register",
            what="冇同意登記",
            consequence="呢個行業用真人素材而冇同意記錄，係法律風險，唔係內容風險。",
            fix="開 data/consent/，逐個案例記低同意範圍同日期。",
            owner="agency",
        ))

    if st.publish_mode != "review-only" and st.voice_confidence != "高":
        out.append(Blocker(
            key="autopublish-too-early",
            what="語氣未穩就開咗自動發布",
            consequence="品牌信任冇得回頭，慳嗰十分鐘唔值。",
            fix="workspace.json 改返 publish_mode: review-only。",
            owner="agency",
        ))

    return out


def _next_action(st: ClientState) -> tuple[str, str]:
    """一個客一次只講一句「下一步」。列十件事等於冇講。"""
    hard = [b for b in st.blockers if b.severity == "block"]
    idle = not any(st.counts.values())

    if hard:
        b = hard[0]
        who = "客戶" if b.owner == "client" else "我哋"
        # 分開兩件事：一個乜都未開始嘅客缺料，係「未設置」；
        # 一個生產線有嘢、但啲嘢出唔到街，先係「阻塞」。
        # 兩者用同一個紅燈，就會日日見到紅燈，然後冇人再望 dashboard。
        return f"{who}：{b.fix}", ("setup" if idle else "blocked")

    # 由後尾行返轉頭 —— 最接近出街嗰格優先清，唔好積喺尾段
    for key, label, owner in reversed(STAGES):
        n = st.counts.get(key, 0)
        if n and owner == "human":
            return f"審「{label}」{n} 件 → 批咗就落下一格", "attention"
    if st.counts.get("06-replies"):
        return f"審回覆草稿 {st.counts['06-replies']} 條", "attention"
    for key, label, owner in STAGES:
        if st.counts.get(key, 0) and owner == "ai":
            return f"AI 處理緊「{label}」{st.counts[key]} 件", "ready"

    if not any(st.counts.values()):
        soft = [b for b in st.blockers if b.severity == "warn"]
        if soft:
            return f"未有工作。開工前建議：{soft[0].fix}", "setup"
        return "工作台空閒 —— 可以開新一輪選題", "ready"
    return "全部已排程", "ready"


@dataclass
class AgencyState:
    root: str
    generated: str
    clients: list[ClientState] = field(default_factory=list)
    trend_packs: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "root": self.root,
            "generated": self.generated,
            "clients": [c.to_dict() for c in self.clients],
            "trend_packs": self.trend_packs,
            "totals": self.totals(),
        }

    def totals(self) -> dict:
        return {
            "clients": len(self.clients),
            "blocked": sum(1 for c in self.clients if c.health == "blocked"),
            "waiting_human": sum(
                c.counts.get(k, 0)
                for c in self.clients
                for k, _, o in STAGES + SIDE_STAGES if o == "human"
            ),
            "scheduled": sum(c.counts.get("05-scheduled", 0) for c in self.clients),
        }


def read_agency(root: Path) -> AgencyState:
    root = Path(root).expanduser().resolve()
    st = AgencyState(root=str(root), generated=datetime.now().isoformat(timespec="seconds"))

    cdir = root / "clients"
    if cdir.is_dir():
        for d in sorted(cdir.iterdir()):
            if d.is_dir() and not d.name.startswith("_"):
                st.clients.append(read_client(d))

    packs = root / "_trends" / "packs"
    if packs.is_dir():
        for p in sorted(packs.glob("*/pack.json")):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            retire = data.get("retire_after")
            expired = bool(retire) and str(retire) < date.today().isoformat()
            st.trend_packs.append({
                "id": data.get("id", p.parent.name),
                "label": data.get("label", ""),
                "retire_after": retire,
                "expired": expired,
                "samples": len(list((p.parent / "samples").glob("*"))) if (p.parent / "samples").is_dir() else 0,
            })
    return st
