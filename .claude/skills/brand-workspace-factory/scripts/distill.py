#!/usr/bin/env python3
"""
由爬回嚟嘅貼文，算出可驗證嘅語氣指標，輸出 voice-profile.md 草稿。

點解要用腳本做呢一步：人（同模型）睇 40 條帖之後，會傾向寫「語氣親切專業」
呢類唔可驗證嘅描述。統計數字逼你寫「平均 38 字一句，感嘆號 50 條入面出現 3 次」
—— 呢類描述先至可以令兩個唔同嘅寫手寫出似嘅嘢。

輸入：一個資料夾嘅 .json 檔（或單一 .json）。每條記錄要有：
  {"text": "...", "platform": "xhs", "url": "...", "date": "2026-01-01",
   "likes": 120, "saves": 30, "comments": 8}
只有 text 係必需。

用法:
  python distill.py --input data/scraped/ --output brand/brain/02-voice-profile.md
  python distill.py --input data/scraped/ --output - --json   # 只出統計
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

# 句子終結符，中英一齊處理
SENT_END = re.compile(r"[。！？!?…]+|\n+")
CJK = re.compile(r"[一-鿿]")

EMOJI = re.compile(
    "[" "\U0001F300-\U0001FAFF" "\U00002600-\U000027BF"
    "\U0001F1E6-\U0001F1FF" "\U00002B00-\U00002BFF" "]"
)
# U+FE0F 係變體選擇符，附喺前一個字元後面。獨立計會令 ✔️ 變成兩個 emoji。
VARIATION = "\uFE0F"

OPENER_PATTERNS = [
    ("問題", re.compile(r"[？?]")),
    ("數字", re.compile(r"^\D{0,6}\d")),
    ("否定／破除", re.compile(r"^(唔好|不要|別|千萬|唔係|不是|其實)")),
    ("情境", re.compile(r"(凌晨|半夜|早上|嗰日|那天|每次|每晚|每朝)")),
    ("第一人稱", re.compile(r"^(我|自己|我哋|我们)")),
    ("直接稱呼", re.compile(r"^(你|大家|各位)")),
]

CTA_VERBS = ["留言", "私訊", "DM", "查詢", "預約", "報名", "收藏", "分享",
             "連結", "link", "購買", "落單", "登記", "追蹤", "關注"]


def char_len(s: str) -> int:
    """CJK 算字，其餘算詞 —— 混合語言時直接數 char 會嚴重高估中文句長。"""
    cjk = len(CJK.findall(s))
    latin = len(re.findall(r"[A-Za-z]+", s))
    return cjk + latin


def load(path: Path) -> list[dict]:
    files = sorted(path.rglob("*.json")) if path.is_dir() else [path]
    if not files:
        raise SystemExit(f"喺 {path} 搵唔到 .json 檔。見 references/ingestion.md 嘅 fallback 做法。")
    out: list[dict] = []
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"⚠️  跳過 {f.name}：{e}", file=sys.stderr)
            continue
        if isinstance(data, dict):
            data = data.get("posts") or data.get("items") or [data]
        for rec in data:
            if isinstance(rec, dict) and (rec.get("text") or "").strip():
                out.append(rec)
    return out


def analyse(posts: list[dict]) -> dict:
    sent_lens: list[int] = []
    para_counts: list[int] = []
    openers = Counter()
    emojis = Counter()
    exclam = 0
    question = 0
    ellipsis = 0
    dash = 0
    address = Counter()   # 第二人稱：你點稱呼讀者
    audience = Counter()  # 受眾稱謂：你點叫呢班人（名詞，唔係稱呼）
    ctas = Counter()
    emoji_total = 0
    by_platform = Counter()

    for p in posts:
        text = p["text"].strip()
        by_platform[p.get("platform", "unknown")] += 1

        paras = [x for x in text.split("\n") if x.strip()]
        para_counts.append(len(paras))

        sents = [s.strip() for s in SENT_END.split(text) if s.strip()]
        sent_lens += [char_len(s) for s in sents if char_len(s) > 0]

        if sents:
            # 保留句末標點：SENT_END.split 會食走個「？」，令問句開場永遠分類唔到
            m = SENT_END.search(text)
            first = (text[: m.end()] if m else text).strip()
            for label, pat in OPENER_PATTERNS:
                if pat.search(first):
                    openers[label] += 1
                    break
            else:
                openers["陳述"] += 1

        exclam += text.count("！") + text.count("!")
        question += text.count("？") + text.count("?")
        ellipsis += text.count("…") + text.count("...")
        dash += text.count("——") + text.count("—")

        found = EMOJI.findall(text.replace(VARIATION, ""))
        emoji_total += len(found)
        emojis.update(found)

        # 由長到短，數完就由 text 移走 —— 唔係咁樣做，「你」會喺「你哋」入面被重複計
        rest = text
        for word in ("你哋", "你們", "大家", "各位", "妳"):
            if word in rest:
                address[word] += 1
                rest = rest.replace(word, "")
        if "你" in rest:
            address["你"] += 1
        for word in ("姊妹", "姐妹", "寶媽", "新手媽媽", "媽媽", "媽咪"):
            if word in text:
                audience[word] += 1
                break  # 只計最具體嗰個
        for v in CTA_VERBS:
            if v.lower() in text.lower():
                ctas[v] += 1

    n = len(posts)
    engaged = [p for p in posts if isinstance(p.get("likes"), (int, float))]
    top = []
    if len(engaged) >= 5:
        med = statistics.median(p["likes"] for p in engaged)
        top = sorted(
            (p for p in engaged if p["likes"] > med * 1.5),
            key=lambda p: p["likes"], reverse=True,
        )[:8]

    return {
        "n_posts": n,
        "by_platform": dict(by_platform),
        "sent_len_mean": round(statistics.mean(sent_lens), 1) if sent_lens else 0,
        "sent_len_median": round(statistics.median(sent_lens), 1) if sent_lens else 0,
        "sent_len_p10": round(sorted(sent_lens)[len(sent_lens) // 10], 1) if len(sent_lens) >= 10 else 0,
        "sent_len_p90": round(sorted(sent_lens)[len(sent_lens) * 9 // 10], 1) if len(sent_lens) >= 10 else 0,
        "sents_total": len(sent_lens),
        "paras_mean": round(statistics.mean(para_counts), 1) if para_counts else 0,
        "openers": openers.most_common(),
        "exclam_per_post": round(exclam / n, 2) if n else 0,
        "question_per_post": round(question / n, 2) if n else 0,
        "ellipsis_per_post": round(ellipsis / n, 2) if n else 0,
        "dash_per_post": round(dash / n, 2) if n else 0,
        "emoji_per_post": round(emoji_total / n, 2) if n else 0,
        "emoji_top": emojis.most_common(8),
        "address": address.most_common(),
        "audience": audience.most_common(),
        "cta": ctas.most_common(8),
        "top_posts": [
            {"likes": p.get("likes"), "url": p.get("url", ""),
             "opener": _first_sentence(p["text"])[:40]}
            for p in top
        ],
    }


def _first_sentence(text: str) -> str:
    m = SENT_END.search(text.strip())
    return (text[: m.end()] if m else text).strip()


SOCIAL = {"xhs", "ig", "instagram", "threads", "fb", "facebook", "yt", "youtube", "linkedin"}


def confidence(n: int, median_len: float, platforms: dict) -> tuple[str, str]:
    """條數唔係唯一指標。

    喺真實案例度發現：由網站 bundle 抽 394 條 UI 文字，條數過關但每條得 19 字，
    而且網站文案同社交貼文根本係兩種寫法。淨計條數會俾一個假嘅「高」信心度，
    而假信心度比低信心度危險 —— 因為冇人會再去 review。
    """
    social = sum(v for k, v in platforms.items() if k.lower() in SOCIAL)
    web_only = social == 0 and bool(platforms)

    if web_only:
        return "中", ("語料全部嚟自網站／落地頁，冇社交貼文。網站文案同社交文案係兩種寫法"
                     "（網站要完整同可信，社交要停得低同傾得埋），所以呢份 profile "
                     "可以用嚟定**用詞同禁忌**，但**節奏同開場**要攞返真實貼文先算數。")
    if median_len < 25:
        return "中", (f"片段偏短（中位數 {median_len} 字），多數係標題或按鈕文字而唔係完整段落。"
                     "句長同段落節奏嘅統計意義有限。")
    if n >= 30 and social >= 20:
        return "高", "自家社交語料充足，第一批稿應該已經似。"
    if n >= 15:
        return "中", "語料偏少。頭兩星期要逐篇審，執完把修改原因回寫入呢份檔案。"
    return "低", "語料不足，以下數字統計意義有限。開工前必須由品牌方逐項 review。"


def render(s: dict) -> str:
    lvl, why = confidence(s["n_posts"], s["sent_len_median"], s["by_platform"])
    L: list[str] = [
        "# 02 · 品牌語氣 Voice Profile",
        "",
        f"> 信心度：**{lvl}** — {why}",
        f"> 樣本：{s['n_posts']} 條貼文 / {s['sents_total']} 句"
        + (f"（{', '.join(f'{k} {v}' for k, v in s['by_platform'].items())}）" if s["by_platform"] else ""),
        "> 由 `scripts/distill.py` 生成。數字係觀察到嘅**現況**，唔係目標。",
        "> 想改變語氣係另一個決定 —— 要明確標明，唔好偷偷改呢啲數字。",
        "",
        "## 句長",
        f"- 平均 **{s['sent_len_mean']} 字**，中位數 {s['sent_len_median']} 字",
        f"- 常見範圍：{s['sent_len_p10']}–{s['sent_len_p90']} 字",
        f"- 平均每篇 **{s['paras_mean']} 段**",
        "",
        "## 開場類型",
    ]
    tot = sum(v for _, v in s["openers"]) or 1
    for label, cnt in s["openers"]:
        L.append(f"- {label}：{cnt} 次（{round(cnt / tot * 100)}%）")

    L += [
        "",
        "## 標點習慣（每篇平均）",
        f"- 感嘆號 **{s['exclam_per_post']}**",
        f"- 問號 {s['question_per_post']}",
        f"- 省略號 {s['ellipsis_per_post']}",
        f"- 破折號 {s['dash_per_post']}",
        "",
        "## Emoji",
        f"- 密度：每篇 **{s['emoji_per_post']}** 個",
    ]
    if s["emoji_top"]:
        L.append("- 常用：" + " ".join(f"{e}({c})" for e, c in s["emoji_top"]))
    else:
        L.append("- 冇使用 emoji ← 呢個本身就係一條語氣規則")

    L += ["", "## 稱呼讀者（第二人稱）"]
    if s["address"]:
        for w_, c in s["address"]:
            L.append(f"- 「{w_}」{c} 次")
        L.append("")
        L.append(f"→ 固定用「{s['address'][0][0]}」。**唔好用**冇出現過嘅稱呼。")
    else:
        L.append("- 冇第二人稱 —— 傾向唔直接對讀者講嘢，呢個本身就係一條語氣規則")

    L += ["", "## 受眾稱謂（名詞，唔係稱呼）"]
    if s["audience"]:
        for w_, c in s["audience"]:
            L.append(f"- 「{w_}」{c} 次")
        L.append("")
        L.append(f"→ 提到呢班人嘅時候叫「{s['audience'][0][0]}」。"
                 "呢個同上面嘅第二人稱係兩件事 —— 唔好撈埋，"
                 "「媽媽你好」同「你好」係兩種距離。")
    else:
        L.append("- 冇特定稱謂")

    L += ["", "## CTA 講法"]
    if s["cta"]:
        for v, c in s["cta"]:
            L.append(f"- 「{v}」{c} 次")
    else:
        L.append("- 冇明顯 CTA 動詞 ← 呢個品牌傾向唔硬性收尾")

    if s["top_posts"]:
        L += ["", "## 高表現帖開場（→ 05-hook-library.md）"]
        for t in s["top_posts"]:
            L.append(f"- ({t['likes']}) 「{t['opener']}…」 {t['url']}")

    L += [
        "",
        "## ⚠️ 要人手補嘅（腳本做唔到）",
        "",
        "呢幾項要睇原文先寫得出，但佢哋對「似唔似」嘅影響最大：",
        "",
        "- **禁用詞** — 同行常用、但呢個品牌從來冇用過嘅字眼。逐個列出。",
        "- **語氣關係** — 好似邊種人物關係喺講嘢？（做開嘅朋友／專業顧問／同路人）",
        "- **情緒弧線** — 一篇文由咩情緒開始，去到咩情緒結束？",
        "- **必做動作** — 每篇都會做嘅一件事（例如先認同情緒一句先俾建議）。",
        "- **平台差異** — 同一品牌喺唔同平台嘅講法分別。",
        "",
        "### 驗收",
        "攞呢份檔案，唔睇任何原帖，寫一段 100 字。同真實帖擺埋一齊 —— 分唔分得出？",
        "分得出，即係寫得唔夠具體，返去補上面幾項。",
        "",
    ]
    return "\n".join(L)


def main() -> int:
    p = argparse.ArgumentParser(description="由爬回嚟嘅貼文生成 voice profile 草稿")
    p.add_argument("--input", required=True, help="JSON 檔或資料夾")
    p.add_argument("--output", required=True, help="輸出 .md 路徑，或 - 出到 stdout")
    p.add_argument("--json", action="store_true", help="輸出原始統計 JSON")
    a = p.parse_args()

    posts = load(Path(a.input).expanduser())
    if not posts:
        raise SystemExit("冇讀到任何有 text 嘅記錄。")

    stats = analyse(posts)
    out = json.dumps(stats, ensure_ascii=False, indent=2) if a.json else render(stats)

    if a.output == "-":
        print(out)
    else:
        dst = Path(a.output).expanduser()
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(out + "\n", encoding="utf-8")
        lvl, _ = confidence(stats["n_posts"], stats["sent_len_median"], stats["by_platform"])
        print(f"✓ {dst}")
        print(f"  {stats['n_posts']} 條貼文 · 信心度 {lvl}")
        if lvl != "高":
            print("  ⚠️  信心度唔係「高」—— 交付訊息入面要主動同用戶講。")
        print("  記得補「要人手補嘅」嗰節，尤其禁用詞。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
