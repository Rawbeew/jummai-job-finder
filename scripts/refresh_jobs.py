#!/usr/bin/env python3
"""
Refresh jobs.json with fresh, direct-employer postings. Runs daily via GitHub
Actions (no keys required). Uses only the Python standard library.

Sources (in order):
  1. SmartRecruiters public API  (keyless) - hospitals/employers that post there,
     e.g. University Health Network (UHN). Returns full details: title, location,
     apply URL, salary, requirements text.
  2. Adzuna API (optional) - requires free ADZUNA_APP_ID / ADZUNA_APP_KEY
     (developer.adzuna.com) provided as GitHub Actions secrets, for extra breadth.

Merge rules:
  - Curated entries (no "live" key) are always kept - they are hand-maintained.
  - Fetched entries get "live": true and are sorted newest-first at the top.
  - Duplicates are dropped by (title + employer).
  - Live entries older than MAX_LIVE_AGE_DAYS are pruned.
  - The list is capped at CAP entries.
"""
import json
import os
import re
import sys
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(os.path.dirname(HERE), "jobs.json")

MAX_LIVE_AGE_DAYS = 45
CAP = 60
DETAILS_PER_EMPLOYER = 10

# Direct employers on SmartRecruiters. Add more slugs as discovered.
SMARTRECRUITER_EMPLOYERS = [
    {"slug": "UniversityHealthNetwork", "tier": "hospital", "name": "University Health Network (UHN)"},
]

CARE_KEYWORDS = [
    "personal support", "support worker", "psw", "care aide", "health care aide",
    "caregiver", "patient services", "health care attendant",
]
TITLE_EXCLUDE = ["animal", "physiotherapist", "occupational therapist", "executive"]
AGENCY_MARKERS = ["staffing", "agency", "recruit", "we place", "assignments", "per visit"]

APP_ID = os.environ.get("ADZUNA_APP_ID", "").strip()
APP_KEY = os.environ.get("ADZUNA_APP_KEY", "").strip()


