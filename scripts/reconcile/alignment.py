def plan(config):
    return {"state": {"exact": "READY_EXACT", "aggregate": "READY_AGGREGATE", "total": "AGGREGATE_ONLY"}[config["mode"]],
            "keys": config["keys"], "grain_a": config["sources"]["a"]["grain"],
            "grain_b": config["sources"]["b"]["grain"],
            "limitations": ["Common-total comparison cannot establish record-level consistency."] if config["mode"] == "total" else
            ["Agreement is limited to configured aggregate keys; differences within a group may cancel. Record-level consistency is not established."] if config["mode"] == "aggregate" else []}
