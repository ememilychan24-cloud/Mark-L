// 多租戶工作台 Worker。
//
// 資料放喺邊：
//   D1  — 客戶名冊、邀請碼（雜湊）、檔案索引
//   R2  — 工作台檔案內容（**淨係文字**）
//
// **服務器唔會收任何圖片。** 冇上載圖片嘅端點，寫入時只接受文字。
// 呢個唔係漏做 —— 呢個工作台服務嘅客入面，參考圖有啲係客人身體。
// 分析喺瀏覽器度做，只有算出嚟嘅色碼會上嚟。咁樣托管方（你）就唔會
// 保管到人哋嘅身體相，責任細一大截。

import { cookieHeader, guard, issue, ownerOnly, readSession, sha256 } from "./auth.js";
import { buildTree } from "./scaffold.js";
import { applyDefaults, cleanDraft, options, slugify, derived } from "./wizard.js";

const json = (data, status = 200, headers = {}) =>
  new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store", ...headers },
  });

const fail = (g) => json({ error: g.error }, g.status);

// 只接受文字路徑 —— 冇二進位檔案入得嚟
const TEXT_EXT = /\.(md|json|txt|csv|gitkeep)$|\/\.gitkeep$/;

async function listClients(env, session) {
  const owner = session.role === "owner";
  const q = owner
    ? env.DB.prepare("SELECT * FROM clients ORDER BY created_at DESC")
    : env.DB.prepare("SELECT * FROM clients WHERE slug = ?").bind(session.slug);
  const { results } = await q.all();
  return (results || []).map(r => ({
    slug: r.slug, brand: r.brand, archetype: r.archetype,
    modifiers: JSON.parse(r.modifiers), platforms: JSON.parse(r.platforms),
    agents: JSON.parse(r.agents), redlines: JSON.parse(r.redlines),
    visual: r.visual ? JSON.parse(r.visual) : {},
    publish_mode: r.publish_mode, created_at: r.created_at,
  }));
}

