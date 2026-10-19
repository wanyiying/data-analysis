"""Independent artifact arithmetic verification, separate from engine and claim verifier."""
import argparse
import csv
import hashlib
import json
from decimal import Decimal, localcontext
from pathlib import Path


def verify(run):
    summary = json.loads((run / "summary.json").read_text(encoding="utf-8"))
    manifest = json.loads((run / "manifest.json").read_text(encoding="utf-8"))
    config = json.loads((run / "contract.json").read_text(encoding="utf-8"))
    failures = []
    contract_hash = hashlib.sha256(json.dumps(config, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    if manifest.get("config_sha256") != contract_hash:
        failures.append("contract_hash_mismatch")
    if set(manifest.get("inputs", {})) != {"a", "b"}:
        failures.append("two_input_manifests_required")
    for side, info in manifest["inputs"].items():
        path = Path(info["path"])
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != info["sha256"]:
            failures.append(f"{side}:input_hash_mismatch")
    if not summary.get("metrics"):
        return {"status": "fail" if failures else "not_assessed", "failures": failures, "reason": "No comparable metrics were calculated."}
    if set(summary["metrics"]) != set(config["metrics"]):
        failures.append("metric_set_mismatch")
    if summary.get("execution") != "success":
        failures.append("execution_status_mismatch")
    with (run / "details.csv").open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    def number(text):
        # CSV formula protection prefixes signed numeric output for safe spreadsheet opening.
        return Decimal(text[1:] if text.startswith("'") else text)
    with localcontext() as ctx:
        ctx.prec = 128
        for metric, values in summary["metrics"].items():
            selected = [r for r in rows if r["metric"] == metric]
            if not selected:
                failures.append(f"{metric}:missing_details")
                continue
            a = sum((number(r["a"]) for r in selected if r["a"]), Decimal(0))
            b = sum((number(r["b"]) for r in selected if r["b"]), Decimal(0))
            matched = only_a = only_b = absolute = positive = negative = Decimal(0)
            mismatch_count = unmatched_count = 0
            for row in selected:
                if row["a"] and row["b"]:
                    diff = number(row["a"]) - number(row["b"])
                    if number(row["difference"]) != diff:
                        failures.append(f"{metric}:detail_difference")
                    matched += diff
                    status = "matched" if abs(diff) <= Decimal(config.get("row_tolerance", "0")) else "value_mismatch"
                    mismatch_count += status == "value_mismatch"
                elif row["a"]:
                    only_a += number(row["a"])
                    diff, status = number(row["a"]), "only_in_a"
                    unmatched_count += 1
                elif row["b"]:
                    only_b += number(row["b"])
                    diff, status = -number(row["b"]), "only_in_b"
                    unmatched_count += 1
                else:
                    failures.append(f"{metric}:empty_pair")
                    continue
                if row["status"] != status:
                    failures.append(f"{metric}:detail_status")
                absolute += abs(diff)
                positive += max(Decimal(0), diff)
                negative += min(Decimal(0), diff)
            expected = {"a_total": a, "b_total": b, "matched_difference": matched, "only_a_total": only_a,
                        "only_b_total": only_b, "net_difference": a-b, "absolute_difference": absolute,
                        "positive_difference": positive, "negative_difference": negative,
                        "mismatch_count": mismatch_count, "unmatched_count": unmatched_count}
            for field, value in expected.items():
                if Decimal(str(values[field])) != value:
                    failures.append(f"{metric}:{field}")
            if a-b != matched+only_a-only_b:
                failures.append(f"{metric}:identity")
            consistent = mismatch_count == unmatched_count == 0 and abs(a-b) <= Decimal(config.get("total_tolerance", "0"))
            if values["within_tolerance"] != consistent or values["identity_valid"] is not True:
                failures.append(f"{metric}:summary_status")
    expected_status = "consistent" if all(s["within_tolerance"] for s in summary["metrics"].values()) else "different"
    if config["mode"] == "total":
        expected_status = "aggregate_" + expected_status
    expected_alignment = {"exact": "READY_EXACT", "aggregate": "READY_AGGREGATE", "total": "AGGREGATE_ONLY"}[config["mode"]]
    if summary.get("consistency") != expected_status or summary.get("alignment", {}).get("state") != expected_alignment:
        failures.append("top_level_status_mismatch")
    return {"status": "fail" if failures else "pass", "failures": failures,
            "scope": "Source hashes, exported detail arithmetic and summary agreement. Does not prove source business correctness or re-establish key semantics."}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", required=True, type=Path)
    args = p.parse_args()
    try:
        result = verify(args.run)
    except (OSError, ValueError, KeyError, TypeError):
        result = {"status": "fail", "failures": ["malformed_or_missing_artifact"]}
    (args.run / "independent-verification.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result))
    return 1 if result["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
