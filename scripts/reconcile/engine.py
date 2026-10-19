from decimal import localcontext
from .contract import AuditError, validate, decimal
from .normalization import normalize
from .alignment import plan
from .matching import aggregate, match
from .comparison import compare
from .diagnostics import diagnose


def audit(a, b, config):
    validate(config)
    with localcontext() as ctx:
        ctx.prec = 128
        normalized, coverage = {}, {}
        for side, rows in (("a", a), ("b", b)):
            normalized[side], coverage[side] = normalize(rows, config["sources"][side], config["metrics"])
        if config["mode"] == "exact":
            dates = {}
            for side in ("a", "b"):
                field = config["sources"][side]["date"]["field"]
                dates[side] = {tuple(r[k] for k in config["keys"]): r[field] for r in normalized[side]}
            if any(dates["a"][k] != dates["b"][k] for k in dates["a"].keys() & dates["b"].keys()):
                raise AuditError("matched_date_mismatch")
        pairs = match(*(aggregate(normalized[s], config["keys"], config["metrics"]) for s in ("a", "b")))
        summaries, details, diagnostics = {}, [], {}
        for metric in config["metrics"]:
            summaries[metric], rows = compare(pairs, metric, decimal(config.get("row_tolerance", "0")), decimal(config.get("total_tolerance", "0")))
            details.extend(rows)
            diagnostics[metric] = diagnose(summaries[metric])
        consistent = all(s["within_tolerance"] for s in summaries.values())
        status = "consistent" if consistent else "different"
        if config["mode"] == "total":
            status = "aggregate_" + status
        return {"schema_version": 1, "execution": "success", "alignment": plan(config), "consistency": status,
                "metrics": summaries, "details": details, "coverage": coverage, "diagnostics": diagnostics,
                "correct_source": "not_determined", "root_cause": "not_established"}
