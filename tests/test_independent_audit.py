"""Adversarial tests with explicit expectations independent of fixture answers."""
import hashlib
import json
from datetime import datetime

import pytest
from test_cross_audit import records, base_contract
from reconcile.contract import AuditError
from reconcile.engine import audit
from reconcile.evidence import emit
from verify_cross_audit_run import verify


def sample():
    return records([["1", "2026-01-01", "east", "10"]])


def test_date_cannot_overwrite_metric():
    c = base_contract()
    for s in c["sources"].values():
        s["date"].update(field="amount", format="%Y%m%d")
    a, b = sample(), sample()
    a[0]["amount"], b[0]["amount"] = "20260101", "020260101"
    with pytest.raises(AuditError, match="date_metric_overlap"):
        audit(a, b, c)


@pytest.mark.parametrize("value", ["2026-01-01T23:00:00-08:00", datetime(2026, 1, 1, 12)])
def test_timestamp_cannot_silently_become_calendar_day(value):
    c = base_contract()
    for s in c["sources"].values():
        s["date"]["format"] = "%Y-%m-%dT%H:%M:%S%z"
    a = sample()
    a[0]["date"] = value
    with pytest.raises(AuditError, match="timestamp_requires_explicit_preprocessing"):
        audit(a, a, c)


def test_exact_date_disagreement_is_not_consistent():
    a, b = sample(), sample()
    b[0]["date"] = "2026-01-02"
    with pytest.raises(AuditError, match="matched_date_mismatch"):
        audit(a, b, base_contract())


def test_aggregate_agreement_discloses_hidden_offsets(tmp_path):
    c = base_contract()
    c.update(mode="aggregate", keys=["date", "region"])
    for s in c["sources"].values():
        s["grain"] = ["id", "date", "region"]
    a = records([["1", "2026-01-01", "east", "10"], ["2", "2026-01-01", "east", "20"]])
    b = records([["1", "2026-01-01", "east", "5"], ["2", "2026-01-01", "east", "25"]])
    result = audit(a, b, c)
    assert result["consistency"] == "consistent"  # agreement at requested grain only
    assert "may cancel" in result["alignment"]["limitations"][0]
    emit(tmp_path, result, c, {}, {})
    assert "may cancel" in (tmp_path / "report.html").read_text(encoding="utf-8")


@pytest.mark.parametrize("mutation", [
    lambda c: c["sources"]["a"]["fields"].update(amount=[]),
    lambda c: c["sources"]["a"].update(grain=[[]]),
    lambda c: c["sources"]["a"]["scope"].update(population="   "),
])
def test_malformed_contract_is_controlled(mutation):
    c = base_contract()
    mutation(c)
    with pytest.raises(AuditError):
        audit(sample(), sample(), c)


@pytest.mark.parametrize("tamper", ["contract", "consistency", "execution", "missing_input"])
def test_verifier_rejects_status_or_contract_tampering(tmp_path, tamper):
    c = base_contract()
    inputs = {}
    for side in ("a", "b"):
        p = tmp_path / (side + ".csv")
        p.write_text("id,date,region,amount\n1,2026-01-01,east,10\n", encoding="utf-8")
        inputs[side] = {"path": str(p), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
    emit(tmp_path, audit(sample(), sample(), c), c, inputs, {})
    assert verify(tmp_path)["status"] == "pass"
    filename = "contract.json" if tamper == "contract" else "manifest.json" if tamper == "missing_input" else "summary.json"
    obj = json.loads((tmp_path / filename).read_text(encoding="utf-8"))
    if tamper == "contract":
        obj["sources"]["a"]["metrics"]["amount"]["definition"] = "other metric"
    elif tamper == "missing_input":
        obj["inputs"].pop("b")
    else:
        obj[tamper] = "different" if tamper == "consistency" else "error"
    (tmp_path / filename).write_text(json.dumps(obj), encoding="utf-8")
    assert verify(tmp_path)["status"] == "fail"


@pytest.mark.parametrize("decision", ["pass", "downgrade"])
def test_finalization_preserves_review_decision_and_mode(tmp_path, monkeypatch, decision):
    import finalize_cross_audit_review as finalizer
    from types import SimpleNamespace
    emit(tmp_path, audit(sample(), sample(), base_contract()), base_contract(), {}, {})
    agents = tmp_path / "agents"
    agents.mkdir()
    for role in ("locator", "mechanism", "falsifier", "reviewer"):
        (agents / (role + ".json")).write_text(json.dumps({"status": "ok", "decision": decision}), encoding="utf-8")
    (agents / "execution.json").write_text(json.dumps({"mode": "serial_fallback"}), encoding="utf-8")
    (tmp_path / "claims.json").write_text('{"claims": []}', encoding="utf-8")
    # Isolate formatting after verification; this does not assert these mock
    # role artifacts satisfy the real publication verifier.
    monkeypatch.setattr(finalizer, "verify", lambda run: {"status": "pass"})
    monkeypatch.setattr(finalizer.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=0, stdout='{"status":"pass"}'))
    if decision == "downgrade":
        original = (tmp_path / "report.html").read_bytes()
        with pytest.raises(ValueError, match="reviewer_downgrade"):
            finalizer.finalize(tmp_path)
        assert (tmp_path / "report.html").read_bytes() == original
        assert not (tmp_path / "finalization-record.json").exists()
        return
    finalizer.finalize(tmp_path)
    assert json.loads((tmp_path / "agent-review.json").read_text(encoding="utf-8"))["mode"] == "serial_fallback"
    assert "native_subagents" not in (tmp_path / "report.html").read_text(encoding="utf-8")
