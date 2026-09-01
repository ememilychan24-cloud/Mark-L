#!/usr/bin/env python3
"""
工作台 CLI。零外部依賴 —— 淨係要 Python 3.11+。

  python -m workbench start       # 開工作台，自動彈開瀏覽器 ← 唔識 terminal 用呢個
  python -m workbench new "我個客賣產後紮肚服務，用開 IG 同小紅書，@mamis_sunshine"
  python -m workbench status
  python -m workbench serve
  python -m workbench doctor
  python -m workbench demo        # 起五個唔同行業嘅示範客戶
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .pipeline import onboard
from .state import STAGES, SIDE_STAGES, read_agency
from .taxonomy import ARCHETYPES, classify

DEFAULT_ROOT = Path("agency")

# demo：每個代表一種真實接得到嘅生意，唔係為咗好睇而砌。
# 第二個值係示範階段 —— 五個客停喺唔同位，先示範到條生產線點流動。
DEMO_CLIENTS = [
    ("我哋係一間 marketing 代理公司，同時服務八個客，用開 IG 同 Facebook，@bright-collective", "running"),
    ("客戶做網店賣產後紮肚服務，用開 IG，想發展埋小紅書、Threads、FB，帳號 @mamis_sunshine，網站 soulful-sunshine.com", "review"),
    ("我哋做小朋友教育玩具，喺 IG 同小紅書賣，@littlesprout.hk", "blocked"),
    ("一間網頁開發公司，主要接企業客，用 LinkedIn 搵生意，@nordic-web-studio", "setup"),
    ("外判客服中心，幫電商品牌處理 Facebook 同 IG 查詢，@carehub-asia", "review"),
]

BAR = "━"


def _c(s: str, code: str) -> str:
    return s if not sys.stdout.isatty() else f"\033[{code}m{s}\033[0m"


HEALTH = {
    "blocked": ("● 阻塞", "31"),
    "attention": ("● 等人審", "33"),
    "ready": ("● 運作中", "32"),
    "setup": ("○ 待設置", "36"),
    "unknown": ("○ 未知", "37"),
}


def cmd_new(a) -> int:
    root = Path(a.root)
    b = classify(a.sentence)

    print(f"\n{_c('讀到嘅嘢', '1')}")
    print(f"  行業      {b.archetype.label}  ({b.archetype.key})")
    print(f"  合規      {'、'.join(m.label for m in b.modifiers) or '冇'}")
    print(f"  平台      {'、'.join(b.platforms)}")
    print(f"  帳號      {'、'.join('@' + h for h in b.handles) or '（冇）'}")
    print(f"  員工      {len(b.agents)} 個：{'、'.join(b.agents)}")
    print(f"  紅線      {len(b.redlines)} 條")

    if b.ambiguous:
        print(f"\n{_c('推斷（未確認）', '33')}")
        for x in b.ambiguous:
            print(f"  ⚠ {x}")

    if a.dry_run:
        print("\n--dry-run：冇寫任何檔案。")
        return 0

    cdir, b = onboard(root, a.sentence, slug=a.slug, force=a.force)
    print(f"\n{_c('✓ 工作台已建立', '32')}  {cdir}")
    print(f"  present 用   {cdir}/pitch.md")
    print(f"  生成報告     {cdir}/run-report.md")
    print(f"  品牌憲法     {cdir}/brand/BIBLE.md")
    print(f"\n下一步：`python -m workbench status` 睇阻塞喺邊。")
    return 0


def cmd_status(a) -> int:
    st = read_agency(Path(a.root))
    if a.json:
        print(json.dumps(st.to_dict(), ensure_ascii=False, indent=2))
        return 0

    if not st.clients:
        print(f"{a.root} 入面冇客戶。先跑 `python -m workbench demo` 或者 `new`。")
        return 0

    t = st.totals()
    print(f"\n{_c('工作台總覽', '1')}   {st.root}")
    print(f"  {t['clients']} 個客 · {t['waiting_human']} 件等緊人審 · "
          f"{t['blocked']} 個阻塞 · {t['scheduled']} 件已排程")
    print(BAR * 68)

    for c in st.clients:
        label, colour = HEALTH[c.health]
        print(f"\n{_c(label, colour)}  {_c(c.brand, '1')}  ({c.archetype})")
        flow = "  ".join(
            f"{name} {c.counts.get(k, 0)}" for k, name, _ in STAGES if c.counts.get(k, 0)
        ) or "（生產線空）"
        print(f"     {flow}")
        if c.counts.get("06-replies"):
            print(f"     待回覆 {c.counts['06-replies']}")
        print(f"     語氣 {c.voice_confidence} · 視覺 {c.visual_confidence} · 發布 {c.publish_mode}")
        for bl in c.blockers:
            mark = "✗" if bl.severity == "block" else "!"
            who = "客戶" if bl.owner == "client" else "我哋"
            print(f"     {mark} {bl.what}（{who}）→ {bl.consequence}")
        print(f"     {_c('下一步：' + c.next_action, '1')}")

    if st.trend_packs:
        print(f"\n{BAR * 68}\n{_c('趨勢圖庫', '1')}")
        for p in st.trend_packs:
            flag = " ⚠ 已過期" if p["expired"] else ""
            print(f"  {p['id']}  樣本 {p['samples']}  到期 {p['retire_after']}{flag}")
    print()
    return 0


def cmd_doctor(a) -> int:
    """檢查工作台有冇「睇落完整但實際上唔可以出街」嘅情況。"""
    st = read_agency(Path(a.root))
    problems = 0
    print(f"\n{_c('健康檢查', '1')}  {st.root}\n")
    for c in st.clients:
        issues = []
        if c.publish_mode != "review-only" and c.voice_confidence != "高":
            issues.append("語氣未穩就開咗自動發布")
        if c.counts.get("05-scheduled") and "04-approved-claims.md" in c.empty_buckets:
            issues.append("已排程有嘢，但證據庫係空 —— 出街內容可能有無出處嘅宣稱")
        if c.counts.get("04-assets") and c.visual_confidence in ("未建立", "低"):
            issues.append("有視覺素材，但品牌視覺未建立 —— 啲圖大機會唔似品牌")
        if not c.agents:
            issues.append("冇員工編制")
        if "qa" not in c.agents and c.agents:
            issues.append("冇 QA 崗位 —— 冇人審係唯一唔可以妥協嘅嘢")
        if issues:
            problems += len(issues)
            print(f"  {_c('✗', '31')} {c.brand}")
            for i in issues:
                print(f"      {i}")
        else:
            print(f"  {_c('✓', '32')} {c.brand}")
    print(f"\n{problems} 個問題。\n")
    return 1 if problems else 0


def cmd_demo(a) -> int:
    root = Path(a.root)
    print(f"起 {len(DEMO_CLIENTS)} 個唔同行業嘅示範客戶 → {root}\n")
    from .seed import seed
    for s, level in DEMO_CLIENTS:
        cdir, b = onboard(root, s, force=a.force)
        if not a.bare:
            seed(cdir, level)
        print(f"  ✓ {cdir.name:<22} {b.archetype.label:<16} {level:<8} "
              f"{len(b.agents)} 員工 · {len(b.redlines)} 紅線 · {'、'.join(b.platforms)}")
    print(f"\n跑 `python -m workbench status --root {root}` 睇狀態，"
          f"或者 `python -m workbench serve --root {root}` 開 dashboard。")
    return 0


def cmd_industries(a) -> int:
    print(f"\n{_c('支援嘅行業', '1')}（分類係規則，唔係靠估 —— 見 workbench/taxonomy.py）\n")
    for x in ARCHETYPES:
        print(f"{_c(x.label, '1')}  ({x.key})")
        print(f"   塞喺邊：{x.pain}")
        print(f"   拆開咗：{x.unlock}\n")
    return 0


def cmd_serve(a) -> int:
    from .server import serve
    return serve(Path(a.root), a.port, a.host, open_browser=False)


def cmd_start(a) -> int:
    """一句嘢開晒 —— 唔識用 terminal 嘅人淨係需要記住呢一個。"""
    from .server import serve
    root = Path(a.root)
    if not (root / "clients").is_dir():
        print("第一次用：仲未有客戶。開咗之後撳「＋ 開新客」就得。\n")
    return serve(root, a.port, a.host, open_browser=True)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="workbench", description="AI marketing 工作台")
    sub = p.add_subparsers(dest="cmd", required=True)

    # --root 放喺每個 subcommand，唔係放喺前面 —— `workbench status --root x` 先係
    # 大家會打嘅次序，而唔係 `workbench --root x status`
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--root", default=str(DEFAULT_ROOT),
                        help=f"agency 根目錄（預設 {DEFAULT_ROOT}）")

    n = sub.add_parser("new", parents=[common], help="一句話開一個新客工作台")
    n.add_argument("sentence")
    n.add_argument("--slug", default=None)
    n.add_argument("--force", action="store_true")
    n.add_argument("--dry-run", action="store_true", help="只顯示判斷結果，唔寫檔案")
    n.set_defaults(fn=cmd_new)

    s = sub.add_parser("status", parents=[common], help="睇所有客嘅生產線狀態")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_status)

    d = sub.add_parser("doctor", parents=[common], help="檢查有冇睇落完整但唔可以出街嘅情況")
    d.set_defaults(fn=cmd_doctor)

    dm = sub.add_parser("demo", parents=[common], help="起五個唔同行業嘅示範客戶")
    dm.add_argument("--force", action="store_true")
    dm.add_argument("--bare", action="store_true",
                    help="唔填示範資料，五個客全部停喺剛開好嘅狀態")
    dm.set_defaults(fn=cmd_demo)

    i = sub.add_parser("industries", parents=[common], help="列出支援行業同各自嘅核心問題")
    i.set_defaults(fn=cmd_industries)

    sv = sub.add_parser("serve", parents=[common], help="開 dashboard（瀏覽器睇）")
    sv.add_argument("--port", type=int, default=8787)
    sv.add_argument("--host", default="127.0.0.1")
    sv.set_defaults(fn=cmd_serve)

    stt = sub.add_parser("start", parents=[common],
                         help="開工作台並自動彈開瀏覽器（唔識 terminal 就用呢個）")
    stt.add_argument("--port", type=int, default=8787)
    stt.add_argument("--host", default="127.0.0.1")
    stt.set_defaults(fn=cmd_start)

    a = p.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    raise SystemExit(main())
