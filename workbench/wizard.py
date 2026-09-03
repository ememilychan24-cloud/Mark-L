#!/usr/bin/env python3
"""
設定精靈：撳掣就完成，唔使填嘢。

**選項喺呢度算，唔喺瀏覽器度算。**
點解：行業→平台→紅線→崗位嘅推導邏輯已經喺 taxonomy.py。如果瀏覽器再寫多份，
兩邊就會慢慢唔同步，而唔同步嘅嗰邊通常係人睇到嗰邊 —— 即係客戶會見到一個
同實際生成出嚟唔一樣嘅工作台。所以瀏覽器淨係負責畫，唔負責諗。

每一步都要答到：
  1. 而家問緊咩（一句，唔使諗）
  2. 有咩揀（大按鈕，預設已經幫你揀好）
  3. 揀完之後下一步會變成點

「預設已經揀好」係重點。一個 80 歲嘅人唔應該要決定「我需唔需要 funnel agent」——
佢應該見到已經揀咗嘅嘢，覺得唔啱先撳走。
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field

from .taxonomy import (
    ARCHETYPES, ARCHETYPE_BY_KEY, MODIFIERS, MODIFIER_BY_KEY,
    PLATFORM_ALIASES, Brief, classify, roster,
)

# 平台顯示名。用人話，唔用代號 —— 「xhs」對一般人嚟講唔係一個字。
PLATFORM_LABELS = {
    "ig": ("Instagram", "圖同短片為主，日常感"),
    "xhs": ("小紅書", "搜尋型平台，收藏比讚重要"),
    "threads": ("Threads", "純文字，靠一句話勾起好奇"),
    "fb": ("Facebook", "年紀大啲嘅受眾，要穩陣"),
    "yt": ("YouTube", "長片同教學"),
    "tiktok": ("TikTok", "短片，節奏要快"),
    "linkedin": ("LinkedIn", "B2B、專業形象"),
    "edm": ("電郵 EDM", "熟客同名單"),
    "web": ("自家網站", "落地頁同 SEO"),
    "whatsapp": ("WhatsApp", "查詢同跟進"),
    "wechat": ("微信", "內地客"),
}

# 技能顯示名。同樣：講佢幫你做到咩，唔好講個技術名。
SKILL_LABELS = {
    "brand-voice": ("學你嘅語氣", "由你出過嘅帖，算出句長、開場、禁忌", True),
    "content-calendar": ("排內容日程", "每週出選題同排程", True),
    "image-gen": ("做圖", "跟你嘅顏色同畫風生成圖卡", False),
    "visual-identity-scan": ("認出你嘅畫風", "由已出街嘅圖，讀返顏色、排版、風格", False),
    "ad-copy": ("寫廣告文案", "投放用嘅短文案同標題", False),
    "edm": ("寫電郵", "EDM 同名單跟進", False),
    "product-copy": ("寫產品文案", "賣點、詳情頁、規格", False),
    "case-study": ("寫個案", "把做過嘅嘢寫成有出處嘅個案", False),
    "proposal": ("寫提案", "把功能翻譯成客戶聽得明嘅好處", False),
    "comment-triage": ("分流留言私訊", "分成 FAQ／疑慮／查詢／選題四類", False),
    "faq-builder": ("建 FAQ 知識庫", "把重複問題變成標準答案", False),
    "escalation": ("轉人手機制", "高風險對話唔會自動回", False),
    "booking-funnel": ("接預約", "由內容接到落表格同跟進", False),
    "curriculum-slice": ("切課程內容", "把課堂知識變成公開內容", False),
    "impact-report": ("寫成效報告", "俾捐款人同持份者睇", False),
    "seo": ("搜尋排名", "關鍵字同網站文案", False),
    "local-seo": ("本地搜尋", "地圖、營業時間、評論", False),
    "report-builder": ("每週覆盤", "邊條 work、點解 work、下輪改咩", True),
    "compliance-check": ("合規檢查", "出街前逐條紅線機械式檢查", False),
    "cross-post": ("跨平台改寫", "同一觀點喺每個平台重新寫過", False),
}

ROLE_LABELS = {
    "orchestrator": ("總監", "派工同驗收"),
    "research": ("研究", "諗選題同角度"),
    "content": ("文案", "寫稿"),
    "qa": ("品質", "出街前逐條檢查"),
    "analytics": ("數據", "覆盤同下輪建議"),
    "visual": ("視覺", "做圖"),
    "video": ("影片", "腳本同剪片"),
    "engage": ("社群", "覆留言私訊"),
    "funnel": ("轉化", "接表格同名單"),
}

STEPS = [
    ("industry", "你做邊行？"),
    ("confirm", "係咪講中咗你？"),
    ("platforms", "你喺邊度出內容？"),
    ("jobs", "想佢幫你做啲咩？"),
    ("visual", "你嘅圖係咩樣？"),
    ("review", "睇一眼就開工"),
]
STEP_KEYS = [k for k, _ in STEPS]


@dataclass
class Choice:
    """一個可以撳嘅選項。"""
    id: str
    label: str
    hint: str = ""
    selected: bool = False
    locked: bool = False       # 已經由前面嘅選擇決定，撳唔郁
    why: str = ""              # locked 嘅原因，一定要講


@dataclass
class Draft:
    """精靈入面嘅狀態。全部有預設值 —— 用戶乜都唔撳都行得。"""
    archetype: str | None = None
    modifiers: list[str] = field(default_factory=list)
    platforms: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    brand_name: str = ""
    handles: list[str] = field(default_factory=list)
    sites: list[str] = field(default_factory=list)
    visual: dict = field(default_factory=dict)   # 由瀏覽器分析圖片得出
    sentence: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def seed_from_sentence(text: str) -> Draft:
    """如果用戶肯打一句嘢，就用返分類器 —— 唔肯打都完全冇問題。"""
    if not text.strip():
        return Draft()
    b: Brief = classify(text)
    return Draft(
        archetype=b.archetype.key if b.archetype.key != "generic" else None,
        modifiers=[m.key for m in b.modifiers],
        platforms=list(b.platforms),
        skills=list(b.skills),
        brand_name=b.brand_name or "",
        handles=list(b.handles),
        sites=list(b.sites),
        sentence=text.strip(),
    )


def apply_archetype_defaults(d: Draft) -> Draft:
    """揀完行業，即刻幫佢揀埋平台同工作 —— 呢個就係「唔使填」嘅關鍵。

    只喺對應欄位仲係空嘅時候先填。用戶自己撳過嘅嘢，唔可以被預設蓋返。
    """
    if not d.archetype:
        return d
    a = ARCHETYPE_BY_KEY[d.archetype]
    if not d.platforms:
        d.platforms = list(a.default_platforms)
    if not d.skills:
        d.skills = list(a.skills)
    return d


def derived(d: Draft) -> dict:
    """由目前選擇推導出嚟嘅嘢。呢個係 review 頁同 confirm 頁顯示嘅內容。"""
    if not d.archetype:
        return {"agents": [], "redlines": [], "pain": "", "unlock": "", "label": ""}
    a = ARCHETYPE_BY_KEY[d.archetype]
    mods = [MODIFIER_BY_KEY[m] for m in d.modifiers if m in MODIFIER_BY_KEY]

    redlines = list(a.redlines)
    for m in mods:
        for r in m.redlines:
            if r not in redlines:
                redlines.append(r)

    agents = roster(a, mods)
    # 技能會加崗位：揀咗做圖就要視覺崗位，揀咗覆留言就要社群崗位。
    # 呢個係「揀工作」同「請人」之間嘅連接 —— 用戶唔使諗編制。
    for skill, role in (("image-gen", "visual"), ("visual-identity-scan", "visual"),
                        ("comment-triage", "engage"), ("faq-builder", "engage"),
                        ("escalation", "engage"), ("booking-funnel", "funnel"),
                        ("proposal", "funnel"), ("edm", "funnel")):
        if skill in d.skills and role not in agents and len(agents) < 8:
            agents.append(role)

    return {
        "label": a.label,
        "pain": a.pain,
        "unlock": a.unlock,
        "agents": [{"id": r, "label": ROLE_LABELS[r][0], "hint": ROLE_LABELS[r][1]}
                   for r in agents],
        "redlines": redlines,
        "modifiers": [{"id": m.key, "label": m.label, "why": m.why, "n": len(m.redlines)}
                      for m in mods],
    }


def options(step: str, d: Draft) -> dict:
    """一步嘅完整內容：問題、選項、可唔可以繼續。"""
    idx = STEP_KEYS.index(step)
    title = STEPS[idx][1]
    out: dict = {
        "step": step, "index": idx, "total": len(STEPS), "title": title,
        "choices": [], "multi": False, "can_advance": True, "note": "", "sub": "",
    }

    if step == "industry":
        out["sub"] = "撳一個最似你嘅。揀錯咗之後改得返。"
        out["choices"] = [
            asdict(Choice(id=a.key, label=a.label, hint=a.pain.split("。")[0] + "。",
                          selected=(d.archetype == a.key)))
            for a in ARCHETYPES
        ]
        out["can_advance"] = bool(d.archetype)
        if not d.archetype:
            out["note"] = "揀一個先可以繼續。"

    elif step == "confirm":
        dv = derived(d)
        out["sub"] = "呢啲係跟住你個行業自動配好嘅。唔啱就撳走。"
        out["multi"] = True
        auto = {m["id"] for m in dv["modifiers"]}
        out["choices"] = [
            asdict(Choice(
                id=m.key, label=m.label, hint=f"{m.why}（＋{len(m.redlines)} 條紅線）",
                selected=(m.key in d.modifiers),
                why="由你嘅行業或者句子偵測到" if m.key in auto else "",
            ))
            for m in MODIFIERS
        ]
        out["derived"] = dv
        out["note"] = ("呢啲叫「合規修飾」—— 講錯呢幾類嘢係要負責任嘅，"
                       "所以工作台會逐條攔住。冇關嘅可以撳走。")

    elif step == "platforms":
        out["sub"] = "已經幫你揀咗常用嗰幾個。加減都得。"
        out["multi"] = True
        order = list(d.platforms) + [k for k in PLATFORM_LABELS if k not in d.platforms]
        out["choices"] = [
            asdict(Choice(id=p, label=PLATFORM_LABELS[p][0], hint=PLATFORM_LABELS[p][1],
                          selected=(p in d.platforms)))
            for p in order if p in PLATFORM_LABELS
        ]
        out["can_advance"] = bool(d.platforms)
        if not d.platforms:
            out["note"] = "至少揀一個。"

    elif step == "jobs":
        out["sub"] = "已經按你個行業揀好。想加想減都得 —— 揀嘅嘢會決定請幾多個崗位。"
        out["multi"] = True
        a = ARCHETYPE_BY_KEY[d.archetype] if d.archetype else None
        rec = set(a.skills) if a else set()
        order = list(d.skills) + [k for k in SKILL_LABELS if k not in d.skills]
        ch = []
        for s in order:
            if s not in SKILL_LABELS:
                continue
            label, hint, core = SKILL_LABELS[s]
            ch.append(asdict(Choice(
                id=s, label=label, hint=hint, selected=(s in d.skills),
                locked=core, why="呢個係基本盤，冇咗就唔係一個工作台" if core else
                       ("你個行業通常都要" if s in rec else ""),
            )))
        out["choices"] = ch
        out["derived"] = derived(d)

    elif step == "visual":
        out["sub"] = ("掉幾張你出過嘅圖入嚟，工作台會自己讀返你嘅顏色。"
                      "唔想做可以直接跳過。")
        out["multi"] = False
        out["choices"] = []
        out["visual"] = d.visual
        out["note"] = ("啲圖唔會離開你部機 —— 分析喺你個瀏覽器度做，"
                       "只有算出嚟嘅色碼會存落工作台。")
        out["handles"] = d.handles

    elif step == "review":
        dv = derived(d)
        out["sub"] = "撳落去就會喺你部機度整好成個工作台。"
        out["derived"] = dv
        out["summary"] = {
            "brand": d.brand_name or "（未改名）",
            "archetype": dv["label"],
            "platforms": [PLATFORM_LABELS[p][0] for p in d.platforms if p in PLATFORM_LABELS],
            "skills": [SKILL_LABELS[s][0] for s in d.skills if s in SKILL_LABELS],
            "agents": dv["agents"],
            "redlines": dv["redlines"],
            "palette": d.visual.get("palette", []),
            "handles": d.handles,
        }
        out["can_advance"] = bool(d.archetype and d.platforms)

    return out


def sentence_for(d: Draft) -> str:
    """把撳出嚟嘅選擇，砌返一句 pipeline 食得嘅描述。

    點解要砌返一句：pipeline.onboard 嘅入口係一句話，而且會把原話存落
    workspace.json。存住原話，日後就查得返「當初點解咁分類」。
    用精靈撳出嚟嘅，一樣要留低呢個紀錄。
    """
    if d.sentence:
        return d.sentence
    a = ARCHETYPE_BY_KEY[d.archetype] if d.archetype else None
    bits = [f"{d.brand_name or '呢個品牌'}係{a.label if a else '未分類業務'}"]
    if d.platforms:
        bits.append("用開 " + "、".join(
            PLATFORM_LABELS[p][0] for p in d.platforms if p in PLATFORM_LABELS))
    if d.handles:
        bits.append("帳號 " + "、".join("@" + h for h in d.handles))
    return "，".join(bits) + "（由設定精靈建立）"


def brief_from_draft(d: Draft) -> Brief:
    """把撳出嚟嘅選擇，變成 pipeline 收得嘅 Brief。

    留意：呢度**唔會**再跑分類器。用戶撳咗咩就係咩 —— 佢撳完 A 之後
    見到工作台出咗 B，係最快摧毀信任嘅方式。
    """
    a = ARCHETYPE_BY_KEY[d.archetype] if d.archetype else None
    if a is None:
        raise ValueError("未揀行業")

    b = Brief(raw=sentence_for(d), archetype=a)
    b.modifiers = [MODIFIER_BY_KEY[m] for m in d.modifiers if m in MODIFIER_BY_KEY]
    b.platforms = list(d.platforms)
    b.handles = list(d.handles)
    b.sites = list(d.sites)
    b.brand_name = d.brand_name or (d.handles[0] if d.handles else a.key)
    b.evidence = {
        "archetype": "由設定精靈人手揀，唔係推斷",
        "platforms": "由設定精靈人手揀",
    }
    for m in b.modifiers:
        b.evidence[f"modifier:{m.key}"] = "由設定精靈確認"

    # 精靈揀嘅嘢冇歧義，但仲有真實嘅缺口要講明 —— 呢兩樣機器補唔到。
    b.ambiguous = []
    if not d.visual.get("n"):
        b.ambiguous.append("未交過參考圖 —— 品牌視覺係空，未可以生圖。")
    if not d.handles and not d.sites:
        b.ambiguous.append("冇帳號亦冇網址 —— 爬唔到現有內容，語氣檔會係空嘅。")
    return b


# skills 由 Draft 決定，唔用 archetype 預設 —— 用戶撳走咗嘅唔應該回來
def skills_for(d: Draft) -> list[str]:
    return list(d.skills)
