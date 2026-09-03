// 由選擇砌出成個 workspace 檔案樹。
// 所有範本嚟自 generated.js（由 Python 嘅 scaffold.py 生成），呢度淨係填位。

import { WB } from "./generated.js";
import { derived } from "./wizard.js";

const T = WB.tpl;

function fill(tpl, brand, platforms, today = "") {
  return tpl
    .replaceAll("{{BRAND}}", brand)
    .replaceAll("{{PLATFORMS}}", platforms.join("、") || "（未指定）")
    // {{DATE}} 係建立嗰刻嘅日期，唔係建置日期 —— 見 scripts/build_web.py
    .replaceAll("{{DATE}}", today);
}

// 同 pipeline.inject_redlines 一樣：按**形狀**搵 placeholder，唔按字面。
// 字面比對兩邊各寫死一次，改咗一邊另一邊就靜靜雞搵唔到，紅線會變成零條而唔報錯。
const PLACEHOLDER = /^- \[ \] <[^>]*>$/m;

export function buildTree(d) {
  const dv = derived(d);
  const brand = d.brand_name || (d.handles[0] ? "@" + d.handles[0] : "未命名品牌");
  const today = new Date().toISOString().slice(0, 10);
  const agents = dv.agents.map(a => a.id);
  const files = {};

  // ── 品牌憲法 ──
  let bible = fill(T.bible, brand, d.platforms, today)
    .replaceAll("{{ARCHETYPE}}", d.archetype);
  const rl = dv.redlines.length
    ? dv.redlines.map(r => `- [ ] ${r}`).join("\n")
    : "- [ ] <呢個行業冇預設紅線 —— 開工前要同客戶逐條問返出嚟>";
  if (PLACEHOLDER.test(bible)) bible = bible.replace(PLACEHOLDER, rl);
  files["brand/BIBLE.md"] = bible;

  // ── Brand Brain 01–08 ──
  for (const b of T.brain) {
    files[`brand/brain/${b.file}`] = b.may_empty
      ? `# ${b.num} · ${b.title}\n\n` + T.empty_notice.replace("{how}", b.how)
      : `# ${b.num} · ${b.title}\n\n<${b.what}>\n\n` +
        "> 由步驟 3–4 填。留白等於冇資料，agent 會自己補 —— 所以寧願寫「未建立」。\n";
  }

  files["brand/MEMORY.md"] = T.memory;
  files["CHECKLIST.md"] = fill(T.checklist, brand, d.platforms, today);

  // ── 每個崗位一份工作說明 ──
  for (const role of agents) {
    if (T.agents[role]) files[`agents/${role}/AGENTS.md`] = fill(T.agents[role], brand, d.platforms, today);
  }

  // ── 佇列（空目錄用 .gitkeep 佔位）──
  for (const q of T.queue_dirs) files[`queue/${q}/.gitkeep`] = "";

  // ── 品牌視覺 ──
  files["style/brand-visual.md"] = brandVisual(d.visual, d.handles, today);

  // ── present 用嗰頁 ──
  files["pitch.md"] = [
    `# ${brand} — 點解要呢個工作台`, "",
    `> 行業：${dv.label} · 合規：${dv.modifiers.map(m => m.label).join("、") || "冇特別合規要求"}`,
    `> 生成日期：${today}`, "",
    "## 你而家嘅情況", dv.pain, "",
    "## 工作台拆開咗咩", dv.unlock, "",
    "## 具體會點運作",
    `- **${agents.length} 個 AI 崗位**：${dv.agents.map(a => a.label).join("、")}。` +
      "分工按交付物切，唔按平台切 —— 一個「小紅書 agent」會同時做策略、文案、圖同回覆，錯咗你查唔到係邊一環出事。",
    `- **${d.platforms.length} 個平台**：同一個觀點喺每個平台重新寫過 hook 同節奏，唔係複製貼上改幾隻字。`,
    `- **${dv.redlines.length} 條紅線**寫死喺品牌憲法入面，每篇稿機械式檢查，違反即退回。`,
    "- **兩個人手關卡**：品牌知識庫生成之後審一次，出街之前審一次。中間全部自動。", "",
    "## 頭一個月唔會做嘅嘢",
    "唔會開自動發布。第一個月全部只排到待審，你逐篇睇。品牌信任冇得回頭，慳嗰十分鐘唔值。", "",
    "## 呢個工作台唔會幫你做嘅嘢",
    "- 唔會幫你決定生意策略 —— 佢執行你嘅定位，唔會發明一個",
    "- 冇證據就唔會寫數字同個案，寧願交白卷",
    "- 唔會扮你未有嘅資歷", "",
  ].join("\n");

  // ── 生成報告：邊啲係事實、邊啲仲未做 ──
  const gaps = [];
  if (!d.visual.n) gaps.push("未交過參考圖 —— 品牌視覺係空，未可以生圖。");
  if (!d.handles.length) gaps.push("冇帳號 —— 爬唔到現有內容，語氣檔會係空嘅。");
  files["run-report.md"] = [
    `# 生成報告 — ${brand}`, "", `生成日期：${today}`, "",
    "## 判斷同根據", "| 項目 | 結果 | 根據 |", "|---|---|---|",
    `| 行業 | \`${d.archetype}\`（${dv.label}） | 由設定精靈人手揀，唔係推斷 |`,
    ...dv.modifiers.map(m => `| 合規 | \`${m.id}\`（${m.label}） | 由設定精靈確認 |`),
    `| 平台 | ${d.platforms.join(", ")} | 由設定精靈人手揀 |`,
    `| 帳號 | ${d.handles.map(h => "@" + h).join(", ") || "（冇）"} | 由設定精靈填 |`,
    `| 員工編制 | ${agents.join(", ")} | 由行業同揀咗嘅工作推導，上限 ${WB.max_agents} |`,
    "", "## 紅線（已寫入 BIBLE.md）",
    ...dv.redlines.map(r => `- ${r}`), "",
    "## 未確認 / 仲未做",
    ...(gaps.length ? gaps.map(g => `- ${g}`) : ["- （冇）"]),
    "- 未爬過任何公開內容 —— 語氣檔係空殼",
    "- 未有已批准證據 —— 所有稿都唔可以落數字或個案", "",
    "> 呢啲做完之前，工作台可以行，但出嚟嘅嘢淨係啱格式，唔會啱品牌。", "",
  ].join("\n");

  files["config/schedule.md"] = [
    "# 排程", "", "## 本月模式：**只排到待審**",
    "第一個月唔開全自動發布。品牌信任冇得回頭，慳嗰十分鐘唔值。",
    "第二個月抽三成審，穩定之後只審新題材。", "",
    "## 每週節奏", "| 日 | 做咩 |", "|---|---|",
    "| 一 | 出選題 |", "| 二 | 人揀主角度 |", "| 三 | 文案交稿 → 品質檢查 |",
    "| 四 | 視覺 ＋ 待審 |", "| 五 | 覆盤 |", "",
    "## 規則",
    "- 每平台每日唔好超過 1 條（Threads 除外）",
    "- 唔好所有平台同日出同一內容 —— 次要平台跟主場後 1–2 日", "",
  ].join("\n");

  return { files, dv, brand, agents };
}

