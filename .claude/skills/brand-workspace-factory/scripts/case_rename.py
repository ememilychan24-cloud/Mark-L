#!/usr/bin/env python3
"""
把客戶原始相片改名成自帶索引嘅檔名。

點解用檔名做索引，唔用另一份 CSV：CSV 要人手維護，而且一定會同實際檔案脫節 ——
改咗個檔名、搬咗個位、加多兩張，CSV 就錯咗而冇人知。檔名跟住檔案走，
搬去邊都仲係啱。sort、glob、配對 before/after 全部直接做得到。

命名格式：
    <case>_<stage>_<seq>_<date>.<ext>
    SS001_d01_01_2026-08-20.jpg
    SS001_d11_01_2026-08-30.jpg

  case   案例編號（唔用姓名 —— 姓名唔應該出現喺檔名）
  stage  由最早嗰日起計嘅日數：d01、d11、d90
  seq    同一日入面嘅序號
  date   拍攝日期（EXIF 優先，冇就用檔案時間）

配對 before/after = 同一個 case、同一個 seq、唔同 stage。

用法:
  # 先睇計劃，唔會改任何嘢（預設）
  python case_rename.py --dir <資料夾> --case SS001

  # 確認冇問題先執行
  python case_rename.py --dir <資料夾> --case SS001 --apply

  # 改錯咗，全部還原
  python case_rename.py --dir <資料夾> --undo

每次 --apply 都會喺同一個資料夾寫低 `_rename-log.csv`（原檔名 → 新檔名）。
呢個 log 有兩個用途：還原，同埋日後追返「呢張係邊個原檔」。唔好刪。
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from datetime import datetime, date as _date
from pathlib import Path

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".webp", ".tif", ".tiff"}
LOG_NAME = "_rename-log.csv"
CASE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]{0,15}$")


def exif_date(p: Path) -> _date | None:
    """讀 EXIF 拍攝日期。冇 Pillow 或者讀唔到就回 None，由呼叫方 fallback。"""
    try:
        from PIL import Image, ExifTags
    except ImportError:
        return None
    try:
        with Image.open(p) as im:
            raw = im.getexif()
            if not raw:
                return None
            tags = {ExifTags.TAGS.get(k, k): v for k, v in raw.items()}
            for key in ("DateTimeOriginal", "DateTimeDigitized", "DateTime"):
                v = tags.get(key)
                if isinstance(v, str):
                    return datetime.strptime(v[:10], "%Y:%m:%d").date()
    except Exception:
        return None
    return None


def taken(p: Path) -> tuple[_date, bool]:
    """回 (日期, 係咪由 EXIF 嚟)。冇 EXIF 就用檔案修改時間。"""
    d = exif_date(p)
    if d:
        return d, True
    return datetime.fromtimestamp(p.stat().st_mtime).date(), False


def plan(files: list[Path], case: str) -> list[tuple[Path, str, bool]]:
    """算出每個檔嘅新名。回 [(原路徑, 新檔名, EXIF 有冇日期)]。"""
    dated = [(p, *taken(p)) for p in files]
    dated.sort(key=lambda t: (t[1], t[0].name.lower()))

    base = dated[0][1]
    seq_per_day: dict[_date, int] = {}
    out = []
    for p, d, from_exif in dated:
        day = (d - base).days + 1
        seq_per_day[d] = seq_per_day.get(d, 0) + 1
        new = f"{case}_d{day:02d}_{seq_per_day[d]:02d}_{d.isoformat()}{p.suffix.lower()}"
        out.append((p, new, from_exif))
    return out


def cmd_rename(a) -> int:
    d = Path(a.dir).expanduser().resolve()
    if not d.is_dir():
        print(f"✗ 唔係資料夾：{d}", file=sys.stderr)
        return 2
    if not CASE_RE.match(a.case):
        print(f"✗ 案例編號只可以用英數同 -，最多 16 個字：{a.case}", file=sys.stderr)
        print("  （用編號，唔好用姓名 —— 姓名唔應該出現喺檔名。）", file=sys.stderr)
        return 2

    files = [p for p in sorted(d.iterdir())
             if p.is_file() and p.suffix.lower() in IMAGE_EXT and not p.name.startswith("_")]
    if not files:
        print(f"喺 {d} 搵唔到圖片檔。")
        return 0

    rows = plan(files, a.case)
    no_exif = sum(1 for _, _, e in rows if not e)

    print(f"{'執行' if a.apply else '計劃（未改任何嘢）'}：{d}")
    print(f"{len(rows)} 個檔案\n")
    width = max(len(p.name) for p, _, _ in rows)
    for p, new, from_exif in rows:
        mark = " " if from_exif else "~"
        print(f"  {mark} {p.name:<{width}}  →  {new}")

    if no_exif:
        print(f"\n⚠️  {no_exif} 個檔冇 EXIF 拍攝日期，用咗檔案修改時間（上面標 ~）。")
        print("   檔案修改時間會被複製、匯出、傳送改變 —— 呢啲日期要人手核對過先當準。")
    try:
        import PIL  # noqa: F401
    except ImportError:
        print("\n⚠️  冇裝 Pillow，所以完全讀唔到 EXIF，全部用咗檔案時間。")
        print("   裝返：pip install Pillow")

    conflicts = [n for _, n, _ in rows if (d / n).exists() and (d / n) not in {p for p, _, _ in rows}]
    if conflicts:
        print(f"\n✗ 目標檔名已經存在：{', '.join(conflicts[:5])}", file=sys.stderr)
        return 1

    if not a.apply:
        print("\n睇啱就加 --apply 執行。")
        return 0

    log = d / LOG_NAME
    existed = log.exists()
    with log.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not existed:
            w.writerow(["timestamp", "old", "new", "date_source"])
        stamp = datetime.now().isoformat(timespec="seconds")
        done = 0
        for p, new, from_exif in rows:
            target = d / new
            if target == p:
                continue
            p.rename(target)
            w.writerow([stamp, p.name, new, "exif" if from_exif else "mtime"])
            done += 1

    print(f"\n✓ 改咗 {done} 個檔案")
    print(f"✓ 記錄寫入 {log.name} —— 呢個係還原同追溯嘅唯一憑證，唔好刪。")
    print("\n下一步：喺 data/consent/_PROCESSING.md 開返對應嘅案例行。")
    return 0


def cmd_undo(a) -> int:
    d = Path(a.dir).expanduser().resolve()
    log = d / LOG_NAME
    if not log.exists():
        print(f"✗ 搵唔到 {LOG_NAME}，還原唔到。", file=sys.stderr)
        return 1

    with log.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        print("記錄係空。")
        return 0

    last = rows[-1]["timestamp"]
    batch = [r for r in rows if r["timestamp"] == last]
    print(f"還原最後一批（{last}），{len(batch)} 個檔案：\n")

    done = 0
    for r in reversed(batch):
        src, dst = d / r["new"], d / r["old"]
        if not src.exists():
            print(f"  ⚠️  搵唔到 {r['new']}，跳過")
            continue
        if dst.exists():
            print(f"  ⚠️  {r['old']} 已存在，跳過")
            continue
        if a.apply:
            src.rename(dst)
            done += 1
        print(f"  {r['new']}  →  {r['old']}")

    if not a.apply:
        print("\n睇啱就加 --apply 執行。")
        return 0

    remaining = [r for r in rows if r["timestamp"] != last]
    with log.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["timestamp", "old", "new", "date_source"])
        for r in remaining:
            w.writerow([r["timestamp"], r["old"], r["new"], r["date_source"]])

    print(f"\n✓ 還原咗 {done} 個檔案")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="把客戶原始相片改名成自帶索引嘅檔名",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("用法:")[1] if "用法:" in __doc__ else None,
    )
    ap.add_argument("--dir", required=True, help="圖片資料夾")
    ap.add_argument("--case", help="案例編號，例如 SS001（--undo 時唔使）")
    ap.add_argument("--apply", action="store_true", help="真係執行；唔加就只係睇計劃")
    ap.add_argument("--undo", action="store_true", help="用 _rename-log.csv 還原最後一批")
    a = ap.parse_args()

    if a.undo:
        return cmd_undo(a)
    if not a.case:
        ap.error("改名要 --case（或者用 --undo 還原）")
    return cmd_rename(a)


if __name__ == "__main__":
    raise SystemExit(main())
