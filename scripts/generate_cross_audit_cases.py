"""Reproducible tiny fixtures. Expected answers are hand-written, never engine output."""
import copy
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "examples" / "cross_audit"


def base_contract():
    source = {"fields": {"id": "id", "date": "date", "region": "region", "amount": "amount"}, "grain": ["id"],
              "date": {"field": "date", "format": "%Y-%m-%d", "meaning": "order_date"},
              "scope": {"start": "2026-01-01", "end": "2026-01-31", "population": "all_test_orders", "cutoff": "2026-02-01T00:00:00+08:00", "filters": {}},
              "metrics": {"amount": {"definition": "signed transaction amount including returns", "aggregation": "sum", "unit": "yuan", "currency": "CNY", "multiplier": "1"}}}
    return {"schema_version": 1, "confirmed": True, "mode": "exact", "keys": ["id"], "metrics": ["amount"],
            "row_tolerance": "0", "total_tolerance": "0", "sources": {"a": copy.deepcopy(source), "b": copy.deepcopy(source)}}


def cases():
    base = [["001", "2026-01-01", "east", "10"], ["002", "2026-01-01", "west", "20"]]
    result = []
    def add(name, a=None, b=None, change=None, **expected):
        c = base_contract()
        if change:
            change(c)
        result.append((name, copy.deepcopy(base if a is None else a), copy.deepcopy(base if b is None else b), c, expected))
    add("consistent", state="READY_EXACT", consistency="consistent", net="0", absolute="0")
    add("value_mismatch", b=[base[0], ["002", "2026-01-01", "west", "17"]], state="READY_EXACT", consistency="different", net="3", absolute="3")
    add("only_a", b=[base[0]], state="READY_EXACT", consistency="different", net="20", only_a="20")
    add("only_b", a=[base[0]], state="READY_EXACT", consistency="different", net="-20", only_b="20")
    def agg(c):
        c.update(mode="aggregate", keys=["date", "region"])
        c["sources"]["a"]["grain"] = ["id", "date", "region"]
        c["sources"]["b"]["grain"] = ["date", "region"]
    add("aggregate", a=[base[0], ["003", "2026-01-01", "east", "5"], base[1]], b=[["x", "2026-01-01", "east", "15"], base[1]], change=agg, state="READY_AGGREGATE", consistency="consistent", net="0")
    add("duplicate", a=base+[base[0]], error="duplicate_grain_many_to_many_risk")
    add("many_to_many", a=base+[base[0]], b=base+[base[0]], error="duplicate_grain_many_to_many_risk")
    add("null_key", a=[["", "2026-01-01", "east", "10"]], error="null_business_key")
    def unit(c):
        c["sources"]["b"]["date"]["format"] = "%d/%m/%Y"
        c["sources"]["b"]["metrics"]["amount"]["multiplier"] = "0.01"
    add("normalized", b=[["001", "01/01/2026", "east", "1000"], ["002", "01/01/2026", "west", "2000"]], change=unit, state="READY_EXACT", consistency="consistent", net="0")
    add("definition", change=lambda c: c["sources"]["b"]["metrics"]["amount"].update(definition="recognized revenue"), error="metric_semantics_mismatch")
    add("coverage", change=lambda c: c["sources"]["b"]["scope"].update(end="2026-01-30"), error="scope_or_cutoff_mismatch")
    add("offset", b=[["001", "2026-01-01", "east", "5"], ["002", "2026-01-01", "west", "25"]], state="READY_EXACT", consistency="different", net="0", absolute="10")
    add("tolerance_boundary", b=[["001", "2026-01-01", "east", "9.99"], base[1]], change=lambda c: c.update(row_tolerance="0.01", total_tolerance="0.01"), state="READY_EXACT", consistency="consistent", net="0.01")
    add("cumulative_tolerance", b=[["001", "2026-01-01", "east", "9.99"], ["002", "2026-01-01", "west", "19.99"]], change=lambda c: c.update(row_tolerance="0.01", total_tolerance="0.01"), state="READY_EXACT", consistency="different", net="0.02")
    neg = [["001", "2026-01-01", "east", "-10"], ["002", "2026-01-01", "west", "0"]]
    add("negative_zero", a=neg, b=neg, state="READY_EXACT", consistency="consistent", net="0")
    add("missing_amount", a=[["001", "2026-01-01", "east", ""]], error="missing_amount")
    add("no_alignment", change=lambda c: c.update(keys=[]), error="no_common_keys")
    add("confirmation", change=lambda c: c.update(confirmed=False), state="NEEDS_CONFIRMATION", error="business_confirmation_required")
    add("total", change=lambda c: c.update(mode="total", keys=[], allow_total=True), state="AGGREGATE_ONLY", consistency="aggregate_consistent", net="0")
    add("date_meaning", change=lambda c: c["sources"]["b"]["date"].update(meaning="posting_date"), error="date_meaning_mismatch")
    add("unit_mismatch", change=lambda c: c["sources"]["b"]["metrics"]["amount"].update(unit="dollar"), error="metric_semantics_mismatch")
    add("unmatched_both", a=[base[0]], b=[base[1]], state="READY_EXACT", consistency="different", net="-10", absolute="30", only_a="10", only_b="20")
    return result


def main():
    for name, a, b, config, expected in cases():
        path = ROOT / name
        path.mkdir(parents=True, exist_ok=True)
        for side, rows in (("a", a), ("b", b)):
            with (path / f"{side}.csv").open("w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f, lineterminator="\n")
                writer.writerow(["id", "date", "region", "amount"])
                writer.writerows(rows)
        for filename, obj in (("contract.json", config), ("expected.json", expected)):
            (path / filename).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(f"Generated {len(cases())} deterministic cases at {ROOT}")


if __name__ == "__main__":
    main()
