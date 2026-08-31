#!/usr/bin/env python3
"""
工作台測試。跑法：python3 -m tests.test_workbench   （或 pytest）

呢度測嘅係**判斷**，唔係格式。分錯行業、漏咗紅線、假信心度 ——
呢三樣係會令客戶出事嘅嘢，所以要鎖死。
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from workbench.pipeline import onboard          # noqa: E402
from workbench.seed import seed                  # noqa: E402
from workbench.state import read_agency, read_client  # noqa: E402
from workbench.taxonomy import classify          # noqa: E402

FAILED: list[str] = []


def check(cond: bool, msg: str) -> None:
    if cond:
        print(f"  ✓ {msg}")
    else:
        print(f"  ✗ {msg}")
        FAILED.append(msg)


def test_classify() -> None:
    print("\n分類")

    # 呢個係真實案例：句子入面同時有「網店」（渠道）同「紮肚」（交付物）。
    # 交付物要贏 —— 分做電商就會漏晒 health-adjacent 同 beauty-efficacy 紅線。
    b = classify("客戶做網店賣產後紮肚服務，用開 IG，帳號 @mamis_sunshine")
    check(b.archetype.key == "service-booking", "交付物（紮肚）贏渠道（網店）")
    mods = {m.key for m in b.modifiers}
    check("health-adjacent" in mods, "紮肚 → health-adjacent")
    check("beauty-efficacy" in mods, "紮肚 → beauty-efficacy（體形宣稱係另一套監管邏輯）")
    check(any("行業分唔清" in x for x in b.ambiguous), "兩個行業都講得通時，有明文警告")

    cases = {
        "我哋係一間 marketing 代理公司，用開 IG": "agency-creative",
        "外判客服中心，幫電商品牌處理 Facebook 查詢": "bpo-support",
        "我哋做小朋友教育玩具，喺小紅書賣": "kids-product",
        "一間網頁開發公司，用 LinkedIn 搵生意": "web-dev",
        "我開緊一間餐廳，兩間分店": "local-storefront",
        "我做補習社，教中學生": "education",
    }
    for text, want in cases.items():
        got = classify(text).archetype.key
        check(got == want, f"「{text[:16]}…」→ {want}" + ("" if got == want else f"（實際 {got}）"))

    # 短英文詞塞喺其他字入面 —— 之前 "ui" 會喺 "guide" 度中，"app" 會喺 "happy" 度中
    b = classify("we publish a happy parenting guide for readers")
    check(b.archetype.key != "web-dev", "「happy」入面嘅 app 唔會誤判做 web-dev")
    check(b.archetype.key != "design-studio", "「guide」入面嘅 ui 唔會誤判做 design-studio")

    b = classify("我賣嘢")
    check(bool(b.ambiguous), "分唔到行業時唔會扮肯定")

    b = classify("marketing 公司 @bright-collective")
    check(b.handles == ["bright-collective"], "帳號連字號唔會被斬")

    b = classify("我哋做設計，網站 studio-nord.com")
    check("studio-nord.com" in b.sites, "抽到網址")


def test_pipeline() -> None:
    print("\n生成")
    tmp = Path(tempfile.mkdtemp())
    try:
        cdir, b = onboard(tmp, "客戶做產後紮肚服務，用開 IG 同小紅書，@demo_brand")

        check((cdir / "workspace.json").is_file(), "workspace.json 寫咗")
        check((cdir / "pitch.md").is_file(), "pitch.md 寫咗（present 用）")
        check((cdir / "run-report.md").is_file(), "run-report.md 寫咗")

        bible = (cdir / "brand" / "BIBLE.md").read_text(encoding="utf-8")
        check("<由 archetype 生成>" not in bible, "BIBLE 嘅 placeholder 已經填咗")
        check("治療" in bible, "health-adjacent 紅線寫入咗 BIBLE 而唔係淨係留喺 reference")
        check("必瘦" in bible or "保證" in bible, "beauty-efficacy 紅線寫入咗 BIBLE")

        meta = json.loads((cdir / "workspace.json").read_text(encoding="utf-8"))
        check(meta["publish_mode"] == "review-only", "預設唔會開自動發布")
        check("qa" in meta["agents"], "一定有 QA 崗位")
        check(len(meta["agents"]) <= 8, "員工唔超過 8 個")
        check(meta["source_sentence"].startswith("客戶做"), "原話有留低，日後查得返點解咁分")

        report = (cdir / "run-report.md").read_text(encoding="utf-8")
        check("未爬過任何公開內容" in report, "報告有講明未做嘅嘢，唔會扮完成")

        # 再跑一次唔可以爆，亦唔可以覆蓋人手改過嘅嘢
        marker = "# 人手改過嘅內容"
        (cdir / "brand" / "brain" / "01-positioning.md").write_text(marker, encoding="utf-8")
        onboard(tmp, "客戶做產後紮肚服務，用開 IG 同小紅書，@demo_brand")
        check((cdir / "brand" / "brain" / "01-positioning.md").read_text(encoding="utf-8") == marker,
              "重跑唔會覆蓋已經人手改咗嘅檔案")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_state() -> None:
    print("\n狀態")
    tmp = Path(tempfile.mkdtemp())
    try:
        idle, _ = onboard(tmp, "一間網頁開發公司，用 LinkedIn 搵生意，@t_setup")
        st = read_client(idle)
        check(st.health == "setup",
              "乜都未開始 + 缺料 = 待設置（唔係阻塞 —— 否則日日紅燈，冇人再望）")

        blocked, _ = onboard(tmp, "我哋做小朋友教育玩具，喺小紅書賣，@t_block")
        seed(blocked, "blocked")
        st = read_client(blocked)
        check(st.health == "blocked", "生產線有嘢但出唔到街 = 阻塞")
        check(any(b.key == "no-claims" for b in st.blockers), "證據庫空 = 硬阻塞")
        check(all(b.consequence for b in st.blockers), "每條阻塞都講到「唔補會點」")
        check(all(b.fix for b in st.blockers), "每條阻塞都有補救方法")

        review, _ = onboard(tmp, "客戶做產後紮肚服務，用開 IG，@t_review")
        seed(review, "review")
        st = read_client(review)
        check(st.health == "attention", "有嘢等人審 = 等人審")
        check("審" in st.next_action, "下一步講到要審咩")

        run, _ = onboard(tmp, "marketing 代理公司，用開 IG，@t_run")
        seed(run, "running")
        st = read_client(run)
        check(st.health == "ready", "全條線通 = 運作中")

        ag = read_agency(tmp)
        check(len(ag.clients) == 4, "讀到全部 4 個客")
        check(ag.totals()["blocked"] == 1, "總數只計真阻塞")
        json.dumps(ag.to_dict(), ensure_ascii=False)  # dashboard 靠呢個
        check(True, "狀態可以序列化做 JSON（dashboard 用）")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_autopublish_guard() -> None:
    print("\n自動發布防護")
    tmp = Path(tempfile.mkdtemp())
    try:
        cdir, _ = onboard(tmp, "marketing 代理公司，用開 IG，@t_auto")
        mf = cdir / "workspace.json"
        meta = json.loads(mf.read_text(encoding="utf-8"))
        meta["publish_mode"] = "auto"
        mf.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
        st = read_client(cdir)
        check(any(b.key == "autopublish-too-early" for b in st.blockers),
              "語氣未穩就開自動發布，會被攔住")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    for fn in (test_classify, test_pipeline, test_state, test_autopublish_guard):
        fn()
    print()
    if FAILED:
        print(f"✗ {len(FAILED)} 項failed：")
        for f in FAILED:
            print(f"   - {f}")
        return 1
    print("✓ 全部通過")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
