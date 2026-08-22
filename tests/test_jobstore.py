"""Tests for the SQLite job store — temp db, no network."""
import datetime
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "scripts"))

from jobstore import JobStore, content_hash  # noqa: E402


def today_str(offset_days=0):
    return (datetime.date.today() + datetime.timedelta(days=offset_days)).isoformat()


class JobStoreTest(unittest.TestCase):
    def setUp(self):
        self.fd, self.path = tempfile.mkstemp(suffix=".db")
        os.close(self.fd)
        self.store = JobStore(self.path)

    def tearDown(self):
        self.store.close()
        os.remove(self.path)

    def test_insert_and_dedupe_same_hash(self):
        r1 = self.store.upsert("PSW", "UHN", "Toronto", posted_at=today_str())
        r2 = self.store.upsert("psw ", " uhn", "toronto")  # same content, different case/space
        self.assertEqual(r1, "inserted")
        self.assertEqual(r2, "dupe")
        self.assertEqual(self.store.conn.execute(
            "SELECT COUNT(*) FROM postings").fetchone()[0], 1)

    def test_content_hash_stable(self):
        self.assertEqual(content_hash("A b", "C", "D"),
                         content_hash(" a  B ", "c", " d "))
        self.assertNotEqual(content_hash("A", "B", ""), content_hash("A", "B", "x"))

    def test_fresh_last_24h_filters_correctly(self):
        self.store.upsert("Fresh", "E1", posted_at=today_str())
        self.store.upsert("Old", "E2", posted_at=today_str(-3))
        fresh = {r["title"] for r in self.store.fresh_last_24h()}
        self.assertIn("Fresh", fresh)
        self.assertNotIn("Old", fresh)
        # NULL posted_at falls back to fetch date (today) => counts as fresh
        self.store.upsert("NoDate", "E3")
        self.assertIn("NoDate", {r["title"] for r in self.store.fresh_last_24h()})

    def test_volume_by_day_groups_right(self):
        self.store.upsert("J1", "E1", posted_at=today_str(-1))
        self.store.upsert("J2", "E2", posted_at=today_str(-1))
        self.store.upsert("J3", "E3", posted_at=today_str(-4))
        vol = {d["day"]: d["count"] for d in self.store.posting_volume_by_day(days=5)}
        self.assertEqual(vol[today_str(-1)], 2)
        self.assertEqual(vol[today_str(-4)], 1)
        self.assertEqual(len(vol), 5)          # gapless series
        self.assertEqual(sum(vol.values()), 3)  # everything accounted for

    def test_by_region_and_top_employers(self):
        for e in ("E1", "E2"):
            self.store.upsert(f"T-{e}", e, region="north-york")
        self.store.upsert("T-E3", "E3", region="unknown")
        regions = {r["region"]: r["n"] for r in self.store.by_region()}
        self.assertEqual(regions["north-york"], 2)
        top = self.store.top_employers(limit=2)
        self.assertEqual(top[0]["n"], 1)
        self.assertEqual(len(top), 2)


if __name__ == "__main__":
    unittest.main()