// 狀態同本機版一樣：由實際存喺度嘅嘢推導，唔另存一份。
function clientState(c, fileCount) {
  const blockers = [];
  const visualConf = c.visual && c.visual.n
    ? (c.visual.n >= 20 ? "高" : c.visual.n >= 8 ? "中" : "低") : "未建立";

  blockers.push({
    key: "no-claims", severity: "block", owner: "client",
    what: "已批准主張／證據係空",
    consequence: "所有稿都唔可以出任何數字、個案、資格認證 —— 出咗就係無出處嘅宣稱。",
    fix: "交有書面同意嘅個案、有出處嘅數據、證書掃描件。",
  });
  if (visualConf === "未建立") {
    blockers.push({
      key: "visual-unset", severity: "block", owner: "client",
      what: "品牌視覺未建立",
      consequence: "生圖模型會自己加漸變、金色點綴、bokeh —— 出嚟唔似品牌。",
      fix: "喺設定精靈第 5 步掉 20 張已出街嘅圖入去。",
    });
  }
  const hard = blockers.filter(b => b.severity === "block");
  return {
    ...c, visual_confidence: visualConf, voice_confidence: "待評估",
    files: fileCount, blockers,
    // 全新開嘅客缺料係正常，唔應該亮紅燈；有嘢出唔到街先係阻塞。
    health: "setup",
    next_action: hard.length ? `客戶：${hard[0].fix}` : "可以開新一輪選題",
  };
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const p = url.pathname;

    if (!env.SESSION_SECRET || !env.OWNER_KEY) {
      return json({ error: "未設定 SESSION_SECRET / OWNER_KEY。見 web/README.md。" }, 500);
    }

    // ── 靜態頁面交返俾 assets binding ──
    if (!p.startsWith("/api/")) return env.ASSETS.fetch(request);

    const session = await readSession(env, request);
    let body = {};
    if (request.method === "POST") {
      try { body = await request.json(); } catch { body = {}; }
    }

    // ── 登入 ──
    if (p === "/api/login" && request.method === "POST") {
      const code = String(body.code || "").trim();
      if (!code) return json({ error: "請輸入通行碼" }, 400);

      if (code === env.OWNER_KEY) {
        return json({ role: "owner" }, 200, { "Set-Cookie": cookieHeader(await issue(env, "owner", "")) });
      }
      const row = await env.DB.prepare(
        "SELECT slug FROM invites WHERE code_hash = ? AND revoked = 0"
      ).bind(await sha256(code)).first();
      if (!row) return json({ error: "通行碼唔啱，或者已經被撤銷。" }, 401);

      return json({ role: "client", slug: row.slug }, 200,
        { "Set-Cookie": cookieHeader(await issue(env, "client", row.slug)) });
    }

    if (p === "/api/logout" && request.method === "POST") {
      return json({ ok: true }, 200, { "Set-Cookie": cookieHeader("", 0) });
    }

    if (p === "/api/me") {
      if (!session) return json({ role: null }, 200);
      return json({ role: session.role, slug: session.slug });
    }

    // ── 以下全部要登入 ──
    if (!session) return json({ error: "未登入" }, 401);

    // ── 精靈：開新客係代理商嘅工作 ──
    if (p === "/api/wizard/options" && request.method === "POST") {
      const g = ownerOnly(session); if (!g.ok) return fail(g);
      const d = applyDefaults(cleanDraft(body.draft));
      const o = options(String(body.step || "industry"), d);
      if (!o) return json({ error: "未知步驟" }, 400);
      return json({ options: o, draft: d });
    }

    if (p === "/api/clients" && request.method === "POST") {
      const g = ownerOnly(session); if (!g.ok) return fail(g);
      const d = applyDefaults(cleanDraft(body.draft));
      if (!d.archetype) return json({ error: "未揀行業" }, 400);
      if (!d.platforms.length) return json({ error: "未揀平台" }, 400);

      const slug = slugify(d.handles[0] || d.brand_name || d.archetype);

      // 撞名就停手。兩個客用同一個 slug，紅線同證據會撈埋一齊，而且冇錯誤訊息。
      const exists = await env.DB.prepare("SELECT slug FROM clients WHERE slug = ?").bind(slug).first();
      if (exists) {
        return json({ error: `已經有一個客叫「${slug}」。改個唔同嘅品牌名或者帳號再試。` }, 409);
      }

      const { files, dv, brand, agents } = buildTree(d);
      const now = new Date().toISOString();

      // 寫 R2（只有文字），再寫索引
      const stmts = [];
      for (const [path, content] of Object.entries(files)) {
        if (!TEXT_EXT.test(path)) continue;          // 防手抖：非文字一律唔寫
        await env.FILES.put(`${slug}/${path}`, content, {
          httpMetadata: { contentType: "text/markdown; charset=utf-8" },
        });
        stmts.push(env.DB.prepare(
          "INSERT OR REPLACE INTO files (slug, path, updated_at) VALUES (?, ?, ?)"
        ).bind(slug, path, now));
      }
      stmts.unshift(env.DB.prepare(
        `INSERT INTO clients (slug, brand, archetype, modifiers, platforms, skills,
           agents, redlines, visual, publish_mode, created_at)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'review-only', ?)`
      ).bind(slug, brand, d.archetype, JSON.stringify(d.modifiers),
        JSON.stringify(d.platforms), JSON.stringify(d.skills), JSON.stringify(agents),
        JSON.stringify(dv.redlines), JSON.stringify(d.visual), now));
      await env.DB.batch(stmts);

      return json({
        slug, brand, agents: agents.length, redlines: dv.redlines.length,
        files: Object.keys(files).length, visual: !!d.visual.n,
        still_needed: [
          "已批准證據（證書、個案、數據）—— 冇呢個，所有稿都唔可以落數字",
          "真實客戶查詢紀錄 —— 冇呢個，內容會用你嘅講法而唔係客人嘅講法",
        ],
      });
    }

    if (p === "/api/clients" && request.method === "GET") {
      const rows = await listClients(env, session);
      const out = [];
      for (const c of rows) {
        const { results } = await env.DB.prepare(
          "SELECT COUNT(*) AS n FROM files WHERE slug = ?").bind(c.slug).all();
        out.push(clientState(c, results[0].n));
      }
      return json({
        role: session.role, clients: out,
        totals: { clients: out.length, blocked: out.filter(c => c.health === "blocked").length },
      });
    }

    // ── 單一客戶：檔案清單同內容 ──
    const mFiles = p.match(/^\/api\/clients\/([^/]+)\/files$/);
    if (mFiles) {
      const slug = decodeURIComponent(mFiles[1]);
      const g = guard(session, slug); if (!g.ok) return fail(g);
      const { results } = await env.DB.prepare(
        "SELECT path, updated_at FROM files WHERE slug = ? ORDER BY path").bind(slug).all();
      if (!results.length) return json({ error: "搵唔到" }, 404);
      return json({ slug, files: results });
    }

    const mFile = p.match(/^\/api\/clients\/([^/]+)\/file$/);
    if (mFile) {
      const slug = decodeURIComponent(mFile[1]);
      const g = guard(session, slug); if (!g.ok) return fail(g);
      const path = url.searchParams.get("path") || "";
      // 路徑一定要喺索引入面出現過 —— 唔可以由 query 直接砌 R2 key，
      // 否則 ../ 之類就可以跳出自己個 slug
      const row = await env.DB.prepare(
        "SELECT path FROM files WHERE slug = ? AND path = ?").bind(slug, path).first();
      if (!row) return json({ error: "搵唔到" }, 404);
      const obj = await env.FILES.get(`${slug}/${path}`);
      if (!obj) return json({ error: "搵唔到" }, 404);
      return new Response(await obj.text(), {
        headers: { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "no-store" },
      });
    }

    // ── 邀請碼：owner 生成，客戶用嚟登入 ──
    if (p === "/api/invites" && request.method === "POST") {
      const g = ownerOnly(session); if (!g.ok) return fail(g);
      const slug = String(body.slug || "");
      const c = await env.DB.prepare("SELECT slug FROM clients WHERE slug = ?").bind(slug).first();
      if (!c) return json({ error: "搵唔到呢個客" }, 404);

      // 隨機碼。**只喺呢一刻回一次**，之後淨係存雜湊 —— 撳失咗就重新生成一個。
      const raw = crypto.getRandomValues(new Uint8Array(15));
      const code = btoa(String.fromCharCode(...raw)).replace(/[+/=]/g, "").slice(0, 16);
      await env.DB.prepare(
        "INSERT INTO invites (code_hash, slug, label, created_at, revoked) VALUES (?, ?, ?, ?, 0)"
      ).bind(await sha256(code), slug, String(body.label || ""), new Date().toISOString()).run();
      return json({ code, slug, note: "呢個碼只顯示呢一次。存低咗先關窗。" });
    }

    if (p === "/api/invites" && request.method === "GET") {
      const g = ownerOnly(session); if (!g.ok) return fail(g);
      const { results } = await env.DB.prepare(
        "SELECT slug, label, created_at, revoked FROM invites ORDER BY created_at DESC").all();
      return json({ invites: results || [] });
    }

    return json({ error: "搵唔到" }, 404);
  },
};
