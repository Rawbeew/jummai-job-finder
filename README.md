# PSW & Adjacent Job Finder

A static, free, anonymized template for a personal job board: live direct-employer postings for the Greater Toronto Area, refreshed every 2 hours, with only the last 12 hours shown.

A personal job board and ATS resume builder for a Toronto Personal Support Worker.
Hosted free on both platforms. It refreshes itself every day, and shows **recent,
still-open postings only**, no expired jobs.

**Live sites:**
- Netlify: https://just-hired.netlify.app
- GitHub Pages: https://rawbeew.github.io/just-hired/

Both stay in sync automatically: the daily workflow refreshes the postings and
redeploys both.

## What it does

- **Open postings** (top): current, dated, direct-employer postings only, no
  staffing agencies, no expired competitions. Every card shows the pay, the posted
  and closing dates, a "closing soon" alert, the requirements that matter, the
  **Apply here** button, and **Read full posting** and **Listen** options.
- **Always-hiring direct employers** (below): 33 evergreen cards (hospitals, City of
  Toronto LTC, non-profits, retirement operators) for weekly checking, so a slow
  posting week never looks empty.
- **Tailored documents**: one tap generates an **ATS-friendly resume** (graded in-page
  by a 21-point checker) and a **cover letter** (4 strongest points, simple English)
  for that exact posting, ready to download as Word files.
- **Paste matcher**: paste any posting from anywhere and it scores the fit and writes
  a tailored resume and cover letter for it too.

## How the daily refresh works (no keys needed)

A GitHub Actions workflow (`.github/workflows/refresh-jobs.yml`) runs **every day at
7:30 AM Toronto time** and executes `scripts/refresh_jobs.py`, which:

1. Fetches live postings from the **SmartRecruiters public API** (keyless) for direct
   employers such as University Health Network (UHN), and from **BambooHR public
   career feeds** (keyless) for community organizations.
2. Optionally adds breadth via the **Adzuna API** if free keys are configured.
3. **Enforces freshness**: drops anything older than 30 days or past its closing
   date, so the board always shows recent, open postings.
4. Commits and pushes, then deploys the updated site to Netlify via the deploy API
   (using the `NETLIFY_AUTH_TOKEN` and `NETLIFY_SITE_ID` repository secrets) and
   redeploys GitHub Pages automatically.

To add more SmartRecruiters employers, extend `SMARTRECRUITER_EMPLOYERS` in
`scripts/refresh_jobs.py` with their company slug. To add more BambooHR sources,
extend `BAMBOO_EMPLOYERS` with their subdomain.

To add the optional Adzuna source: create free keys at developer.adzuna.com and add
them as repository secrets `ADZUNA_APP_ID` and `ADZUNA_APP_KEY`.

## Deploy elsewhere

The site is fully static (`index.html` + `jobs.json`), so it also runs on
Netlify (drag-and-drop) or Cloudflare Pages. The included `netlify.toml` is harmless
on GitHub Pages.

## For the user (no tech needed)

1. Open the site link on a phone.
2. Current postings are already there. Tap **Type** and **Location** to narrow down.
3. Tap **Apply here** on any job to open the employer's application page.
4. Tap **Show tailored resume** and **Show cover letter**, then download both.
5. Attach both files to the application.

If there are no fresh postings this week, use the **Always-hiring direct employers**
section to check the employers' careers pages directly.

Note: the resume dates under "Balda Care Home" are placeholders. Fill in the real
dates once, and every generated resume grades 100/100 on the built-in ATS checker.
