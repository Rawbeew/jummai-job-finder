# Jummai's Job Finder

A personal job board and ATS resume builder for a Toronto Personal Support Worker.
Hosted free on GitHub Pages. It refreshes itself every day.

## What it does

- Lists **direct-employer** postings only (no staffing agencies): hospitals, City of
  Toronto LTC, non-profit homes, and retirement operators across the GTA and environs.
- Covers **PSW and adjacent roles**: behavioural support, DSW, clerical, restorative,
  and coordination.
- Every card shows the **application link**, the **requirements that matter**, and a
  **Read full posting** and **Listen** option.
- One tap generates an **ATS-friendly resume** and a **cover letter** tailored to that
  exact posting, ready to download as a Word file.

## How the daily refresh works (no keys needed)

A GitHub Actions workflow (`.github/workflows/refresh-jobs.yml`) runs **every day at
7:30 AM Toronto time** and executes `scripts/refresh_jobs.py`, which:

1. Fetches live postings from the **SmartRecruiters public API** (keyless) for direct
   employers such as University Health Network (UHN).
2. Optionally adds breadth via the **Adzuna API** if free keys are configured.
3. Merges fresh postings into `jobs.json` (curated entries are always kept, live
   entries are deduplicated and marked "new").
4. Commits and pushes, which redeploys the GitHub Pages site automatically.

To add more SmartRecruiters employers, extend `SMARTRECRUITER_EMPLOYERS` in
`scripts/refresh_jobs.py` with their company slug.

To add the optional Adzuna source: create free keys at developer.adzuna.com and add
them as repository secrets `ADZUNA_APP_ID` and `ADZUNA_APP_KEY`.

## Deploy elsewhere

The site is fully static (`index.html` + `jobs.json`), so it also runs on
Netlify (drag-and-drop) or Cloudflare Pages. The included `netlify.toml` is harmless
on GitHub Pages.

## For the user (no tech needed)

1. Open the site link on a phone.
2. New postings are already there. Tap **Type** and **Location** to narrow down.
3. Tap **Apply / open posting** on any job.
4. Tap **Show tailored resume** and **Show cover letter**, then download both.
5. Attach both files to the application.

Note: the resume dates under "Balda Care Home" are placeholders. Fill in the real
dates once, and every generated resume grades 100/100 on the built-in ATS checker.
