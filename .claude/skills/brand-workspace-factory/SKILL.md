---
name: brand-workspace-factory
description: >
  由一句話生成一個完整、即刻用得嘅 AI marketing 工作台（多客戶／agency 適用）。
  用戶只需講「我個業務係 X，用開 小紅書／IG／Threads／FB，帳號係 @yyy」，
  呢個 skill 就會爬取公開內容、抽取寫作風格、生成品牌知識庫（Brand Brain）、
  按品牌類型自動決定員工編制、寫好每個 AI 員工嘅 AGENTS.md、安裝所需 Skills、
  配置工具同排程，最後交出一個有 dashboard、有待審佇列、跑得動嘅工作台。
  Use this skill whenever someone wants to set up, bootstrap, scaffold, or spin up an AI
  agent workspace / AI 員工 / AI marketing team / content operation for a brand, business,
  or client — including when they describe a business and its social accounts and expect a
  working setup, when they say things like「幫我起個工作台」「配置 AI 員工」「onboard 呢個客」
  「build me an AI marketing team」「set up agents for this brand」, when they want to
  replicate an existing workspace for a new client, or when they are tired of manually
  writing MD files / choosing sources / picking tools and want it configured in one shot.
  Also use it when someone asks to add a client to an existing agency workspace.
---

# Brand Workspace Factory

由一句話，起一間可以運作嘅 AI 數碼公司。

## 你要造嘅嘢

呢個 skill 唔係生成一堆模板文件就算。**完成標準係：跑完之後，用戶可以即刻叫工作台交第一批稿，而啲稿係像返佢個品牌嘅。** 一個生成得靚但冇讀過真實資料嘅工作台，價值等於零 —— 因為佢寫出嚟嘅嘢同 ChatGPT 白紙開始冇分別。

所以整條流水線嘅重心係第 2、3 步（爬取 + 蒸餾）。其餘步驟都係圍住嗰兩步嘅產物嚟組裝。

## 心智模型

一個工作台 = 一間公司。每一層對應公司入面一樣真實嘢：

| 層 | 公司對應物 | 檔案 |
|---|---|---|
| 定位 | 入職手冊 / 公司憲法 | `brand/BIBLE.md` |
| 資料庫 | 檔案櫃（8 個櫃桶） | `brand/brain/*.md` |
| 大腦 | 職位說明 | `agents/<role>/AGENTS.md` |
| 技能 | 工作 SOP | `skills/<skill>/SKILL.md` |
| 工具 | 系統權限 | `config/tools.md` |
| 視覺 | 品牌手冊 ＋ 當季風格 | `style/brand-visual.md` ＋ `_trends/packs/` |
| 展示 | 辦公室白板 | `dashboard/index.html` |
| 記憶 | 會議紀錄 / 決策檔 | `brand/MEMORY.md` |

Agent 唔會因為個名叫「Content Agent」就識做嘢。佢識做嘢，係因為佢知道自己嘅崗位、可以讀邊啲資料、做事規則、同交付標準。**冇寫低嘅規則，對 Agent 嚟講等於唔存在。**

## 多客戶結構（agency 必讀）

呢個 skill 預設係 agency 用。每個客戶一個 workspace，共用根目錄嘅模板同技能庫：

```
<root>/
├── _templates/          共用骨架（唔好直接改客戶檔案嚟做模板）
├── _skills/             共用技能庫（platform skills、format skills）
├── _archetypes/         行業預設（編制、紅線、平台優先次序）
├── _trends/             ⭐ 總公司風格庫（見下）
└── clients/
    ├── acme-postpartum/ 一個客一個資料夾，內部結構完全一致
    └── beta-cafe/
```

一致嘅內部結構係重點：任何同事、任何 agent 入到任何一個客戶資料夾，都知道去邊度搵嘢。當你服務第五個客嘅時候，呢個一致性就係你嘅護城河。

如果用戶已經有 workspace 而係想加多一個客，唔好重新生成根目錄 —— 只跑第 1–9 步入面同 client 相關嘅部分。

## 總公司 Trend Library（呢套系統嘅槓桿位）

客戶自己冇時間追「而家興咩形式」。流量體裁更替好快 —— 上一排 Challenge，之後
Tier 評級，再之後 POV 封面。工作台如果只識用建立當日嘅風格，三個月後就過時。

