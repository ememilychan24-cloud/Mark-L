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
from workbench.taxonomy import classify, slugify # noqa: E402
from workbench.visual import _hue_of, _missing_hues, render as render_visual  # noqa: E402
from workbench.wizard import (                    # noqa: E402
    Draft, apply_archetype_defaults, brief_from_draft, derived, options, seed_from_sentence,
)

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

        # 紅線曾經寫咗兩次（scaffold 同 taxonomy 各有一份），而且兩份字眼唔同：
        # 「功效宣稱要有測試依據」有長短兩個版本並存。一份合規檔案入面
        # 同一條規矩有兩個講法，agent 就唔知邊個算數。
        from collections import Counter
        rl = [x for x in bible.splitlines() if x.startswith("- [ ]")]
        check(len(rl) == len(b.redlines),
              f"BIBLE 紅線數目 {len(rl)} 等於 brief 嘅 {len(b.redlines)}（唔會寫兩次）")
        check(not [x for x, n in Counter(rl).items() if n > 1], "冇任何一條紅線重複")
        check(not any(x.startswith("- [ ] <") for x in rl), "placeholder 已經真係被取代")

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


def test_wizard() -> None:
    print("\n設定精靈")

    # 一個乜都唔識嘅人，開頁乜都唔打
    d = seed_from_sentence("")
    o = options("industry", d)
    check(not o["can_advance"], "未揀行業就唔行得（唔會靜靜雞用預設）")
    check(len(o["choices"]) == 13, "13 個行業全部撳得")
    check(all(c["hint"] for c in o["choices"]), "每個行業都有一句解釋，唔係淨係一個名")

    # 撳一下行業 → 平台同工作自動填好。呢個就係「唔使填嘢」嘅核心。
    d = apply_archetype_defaults(Draft(archetype="service-booking"))
    check(len(d.platforms) >= 3, "揀完行業，平台自動填好")
    check(len(d.skills) >= 4, "揀完行業，工作自動填好")

    # 加合規修飾 → 紅線跟住變多
    before = len(derived(d)["redlines"])
    d.modifiers = ["health-adjacent", "beauty-efficacy"]
    after = len(derived(d)["redlines"])
    check(after > before, f"加合規修飾，紅線由 {before} 變 {after} 條")

    # 揀「做圖」→ 自動請視覺崗位，用戶唔使識咩叫 agent
    d.skills = list(d.skills) + ["image-gen"]
    roles = [a["id"] for a in derived(d)["agents"]]
    check("visual" in roles, "揀咗做圖，就自動請視覺崗位")
    check("qa" in roles, "QA 永遠喺度")
    check(len(roles) <= 8, "崗位唔超過 8 個")

    o = options("jobs", d)
    locked = [c for c in o["choices"] if c["locked"]]
    check(bool(locked) and all(c["why"] for c in locked), "撳唔郁嘅工作要講明點解")

    # 用戶撳走嘅嘢，唔可以被預設偷偷加返
    d2 = apply_archetype_defaults(Draft(archetype="service-booking", platforms=["ig"]))
    check(d2.platforms == ["ig"], "用戶自己揀咗平台，預設唔會蓋返佢")

    # 精靈唔會再估一次 —— 撳咗咩就係咩
    b = brief_from_draft(d)
    check(b.archetype.key == "service-booking", "精靈用返用戶撳嘅行業，唔會重新分類")
    check(all("人手揀" in v or "確認" in v for v in b.evidence.values()),
          "每項判斷都標明係人手揀，唔係推斷出嚟")
    check(not any("行業分唔清" in x for x in b.ambiguous),
          "人手揀完就冇行業歧義（歧義只屬於猜測，唔屬於選擇）")
    check(any("未交過參考圖" in x for x in b.ambiguous),
          "但真實缺口照樣要講：未交圖就係未交圖")

    o = options("review", d)
    check(o["can_advance"], "揀齊嘢就開得工")
    check(bool(o["summary"]["redlines"]), "最後一頁會列晒紅線先俾你撳")


def test_web_export_in_sync() -> None:
    """web/src/generated.js 一定要同 Python 同步。

    Cloudflare 版嘅行業表同範本係由 Python 匯出。改咗 taxonomy.py 但冇重新匯出，
    網站就會顯示舊嘅行業同紅線 —— 而客戶睇到嘅係網站嗰邊，唔係 Python 嗰邊。
    呢個 repo 已經因為「兩個真相來源」中過一次招（紅線寫咗兩次），唔好再中。
    """
    print("\nweb 匯出同步")
    import subprocess
    root = Path(__file__).resolve().parent.parent
    r = subprocess.run([sys.executable, "scripts/build_web.py", "--check"],
                       cwd=root, capture_output=True, text=True)
    check(r.returncode == 0, "generated.js 同 Python 同步"
          + ("" if r.returncode == 0 else "　→ 跑 python3 scripts/build_web.py"))


def test_slug() -> None:
    print("\n資料夾命名")

    # 之前淨係留 a-z0-9，於是三個唔同嘅中文名全部變咗 `client`，
    # 第二個客會靜靜雞寫入第一個客個資料夾 —— 冇錯誤訊息，冇人發現
    names = ["陳記茶餐廳", "小紅點設計", "日日鮮"]
    slugs = [slugify(n) for n in names]
    check(len(set(slugs)) == 3, f"三個中文名出到三個唔同資料夾（{slugs}）")
    check("client" not in slugs, "中文名唔會全部塌落同一個預設值")
    check(slugify("美麗人生 Salon") == "美麗人生-salon", "中英混合保得住兩邊")
    check(slugify("") == "client" and slugify("!!!") == "client", "真係冇名先用預設")
    check("/" not in slugify("a/../b") and ".." not in slugify("a/../b"),
          "路徑符號會被洗走")


def test_visual() -> None:
    print("\n圖片分析")

    # 之前用 R/G/B 大小比較，琥珀色被判做紅色，於是「從來冇出現」欄
    # 會叫生圖模型避開品牌自己嘅強調色 —— 冇人 review 得到嘅錯
    check(_hue_of("#E8A530") == "黃／橙", "琥珀色分類做黃／橙，唔係紅")
    check(_hue_of("#5F7043") == "綠", "橄欖綠分類做綠")
    check(_hue_of("#FCFAF3") is None, "米白色算中性，唔佔任何色系")
    check(_hue_of("#000000") is None, "純黑算中性")

    pal = ["#FCFAF3", "#5F7043", "#E8A530", "#424330"]
    missing = _missing_hues(pal)
    check("黃／橙" not in missing, "品牌自己有嘅色，唔會被列入禁用")
    check("藍／紫" in missing, "真係冇出現過嘅色系，有列出嚟")

    md = render_visual({"n": 26, "light": .71, "sat": .19, "portrait": .83, "edge": .07,
                        "palette": [{"hex": h, "share": .2} for h in pal]})
    check("信心度：**高**" in md, "26 張圖 = 高信心度")
    check("從來冇出現" in md, "有寫「從來冇出現」欄")
    check("要人手填" in md, "機器讀唔到嘅嘢，明明白白留白俾人填")

    md0 = render_visual({"n": 3, "palette": [{"hex": "#5F7043", "share": 1}]})
    check("信心度：**低**" in md0, "得 3 張圖唔會扮有信心")


def main() -> int:
    for fn in (test_classify, test_pipeline, test_state, test_autopublish_guard,
               test_wizard, test_slug, test_visual, test_web_export_in_sync):
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
