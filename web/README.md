# Cloudflare 版 — 多租戶工作台

每個客戶用自己嘅通行碼登入，只見到自己嗰個工作台。你（owner）見到全部。

```
瀏覽器 ──▶ Worker ──┬──▶ D1   名冊、邀請碼雜湊、檔案索引
                     └──▶ R2   工作台檔案內容（**只有文字**）
```

---

## 一件事要你先知

**呢個 server 唔會收任何圖片。冇上載圖片嘅端點。**

參考圖嘅分析（顏色、亮度、構圖）繼續喺客戶自己個瀏覽器度做，只有算出嚟嘅
色碼會上嚟。呢個唔係漏做 —— 你有啲客嘅參考圖係客人身體。原圖唔上你個 server，
你就唔會保管到人哋嘅身體相，出事嘅風險細一大截。

同意書亦都係一份**文字登記冊**（邊個、幾時、同意咗咩範圍），唔係掃描件。

托管客戶資料本身仍然係你嘅責任 —— 呢個設計只係把最敏感嗰部分擋喺門外。

---

## 部署（一次過）

需要 Node 18+。所有指令喺 `web/` 目錄入面跑。

**1. 登入 Cloudflare**
```bash
npx wrangler login
```

**2. 開資料庫同儲存**
```bash
npx wrangler d1 create workbench
npx wrangler r2 bucket create workbench-files
```

第一句會印一個 `database_id`。**抄低佢，貼入 `wrangler.toml`** 取代
`database_id = "..."` 嗰行。

**3. 建表**
```bash
npm run db:init
```

**4. 設兩個密碼**
```bash
npx wrangler secret put OWNER_KEY        # 你自己登入用嘅
npx wrangler secret put SESSION_SECRET   # 隨機長字串，貼落去就算
```

`SESSION_SECRET` 用呢句生成：
```bash
head -c 32 /dev/urandom | base64
```

> 兩個都**唔好**寫入 `wrangler.toml` —— 嗰個檔案會入 git。

**5. 出街**
```bash
npm run deploy
```

完成之後會俾你一個 `https://workbench.<你嘅名>.workers.dev` 網址。

---

## 日常用法

**你自己**：開個網址 → 用 `OWNER_KEY` 登入 → 撳「＋ 開新客」→ 六步撳完 →
撳「生成客戶通行碼」。

**個碼只顯示一次**，抄低咗先閂窗。之後淨係存雜湊，連你都攞唔返 ——
撳失咗就重新生成一個。

**客戶**：開同一個網址 → 入你俾佢嘅碼 → 只會見到自己嗰個工作台。

---

## 改咗行業表點算

行業、紅線、檔案範本嘅**唯一來源係 Python**（`workbench/taxonomy.py`、
`scaffold.py`）。改完之後：

```bash
python3 scripts/build_web.py    # 重新匯出 web/src/generated.js
cd web && npm run deploy
```

唔好手改 `web/src/generated.js`。`python3 -m tests.test_workbench` 會捉到唔同步。

點解咁緊張：呢個 repo 之前有兩個地方各自寫咗一份合規紅線，結果每份 BIBLE
有 15 條而唔係 8 條，仲有兩個唔同字眼嘅版本並存，靜靜雞錯咗好耐冇人發現。

---

## 測試

```bash
cd web && ./test.sh
```

12 項，全部測**隔離**：客戶偷唔偷到第二個客嘅檔案、路徑穿越、偽造 cookie、
撞名會唔會靜靜雞合併。

呢個唔係功能測試。隔離錯咗唔會有錯誤訊息，只會有一日有人喺自己個工作台
見到人哋嘅同意書。

---

## 本機試跑

```bash
cd web
cp .dev.vars.example .dev.vars    # 或者自己寫兩行
npm run db:init:local
npx wrangler dev --local
```

`.dev.vars` 已經喺 `.gitignore` 入面。

---

## 費用

Workers、D1、R2 都有免費額度。以呢個用量（幾十個客、每個三十個文字檔），
正常情況下唔會超出免費額度。真實數字要睇你 Cloudflare dashboard，
唔好信任何人（包括我）報嘅預估。

---

## 仲未做嘅嘢

老實講清楚：

- **冇備份／匯出。** 客戶資料喺 D1 同 R2，冇一鍵匯出。托管人哋嘅嘢通常要有。
- **冇刪除流程。** 客戶叫你刪晒佢啲嘢，你要自己入 dashboard 手動做。
- **冇審計記錄。** 邊個幾時睇過咩，冇記低。
- **通行碼冇到期。** 撤銷要入 D1 改 `revoked = 1`。
- **內容生產仲未接上。** 而家個網站做到嘅係：開工作台、睇工作台、隔離。
  真正生成內容要接 AI API，見 `docs/API-MODULES.md`。

頭四樣係托管客戶資料嘅基本責任。開始收真客戶之前值得補。
