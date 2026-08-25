#!/usr/bin/env python3
"""
總公司 trend library 嘅建立、驗證同索引工具。

點解要用腳本：trend library 嘅價值全靠**紀律**——每個 pack 都要有過期日、
要有來源證據、要聲明 render mode。少咗任何一樣，三個月後就冇人知邊個 pack
仲有效，成個庫變垃圾崗。腳本逼你每次都填齊。

用法:
  # 開一個新 pack（生成骨架）
  python trend_pack.py new --root ./workspace --id pov-cover-2026q3 \\
      --label "POV 第一人稱封面" --format cover --genre pov \\
      --render-mode image-only --aspect 3:4 --platforms xhs,ig \\
      --hot-from 2026-06 --hot-to 2026-09 --retire-after 2026-11

  # 驗證全部 pack（缺欄位、過期、樣本缺失）
  python trend_pack.py check --root ./workspace

  # 重建 INDEX.md
  python trend_pack.py index --root ./workspace

  # 客戶揀 pack
  python trend_pack.py select --root ./workspace --client mamis-sunshine \\
      --slot cover --pack pov-cover-2026q3
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

REQUIRED = ["id", "label", "format", "genre", "render_mode", "aspect",
            "platforms", "hot_window", "retire_after", "text_capacity",
            "brand_slots", "evidence", "avoid"]

RENDER_MODES = ["image-only", "image-plus-text-layer"]
FORMATS = ["cover", "carousel", "reel-thumb", "quote-card", "product-shot"]
SLOTS = ["cover", "carousel", "reel_thumb", "quote_card", "product_shot"]


def month_key(s: str) -> tuple[int, int]:
    y, m = s.split("-")[:2]
    return int(y), int(m)


def this_month() -> str:
    t = date.today()
    return f"{t.year:04d}-{t.month:02d}"


def packs_dir(root: Path) -> Path:
    return root / "_trends" / "packs"


def load_packs(root: Path) -> list[tuple[Path, dict]]:
    d = packs_dir(root)
    if not d.exists():
        return []
    out = []
    for pj in sorted(d.glob("*/pack.json")):
        if "_archived" in pj.parts:
            continue
        try:
            out.append((pj.parent, json.loads(pj.read_text(encoding="utf-8"))))
        except json.JSONDecodeError as e:
            print(f"⚠️  {pj}: JSON 壞咗 — {e}", file=sys.stderr)
    return out


RECIPE = """# {label} · 生圖配方

> pack: `{id}` · render mode: `{render_mode}` · {aspect}

## 骨架

<喺呢度寫模型無關嘅構圖描述：視角、主體、光線、構圖、色調、質感、排除項。
唔好寫模型名或者參數 —— 模型會換，配方唔應該跟住改。>

{{SUBJECT}}，{{MOOD}} 氛圍。
光線：{{LIGHT_DIRECTION}}。
構圖：主體偏 {{SUBJECT_POSITION}}，{safe_zone} 留白。
色調：{{PALETTE}}，飽和度 {{SATURATION}}。
質感：{{TEXTURE}}。
畫面內唔好出現：水印、假 logo、邊框、無意義裝飾圖形。

## 變數槽

| 槽 | 由邊度嚟 |
|---|---|
| SUBJECT | 已批准文案內容 |
| MOOD | 文案情緒 |
| LIGHT_DIRECTION | style/brand-visual.md |
| SUBJECT_POSITION | style/brand-visual.md |
| PALETTE | style/brand-visual.md |
| SATURATION | style/brand-visual.md |
| TEXTURE | style/brand-visual.md |

## 文字處理

{text_note}

## 常見失敗

| 症狀 | 原因 | 點改 |
|---|---|---|
| 出咗英文字 | 冇指定語言 | prompt 加「文字為繁體中文」 |
| 加咗唔想要嘅裝飾 | 排除項唔夠具體 | 補「畫面內唔好出現」清單 |
| 風格每次唔同 | 冇用骨架 | 一定要由呢份配方出發 |
"""

PACK_MD = """# {label}

> `{id}` · {format} / {genre} · {aspect} · 熱度窗口 {hf} → {ht} · 退役 {retire}

## 呢個體裁係咩

<一段。講清楚個**呈現形式**，唔係講主題。>

## 點解 work

<受眾點解會停低。呢節寫得好，客戶先知幾時應該用、幾時唔應該用。>

## 幾時唔啱用

<至少兩條。冇「唔啱用」嘅 pack 會被亂用。>

## 觀察證據

<邊個平台、邊個垂直領域、幾時開始升。要有來源連結。>

## 樣本

