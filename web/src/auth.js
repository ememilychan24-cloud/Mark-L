// 認證同隔離。
//
// 呢個檔案入面得一條規矩係唔可以錯嘅：**一個客戶只可以見到自己嘅 slug。**
// 所以隔離check寫成一個 helper（`guard`），每條掂到客戶資料嘅 route 都要行過佢。
// 唔好喺 route 裡面逐個手寫 if —— 手寫嘅遲早會漏一個，而漏嗰個唔會報錯，
// 只會令 A 客見到 B 客嘅同意書。

const enc = new TextEncoder();

async function hmac(secret, msg) {
  const key = await crypto.subtle.importKey(
    "raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", key, enc.encode(msg));
  return b64url(new Uint8Array(sig));
}

export async function sha256(s) {
  const buf = await crypto.subtle.digest("SHA-256", enc.encode(s));
  return [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, "0")).join("");
}

function b64url(bytes) {
  return btoa(String.fromCharCode(...bytes))
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

// 時間恆定比較 —— 用 === 比 HMAC 會洩漏長度同前綴資訊
function sameSig(a, b) {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

const DAYS_14 = 14 * 24 * 3600;

export async function issue(env, role, slug) {
  const exp = Math.floor(Date.now() / 1000) + DAYS_14;
  const payload = `${role}|${slug || ""}|${exp}`;
  return `${payload}|${await hmac(env.SESSION_SECRET, payload)}`;
}

export async function readSession(env, request) {
  const cookie = request.headers.get("Cookie") || "";
  const m = cookie.match(/(?:^|;\s*)wb=([^;]+)/);
  if (!m) return null;
  const token = decodeURIComponent(m[1]);
  const parts = token.split("|");
  if (parts.length !== 4) return null;
  const [role, slug, exp, sig] = parts;
  if (!sameSig(sig, await hmac(env.SESSION_SECRET, `${role}|${slug}|${exp}`))) return null;
  if (Number(exp) * 1000 < Date.now()) return null;
  return { role, slug: slug || null };
}

export function cookieHeader(token, maxAge = DAYS_14) {
  // HttpOnly：JS 攞唔到，XSS 就偷唔到 session
  // SameSite=Strict：唔會跟住第三方網站嘅 request 送出去
  return `wb=${encodeURIComponent(token)}; HttpOnly; Secure; SameSite=Strict; ` +
         `Path=/; Max-Age=${maxAge}`;
}

/**
 * 隔離check。**每條掂到客戶資料嘅 route 都要行過呢度。**
 *
 * owner  → 見到全部
 * client → 只見到自己嗰個 slug，其他一律當「唔存在」（404，唔係 403）
 *
 * 用 404 唔用 403 係故意嘅：403 等於話「呢個客係存在嘅，但你冇權」，
 * 咁樣一個客戶就可以逐個試 slug 去查出你有邊啲客。404 咩都唔講。
 */
export function guard(session, slug) {
  if (!session) return { ok: false, status: 401, error: "未登入" };
  if (session.role === "owner") return { ok: true };
  if (slug && session.slug === slug) return { ok: true };
  return { ok: false, status: 404, error: "搵唔到" };
}

export function ownerOnly(session) {
  if (!session) return { ok: false, status: 401, error: "未登入" };
  if (session.role !== "owner") return { ok: false, status: 404, error: "搵唔到" };
  return { ok: true };
}
