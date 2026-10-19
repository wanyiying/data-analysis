"""Quality metadata without logging sensitive cell values."""
def profile(rows):
    return {"rows": len(rows), "columns": list(rows[0]) if rows else [],
            "missing": {k: sum(r[k] == "" for r in rows) for k in rows[0]} if rows else {}}
