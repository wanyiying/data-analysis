#!/usr/bin/env python3
"""Audit two local CSV/XLSX sources under an explicitly confirmed KPI contract."""
import argparse
import json
import sys
from pathlib import Path
from reconcile.contract import AuditError
from reconcile.loader import load
from reconcile.profiler import profile
from reconcile.engine import audit
from reconcile.evidence import new_run, emit


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-a", required=True)
    parser.add_argument("--source-b", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output-root", required=True)
    args = parser.parse_args(argv)
    try:
        run = new_run(args.output_root)
    except (OSError, ValueError):
        print(json.dumps({"execution": "error", "error": "unsafe_or_unwritable_output"}))
        return 2
    config, manifest, profiles, rows = {}, {}, {}, {}
    try:
        cp = Path(args.config)
        if cp.is_symlink() or any(p.is_symlink() for p in cp.parents):
            raise AuditError("symlink_config", "ERROR")
        if cp.stat().st_size > 1_000_000:
            raise AuditError("config_size_limit", "ERROR")
        config = json.loads(cp.read_text(encoding="utf-8-sig"))
        for side, path in (("a", args.source_a), ("b", args.source_b)):
            options = config.get("sources", {}).get(side, {}).get("read", {}) if isinstance(config, dict) else {}
            rows[side], manifest[side] = load(path, options)
            profiles[side] = profile(rows[side])
        result = audit(rows["a"], rows["b"], config)
        code = 0 if result["consistency"] in ("consistent", "aggregate_consistent") else 1
    except (AuditError, OSError, ValueError, TypeError, AttributeError, RecursionError) as exc:
        state = exc.state if isinstance(exc, AuditError) else "ERROR"
        code = {"NEEDS_CONFIRMATION": 4, "BLOCKED": 3}.get(state, 2)
        result = {"schema_version": 1, "execution": "error" if code == 2 else "success",
                  "alignment": {"state": state if state != "ERROR" else "BLOCKED"},
                  "consistency": "not_assessed", "errors": [exc.code if isinstance(exc, AuditError) else "invalid_input_or_config"],
                  "root_cause": "not_established", "correct_source": "not_determined"}
    emit(run, result, config, manifest, profiles)
    print(json.dumps({"run": str(run.resolve()), "execution": result["execution"], "alignment": result["alignment"]["state"], "consistency": result["consistency"], "exit_code": code}))
    return code


if __name__ == "__main__":
    sys.exit(main())
