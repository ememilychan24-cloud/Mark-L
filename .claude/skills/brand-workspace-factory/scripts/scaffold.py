#!/usr/bin/env python3
"""
生成一個 client workspace 嘅完整目錄樹。

先跑呢個，唔好逐個檔案手動創建 —— 手動創建最常見嘅錯誤係漏咗某個空櫃桶，
而空櫃桶漏咗之後 agent 唔知係「冇資料」定「未讀到」，就會自己補（幻覺來源）。

用法:
  python scaffold.py --root ./workspace --client acme-postpartum \\
      --name "Acme 產後護理" \\
      --archetype service-booking --modifiers health-adjacent \\
      --agents research,content,visual,qa,analytics,engage,funnel \\
      --platforms xhs,ig,threads,fb

再跑一次同一個 client 係安全嘅：已存在嘅檔案唔會被覆蓋（除非 --force）。
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

CORE_AGENTS = ["orchestrator", "research", "content", "qa", "analytics"]
OPTIONAL_AGENTS = ["visual", "video", "engage", "funnel"]

AGENT_LABELS = {
    "orchestrator": ("總監", "派工、驗收、對齊 BIBLE", "queue/00-briefs/"),
    "research": ("研究", "由市場訊號提煉 3–6 個候選角度", "queue/01-insights/"),
    "content": ("文案", "把已批准角度寫成 Master Content 及各平台版本", "queue/02-drafts/"),
    "qa": ("品質", "對照紅線與語氣檔判定可否交人審閱", "queue/03-approved/"),
    "visual": ("視覺", "把已批准內容變成圖卡與素材", "queue/04-assets/"),
    "video": ("影片", "把內容拆成腳本、字幕、封面與延伸卡片", "queue/04-assets/"),
    "engage": ("社群", "分流留言與私訊，草擬回覆", "queue/06-replies/"),
    "funnel": ("轉化", "承接內容到落地頁、表單與名單", "queue/05-scheduled/"),
    "analytics": ("數據", "週度覆盤與下一輪測試建議", "reports/"),
}

BRAIN_FILES = [
    ("01-positioning.md", "定位背景", "使命、產品、價值主張、競爭位置", False),
    ("02-voice-profile.md", "品牌語氣", "句長、開場、標點、稱呼、禁用詞", False),
    ("03-audience-language.md", "受眾語言", "受眾原話、反對理由、常用詞", True),
    ("04-approved-claims.md", "已批准主張／證據", "已授權個案、數據、產品事實", True),
    ("05-hook-library.md", "Hook 與成功例子", "有效開場結構，附原帖連結", True),
    ("06-platform-rules.md", "平台規格", "各平台格式、節奏、禁忌", False),
    ("07-review-log.md", "決策／Review 記錄", "批准、退回、修改原因", True),
    ("08-learning.md", "Learning 更新", "學到嘅有效做法與 SOP 修訂", True),
]

QUEUE_DIRS = [
    "00-briefs", "01-insights", "02-drafts", "03-approved",
    "04-assets", "05-scheduled", "06-replies",
]

EMPTY_NOTICE = """（空）

第一版未有內容。

**在此檔案為空期間，任何產出唔可以引用呢個櫃桶嘅資料。**
唔好因為空就自己推斷內容 —— 空係一個明確狀態，唔係一個要填嘅空格。

