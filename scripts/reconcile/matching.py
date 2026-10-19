from decimal import Decimal


def aggregate(rows, keys, metrics):
    groups = {}
    for row in rows:
        key = tuple(row[k] for k in keys)
        if key not in groups:
            groups[key] = {m: Decimal(0) for m in metrics}
            groups[key]["source_rows"] = []
        for m in metrics:
            groups[key][m] += row[m]
        groups[key]["source_rows"].append(row["__source_row__"])
    return groups


def match(a, b):
    # Dictionaries ensure at most one group per key. No Cartesian product.
    return [(key, a.get(key), b.get(key)) for key in sorted(a.keys() | b.keys())]
