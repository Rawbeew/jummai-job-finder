#!/usr/bin/env python3
"""
SQLite persistence layer for just-hired.

Stores every posting we have ever seen (postings history), deduped by a
content hash of (title + employer + location), and answers a handful of
queryable stats questions. Standard library only — no dependencies.

Schema:
  postings(id, hash UNIQUE, title, employer, location, region,
           posted_at, fetched_at, url, source)
"""
import datetime
import hashlib
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB = os.path.join(os.path.dirname(HERE), "jobs.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS postings (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    hash       TEXT NOT NULL UNIQUE,
    title      TEXT NOT NULL,
    employer   TEXT NOT NULL,
    location   TEXT NOT NULL DEFAULT '',
    region     TEXT NOT NULL DEFAULT 'unknown',
    posted_at  TEXT,
    fetched_at TEXT NOT NULL,
    url        TEXT NOT NULL DEFAULT '',
    source     TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_postings_posted_at ON postings(posted_at);
CREATE INDEX IF NOT EXISTS idx_postings_region    ON postings(region);
CREATE INDEX IF NOT EXISTS idx_postings_employer  ON postings(employer);
"""


def content_hash(title, employer, location):
    """Stable dedupe key: lowercase, whitespace-normalized title+employer+location."""
    def norm(s):
        return " ".join((s or "").lower().split())
    raw = "|".join([norm(title), norm(employer), norm(location)])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _now_iso():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class JobStore:
    def __init__(self, path=DEFAULT_DB):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def close(self):
        self.conn.close()

    # -- writes ------------------------------------------------------------

    def upsert(self, title, employer, location="", region="unknown",
               posted_at=None, url="", source=""):
        """Insert a posting; if its content hash already exists, refresh
        fetched_at/url but keep the original row. Returns 'inserted' or 'dupe'."""
        h = content_hash(title, employer, location)
        cur = self.conn.execute(
            "SELECT id FROM postings WHERE hash = ?", (h,))
        row = cur.fetchone()
        if row:
            self.conn.execute(
                "UPDATE postings SET fetched_at = ?, url = CASE WHEN ? != '' THEN ? ELSE url END "
                "WHERE id = ?",
                (_now_iso(), url, url, row["id"]))
            self.conn.commit()
            return "dupe"
        self.conn.execute(
            "INSERT INTO postings(hash, title, employer, location, region, "
            "posted_at, fetched_at, url, source) VALUES (?,?,?,?,?,?,?,?,?)",
            (h, (title or "").strip(), (employer or "").strip(),
             (location or "").strip(), region or "unknown", posted_at,
             _now_iso(), url or "", source or ""))
        self.conn.commit()
        return "inserted"

    def upsert_many(self, rows, source=""):
        """rows: iterable of dicts with keys title, employer, and optionally
        location, region, posted_at, url. Returns (inserted, dupes)."""
        ins = dup = 0
        for r in rows:
            res = self.upsert(
                r.get("title", ""), r.get("employer", r.get("e", "")),
                r.get("location", r.get("loc", "")),
                r.get("region", "unknown"),
                r.get("posted_at", r.get("releasedDate")),
                r.get("url", r.get("link", "")),
                r.get("source", source))
            if res == "inserted":
                ins += 1
            else:
                dup += 1
        return ins, dup

    # -- queries -----------------------------------------------------------

    def fresh_last_24h(self):
        """Postings seen in the store whose posted_at falls in the last 24h
        (or that were first fetched in the last 24h when posted_at is NULL)."""
        cutoff = (datetime.datetime.now(datetime.timezone.utc)
                  - datetime.timedelta(hours=24)).strftime("%Y-%m-%d")
        return self.conn.execute(
            "SELECT * FROM postings WHERE "
            "substr(COALESCE(posted_at, fetched_at), 1, 10) >= ? "
            "ORDER BY COALESCE(posted_at, fetched_at) DESC", (cutoff,)
        ).fetchall()

    def by_region(self):
        """Count of postings per region, highest first."""
        return self.conn.execute(
            "SELECT region, COUNT(*) AS n FROM postings "
            "GROUP BY region ORDER BY n DESC, region").fetchall()

    def top_employers(self, limit=10):
        return self.conn.execute(
            "SELECT employer, COUNT(*) AS n FROM postings "
            "GROUP BY employer ORDER BY n DESC, employer LIMIT ?",
            (limit,)).fetchall()

    def posting_volume_by_day(self, days=30):
        """Postings per posted_at day for the last `days` days, oldest first.
        Days with zero postings are included (0) so the series is gapless."""
        start = (datetime.date.today() - datetime.timedelta(days=days - 1)).isoformat()
        rows = self.conn.execute(
            "SELECT substr(posted_at, 1, 10) AS day, COUNT(*) AS n FROM postings "
            "WHERE posted_at IS NOT NULL AND posted_at >= ? "
            "GROUP BY day", (start,)).fetchall()
        counts = {r["day"]: r["n"] for r in rows}
        out = []
        for i in range(days):
            d = (datetime.date.today() - datetime.timedelta(days=days - 1 - i)).isoformat()
            out.append({"day": d, "count": counts.get(d, 0)})
        return out

    def stats(self):
        return {
            "total": self.conn.execute("SELECT COUNT(*) FROM postings").fetchone()[0],
            "by_region": [dict(r) for r in self.by_region()],
            "top_employers": [dict(r) for r in self.top_employers()],
        }


if __name__ == "__main__":
    store = JobStore()
    print(json.dumps(store.stats(), indent=2))
