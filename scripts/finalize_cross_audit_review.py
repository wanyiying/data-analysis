"""Finalize only after real role files, execution manifest and model-authored claims exist."""
import argparse
import copy
import json
import subprocess
import sys
from pathlib import Path
from da_report import render_report, validate
from reconcile.evidence import dump
from verify_cross_audit_run import verify


def finalize(run):
    # This script never creates role files or invents Agent identifiers.
    roles = {role: json.loads((run / "agents" / f"{role}.json").read_text(encoding="utf-8")) for role in ("locator", "mechanism", "falsifier", "reviewer")}
    execution = json.loads((run / "agents" / "execution.json").read_text(encoding="utf-8"))
    mode = execution.get("mode")
    if mode not in ("native_subagents", "serial_fallback"):
        raise ValueError("invalid_execution_mode")
    if any(r.get("status") not in ("ok", "degraded") for r in roles.values()):
        raise ValueError("role_blocked_or_invalid")
    reviewer = roles["reviewer"]
    if reviewer.get("decision", reviewer.get("verdict", "")) not in ("pass", "downgrade"):
        raise ValueError("reviewer_decision_required")
    if reviewer.get("decision", reviewer.get("verdict")) == "downgrade":
        raise ValueError("reviewer_downgrade_requires_revised_claims_and_new_review")
    arithmetic = verify(run)
    dump(run / "independent-verification.json", arithmetic)
    if arithmetic["status"] != "pass":
        raise ValueError("independent_math_verification_failed")
    evidence = json.loads((run / "evidence.json").read_text(encoding="utf-8"))
    for entry in evidence["evidence"]:
        if entry.get("kind") == "cross_source_calculation" and "exact_values" not in entry:
            # Compatibility for early development run; leave the original evidence untouched.
            entry["exact_values"] = copy.deepcopy(entry["values"])
            entry["values"] = {k: float(v) if isinstance(v, str) else v for k, v in entry["values"].items()}
    dump(run / "evidence-for-verify.json", evidence)
    command = [sys.executable, str(Path(__file__).with_name("da_verify.py")), "--claims", str(run / "claims.json"), "--evidence", str(run / "evidence-for-verify.json"), "--agents-dir", str(run / "agents"), "--require-agent-manifest", "--strict", "--require-evidence-ids"]
    completed = subprocess.run(command, capture_output=True, text=True)
    verification = json.loads(completed.stdout)
    dump(run / "claim-verification.json", verification)
    if completed.returncode or verification["status"] != "pass":
        raise ValueError("upstream_claim_verification_not_pass")
    spec = json.loads((run / "report_spec.json").read_text(encoding="utf-8"))
    spec["meta"]["degraded"]["reason"] = f"Role review ({mode}) and strict claim verification passed. Source correctness, independent system provenance and true root cause remain unestablished."
    # Keep degraded: independent role review cannot upgrade this fixture to a real-business root-cause audit.
    spec["analysis"][0]["tables"] = [spec["analysis"][0].pop("table")] if "table" in spec["analysis"][0] else spec["analysis"][0].get("tables", [])
    claims = json.loads((run / "claims.json").read_text(encoding="utf-8"))["claims"]
    spec["findings"] += [{"title": "已核验差异事实", "body": c["statement"], "level": c["level"], "evidence_ids": c["evidence_ids"], "limitations": c.get("limitations", [])} for c in claims]
    spec["appendix"]["notes"] = [f"Recorded execution mode: {mode}; see agents/execution.json. Local role files alone cannot authenticate Agent execution.", "Role artifacts: agents/locator.json, agents/mechanism.json, agents/falsifier.json, agents/reviewer.json.", "Exact Decimal mathematics: checks.json and independent-verification.json; strict claim check: claim-verification.json.", "evidence-for-verify.json contains the numeric compatibility adapter; original evidence.json is retained.", "No real enterprise deployment or independently authoritative financial source is demonstrated."]
    if validate(spec):
        raise ValueError("invalid_report_spec")
    previous = run / "preliminary-report.html"
    if previous.exists():
        raise ValueError("review_already_finalized")
    previous.write_bytes((run / "report.html").read_bytes())
    dump(run / "reviewed-report-spec.json", spec)
    (run / "report.html").write_text(render_report(spec), encoding="utf-8")
    dump(run / "agent-review.json", {"status": "pass", "mode": mode, "reviewer_decision": reviewer.get("decision", reviewer.get("verdict")), "scope": "Reviewed facts, no established business root cause; local execution manifest is not authenticated"})
    dump(run / "verification.json", {"arithmetic": "pass", "independent_arithmetic": "pass", "upstream_claim_verifier": "pass", "publication": "degraded", "reason": "Synthetic demonstration; source correctness and root cause unestablished."})
    dump(run / "finalization-record.json", {"actual_command": command, "actual_exit": completed.returncode, "retained_preliminary_report": previous.name})
    return {"status": "pass", "run": str(run), "report": str(run / "report.html")}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", required=True, type=Path)
    args = p.parse_args()
    try:
        print(json.dumps(finalize(args.run)))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}))
        raise SystemExit(2)
