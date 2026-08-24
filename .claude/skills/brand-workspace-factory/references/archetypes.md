# 業務原型 Archetypes

用途：由一句業務描述，決定編制、紅線、平台優先次序同技能組合。

**設計方式：archetype（基礎型）× modifier（疊加層）。** 八個 archetype 覆蓋大部分生意；modifier 處理合規同特殊風險。呢個組合方式比列二十個 archetype 好用，因為現實中一間公司經常同時係「服務預約」同「醫療相鄰」。

## 目錄

- [點揀 archetype](#點揀-archetype)
- [八個 archetype](#八個-archetype)
- [Modifier（可疊加）](#modifier可疊加)
- [編制公式](#編制公式)

---

## 點揀 archetype

問一條問題：**客人俾錢之後，即刻攞到咩？**

| 即刻攞到 | Archetype |
|---|---|
| 一件實物 | `ecommerce-physical` |
| 一個預約時段 | `service-booking` |
| 一堂課／一份知識 | `education` |
| 要親身去門店 | `local-storefront` |
| 一份合約／一個提案 | `b2b-services` |
| 追蹤咗一個人 | `creator-ip` |
| 一個帳號登入 | `saas` |
| 一次捐款／參與 | `nonprofit-community` |
| 一份創意成品（設計／內容／網站） | `agency-creative` |
| 一隊人幫你頂住日常運作 | `bpo-support` |

含糊嘅時候，揀**收入佔比最大**嗰個，另一個當次要。唔好一次過套兩個 archetype —— 會生成一隊唔知自己做緊咩嘅團隊。

---

## 八個 archetype

### `ecommerce-physical` — 電商實體貨

- **核心張力**：信任（睇唔到實物）＋ 即時性（幾時到貨）
- **內容重心**：使用場景 > 產品規格。開箱、對比、真實使用。
- **平台優先**：小紅書 / IG > FB > Threads
- **必備技能**：`product-content`、`ugc-repurpose`、`social-media`
- **加開角色**：視覺（必），Funnel（如有自家網店）
- **典型紅線**：唔誇大功效、唔保證到貨時間、價格資訊要同店面一致
- **成效指標**：加購率、內容 → 商品頁點擊

### `service-booking` — 服務預約

- **核心張力**：專業信任 ＋ 「適唔適合我」
- **內容重心**：教育型內容為主，銷售為輔。先解決一個小問題，建立資格感。
- **平台優先**：小紅書 / IG > FB（本地社群）> Threads
- **必備技能**：`social-media`、`faq-content`、`booking-funnel`
- **加開角色**：Funnel（必，要收預約）、Engage（私訊查詢通常好多）
- **典型紅線**：唔承諾結果、唔比較同行、個案要有書面同意
- **成效指標**：查詢量、查詢 → 預約轉換率
- **注意**：呢個 archetype 最常疊加 `health-adjacent` 或 `beauty-efficacy` modifier

### `education` — 課程／知識付費

- **核心張力**：值唔值呢個價 ＋ 我學唔學得識
- **內容重心**：免費俾出真嘢。留一手嘅內容喺呢個類別死得最快。
- **平台優先**：YouTube / 小紅書 > IG > Threads > FB
- **必備技能**：`long-form-content`、`social-media`、`webinar-funnel`
- **加開角色**：影片（幾乎必），Funnel
- **典型紅線**：唔保證收入／成果、學員案例要授權、唔用稀缺性造假（假倒數、假名額）
- **成效指標**：報名率、完課率、轉介率

### `local-storefront` — 本地門店（餐飲／美容／零售）

- **核心張力**：值唔值得專登去一趟
- **內容重心**：氛圍、即時性、在地感。內容保鮮期短，數量重過深度。
- **平台優先**：IG > 小紅書 > FB（本地群組好重要）> Google Business
- **必備技能**：`social-media`、`local-seo`、`ugc-repurpose`
- **加開角色**：視覺（必），Engage
- **典型紅線**：食品安全同過敏標示、營業時間要準、唔用非本店實拍圖
- **成效指標**：到店查詢、地圖點擊、限時優惠核銷

### `b2b-services` — B2B ／ 專業服務

- **核心張力**：可信度 ＋ 風險（揀錯代價好大）
- **內容重心**：觀點同案例。長文、拆解、行業判斷。發布頻率低但密度高。
- **平台優先**：LinkedIn > 自家 Blog / SEO > Threads > FB
- **必備技能**：`long-form-content`、`case-study`、`lead-nurture`
- **加開角色**：Funnel（必），研究角色權重要加大
- **典型紅線**：客戶名要授權先可以用、數據要標明出處同時間、唔講具體財務承諾
- **成效指標**：合資格查詢（MQL）、內容 → 會議

### `creator-ip` — 個人 IP／創作者

- **核心張力**：一致性同真實感
- **內容重心**：觀點 > 資訊。同一個人講嘢，語氣就係產品。
- **平台優先**：主場單一平台深耕 > 其餘做分發
- **必備技能**：`social-media`、`repurpose`、`community`
- **加開角色**：Engage（必），影片（視乎主場）
- **典型紅線**：贊助內容要標示、唔講未經證實嘅個人成果
- **成效指標**：留存、互動深度（留言 > 讚）、轉介
- **注意**：呢個 archetype 嘅 `voice-profile.md` 要求最高。冇真實語料就唔好開工。

### `saas` — 軟件／應用

- **核心張力**：解唔解決到我個問題 ＋ 遷移成本
- **內容重心**：用例、對比、教學。SEO 同文件檔佔比高。
- **平台優先**：SEO / Blog > LinkedIn > X > 產品內
- **必備技能**：`long-form-content`、`seo-geo`、`onboarding-content`
- **加開角色**：Funnel（必）
- **典型紅線**：功能唔可以講未 ship 嘅、效能數字要有測試條件、唔貶低競品
- **成效指標**：試用註冊、啟用率

### `nonprofit-community` — 非牟利／社群

- **核心張力**：資源用得其所 ＋ 我參與有冇用
- **內容重心**：故事同透明度。定期公開成果。
- **平台優先**：FB（社群動員最強）> IG > 電郵
- **必備技能**：`storytelling`、`social-media`、`donor-comms`
- **加開角色**：Engage
- **典型紅線**：受助人身分保護（極重要）、財務數字要準、唔用悲情剝削式圖像
- **成效指標**：參與人數、定期捐款留存


### `agency-creative` — 創意代理（marketing／design／social media 營運／網頁開發）

- **核心張力**：睇唔到成品之前，點知你做唔做得掂？＋ 我畀嘅錢買緊咩
- **內容重心**：**作品同過程**。呢個 archetype 最特別嘅地方係——過程比成品更有說服力。
  「我哋點解揀呢個顏色」比「呢個 banner 好靚」有效十倍，因為前者證明你有方法，後者只證明你有品味。
- **平台優先**：IG（作品集）＞ LinkedIn（決策者）＞ Threads（觀點）＞ 自家 Blog／SEO（案例）
- **必備技能**：`case-study`、`visual-identity-scan`、`social-media`、`long-form-content`
- **加開角色**：視覺（必）、Funnel（必，收 brief）
- **典型紅線**：
  - 客戶作品要有授權先可以出（NDA 好常見，呢條唔可以靠記憶）
  - 唔可以展示未上線嘅客戶專案
  - 成效數字要標明時段同條件
- **成效指標**：合資格查詢、提案邀請
- **注意**：呢個 archetype 嘅客戶自己就係做內容嘅 —— 佢哋對「AI 味」極度敏感。
  `02-voice-profile.md` 唔夠具體嘅話，佢哋一眼睇得出，而且會即刻唔信成個工作台。
  呢類客一定要攞到 30 條以上真實語料先開工。

### `bpo-support` — 客服中心／外包營運

- **核心張力**：交畀你之後，我會唔會失去控制？
- **內容重心**：可靠性、流程透明、數據。故事性低，證據性高。
- **平台優先**：LinkedIn ＞ 自家網站／SEO ＞ FB（招聘同僱主品牌）
- **必備技能**：`case-study`、`long-form-content`、`lead-nurture`、`faq-content`
- **加開角色**：Funnel（必）
- **典型紅線**：
  - 唔可以披露客戶嘅營運數據或投訴內容
  - 服務水平（SLA）數字要有實際依據
  - 招聘內容唔可以誇大待遇
- **成效指標**：合資格查詢、提案邀請、招聘應徵量
- **注意**：呢類客有**兩個受眾**（買服務嘅企業 ＋ 請人）。
  唔好用一套語氣做兩件事 —— 喺 `06-platform-rules.md` 分開寫，
  或者索性當兩條內容線處理。

---

## Modifier（可疊加）

Modifier 唔改編制核心，但**加紅線、加檢查層、有時強制拆開角色**。

### `health-adjacent` — 醫療健康相鄰

適用：產後護理、營養、心理、復康、保健品、醫美

- **強制**：QA 必須獨立成一個 agent，唔可以同文案同一個。自我檢查喺合規上無效。
- **紅線**：
  - 唔用「治療、根治、醫學證實、療效」呢類字眼
  - 任何身體症狀嘅內容一律加「持續／惡化請諮詢醫護人員」
  - 唔提供劑量、療程建議
  - 個案分享要有書面同意，並隱去可識別資料
  - 唔宣稱取代專業醫療意見
- **加開檢查項**：每篇稿要過一次禁用詞掃描 ＋ 免責聲明存在性檢查

### `finance-adjacent` — 金融理財相鄰

適用：保險、投資、借貸、會計、加密

- **強制**：QA 獨立；所有數字要有出處同日期
- **紅線**：唔保證回報、唔講「穩賺／低風險高回報」、唔提供個人化投資建議、要標明受規管身分（如適用）

### `minors` — 面向兒童／青少年

適用：教育、玩具、兒童產品

- **紅線**：唔直接向兒童落 CTA、唔用兒童真實影像（除非有監護人同意）、廣告標示要更明顯
- **加開檢查項**：內容適齡性檢查

### `beauty-efficacy` — 美妝功效宣稱

- **紅線**：功效宣稱要有測試依據、前後對比圖要標明個人差異、唔宣稱即時／永久效果
- **加開檢查項**：宣稱 ↔ 證據配對檢查

### `regulated-hk` — 香港特定

- 廣告要符合本地法例（例如商品說明條例）
- 醫療儀器、藥物、保健聲稱有額外限制
- **注意**：呢個 modifier 只係提醒建立檢查點，唔係法律意見。工作台應該喺 BIBLE 寫明「重大宣稱要經人手法務確認」。

---

## 常見客戶類型速查

| 客戶講嘅嘢 | Archetype | Modifier |
|---|---|---|
| Marketing 公司 | `agency-creative` | — |
| Design studio | `agency-creative` | — |
| Social media 營運商 | `agency-creative` | — |
| 網頁開發公司 | `agency-creative` | — |
| 小朋友產品 | `ecommerce-physical` | `minors` |
| 電商品牌 | `ecommerce-physical` | 視產品而定 |
| 客服中心／BPO | `bpo-support` | — |
| 產後護理／紮肚 | `service-booking` | `health-adjacent` ＋ `beauty-efficacy` |
| 美容院 | `local-storefront` | `beauty-efficacy` |
| 補習社 | `education` | `minors` |
| 保險經紀 | `b2b-services` | `finance-adjacent` |

**紮肚特別注意**：涉及體型改變宣稱，`beauty-efficacy` 一定要疊。
唔好因為佢係「產後服務」就只疊 `health-adjacent` —— 收腹、瘦身、尺寸數字
係另一套規管邏輯，而且係客戶最想講、最容易講過龍嗰部分。

## 編制公式

```
核心 5 人（一定有）
  總監 Orchestrator
  研究 Research
  文案 Content
  品質 QA
  數據 Analytics

+ 視覺 Visual     ← 有 IG / 小紅書 / FB 任何一個
+ 影片 Video      ← 有影片格式需求
+ 社群 Engage     ← 有留言／私訊量，或 archetype 標明必備
+ 轉化 Funnel     ← 有 landing page / 收 lead / 收預約

上限 8 人（超過就合併次要角色）
```

### 常見結果

| 情境 | 人數 | 編制 |
|---|---|---|
| 單一平台、純圖文、無 funnel | 5 | 核心五人 |
| 小紅書＋IG＋Threads＋FB，服務預約 | 8 | 核心五 ＋ 視覺 ＋ Engage ＋ Funnel |
| 課程，有影片 | 8 | 核心五 ＋ 視覺 ＋ 影片 ＋ Funnel |
| B2B，長文為主 | 6 | 核心五 ＋ Funnel |
| 個人 IP，單一主場 | 7 | 核心五 ＋ 視覺 ＋ Engage |

### 撞到上限點算

超過 8 人嘅時候，按呢個次序合併：

1. 視覺 ＋ 影片 → 「創意 Creative」
2. 研究 ＋ 數據 → 「洞察 Insight」（因為兩者都係讀數據做判斷）
3. **永遠唔好合併 QA 落其他角色**，尤其有 compliance modifier 嘅時候

### 唔好咁做

- **唔好按平台開角色**（「小紅書 agent」「IG agent」）。同一篇內容跨平台改寫係一個人做嘅事，拆開只會令品牌語氣分裂。
- **唔好開「策略 agent」然後乜都掉俾佢**。策略係總監同研究嘅工作，開多一個只會令責任模糊。
- **唔好因為客戶大就加人**。編制由產出物種類決定，唔係由預算決定。