def http_json(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "jummai-job-finder/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def strip_html(text):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("&#xa0;", " ").replace("&amp;", "&").replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", text).strip()


def salary_from(text):
    m = re.search(r"\$?(\d{2}(?:\.\d{1,2})?)\s*-\s*\$?(\d{2}(?:\.\d{1,2})?)(?:\s*(?:/|\sper\s)\s*hr|hourly|per hour)?", text or "")
    if m:
        lo, hi = float(m.group(1)), float(m.group(2))
        if 10 <= lo <= 100 and lo <= hi <= 100:
            return lo, f"${lo:.2f}-${hi:.2f}/hr"
    return None, "See posting"


def fetch_smartrecruiters():
    out = []
    for emp in SMARTRECRUITER_EMPLOYERS:
        base = f"https://api.smartrecruiters.com/v1/companies/{emp['slug']}/postings"
        try:
            data = http_json(base + "?limit=100")
        except Exception as e:  # noqa: BLE001
            print(f"SmartRecruiters {emp['slug']} list failed: {e}", file=sys.stderr)
            continue
        care = []
        for c in data.get("content", []):
            name = (c.get("name") or "").strip()
            low = name.lower()
            if any(k in low for k in CARE_KEYWORDS) and not any(k in low for k in TITLE_EXCLUDE):
                care.append(c)
        details = 0
        for c in care:
            if details >= DETAILS_PER_EMPLOYER:
                break
            name = (c.get("name") or "").strip()
            pid = c.get("id")
            try:
                d = http_json(f"{base}/{pid}")
            except Exception as e:  # noqa: BLE001
                print(f"SmartRecruiters {pid} detail failed: {e}", file=sys.stderr)
                continue
            ad = d.get("jobAd") or {}
            sections = ad.get("sections") or {}
            desc = strip_html((sections.get("jobDescription") or {}).get("text", "") if isinstance(sections.get("jobDescription"), dict) else "")
            quals = strip_html((sections.get("qualifications") or {}).get("text", "") if isinstance(sections.get("qualifications"), dict) else "")
            comp = d.get("compensation") or {}
            comp_text = strip_html(json.dumps(comp)) if comp else ""
            pay_min, pay = salary_from((desc + " " + comp_text) or "")
            req_text = (desc + " " + quals).strip()[:800]
            if not req_text:
                req_text = name
            blob = (name + " " + req_text).lower()
            if any(m in blob for m in AGENCY_MARKERS):
                continue
            if any(k in blob for k in ("behavioural", "behavioral", "dementia", "responsive")):
                cat = "behavioural"
            else:
                cat = "psw"
            loc = ((d.get("location") or {}).get("city") or "").strip() or "Toronto"
            toe = d.get("typeOfEmployment") or {}
            if isinstance(toe, dict):
                emp_type = toe.get("label") or "See posting"
            else:
                emp_type = str(toe or "See posting")
            out.append({
                "e": emp["name"],
                "title": name,
                "cat": cat,
                "tier": emp["tier"],
                "loc": loc,
                "pay": pay,
                "payMin": pay_min,
                "type": emp_type,
                "link": d.get("applyUrl") or d.get("postingUrl") or "",
                "search": "https://www.google.com/search?q=" + urllib.parse.quote(name),
                "hl": [h for h in [strip_html(x)[:110] for x in quals.split(";")[:4]] if h],
                "req": req_text,
                "live": True,
                "releasedDate": (d.get("releasedDate") or "")[:10],
            })
            details += 1
        print(f"SmartRecruiters {emp['slug']}: {len(care)} care roles, {details} detailed")
    return out


def fetch_adzuna():
    if not (APP_ID and APP_KEY):
        return []
    out = []
    for q in ["personal support worker", "caregiver", "health care aide"]:
        params = urllib.parse.urlencode({
            "app_id": APP_ID, "app_key": APP_KEY, "what": q, "where": "Toronto",
            "content-type": "application/json", "results_per_page": 10,
        })
        url = "https://api.adzuna.com/v1/api/jobs/ca/search/1?" + params
        try:
            data = http_json(url)
        except Exception as e:  # noqa: BLE001
            print(f"Adzuna fetch failed for '{q}': {e}", file=sys.stderr)
            continue
        for item in data.get("results", []):
            title = (item.get("title") or "").strip()
            desc = (item.get("description") or "").strip()
            blob = (title + " " + desc).lower()
            if any(m in blob for m in AGENCY_MARKERS):
                continue
            if not any(k in blob for k in ("care", "support worker", "health")):
                continue
            out.append({
                "e": (item.get("company") or {}).get("display_name", "Employer"),
                "title": title,
                "cat": "behavioural" if ("dementia" in blob or "behavioural" in blob or "behavioral" in blob) else "psw",
                "tier": "ltco",
                "loc": "Toronto / GTA",
                "pay": "See posting",
                "payMin": None,
                "type": (item.get("contract_type") or "Varies"),
                "link": item.get("redirect_url", ""),
                "search": "https://www.google.com/search?q=" + urllib.parse.quote(title),
                "hl": ["See the posting for full requirements."],
                "req": desc[:600],
                "live": True,
                "releasedDate": (item.get("created") or "")[:10],
            })
    return out


def main():
    base = []
    if os.path.exists(JSON_PATH):
        try:
            with open(JSON_PATH, encoding="utf-8") as f:
                base = json.load(f)
        except Exception:  # noqa: BLE001
            base = []

    curated = [j for j in base if j.get("live") is not True]
    live_old = [j for j in base if j.get("live") is True]

    fresh = fetch_smartrecruiters() + fetch_adzuna()
    if fresh:
        fresh.sort(key=lambda j: j.get("releasedDate", ""), reverse=True)
        live_old = [j for j in live_old if j.get("releasedDate", "")[:10] >= "2000-01-01"]  # keep all; prune below

    # merge live: fresh first, then older live entries (dedup)
    seen = {(j.get("title", "").strip().lower(), j.get("e", "").strip().lower()) for j in curated}
    live_merged = []
    for j in fresh + live_old:
        key = (j.get("title", "").strip().lower(), j.get("e", "").strip().lower())
        if key in seen:
            continue
        seen.add(key)
        live_merged.append(j)

    merged = live_merged[:CAP - len(curated)] + curated

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2)
        f.write("\n")
    print(f"jobs.json written: {len(merged)} total ({len(curated)} curated, {len(live_merged)} live-fetched)")


if __name__ == "__main__":
    main()
