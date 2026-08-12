"""Read-only Longbridge market-data and portfolio queries."""

import json
import re
import shutil
import subprocess
from datetime import date, datetime
from pathlib import Path
from typing import Any


_SYMBOL_RE = re.compile(r"^[A-Z0-9][A-Z0-9.-]{0,24}$")
_COMMON_CLI_PATHS = (
    Path("/opt/homebrew/bin/longbridge"),
    Path("/usr/local/bin/longbridge"),
)


def longbridge_quote_action(
    parameters: dict,
    player=None,
    session_memory=None,
) -> str:
    """Run one safe, read-only Longbridge CLI query and summarize its JSON."""
    query_type = str(parameters.get("query_type", "quote")).strip().lower()

    try:
        command = _build_command(query_type, parameters)
    except ValueError as exc:
        return _finish(f"Sir, {exc}", player)

    cli = _find_cli()
    if not cli:
        return _finish(
            "Sir, the Longbridge CLI is not installed or is not on this computer's PATH.",
            player,
        )
    command[0] = cli

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return _finish("Sir, the Longbridge request timed out.", player)
    except OSError as exc:
        return _finish(f"Sir, Longbridge could not be started: {exc}", player)

    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip().splitlines()
        reason = detail[-1][:180] if detail else "unknown CLI error"
        return _finish(f"Sir, Longbridge returned an error: {reason}", player)

    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return _finish("Sir, Longbridge returned an unreadable response.", player)

    message = _summarize(query_type, payload, parameters)
    if session_memory:
        try:
            session_memory.set_last_search(
                query=f"Longbridge {query_type}",
                response=message,
            )
        except Exception:
            pass
    return _finish(message, player)


def _find_cli() -> str | None:
    discovered = shutil.which("longbridge")
    if discovered:
        return discovered
    for candidate in _COMMON_CLI_PATHS:
        if candidate.is_file():
            return str(candidate)
    return None


def _build_command(query_type: str, parameters: dict) -> list[str]:
    if query_type == "quote":
        symbol = _normalize_symbol(parameters.get("symbol"))
        return ["longbridge", "quote", symbol, "--format", "json"]

    if query_type == "portfolio":
        return ["longbridge", "portfolio", "--format", "json"]

    if query_type == "positions":
        return ["longbridge", "positions", "--format", "json"]

    if query_type == "performance":
        command = ["longbridge", "profit-analysis"]
        start, end = _date_range(parameters)
        if start:
            command.extend(["--start", start])
        if end:
            command.extend(["--end", end])
        command.extend(["--format", "json"])
        return command

    raise ValueError("choose quote, portfolio, positions, or performance.")


def _normalize_symbol(raw_symbol: Any) -> str:
    symbol = str(raw_symbol or "").strip().upper()
    if not symbol:
        raise ValueError("please specify a stock symbol.")
    if "." not in symbol and symbol.isalpha():
        symbol = f"{symbol}.US"
    if not _SYMBOL_RE.fullmatch(symbol):
        raise ValueError("the stock symbol is invalid.")
    return symbol


def _date_range(parameters: dict) -> tuple[str | None, str | None]:
    period = str(parameters.get("period", "")).strip().lower()
    if period == "this_month":
        today = date.today()
        return today.replace(day=1).isoformat(), today.isoformat()

    start = _valid_iso_date(parameters.get("start_date"), "start date")
    end = _valid_iso_date(parameters.get("end_date"), "end date")
    if start and end and start > end:
        raise ValueError("the start date must not be after the end date.")
    return start, end


def _valid_iso_date(value: Any, label: str) -> str | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    try:
        return datetime.strptime(text, "%Y-%m-%d").date().isoformat()
    except ValueError as exc:
        raise ValueError(f"the {label} must use YYYY-MM-DD.") from exc


