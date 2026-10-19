"""Fail-closed business and structural contract validation."""
from datetime import date, datetime
from decimal import Decimal, InvalidOperation


class AuditError(ValueError):
    def __init__(self, code, state="BLOCKED"):
        super().__init__(code)
        self.code, self.state = code, state


def decimal(value):
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise AuditError("invalid_number") from None
    if not result.is_finite() or len(result.as_tuple().digits) > 24 or abs(result.adjusted()) > 24:
        raise AuditError("nonfinite_or_precision_limit")
    return result


def validate(c):
    if not isinstance(c, dict) or c.get("schema_version") != 1:
        raise AuditError("invalid_config", "ERROR")
    if c.get("confirmed") is not True:
        raise AuditError("business_confirmation_required", "NEEDS_CONFIRMATION")
    try:
        mode, keys, metrics = c["mode"], c["keys"], c["metrics"]
        if mode not in ("exact", "aggregate", "total"):
            raise AuditError("unsupported_mode")
        if not isinstance(keys, list) or not isinstance(metrics, list) or not metrics:
            raise AuditError("invalid_fields")
        names = keys + metrics
        if any(not isinstance(n, str) or not n for n in names) or len(set(names)) != len(names):
            raise AuditError("invalid_fields")
        if mode == "total" and (keys or c.get("allow_total") is not True):
            raise AuditError("total_requires_explicit_authorization")
        if mode != "total" and not keys:
            raise AuditError("no_common_keys")
        for name in ("row_tolerance", "total_tolerance"):
            if decimal(c.get(name, "0")) < 0:
                raise AuditError("negative_tolerance")
        sources = [c["sources"][s] for s in ("a", "b")]
        for s in sources:
            if not isinstance(s["fields"], dict) or not isinstance(s["grain"], list) or not s["grain"]:
                raise AuditError("invalid_source_contract")
            if any(not isinstance(v, str) or not v.strip() for v in s["fields"].values()) or any(not isinstance(v, str) or not v.strip() for v in s["grain"]):
                raise AuditError("invalid_source_contract")
            if s["date"]["field"] in metrics:
                raise AuditError("date_metric_overlap")
            if any(not isinstance(n, str) or n.startswith("__") or n == "source_rows" or n.lstrip().startswith(("=", "+", "-", "@")) for n in s["fields"]):
                raise AuditError("reserved_or_invalid_field")
            if set(s["grain"]) & set(metrics):
                raise AuditError("metric_in_grain")
            needed = set(keys + metrics + s["grain"] + [s["date"]["field"]])
            if not needed.issubset(s["fields"]) or len(set(s["fields"].values())) != len(s["fields"]):
                raise AuditError("incomplete_or_ambiguous_mapping")
            if not set(keys).issubset(s["grain"]) or len(set(s["grain"])) != len(s["grain"]):
                raise AuditError("invalid_grain")
            if mode == "exact" and set(keys) != set(s["grain"]):
                raise AuditError("exact_grain_mismatch")
            if not s["date"]["meaning"] or not s["date"]["format"]:
                raise AuditError("missing_date_semantics")
            scope = s["scope"]
            if date.fromisoformat(scope["start"]) > date.fromisoformat(scope["end"]):
                raise AuditError("invalid_window")
            if not isinstance(scope["population"], str) or not scope["population"].strip() or datetime.fromisoformat(scope["cutoff"]).utcoffset() is None:
                raise AuditError("invalid_scope_or_cutoff")
            if not isinstance(scope["filters"], dict):
                raise AuditError("invalid_filters")
            for field, values in scope["filters"].items():
                if field not in s["fields"] or not isinstance(values, list) or not values or any(not isinstance(v, str) for v in values):
                    raise AuditError("invalid_filters")
            for metric in metrics:
                m = s["metrics"][metric]
                if m["aggregation"] != "sum" or not all(m[k] for k in ("definition", "unit", "currency")):
                    raise AuditError("unsupported_metric")
                if decimal(m.get("multiplier", "1")) <= 0:
                    raise AuditError("invalid_multiplier")
        a, b = sources
        if a["scope"] != b["scope"]:
            raise AuditError("scope_or_cutoff_mismatch")
        if a["date"]["meaning"] != b["date"]["meaning"]:
            raise AuditError("date_meaning_mismatch")
        for metric in metrics:
            if any(a["metrics"][metric][k] != b["metrics"][metric][k] for k in ("definition", "unit", "currency", "aggregation")):
                raise AuditError("metric_semantics_mismatch")
    except (KeyError, TypeError, ValueError) as exc:
        if isinstance(exc, AuditError):
            raise
        raise AuditError("invalid_config", "ERROR") from None
    return c
