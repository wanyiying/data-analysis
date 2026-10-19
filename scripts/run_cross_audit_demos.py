"""Run three acceptance demos plus optional public sample without overwriting runs."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    demos = []
    for name, expected in (("consistent", 0), ("value_mismatch", 1), ("definition", 3), ("public_retail", 1)):
        case = ROOT / "examples/cross_audit" / name
        if not case.is_dir():
            continue
        command = [sys.executable, str(ROOT / "scripts/da_cross_reconcile.py"), "--source-a", str(case / "a.csv"), "--source-b", str(case / "b.csv"), "--config", str(case / "contract.json"), "--output-root", str(ROOT / "outputs/cross-audit-demos")]
        completed = subprocess.run(command, capture_output=True, text=True)
        if completed.returncode != expected:
            raise RuntimeError(f"{name}:unexpected exit {completed.returncode}: {completed.stderr}")
        result = json.loads(completed.stdout)
        verification_command = [sys.executable, str(ROOT / "scripts/verify_cross_audit_run.py"), "--run", result["run"]]
        verification = subprocess.run(verification_command, capture_output=True, text=True)
        if verification.returncode:
            raise RuntimeError(verification.stdout + verification.stderr)
        demos.append({"case": name, "command": command, "actual_exit": completed.returncode, **result,
                      "independent_verification": json.loads(verification.stdout)})
    destination = ROOT / "outputs/cross-audit-demos/index.json"
    destination.write_text(json.dumps(demos, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(demos, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