補充方式：{how}
"""

EMPTY_HOW = {
    "03-audience-language.md": "由留言區爬取後蒸餾，或由客戶提供真實客戶查詢記錄。",
    "04-approved-claims.md": "客戶提供有書面同意嘅個案或有出處嘅數據後，由人手加入並標明授權範圍。",
    "05-hook-library.md": "由自家高表現帖抽取開場結構，每條附原帖連結。",
    "07-review-log.md": "每次人手 review 之後補一條，記低批准／退回同原因。",
    "08-learning.md": "每次 campaign 完結後補一條，記低有效做法同 SOP 修訂。",
}


def w(path: Path, content: str, force: bool) -> bool:
    """寫檔案。已存在就跳過，除非 force。回傳有冇真係寫。"""
    if path.exists() and not force:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def bible(name: str, archetype: str, modifiers: list[str]) -> str:
    lines = [
        f"# {name} 品牌憲法",
        "",
        f"> 最後更新：{date.today().isoformat()} · 語料信心度：**待評估**",
        f"> Archetype：`{archetype}`" + (f" · Modifiers：{', '.join(f'`{m}`' for m in modifiers)}" if modifiers else ""),
        "",
        "## 一句話定位",
        "<賣咩，賣俾邊個，解決咩 — 由步驟 1 填>",
        "",
        "## 受眾（具體到可以認得出）",
        "- 年齡／人生階段：",
        "- 處境（幾時、喺邊、心情點）：",
        "- 佢自己點形容個問題：「<原話，由 03-audience-language.md 攞>」",
        "- 佢唔買嘅理由：",
        "",
        "## 語氣三行",
        "1. 好似 <一個具體嘅人物關係>",
        "2. 每篇都要 <一個必做動作>",
        "3. 從來唔會 <一個必唔做>",
        "",
        "## 紅線（違反即退回，唔需要討論）",
        "",
        "> 每一條都要可以機械式檢查。寫唔到檢查方法嘅，唔算紅線。",
        "",
        "- [ ] <未填 —— 行業同合規紅線由 taxonomy.py 寫入。單獨跑 scaffold.py 唔會有紅線，因為 scaffold 唔知你揀咗咩合規修飾。>",
    ]
    # 合規紅線**唔喺呢度寫**。唯一來源係 taxonomy.py，由 pipeline.inject_redlines
    # 寫入上面嗰個 placeholder。
    #
    # 之前呢度自己寫多份，結果每份 BIBLE 都有 15 條而唔係 8 條：5 條健康紅線
    # 重複兩次，而「功效宣稱要有測試依據」仲有長短兩個唔同版本並存。
    # 一份合規檔案入面同一條規矩有兩個講法，agent 就唔知邊個算數 ——
    # 呢個正正係「兩個真相來源一定會飄」嘅實例。

    lines += [
        "",
        "## 證據來源",
        "只可引用 `brand/brain/04-approved-claims.md` 入面嘅嘢。",
        "嗰份檔案為空 = 呢一輪唔可以落任何數據或個案 Claim。",
        "",
        "## 邊啲嘢一定要人批",
        "- 主角度同對外 Claim",
        "- 所有 CTA",
        "- <由客戶答案補充>",
        "",
    ]
    return "\n".join(lines)


def agents_md(role: str, brand: str, platforms: list[str]) -> str:
    label, goal, out = AGENT_LABELS[role]
    plat = "、".join(platforms) if platforms else "（未指定）"
    inputs = ["brand/BIBLE.md", "brand/brain/01-positioning.md", "brand/brain/02-voice-profile.md"]
    if role in ("research", "content", "engage"):
        inputs.append("brand/brain/03-audience-language.md")
    if role in ("content", "qa"):
        inputs += ["brand/brain/04-approved-claims.md", "brand/brain/06-platform-rules.md"]
    if role in ("content", "research"):
        inputs.append("brand/brain/05-hook-library.md")

    upstream = {
        "research": "data/scraped/",
        "content": "queue/01-insights/  ← 只讀已批准嘅",
        "qa": "queue/02-drafts/",
        "visual": "queue/03-approved/",
        "video": "queue/03-approved/",
        "funnel": "queue/03-approved/",
        "engage": "data/inbox/",
        "analytics": "queue/05-scheduled/ 及平台成效資料",
    }.get(role)
    if upstream:
        inputs.append(upstream)

    rules = {
        "orchestrator": [
            "唔好自己寫內容 —— 你嘅工作係派工同驗收",
            "任何 agent 交嘢，先對照 CHECKLIST.md 再決定收唔收",
            "同一個問題被退回兩次以上，要求補返 MEMORY.md 而唔係再改一次",
        ],
        "research": [
            "每個關鍵 Claim 要保留原始連結、平台、作者同日期",
            "唔可以把熱門內容直接當品牌立場 —— 熱門同啱唔啱係兩回事",
            "先出 3–6 個角度再由人揀，唔好自己落決定",
            "高互動唔等於有效：多讚可能係有爭議，多收藏先代表實用",
        ],
        "content": [
            "先寫一份 Master Content，再按平台改寫 —— 唔好四個平台改幾隻字",
            "每個平台重新寫 hook、重新排節奏、重新諗 CTA",
            "逐項對照 02-voice-profile.md 嘅數字（句長、標點、稱呼、emoji）",
            "04-approved-claims.md 為空時，唔可以落任何數字或個案",
        ],
        "qa": [
            "你嘅唯一標準來源係 CHECKLIST.md 同 BIBLE.md 嘅紅線，唔好加自己嘅偏好",
            "退回時一定要指明違反咗邊一條，同建議補去邊一層",
            "同一份稿唔好退回超過兩次 —— 第三次要升級俾人處理",
        ],
        "visual": [
            "視覺跟隨已批准內容，唔好先出靚圖再塞文字",
            "一張卡只承擔一個主要訊息",
            "品牌規格（顏色、字體、水印）由 06-platform-rules.md 決定，唔好每次重新描述",
        ],
        "video": [
            "把內容拆成聲音、畫面、字幕、封面、CTA 五層分別處理",
            "Repurpose 唔係搬運 —— 同一觀點要重新組織成另一種閱讀體驗",
            "局部重跑失敗嘅段落，唔好成套重做",
        ],
        "engage": [
            "分流先於回覆：分成 FAQ／反對理由／內容缺口／潛在查詢四類",
            "需要判斷或高價值嘅對話一律入 Review Queue，唔好自己答",
            "把重複問題送返 03-audience-language.md 同下一輪選題",
        ],
        "funnel": [
            "CTA 同追蹤參數喺設計時就要預留，唔好事後補",
            "完成標準係後台搵得返記錄，唔係前台彈「成功」",
            "每個名單要有來源、階段、負責人、下一步",
        ],
        "analytics": [
            "唔好用一個總分代替判斷 —— 沿流程逐層睇邊層掉失",
            "下一輪只建議改一個主要變數，否則分唔清改善來自邊度",
            "結論要寫返 08-learning.md，唔係淨係出報表",
        ],
    }[role]

    deliver = {
        "orchestrator": ["本週工作分派", "驗收結果（收／退／原因）"],
        "research": ["3–6 個候選角度，每個附受眾張力、證據連結、建議 hook 與 CTA、風險", "建議主角度同理由"],
        "content": ["master-content.md（受眾問題／核心觀點／3–5 個重點／證據／CTA）", f"各平台版本（{plat}）"],
        "qa": ["判定：Ready to Review 或 退回", "退回時：違反條目 ＋ 應補去邊一層"],
        "visual": ["圖卡檔案", "卡序說明（首卡 hook、尾卡 CTA）"],
        "video": ["腳本、字幕檔、封面", "延伸 Carousel 卡片"],
        "engage": ["回覆草稿（分流標記）", "送返選題嘅問題清單"],
        "funnel": ["落地頁 ／ 表單規格", "追蹤參數規則", "測試計劃"],
        "analytics": ["週報：保留／停止／再測／更新 Skill 四個決定", "下一輪測試建議（單一變數）"],
    }[role]

    check = {
        "orchestrator": "本週主題方向要人確認先開工。",
        "research": "主角度、對外 Claim、CTA 一律等人批准後先交俾文案。",
        "content": "主要文案、標題、CTA 要人批准後先交俾視覺。",
        "qa": "紅線違規一律升級俾人，唔可以自行放行。",
        "visual": "主要畫面要人批准後先入排程。",
        "video": "封面同 hook 要人批准。",
        "engage": "所有對外回覆要人批准後先發出。",
        "funnel": "對外承諾、收集資料範圍要人批准。",
        "analytics": "Skill 或品牌資料嘅修訂建議要人批准後先寫回。",
    }[role]

    return "\n".join([
        f"# {label} Agent — {brand}",
        "",
        "## Role",
        f"你係 {brand} 嘅{label} Agent。",
        "",
        "## Goal",
        goal + "。",
        "",
        "## Inputs（只可以讀呢啲）",
        *[f"- `{i}`" for i in inputs],
        "",
        "## Rules",
        *[f"- {r}" for r in rules],
        "",
        "## 交付成果",
        f"交去 `{out}`，包含：",
        *[f"- {d}" for d in deliver],
        "",
        "## 人手檢查點",
        check,
        "",
    ])


def memory_md() -> str:
    """決策與學習記錄。抽咗出嚟做函式，令 web 版可以由呢度匯出同一份範本 ——
    唔好喺 JS 手抄多一份。"""
    return "\n".join([
        "# 決策與學習記錄",
        "",
        "> 每次 review 之後補一條。「點解改」比「改成點」有用。",
        "",
        "## 已批准（可以再用）",
        "| 日期 | 咩嘢 | 點解 work | 連結 |",
        "|---|---|---|---|",
        "",
        "## 已退回（唔好再犯）",
        "| 日期 | 咩嘢 | 點解唔得 | 已補去邊層 |",
        "|---|---|---|---|",
        "",
        "> 「已補去邊層」填唔到，即係今次只執咗份稿冇改到系統，下次會再犯。",
        "",
        "## 已知問題",
        "",
        "## 下次提醒",
        "",
    ])


def checklist_md(brand: str) -> str:
    """交付前驗收清單。同上：一個來源。"""
    redlines = "- [ ] <由 BIBLE 紅線逐條複製過嚟>"
    return "\n".join([
        f"# {brand} 交付前驗收",
        "",
        "## 來源與證據",
        "- [ ] 每個數據／個案 Claim 有來源（標題／平台／作者／日期／連結）",
        "- [ ] 冇引用 04-approved-claims.md 以外嘅證據",
        "- [ ] 冇把同行觀點當成品牌立場",
        "",
        "## 品牌",
        "- [ ] 句長、開場類型、標點習慣對得上 02-voice-profile.md",
        "- [ ] 稱呼讀者用返固定講法",
        "- [ ] 冇用禁用詞",
        "- [ ] 平台規格符合 06-platform-rules.md",
        "",
        "## 紅線",
        redlines,
        "",
        "## 對外一致性",
        "- [ ] 內容、落地頁、表單、訊息講緊同一件事",
        "- [ ] CTA 清楚，下一步冇歧義",
        "- [ ] 連結行得通",
        "",
        "## 交付完整性",
        "- [ ] 文字／圖／caption／CTA／來源齊全",
        "- [ ] 檔名同路徑符合規範",
        "",
    ])


def main() -> int:
    p = argparse.ArgumentParser(description="生成 client workspace 目錄樹")
    p.add_argument("--root", required=True, help="agency 根目錄")
    p.add_argument("--client", required=True, help="client slug，例如 acme-postpartum")
    p.add_argument("--name", default=None, help="品牌顯示名（預設用 slug）")
    p.add_argument("--archetype", default="unspecified")
    p.add_argument("--modifiers", default="", help="逗號分隔")
    p.add_argument("--agents", default=",".join(CORE_AGENTS), help="逗號分隔角色")
    p.add_argument("--platforms", default="", help="逗號分隔平台")
    p.add_argument("--skills", default="", help="逗號分隔技能，見 references/skill-catalogue.md")
    p.add_argument("--force", action="store_true", help="覆蓋已存在檔案")
    a = p.parse_args()

    root = Path(a.root).expanduser().resolve()
    brand = a.name or a.client
    mods = [m.strip() for m in a.modifiers.split(",") if m.strip()]
    plats = [x.strip() for x in a.platforms.split(",") if x.strip()]
    agents = [x.strip() for x in a.agents.split(",") if x.strip()]

    unknown = [r for r in agents if r not in AGENT_LABELS]
    if unknown:
        print(f"未知角色：{', '.join(unknown)}", file=sys.stderr)
        print(f"可用：{', '.join(AGENT_LABELS)}", file=sys.stderr)
        return 2
    for r in CORE_AGENTS:
        if r not in agents:
            agents.insert(0, r)
    if len(agents) > 8:
        print(f"警告：{len(agents)} 個角色超過上限 8。見 references/archetypes.md 嘅合併次序。", file=sys.stderr)

    cdir = root / "clients" / a.client
    written = 0

    for shared in ("_templates", "_skills", "_archetypes"):
        (root / shared).mkdir(parents=True, exist_ok=True)

    written += w(cdir / "brand" / "BIBLE.md", bible(brand, a.archetype, mods), a.force)

    for fn, title, what, may_empty in BRAIN_FILES:
        num = fn.split("-")[0]
        if may_empty:
            body = f"# {num} · {title}\n\n" + EMPTY_NOTICE.format(
                how=EMPTY_HOW.get(fn, "由對應步驟蒸餾產生。")
            )
        else:
            body = f"# {num} · {title}\n\n<{what}>\n\n> 由步驟 3–4 填。留白等於冇資料，agent 會自己補 —— 所以寧願寫「未建立」。\n"
        written += w(cdir / "brand" / "brain" / fn, body, a.force)

    written += w(cdir / "brand" / "MEMORY.md", memory_md(), a.force)

    written += w(cdir / "CHECKLIST.md", checklist_md(brand), a.force)

    for role in agents:
        written += w(cdir / "agents" / role / "AGENTS.md", agents_md(role, brand, plats), a.force)

    for q in QUEUE_DIRS:
        d = cdir / "queue" / q
        d.mkdir(parents=True, exist_ok=True)
        written += w(d / ".gitkeep", "", a.force)

    for d in ("data/scraped", "data/inbox", "reports", "dashboard", "config",
              "skills", "style/renders"):
        (cdir / d).mkdir(parents=True, exist_ok=True)

    written += w(cdir / "style" / "brand-visual.md",
                 "# 品牌視覺 Brand Visual\n\n"
                 "> 樣本：0 張 · 信心度：**未建立**\n"
                 "> 由 `visual-identity-scan` 技能爬客戶現有內容產生。規格見 references/visual-system.md。\n\n"
                 "## 色彩\n- 主色：\n- 輔色：\n- 強調色：\n"
                 "- **從來冇出現**：<呢欄最重要 —— 冇寫低，生圖模型會自己加金色點綴、渐變、bokeh>\n\n"
                 "## 畫風\n- 攝影 / 插畫比例：\n- 光線：\n- 質感：\n- 主體處理：\n- 構圖：\n\n"
                 "## 排版\n- 字體：\n- 標題／內文字級比例：\n- 對齊：\n- 文字位置：\n- 每張圖文字量：\n\n"
                 "## 唔好做\n\n## ⚠️ 要人手確認\n- 有冇官方品牌指引？（如有，覆蓋以上觀察）\n"
                 "- Logo 使用規則同安全距離\n- 有冇唔可以用嘅顏色或元素\n",
                 a.force)

    written += w(cdir / "style" / "selected-packs.json",
                 json.dumps({"_note": "引用 _trends/packs/ 嘅 id，唔好複製 pack 內容。"
                                      "總公司更新 pack，呢個客自動跟到最新。",
                             "cover": None, "carousel": None, "reel_thumb": None,
                             "updated": None}, ensure_ascii=False, indent=2) + "\n",
                 a.force)

    for plat in plats:
        written += w(cdir / "skills" / "social-media" / "03_platform_rules" / f"{plat}.md",
                     f"# {plat} 平台規格\n\n<由 references/platforms.md 生成，並由客戶確認一次>\n\n"
                     "- 字數／長度：\n- 圖片規格：\n- Hashtag：\n- 節奏／語感：\n- 排程窗口：\n- 唔好做：\n",
                     a.force)

    written += w(cdir / "config" / "tools.md",
                 "# 工具映射\n\n> 寫類型，唔好寫品牌名 —— 工具會換，工作站唔會。\n\n"
                 "| 工作需要 | 工具類型 | 輸入 | 輸出 | 交俾邊個 |\n|---|---|---|---|---|\n"
                 "| 讀取公開來源 | Browser／Capture | 連結 | 原文 ＋ 來源記錄 | 研究 |\n"
                 "| 影片轉文字 | Transcript | 影片 | 逐段文字 | 研究 |\n"
                 "| 內容產出 | 寫作模型 | Insight Pack | Master ＋ 平台版本 | 品質 |\n"
                 "| 視覺產出 | Image／Design | 已批准文案 | 圖卡 ＋ 規格 | 品質 |\n"
                 "| 名單與跟進 | 表單／試算表 | 表單提交 | 名單記錄 | 轉化 |\n",
                 a.force)

    written += w(cdir / "config" / "schedule.md",
                 "# 排程\n\n"
                 "## 本月模式：**只排到待審**\n"
                 "第一個月唔開全自動發布。品牌信任冇得回頭，慳嗰十分鐘唔值。\n"
                 "第二個月抽三成審，穩定之後只審新題材。\n\n"
                 "## 每週節奏\n| 日 | 做咩 |\n|---|---|\n| 一 | 出選題（研究交 insight pack）|\n"
                 "| 二 | 人揀主角度 |\n| 三 | 文案交稿 → 品質檢查 |\n| 四 | 視覺 ＋ 待審 |\n"
                 "| 五 | 覆盤（數據交週報）|\n\n"
                 "## 平台窗口\n<由 references/platforms.md 按客戶時區生成>\n\n"
                 "## 規則\n- 每平台每日唔好超過 1 條（Threads 除外）\n"
                 "- 唔好四平台同日出同一內容 —— 次要平台跟主場後 1–2 日\n"
                 "- 留一格機動位俾即時性內容\n",
                 a.force)

    manifest = {
        "client": a.client,
        "brand": brand,
        "archetype": a.archetype,
        "modifiers": mods,
        "agents": agents,
        "platforms": plats,
        "created": date.today().isoformat(),
        "voice_confidence": "待評估",
        "visual_confidence": "未建立",
        "skills": [x.strip() for x in a.skills.split(",") if x.strip()],
        "publish_mode": "review-only",
    }
    written += w(cdir / "workspace.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", a.force)

    print(f"✓ Workspace: {cdir}")
    print(f"  角色 {len(agents)}：{', '.join(agents)}")
    print(f"  平台 {len(plats)}：{', '.join(plats) or '（未指定）'}")
    print(f"  Archetype：{a.archetype}" + (f" + {', '.join(mods)}" if mods else ""))
    if a.skills:
        print(f"  技能：{a.skills}")
    print(f"  寫入 {written} 個檔案" + ("（已存在嘅已跳過）" if not a.force else ""))
    print()
    print("下一步：跑步驟 2 爬取，然後 distill.py 生成 voice profile。")
    print("提醒：未有真實語料之前，唔好把 voice-profile 當成完成。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