所以體裁知識**唔放喺客戶工作台**，放喺 `_trends/`：總公司每月爬一次，整理成
style pack；客戶喺 dashboard 揀邊個 pack，視覺 agent 生圖就跟嗰個骨架。

**總公司更新一次 pack，所有引用緊嘅客戶自動跟到最新。**

完整規格、`pack.json` schema、模仿嘅界線 —— 見 `references/visual-system.md`。
用 `scripts/trend_pack.py` 建立、驗證、出索引。

> **模仿界線（唔可以含糊）**：抄**體裁**（POV 封面、Tier 排版、編號清單卡）——
> 呢啲同「三幕劇」一樣係格式慣例，冇人擁有。唔抄某個創作者嘅原圖或簽名畫風。
> `samples/` 全部要係自己生成嘅中性題材示範圖。
> 實際好處：抄體裁，你有位放品牌變數；抄原圖，你變成第 500 個一樣嘅帖。

## 流水線

跑呢九步。第 5 步同第 9 步係**人手閘門，唔可以跳**。

---

### 步驟 1 — 解析 + 補問（上限 5 條）

由用戶嗰句話抽出：

- **業務性質** → 對應一個 archetype（見 `references/archetypes.md`）
- **平台** → 每個平台有唔同規格同排程窗口（見 `references/platforms.md`）
- **帳號 handle** → 爬取入口
- **賣咩 / 收咩錢** → 決定 funnel 有冇需要
- **地區同語言** → 香港／台灣／內地嘅用詞同法規差好遠

能推斷嘅就推斷，唔好問。例如「網店賣產後服務」＝ service-booking archetype ＋ health-adjacent modifier ＋ 大機會係香港繁體 —— 呢啲唔使問。

**只問真係會改變產出嘅嘢。** 最多 5 條，一次過問晒，問完即刻做。典型嘅五條：

1. 主要目標係咩？（多啲查詢／多啲落單／建立知名度／教育市場）
2. 有冇同行係你想拎嚟做參考嘅？（俾 3–5 個 handle）
3. 有冇絕對唔可以講嘅嘢？（法規、競品、價格）
4. 邊個平台係主場，邊啲係次要？
5. 邊啲嘢一定要你親自批先出得街？

問多過五條，用戶會走。缺嘅資料寧願用假設補，再喺第 5 步俾佢改 —— 睇住一份初稿改，永遠快過答一堆抽象問題。

### 步驟 2 — 爬取（Ingestion）

爬三類嘢，用途完全唔同：

| 對象 | 抽咩 | 變成 |
|---|---|---|
| 客戶自己嘅帳號 | 句長、開場、emoji 密度、CTA 講法、高表現帖嘅結構 | `voice-profile.md` |
| 同行 5–10 個 | 選題地圖、內容缺口（邊啲題有人問冇人答） | `topic-map.md` |
| 留言區 | 真實用戶點形容自己個問題、反對理由 | `audience-language.md`、`faq.md` |
| 客戶嘅**圖** | 顏色、畫風、排版、主體處理、「從來冇出現」清單 | `style/brand-visual.md` |

最後一行好易漏。**語氣同視覺係兩套獨立嘅嘢** —— 語氣像咗但配圖唔似，一樣會俾人
一眼識穿。`visual-identity-scan` 技能負責呢部分，規格見 `references/visual-system.md`。

留言區係最值錢嗰忽。真實受眾用嘅字眼，永遠好過 agent 自己估嘅 persona。

**做法同界線見 `references/ingestion.md`** —— 入面有各平台嘅可行途徑、rate limit、同 fallback。三條硬規則：

- 只爬公開內容，尊重 robots.txt、平台條款同 rate limit。唔繞過登入牆。
- 唔儲存個人資料（真實姓名、聯絡方式）。留言只抽用詞同主題，抽完就丟原始 ID。
- 爬唔到就用 fallback（用戶手動匯出 / 貼 20–30 條內容），**唔好靜靜跳過然後生成一個估出嚟嘅 voice profile**。冇真實語料嘅 voice profile 係整條流水線最危險嘅失敗模式，因為佢睇落好完整。

每條來源保留 **標題、平台、作者、日期、連結**（Source Receipt）。後面內容改到第五版，仍然追得返證據。

### 步驟 3 — 蒸餾（Distillation）

