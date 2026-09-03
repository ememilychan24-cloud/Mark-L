#!/usr/bin/env python3
"""
把瀏覽器讀返嚟嘅圖片特徵，寫成 brand-visual.md。

點解喺瀏覽器度分析，唔喺呢邊：
  1. 唔使裝任何嘢（Pillow、OpenCV 全部唔使）
  2. **啲圖唔使離開用戶部機。** 呢個唔係細節 —— 呢個工作台服務嘅客入面，
     有啲嘅參考圖係客人身體。冇理由要佢哋上載去一個 server 先分析到顏色。

瀏覽器交返嚟嘅格式（見 static/setup.html）：
  {"n": 24,
   "palette": [{"hex":"#5F7043","share":0.31}, ...],   # 由多到少
   "light": 0.62,          # 平均亮度 0–1
   "sat": 0.28,            # 平均飽和度 0–1
   "portrait": 0.83,       # 直度圖佔比
   "edge": 0.11}           # 邊緣密度，用嚟粗略估「圖入面有幾多字／細節」

呢度做嘅唔係「認出風格」，係**把觀察到嘅數字寫低**，同 voice-profile 一樣嘅原則：
可驗證嘅數字，先至令兩個唔同嘅人做出似嘅嘢。
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

# 常見嘅「模型會自己加，但品牌通常冇」嘅元素。
# 呢個清單係 brand-visual.md 入面最有用嗰欄：唔寫低，生圖模型一定會加。
COMMON_ADDITIONS = ["漸變", "金色點綴", "bokeh 散景", "光暈", "閃粉", "純黑背景"]


HUE_BUCKETS = ("紅／粉", "黃／橙", "綠", "藍／紫")
COOL = {"藍／紫"}


def _hue_of(hexcode: str) -> str | None:
    """一隻色屬邊個色系。中性色（灰、白、米、炭）回 None。

    一定要用色相角，唔可以用 R/G/B 邊個大。之前用大小比較，
    琥珀色 #E8A530 被判做「紅」—— 於是「從來冇出現」欄會叫生圖模型避開
    「黃／橙」，即係避開咗品牌自己嘅強調色。呢種錯冇人會 review 到，
    只會見到出嚟嘅圖唔似品牌而唔知點解。
    """
    h = hexcode.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    mx, mn = max(r, g, b), min(r, g, b)
    d = mx - mn
    if d < 25:                     # 近乎中性 —— 唔屬於任何色系
        return None
    if mx == r:
        hue = (60 * ((g - b) / d)) % 360
    elif mx == g:
        hue = 60 * (2 + (b - r) / d)
    else:
        hue = 60 * (4 + (r - g) / d)
    if hue < 20 or hue >= 330:
        return "紅／粉"
    if hue < 70:
        return "黃／橙"
    if hue < 165:
        return "綠"
    return "藍／紫"


def _missing_hues(hexes: list[str]) -> list[str]:
    """邊啲色系完全冇出現。呢個比「有咩色」更有用 —— 生圖模型要嘅係禁令。"""
    seen = {_hue_of(h) for h in hexes} - {None}
    return [k for k in HUE_BUCKETS if k not in seen]


def _warmth(hexes: list[str]) -> str:
    """冷暖描述。由同一個色相分類推導，唔另外計 ——
    兩行講嘅嘢一定要一致，否則檔案自己打自己嘴巴。"""
    seen = {_hue_of(h) for h in hexes} - {None}
    if not seen:
        return "全部中性色（灰、白、米、炭），冇明顯色相"
    cool, warm = seen & COOL, seen - COOL
    if warm and not cool:
        return "全部暖色 —— 冷色（藍／紫）從來冇出現過"
    if cool and not warm:
        return "全部冷色 —— 暖色從來冇出現過"
    return "冷暖都有：" + "、".join(sorted(seen))


def render(v: dict) -> str:
    """由分析結果生成 brand-visual.md。"""
    n = int(v.get("n", 0))
    pal = v.get("palette", []) or []
    hexes = [p["hex"] for p in pal]

    if n == 0:
        conf, why = "未建立", "未有參考圖。"
    elif n < 8:
        conf, why = "低", f"只有 {n} 張圖，統計意義有限。呢啲色可能只係嗰幾張嘅巧合。"
    elif n < 20:
        conf, why = "中", f"{n} 張圖。夠睇到大方向，但個別細節（排版、字級）仲要人手確認。"
    else:
        conf, why = "高", f"{n} 張圖，色彩分佈已經穩定。"

    light = float(v.get("light", 0) or 0)
    sat = float(v.get("sat", 0) or 0)
    portrait = float(v.get("portrait", 0) or 0)
    edge = float(v.get("edge", 0) or 0)

    tone = ("偏光、通透" if light > 0.66 else
            "偏暗、沉穩" if light < 0.38 else "中間調")
    satdesc = ("低飽和、素淨" if sat < 0.22 else
               "高飽和、鮮明" if sat > 0.5 else "中等飽和")
    shape = ("以直度圖為主" if portrait > 0.65 else
             "以橫度圖為主" if portrait < 0.35 else "直橫都有")
    density = ("留白多，圖入面文字／細節少" if edge < 0.09 else
               "資訊密度高，圖入面字多" if edge > 0.18 else "中等密度")

    missing = _missing_hues(hexes)
    never = list(COMMON_ADDITIONS)
    if missing:
        never = [f"{m} 色系" for m in missing] + never

    L = [
        "# 品牌視覺 Brand Visual",
        "",
        f"> 樣本：{n} 張 · 信心度：**{conf}** — {why}",
        f"> 由設定精靈喺瀏覽器分析。原圖冇離開過用戶部機。",
        f"> 更新：{date.today().isoformat()}",
        "",
        "## 色彩",
    ]
    if pal:
        for i, p in enumerate(pal[:6]):
            role = ("主色" if i == 0 else "輔色" if i == 1 else
                    "強調色" if i == 2 else "次要色")
            L.append(f"- {role}：`{p['hex']}`（出現佔比 {round(float(p.get('share', 0)) * 100)}%）")
        L.append(f"- 冷暖：{_warmth(hexes)}")
    else:
        L.append("- <未有參考圖，要人手填>")

    L += [
        "",
        "- **從來冇出現**（呢欄最重要）：" + "、".join(never),
        "  → 冇寫低呢一欄，生圖模型會自己加。呢個係「生成出嚟唔似品牌」嘅頭號原因。",
        "",
        "## 畫風",
        f"- 光線：{tone}（平均亮度 {round(light * 100)}/100）",
        f"- 色彩濃度：{satdesc}（平均飽和 {round(sat * 100)}/100）",
        f"- 構圖比例：{shape}（直度圖佔 {round(portrait * 100)}%）",
        f"- 資訊密度：{density}（邊緣密度 {round(edge, 3)}）",
        "- 攝影 / 插畫比例：<要人手睇一眼填>",
        "- 主體處理：<要人手填 —— 例如「一定唔露樣」、「只影產品唔影人」>",
        "",
        "## 排版",
        "- 字體：<要人手填>",
        "- 每張圖文字量：" + ("少（≤ 15 字）" if edge < 0.09 else
                              "多（可以 30 字以上）" if edge > 0.18 else "中等（15–25 字）"),
        "- 文字位置：<要人手填>",
        "",
        "## ⚠️ 呢幾樣機器讀唔到，一定要人答",
        "- 有冇官方品牌指引？（如有，覆蓋以上全部觀察）",
        "- Logo 使用規則同安全距離",
        "- 身體／人物入鏡嘅界線（邊個部位可以影、要唔要露樣）",
        "- 有冇唔可以用嘅顏色或元素",
        "",
    ]
    if v.get("handles"):
        L += [
            "## 參考帳號（未爬取）",
            *[f"- @{h} —— 記錄低咗，但**未爬過**。"
              "呢個工作台唔會自動登入去攞你嘅帖；要嘅話由你匯出再掉入嚟。"
              for h in v["handles"]],
            "",
        ]
    return "\n".join(L)


def write(cdir: Path, v: dict) -> bool:
    """寫入 client workspace。冇分析結果就唔寫，保留 scaffold 嘅空殼。"""
    if not v or not v.get("n"):
        return False
    (cdir / "style").mkdir(parents=True, exist_ok=True)
    (cdir / "style" / "brand-visual.md").write_text(render(v), encoding="utf-8")
    return True
