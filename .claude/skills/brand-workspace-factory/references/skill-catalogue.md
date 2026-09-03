# 技能庫 Skill Catalogue

`_skills/` 入面有咩、每個裝咗咩、邊個 archetype 要用邊啲。

**技能係一個資料夾，唔係一句 prompt。**每個技能嘅標準結構：

```
_skills/<name>/
├── SKILL.md              用途、適用場景、SOP 五步、範例、常見問題
├── 00_brief/             brief-template.md
├── 01_brand/             → 引用 clients/<slug>/brand/brain/（唔好複製）
├── 02_assets/            範例、素材、參考
├── 03_rules/             平台或格式規則
└── 04_qa/                qa-checklist.md
```

安裝到客戶工作台嗰陣係**引用**，唔係複製。品牌資料只可以有一個真相來源 —— 複製咗之後，改完一邊另一邊繼續用舊嘢，而且冇人會發現。

---

## 目錄

- [核心（幾乎每個客都要）](#核心幾乎每個客都要)
- [內容製作](#內容製作)
- [視覺](#視覺)
- [影片](#影片)
- [轉化](#轉化)
- [營運](#營運)
- [Archetype → 技能對照](#archetype--技能對照)

---

## 核心（幾乎每個客都要）

### `social-media`
一個 Insight → 多平台貼文。整個系統嘅主力技能。

- `03_rules/` 每個平台一個檔（`instagram.md`、`xhs.md`、`threads.md`、`facebook.md`）
- SOP：讀 Brief → 撮要資料 → 睇平台規格 → 寫 Master → 分平台改寫 → QA
- **關鍵**：一定要先寫 Master Content 再分平台。跳過呢層，四個平台會變成同一段字改幾隻字。

### `faq-content`
把重複問題變成內容。輸入係 `03-audience-language.md` 同 Engage 收集嘅問題。

- 一條問題一篇內容，唔好夾埋十條做「懶人包」（搜尋意圖唔同）
- 有 compliance modifier 嘅客，FAQ 係最高危區 —— 客人問嘅嘢往往正正就係唔可以答嘅嘢

### `visual-identity-scan` ⭐
爬取客戶現有內容嘅**圖像風格**：顏色、畫風、排版、主體處理。

- 產出 `style/brand-visual.md`（規格見 `visual-system.md`）
- 同 voice profile 一樣：要數字，要「從來冇出現」清單
- **`agency-creative` 客戶必用** —— 佢哋自己就係做設計，視覺唔似會即刻被識穿

---

## 內容製作

### `long-form-content`
Blog、SEO／GEO 文章、深度拆解。

- `03_rules/seo-geo.md`：搜尋意圖分類、H2/H3 結構、可被 AI 引用嘅段落寫法
- 一節可以獨立回答一條問題 —— 呢個係 GEO 嘅核心，唔係加關鍵字

### `case-study`
案例研究。`agency-creative`、`b2b-services`、`bpo-support` 嘅主力。

- 固定結構：處境 → 限制 → 我哋點做（**呢節最重要**）→ 結果 → 可轉移嘅原則
- `04_qa/` 必查：客戶授權、數字時段條件、有冇披露 NDA 內容
- **常見錯誤**：只寫「結果好好」。買家買緊嘅係你嘅**方法**，唔係你上次好彩

### `ad-copy`
廣告文案。同 organic 內容係兩回事 —— 有明確轉化目標同平台審核規則。

- `03_rules/`：Meta 廣告政策要點、字數限制、素材比例
- 每組要出 3–5 個變體，**只變一個變數**（hook／CTA／角度），否則測完唔知邊樣有效
- 有 `health-adjacent`／`beauty-efficacy`／`finance-adjacent` → 廣告審核比 organic 嚴好多，禁用詞清單要另外一份

### `edm`
電郵。

- `03_rules/`：主旨行長度、preheader、單一 CTA 原則、退訂合規
- 分**廣播**（一次過）同**旅程**（按階段觸發）兩類，SOP 唔同
- 旅程郵件要接 CRM 階段 —— 冇 CRM 就唔好做旅程，做咗只會亂寄

### `language-module` ⭐
多語言／地區化。唔係翻譯。

- 支援：繁中（港）、繁中（台）、簡中、英文
- **核心觀念**：同一個意思，喺唔同市場要用唔同嘅**例子、稱呼、平台慣例**，唔係換字
  - 港繁 ↔ 台繁：唔止用字（軟體/軟件），連句子節奏同語氣距離都唔同
  - 繁 → 簡：小紅書有自己嘅內容慣例，直譯港式廣東話會好突兀
  - 中 → 英：長度會變，排版要重排，Carousel 卡數可能要改
- `03_rules/<locale>.md`：每個地區一份，列用字對照、禁忌、平台差異
- **一定要有** `04_qa/locale-check.md`：檢查有冇混用（同一篇入面港式同台式並存係最常見錯誤）
- 有 compliance modifier → **每個地區嘅紅線要分開寫**，法規唔一樣

---

## 視覺

### `image-gen` ⭐
生圖。核心技能，詳細規格見 `references/visual-system.md`。

- `03_rules/render-modes.md`：`image-only` vs `image-plus-text-layer` 嘅判斷
- `02_assets/` → 引用 `_trends/packs/`（總公司風格包）
- `04_qa/image-check.md`：逐字核對圖上文字、色彩合規、排除項檢查
- **唔好由零寫 prompt** —— 一定要用 pack 嘅配方骨架，否則風格每次唔同

### `carousel`
多卡滑動圖嘅**結構**（唔係生圖本身）。

- 卡序規則：第一卡 hook、每卡一個重點、最後一卡 CTA
- 先定卡序同文字，先至生圖 —— 未改好內容前唔好做靚圖
- 資訊密度高 → 走 `image-plus-text-layer`

### `trend-radar` ⭐
**總公司專用**，唔安裝落客戶工作台。

- 定期爬各平台高互動內容，分類**呈現體裁**（唔係主題）
- 出現頻率上升 → 開新 style pack；下跌 → 標 `retire_after`
- 用 `scripts/trend_pack.py` 建立同驗證
- **界線**：模仿體裁，唔模仿某個創作者嘅原圖或簽名畫風。sample 圖全部自己生成。

---

## 影片

### `video-edit`
剪片。

- 把內容拆成五層分開處理：**聲音、畫面、字幕、封面、CTA**
- `03_rules/`：各平台比例同長度（Reels 9:16、YouTube Shorts、小紅書影片）
- 局部重跑：某一段唔啱就只重做嗰段，唔好成條片重來
- 封面走 `image-gen`，用 `format: reel-thumb` 嘅 pack

### `video-repurpose`
一條片 → 多種內容。

- Transcript → 重點段落 → Carousel / Threads 串 / Blog
- **Repurpose 唔係搬運**：同一觀點要重新組織成另一種閱讀體驗，唔係把字幕貼出嚟
- 長片係最高效嘅內容來源 —— 一條 20 分鐘嘅片可以出一星期內容

---

## 轉化

### `booking-funnel`
預約型（`service-booking`）。查詢 → 預約 → 出席。

### `lead-nurture`
B2B 長週期（`b2b-services`、`bpo-support`、`agency-creative`）。

### `product-content`
電商（`ecommerce-physical`）。產品頁、規格、UGC 整合。

### `ugc-repurpose`
用戶內容再利用。**授權係第一步**，唔係最後一步。

---

## 營運

### `community` / Engage
留言私訊分流：FAQ／反對理由／內容缺口／潛在查詢四類。

- 需要判斷或高價值嘅對話入 Review Queue，唔好自己答
- 收集到嘅問題送返 `03-audience-language.md` 同下一輪選題

### `weekly-review`
週度覆盤。四個決定：**保留／停止／再測／更新 Skill**。

- 冇「更新 Skill」呢個決定嘅覆盤係假覆盤 —— 結果冇寫回系統，下次一樣

---

## Archetype → 技能對照

| Archetype | 必裝 | 通常加 |
|---|---|---|
| `ecommerce-physical` | social-media, product-content, image-gen, carousel | ugc-repurpose, ad-copy, edm |
| `service-booking` | social-media, faq-content, booking-funnel, image-gen | carousel, ad-copy, video-edit |
| `education` | long-form-content, social-media, video-edit, video-repurpose | edm, ad-copy |
| `local-storefront` | social-media, image-gen | ugc-repurpose, video-edit |
| `b2b-services` | long-form-content, case-study, lead-nurture | edm |
| `creator-ip` | social-media, video-repurpose, image-gen, community | carousel |
| `saas` | long-form-content, edm | ad-copy, case-study |
| `nonprofit-community` | social-media, community, edm | video-edit |
| `agency-creative` | case-study, visual-identity-scan, social-media, image-gen, carousel | long-form-content, video-edit |
| `bpo-support` | case-study, long-form-content, lead-nurture, faq-content | edm |

**跨 archetype 加裝**：
- 客戶做多過一個地區或語言 → `language-module`
- 客戶有落廣告 → `ad-copy`
- 客戶有影片內容 → `video-edit` ＋ `video-repurpose`
- **任何有視覺平台嘅客** → `image-gen`（呢個近乎必裝）

**唔好一次過裝晒。**裝咗但冇用嘅技能會令 agent 每次開工都讀多幾份唔相關嘅檔案，判斷反而變差。由必裝開始，跑通咗先加。
