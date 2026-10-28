#!/usr/bin/env python3
"""Schedule C Sort (Lite): tag each row of ONE bank/card CSV with a suggested
Schedule C category and total the categories. Python 3.8+, standard library only,
no network. MIT License. Not tax advice.

    python3 sort_lite.py statement.csv --out sorted.csv [--money-out negative|positive]

Writes sorted.csv (your rows + suggested_line + suggested_category) and
sorted_totals.csv (sum per category). Rows nothing matches are tagged UNSORTED.
"""
import argparse
import csv
import re
import sys
from decimal import Decimal, InvalidOperation

# (keyword, Schedule C line, category). First match wins. Edit freely.
KEYWORDS = [
    ("STRIPE", "1", "Gross receipts"), ("INVOICE", "1", "Gross receipts"),
    ("FACEBK", "8", "Advertising"), ("GOOGLE ADS", "8", "Advertising"), ("META ADS", "8", "Advertising"),
    ("SHELL", "9", "Car and truck"), ("CHEVRON", "9", "Car and truck"), ("EXXON", "9", "Car and truck"),
    ("UPWORK", "11", "Contract labor"), ("FIVERR", "11", "Contract labor"),
    ("INSURANCE", "15", "Insurance (other than health)"),
    ("ATTORNEY", "17", "Legal and professional"), ("CPA", "17", "Legal and professional"),
    ("STAPLES", "18", "Office expense"), ("USPS", "18", "Office expense"), ("OFFICE DEPOT", "18", "Office expense"),
    ("WEWORK", "20b", "Rent (other business property)"), ("COWORK", "20b", "Rent (other business property)"),
    ("AMAZON", "22", "Supplies"), ("AMZN", "22", "Supplies"), ("HOME DEPOT", "22", "Supplies"),
    ("LICENSE", "23", "Taxes and licenses"),
    ("AIRLINES", "24a", "Travel"), ("DELTA", "24a", "Travel"), ("HOTEL", "24a", "Travel"), ("AIRBNB", "24a", "Travel"),
    ("RESTAURANT", "24b", "Meals"), ("CAFE", "24b", "Meals"), ("STARBUCKS", "24b", "Meals"), ("DOORDASH", "24b", "Meals"),
    ("VERIZON", "25", "Utilities"), ("COMCAST", "25", "Utilities"), ("AT&T", "25", "Utilities"),
    ("ADOBE", "27b", "Other: software"), ("GITHUB", "27b", "Other: software"), ("ZOOM", "27b", "Other: software"),
    ("NOTION", "27b", "Other: software"), ("DROPBOX", "27b", "Other: software"), ("GSUITE", "27b", "Other: software"),
    ("SERVICE FEE", "27b", "Other: bank fees"),
    ("PAYMENT THANK YOU", "-", "Card payment (not an expense)"), ("TRANSFER", "-", "Transfer (not an expense)"),
]


def to_decimal(text):
    t = (text or "").strip().replace("$", "").replace(",", "")
    if not t:
        return None
    neg = t.startswith("(") and t.endswith(")")
    t = t.strip("()")
    try:
        v = Decimal(t)
    except InvalidOperation:
        sys.exit(f"Could not read amount: {text!r}")
    return -v if neg else v


def pick(headers, names):
    low = [h.strip().lower() for h in headers]
    for n in names:
        if n in low:
            return headers[low.index(n)]
    return None


def main():
    ap = argparse.ArgumentParser(description="Tag one CSV with suggested Schedule C categories. Not tax advice.")
    ap.add_argument("csv_file")
    ap.add_argument("--out", required=True)
    ap.add_argument("--money-out", choices=["negative", "positive"], default="negative",
                    help="which sign means money out in the Amount column (default negative)")
    a = ap.parse_args()
    with open(a.csv_file, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        headers = reader.fieldnames or []
    desc_col = pick(headers, ["description", "memo", "payee", "name", "details"])
    amt_col = pick(headers, ["amount"])
    deb_col, cred_col = pick(headers, ["debit", "withdrawal"]), pick(headers, ["credit", "deposit"])
    if not desc_col or not (amt_col or deb_col or cred_col):
        sys.exit("Need a Description column and an Amount column (or Debit/Credit columns).")
    totals = {}
    for r in rows:
        if amt_col:
            amt = to_decimal(r.get(amt_col)) or Decimal(0)
            if a.money_out == "positive":
                amt = -amt
        else:
            amt = (abs(to_decimal(r.get(cred_col)) or 0)) - (abs(to_decimal(r.get(deb_col)) or 0))
        text = re.sub(r"\s+", " ", (r.get(desc_col) or "").upper())
        line, cat = "?", "UNSORTED"
        for kw, ln, c in KEYWORDS:
            if kw in text:
                line, cat = ln, c
                break
        r["normalized_amount"] = f"{amt:.2f}"
        r["suggested_line"], r["suggested_category"] = line, cat
        key = (line, cat)
        totals[key] = totals.get(key, Decimal(0)) + amt
    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=headers + ["normalized_amount", "suggested_line", "suggested_category"])
        w.writeheader()
        w.writerows(rows)
    tot_path = re.sub(r"\.csv$", "", a.out) + "_totals.csv"
    with open(tot_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["schedule_c_line", "category", "net_amount (negative = money out)"])
        for (ln, c), v in sorted(totals.items()):
            w.writerow([ln, c, f"{v:.2f}"])
    unsorted = sum(1 for r in rows if r["suggested_category"] == "UNSORTED")
    print(f"{len(rows)} rows tagged, {unsorted} UNSORTED. Wrote {a.out} and {tot_path}. Not tax advice.")


if __name__ == "__main__":
    main()
