from datetime import datetime, date
from .contract import AuditError, decimal


def normalize(rows, source, metrics):
    if not rows or not set(source["fields"].values()).issubset(rows[0]):
        raise AuditError("missing_columns_or_data")
    result, seen, dates = [], set(), []
    start, end = (date.fromisoformat(source["scope"][k]) for k in ("start", "end"))
    filtered = 0
    for index, row in enumerate(rows, 2):
        r = {key: row[field] for key, field in source["fields"].items()}
        # Never silently drop an unparseable date, even on a filtered row.
        try:
            value = r[source["date"]["field"]]
            parsed = value if isinstance(value, (date, datetime)) else datetime.strptime(value, source["date"]["format"])
            # V1 supports calendar dates only. Never guess a business timezone or
            # erase a timestamp's time/offset. Excel midnight dates remain valid.
            if isinstance(parsed, datetime) and (parsed.tzinfo is not None or parsed.time().isoformat() != "00:00:00" or any(token in source["date"]["format"] for token in ("%H", "%I", "%M", "%S", "%f", "%z", "%Z"))):
                raise AuditError("timestamp_requires_explicit_preprocessing")
            d = parsed.date() if isinstance(parsed, datetime) else parsed
        except AuditError:
            raise
        except (ValueError, TypeError):
            raise AuditError("invalid_date") from None
        r[source["date"]["field"]] = d.isoformat()
        if not start <= d <= end:
            raise AuditError("observed_date_outside_scope")
        if any(r[k] not in allowed for k, allowed in source["scope"]["filters"].items()):
            filtered += 1
            continue
        key = tuple(r[k] for k in source["grain"])
        if any(not value.strip() for value in key):
            raise AuditError("null_business_key")
        if key in seen:
            raise AuditError("duplicate_grain_many_to_many_risk")
        seen.add(key)
        for m in metrics:
            if r[m] == "":
                raise AuditError("missing_amount")
            r[m] = decimal(r[m]) * decimal(source["metrics"][m].get("multiplier", "1"))
        r["__source_row__"] = index
        result.append(r)
        dates.append(d.isoformat())
    if not result:
        raise AuditError("empty_filtered_scope")
    return result, {"included": len(result), "filtered": filtered, "date_min": min(dates), "date_max": max(dates)}
