-- 多租戶工作台 schema。
--
-- R2 存檔案內容（只有文字），D1 存名冊同索引。
-- 索引唔係為咗快 —— 係為咗**唔可以由 URL 直接砌 R2 key**。
-- 讀檔案之前一定要喺 files 表搵到嗰行，否則 ../ 之類就跳得出自己個 slug。

CREATE TABLE IF NOT EXISTS clients (
  slug         TEXT PRIMARY KEY,
  brand        TEXT NOT NULL,
  archetype    TEXT NOT NULL,
  modifiers    TEXT NOT NULL DEFAULT '[]',
  platforms    TEXT NOT NULL DEFAULT '[]',
  skills       TEXT NOT NULL DEFAULT '[]',
  agents       TEXT NOT NULL DEFAULT '[]',
  redlines     TEXT NOT NULL DEFAULT '[]',
  visual       TEXT,
  publish_mode TEXT NOT NULL DEFAULT 'review-only',
  created_at   TEXT NOT NULL
);

-- 邀請碼只存雜湊。原碼生成嗰刻顯示一次，之後任何人（包括你）都攞唔返 ——
-- 資料庫外洩都唔會直接變成登入權。
CREATE TABLE IF NOT EXISTS invites (
  code_hash  TEXT PRIMARY KEY,
  slug       TEXT NOT NULL,
  label      TEXT,
  created_at TEXT NOT NULL,
  revoked    INTEGER NOT NULL DEFAULT 0,
  FOREIGN KEY (slug) REFERENCES clients(slug)
);
CREATE INDEX IF NOT EXISTS idx_invites_slug ON invites(slug);

CREATE TABLE IF NOT EXISTS files (
  slug       TEXT NOT NULL,
  path       TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  PRIMARY KEY (slug, path)
);