呢步係把原始資料變成 agent 讀得郁嘅嘢。用 `scripts/distill.py` 做統計部分，判斷部分由你自己做。

產出五份檔案入 `brand/brain/`：

- `voice-profile.md` — 句長分佈、常用開場、禁用詞、emoji 密度、段落節奏、CTA 講法。**要具體到可驗證**：「平均 42 字一句，好少用感嘆號，開場七成係一條問題」，唔係「親切專業」。
- `hook-library.md` — 由高表現帖抽出嚟嘅開場結構，附原帖連結。
- `audience-language.md` — 受眾原話。直接引用，唔好改寫成 marketing 用語。
- `topic-map.md` — 選題 × 競爭密度 × 缺口。
- `platform-rules.md` — 每個平台嘅字數、節奏、hashtag、禁忌。

**驗收標準：**攞兩個唔同嘅寫手睇完 `voice-profile.md`，佢哋寫出嚟嘅嘢應該似。如果唔似，即係寫得唔夠具體，返去補。

### 步驟 4 — 生成 Brand Brain（8 個櫃桶）

用蒸餾出嚟嘅嘢填滿八個櫃桶。全部模板喺 `references/file-templates.md`。

1. 定位背景 · 2. 品牌語氣 · 3. 受眾語言 · 4. 已批准主張／證據 · 5. Hook 與成功例子 · 6. 平台規格 · 7. 決策／Review 記錄 · 8. Learning 更新

第 4 個櫃桶（已批准證據）第一版通常係空嘅 —— **咁就寫「空」，唔好填假嘢**。空櫃桶會令 agent 知道「我而家冇證據可以引」，好過俾佢一堆生成出嚟嘅假案例。

**客戶會用真實客人嘅相、身體或個人故事**（`health-adjacent`／`beauty-efficacy`／`minors`）→
第 4 個櫃桶要拆成「品牌自身證據」同「客戶個案」兩條路，並建立 `data/consent/` 同意登記。
規格喺 `references/file-templates.md` 嘅〈同意登記〉。三條唔可以省：agent 唔可以寫入同意登記、
正本唔放 workspace、要有使用索引（因為同意可以撤回，而撤回要做得到）。

**客戶做咗幾年、舊個案得紙本同意**（好常見）→ 紙本係有效同意，但要按**原文授權範圍**
分三層：範圍已涵蓋社交／廣告嘅照用；只寫「本店宣傳」或冇寫用途嘅唔可以出新平台；
搵唔返紙本嘅當唔存在。唔好一刀切批准 —— 舊同意嘅問題通常唔係「有冇」，係「範圍」。

同時生成 `brand/BIBLE.md`：一頁式憲法，包住定位、受眾、語氣三行總結、同紅線清單。紅線由 archetype ＋ modifier 決定（見 `references/archetypes.md`）。

### 步驟 5 — 🛑 人手閘門一：審 Brand Brain

**停低。唔好跑落去。**

呈俾用戶睇三樣嘢，其餘唔使佢逐份揭：

1. `BIBLE.md` 全文（短，一頁）
2. `voice-profile.md` 全文（呢份錯，之後全部嘢都錯）
3. 紅線清單

問一條問題：**「呢個似唔似你？邊度唔啱？」**

呢步係整條流水線唯一唔可以自動化嘅位。理由好簡單：下面所有嘢都係由呢兩份檔案長出嚟。呢度錯一個字，後面五十份檔案一齊錯，而你要跑完成個 campaign 先發現。

改完先繼續。

### 步驟 6 — 配置員工編制

編制唔係拍腦袋決定。用呢條公式：

**核心五人（一定有）**
| 角色 | 交付物 |
|---|---|
| 總監 Orchestrator | 派工、驗收、對齊 BIBLE |
| 研究 Research | `insight-pack.md`（3–6 個角度，人揀一個）|
| 文案 Content | `master-content.md` ＋ 各平台版本 |
| 品質 QA | Ready-to-Review 判定 |
| 數據 Analytics | 週報 ＋ 下一輪測試建議 |

**按需要加（每個 +1）**
- 有視覺平台（IG／小紅書／FB）→ **視覺 Visual**
- 有影片格式 → **影片 Video**
- 有留言私訊量 → **社群 Engage**
- 有 landing page／收 lead → **轉化 Funnel**

