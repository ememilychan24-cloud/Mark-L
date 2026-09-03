#!/usr/bin/env python3
"""
把 Python 嘅行業表同檔案範本，匯出做 Cloudflare Worker 食得嘅 JSON。

**點解要匯出，唔手寫多份 JS：**
呢個 repo 已經因為「兩個真相來源」中過一次招 —— scaffold.py 同 taxonomy.py
各自寫咗一份合規紅線，結果每份 BIBLE 有 15 條而唔係 8 條，仲有兩個唔同字眼嘅
版本並存，靜靜雞錯咗好耐冇人發現。

所以 web 版嘅行業表、紅線、範本，全部由呢支腳本由 Python 生成。
JS 嗰邊只負責砌字串，唔負責諗。改行業表 = 改 taxonomy.py，跑一次呢支，就同步。

範本點嚟：唔係手抄，係**直接叫返 Python 嗰個函式**，用 {{sentinel}} 做參數。
咁樣範本永遠等於真實輸出，唔會抄漏。

用法:
  python3 scripts/build_web.py            # 寫入 web/src/generated.js
  python3 scripts/build_web.py --check    # 只檢查有冇過時（CI／測試用）
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from workbench.taxonomy import ARCHETYPES, MODIFIERS, CORE_AGENTS, MAX_AGENTS  # noqa: E402
from workbench.wizard import (  # noqa: E402
    PLATFORM_LABELS, ROLE_LABELS, SKILL_LABELS, STEPS,
)

OUT = ROOT / "web" / "src" / "generated.js"

BRAND = "{{BRAND}}"
PLAT = "{{PLATFORMS}}"
DATE = "{{DATE}}"

# scaffold.bible() 會 stamp date.today()。如果照原樣匯出，就會把**建置當日**
# 燒死喺範本入面：(a) 同步檢查每日都失敗，就算乜都冇改 —— 而一個日日報錯嘅
# 檢查，兩星期內就會被人關咗；(b) 網頁版生成嘅 BIBLE 會寫住建置日期，
# 唔係嗰個客真正開嘅日期。所以換成 sentinel，由 JS 喺建立嗰刻填。
_TODAY = re.compile(r"\d{4}-\d{2}-\d{2}")


def _scaffold():
    """由 skill 目錄載入 scaffold.py（佢唔係一個 package）。"""
    path = ROOT / ".claude" / "skills" / "brand-workspace-factory" / "scripts" / "scaffold.py"
    spec = importlib.util.spec_from_file_location("scaffold", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build() -> dict:
    sc = _scaffold()

    return {
        "_generated_by": "scripts/build_web.py — 唔好手改。改 taxonomy.py 再跑一次。",
        "core_agents": CORE_AGENTS,
        "max_agents": MAX_AGENTS,
        "steps": [{"key": k, "title": t} for k, t in STEPS],

        "archetypes": [
            {
                "key": a.key, "label": a.label, "pain": a.pain, "unlock": a.unlock,
                "extra_agents": list(a.extra_agents),
                "platforms": list(a.default_platforms),
                "skills": list(a.skills),
                "redlines": list(a.redlines),
            }
            for a in ARCHETYPES
        ],
        "modifiers": [
            {"key": m.key, "label": m.label, "why": m.why, "redlines": list(m.redlines)}
            for m in MODIFIERS
        ],
        "platform_labels": {k: {"label": v[0], "hint": v[1]}
                            for k, v in PLATFORM_LABELS.items()},
        "skill_labels": {k: {"label": v[0], "hint": v[1], "core": v[2]}
                         for k, v in SKILL_LABELS.items()},
        "role_labels": {k: {"label": v[0], "hint": v[1]} for k, v in ROLE_LABELS.items()},

        # ── 檔案範本：叫返 Python 函式生成，唔手抄 ──
        "tpl": {
            # bible() 唔再自己寫合規紅線（見 scaffold.py 入面嗰段註解），
            # 所以呢個骨架對所有 archetype 都一樣，紅線由 JS 照 pipeline
            # 嗰個做法注入 `- [ ] <…>` 嗰行。
            "bible": _TODAY.sub(DATE, sc.bible(BRAND, "{{ARCHETYPE}}", []), count=1),
            "agents": {r: sc.agents_md(r, BRAND, [PLAT]) for r in sc.AGENT_LABELS},
            "brain": [
                {"file": fn, "num": fn.split("-")[0], "title": title,
                 "what": what, "may_empty": may_empty,
                 "how": sc.EMPTY_HOW.get(fn, "由對應步驟蒸餾產生。")}
                for fn, title, what, may_empty in sc.BRAIN_FILES
            ],
            "empty_notice": sc.EMPTY_NOTICE,
            "memory": sc.memory_md(),
            "checklist": sc.checklist_md(BRAND),
            "tools": sc.TOOLS_MD if hasattr(sc, "TOOLS_MD") else "",
            "queue_dirs": list(sc.QUEUE_DIRS),
            "agent_labels": {k: {"label": v[0], "goal": v[1], "out": v[2]}
                             for k, v in sc.AGENT_LABELS.items()},
        },
    }


def render(data: dict) -> str:
    return (
        "// 由 scripts/build_web.py 生成 —— 唔好手改。\n"
        "// 改行業表／紅線／範本 = 改 workbench/taxonomy.py 或 scaffold.py，\n"
        "// 然後跑 `python3 scripts/build_web.py`。\n"
        "// 手改呢個檔案 = 製造第二個真相來源，呢個 repo 已經因為咁中過一次招。\n\n"
        "export const WB = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="匯出行業表同範本俾 Cloudflare Worker")
    ap.add_argument("--check", action="store_true",
                    help="唔寫檔案，只檢查現有嘅係咪同 Python 同步")
    a = ap.parse_args()

    text = render(build())

    if a.check:
        if not OUT.is_file():
            print(f"✗ 未生成過：{OUT.relative_to(ROOT)}", file=sys.stderr)
            return 1
        if OUT.read_text(encoding="utf-8") != text:
            print(f"✗ {OUT.relative_to(ROOT)} 同 Python 唔同步了。", file=sys.stderr)
            print("  跑：python3 scripts/build_web.py", file=sys.stderr)
            return 1
        print(f"✓ {OUT.relative_to(ROOT)} 同 Python 同步")
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    d = json.loads(text[text.index("{"):text.rindex("}") + 1])
    print(f"✓ {OUT.relative_to(ROOT)}")
    print(f"  {len(d['archetypes'])} 個行業 · {len(d['modifiers'])} 個合規修飾 · "
          f"{len(d['tpl']['agents'])} 個崗位範本 · {len(text) // 1024} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
