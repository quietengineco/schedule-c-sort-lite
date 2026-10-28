# Schedule C Sort (Lite): free agent skill

A free, MIT-licensed agent skill that tags each row of one bank or card CSV with a suggested Schedule C category and totals the categories. Not tax advice.

## What it does

- Reads one CSV with a Description column and an Amount column (or Debit/Credit columns)
- Matches 42 editable keywords to a suggested Schedule C line (advertising, supplies, travel, meals, software, and so on)
- Writes `sorted.csv` (your rows plus the suggestion) and `sorted_totals.csv` (net amount per category)
- Tags anything it doesn't recognize as `UNSORTED` so you decide

## What it doesn't do

It handles one file at a time and does no duplicate removal, transfer or card-payment matching, refund handling, owner-draw detection, 1099 contractor checks, review workflow or accountant-ready report.

## Install

Copy the `schedule-c-sort-lite` folder to `~/.claude/skills/` (Claude Code), `~/.cursor/skills/` (Cursor) or `~/.agents/skills/` (Codex). Requires Python 3.8+.

## Try it

```bash
python3 scripts/sort_lite.py examples/sample.csv --out /tmp/sorted.csv
```

Or ask your agent: "Sort my January bank CSV into Schedule C categories."

## Not tax advice

Suggestions are keyword matches and can be wrong. Review every row, and have a qualified tax professional check anything you file.


## Support
Questions or problems? Email **quietenginecompany@gmail.com** with the product name and what you tried. We usually reply within a few business days.

## What was tested
Checked with the official Agent Skills validator and run on the included `examples/sample.csv` with Python 3. Not yet run in a live agent session.

## Full version
The **Year-End Books Cleanup Skill** handles many files at once and adds duplicate removal, transfer and refund matching, a 1099-NEC payee list and an accountant-ready report: https://quietenginecompany.com/products/

---
Made with AI assistance. MIT licensed (see `LICENSE`).

Made by Quiet Engine Co. · https://quietenginecompany.com
