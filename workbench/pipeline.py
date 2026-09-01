#!/usr/bin/env python3
"""
一句話 → 可以開工嘅 client workspace。

呢個檔案唔重新實作 scaffold —— 佢調用 skill 入面嗰支，然後做三件 scaffold 做唔到嘅嘢：
  1. 把行業同合規紅線**寫死**入 BIBLE（scaffold 只識通用嗰幾條）
  2. 寫一份 pitch.md：呢個客嘅流程塞喺邊、工作台拆開咗咩。present 嗰陣就係讀呢頁。
  3. 寫一份 run-report.md：邊啲嘢係推斷、邊啲係確認、邊啲仲爭緊。

第 3 點最容易被跳過，亦係最重要 —— 一個睇落完整但係靠估砌出嚟嘅工作台，
比一個明顯未做完嘅工作台危險，因為冇人會再去 review。
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

from .taxonomy import Brief, classify, slugify

SKILL_DIR = Path(__file__).resolve().parent.parent / ".claude" / "skills" / "brand-workspace-factory"
SCAFFOLD = SKILL_DIR / "scripts" / "scaffold.py"


def run_scaffold(root: Path, slug: str, b: Brief, force: bool = False) -> str:
    if not SCAFFOLD.is_file():
        raise SystemExit(f"搵唔到 scaffold.py：{SCAFFOLD}")
    cmd = [
        sys.executable, str(SCAFFOLD),
        "--root", str(root),
        "--client", slug,
        "--name", b.brand_name or slug,
        "--archetype", b.archetype.key,
        "--modifiers", ",".join(m.key for m in b.modifiers),
        "--agents", ",".join(b.agents),
        "--platforms", ",".join(b.platforms),
        "--skills", ",".join(b.skills),
    ]
    if force:
        cmd.append("--force")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"scaffold 失敗：\n{r.stderr}")
    return r.stdout


def inject_redlines(cdir: Path, b: Brief) -> int:
    """把行業／合規紅線寫入 BIBLE，取代 scaffold 嗰行 placeholder。

    紅線唔可以只留喺 reference 檔 —— agent 讀嘅係 BIBLE，唔會自己去揭 reference。
    """
    bible = cdir / "brand" / "BIBLE.md"
    if not bible.is_file():
        return 0
    text = bible.read_text(encoding="utf-8")
    placeholder = "- [ ] <由 archetype 生成>"
    lines = [f"- [ ] {r}" for r in b.redlines]
    if not lines:
        lines = ["- [ ] <呢個行業冇預設紅線 —— 開工前要同客戶逐條問返出嚟>"]
    if placeholder in text:
        text = text.replace(placeholder, "\n".join(lines), 1)
    elif "## 紅線" in text:
        return 0  # 已經填過，唔好重複塞
    bible.write_text(text, encoding="utf-8")
    return len(lines)


def write_pitch(cdir: Path, b: Brief) -> None:
    """present 用嗰頁。講客戶嘅問題，唔好講我哋嘅功能。"""
    a = b.archetype
    who = b.brand_name or cdir.name
    mods = "、".join(m.label for m in b.modifiers) or "冇特別合規要求"
    p = [
        f"# {who} — 點解要呢個工作台",
        "",
        f"> 行業：{a.label} · 合規：{mods}",
        f"> 生成日期：{date.today().isoformat()}",
        "",
        "## 你而家嘅情況",
        a.pain,
        "",
        "## 工作台拆開咗咩",
        a.unlock,
        "",
        "## 具體會點運作",
        f"- **{len(b.agents)} 個 AI 崗位**：{'、'.join(b.agents)}。分工按交付物切，唔按平台切 ——"
        "一個「小紅書 agent」會同時做策略、文案、圖同回覆，錯咗你查唔到係邊一環出事。",
        f"- **{len(b.platforms)} 個平台**：{'、'.join(b.platforms)}。同一個觀點喺每個平台重新寫過 hook 同節奏，"
        "唔係複製貼上改幾隻字。",
        f"- **{len(b.redlines)} 條紅線**寫死喺品牌憲法入面，每篇稿機械式檢查，違反即退回。",
        "- **兩個人手關卡**：品牌知識庫生成之後審一次，出街之前審一次。中間全部自動。",
        "",
        "## 頭一個月唔會做嘅嘢",
        "唔會開自動發布。第一個月全部只排到待審，你逐篇睇。",
        "第二個月抽三成審，穩定咗之後只審新題材。",
        "品牌信任冇得回頭，慳嗰十分鐘唔值。",
        "",
        "## 呢個工作台唔會幫你做嘅嘢",
        "- 唔會幫你決定生意策略 —— 佢執行你嘅定位，唔會發明一個",
        "- 冇證據就唔會寫數字同個案，寧願交白卷",
        "- 唔會扮你未有嘅資歷",
        "",
    ]
    if b.ambiguous:
        p += ["## ⚠️ 呢頁有啲嘢係推斷出嚟", *[f"- {x}" for x in b.ambiguous], ""]
    (cdir / "pitch.md").write_text("\n".join(p), encoding="utf-8")


def write_run_report(cdir: Path, b: Brief, scaffold_out: str) -> None:
    """邊啲係事實、邊啲係推斷。呢頁係之後 debug 嘅唯一線索。"""
    r = [
        f"# 生成報告 — {cdir.name}",
        "",
        f"生成日期：{date.today().isoformat()}",
        "",
        "## 輸入（原話）",
        "```",
        b.raw,
        "```",
        "",
        "## 判斷同根據",
        "| 項目 | 結果 | 根據 |",
        "|---|---|---|",
        f"| 行業 | `{b.archetype.key}`（{b.archetype.label}） | {b.evidence.get('archetype', '**冇根據 —— 用咗預設**')} |",
    ]
    for m in b.modifiers:
        r.append(f"| 合規 | `{m.key}`（{m.label}） | {b.evidence.get('modifier:' + m.key, '')} |")
    if not b.modifiers:
        r.append("| 合規 | 冇 | 句子入面冇命中任何受規管字眼 |")
    r += [
        f"| 平台 | {', '.join(b.platforms)} | {b.evidence.get('platforms', '')} |",
        f"| 帳號 | {', '.join('@' + h for h in b.handles) or '（冇）'} | 由句子抽取 |",
        f"| 網址 | {', '.join(b.sites) or '（冇）'} | 由句子抽取 |",
        f"| 員工編制 | {', '.join(b.agents)} | 由 archetype 推導，上限 8 |",
        "",
        "## 紅線（已寫入 BIBLE.md）",
    ]
    r += [f"- {x}" for x in b.redlines] or ["（冇）"]
    r += [
        "",
        "## 未確認 / 靠推斷",
    ]
    r += [f"- {x}" for x in b.ambiguous] or ["- （冇。所有判斷都有句子入面嘅直接根據。）"]
    r += [
        "",
        "## 呢一刻仲未做嘅嘢",
        "- 未爬過任何公開內容 —— 語氣檔係空殼",
        "- 未有已批准證據 —— 所有稿都唔可以落數字或個案",
        "- 未建立品牌視覺 —— 未可以生圖",
        "",
        "> 呢三樣做完之前，工作台可以行，但出嚟嘅嘢淨係啱格式，唔會啱品牌。",
        "",
        "## scaffold 輸出",
        "```",
        scaffold_out.strip(),
        "```",
        "",
    ]
    (cdir / "run-report.md").write_text("\n".join(r), encoding="utf-8")


def onboard_brief(root: Path, b: Brief, slug: str | None = None,
                  force: bool = False) -> tuple[Path, Brief]:
    """由一份**已經定咗**嘅 Brief 生成工作台。

    設定精靈行呢條路：用戶撳出嚟嘅選擇就係最終答案，唔應該再拎去分類器估一次
    （估出嚟同佢撳嘅唔同，就會出現「我明明揀咗 A，點解出咗 B」）。
    `onboard()` 先至係由一句話估。兩條路之後嘅步驟完全一樣。
    """
    slug = slug or slugify(b.brand_name or b.archetype.key)
    root = Path(root).expanduser().resolve()
    out = run_scaffold(root, slug, b, force=force)
    cdir = root / "clients" / slug
    inject_redlines(cdir, b)
    write_pitch(cdir, b)
    write_run_report(cdir, b, out)

    mf = cdir / "workspace.json"
    meta = json.loads(mf.read_text(encoding="utf-8"))
    meta["source_sentence"] = b.raw
    meta["redlines"] = b.redlines
    meta["ambiguous"] = b.ambiguous
    mf.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return cdir, b


def onboard(root: Path, sentence: str, slug: str | None = None,
            force: bool = False) -> tuple[Path, Brief]:
    """由一句話生成工作台（CLI 走呢條）。"""
    return onboard_brief(root, classify(sentence), slug=slug, force=force)
