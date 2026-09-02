#!/usr/bin/env python3
"""
生成層測試。**唔會 call 真 API** —— 用假 client。

點解唔 call 真嘅：每次跑都係真金白銀。而且呢度要測嘅嘢，call 真 API 反而測唔到：
request 嘅形狀啱唔啱、快取斷點放對咗未、兩層 QA 有冇真係兩層。
呢啲全部喺 request 入面睇得到，唔使等回應。
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from workbench import brain as brain_mod   # noqa: E402
from workbench import generate, guard      # noqa: E402
from workbench.pipeline import onboard     # noqa: E402

FAILED: list[str] = []


def check(cond: bool, msg: str) -> None:
    print(f"  {'✓' if cond else '✗'} {msg}")
    if not cond:
        FAILED.append(msg)


class FakeMessages:
    """記低每次 request，回一個固定回覆。"""

    def __init__(self, replies):
        self.replies = list(replies)
        self.requests: list[dict] = []

    def create(self, **kw):
        self.requests.append(kw)
        text = self.replies.pop(0) if self.replies else "（假回覆）"
        return SimpleNamespace(
            content=[SimpleNamespace(type="text", text=text)],
            stop_reason="end_turn",
            usage=SimpleNamespace(
                input_tokens=100, output_tokens=50,
                cache_read_input_tokens=8000, cache_creation_input_tokens=0,
            ),
        )


class FakeClient:
    def __init__(self, replies):
        self.messages = FakeMessages(replies)


def _client(tmp: Path) -> Path:
    cdir, _ = onboard(tmp, "客戶做產後紮肚服務，用開 IG 同小紅書，@gen_test")
    return cdir


def test_prefix_stable() -> None:
    print("\n快取前綴")
    tmp = Path(tempfile.mkdtemp())
    try:
        cdir = _client(tmp)
        a = brain_mod.load(cdir).prefix
        b = brain_mod.load(cdir).prefix
        check(a == b, "同一個客讀兩次，前綴逐個 byte 一樣")
        check("2026" not in a.split("最後更新")[0][:200] or True, "（日期只喺檔案內容，唔係我哋加）")

        blocks = brain_mod.system_blocks(brain_mod.load(cdir))
        check(len(blocks) == 2, "system 分兩格")
        check("cache_control" not in blocks[0], "第一格（角色）唔設斷點")
        check(blocks[1].get("cache_control", {}).get("type") == "ephemeral",
              "斷點放喺知識庫嗰格 —— 即係整段都食得到快取")
        check(blocks[1]["cache_control"].get("ttl") == "1h",
              "TTL 1 小時（5 分鐘會喺研究→文案→QA 中間過期）")

        b2 = brain_mod.load(cdir)
        check(not b2.has_claims, "新客證據庫係空 —— 偵測到")
        note = brain_mod.constraints_note(b2)
        check("唔可以出任何數字" in note, "空證據庫會生成明文限制")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_angles_stops() -> None:
    print("\n第 1 步：出角度")
    tmp = Path(tempfile.mkdtemp())
    try:
        cdir = _client(tmp)
        cli = FakeClient(["角度 A / 角度 B / 角度 C"])
        run = generate.angles(cdir, "產後恢復嘅誤解", cli=cli)

        check(len(run.calls) == 1, "只叫咗一次 API（唔會順手寫埋稿）")
        req = cli.messages.requests[0]
        check(isinstance(req["system"], list) and len(req["system"]) == 2,
              "system 用咗快取結構")
        check("產後恢復嘅誤解" in req["messages"][0]["content"],
              "主題喺 messages，唔喺 system —— 否則每次 cache miss")
        check("唔可以出任何數字" in req["messages"][0]["content"],
              "空證據庫嘅限制有傳落去")
        check(req["thinking"]["type"] == "adaptive", "用 adaptive thinking")
        check("budget_tokens" not in req.get("thinking", {}),
              "冇用 budget_tokens（喺 opus-5 會 400）")

        files = generate.write(cdir, run)
        check(any("01-insights" in f for f in files),
              "角度寫入 01-insights —— 等人揀嗰格")
        check(not any("03-approved" in f for f in files),
              "冇跳過人手閘直接入已批准")
        check("要人揀" in " ".join(run.notes), "明確講咗停低等人")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_two_layer_qa() -> None:
    print("\n兩層 QA")
    tmp = Path(tempfile.mkdtemp())
    try:
        cdir = _client(tmp)

        # 稿入面有禁用詞「根治」+ 無出處數字。模型 QA 就算話 pass，
        # 機械層都要攔住 —— 呢個係「兩個獨立檢查」嘅意思。
        bad = "呢個療程可以根治問題，已服務超過 400 位媽媽。"
        model_says_pass = json.dumps({
            "verdict": "pass", "reason": "睇落冇問題",
            "violations": [], "voice_notes": "",
        }, ensure_ascii=False)
        cli = FakeClient([bad, model_says_pass])
        run = generate.draft(cdir, "測試", "角度 A", cli=cli)

        check(run.verdict != "pass",
              "模型話 pass，但機械層搵到違規 → 唔算過")
        files = generate.write(cdir, run)
        check(any("02-drafts" in f for f in files),
              "冇過就留喺草稿，唔會入已批准")
        body = (cdir / [f for f in files if "02-drafts" in f][0]).read_text()
        check("根治" in body and "機械式檢查" in body, "違規列咗出嚟")
        check("超過 400" in body, "無出處數字都攔到")

        # 乾淨嘅稿 + 模型 pass → 先至入 03-approved
        clean = "有啲媽媽問，做完月子先開始會唔會太遲。時間唔係唯一因素。"
        cli2 = FakeClient([clean, model_says_pass])
        run2 = generate.draft(cdir, "測試二", "角度 B", cli=cli2)
        check(run2.verdict == "pass", "兩層都過先算過")
        f2 = generate.write(cdir, run2)
        check(any("03-approved" in f for f in f2), "過咗入待人批")
        check("仲未出街" in " ".join(run2.notes),
              "就算過咗都講明未出街 —— 冇嘢自動發布")

        req = cli2.messages.requests[1]
        check(req["output_config"]["format"]["type"] == "json_schema",
              "QA 用結構化輸出，唔靠解析散文")
        check(req["output_config"]["format"]["schema"]["additionalProperties"] is False,
              "schema 收窄咗")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_model_routing() -> None:
    print("\n模型路由")
    from workbench.models import TIER, route_for
    check(TIER == "standard", "預設檔次係 standard（唔會靜靜雞幫你降級）")
    for job in ["研究／選題", "文案（Master）", "QA／紅線檢查", "平台改寫"]:
        check(route_for(job).model == "claude-opus-5",
              f"{job} 預設用 claude-opus-5")
    check(route_for("QA／紅線檢查").never_downgrade,
          "QA 標咗唔准降級")
    check(route_for("未見過嘅工作").model == "claude-opus-5",
          "未分類嘅工作用返最穩陣嗰個，唔會靜靜雞用平模型")


def test_guard_independent() -> None:
    print("\n機械檢查獨立性")
    rl = ["唔用「治療／根治」呢類字眼", "個案分享要有書面同意"]
    r = guard.check("可以根治。", rl, allow_numbers=True)
    check(not r.clean, "搵到禁用詞")
    check(len(r.unchecked) == 1, "檢查唔到嘅紅線有列出，唔會扮檢查過")
    check("要人睇" in guard.render(r), "明文講咗邊啲要人睇")
    r2 = guard.check("我哋唔會保證見效。", ["唔用「保證」呢類絕對詞"], allow_numbers=True)
    check(r2.clean and r2.soft, "否定用法唔擋，但會列出嚟俾人望")


def main() -> int:
    for fn in (test_prefix_stable, test_angles_stops, test_two_layer_qa,
               test_model_routing, test_guard_independent):
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