**上限 8 人。** 再多，總監協調成本大過收益 —— 呢個唔係技術限制，係實際觀察：超過八個角色之後，交接錯誤增長得比產能快。

**分工原則：按產出物分，唔好按話題分。**「小紅書 agent」係壞設計（佢要同時諗策略、寫文、出圖、覆留言，質量冇得獨立驗收）。「文案 agent」「視覺 agent」係好設計，因為每個只交一種嘢。

**有 compliance modifier（醫療／金融／兒童相鄰）→ QA 必須獨立成一個 agent，唔可以叫文案自己檢查自己。** 自我檢查喺合規上係無效嘅。

每個角色生成一份 `agents/<role>/AGENTS.md`，六個欄位缺一不可：Role · Goal · Inputs · Rules · 交付成果 · 人手檢查點。模板喺 `references/file-templates.md`。

寫 Rules 嗰陣要具體到可以執行。「保持專業」係廢話；「每個關鍵 Claim 要保留來源；唔可以把熱門內容直接當品牌立場；先出三個角度再由人揀」先係規則。

### 步驟 7 — 安裝技能

由 `_skills/` 挑，唔好每次重新寫。技能係一個**資料夾**，唔係一句 prompt：

```
skills/social-media/
├── SKILL.md              用途、適用場景、SOP 五步、範例、常見問題
├── 00_brief/             brief-template.md
├── 01_brand/             → 指去 brand/brain/（唔好複製，用引用）
├── 02_assets/            已批准內容、素材
├── 03_platform_rules/    instagram.md / threads.md / xhs.md / facebook.md
└── 04_qa/                qa-checklist.md · review-rubric.md
```

平台規格檔由步驟 3 嘅 `platform-rules.md` 拆出嚟。**唔好複製 brand 資料入技能資料夾** —— 用引用。品牌資料只可以有一個真相來源，否則改完一邊，另一邊繼續用舊嘢。

按平台同格式揀技能。**完整技能庫同 archetype → 技能對照表喺 `references/skill-catalogue.md`。**

近乎每個有視覺平台嘅客都要裝 `image-gen`。有多過一個地區或語言 → `language-module`
（呢個唔係翻譯：港繁／台繁／簡中／英文喺例子、稱呼、平台慣例上都唔同，直譯會好突兀）。

**唔好一次過裝晒。**裝咗但冇用嘅技能，會令 agent 每次開工讀多幾份唔相關嘅檔案，
判斷反而變差。由必裝開始，跑通咗先加。

### 步驟 8 — 工具映射 ＋ 排程

寫 `config/tools.md`：每一步用邊類工具、入咩、出咩、交俾邊個。重點係**類型**，唔係品牌名 —— 工具會換，工作站唔會。

寫 `config/schedule.md`：

- 各平台嘅發布窗口（見 `references/platforms.md`，按地區調整）
- 每週節奏：邊日出選題、邊日交稿、邊日覆盤
- 待審佇列點運作、幾時提你

**第一個月唔好開全自動發布。** 排程只排到「待審」，人㩒掣先出街。理由：品牌信任冇得回頭，而你慳嗰十分鐘唔值。第二個月抽三成審，穩定之後只審新題材。

### 步驟 8.5 — 配置視覺

兩件事：

1. **`style/brand-visual.md`** — 由步驟 2 爬到嘅圖蒸餾。要具體到可驗證，同 voice
   profile 一樣。特別唔可以漏「**從來冇出現**」嗰欄：生圖模型好鍾意自己加金色點綴、
   渐變、bokeh；冇明確寫低「呢個品牌從來唔用」，佢就會加。

2. **`style/selected-packs.json`** — 由 `_trends/` 揀 pack，一個 slot 一個
   （cover / carousel / reel_thumb）。用 `trend_pack.py select`。

生圖預設用圖像模型，**唔用 code 排版** —— code 排出嚟每個元素都喺數學上正確嘅位置，
人眼一睇就知係機器砌嘅。但圖像模型嘅弱點係精準文字（價錢、步驟編號、免責聲明會出錯字），
所以每個 pack 自己聲明 `render_mode`：

- `image-only` — 圖上文字 ≤ 約 18 字且係口號式。最自然。**生完要逐字核對。**
- `image-plus-text-layer` — 模型只生底圖同氛圍並預留安全區，文字用品牌字體疊上去。

