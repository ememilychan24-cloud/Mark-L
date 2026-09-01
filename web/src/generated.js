// 由 scripts/build_web.py 生成 —— 唔好手改。
// 改行業表／紅線／範本 = 改 workbench/taxonomy.py 或 scaffold.py，
// 然後跑 `python3 scripts/build_web.py`。
// 手改呢個檔案 = 製造第二個真相來源，呢個 repo 已經因為咁中過一次招。

export const WB = {
  "_generated_by": "scripts/build_web.py — 唔好手改。改 taxonomy.py 再跑一次。",
  "core_agents": [
    "orchestrator",
    "research",
    "content",
    "qa",
    "analytics"
  ],
  "max_agents": 8,
  "steps": [
    {
      "key": "industry",
      "title": "你做邊行？"
    },
    {
      "key": "confirm",
      "title": "係咪講中咗你？"
    },
    {
      "key": "platforms",
      "title": "你喺邊度出內容？"
    },
    {
      "key": "jobs",
      "title": "想佢幫你做啲咩？"
    },
    {
      "key": "visual",
      "title": "你嘅圖係咩樣？"
    },
    {
      "key": "review",
      "title": "睇一眼就開工"
    }
  ],
  "archetypes": [
    {
      "key": "agency-creative",
      "label": "Marketing／廣告代理",
      "pain": "每個客一套做法，全部喺人腦入面。做嘢嘅人一走，個客嘅語氣同禁忌就冇咗。新人上手要跟三個月，而且每次交稿都要 AD 逐隻字改。",
      "unlock": "每個客一個獨立工作台，語氣、紅線、已批准講法全部係檔案。新人第一日就用同一套規矩交稿，AD 只審有爭議嗰啲。",
      "extra_agents": [
        "engage"
      ],
      "platforms": [
        "ig",
        "fb",
        "threads",
        "xhs"
      ],
      "skills": [
        "brand-voice",
        "content-calendar",
        "ad-copy",
        "edm",
        "report-builder"
      ],
      "redlines": [
        "唔可以把 A 客嘅個案、數據、講法搬去 B 客",
        "客戶未批准嘅 Claim 唔可以出街"
      ]
    },
    {
      "key": "design-studio",
      "label": "設計工作室",
      "pain": "靚嘢做得出，但講唔出點解值呢個價。提案九成篇幅係圖，客戶問「點解要咁」就答唔到，最後變成鬥改稿同鬥平。",
      "unlock": "每個提案自動配一份「設計理由」：呢個色解決咩、呢個排版對住邊個受眾。改稿次數跌，因為爭論由品味變成目標。",
      "extra_agents": [
        "visual"
      ],
      "platforms": [
        "ig",
        "xhs"
      ],
      "skills": [
        "brand-voice",
        "visual-identity-scan",
        "image-gen",
        "case-study"
      ],
      "redlines": [
        "唔可以用未買授權嘅字體、圖庫、音樂"
      ]
    },
    {
      "key": "social-ops",
      "label": "Social Media 營運",
      "pain": "日日追 deadline 出帖，冇時間諗。四個平台等於四份工，而覆盤永遠冇做 —— 所以下個月再由零開始諗題目。",
      "unlock": "一份主內容自動改寫成四個平台版本（唔係複製，係重寫 hook 同節奏），同埋每星期自動出一份「邊條 work、點解 work」，直接變下輪選題。",
      "extra_agents": [
        "engage",
        "visual"
      ],
      "platforms": [
        "ig",
        "threads",
        "fb",
        "xhs"
      ],
      "skills": [
        "brand-voice",
        "content-calendar",
        "cross-post",
        "comment-triage",
        "report-builder"
      ],
      "redlines": [
        "回覆客人前一律要人批"
      ]
    },
    {
      "key": "web-dev",
      "label": "網頁／應用開發",
      "pain": "賣緊技術，但客戶聽唔明技術。報價單一堆功能名，客戶只係識比價錢，結果每單都要傾好耐先簽，簽完又不停改需求。",
      "unlock": "把功能自動翻譯成「你嘅生意會點樣改變」，報價變成方案。同時把每次改需求記錄成有出處嘅決定，收尾唔會拗數。",
      "extra_agents": [
        "funnel"
      ],
      "platforms": [
        "linkedin",
        "fb"
      ],
      "skills": [
        "brand-voice",
        "case-study",
        "proposal",
        "seo",
        "edm"
      ],
      "redlines": [
        "唔可以承諾未落實嘅交付日期同功能"
      ]
    },
    {
      "key": "kids-product",
      "label": "小朋友產品",
      "pain": "受眾係家長，用家係細路，兩把聲要用同一篇嘢講。而且講錯安全、成長、教育效果，係要負法律責任嘅。",
      "unlock": "家長版同小朋友版分開生成，安全同功效字眼行預設攔截，有小朋友出鏡嘅素材一律要監護人同意先入得工作台。",
      "extra_agents": [
        "visual"
      ],
      "platforms": [
        "ig",
        "fb",
        "xhs"
      ],
      "skills": [
        "brand-voice",
        "image-gen",
        "content-calendar",
        "compliance-check"
      ],
      "redlines": []
    },
    {
      "key": "ecommerce",
      "label": "電商品牌",
      "pain": "產品好，但每張圖每篇文都要人由零起。上新款＝重做一次成套素材，所以出貨速度永遠追唔上補貨速度。",
      "unlock": "一個 SKU 入面嘅賣點，一次過生成主圖、詳情、廣告文案、EDM，全部跟返品牌語氣同已批准功效講法。",
      "extra_agents": [
        "visual",
        "funnel"
      ],
      "platforms": [
        "ig",
        "xhs",
        "fb"
      ],
      "skills": [
        "brand-voice",
        "image-gen",
        "ad-copy",
        "edm",
        "product-copy",
        "report-builder"
      ],
      "redlines": [
        "價格、庫存、運費要同後台一致"
      ]
    },
    {
      "key": "bpo-support",
      "label": "客服中心 / BPO",
      "pain": "同樣嘅問題答一萬次，但每個同事答法唔同。客人投訴嘅唔係答案錯，係「上次唔係咁講」。而知識庫永遠落後現實兩個月。",
      "unlock": "回覆由同一份已批准講法生成，語氣一致；答唔到嘅自動變成知識庫缺口清單，唔會沉底。高風險對話一律轉人手，唔會自動出街。",
      "extra_agents": [
        "engage"
      ],
      "platforms": [
        "fb",
        "ig"
      ],
      "skills": [
        "brand-voice",
        "comment-triage",
        "faq-builder",
        "escalation",
        "report-builder"
      ],
      "redlines": [
        "投訴、退款、法律相關對話一律轉人手，唔可以自動回覆",
        "唔可以承諾補償金額或處理時限"
      ]
    },
    {
      "key": "service-booking",
      "label": "預約制服務",
      "pain": "生意靠師傅同口碑，但口碑喺 WhatsApp 入面散晒。問極都係嗰幾條問題，答完冇人記低，落單率靠彩數。",
      "unlock": "把重複查詢變成內容（因為佢哋問嘅就係佢哋想睇嘅），把個案變成有同意書、有出處嘅證據庫，落單前嘅疑問內容自動處理咗。",
      "extra_agents": [
        "engage",
        "funnel"
      ],
      "platforms": [
        "ig",
        "xhs",
        "fb",
        "threads"
      ],
      "skills": [
        "brand-voice",
        "content-calendar",
        "comment-triage",
        "case-study",
        "booking-funnel"
      ],
      "redlines": [
        "個案分享要有書面同意並隱去可識別資料"
      ]
    },
    {
      "key": "education",
      "label": "教育／培訓",
      "pain": "課程內容係最強嘅資產，但全部困喺課室入面。招生靠減價，因為冇嘢俾人喺報名前判斷質素。",
      "unlock": "把課程知識切成公開內容，令人未報名已經學到嘢，報名變成「想學多啲」而唔係「邊間平」。",
      "extra_agents": [
        "funnel"
      ],
      "platforms": [
        "ig",
        "fb",
        "threads",
        "yt"
      ],
      "skills": [
        "brand-voice",
        "content-calendar",
        "curriculum-slice",
        "edm",
        "seo"
      ],
      "redlines": [
        "唔可以保證成績、合格率或收入結果"
      ]
    },
    {
      "key": "local-storefront",
      "label": "實體店",
      "pain": "街客靠地點，熟客靠老闆記性。網上搵到嘅資料同店入面唔一樣，而評論冇人管，好嘅冇用，差嘅冇覆。",
      "unlock": "店內現實（貨、價、時間）同對外內容綁埋一齊更新，評論分流成回覆同下輪內容題目。",
      "extra_agents": [
        "engage"
      ],
      "platforms": [
        "ig",
        "fb"
      ],
      "skills": [
        "brand-voice",
        "content-calendar",
        "comment-triage",
        "local-seo"
      ],
      "redlines": [
        "營業時間、地址、價格要同現場一致"
      ]
    },
    {
      "key": "b2b-services",
      "label": "B2B 專業服務",
      "pain": "專業嘢講得太深冇人明，講得太淺又似騙徒。銷售週期長，但中間六個月完全冇嘢同潛在客戶講。",
      "unlock": "把專業判斷變成一連串可以連續睇落去嘅內容，令長銷售週期有嘢可以跟進，而唔係靠 sales 死跟。",
      "extra_agents": [
        "funnel"
      ],
      "platforms": [
        "linkedin",
        "fb"
      ],
      "skills": [
        "brand-voice",
        "case-study",
        "proposal",
        "edm",
        "seo"
      ],
      "redlines": [
        "唔可以提供個別專業意見，只可以講一般原則"
      ]
    },
    {
      "key": "creator-ip",
      "label": "個人品牌／創作者",
      "pain": "條數靠自己一個人出鏡。停一星期，數字就跌。想搵人幫手，但冇人講到嗰把聲。",
      "unlock": "把「嗰把聲」寫成可驗證嘅檔案（句長、開場、禁忌、口頭禪），第二個人（或 AI）寫出嚟嘅嘢過得到自己嗰關。",
      "extra_agents": [
        "visual",
        "engage"
      ],
      "platforms": [
        "ig",
        "threads",
        "xhs",
        "yt"
      ],
      "skills": [
        "brand-voice",
        "content-calendar",
        "image-gen",
        "comment-triage"
      ],
      "redlines": []
    },
    {
      "key": "nonprofit",
      "label": "非牟利／社區組織",
      "pain": "做嘅嘢好有意義，但講出嚟好悶。捐款同義工靠一年一次活動，平時完全冇聲。",
      "unlock": "把日常工作變成持續可信嘅紀錄，令支持者知道錢去咗邊，而唔係一年感動一次。",
      "extra_agents": [
        "engage"
      ],
      "platforms": [
        "fb",
        "ig"
      ],
      "skills": [
        "brand-voice",
        "content-calendar",
        "impact-report",
        "edm"
      ],
      "redlines": [
        "服務對象嘅影像同故事要有書面同意",
        "唔可以誇大受助人數或成效"
      ]
    }
  ],
  "modifiers": [
    {
      "key": "health-adjacent",
      "label": "健康相關",
      "why": "講身體、症狀、康復就落入醫療廣告嘅監管範圍，唔係「小心啲用字」咁簡單。",
      "redlines": [
        "唔用「治療／根治／醫學證實／療效」呢類字眼",
        "任何身體症狀內容一律加「持續或惡化請諮詢醫護人員」",
        "唔提供劑量或療程建議",
        "個案分享要有書面同意並隱去可識別資料",
        "唔宣稱取代專業醫療意見"
      ]
    },
    {
      "key": "beauty-efficacy",
      "label": "美容功效",
      "why": "體形、外觀嘅功效宣稱有獨立一套監管邏輯，同健康嗰套唔一樣，要疊埋一齊。",
      "redlines": [
        "功效宣稱要有測試依據，唔可以用個人感受當證據",
        "前後對比圖要標明個人差異，同拍攝條件一致",
        "唔用「必瘦」「保證」「永久」呢類絕對詞"
      ]
    },
    {
      "key": "finance-adjacent",
      "label": "金融相關",
      "why": "講錢嘅承諾係受規管嘅行為，講錯會有法律後果而唔係公關後果。",
      "redlines": [
        "唔保證回報，唔講「穩賺」「低風險高回報」",
        "唔提供個人化投資建議",
        "所有數字要標明出處同日期"
      ]
    },
    {
      "key": "minors",
      "label": "涉及未成年",
      "why": "未成年人嘅影像同數據有獨立保護要求，唔可以當普通素材處理。",
      "redlines": [
        "唔直接向兒童落 CTA",
        "唔用兒童真實影像（除非有監護人書面同意）",
        "唔收集兒童個人資料"
      ]
    },
    {
      "key": "regulated-hk",
      "label": "香港受規管行業",
      "why": "香港有《商品說明條例》同行業牌照要求，本地客戶唔可以照搬外地做法。",
      "redlines": [
        "牌照號碼、資格要準確並可查證",
        "唔用誤導性價格表述（原價、限時要真實）"
      ]
    }
  ],
  "platform_labels": {
    "ig": {
      "label": "Instagram",
      "hint": "圖同短片為主，日常感"
    },
    "xhs": {
      "label": "小紅書",
      "hint": "搜尋型平台，收藏比讚重要"
    },
    "threads": {
      "label": "Threads",
      "hint": "純文字，靠一句話勾起好奇"
    },
    "fb": {
      "label": "Facebook",
      "hint": "年紀大啲嘅受眾，要穩陣"
    },
    "yt": {
      "label": "YouTube",
      "hint": "長片同教學"
    },
    "tiktok": {
      "label": "TikTok",
      "hint": "短片，節奏要快"
    },
    "linkedin": {
      "label": "LinkedIn",
      "hint": "B2B、專業形象"
    },
    "edm": {
      "label": "電郵 EDM",
      "hint": "熟客同名單"
    },
    "web": {
      "label": "自家網站",
      "hint": "落地頁同 SEO"
    },
    "whatsapp": {
      "label": "WhatsApp",
      "hint": "查詢同跟進"
    },
    "wechat": {
      "label": "微信",
      "hint": "內地客"
    }
  },
  "skill_labels": {
    "brand-voice": {
      "label": "學你嘅語氣",
      "hint": "由你出過嘅帖，算出句長、開場、禁忌",
      "core": true
    },
    "content-calendar": {
      "label": "排內容日程",
      "hint": "每週出選題同排程",
      "core": true
    },
    "image-gen": {
      "label": "做圖",
      "hint": "跟你嘅顏色同畫風生成圖卡",
      "core": false
    },
    "visual-identity-scan": {
      "label": "認出你嘅畫風",
      "hint": "由已出街嘅圖，讀返顏色、排版、風格",
      "core": false
    },
    "ad-copy": {
      "label": "寫廣告文案",
      "hint": "投放用嘅短文案同標題",
      "core": false
    },
    "edm": {
      "label": "寫電郵",
      "hint": "EDM 同名單跟進",
      "core": false
    },
    "product-copy": {
      "label": "寫產品文案",
      "hint": "賣點、詳情頁、規格",
      "core": false
    },
    "case-study": {
      "label": "寫個案",
      "hint": "把做過嘅嘢寫成有出處嘅個案",
      "core": false
    },
    "proposal": {
      "label": "寫提案",
      "hint": "把功能翻譯成客戶聽得明嘅好處",
      "core": false
    },
    "comment-triage": {
      "label": "分流留言私訊",
      "hint": "分成 FAQ／疑慮／查詢／選題四類",
      "core": false
    },
    "faq-builder": {
      "label": "建 FAQ 知識庫",
      "hint": "把重複問題變成標準答案",
      "core": false
    },
    "escalation": {
      "label": "轉人手機制",
      "hint": "高風險對話唔會自動回",
      "core": false
    },
    "booking-funnel": {
      "label": "接預約",
      "hint": "由內容接到落表格同跟進",
      "core": false
    },
    "curriculum-slice": {
      "label": "切課程內容",
      "hint": "把課堂知識變成公開內容",
      "core": false
    },
    "impact-report": {
      "label": "寫成效報告",
      "hint": "俾捐款人同持份者睇",
      "core": false
    },
    "seo": {
      "label": "搜尋排名",
      "hint": "關鍵字同網站文案",
      "core": false
    },
    "local-seo": {
      "label": "本地搜尋",
      "hint": "地圖、營業時間、評論",
      "core": false
    },
    "report-builder": {
      "label": "每週覆盤",
      "hint": "邊條 work、點解 work、下輪改咩",
      "core": true
    },
    "compliance-check": {
      "label": "合規檢查",
      "hint": "出街前逐條紅線機械式檢查",
      "core": false
    },
    "cross-post": {
      "label": "跨平台改寫",
      "hint": "同一觀點喺每個平台重新寫過",
      "core": false
    }
  },
  "role_labels": {
    "orchestrator": {
      "label": "總監",
      "hint": "派工同驗收"
    },
    "research": {
      "label": "研究",
      "hint": "諗選題同角度"
    },
    "content": {
      "label": "文案",
      "hint": "寫稿"
    },
    "qa": {
      "label": "品質",
      "hint": "出街前逐條檢查"
    },
    "analytics": {
      "label": "數據",
      "hint": "覆盤同下輪建議"
    },
    "visual": {
      "label": "視覺",
      "hint": "做圖"
    },
    "video": {
      "label": "影片",
      "hint": "腳本同剪片"
    },
    "engage": {
      "label": "社群",
      "hint": "覆留言私訊"
    },
    "funnel": {
      "label": "轉化",
      "hint": "接表格同名單"
    }
  },
  "tpl": {
    "bible": "# {{BRAND}} 品牌憲法\n\n> 最後更新：2026-09-01 · 語料信心度：**待評估**\n> Archetype：`{{ARCHETYPE}}`\n\n## 一句話定位\n<賣咩，賣俾邊個，解決咩 — 由步驟 1 填>\n\n## 受眾（具體到可以認得出）\n- 年齡／人生階段：\n- 處境（幾時、喺邊、心情點）：\n- 佢自己點形容個問題：「<原話，由 03-audience-language.md 攞>」\n- 佢唔買嘅理由：\n\n## 語氣三行\n1. 好似 <一個具體嘅人物關係>\n2. 每篇都要 <一個必做動作>\n3. 從來唔會 <一個必唔做>\n\n## 紅線（違反即退回，唔需要討論）\n\n> 每一條都要可以機械式檢查。寫唔到檢查方法嘅，唔算紅線。\n\n- [ ] <未填 —— 行業同合規紅線由 taxonomy.py 寫入。單獨跑 scaffold.py 唔會有紅線，因為 scaffold 唔知你揀咗咩合規修飾。>\n\n## 證據來源\n只可引用 `brand/brain/04-approved-claims.md` 入面嘅嘢。\n嗰份檔案為空 = 呢一輪唔可以落任何數據或個案 Claim。\n\n## 邊啲嘢一定要人批\n- 主角度同對外 Claim\n- 所有 CTA\n- <由客戶答案補充>\n",
    "agents": {
      "orchestrator": "# 總監 Agent — {{BRAND}}\n\n## Role\n你係 {{BRAND}} 嘅總監 Agent。\n\n## Goal\n派工、驗收、對齊 BIBLE。\n\n## Inputs（只可以讀呢啲）\n- `brand/BIBLE.md`\n- `brand/brain/01-positioning.md`\n- `brand/brain/02-voice-profile.md`\n\n## Rules\n- 唔好自己寫內容 —— 你嘅工作係派工同驗收\n- 任何 agent 交嘢，先對照 CHECKLIST.md 再決定收唔收\n- 同一個問題被退回兩次以上，要求補返 MEMORY.md 而唔係再改一次\n\n## 交付成果\n交去 `queue/00-briefs/`，包含：\n- 本週工作分派\n- 驗收結果（收／退／原因）\n\n## 人手檢查點\n本週主題方向要人確認先開工。\n",
      "research": "# 研究 Agent — {{BRAND}}\n\n## Role\n你係 {{BRAND}} 嘅研究 Agent。\n\n## Goal\n由市場訊號提煉 3–6 個候選角度。\n\n## Inputs（只可以讀呢啲）\n- `brand/BIBLE.md`\n- `brand/brain/01-positioning.md`\n- `brand/brain/02-voice-profile.md`\n- `brand/brain/03-audience-language.md`\n- `brand/brain/05-hook-library.md`\n- `data/scraped/`\n\n## Rules\n- 每個關鍵 Claim 要保留原始連結、平台、作者同日期\n- 唔可以把熱門內容直接當品牌立場 —— 熱門同啱唔啱係兩回事\n- 先出 3–6 個角度再由人揀，唔好自己落決定\n- 高互動唔等於有效：多讚可能係有爭議，多收藏先代表實用\n\n## 交付成果\n交去 `queue/01-insights/`，包含：\n- 3–6 個候選角度，每個附受眾張力、證據連結、建議 hook 與 CTA、風險\n- 建議主角度同理由\n\n## 人手檢查點\n主角度、對外 Claim、CTA 一律等人批准後先交俾文案。\n",
      "content": "# 文案 Agent — {{BRAND}}\n\n## Role\n你係 {{BRAND}} 嘅文案 Agent。\n\n## Goal\n把已批准角度寫成 Master Content 及各平台版本。\n\n## Inputs（只可以讀呢啲）\n- `brand/BIBLE.md`\n- `brand/brain/01-positioning.md`\n- `brand/brain/02-voice-profile.md`\n- `brand/brain/03-audience-language.md`\n- `brand/brain/04-approved-claims.md`\n- `brand/brain/06-platform-rules.md`\n- `brand/brain/05-hook-library.md`\n- `queue/01-insights/  ← 只讀已批准嘅`\n\n## Rules\n- 先寫一份 Master Content，再按平台改寫 —— 唔好四個平台改幾隻字\n- 每個平台重新寫 hook、重新排節奏、重新諗 CTA\n- 逐項對照 02-voice-profile.md 嘅數字（句長、標點、稱呼、emoji）\n- 04-approved-claims.md 為空時，唔可以落任何數字或個案\n\n## 交付成果\n交去 `queue/02-drafts/`，包含：\n- master-content.md（受眾問題／核心觀點／3–5 個重點／證據／CTA）\n- 各平台版本（{{PLATFORMS}}）\n\n## 人手檢查點\n主要文案、標題、CTA 要人批准後先交俾視覺。\n",
      "qa": "# 品質 Agent — {{BRAND}}\n\n## Role\n你係 {{BRAND}} 嘅品質 Agent。\n\n## Goal\n對照紅線與語氣檔判定可否交人審閱。\n\n## Inputs（只可以讀呢啲）\n- `brand/BIBLE.md`\n- `brand/brain/01-positioning.md`\n- `brand/brain/02-voice-profile.md`\n- `brand/brain/04-approved-claims.md`\n- `brand/brain/06-platform-rules.md`\n- `queue/02-drafts/`\n\n## Rules\n- 你嘅唯一標準來源係 CHECKLIST.md 同 BIBLE.md 嘅紅線，唔好加自己嘅偏好\n- 退回時一定要指明違反咗邊一條，同建議補去邊一層\n- 同一份稿唔好退回超過兩次 —— 第三次要升級俾人處理\n\n## 交付成果\n交去 `queue/03-approved/`，包含：\n- 判定：Ready to Review 或 退回\n- 退回時：違反條目 ＋ 應補去邊一層\n\n## 人手檢查點\n紅線違規一律升級俾人，唔可以自行放行。\n",
      "visual": "# 視覺 Agent — {{BRAND}}\n\n## Role\n你係 {{BRAND}} 嘅視覺 Agent。\n\n## Goal\n把已批准內容變成圖卡與素材。\n\n## Inputs（只可以讀呢啲）\n- `brand/BIBLE.md`\n- `brand/brain/01-positioning.md`\n- `brand/brain/02-voice-profile.md`\n- `queue/03-approved/`\n\n## Rules\n- 視覺跟隨已批准內容，唔好先出靚圖再塞文字\n- 一張卡只承擔一個主要訊息\n- 品牌規格（顏色、字體、水印）由 06-platform-rules.md 決定，唔好每次重新描述\n\n## 交付成果\n交去 `queue/04-assets/`，包含：\n- 圖卡檔案\n- 卡序說明（首卡 hook、尾卡 CTA）\n\n## 人手檢查點\n主要畫面要人批准後先入排程。\n",
      "video": "# 影片 Agent — {{BRAND}}\n\n## Role\n你係 {{BRAND}} 嘅影片 Agent。\n\n## Goal\n把內容拆成腳本、字幕、封面與延伸卡片。\n\n## Inputs（只可以讀呢啲）\n- `brand/BIBLE.md`\n- `brand/brain/01-positioning.md`\n- `brand/brain/02-voice-profile.md`\n- `queue/03-approved/`\n\n## Rules\n- 把內容拆成聲音、畫面、字幕、封面、CTA 五層分別處理\n- Repurpose 唔係搬運 —— 同一觀點要重新組織成另一種閱讀體驗\n- 局部重跑失敗嘅段落，唔好成套重做\n\n## 交付成果\n交去 `queue/04-assets/`，包含：\n- 腳本、字幕檔、封面\n- 延伸 Carousel 卡片\n\n## 人手檢查點\n封面同 hook 要人批准。\n",
      "engage": "# 社群 Agent — {{BRAND}}\n\n## Role\n你係 {{BRAND}} 嘅社群 Agent。\n\n## Goal\n分流留言與私訊，草擬回覆。\n\n## Inputs（只可以讀呢啲）\n- `brand/BIBLE.md`\n- `brand/brain/01-positioning.md`\n- `brand/brain/02-voice-profile.md`\n- `brand/brain/03-audience-language.md`\n- `data/inbox/`\n\n## Rules\n- 分流先於回覆：分成 FAQ／反對理由／內容缺口／潛在查詢四類\n- 需要判斷或高價值嘅對話一律入 Review Queue，唔好自己答\n- 把重複問題送返 03-audience-language.md 同下一輪選題\n\n## 交付成果\n交去 `queue/06-replies/`，包含：\n- 回覆草稿（分流標記）\n- 送返選題嘅問題清單\n\n## 人手檢查點\n所有對外回覆要人批准後先發出。\n",
      "funnel": "# 轉化 Agent — {{BRAND}}\n\n## Role\n你係 {{BRAND}} 嘅轉化 Agent。\n\n## Goal\n承接內容到落地頁、表單與名單。\n\n## Inputs（只可以讀呢啲）\n- `brand/BIBLE.md`\n- `brand/brain/01-positioning.md`\n- `brand/brain/02-voice-profile.md`\n- `queue/03-approved/`\n\n## Rules\n- CTA 同追蹤參數喺設計時就要預留，唔好事後補\n- 完成標準係後台搵得返記錄，唔係前台彈「成功」\n- 每個名單要有來源、階段、負責人、下一步\n\n## 交付成果\n交去 `queue/05-scheduled/`，包含：\n- 落地頁 ／ 表單規格\n- 追蹤參數規則\n- 測試計劃\n\n## 人手檢查點\n對外承諾、收集資料範圍要人批准。\n",
      "analytics": "# 數據 Agent — {{BRAND}}\n\n## Role\n你係 {{BRAND}} 嘅數據 Agent。\n\n## Goal\n週度覆盤與下一輪測試建議。\n\n## Inputs（只可以讀呢啲）\n- `brand/BIBLE.md`\n- `brand/brain/01-positioning.md`\n- `brand/brain/02-voice-profile.md`\n- `queue/05-scheduled/ 及平台成效資料`\n\n## Rules\n- 唔好用一個總分代替判斷 —— 沿流程逐層睇邊層掉失\n- 下一輪只建議改一個主要變數，否則分唔清改善來自邊度\n- 結論要寫返 08-learning.md，唔係淨係出報表\n\n## 交付成果\n交去 `reports/`，包含：\n- 週報：保留／停止／再測／更新 Skill 四個決定\n- 下一輪測試建議（單一變數）\n\n## 人手檢查點\nSkill 或品牌資料嘅修訂建議要人批准後先寫回。\n"
    },
    "brain": [
      {
        "file": "01-positioning.md",
        "num": "01",
        "title": "定位背景",
        "what": "使命、產品、價值主張、競爭位置",
        "may_empty": false,
        "how": "由對應步驟蒸餾產生。"
      },
      {
        "file": "02-voice-profile.md",
        "num": "02",
        "title": "品牌語氣",
        "what": "句長、開場、標點、稱呼、禁用詞",
        "may_empty": false,
        "how": "由對應步驟蒸餾產生。"
      },
      {
        "file": "03-audience-language.md",
        "num": "03",
        "title": "受眾語言",
        "what": "受眾原話、反對理由、常用詞",
        "may_empty": true,
        "how": "由留言區爬取後蒸餾，或由客戶提供真實客戶查詢記錄。"
      },
      {
        "file": "04-approved-claims.md",
        "num": "04",
        "title": "已批准主張／證據",
        "what": "已授權個案、數據、產品事實",
        "may_empty": true,
        "how": "客戶提供有書面同意嘅個案或有出處嘅數據後，由人手加入並標明授權範圍。"
      },
      {
        "file": "05-hook-library.md",
        "num": "05",
        "title": "Hook 與成功例子",
        "what": "有效開場結構，附原帖連結",
        "may_empty": true,
        "how": "由自家高表現帖抽取開場結構，每條附原帖連結。"
      },
      {
        "file": "06-platform-rules.md",
        "num": "06",
        "title": "平台規格",
        "what": "各平台格式、節奏、禁忌",
        "may_empty": false,
        "how": "由對應步驟蒸餾產生。"
      },
      {
        "file": "07-review-log.md",
        "num": "07",
        "title": "決策／Review 記錄",
        "what": "批准、退回、修改原因",
        "may_empty": true,
        "how": "每次人手 review 之後補一條，記低批准／退回同原因。"
      },
      {
        "file": "08-learning.md",
        "num": "08",
        "title": "Learning 更新",
        "what": "學到嘅有效做法與 SOP 修訂",
        "may_empty": true,
        "how": "每次 campaign 完結後補一條，記低有效做法同 SOP 修訂。"
      }
    ],
    "empty_notice": "（空）\n\n第一版未有內容。\n\n**在此檔案為空期間，任何產出唔可以引用呢個櫃桶嘅資料。**\n唔好因為空就自己推斷內容 —— 空係一個明確狀態，唔係一個要填嘅空格。\n\n補充方式：{how}\n",
    "memory": "# 決策與學習記錄\n\n> 每次 review 之後補一條。「點解改」比「改成點」有用。\n\n## 已批准（可以再用）\n| 日期 | 咩嘢 | 點解 work | 連結 |\n|---|---|---|---|\n\n## 已退回（唔好再犯）\n| 日期 | 咩嘢 | 點解唔得 | 已補去邊層 |\n|---|---|---|---|\n\n> 「已補去邊層」填唔到，即係今次只執咗份稿冇改到系統，下次會再犯。\n\n## 已知問題\n\n## 下次提醒\n",
    "checklist": "# {{BRAND}} 交付前驗收\n\n## 來源與證據\n- [ ] 每個數據／個案 Claim 有來源（標題／平台／作者／日期／連結）\n- [ ] 冇引用 04-approved-claims.md 以外嘅證據\n- [ ] 冇把同行觀點當成品牌立場\n\n## 品牌\n- [ ] 句長、開場類型、標點習慣對得上 02-voice-profile.md\n- [ ] 稱呼讀者用返固定講法\n- [ ] 冇用禁用詞\n- [ ] 平台規格符合 06-platform-rules.md\n\n## 紅線\n- [ ] <由 BIBLE 紅線逐條複製過嚟>\n\n## 對外一致性\n- [ ] 內容、落地頁、表單、訊息講緊同一件事\n- [ ] CTA 清楚，下一步冇歧義\n- [ ] 連結行得通\n\n## 交付完整性\n- [ ] 文字／圖／caption／CTA／來源齊全\n- [ ] 檔名同路徑符合規範\n",
    "tools": "",
    "queue_dirs": [
      "00-briefs",
      "01-insights",
      "02-drafts",
      "03-approved",
      "04-assets",
      "05-scheduled",
      "06-replies"
    ],
    "agent_labels": {
      "orchestrator": {
        "label": "總監",
        "goal": "派工、驗收、對齊 BIBLE",
        "out": "queue/00-briefs/"
      },
      "research": {
        "label": "研究",
        "goal": "由市場訊號提煉 3–6 個候選角度",
        "out": "queue/01-insights/"
      },
      "content": {
        "label": "文案",
        "goal": "把已批准角度寫成 Master Content 及各平台版本",
        "out": "queue/02-drafts/"
      },
      "qa": {
        "label": "品質",
        "goal": "對照紅線與語氣檔判定可否交人審閱",
        "out": "queue/03-approved/"
      },
      "visual": {
        "label": "視覺",
        "goal": "把已批准內容變成圖卡與素材",
        "out": "queue/04-assets/"
      },
      "video": {
        "label": "影片",
        "goal": "把內容拆成腳本、字幕、封面與延伸卡片",
        "out": "queue/04-assets/"
      },
      "engage": {
        "label": "社群",
        "goal": "分流留言與私訊，草擬回覆",
        "out": "queue/06-replies/"
      },
      "funnel": {
        "label": "轉化",
        "goal": "承接內容到落地頁、表單與名單",
        "out": "queue/05-scheduled/"
      },
      "analytics": {
        "label": "數據",
        "goal": "週度覆盤與下一輪測試建議",
        "out": "reports/"
      }
    }
  }
};
