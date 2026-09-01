# 工作台 Workbench

由一句話，生成一個真正跑得動嘅多客戶 AI marketing 工作台。

零外部依賴 —— 淨係要 Python 3.11+。冇 pip install，冇 API key 都行得（分類、生成、
dashboard 全部本機跑）。接 API 係之後嘅事，見 [`docs/API-MODULES.md`](../docs/API-MODULES.md)。

**唔識用 terminal 嘅人，睇 [`docs/開始使用.md`](../docs/開始使用.md)，只需要記一行指令。**

```bash
python3 -m workbench start         # 開工作台＋自動彈瀏覽器，之後全部撳掣
python3 -m workbench demo          # 起五個唔同行業嘅示範客戶
python3 -m workbench status        # 睇每個客塞喺邊
python3 -m workbench serve         # 開 dashboard（http://127.0.0.1:8787）
python3 -m workbench doctor        # 檢查有冇「睇落完整但唔可以出街」
python3 -m workbench industries    # 列出支援行業同各自嘅核心問題
```

開真客：

```bash
python3 -m workbench new "客戶做網店賣產後紮肚服務，用開 IG，想發展埋小紅書、Threads、FB，帳號 @mamis_sunshine"
```

先睇判斷結果、唔寫檔案：加 `--dry-run`。

或者完全唔打字 —— `start` 之後撳「＋ 開新客」，六步撳完就有。
每一步嘅選項會跟住上一步變（揀咗行業，平台同工作就自動配好；
揀咗「做圖」，視覺崗位就自動加）。

---

## 呢個工作台解決緊咩

唔係「幫你寫快啲」。係**令生產過程有得查**。

一般做法係：靠人記住每個客嘅語氣同禁忌，出事之後執嗰篇稿。
呢度嘅做法係：語氣、紅線、已批准講法全部係檔案，出事之後**執嗰一層**，
下次唔會再犯 —— 執咗份稿冇改到系統，就一定會再犯。

三件事係硬規矩：

1. **空係一個明確狀態，唔係一個要填嘅空格。**
   證據庫係空 → 所有稿都唔可以落任何數字、個案、資格。寧願交白卷。
2. **紅線要機械式檢查得到。** 寫唔到檢查方法嘅，唔算紅線。
3. **QA 永遠唔合併。** 員工編制爆咗上限可以合併其他崗位，唔可以合併 QA ——
   自己審自己唔算審過。

---

## 支援行業

分類係**明文規則**（`taxonomy.py`），唔係每次問模型。同一句嘢今日聽日分類一樣，
睇得到、改得到、argue 得到。

Marketing 代理 · 設計工作室 · Social Media 營運 · 網頁開發 · 小朋友產品 ·
電商品牌 · 客服中心 · 預約制服務 · 教育培訓 · 實體店 · B2B 專業服務 ·
個人品牌 · 非牟利

關鍵詞分三級：**交付物（6 分）> 行業詞（3 分）> 通用商業詞（1 分）**。

點解要分：「網店賣紮肚服務」入面，「網店」講嘅係**賣嘅渠道**，「紮肚」講嘅係
**交付咩**。分做電商就會漏晒健康同功效兩套紅線。交付物一定要贏渠道。

兩個行業分數差距細過一個交付物詞（< 6 分）時，工作台**唔會扮肯定** ——
會喺 `run-report.md` 寫明「行業分唔清，要人手確認」。

---

## 五種合規修飾

命中就自動疊紅線入 `BIBLE.md`（唔係留喺 reference 檔 —— agent 讀 BIBLE，
唔會自己去揭 reference）：

`health-adjacent` · `beauty-efficacy` · `finance-adjacent` · `minors` · `regulated-hk`

可以疊。紮肚同時中健康同功效 —— 因為體形宣稱係**另一套**監管邏輯，唔係健康嗰套。

---

## 四種狀態

| 燈 | 意思 | 分別喺邊 |
|---|---|---|
| ○ 待設置 | 乜都未開始，缺料 | 未開工缺料係正常 |
| ● 阻塞 | 生產線有嘢，但出唔到街 | 有稿出唔到街先係問題 |
| ● 等人審 | 行緊，塞喺人手關卡 | 正常運作嘅樣 |
| ● 運作中 | 全條線通 | — |

呢個分別好重要：兩者用同一個紅燈，就會日日見到紅燈，然後冇人再望 dashboard。

---

## 每個客會生成咩

```
clients/<slug>/
  pitch.md              ← present 俾客聽嗰頁：佢塞喺邊、工作台拆開咗咩
  run-report.md         ← 邊啲係事實、邊啲係推斷、邊啲仲未做
  workspace.json        ← 編制、平台、紅線、原話
  CHECKLIST.md          ← 交付前驗收
  brand/
    BIBLE.md            ← 品牌憲法（紅線已經寫死喺度）
    MEMORY.md           ← 點解改，唔係改成點
    brain/01–08         ← 定位、語氣、受眾語言、已批准證據、hook、平台、review、learning
  agents/<role>/AGENTS.md
  queue/00–06           ← 簡報 → 角度 → 草稿 → 已過質 → 素材 → 排程 ／ 回覆
  style/                ← brand-visual.md、selected-packs.json、renders/
  data/                 ← scraped、inbox、consent
  config/               ← tools.md、schedule.md
```

重跑同一個客係安全嘅 —— 已存在嘅檔案唔會被覆蓋（除非 `--force`）。

---

## 檔案

| | |
|---|---|
| `taxonomy.py` | 行業分類、合規修飾、員工編制推導 |
| `wizard.py` | 六步設定精靈嘅步驟同選項（選項喺呢度算，唔喺瀏覽器算）|
| `visual.py` | 把瀏覽器讀返嘅圖片特徵寫成 `brand-visual.md` |
| `pipeline.py` | 一句話 → workspace（調用 skill 嘅 `scaffold.py`）|
| `state.py` | 讀檔案系統 → 生產線狀態、阻塞、下一步 |
| `server.py` | Dashboard ＋ 精靈 API（stdlib，冇依賴）|
| `models.py` | 每個崗位用邊個模型、effort、batch、快取 |
| `seed.py` | 示範資料（**只用喺 demo**）|
| `cli.py` | 指令 |

狀態**由檔案系統推導，唔另存一份 state.json** —— 存多一份就一定會同實際檔案脫節，
而脫節嘅 dashboard 比冇 dashboard 更差，因為人會信佢。

---

## 測試

```bash
python3 -m tests.test_workbench
```

測嘅係判斷，唔係格式：分錯行業、漏咗紅線、假信心度 —— 呢三樣會令客戶出事。