有 `health-adjacent` 或 `beauty-efficacy` 嘅客，**任何帶免責聲明嘅圖一律走
text-layer** —— 法規字眼唔可以有錯字，呢個唔係美觀問題。

### 步驟 9 — 🛑 人手閘門二：自我驗收 ＋ 冒煙測試

用 `references/verification.md` 逐項 check。唔好靠感覺，逐條對。

然後做一次**冒煙測試**：叫工作台由頭跑一條真實內容出嚟（選題 → 文案 → **配圖** → QA → 待審）。

配圖嗰步唔好跳 —— 視覺係最容易生成得「睇落有」但實際唔似品牌嘅一層。

睇兩樣嘢：
1. 跑唔跑得完（有冇 agent 搵唔到檔案、有冇死循環）
2. 出嚟嗰篇嘢，**像唔像返個品牌**

如果唔似 —— 唔好改嗰篇稿。返去改 `voice-profile.md`。呢個係最重要嘅習慣，見下面。

最後生成 `dashboard/index.html`（用 `assets/dashboard-template.html`）：八站狀態、待審佇列、本週排程、最近決策。

---

## 改嘢嘅規矩（交俾用戶嘅最重要一課）

工作台交出去之後，用戶一定會見到唔滿意嘅產出。**答案永遠唔係改嗰份產出。** 教佢查呢張表：

| 見到嘅問題 | 唔好咁做 | 應該補返去邊 |
|---|---|---|
| 搵錯資料／漏咗背景 | 下次再口頭補充 | 資料庫 或 輸入清單 |
| 語氣唔似／節奏唔啱 | 只講「寫自然啲」 | `voice-profile.md`、平台規格、好例子 |
| Claim 冇證據／太誇 | 只刪一句 | Source Receipt、Rules、QA checklist |
| 流程亂／交付唔齊 | 只叫佢重做 | Skill SOP 同交付格式 |
| 同一種錯翻嚟覆去 | 每次自己修 | `MEMORY.md` ＋ 新增檢查項 |

工作台唔會自己變聰明。佢變好，係因為每次 review 之後有人把經驗回寫入去。冇呢個閉環，半年後嘅產出同第一日一模一樣 —— 呢個係大部分工作台死亡嘅方式。

## 交付訊息

跑完之後，向用戶交代呢幾樣（簡短，唔使長篇）：

1. 生成咗幾多個 agent、點解係呢個數
2. 爬咗幾多條內容、voice profile 嘅信心度（高／中／低，同原因）
3. 邊啲櫃桶係空嘅、要佢補咩
4. 冒煙測試嘅產出（貼出嚟俾佢睇）
5. 下一步：跑第一條真 campaign

**唔好聲稱做咗未做嘅嘢。** 爬唔到嘅平台要明講；用假設填嘅位要標明。一個誠實嘅「呢部分我用咗行業預設，你要 review」，遠遠好過一個睇落完整但入面係估嘅工作台。

## 參考檔案

- `references/archetypes.md` — 業務類型 → 編制、紅線、平台優先次序、技能組合
- `references/platforms.md` — 各平台規格、爬取途徑、排程窗口
- `references/ingestion.md` — 爬取做法、界線、fallback、蒸餾方法
- `references/file-templates.md` — BIBLE / AGENTS / SKILL / MEMORY / CHECKLIST 模板
- `references/visual-system.md` — ⭐ 生圖政策、style pack、總公司 trend library、模仿界線
- `references/skill-catalogue.md` — 技能庫全表 ＋ archetype → 技能對照
- `references/verification.md` — 交付前驗收清單

## 腳本

- `scripts/scaffold.py` — 生成完整 client workspace 目錄樹。**先跑呢個**，唔好逐個檔案手動創建。
  `python scripts/scaffold.py --root <root> --client <slug> --agents research,content,visual,qa,analytics --platforms xhs,ig,threads,fb`
- `scripts/distill.py` — 由爬回嚟嘅 JSON 算出句長分佈、開場模式、emoji 密度、CTA 頻率，輸出 `voice-profile.md` 草稿。
  `python scripts/distill.py --input data/scraped/ --output brand/brain/voice-profile.md`
- `scripts/trend_pack.py` — 總公司 trend library：開 pack、驗證（缺欄位／過期／樣本缺失）、
  出索引、幫客戶揀 pack。
  `python scripts/trend_pack.py check --root <root>` · `... index --root <root>`