// ── 品牌視覺：由瀏覽器算返嚟嘅數字寫成檔案 ──
// 對應 workbench/visual.py。色相一定要用角度算，唔可以比 R/G/B 邊個大 ——
// 之前咁做令琥珀色 #E8A530 被判做紅，「從來冇出現」欄就會叫生圖模型
// 避開品牌自己嘅強調色。
const HUES = ["紅／粉", "黃／橙", "綠", "藍／紫"];

export function hueOf(hex) {
  const h = hex.replace("#", "");
  const r = parseInt(h.slice(0, 2), 16), g = parseInt(h.slice(2, 4), 16), b = parseInt(h.slice(4, 6), 16);
  const mx = Math.max(r, g, b), mn = Math.min(r, g, b), dd = mx - mn;
  if (dd < 25) return null;                       // 近乎中性色
  let hue;
  if (mx === r) hue = ((60 * ((g - b) / dd)) % 360 + 360) % 360;
  else if (mx === g) hue = 60 * (2 + (b - r) / dd);
  else hue = 60 * (4 + (r - g) / dd);
  if (hue < 20 || hue >= 330) return "紅／粉";
  if (hue < 70) return "黃／橙";
  if (hue < 165) return "綠";
  return "藍／紫";
}

const COMMON_ADDITIONS = ["漸變", "金色點綴", "bokeh 散景", "光暈", "閃粉", "純黑背景"];

