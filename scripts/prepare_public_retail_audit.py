"""Download official UCI II or reuse --raw; create bounded, anonymized simulated sources."""
import argparse
import copy
import csv
import hashlib
import json
import urllib.request
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from generate_cross_audit_cases import base_contract

URL = "https://archive.ics.uci.edu/static/public/502/online%2Bretail%2Bii.zip"
PAGE = "https://archive.ics.uci.edu/dataset/502/online+retail+ii"


def prepare(raw, destination, limit=2000):
    import openpyxl
    destination.mkdir(parents=True, exist_ok=False)
    wb = openpyxl.load_workbook(raw, read_only=True, data_only=True)
    try:
        ws = wb.worksheets[0]
        iterator = ws.values
        header = next(iterator)
        fields = {name: i for i, name in enumerate(header)}
        required = ["InvoiceDate", "Quantity", "Price", "Country"]
        if any(f not in fields for f in required):
            raise ValueError("Unexpected UCI II schema")
        rows = []
        groups = defaultdict(Decimal)
        for index, row in enumerate(iterator, 2):
            values = {k: row[fields[k]] for k in required}
            if any(values[k] is None for k in required):
                raise ValueError(f"Missing required public field at source row {index}")
            day = values["InvoiceDate"].date().isoformat()
            amount = Decimal(str(values["Quantity"])) * Decimal(str(values["Price"]))
            country = str(values["Country"])
            rows.append([str(index), day, country, str(amount)])
            groups[(day, country)] += amount
            if len(rows) == limit:
                break
        sheet_name = ws.title
    finally:
        wb.close()
    b = [[str(i), d, r, str(v)] for i, ((d, r), v) in enumerate(sorted(groups.items()), 1)]
    before = b[0][3]
    b[0][3] = str(Decimal(before) + Decimal("7.25"))
    for side, records in (("a", rows), ("b", b)):
        with (destination / f"{side}.csv").open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, lineterminator="\n")
            writer.writerow(["id", "date", "region", "amount"])
            writer.writerows(records)
    c = base_contract()
    c.update(mode="aggregate", keys=["date", "region"])
    dates = [row[1] for row in rows]
    for side, source in c["sources"].items():
        source["grain"] = ["id", "date", "region"] if side == "a" else ["date", "region"]
        source["date"]["meaning"] = "invoice_calendar_day"
        source["scope"].update(start=min(dates), end=max(dates), cutoff="2012-01-01T00:00:00+00:00", population=f"first_{len(rows)}_source_rows_sheet_0")
        source["metrics"]["amount"].update(definition="Quantity times Price signed transaction value; not accounting revenue", currency="GBP", unit="pound")
    metadata = {"source": PAGE, "download": URL, "doi": "10.24432/C5CG6D", "author": "Daqing Chen", "license": "CC BY 4.0", "raw_sha256": hashlib.sha256(raw.read_bytes()).hexdigest(), "sheet": sheet_name,
                "sampling": f"first {len(rows)} data rows in original sheet order, source row ID starts at 2", "injection": [{"key": b[0][1:3], "side": "b", "before": before, "after": b[0][3], "delta": "7.25"}],
                "limitation": "Same public source derived into two simulated views, not independent operational/financial systems; no customer identifiers exported.", "expected_net_difference": "-7.25",
                "generated_at": datetime.now(timezone.utc).isoformat()}
    for name, obj in (("contract.json", c), ("provenance.json", metadata)):
        (destination / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    return metadata


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--raw", type=Path)
    p.add_argument("--download-dir", type=Path, default=Path("outputs/public-raw"))
    p.add_argument("--destination", type=Path, required=True)
    p.add_argument("--limit", type=int, default=2000)
    args = p.parse_args()
    if not 1 <= args.limit <= 10000:
        p.error("limit must be 1..10000")
    raw = args.raw
    if raw is None:
        args.download_dir.mkdir(parents=True, exist_ok=True)
        archive = args.download_dir / "online-retail-ii.zip"
        if not archive.exists():
            # Stream bounded download, never execute archive paths.
            with urllib.request.urlopen(URL, timeout=60) as response, archive.open("xb") as f:
                count = 0
                while chunk := response.read(1024 * 1024):
                    count += len(chunk)
                    if count > 60_000_000:
                        raise ValueError("download_size_limit")
                    f.write(chunk)
        raw = args.download_dir / "online_retail_II.xlsx"
        if not raw.exists():
            with zipfile.ZipFile(archive) as z:
                candidates = [i for i in z.infolist() if Path(i.filename).name == "online_retail_II.xlsx"]
                if len(candidates) != 1 or candidates[0].file_size > 60_000_000:
                    raise ValueError("unexpected_archive")
                with z.open(candidates[0]) as source, raw.open("xb") as out:
                    while chunk := source.read(1024 * 1024):
                        out.write(chunk)
    print(json.dumps(prepare(raw, args.destination, args.limit), ensure_ascii=False))


if __name__ == "__main__":
    main()
