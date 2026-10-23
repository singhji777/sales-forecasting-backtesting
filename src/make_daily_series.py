"""Builds data/daily_sales.csv (one row per trading day) from the public UCI 'Online Retail' data.

Series = gross sales (quantity * unit price) of genuine product lines on non-cancelled invoices, per day.
Cleaning (same rules as project 05): drop exact duplicates, non-product stock codes (postage, fees, vouchers), unit price <= 0, cancellations.
Two invoices are also excluded: 541431 and 581483, huge mistaken wholesale orders that were reversed within minutes (see project 05).
The last day (9 Dec 2011) is dropped because the file ends mid-day.

Usage:  python src/make_daily_series.py [path_to_raw_csv_or_csv.gz]     (downloads the data if no path is given)
"""
import sys, tempfile, urllib.request
from pathlib import Path
import pandas as pd

URL = "https://raw.githubusercontent.com/databricks/Spark-The-Definitive-Guide/master/data/retail-data/all/online-retail-dataset.csv"
OUT = Path(__file__).resolve().parents[1] / "data" / "daily_sales.csv"
src = sys.argv[1] if len(sys.argv) > 1 else None
if src is None:
    src = str(Path(tempfile.mkdtemp()) / "raw.csv"); urllib.request.urlretrieve(URL, src)

df = pd.read_csv(src, dtype={"InvoiceNo": str, "StockCode": str})
df = df.drop_duplicates()
df = df[df.StockCode.str.match(r"^\d{5}", na=False) & (df.UnitPrice > 0)]
df = df[~df.InvoiceNo.str.startswith("C") & (df.Quantity > 0)]
df = df[~df.InvoiceNo.isin(["541431", "581483"])]
df["ts"] = pd.to_datetime(df.InvoiceDate, format="%m/%d/%Y %H:%M")
df["date"] = df.ts.dt.normalize()
daily = df.assign(revenue=df.Quantity * df.UnitPrice).groupby("date").agg(
    revenue=("revenue", "sum"), orders=("InvoiceNo", "nunique")).reset_index()
daily = daily[daily.date < "2011-12-09"]
daily.assign(revenue=daily.revenue.round(2)).to_csv(OUT, index=False)
print(f"saved {OUT}: {len(daily)} trading days, {daily.date.min().date()} to {daily.date.max().date()}, total GBP {daily.revenue.sum():,.0f}")
