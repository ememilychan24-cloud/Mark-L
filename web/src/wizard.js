// 精靈邏輯。**所有資料嚟自 generated.js（由 Python 匯出），呢度淨係砌。**
// 對應 workbench/wizard.py。改行業表要改 taxonomy.py 再跑 build_web.py。

import { WB } from "./generated.js";

const A_BY_KEY = Object.fromEntries(WB.archetypes.map(a => [a.key, a]));
const M_BY_KEY = Object.fromEntries(WB.modifiers.map(m => [m.key, m]));
export const STEP_KEYS = WB.steps.map(s => s.key);

export function cleanDraft(d = {}) {
  // 未知 id 一律當冇揀過，唔係報錯 —— 唔好信瀏覽器送咩過嚟
  const arr = (v, known) => (Array.isArray(v) ? v : []).filter(x => known.has(x));
  return {
    archetype: A_BY_KEY[d.archetype] ? d.archetype : null,
    modifiers: arr(d.modifiers, new Set(Object.keys(M_BY_KEY))),
    platforms: arr(d.platforms, new Set(Object.keys(WB.platform_labels))),
    skills: arr(d.skills, new Set(Object.keys(WB.skill_labels))),
    brand_name: String(d.brand_name || "").slice(0, 80),
    handles: (Array.isArray(d.handles) ? d.handles : [])
      .map(x => String(x).replace(/^@/, "").slice(0, 40)).filter(Boolean).slice(0, 10),
    visual: (d.visual && typeof d.visual === "object" && !Array.isArray(d.visual))
      ? d.visual : {},
  };
}

export function applyDefaults(d) {
  // 只填空欄位。用戶自己撳過嘅嘢唔可以被預設蓋返。
  const a = A_BY_KEY[d.archetype];
  if (!a) return d;
  if (!d.platforms.length) d.platforms = [...a.platforms];
  if (!d.skills.length) d.skills = [...a.skills];
  return d;
}

// 揀邊樣工作 → 要邊個崗位。用戶唔使識咩叫 agent。
const SKILL_ROLE = {
  "image-gen": "visual", "visual-identity-scan": "visual",
  "comment-triage": "engage", "faq-builder": "engage", "escalation": "engage",
  "booking-funnel": "funnel", "proposal": "funnel", "edm": "funnel",
};

export function derived(d) {
  const a = A_BY_KEY[d.archetype];
  if (!a) return { label: "", pain: "", unlock: "", agents: [], redlines: [], modifiers: [] };
  const mods = d.modifiers.map(k => M_BY_KEY[k]).filter(Boolean);

  const redlines = [...a.redlines];
  for (const m of mods) for (const r of m.redlines) if (!redlines.includes(r)) redlines.push(r);

  const agents = [...WB.core_agents];
  for (const r of a.extra_agents) if (!agents.includes(r)) agents.push(r);
  for (const [skill, role] of Object.entries(SKILL_ROLE)) {
    if (d.skills.includes(skill) && !agents.includes(role) && agents.length < WB.max_agents) {
      agents.push(role);
    }
  }

  return {
    label: a.label, pain: a.pain, unlock: a.unlock, redlines,
    agents: agents.map(r => ({ id: r, ...WB.role_labels[r] })),
    modifiers: mods.map(m => ({ id: m.key, label: m.label, why: m.why, n: m.redlines.length })),
  };
}

const FIELD = { industry: "archetype", confirm: "modifiers", platforms: "platforms", jobs: "skills" };
export { FIELD };

export function options(step, d) {
  const idx = STEP_KEYS.indexOf(step);
  if (idx < 0) return null;
  const out = {
    step, index: idx, total: STEP_KEYS.length, title: WB.steps[idx].title,
    choices: [], multi: false, can_advance: true, note: "", sub: "",
  };
  const dv = derived(d);

  if (step === "industry") {
    out.sub = "撳一個最似你嘅。揀錯咗之後改得返。";
    out.choices = WB.archetypes.map(a => ({
      id: a.key, label: a.label, hint: a.pain.split("。")[0] + "。",
      selected: d.archetype === a.key, locked: false, why: "",
    }));
    out.can_advance = !!d.archetype;
    if (!d.archetype) out.note = "揀一個先可以繼續。";

  } else if (step === "confirm") {
    out.sub = "呢啲係跟住你個行業自動配好嘅。唔啱就撳走。";
    out.multi = true;
    const auto = new Set(dv.modifiers.map(m => m.id));
    out.choices = WB.modifiers.map(m => ({
      id: m.key, label: m.label,
      hint: `${m.why}（＋${m.redlines.length} 條紅線）`,
      selected: d.modifiers.includes(m.key), locked: false,
      why: auto.has(m.key) ? "由你嘅行業偵測到" : "",
    }));
    out.derived = dv;
    out.note = "呢啲叫「合規修飾」—— 講錯呢幾類嘢係要負責任嘅，所以工作台會逐條攔住。冇關嘅可以撳走。";

  } else if (step === "platforms") {
    out.sub = "已經幫你揀咗常用嗰幾個。加減都得。";
    out.multi = true;
    const order = [...d.platforms, ...Object.keys(WB.platform_labels).filter(k => !d.platforms.includes(k))];
    out.choices = order.map(p => ({
      id: p, ...WB.platform_labels[p], selected: d.platforms.includes(p), locked: false, why: "",
    }));
    out.can_advance = d.platforms.length > 0;
    if (!out.can_advance) out.note = "至少揀一個。";

  } else if (step === "jobs") {
    out.sub = "已經按你個行業揀好。想加想減都得 —— 揀嘅嘢會決定請幾多個崗位。";
    out.multi = true;
    const a = A_BY_KEY[d.archetype];
    const rec = new Set(a ? a.skills : []);
    const order = [...d.skills, ...Object.keys(WB.skill_labels).filter(k => !d.skills.includes(k))];
    out.choices = order.map(s => {
      const L = WB.skill_labels[s];
      return {
        id: s, label: L.label, hint: L.hint,
        selected: d.skills.includes(s), locked: L.core,
        why: L.core ? "呢個係基本盤，冇咗就唔係一個工作台"
                    : (rec.has(s) ? "你個行業通常都要" : ""),
      };
    });
    out.derived = dv;

  } else if (step === "visual") {
    out.sub = "掉幾張你出過嘅圖入嚟，工作台會自己讀返你嘅顏色。唔想做可以直接跳過。";
    out.visual = d.visual;
    out.handles = d.handles;
    out.note = "啲圖唔會離開你部機 —— 分析喺你個瀏覽器度做，只有算出嚟嘅色碼會上傳。";

  } else if (step === "review") {
    out.sub = "撳落去就會開好呢個客嘅工作台。";
    out.derived = dv;
    out.summary = {
      brand: d.brand_name || (d.handles[0] ? "@" + d.handles[0] : "（未改名）"),
      archetype: dv.label,
      platforms: d.platforms.map(p => WB.platform_labels[p].label),
      skills: d.skills.map(s => WB.skill_labels[s].label),
      agents: dv.agents, redlines: dv.redlines,
      palette: d.visual.palette || [], handles: d.handles,
    };
    out.can_advance = !!(d.archetype && d.platforms.length);
  }
  return out;
}

export function slugify(name) {
  // 中文字要保留 —— 淨係留 a-z0-9 嘅話，「陳記茶餐廳」「日日鮮」會全部塌落 "client"，
  // 第二個客就會寫入第一個客個位。同 workbench/taxonomy.py 一樣嘅規則。
  const s = String(name || "").trim().toLowerCase()
    .replace(/[^a-z0-9㐀-䶿一-鿿豈-﫿]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return s || "client";
}