`samples/` 入面嘅圖**全部由我哋自己生成**，用中性題材示範個格式。
唔存別人嘅原圖，唔模仿某個創作者嘅簽名畫風 —— 我哋抄嘅係體裁，唔係作品。
"""


def cmd_new(a) -> int:
    root = Path(a.root).resolve()
    d = packs_dir(root) / a.id
    if d.exists() and not a.force:
        print(f"✗ {a.id} 已存在。用 --force 覆蓋。", file=sys.stderr)
        return 1
    if a.render_mode not in RENDER_MODES:
        print(f"✗ render-mode 要係 {RENDER_MODES} 其中一個", file=sys.stderr)
        return 2

    text_only = a.render_mode == "image-only"
    pack = {
        "id": a.id,
        "label": a.label,
        "format": a.format,
        "genre": a.genre,
        "render_mode": a.render_mode,
        "aspect": a.aspect,
        "platforms": [p.strip() for p in a.platforms.split(",") if p.strip()],
        "hot_window": {"from": a.hot_from, "to": a.hot_to},
        "retire_after": a.retire_after,
        "text_capacity": {
            "max_chars": a.max_chars,
            "safe_zone": a.safe_zone,
        },
        "brand_slots": ["palette", "subject", "mood", "typeface", "texture"],
        "evidence": [],
        "avoid": [],
        "created": date.today().isoformat(),
    }

    (d / "samples").mkdir(parents=True, exist_ok=True)
    (d / "pack.json").write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (d / "PACK.md").write_text(PACK_MD.format(
        label=a.label, id=a.id, format=a.format, genre=a.genre, aspect=a.aspect,
        hf=a.hot_from, ht=a.hot_to, retire=a.retire_after), encoding="utf-8")
    (d / "prompt-recipe.md").write_text(RECIPE.format(
        label=a.label, id=a.id, render_mode=a.render_mode, aspect=a.aspect,
        safe_zone=a.safe_zone,
        text_note=(
            f"`image-only`：圖上文字（**上限約 {a.max_chars} 字**）直接寫入 prompt，"
            "用引號括住，並要求「文字必須完全一致，唔好改寫」。\n"
            "**生完要逐字核對** —— 圖像模型出錯字係結構性限制，唔係 prompt 寫得靚就避得到。"
            if text_only else
            f"`image-plus-text-layer`：模型只生底圖同氛圍，**{a.safe_zone}** 要保持乾淨。\n"
            "文字用品牌字體疊上去 —— 咁樣價錢、步驟編號、免責聲明先會 100% 準確，\n"
            "而且改文唔使重新生圖。"
        )), encoding="utf-8")

    print(f"✓ 開咗 {d}")
    print("  仲要填：PACK.md（點解 work、幾時唔啱用）、pack.json 嘅 evidence 同 avoid")
    print("  然後生 2–3 張 sample 落 samples/（用中性題材，唔好用客戶資料）")
    return 0


def cmd_check(a) -> int:
    root = Path(a.root).resolve()
    packs = load_packs(root)
    if not packs:
        print("冇 pack。用 `trend_pack.py new` 開第一個。")
        return 0

    now = this_month()
    problems = 0
    for d, p in packs:
        issues = []
        for k in REQUIRED:
            if k not in p or p[k] in (None, "", [], {}):
                issues.append(f"缺 `{k}`")
        if p.get("render_mode") not in RENDER_MODES:
            issues.append(f"render_mode 唔合法：{p.get('render_mode')}")
        if not p.get("evidence"):
            issues.append("冇 evidence — 冇來源就證明唔到呢個體裁真係喺流行")
        if not p.get("avoid"):
            issues.append("冇 avoid — 冇「幾時唔啱用」嘅 pack 會被亂用")
        if not list((d / "samples").glob("*")):
            issues.append("samples/ 係空 — 客戶喺 dashboard 揀嘅時候冇嘢睇")
        ra = p.get("retire_after")
        if ra and month_key(ra) < month_key(now):
            issues.append(f"已過期（retire_after {ra}）— 移去 packs/_archived/")
        elif ra and month_key(ra) == month_key(now):
            issues.append(f"今個月到期（{ra}）— 決定續期定退役")

        if issues:
            problems += 1
            print(f"\n✗ {p.get('id', d.name)}")
            for i in issues:
                print(f"    · {i}")
        else:
            print(f"✓ {p['id']}  ({p['format']}/{p['render_mode']}, 到 {ra})")

    print(f"\n{len(packs)} 個 pack，{problems} 個有問題。")
    return 1 if problems else 0


def cmd_index(a) -> int:
    root = Path(a.root).resolve()
    packs = load_packs(root)
    now = this_month()

    live = [(d, p) for d, p in packs
            if not p.get("retire_after") or month_key(p["retire_after"]) >= month_key(now)]
    dead = [(d, p) for d, p in packs if (d, p) not in live]

    L = ["# Trend Library 索引", "",
         f"> 更新：{date.today().isoformat()} · 生效 {len(live)} 個 · 已過期 {len(dead)} 個", "",
         "客戶工作台**引用**呢度嘅 pack，唔複製。",
         "所以總公司更新一次 pack，所有引用緊嘅客戶自動跟到最新。", "",
         "## 生效中", "",
         "| Pack | 體裁 | 格式 | Render | 平台 | 到期 |",
         "|---|---|---|---|---|---|"]
    for _, p in sorted(live, key=lambda x: x[1].get("retire_after", "")):
        L.append(f"| `{p['id']}` | {p.get('label','')} | {p.get('format','')} | "
                 f"{p.get('render_mode','')} | {', '.join(p.get('platforms', []))} | "
                 f"{p.get('retire_after','—')} |")
    if not live:
        L.append("| （冇）| | | | | |")

    if dead:
        L += ["", "## 已過期", "",
              "> 唔好刪 —— 歷史觀察有參考價值。移去 `packs/_archived/`，唔再喺上面出現。", ""]
        for _, p in dead:
            L.append(f"- `{p['id']}` — {p.get('label','')}（{p.get('retire_after','')}）")

    L += ["", "## 更新節奏", "",
          "每月一次，30–60 分鐘：", "",
          "1. 爬三個平台各一個垂直領域嘅高互動內容",
          "2. 分類**呈現體裁**（唔係主題）",
          "3. 頻率上升 → `trend_pack.py new`",
          "4. 頻率下跌 → 改 `retire_after`",
          "5. 每個新 pack 生 2–3 張 sample（中性題材）",
          "6. `trend_pack.py check` 再 `trend_pack.py index`", ""]

    out = root / "_trends" / "INDEX.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"✓ {out}  （生效 {len(live)}、過期 {len(dead)}）")
    return 0


def cmd_select(a) -> int:
    root = Path(a.root).resolve()
    if a.slot not in SLOTS:
        print(f"✗ slot 要係 {SLOTS} 其中一個", file=sys.stderr)
        return 2
    pd = packs_dir(root) / a.pack
    if not (pd / "pack.json").exists():
        print(f"✗ 搵唔到 pack `{a.pack}`", file=sys.stderr)
        return 1
    p = json.loads((pd / "pack.json").read_text(encoding="utf-8"))

    f = root / "clients" / a.client / "style" / "selected-packs.json"
    cur = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    cur[a.slot] = a.pack
    cur["updated"] = date.today().isoformat()
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(cur, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"✓ {a.client} 嘅 `{a.slot}` → {a.pack}")
    print(f"  render mode：{p['render_mode']}"
          + ("（圖上文字要逐字核對）" if p["render_mode"] == "image-only"
             else "（文字用品牌字體疊上去）"))
    print(f"  熱度到 {p.get('retire_after','—')}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="總公司 trend library 工具")
    sub = ap.add_subparsers(dest="cmd", required=True)

    n = sub.add_parser("new", help="開新 pack")
    n.add_argument("--root", required=True)
    n.add_argument("--id", required=True)
    n.add_argument("--label", required=True)
    n.add_argument("--format", default="cover", choices=FORMATS)
    n.add_argument("--genre", required=True)
    n.add_argument("--render-mode", default="image-only", choices=RENDER_MODES)
    n.add_argument("--aspect", default="3:4")
    n.add_argument("--platforms", default="xhs,ig")
    n.add_argument("--hot-from", default=this_month())
    n.add_argument("--hot-to", required=True)
    n.add_argument("--retire-after", required=True)
    n.add_argument("--max-chars", type=int, default=16)
    n.add_argument("--safe-zone", default="上方 25%")
    n.add_argument("--force", action="store_true")
    n.set_defaults(fn=cmd_new)

    c = sub.add_parser("check", help="驗證全部 pack")
    c.add_argument("--root", required=True)
    c.set_defaults(fn=cmd_check)

    i = sub.add_parser("index", help="重建 INDEX.md")
    i.add_argument("--root", required=True)
    i.set_defaults(fn=cmd_index)

    s = sub.add_parser("select", help="客戶揀 pack")
    s.add_argument("--root", required=True)
    s.add_argument("--client", required=True)
    s.add_argument("--slot", required=True, choices=SLOTS)
    s.add_argument("--pack", required=True)
    s.set_defaults(fn=cmd_select)

    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    raise SystemExit(main())
