#!/usr/bin/env python3
"""
Refresh jobs.json with fresh, current, direct-employer postings. Runs daily via
GitHub Actions (no keys required). Standard library only.

Sources (keyless):
  1. SmartRecruiters public API - e.g. University Health Network (UHN).
     Full details: title, location, apply URL, salary, requirements, closing date.
  2. BambooHR public careers feed - e.g. Better Living Health & Community
     Services. List endpoint only; apply URL built from the job id.
  3. Adzuna API (optional) - free ADZUNA_APP_ID / ADZUNA_APP_KEY as secrets.

Freshness rules (this is the important part):
  - Only postings released within MAX_LIVE_AGE_HOURS (12h) are kept, so the
    list shows genuinely fresh openings that are unlikely to be filled yet.
  - Postings with a parsed closing date in the past are dropped.
  - Curated entries (no "live" key) are kept only if CURATED_KEEP is True.
    This build sets CURATED_KEEP = False: the job list shows RECENT postings
    only. Evergreen employer career pages live in the site's directory.
"""
import datetime
import json
import os
import re
import sys
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(os.path.dirname(HERE), "jobs.json")

MAX_LIVE_AGE_HOURS = 12  # only postings released within the last 12 hours
CAP = 60
DETAILS_PER_EMPLOYER = 15
CURATED_KEEP = False  # job list = recent postings only

SMARTRECRUITER_EMPLOYERS = [
    {"slug": "UniversityHealthNetwork", "tier": "hospital", "name": "University Health Network (UHN)"},
]

# Remote-capable OFFICE track: admin/scheduler/coordinator/finance roles at
# DIRECT employers (not agencies). These suit a PSW grad whose second degree
# is Accounting, and can be hybrid/remote-capable.
OFFICE_KEYWORDS = [
    "scheduler", "scheduling", "coordinator", "intake", "client services",
    "unit clerk", "clerk", "receptionist", "administrative assistant",
    "accounting", "accounting clerk", "billing", "payroll", "finance",
    "financial", "data entry", "office assistant", "program assistant",
    "service coordinator", "operations assistant", "records",
]


def is_office_role(name):
    low = (name or "").lower()
    return any(k in low for k in OFFICE_KEYWORDS) and not any(k in low for k in TITLE_EXCLUDE)

BAMBOO_EMPLOYERS = [
    {"subdomain": "betterlivinghealth", "tier": "nonprofit", "name": "Better Living Health & Community Services"},
]

CARE_KEYWORDS = [
    "personal support", "support worker", "psw", "care aide", "health care aide",
    "caregiver", "patient services", "health care attendant", "community health worker",
    "recreation therapist", "activation aide", "home support worker",
]
TITLE_EXCLUDE = [
    "animal", "physiotherapist", "occupational therapist", "executive", "intern",
    "cleaner", "maintenance", "housekeep", "church",
]
AGENCY_MARKERS = ["staffing", "agency", "recruit", "we place", "assignments", "per visit"]

APP_ID = os.environ.get("ADZUNA_APP_ID", "").strip()
APP_KEY = os.environ.get("ADZUNA_APP_KEY", "").strip()


def today():
    return datetime.date.today()