export function brandVisual(v = {}, handles = [], today = "") {
  const n = Number(v.n || 0);
  const pal = Array.isArray(v.palette) ? v.palette : [];
  const hexes = pal.map(p => p.hex).filter(Boolean);

  let conf, why;
  if (!n) { conf = "未建立"; why = "未有參考圖。"; }
  else if (n < 8) { conf = "低"; why = `只有 ${n} 張圖，統計意義有限。`; }
  else if (n < 20) { conf = "中"; why = `${n} 張圖。夠睇到大方向，但排版同字級仲要人手確認。`; }
  else { conf = "高"; why = `${n} 張圖，色彩分佈已經穩定。`; }

  const seen = new Set(hexes.map(hueOf).filter(Boolean));
  const missing = HUES.filter(h => !seen.has(h));
  const never = [...missing.map(m => m + " 色系"), ...COMMON_ADDITIONS];

  const light = Number(v.light || 0), sat = Number(v.sat || 0);
  const portrait = Number(v.portrait || 0), edge = Number(v.edge || 0);
  const warmth = !seen.size ? "全部中性色，冇明顯色相"
    : (!seen.has("藍／紫") ? "全部暖色 —— 冷色（藍／紫）從來冇出現過"
      : (seen.size === 1 ? "全部冷色 —— 暖色從來冇出現過" : "冷暖都有"));

  const L = [
    "# 品牌視覺 Brand Visual", "",
    `> 樣本：${n} 張 · 信心度：**${conf}** — ${why}`,
    "> 喺瀏覽器分析。**原圖冇離開過用戶部機，冇上載過**，只有色碼存低。",
    `> 更新：${today}`, "", "## 色彩",
  ];
  if (pal.length) {
    const roles = ["主色", "輔色", "強調色", "次要色", "次要色", "次要色"];
    pal.slice(0, 6).forEach((p, i) =>
      L.push(`- ${roles[i]}：\`${p.hex}\`（出現佔比 ${Math.round((p.share || 0) * 100)}%）`));
    L.push(`- 冷暖：${warmth}`);
  } else {
    L.push("- <未有參考圖，要人手填>");
  }
  L.push("",
    "- **從來冇出現**（呢欄最重要）：" + never.join("、"),
    "  → 冇寫低呢一欄，生圖模型會自己加。呢個係「生成出嚟唔似品牌」嘅頭號原因。",
    "", "## 畫風",
    `- 光線：${light > .66 ? "偏光、通透" : light < .38 ? "偏暗、沉穩" : "中間調"}（平均亮度 ${Math.round(light * 100)}/100）`,
    `- 色彩濃度：${sat < .22 ? "低飽和、素淨" : sat > .5 ? "高飽和、鮮明" : "中等飽和"}（${Math.round(sat * 100)}/100）`,
    `- 構圖比例：${portrait > .65 ? "以直度圖為主" : portrait < .35 ? "以橫度圖為主" : "直橫都有"}（直度圖 ${Math.round(portrait * 100)}%）`,
    `- 資訊密度：${edge < .09 ? "留白多，圖入面文字少" : edge > .18 ? "資訊密度高，字多" : "中等密度"}`,
    "- 攝影 / 插畫比例：<要人手睇一眼填>",
    "- 主體處理：<要人手填 —— 例如「一定唔露樣」、「只影產品唔影人」>",
    "", "## 排版",
    "- 字體：<要人手填>",
    `- 每張圖文字量：${edge < .09 ? "少（≤ 15 字）" : edge > .18 ? "多（30 字以上）" : "中等（15–25 字）"}`,
    "", "## ⚠️ 呢幾樣機器讀唔到，一定要人答",
    "- 有冇官方品牌指引？（如有，覆蓋以上全部觀察）",
    "- Logo 使用規則同安全距離",
    "- 身體／人物入鏡嘅界線（邊個部位可以影、要唔要露樣）", "");
  if (handles.length) {
    L.push("## 參考帳號（未爬取）",
      ...handles.map(h => `- @${h} —— 記錄低咗，但**未爬過**。工作台唔會自動登入去攞你嘅帖。`), "");
  }
  return L.join("\n");
}