def _summarize(query_type: str, payload: Any, parameters: dict) -> str:
    if query_type == "quote":
        symbol = _normalize_symbol(parameters.get("symbol"))
        row = _first_mapping(payload, required=("symbol",)) or _first_mapping(payload)
        last = _pick(row, "last", "last_done", "last_price", "price")
        currency = _pick(row, "currency") or _currency_for_symbol(symbol)
        previous = _pick(row, "prev_close", "previous_close")
        change = _pick(
            row,
            "change_percentage",
            "change_percent",
            "change_rate",
            "change",
        )
        if last is None:
            return _fallback_summary(f"The latest {symbol} quote", payload)
        details = []
        if change is not None:
            change_text = str(change)
            if not change_text.endswith("%"):
                change_text += "%"
            details.append(f"change {change_text}")
        elif previous is not None:
            details.append(f"previous close {previous}")
        suffix = f", with {', '.join(details)}" if details else ""
        return f"{symbol} is {last} {currency}{suffix}."

    if query_type == "portfolio":
        row = _first_mapping_with_any(
            payload,
            "currency",
            "total_asset",
            "total_assets",
            "net_assets",
            "market_cap",
            "market_value",
            "total_pl",
            "total_pnl",
            "profit_loss",
            "pnl",
        )
        currency = _pick(row, "currency") or "account currency"
        assets = _pick(row, "total_asset", "total_assets", "net_assets")
        market_value = _pick(row, "market_cap", "market_value")
        pnl = _pick(row, "total_pl", "total_pnl", "profit_loss", "pnl")
        fields = _present_fields(
            ("total assets", assets),
            ("market value", market_value),
            ("total P and L", pnl),
        )
        if fields:
            return f"Your portfolio in {currency} has {fields}."
        return _fallback_summary("Your portfolio", payload)

    if query_type == "positions":
        positions = [
            row for row in _all_mappings(payload)
            if _pick(row, "symbol") is not None
            and _pick(row, "quantity", "qty") is not None
        ]
        if not positions:
            return "You currently have no stock positions."
        holdings = []
        for row in positions[:5]:
            holdings.append(
                f"{_pick(row, 'symbol')} {_pick(row, 'quantity', 'qty')} shares"
            )
        extra = f", plus {len(positions) - 5} more" if len(positions) > 5 else ""
        return f"You have {len(positions)} positions: {', '.join(holdings)}{extra}."

    row = _first_mapping_with_any(
        payload,
        "currency",
        "total_pl",
        "total_pnl",
        "profit_loss",
        "pnl",
        "sum_profit",
        "total_simple_earning_yield",
        "total_time_earning_yield",
        "simple_yield",
        "yield",
        "twr",
        "time_weighted_return",
    )
    currency = _pick(row, "currency") or "account currency"
    pnl = _pick(row, "sum_profit", "total_pl", "total_pnl", "profit_loss", "pnl")
    simple_yield = _as_percentage(
        _pick(row, "total_simple_earning_yield", "simple_yield", "yield")
    )
    twr = _as_percentage(
        _pick(row, "total_time_earning_yield", "twr", "time_weighted_return")
    )
    fields = _present_fields(
        ("P and L", pnl),
        ("simple yield", simple_yield),
        ("time-weighted return", twr),
    )
    period = "this month" if parameters.get("period") == "this_month" else "the requested period"
    if fields:
        return f"For {period}, your portfolio in {currency} has {fields}."
    return _fallback_summary(f"Your portfolio performance for {period}", payload)


def _first_mapping(payload: Any, required: tuple[str, ...] = ()) -> dict:
    for row in _all_mappings(payload):
        lowered = {str(key).lower() for key in row}
        if all(key.lower() in lowered for key in required):
            return row
    return {}


def _first_mapping_with_any(payload: Any, *keys: str) -> dict:
    wanted = {key.lower() for key in keys}
    for row in _all_mappings(payload):
        if wanted.intersection(str(key).lower() for key in row):
            return row
    return _first_mapping(payload)


def _all_mappings(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _all_mappings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _all_mappings(child)


def _pick(row: dict, *keys: str):
    lowered = {str(key).lower(): value for key, value in row.items()}
    for key in keys:
        value = lowered.get(key.lower())
        if value not in (None, ""):
            return value
    return None


def _present_fields(*items: tuple[str, Any]) -> str:
    return ", ".join(f"{label} {value}" for label, value in items if value is not None)


def _as_percentage(value: Any) -> Any:
    if value in (None, ""):
        return None
    text = str(value).strip()
    if text.endswith("%"):
        return text
    try:
        return f"{float(text) * 100:.2f}%"
    except ValueError:
        return text


def _fallback_summary(label: str, payload: Any) -> str:
    row = next(
        (
            candidate
            for candidate in _all_mappings(payload)
            if any(isinstance(value, (str, int, float, bool)) for value in candidate.values())
        ),
        {},
    )
    values = []
    for key, value in row.items():
        if isinstance(value, (str, int, float, bool)) and value not in ("", None):
            values.append(f"{str(key).replace('_', ' ')} {value}")
        if len(values) == 3:
            break
    return f"{label}: {', '.join(values)}." if values else f"{label} is unavailable."


def _currency_for_symbol(symbol: str) -> str:
    market = symbol.rsplit(".", 1)[-1]
    return {"US": "USD", "HK": "HKD", "SG": "SGD", "SH": "CNY", "SZ": "CNY"}.get(
        market,
        "",
    )


def _finish(message: str, player=None) -> str:
    print(f"[Longbridge] {message}")
    if player:
        try:
            player.write_log(f"JARVIS: {message}")
        except Exception:
            pass
    return message
