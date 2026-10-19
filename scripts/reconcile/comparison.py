from decimal import Decimal


def compare(pairs, metric, row_tolerance, total_tolerance):
    z = Decimal(0)
    a_total = b_total = matched = only_a = only_b = positive = negative = absolute = z
    details, mismatches, missing = [], 0, 0
    for key, a, b in pairs:
        av, bv = (a[metric] if a else None), (b[metric] if b else None)
        if a is not None:
            a_total += av
        if b is not None:
            b_total += bv
        difference = av - bv if av is not None and bv is not None else None
        if difference is not None:
            matched += difference
            status = "matched" if abs(difference) <= row_tolerance else "value_mismatch"
            mismatches += status == "value_mismatch"
            contribution = difference
        elif av is not None:
            only_a += av
            contribution, status = av, "only_in_a"
            missing += 1
        else:
            only_b += bv
            contribution, status = -bv, "only_in_b"
            missing += 1
        absolute += abs(contribution)
        positive += max(z, contribution)
        negative += min(z, contribution)
        details.append({"key": list(key), "metric": metric, "a": av, "b": bv,
                        "difference": difference, "status": status,
                        "a_rows": a["source_rows"] if a else [], "b_rows": b["source_rows"] if b else []})
    net = a_total - b_total
    summary = {"a_total": a_total, "b_total": b_total, "matched_difference": matched,
               "only_a_total": only_a, "only_b_total": only_b, "net_difference": net,
               "absolute_difference": absolute, "positive_difference": positive, "negative_difference": negative,
               "mismatch_count": mismatches, "unmatched_count": missing,
               "identity_valid": net == matched + only_a - only_b,
               "within_tolerance": mismatches == 0 and missing == 0 and abs(net) <= total_tolerance,
               "row_tolerance": row_tolerance, "total_tolerance": total_tolerance}
    return summary, details
