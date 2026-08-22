#!/usr/bin/env python3
"""
One-time backfill: load the existing jobs.json snapshot into the SQLite
store (jobs.db), computing content hashes. Safe to re-run — dedupe is
hash-based, so repeats only refresh fetched_at.

Usage: python scripts/backfill.py [path/to/jobs.json]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from jobstore import JobStore, DEFAULT_DB  # noqa: E402

ROOT = os.path.dirname(HERE)


def main():
    json_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "jobs.json")
    with open(json_path, encoding="utf-8") as f:
        jobs = json.load(f)
    store = JobStore()
    try:
        inserted, dupes = store.upsert_many(jobs, source="backfill")
    finally:
        store.close()
    print(f"backfill complete: {inserted} inserted, {dupes} duplicates -> {DEFAULT_DB}")


if __name__ == "__main__":
    main()
