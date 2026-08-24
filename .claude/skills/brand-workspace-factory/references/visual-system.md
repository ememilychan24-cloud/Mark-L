# 視覺系統 Visual System

點樣令生成出嚟嘅圖，**似返個品牌**，同時**跟得上而家嘅流量形式**。

呢兩件事係分開嘅，好多人搵埋一齊做結果兩樣都唔到位：

- **似返個品牌** = 顏色、畫風、排版、主體處理 → 由 `visual-identity-scan` 由客戶現有內容爬出嚟
- **跟得上流量** = 而家興咩體裁（POV 封面、Tier 評級、Challenge、對比圖…）→ 由**總公司 trend library** 定期更新

生圖嘅時候，兩者合成：**體裁骨架（總公司）＋ 品牌變數（客戶）＋ 內容（文案 agent 已寫好）**。

## 目錄

- [點解唔用 code 砌圖](#點解唔用-code-砌圖)
- [兩種 render mode](#兩種-render-mode)
- [總公司 Trend Library](#總公司-trend-library)
- [模仿嘅界線](#模仿嘅界線)
- [客戶端：品牌視覺檔](#客戶端品牌視覺檔)
- [生圖流程](#生圖流程)
- [Prompt 配方寫法](#prompt-配方寫法)

---

## 點解唔用 code 砌圖

用 HTML／Canvas 排版然後截圖，出嚟嘅嘢會**生硬**：每個元素都喺數學上正確嘅位置，行距永遠一致，主體永遠置中，陰影永遠同一個角度。人眼一睇就知係機器排嘅 —— 而社交平台嘅受眾對呢種「模板感」極度敏感，因為佢哋每日碌幾百張圖。

生成式圖像模型嘅優勢正正喺於**唔完美**：構圖有呼吸、光影有偶然、質感有變化。呢啲係吸引力嘅來源。

所以預設用圖像模型生成，唔用 code 排版。

**但係**——圖像模型嘅弱點係**精準文字**。一長串價錢、步驟編號、免責聲明、電話號碼，生出嚟會有錯字或者變形。呢個唔係 prompt 寫得好啲就解決到嘅結構性限制。

所以我哋唔係二選一，係按內容決定。

---

## 兩種 render mode

每個 style pack 自己聲明用邊種。呢個決定由**圖上要承載幾多精準文字**決定，唔係由靚唔靚決定。

### `image-only` — 純生圖

圖上文字 ≤ 約 18 個字，而且係口號式（唔怕輕微變體）。

適用：POV 封面、情緒圖、氛圍圖、產品情境圖、Reel 封面、單句金句卡。

優點：最自然，冇拼貼感。
風險：文字可能出錯 → QA 一定要**逐張核對圖上文字**，唔可以只睇 prompt。

### `image-plus-text-layer` — 生圖底 ＋ 文字層

圖像模型只負責**底圖同氛圍**，並喺構圖上預留安全區；文字用品牌字體疊上去。

適用：資訊型 Carousel、步驟卡、價目、對比表、任何有法規字眼（免責聲明）嘅卡。

優點：文字 100% 準確、字體 100% 一致、改文唔使重新生圖。
關鍵：**安全區要喺 prompt 入面明確要求**（例如「上方三分一留白，構圖重心偏下」），唔係生完先諗點擺字。

### 點揀

```
圖上要放嘅文字係咪包含以下任何一樣？
  價錢 / 日期 / 電話 / 網址 / 步驟編號 / 免責聲明 / 超過 18 字
    ├─ 有  → image-plus-text-layer
    └─ 冇  → image-only
```

有 `health-adjacent` 或 `beauty-efficacy` modifier 嘅客戶，**任何帶免責聲明嘅圖一律走 text-layer** —— 法規字眼唔可以有錯字，呢個唔係美觀問題。

---

## 總公司 Trend Library

呢個係整套系統嘅槓桿位。

**問題**：客戶自己冇時間追「而家興咩」。而流量形式嘅更替好快 —— 上一排係 Challenge，之後係 Tier 評級，再之後係 POV 封面。客戶嘅工作台如果只會用建立當日嘅風格，三個月後就過時。

**做法**：總公司（你）定期爬，把觀察整理成 **style pack**，放喺共用目錄。客戶工作台生圖嗰陣，旁邊就有你預備好嘅 sample 可以揀，揀完㩒掣，佢自己嘅文案就跟返嗰個風格出圖。

### 目錄結構

```
<root>/_trends/
├── INDEX.md                       # 而家生效嘅 pack，按平台同時段
├── radar/
│   └── 2026-08/observations.json  # 每次爬取嘅原始觀察（帶來源）
└── packs/
    └── pov-cover-2026q3/
        ├── pack.json              # 機讀規格
        ├── PACK.md               # 人讀：幾時興、點解 work、幾時唔啱用
        ├── prompt-recipe.md      # 生圖配方（骨架 ＋ 變數槽）
        └── samples/              # 我哋自己生成嘅樣板圖
```

### `pack.json` 規格

```json
{
  "id": "pov-cover-2026q3",
  "label": "POV 第一人稱封面",
  "format": "cover",
  "genre": "pov",
  "render_mode": "image-only",
  "aspect": "3:4",
  "platforms": ["xhs", "ig"],
  "hot_window": { "from": "2026-06", "to": "2026-09" },
  "text_capacity": { "max_chars": 16, "safe_zone": "上方 25% 留白" },
  "brand_slots": ["palette", "subject", "mood", "typeface"],
  "evidence": [
    { "platform": "xhs", "observed": "呢個體裁喺 8 月 母嬰類 出現頻率明顯上升", "url": "..." }
  ],
  "avoid": ["唔適合資訊密度高嘅內容", "唔適合需要放價錢嘅推廣"],
  "retire_after": "2026-11"
}
```

`retire_after` 好重要。**冇過期日嘅 trend library 會變成垃圾崗** —— 三年之後入面有六十個 pack，冇人知邊個仲有效。過咗期嘅 pack 移去 `packs/_archived/`，唔好刪（歷史觀察有參考價值），但唔再喺 INDEX 出現。

### 更新節奏

建議每月一次，每次 30–60 分鐘：

1. 爬三個平台（小紅書、IG、Threads）各一個垂直領域嘅高互動內容
2. 分類體裁 —— 唔係睇個別內容講咩，係睇**呈現形式**
3. 出現頻率明顯上升嘅體裁 → 開新 pack
4. 頻率下跌嘅 → 標 `retire_after`
5. 每個新 pack 生 2–3 張 sample（用自己嘅中性題材，唔用客戶資料）

用 `scripts/trend_pack.py` 建立同驗證 pack 結構。

### 客戶端點用

客戶工作台唔複製 trend library —— **引用**。`clients/<slug>/style/selected-packs.json`：

```json
{
  "cover": "pov-cover-2026q3",
  "carousel": "numbered-list-2026q2",
  "reel_thumb": "tier-rank-2026q3",
  "updated": "2026-08-24",
  "note": "客戶喺 dashboard 揀嘅"
}
```

視覺 agent 開工時讀呢個檔案，去 `_trends/packs/<id>/prompt-recipe.md` 攞骨架。

**當你更新總公司嘅 pack，所有引用緊嗰個 pack 嘅客戶自動跟到最新** —— 呢個就係「總公司養一次，全部客受惠」嘅機制。

Dashboard 應該顯示：目前選用嘅 pack、佢嘅 sample 圖、`hot_window` 剩返幾耐、有冇新 pack 可以換。

---

## 模仿嘅界線

呢節唔可以跳過。

**可以模仿：體裁（genre／format）。**
「第一人稱 POV 封面」「Tier 評級排版」「前後對比雙格」「編號清單卡」—— 呢啲係**格式慣例**，同「三幕劇結構」或者「開箱影片」一樣，冇人擁有。

**唔可以模仿：某個創作者嘅獨特作品或畫風簽名。**
唔好把某條爆紅帖嘅原圖放入 `samples/`，唔好喺 prompt 入面寫「in the style of @某某」，唔好複製某個插畫師嘅辨識度極高嘅畫法。

**所以 `samples/` 入面嘅圖，全部要係我哋自己生成嘅。**用中性題材示範個體裁，唔用任何真實客戶或別人嘅內容。呢啲 sample 嘅作用係「示範個格式係點」，唔係「呢張圖抄佢」。

`radar/observations.json` 記低觀察同來源連結（用嚟證明呢個體裁真係喺流行），但**唔存原圖**。

實際好處：跟呢條線做，你嘅客戶唔會同人撞樣。抄體裁 = 你有位放自己嘅品牌變數；抄原圖 = 你變成第 500 個一樣嘅帖。

---

## 客戶端：品牌視覺檔

由 `visual-identity-scan` 技能產出 `clients/<slug>/style/brand-visual.md`。

同 voice profile 一樣嘅原則：**要具體到可驗證**。

```markdown
# 品牌視覺 Brand Visual

> 樣本：<N> 張圖 · 信心度：<高/中/低>

## 色彩
- 主色：#E8D5C4（暖米）— 出現於 <N>/<總數> 張
- 輔色：#7A9E7E（灰綠）
- 強調色：#C4756B（磚紅）— 只用喺 CTA 同重點
- **從來冇出現**：純黑 #000、高飽和螢光色
- 整體飽和度偏低，明度偏高（淺調）

## 畫風
- 攝影為主 / 插畫為輔（比例 8:2）
- 光線：自然光、柔和、多數側光
- 質感：有輕微顆粒，唔係乾淨嘅商業攝影
- 主體：真人入鏡，多數唔望鏡頭
- 構圖：留白多，主體偏一側

## 排版
- 字體：<觀察到嘅中英文字體>
- 標題字級 vs 內文比例：約 2.2:1
- 對齊：左對齊為主
- 文字位置：多數喺下三分一
- 每張圖文字量：平均 <N> 字

## 唔好做（由觀察反推）
- 唔用滿版文字
- 唔用強對比黑底白字
- 唔用貼紙式裝飾元素

## ⚠️ 要人手確認
- 有冇官方品牌指引？（如有，覆蓋以上觀察）
- Logo 使用規則同安全距離
- 有冇唔可以用嘅顏色或元素
```

**點解要「從來冇出現」呢一欄**：同 voice profile 嘅禁用詞一樣道理。生圖模型好鍾意加自己嘅嘢（金色點綴、渐變、bokeh）。冇明確寫低「呢個品牌從來唔用」，佢就會加。

---

## 生圖流程

視覺 agent 每張圖行呢五步：

```
1. 讀已批准文案        queue/03-approved/<id>.md
2. 讀品牌視覺          style/brand-visual.md
3. 讀選用 pack         style/selected-packs.json → _trends/packs/<id>/prompt-recipe.md
4. 合成 prompt         骨架（pack）＋ 變數（brand）＋ 內容（文案）
5. 生圖 → 落 queue/04-assets/<id>/
```

**唔好由零寫 prompt。**每次由零寫，出嚟嘅風格就會每次唔同 —— 而品牌一致性正正就係靠風格唔變。配方係骨架，變嘅只有內容同品牌變數。

### 交付要留低咩

每張圖要有一份 `render.json` 同佢一齊：

```json
{
  "asset_id": "w35-post-01-cover",
  "pack_id": "pov-cover-2026q3",
  "render_mode": "image-only",
  "prompt": "<完整送出去嘅 prompt>",
  "model": "<config/tools.md 入面配置嘅圖像模型>",
  "aspect": "3:4",
  "text_on_image": "凌晨三點，我終於敢照鏡",
  "attempts": 2,
  "approved": false
}
```

留低完整 prompt 嘅理由：出到一張好嘅，你要重現到；出到一張差嘅，你要知道問題出喺骨架定變數。冇呢份記錄，視覺質量永遠靠彩數。

### QA 對圖要查咩

- [ ] 圖上文字**逐字**同 `text_on_image` 一致（`image-only` 模式必查）
- [ ] 顏色喺 `brand-visual.md` 嘅色系內，冇出現「從來冇出現」嘅顏色
- [ ] 冇模型自己加嘅裝飾（渐變、光暈、水印狀嘅假 logo）
- [ ] 主體處理符合品牌（例如「真人唔望鏡頭」）
- [ ] 有 `beauty-efficacy` modifier → **前後對比圖必須有「效果因人而異」字樣**，而且要用 text-layer 確保準確
- [ ] `aspect` 同目標平台一致

---

## Prompt 配方寫法

`prompt-recipe.md` 用變數槽，唔好寫死。

```markdown
# POV 封面 · 生圖配方

## 骨架
第一人稱視角，{SUBJECT}，{MOOD} 氛圍。
自然光，{LIGHT_DIRECTION}。
構圖：主體偏 {SUBJECT_POSITION}，{SAFE_ZONE} 留白。
色調：{PALETTE}，飽和度 {SATURATION}。
質感：{TEXTURE}。
畫面內唔好出現：文字以外嘅任何圖形標記、水印、logo、邊框。

## 變數槽
| 槽 | 由邊度嚟 | 例 |
|---|---|---|
| SUBJECT | 文案內容 | 一個女人坐喺床邊，背向鏡頭 |
| MOOD | 文案情緒 | 安靜、疲累但唔絕望 |
| LIGHT_DIRECTION | brand-visual.md | 側光，由左窗入 |
| SUBJECT_POSITION | brand-visual.md | 右下 |
| SAFE_ZONE | pack.json | 上方 25% |
| PALETTE | brand-visual.md | 暖米 #E8D5C4、灰綠 #7A9E7E |
| SATURATION | brand-visual.md | 偏低 |
| TEXTURE | brand-visual.md | 輕微顆粒 |

## 文字處理
render_mode = image-only → 圖上文字直接寫入 prompt，用引號括住，
並要求「文字必須完全一致，唔好改寫」。生完逐字核對。

## 常見失敗
| 症狀 | 原因 | 點改 |
|---|---|---|
| 出咗英文字 | 冇指定語言 | prompt 加「文字為繁體中文」 |
| 加咗唔想要嘅裝飾 | 冇寫排除項 | 補「畫面內唔好出現」清單 |
| 主體太中 | 冇指定位置 | 明確寫 SUBJECT_POSITION |
| 風格每次唔同 | 由零寫 prompt | 一定要用配方骨架 |
```

### 模型配置

實際用邊個圖像模型，寫喺 `config/tools.md`，唔好寫死喺配方入面 —— 模型更替快，配方唔應該跟住改。

配方應該係模型無關嘅：講構圖、光線、色調、質感、排除項。呢啲要求對任何圖像模型都成立。