def http_json(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "jummai-job-finder/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def strip_html(text):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("&#xa0;", " ").replace("&amp;", "&").replace("&nbsp;", " ")
    text = text.replace("\u2014", ", ").replace("\u2013", "-")
    return re.sub(r"\s+", " ", text).strip()


def salary_from(text, comp=None):
    # 1) structured compensation object first
    if isinstance(comp, dict):
        try:
            lo = float(comp.get("min", 0))
            hi = float(comp.get("max", 0))
        except (TypeError, ValueError):
            lo = hi = 0
        if lo and hi and lo <= hi:
            period = (comp.get("period") or "").lower()
            if period == "yearly":
                return round(lo / 2080, 2), f"${lo:,.0f}-${hi:,.0f}/yr"
            return lo, f"${lo:.2f}-${hi:.2f}/hr"
    # 2) hourly text fallback (strict: both figures must look like hourly rates)
    m = re.search(r"\$?(\d{2}(?:\.\d{1,2})?)\s*-\s*\$?(\d{2}(?:\.\d{1,2})?)\s*(?:/|\sper\s)\s*(?:hr|hour)", text or "", re.I)
    if m:
        lo, hi = float(m.group(1)), float(m.group(2))
        if 10 <= lo <= 60 and lo <= hi <= 60:
            return lo, f"${lo:.2f}-${hi:.2f}/hr"
    return None, "See posting"


def closing_date_from(text):
    m = re.search(r"closing\s*date:?\s*([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})", text or "", re.I)
    if not m:
        return None
    try:
        return datetime.datetime.strptime(f"{m.group(1)} {m.group(2)} {m.group(3)}", "%B %d %Y").date().isoformat()
    except ValueError:
        return None


def cat_of(blob):
    if any(k in blob for k in ("behavioural", "behavioral", "dementia", "responsive")):
        return "behavioural"
    if any(k in blob for k in ("recreation", "activation", "therapist", "restorative")):
        return "restorative"
    if any(k in blob for k in ("community health", "outreach", "coordinator")):
        return "coordination"
    return "psw"


def too_old(released):
    """True when a posting was released more than MAX_LIVE_AGE_HOURS ago.

    Accepts a full ISO timestamp (e.g. '2026-08-18T11:46:36Z') or a bare date
    ('2026-08-18'); for a bare date we compare against end-of-day so a posting
    from today still counts as fresh today.
    """
    if not released:
        return False
    s = released.strip()
    try:
        # prefer full timestamp (has a timezone letter / datetime separator)
        if "T" in s or len(s) > 10:
            dt = datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
            now = datetime.datetime.now(datetime.timezone.utc)
            return (now - dt).total_seconds() > MAX_LIVE_AGE_HOURS * 3600
        # bare date: allow all of the release date (treated as fresh all that day)
        d = datetime.date.fromisoformat(s[:10])
        return (today() - d).days >= 1
    except ValueError:
        return False


def already_closed(closes):
    if not closes:
        return False
    try:
        return datetime.date.fromisoformat(closes) < today()
    except ValueError:
        return False


def fetch_smartrecruiters():
    out = []
    for emp in SMARTRECRUITER_EMPLOYERS:
        base = f"https://api.smartrecruiters.com/v1/companies/{emp['slug']}/postings"
        try:
            data = http_json(base + "?limit=200")
        except Exception as e:  # noqa: BLE001
            print(f"SmartRecruiters {emp['slug']} list failed: {e}", file=sys.stderr)
            continue
        care = []
        office = []
        for c in data.get("content", []):
            name = (c.get("name") or "").strip()
            low = name.lower()
            if any(k in low for k in CARE_KEYWORDS) and not any(k in low for k in TITLE_EXCLUDE):
                care.append(c)
            elif is_office_role(name):
                office.append(c)
        details = 0
        for c in care + office:
            if details >= DETAILS_PER_EMPLOYER * 2:
                break
            is_office = c in office
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
            pay_min, pay = salary_from(desc + " " + comp_text, comp)
            req_text = (desc + " " + quals).strip()[:800] or name
            blob = (name + " " + req_text).lower()
            if any(m in blob for m in AGENCY_MARKERS):
                continue
            released = (d.get("releasedDate") or "")[:10]
            closes = closing_date_from(desc) or closing_date_from(quals)
            if too_old(released) or already_closed(closes):
                continue
            toe = d.get("typeOfEmployment") or {}
            emp_type = toe.get("label") if isinstance(toe, dict) else str(toe or "See posting")
            loc = ((d.get("location") or {}).get("city") or "").strip() or "Toronto"
            out.append({
                "e": emp["name"],
                "title": name,
                "cat": "admin" if is_office else cat_of(blob),
                "remote_capable": True if is_office else False,
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
                "releasedDate": released,
                "closes": closes,
            })
            details += 1
        print(f"SmartRecruiters {emp['slug']}: {len(care)} care roles -> {details} current after date filters")
    return out


def fetch_bamboohr():
    out = []
    for emp in BAMBOO_EMPLOYERS:
        url = f"https://{emp['subdomain']}.bamboohr.com/careers/list/?output=json"
        try:
            data = http_json(url)
        except Exception as e:  # noqa: BLE001
            print(f"BambooHR {emp['subdomain']} failed: {e}", file=sys.stderr)
            continue
        rows = data.get("result", data) if isinstance(data, dict) else data
        count = 0
        for j in rows:
            name = (j.get("jobOpeningName") or "").strip()
            low = name.lower()
            if not any(k in low for k in CARE_KEYWORDS) or any(k in low for k in TITLE_EXCLUDE):
                continue
            jid = j.get("id")
            loc = (j.get("location") or {}).get("city", "") if isinstance(j.get("location"), dict) else (j.get("location") or "")
            blob = low
            out.append({
                "e": emp["name"],
                "title": name,
                "cat": cat_of(blob),
                "tier": emp["tier"],
                "loc": loc or "Toronto",
                "pay": "See posting",
                "payMin": None,
                "type": (j.get("employmentStatusLabel") or "See posting"),
                "link": f"https://{emp['subdomain']}.bamboohr.com/careers/{jid}",
                "search": "https://www.google.com/search?q=" + urllib.parse.quote(name),
                "hl": ["See the posting for full requirements."],
                "req": name,
                "live": True,
                "releasedDate": None,
                "closes": None,
            })
            count += 1
        print(f"BambooHR {emp['subdomain']}: {count} care roles")
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
            released = (item.get("created") or "")[:10]
            if too_old(released):
                continue
            out.append({
                "e": (item.get("company") or {}).get("display_name", "Employer"),
                "title": title,
                "cat": cat_of(blob),
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
                "releasedDate": released,
                "closes": None,
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

    curated = [j for j in base if j.get("live") is not True] if CURATED_KEEP else []

    fresh = fetch_smartrecruiters() + fetch_bamboohr() + fetch_adzuna()
    fresh.sort(key=lambda j: j.get("releasedDate") or "", reverse=True)

    seen = set()
    live_merged = []
    for j in fresh:
        key = (j.get("title", "").strip().lower(), j.get("e", "").strip().lower(), (j.get("link") or "").strip())
        if key in seen:
            continue
        seen.add(key)
        live_merged.append(j)

    merged = (live_merged + curated)[:CAP]

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2)
        f.write("\n")
    print(f"jobs.json written: {len(merged)} total ({len(live_merged)} recent live, {len(curated)} curated)")


if __name__ == "__main__":
    main()
