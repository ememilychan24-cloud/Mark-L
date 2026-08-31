#!/usr/bin/env python3
"""
行業分類表：一句話業務描述 → archetype、合規修飾、員工編制、核心痛點。

點解要有呢張表，而唔係每次問模型：
分類要**穩定**。同一句嘢今日分做 ecommerce、聽日分做 retail，下游成個工作台
（員工編制、紅線、平台規格）就會跟住變，而冇人知點解變。呢張表係明文規則，
睇得到、改得到、argue 得到。模型可以喺分唔到嘅時候補上，但唔可以推翻已定嘅規則。

每個 archetype 要答三條嘢：
  1. 佢嘅生意流程係邊度塞住（pain）—— 呢個係我哋 present 俾客聽嘅嗰句
  2. 佢要邊幾個 AI 員工（roster）
  3. 佢有咩嘢係講錯就要負責任（modifiers → 紅線）
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

CORE_AGENTS = ["orchestrator", "research", "content", "qa", "analytics"]
MAX_AGENTS = 8


@dataclass(frozen=True)
class Archetype:
    key: str
    label: str
    # 呢個行業實際塞喺邊。present 嘅時候講呢句，唔好講「提升效率」。
    pain: str
    # 工作台幫佢拆開嘅嗰件事
    unlock: str
    extra_agents: tuple[str, ...] = ()
    default_platforms: tuple[str, ...] = ()
    # 呢個行業預設要裝嘅技能
    skills: tuple[str, ...] = ()

    # 關鍵詞分三級。點解要分：「網店賣紮肚服務」入面，「網店」講嘅係**賣嘅渠道**，
    # 「紮肚」講嘅係**交付咩**。交付物決定員工編制同紅線，渠道只決定平台 ——
    # 所以交付物一定要贏渠道，否則成個工作台會照電商嗰套砌，紅線會漏。
    decisive: tuple[str, ...] = ()   # 講明交付咩，權重 6
    keywords: tuple[str, ...] = ()   # 一般行業詞，權重 3
    weak: tuple[str, ...] = ()       # 通用商業詞（賣、產品、服務），權重 1

    # 呢行特有、寫死落 BIBLE 嘅紅線
    redlines: tuple[str, ...] = ()

    def weights(self) -> dict[str, int]:
        w: dict[str, int] = {}
        for word in self.weak:
            w[word] = 1
        for word in self.keywords:
            w[word] = 3
        for word in self.decisive:
            w[word] = 6
        return w


ARCHETYPES: tuple[Archetype, ...] = (
    Archetype(
        key="agency-creative",
        label="Marketing／廣告代理",
        pain="每個客一套做法，全部喺人腦入面。做嘢嘅人一走，個客嘅語氣同禁忌就冇咗。"
             "新人上手要跟三個月，而且每次交稿都要 AD 逐隻字改。",
        unlock="每個客一個獨立工作台，語氣、紅線、已批准講法全部係檔案。"
               "新人第一日就用同一套規矩交稿，AD 只審有爭議嗰啲。",
        extra_agents=("engage",),
        default_platforms=("ig", "fb", "threads", "xhs"),
        skills=("brand-voice", "content-calendar", "ad-copy", "edm", "report-builder"),
        decisive=("marketing", "廣告代理", "agency"),
        keywords=("廣告", "營銷", "推廣", "代理"),
        redlines=(
            "唔可以把 A 客嘅個案、數據、講法搬去 B 客",
            "客戶未批准嘅 Claim 唔可以出街",
        ),
    ),
    Archetype(
        key="design-studio",
        label="設計工作室",
        pain="靚嘢做得出，但講唔出點解值呢個價。提案九成篇幅係圖，"
             "客戶問「點解要咁」就答唔到，最後變成鬥改稿同鬥平。",
        unlock="每個提案自動配一份「設計理由」：呢個色解決咩、呢個排版對住邊個受眾。"
               "改稿次數跌，因為爭論由品味變成目標。",
        extra_agents=("visual",),
        default_platforms=("ig", "xhs"),
        skills=("brand-voice", "visual-identity-scan", "image-gen", "case-study"),
        decisive=("設計工作室", "品牌設計", "平面設計", "design studio"),
        keywords=("design", "設計", "工作室", "studio", "平面"),
        redlines=("唔可以用未買授權嘅字體、圖庫、音樂",),
    ),
    Archetype(
        key="social-ops",
        label="Social Media 營運",
        pain="日日追 deadline 出帖，冇時間諗。四個平台等於四份工，"
             "而覆盤永遠冇做 —— 所以下個月再由零開始諗題目。",
        unlock="一份主內容自動改寫成四個平台版本（唔係複製，係重寫 hook 同節奏），"
               "同埋每星期自動出一份「邊條 work、點解 work」，直接變下輪選題。",
        extra_agents=("engage", "visual"),
        default_platforms=("ig", "threads", "fb", "xhs"),
        skills=("brand-voice", "content-calendar", "cross-post", "comment-triage", "report-builder"),
        decisive=("social media", "內容營運", "小編"),
        keywords=("social", "營運", "kol", "帖文"),
        redlines=("回覆客人前一律要人批",),
    ),
    Archetype(
        key="web-dev",
        label="網頁／應用開發",
        pain="賣緊技術，但客戶聽唔明技術。報價單一堆功能名，客戶只係識比價錢，"
             "結果每單都要傾好耐先簽，簽完又不停改需求。",
        unlock="把功能自動翻譯成「你嘅生意會點樣改變」，報價變成方案。"
               "同時把每次改需求記錄成有出處嘅決定，收尾唔會拗數。",
        extra_agents=("funnel",),
        default_platforms=("linkedin", "fb"),
        skills=("brand-voice", "case-study", "proposal", "seo", "edm"),
        decisive=("網頁開發", "網站開發", "程式開發", "軟件開發", "saas", "software"),
        keywords=("網頁", "網站", "開發", "web", "程式", "系統"),
        redlines=("唔可以承諾未落實嘅交付日期同功能",),
    ),
    Archetype(
        key="kids-product",
        label="小朋友產品",
        pain="受眾係家長，用家係細路，兩把聲要用同一篇嘢講。"
             "而且講錯安全、成長、教育效果，係要負法律責任嘅。",
        unlock="家長版同小朋友版分開生成，安全同功效字眼行預設攔截，"
               "有小朋友出鏡嘅素材一律要監護人同意先入得工作台。",
        extra_agents=("visual",),
        default_platforms=("ig", "fb", "xhs"),
        skills=("brand-voice", "image-gen", "content-calendar", "compliance-check"),
        decisive=("玩具", "童裝", "嬰兒用品"),
        keywords=("小朋友", "兒童", "親子", "嬰兒", "kids", "baby"),
        redlines=(),  # 由 minors modifier 補
    ),
    Archetype(
        key="ecommerce",
        label="電商品牌",
        pain="產品好，但每張圖每篇文都要人由零起。上新款＝重做一次成套素材，"
             "所以出貨速度永遠追唔上補貨速度。",
        unlock="一個 SKU 入面嘅賣點，一次過生成主圖、詳情、廣告文案、EDM，"
               "全部跟返品牌語氣同已批准功效講法。",
        extra_agents=("visual", "funnel"),
        default_platforms=("ig", "xhs", "fb"),
        skills=("brand-voice", "image-gen", "ad-copy", "edm", "product-copy", "report-builder"),
        decisive=("電商", "e-commerce", "ecommerce", "shopify"),
        keywords=("網店", "shop"),
        weak=("賣", "產品"),
        redlines=("價格、庫存、運費要同後台一致",),
    ),
    Archetype(
        key="bpo-support",
        label="客服中心 / BPO",
        pain="同樣嘅問題答一萬次，但每個同事答法唔同。客人投訴嘅唔係答案錯，"
             "係「上次唔係咁講」。而知識庫永遠落後現實兩個月。",
        unlock="回覆由同一份已批准講法生成，語氣一致；答唔到嘅自動變成知識庫缺口清單，"
               "唔會沉底。高風險對話一律轉人手，唔會自動出街。",
        extra_agents=("engage",),
        default_platforms=("fb", "ig"),
        skills=("brand-voice", "comment-triage", "faq-builder", "escalation", "report-builder"),
        decisive=("客服", "客戶服務", "call center", "bpo", "熱線"),
        keywords=("support",),
        weak=("查詢",),
        redlines=(
            "投訴、退款、法律相關對話一律轉人手，唔可以自動回覆",
            "唔可以承諾補償金額或處理時限",
        ),
    ),
    Archetype(
        key="service-booking",
        label="預約制服務",
        pain="生意靠師傅同口碑，但口碑喺 WhatsApp 入面散晒。"
             "問極都係嗰幾條問題，答完冇人記低，落單率靠彩數。",
        unlock="把重複查詢變成內容（因為佢哋問嘅就係佢哋想睇嘅），"
               "把個案變成有同意書、有出處嘅證據庫，落單前嘅疑問內容自動處理咗。",
        extra_agents=("engage", "funnel"),
        default_platforms=("ig", "xhs", "fb", "threads"),
        skills=("brand-voice", "content-calendar", "comment-triage", "case-study", "booking-funnel"),
        decisive=("紮肚", "療程", "按摩", "診所", "預約", "salon", "美容院"),
        keywords=("美容", "booking", "纖體", "spa"),
        weak=("服務",),
        redlines=("個案分享要有書面同意並隱去可識別資料",),
    ),
    Archetype(
        key="education",
        label="教育／培訓",
        pain="課程內容係最強嘅資產，但全部困喺課室入面。"
             "招生靠減價，因為冇嘢俾人喺報名前判斷質素。",
        unlock="把課程知識切成公開內容，令人未報名已經學到嘢，"
               "報名變成「想學多啲」而唔係「邊間平」。",
        extra_agents=("funnel",),
        default_platforms=("ig", "fb", "threads", "yt"),
        skills=("brand-voice", "content-calendar", "curriculum-slice", "edm", "seo"),
        decisive=("補習", "課程", "培訓", "training", "course"),
        keywords=("教育", "導師", "school", "學院"),
        redlines=("唔可以保證成績、合格率或收入結果",),
    ),
    Archetype(
        key="local-storefront",
        label="實體店",
        pain="街客靠地點，熟客靠老闆記性。網上搵到嘅資料同店入面唔一樣，"
             "而評論冇人管，好嘅冇用，差嘅冇覆。",
        unlock="店內現實（貨、價、時間）同對外內容綁埋一齊更新，"
               "評論分流成回覆同下輪內容題目。",
        extra_agents=("engage",),
        default_platforms=("ig", "fb"),
        skills=("brand-voice", "content-calendar", "comment-triage", "local-seo"),
        decisive=("門市", "實體店", "餐廳", "分店", "門店", "storefront"),
        keywords=("cafe", "咖啡"),
        redlines=("營業時間、地址、價格要同現場一致",),
    ),
    Archetype(
        key="b2b-services",
        label="B2B 專業服務",
        pain="專業嘢講得太深冇人明，講得太淺又似騙徒。"
             "銷售週期長，但中間六個月完全冇嘢同潛在客戶講。",
        unlock="把專業判斷變成一連串可以連續睇落去嘅內容，"
               "令長銷售週期有嘢可以跟進，而唔係靠 sales 死跟。",
        extra_agents=("funnel",),
        default_platforms=("linkedin", "fb"),
        skills=("brand-voice", "case-study", "proposal", "edm", "seo"),
        decisive=("b2b", "顧問公司", "會計", "審計", "consulting", "企業服務"),
        keywords=("顧問", "法律"),
        redlines=("唔可以提供個別專業意見，只可以講一般原則",),
    ),
    Archetype(
        key="creator-ip",
        label="個人品牌／創作者",
        pain="條數靠自己一個人出鏡。停一星期，數字就跌。"
             "想搵人幫手，但冇人講到嗰把聲。",
        unlock="把「嗰把聲」寫成可驗證嘅檔案（句長、開場、禁忌、口頭禪），"
               "第二個人（或 AI）寫出嚟嘅嘢過得到自己嗰關。",
        extra_agents=("visual", "engage"),
        default_platforms=("ig", "threads", "xhs", "yt"),
        skills=("brand-voice", "content-calendar", "image-gen", "comment-triage"),
        decisive=("個人品牌", "創作者", "自媒體", "influencer", "youtuber", "博主"),
        keywords=("kol",),
        redlines=(),
    ),
    Archetype(
        key="nonprofit",
        label="非牟利／社區組織",
        pain="做嘅嘢好有意義，但講出嚟好悶。捐款同義工靠一年一次活動，"
             "平時完全冇聲。",
        unlock="把日常工作變成持續可信嘅紀錄，令支持者知道錢去咗邊，"
               "而唔係一年感動一次。",
        extra_agents=("engage",),
        default_platforms=("fb", "ig"),
        skills=("brand-voice", "content-calendar", "impact-report", "edm"),
        decisive=("非牟利", "ngo", "慈善", "社企", "基金會", "nonprofit"),
        keywords=("義工",),
        redlines=(
            "服務對象嘅影像同故事要有書面同意",
            "唔可以誇大受助人數或成效",
        ),
    ),
)

ARCHETYPE_BY_KEY = {a.key: a for a in ARCHETYPES}

GENERIC = Archetype(
    key="generic",
    label="未分類業務",
    pain="（未分類：需要人手確認行業）",
    unlock="（未分類）",
    default_platforms=("ig", "fb"),
    skills=("brand-voice", "content-calendar"),
)


@dataclass(frozen=True)
class Modifier:
    key: str
    label: str
    why: str
    redlines: tuple[str, ...]
    keywords: tuple[str, ...] = ()
    # 呢類修飾強制要獨立 QA agent：自己審自己唔算合規
    force_qa: bool = True


MODIFIERS: tuple[Modifier, ...] = (
    Modifier(
        key="health-adjacent",
        label="健康相關",
        why="講身體、症狀、康復就落入醫療廣告嘅監管範圍，唔係「小心啲用字」咁簡單。",
        redlines=(
            "唔用「治療／根治／醫學證實／療效」呢類字眼",
            "任何身體症狀內容一律加「持續或惡化請諮詢醫護人員」",
            "唔提供劑量或療程建議",
            "個案分享要有書面同意並隱去可識別資料",
            "唔宣稱取代專業醫療意見",
        ),
        keywords=("健康", "產後", "紮肚", "療程", "身體", "康復", "醫", "護理", "營養",
                  "健身", "減肥", "wellness", "clinic", "supplement"),
    ),
    Modifier(
        key="beauty-efficacy",
        label="美容功效",
        why="體形、外觀嘅功效宣稱有獨立一套監管邏輯，同健康嗰套唔一樣，要疊埋一齊。",
        redlines=(
            "功效宣稱要有測試依據，唔可以用個人感受當證據",
            "前後對比圖要標明個人差異，同拍攝條件一致",
            "唔用「必瘦」「保證」「永久」呢類絕對詞",
        ),
        keywords=("美容", "瘦", "纖體", "塑形", "紮肚", "皮膚", "beauty", "slimming", "facial"),
    ),
    Modifier(
        key="finance-adjacent",
        label="金融相關",
        redlines=(
            "唔保證回報，唔講「穩賺」「低風險高回報」",
            "唔提供個人化投資建議",
            "所有數字要標明出處同日期",
        ),
        why="講錢嘅承諾係受規管嘅行為，講錯會有法律後果而唔係公關後果。",
        keywords=("金融", "投資", "保險", "貸款", "理財", "股票", "finance", "insurance", "loan"),
    ),
    Modifier(
        key="minors",
        label="涉及未成年",
        why="未成年人嘅影像同數據有獨立保護要求，唔可以當普通素材處理。",
        redlines=(
            "唔直接向兒童落 CTA",
            "唔用兒童真實影像（除非有監護人書面同意）",
            "唔收集兒童個人資料",
        ),
        keywords=("小朋友", "兒童", "學生", "嬰兒", "bb", "kids", "童", "青少年"),
    ),
    Modifier(
        key="regulated-hk",
        label="香港受規管行業",
        why="香港有《商品說明條例》同行業牌照要求，本地客戶唔可以照搬外地做法。",
        redlines=(
            "牌照號碼、資格要準確並可查證",
            "唔用誤導性價格表述（原價、限時要真實）",
        ),
        keywords=("持牌", "牌照", "註冊", "認可", "licence", "license"),
    ),
)

MODIFIER_BY_KEY = {m.key: m for m in MODIFIERS}

PLATFORM_ALIASES = {
    "小紅書": "xhs", "紅書": "xhs", "xiaohongshu": "xhs", "rednote": "xhs", "xhs": "xhs",
    "instagram": "ig", "ig": "ig", "insta": "ig",
    "threads": "threads", "thread": "threads",
    "facebook": "fb", "fb": "fb", "面書": "fb",
    "youtube": "yt", "yt": "yt", "油管": "yt",
    "tiktok": "tiktok", "抖音": "tiktok", "douyin": "tiktok",
    "linkedin": "linkedin",
    "whatsapp": "whatsapp",
    "wechat": "wechat", "微信": "wechat",
    "電郵": "edm", "email": "edm", "edm": "edm", "電子報": "edm",
    "網站": "web", "官網": "web", "website": "web",
}


@dataclass
class Brief:
    """一句話拆出嚟嘅結構。每一格都要知道係邊度嚟 —— 所以有 evidence。"""
    raw: str
    archetype: Archetype
    modifiers: list[Modifier] = field(default_factory=list)
    platforms: list[str] = field(default_factory=list)
    handles: list[str] = field(default_factory=list)
    sites: list[str] = field(default_factory=list)
    brand_name: str | None = None
    evidence: dict[str, str] = field(default_factory=dict)
    ambiguous: list[str] = field(default_factory=list)

    @property
    def agents(self) -> list[str]:
        return roster(self.archetype, self.modifiers)

    @property
    def redlines(self) -> list[str]:
        out = list(self.archetype.redlines)
        for m in self.modifiers:
            for r in m.redlines:
                if r not in out:
                    out.append(r)
        return out

    @property
    def skills(self) -> list[str]:
        out = list(self.archetype.skills)
        if self.modifiers and "compliance-check" not in out:
            out.append("compliance-check")
        if any(p in self.platforms for p in ("ig", "xhs", "tiktok")) and "image-gen" not in out:
            out.append("image-gen")
        return out


def roster(a: Archetype, mods: list[Modifier]) -> list[str]:
    """員工編制係推導出嚟，唔係揀出嚟。

    上限 8 個。爆咗就照 references/archetypes.md 嘅次序合併：
    visual+video → creative；research+analytics → insight。QA **永遠唔合併** ——
    合併咗 QA 就等於冇人審，而冇人審係呢個工作台唯一唔可以妥協嘅嘢。
    """
    agents = list(CORE_AGENTS)
    for extra in a.extra_agents:
        if extra not in agents:
            agents.append(extra)
    if len(agents) > MAX_AGENTS:
        agents = agents[:MAX_AGENTS]
    return agents


def _hit(text: str, words: tuple[str, ...]) -> str | None:
    low = text.lower()
    for w in words:
        if w.lower() in low:
            return w
    return None


def classify(text: str) -> Brief:
    """一句話 → Brief。純規則，唔使 API，所以每次跑結果一樣。"""
    b = Brief(raw=text.strip(), archetype=GENERIC)

    # archetype：加權計分。交付物（decisive, 6）＞ 行業詞（3）＞ 通用商業詞（1）
    low = text.lower()
    scored: list[tuple[int, list[str], Archetype]] = []
    for a in ARCHETYPES:
        hits = [w for w in a.weights() if w.lower() in low]
        if hits:
            scored.append((sum(a.weights()[w] for w in hits), hits, a))
    scored.sort(key=lambda s: -s[0])

    if scored:
        score, hits, a = scored[0]
        b.archetype = a
        b.evidence["archetype"] = f"命中「{'、'.join(hits)}」，得分 {score}"
        if len(scored) > 1:
            runner_score, runner_hits, runner = scored[1]
            # 差距細過一個 decisive 詞嘅重量 = 兩個行業都講得通，唔可以扮肯定。
            # 分錯行業唔係細節：員工編制、紅線、平台規格全部跟住錯。
            if score - runner_score < 6:
                b.ambiguous.append(
                    f"行業分唔清：{a.label}（{score}分）vs {runner.label}（{runner_score}分，"
                    f"命中「{'、'.join(runner_hits)}」）。要人手確認 —— 揀錯會連紅線一齊錯。"
                )
                b.evidence["archetype_runner_up"] = runner.key
    else:
        b.ambiguous.append("分唔到行業 —— 要人手指定 archetype，否則員工編制同紅線都係錯嘅。")

    for m in MODIFIERS:
        w = _hit(text, m.keywords)
        if w:
            b.modifiers.append(m)
            b.evidence[f"modifier:{m.key}"] = f"因為出現「{w}」"

    for alias, canon in PLATFORM_ALIASES.items():
        if alias.lower() in low and canon not in b.platforms:
            b.platforms.append(canon)
    if not b.platforms:
        b.platforms = list(b.archetype.default_platforms)
        b.evidence["platforms"] = "句子冇提平台，用咗 archetype 預設 —— 開工前要客戶確認。"
        b.ambiguous.append("平台係推測出嚟，未經確認。")
    else:
        b.evidence["platforms"] = "由句子直接抽取。"

    # 連字號要包 —— @bright-collective 斬成 @bright 就會開錯 slug、爬錯帳號
    b.handles = sorted(set(re.findall(r"@([A-Za-z0-9._-]{2,30})", text)))

    # 網址：要避開已經當咗 handle 嗰啲（@littlesprout.hk 唔係網站）
    handle_low = {h.lower() for h in b.handles}
    sites = set(re.findall(r"(?:https?://)?(?:www\.)?([a-z0-9-]+\.[a-z]{2,}(?:\.[a-z]{2,})?)", low))
    b.sites = sorted(sites - handle_low - {"gmail.com", "protonmail.com"})

    if b.handles:
        b.brand_name = b.handles[0]
    elif b.sites:
        b.brand_name = b.sites[0].split(".")[0]

    if not b.handles and not b.sites:
        b.ambiguous.append("冇帳號亦冇網址 —— 爬唔到現有內容，語氣檔會係空嘅。")

    return b


def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (name or "client").lower()).strip("-")
    return s or "client"
