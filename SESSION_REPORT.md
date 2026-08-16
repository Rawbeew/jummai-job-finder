# Session Report — Jummai's PSW Job Finder

**Date:** 16 August 2026
**Client:** Jummai Salami Raji (certified Personal Support Worker, North York, Toronto)
**Built for:** a friend of the user, who asked me to help her maximize her earning potential in Ontario's healthcare market.
**Outcome:** a live, self-refreshing job board + ATS resume & cover-letter builder, deployed free on two hosts, with a keyless daily auto-fetch of real employer postings.

**Live:**
- Netlify: https://jummai-job-finder.netlify.app
- GitHub Pages: https://rawbeew.github.io/jummai-job-finder/
- Repo: https://github.com/Rawbeew/jummai-job-finder

---

## 1. Executive summary

Over a single working session we took a real person's resume PDF and turned it into a complete, automated job-application system:

1. **Career strategy** grounded in current 2026 Ontario pay data (private care vs. institutional vs. adjacent roles vs. RPN).
2. **An ATS-compliant resume** rebuilt to Canadian conventions, plus a **landing page** for private clients, a **perks ranking**, an **adjacent-roles ladder**, and **email templates**.
3. **A consolidated web tool** that lists direct-employer postings (no agencies), shows each job's requirements and application link, and generates a **tailored resume + cover letter per posting** as a real Word file.
4. **A harsh ATS grader** (21 checks) that scores every generated resume — currently **95/100**, with the single deduction being a date the client must supply herself (we refuse to fabricate it).
5. **Daily automation**: a keyless fetch of live postings via the SmartRecruiters public API, a GitHub Actions schedule (07:30 Toronto time), and automatic deploys to both Netlify and GitHub Pages.

The system is deliberately **phone-first and plain-language**, because the end user is not comfortable with technology — she can even have each job posting read aloud.

---

## 2. The client

- **Name:** Jummai Salami Raji
- **Role:** Personal Support Worker (PSW) / Caregiver, North York, ON
- **Education:** PSW Diploma (Pharma Medical Science College, Toronto) · B.Sc. in Accounting (University of Maiduguri, Nigeria)
- **Certifications:** Nonviolent Crisis Intervention (CPI), Gentle Persuasive Approach (GPA), Standard First Aid & CPR (Red Cross), Infection Prevention & Control, Mask Fit, AODA
- **Experience:** 7+ years — Chartwell (Thornhill), Villa Colombo (Toronto), Sanctuary Nursing Home (Abuja), Regina Mundi Elderly Home (Lagos), Balda Care Home (Lagos, 1:1 Alzheimer's care)
- **Key differentiators:** CPI + GPA + real Alzheimer's/dementia experience (rare among PSWs), plus an Accounting degree (rare among caregivers)
- **Constraints:** not tech-savvy; HSCPOA registration still in progress (so we must not claim it yet); Balda Care Home employment dates missing from the original resume.

---

## 3. The problem

- PSWs in Toronto are paid ~$20/hr by agencies while agencies bill families $35–45/hr — the margin goes to the middleman.
- The best-paying standard PSW roles ($31–34/hr at hospitals and the City of Toronto) sit behind ATS systems and specific requirements (HSCPOA, BCLS).
- Her strongest assets (CPI, GPA, dementia care, Accounting degree) qualify her for **adjacent** roles that pay more than standard PSW work — but she had no way to discover or target them.
- Job boards bury direct employers under agency ads.
- The user wanted all of this to **refresh daily** and to be **hosted permanently**, with an ATS resume tailored to *each* posting.

---

## 4. The complete session log (the back-and-forth)

### Turn 1 — "How do I make her earn as high as possible?"
**They asked:** a strategy question, plus whether to start by tweaking the resume or building a private-care landing page.
**What I did:** extracted and read the resume PDF; pulled live 2026 pay data; built **both** the upgraded resume (`Jummai_Raji_PSW_Resume.docx`) and the private-care landing page (`Jummai_Care_LandingPage.html`); gave a two-track recommendation.
**Why:** the data showed the highest *ceiling* was private care (agencies bill $35–45, pay PSWs ~$20 — go direct and keep the spread), but the highest *floor* was institutional work that pays immediately. Running both tracks maximizes total earnings. I answered the either/or with "both," because the assets are complementary, not competing.

### Turn 2 — "Build a tool for job postings that matches her resume. Direct employers if possible, less of agencies."
**What I did:** built `PSW_Job_Match_Tool.html` — a scoring engine (weighted skill groups vs. posting text), 19 embedded postings, direct-employer-first ranking, a paste-a-posting matcher, an employer directory, and a before-you-apply checklist. Verified scoring math in Node.
**Why:** a scoring engine is more durable than a static list — it keeps working on any posting she pastes. I deliberately **weighted direct employers higher** (priority = match × 0.7 + tier × 0.3) and greyed out agencies, because the user's explicit goal was to avoid agency rent-taking.

### Turn 3 — "With her certification, there are higher paying adjacent roles."
**What I did:** researched behavioural support, DSW, unit clerk, care coordinator, restorative, and RPN pay (2026); built `Jummai_Adjacent_Roles_Ladder.html` (tier A "apply now" / B "small step" / C "strategic"); extended the matcher's keyword groups to recognize adjacent roles.
**Why:** her CPI/GPA/dementia trio maps to **behavioural** roles (LOFT pays $52–67k), and her Accounting degree maps to **clerical/coordination** roles (unit clerk $26–30/hr) — both out-earn standard PSW work without new schooling. The ladder frames *time-to-payoff*, which is what actually drives a career decision.

### Turn 4 — "Summarize each posting: what's needed, is she qualified, what strength wins it. Exclude agencies."
**What I did:** built `Jummai_Job_Posting_Summary.html` — 13 direct postings with ✓ qualified / △ conditional / ✗ wrong-posting verdicts, each with the specific strength from her resume that wins it, and the shared gaps (HSCPOA, BCLS).
**Why:** converting raw postings into verdicts turns the tool from a list into a decision aid. The honest verdict (e.g. the City's *bilingual* posting is ✗ for her, but its *English-only* sibling at the same $31–34 rate is a top target) is more useful than blanket optimism.

### Turn 5 — "Look for perks-providing employers, then email to contact. She's not conversant with tech."
**What I did:** researched HOOPP/OMERS pensions, vacation, bonuses, and the **BEGIN** tuition program; built `Jummai_Perks_Employers.html` and `Jummai_Email_Templates.txt` (5 plain-English emails + a phone script + a step-by-step "how to attach your resume" guide).
**Why:** total compensation (pension + benefits + paid sick days) is worth more than a dollar or two of hourly rate — HOOPP is a defined-benefit pension private operators don't offer. BEGIN makes her future RPN upgrade nearly free (up to $6,000/yr). The email kit had to be copy-paste simple because she isn't technical.

### Turn 6 — "Always refresh daily… what if she can download an ATS resume for that same posting?"
**What I did:** was honest that a 24/7 bot can't live inside chat, but made refresh **on-demand** (one message = re-fetch in seconds); built `Jummai_Resume_Builder.html` that generates a real `.docx` **entirely in the browser** (hand-written OOXML zip writer, no internet, no install); wired a "Download tailored resume" button into the match tool.
**Why:** I set expectations honestly about the refresh mechanism, and chose browser-side `.docx` generation so the resume feature works offline on her phone with zero dependencies — important for a non-technical user.

### Turn 7 — "One tool: fetch PSW + adjacent roles across GTA & environs, add application link + highlights + ATS resume per job."
**What I did:** consolidated everything into `Jummai_Job_Finder.html` — 25 direct postings, each card showing match score, requirements highlights, **application link**, and an inline tailored resume with download.
**Why:** consolidation reduces cognitive load for the end user (one URL, one flow). Every card carries all four requested elements.

### Turn 8 — "What if you host on Cloudflare Pages or Netlify?"
**What I did:** created the `hosted/` project — **split the app (`index.html`) from the data (`jobs.json`)** so refresh touches only data; added `netlify.toml`, a GitHub Actions workflow, `scripts/refresh_jobs.py` (optional Adzuna), and `README_DEPLOY.md`.
**Why:** static hosting is free and permanent, and hosting fixes the one preview limitation (download buttons). The app/data split is the architectural key that makes "refresh daily" cheap — the app never changes, only the JSON does.

### Turn 9 — "If she had a PSW licence, earning potential goes up? (certificate is coming, don't put it on the CV — that would be fraud. Don't touch the build.)"
**What I did:** answered "Yes" with the concrete math (HSCPOA unlocks $31–34/hr hospital/City roles and legitimizes $40–50/hr private), recommended the honest interim phrasing ("registration in progress") **only** on application forms, and **did not touch the build**.
**Why:** the integrity constraint is non-negotiable — I will not fabricate a credential. The grader's only deduction (missing Balda dates) is the same principle applied: better 95/100 honest than 100/100 invented.

### Turn 10 — "Fine-tune the website, it looks AI-ish. Look for inspiration on getdesign.md."
**What I did:** pulled two real DESIGN.md briefs (Claude, Mastercard) and restyled the whole site on their tokens — warm cream canvas, single coral accent, editorial serif headlines, hairline borders, flat color-block elevation, **removed every emoji, gradient, and rainbow badge**.
**Why:** the "AI look" comes from gradients, emoji, pill-rainbow badges, and shadow-on-everything. The Claude brief's principles ("color-block first, shadow rare," cream + coral + ink trinity, serif display) were the antidote, applied without changing any function.

### Turn 11 — "Edit the whole wording. She is the user, not me. Host on Netlify, always auto-refresh."
**What I did:** rewrote every string to second person ("Your job board," "Tick what you have," "true to your experience"); built a **live feed** into the page (Adzuna slot with key placeholders); fixed the offline fallback; updated the workflow and README around true auto-refresh.
**Why:** the site is *hers* — third-person copy ("Built for Jummai…") reads as a developer's artifact. Auto-refresh needed two layers: the scheduled pipeline (reliable) and the optional live feed (instant).

### Turn 12 — "They need a cover letter too. Simplified English, **no em dashes ever**."
**What I did:** added per-job cover-letter generation (and in the paste matcher) in simple English; **scrubbed every em/en dash** from `index.html`, `jobs.json`, generated text, and even the read-aloud and dash-stripping functions.
**Why:** employers (hospitals, the City) expect a cover letter with the application. "No em dashes" was an absolute style rule, so I enforced it globally rather than only in the letters — including replacing job-title dashes with commas and date dashes with "to."

### Turn 13 — "Test end-to-end and look for posting sources. Prefer direct company/employer postings."
**What I did:** wrote a full E2E harness (**44/44 passed** — load, filters, sort, match, resume, cover, docx validity, panels, read-aloud, paste matcher); hunted direct sources; added 4 fresh direct postings (City of Toronto PT LTC at $28.39–31.13, Hawthorne Place, Scarborough Retirement Residence, Amica) and enriched WoodGreen with its live GPA requirement; expanded the directory with a "direct-employer search tools" group (Job Bank, Durham Workforce Authority).
**Why:** testing isn't optional when the output is a person's job application. And direct-employer sources beat aggregators for exactly the user's reason — no agency middlemen.

### Turn 14 — "Tailor it the Canadian way, always ATS-compliant. Grade harshly as if you were the ATS, aim for 95%+. 'Dear Hiring Manager' sounds like AI — use 4 strongest points, mention the rest in passing."
**What I did:** Canadianized the resume (Canadian spelling, "City, Province" format, no photo/age/marital status, standard section order, month-year dates); built a **21-point ATS grader** that runs on every generated resume and displays its score in the UI; achieved **95/100 on all six job categories** (the only deduction = the honest Balda-dates placeholder); rewrote the cover letter with a **personal greeting** ("Dear [Employer] Recruitment Team,") and **exactly 4 strongest points + a single "I also bring…" bonus line**; added a 6-rule cover check (100%).
**Why:** ATS software is the gatekeeper, so I *became* the grader — and then closed every checkable gap. 100% would require inventing her Balda dates, which we won't do. The cover-letter rules directly answer "what makes it sound human": a real addressee and a focused 4-point structure beat a boilerplate "Dear Hiring Manager" wall of text.

### Turn 15 — "Here's a throwaway GitHub token. Host on GitHub and find a way to auto-fetch daily."
**What I did:** verified the token (account `Rawbeew`); discovered Job Bank's RSS is dead and Adzuna needs a key, but **SmartRecruiters' public API is keyless** (UHN exposes 181 live postings, including 4 fresh PSW roles); wrote a keyless `refresh_jobs.py`; created the repo, pushed, enabled GitHub Pages, verified live.
**Why:** the auto-fetch must not depend on keys to be durable. Finding a *keyless* official employer API (the same feed UHN uses) was the highest-value discovery of the session.

### Turn 16 — "Here's a Netlify token too."
**What I did:** verified the token (`rajirabiu3@gmail.com`); created the Netlify site, deployed; **fixed a 401** (Netlify's SSO-login was on by default — disabled it so the site is public); encrypted `NETLIFY_AUTH_TOKEN` + `NETLIFY_SITE_ID` into GitHub Actions **secrets** (libsodium sealed-box); updated the workflow to deploy to Netlify after each refresh; **triggered the workflow live and watched it deploy**; fixed a dedup bug (two UHN postings share a title) so all 4 live postings survive.
**Why:** secrets go in the encrypted store, never in the repo. Running the pipeline once, not just reading it, is the only way to know it works.

### Turn 17 — "Where does she see the application link?"
**What I did:** pointed to the first button on each card; then **improved it** — renamed the vague "Apply / open posting" to **"Apply here"** (or "Find application page" for search-linked homes), made it bigger/bolder, and added a "The application opens on [site]" hint under each card; deployed to both hosts.
**Why:** for a non-technical user, "where do I click" is the whole ballgame. A button that says *where it goes* removes the last moment of hesitation.

### Turn 18 — (this turn) "Write everything about the session… add it to GitHub."
**What I did:** wrote this report and committed it to the repo.

---

## 5. Key decisions & reasonings (the "why" behind the how)

1. **Both tracks, not either/or.** Private care (ceiling) + institutional work (floor) are complementary income streams; building both assets costs little and hedges the timeline risk of filling a private client book.
2. **Direct employers weighted above agencies.** The agency spread ($35–45 billed vs. ~$20 paid) is pure margin the worker gives away. The tool structurally de-prioritizes agencies instead of just mentioning it.
3. **A scoring engine, not a static list.** Keyword-group weights let the same tool rank *any* posting she ever pastes — durable beyond any single snapshot of the job market.
4. **Adjacent roles are the real unlock.** CPI/GPA → behavioural roles ($52–67k); Accounting → clerical/coordination ($26–30/hr, pensioned); PSW diploma + degree → RPN bridge (BEGIN pays up to $6,000/yr). These beat standard PSW pay without new schooling.
5. **App/data separation.** `index.html` is static; `jobs.json` is the only file that changes. Refresh is a one-file swap, and the app falls back to an embedded snapshot offline.
6. **Keyless auto-fetch.** SmartRecruiters' public API (the feed UHN itself uses) provides real, current, direct-employer postings with salary and requirements — no keys, no scraping, no ToS risk.
7. **Integrity over perfection.** Never fabricate dates or credentials. The ATS grader honestly reports 95/100 because the Balda dates are placeholders; the HSCPOA licence is *not* claimed anywhere because it hasn't been issued. Both are the client's to fix, and the tool tells her exactly what to fix.
8. **Act as the ATS.** Building a 21-point grader and iterating until ≥95% is how "ATS-compliant" stops being a buzzword and becomes a measurable, displayed number.
9. **Human-sounding cover letters.** "Dear Hiring Manager" is the AI tell; a personal addressee plus a disciplined 4-point structure plus one "I also bring…" line reads like a person who knows her worth.
10. **De-AI the design.** Removed gradients, emoji, rainbow badges, and heavy shadows; adopted the warm-cream/coral/ink, serif-headline, hairline-border language from the Claude and Mastercard DESIGN.md briefs.
11. **Phone-first, plain-language, read-aloud.** The user isn't technical; `speechSynthesis` lets her *listen* to any posting, and every label says what it does.
12. **Secrets in the encrypted store.** Tokens go into GitHub Actions secrets via libsodium encryption, never into the repo, and the raw tokens should be revoked once setup is complete.

---

## 6. Architecture

```
GitHub (Rawbeew/jummai-job-finder)
├── index.html          ← the app: finder + grader + resume/cover-letter builder
├── jobs.json           ← the data: 33 direct-employer postings (29 curated + 4 live)
├── scripts/refresh_jobs.py   ← keyless fetcher (SmartRecruiters API)
├── .github/workflows/refresh-jobs.yml ← daily 07:30 Toronto, then deploy
├── netlify.toml / README.md
└── SESSION_REPORT.md   ← this document

Daily loop:
  schedule (07:30 ET) → refresh_jobs.py → SmartRecruiters API (keyless)
      → merge into jobs.json → commit+push
      → deploy to Netlify (API, secrets) + GitHub Pages (auto)

In-browser (no server):
  job card → "Apply here" → employer page
           → "Show tailored resume" / "Show cover letter"
           → generated in-page, graded by the 21-point ATS checker
           → downloaded as .docx (hand-written OOXML zip, offline)
```

---

## 7. Case study

### From agency-rate PSW to a self-refreshing, direct-employer job system — in one day

**Client profile.** Jummai Salami Raji is a certified PSW in North York with 7+ years of experience, a rare combination of certifications (CPI, GPA) and hands-on Alzheimer's care, and an Accounting degree. She is not comfortable with technology, and her HSCPOA registration is still in progress.

**Situation.** Toronto agencies bill families $35–45/hour for PSW care but pay the PSW roughly $20. The roles that pay well ($31–34/hour at hospitals and the City of Toronto) sit behind ATS filters and unadvertised requirements. Her highest-value skills pointed at adjacent roles she had no way to find. Her resume had ATS red flags (missing dates, passive language, buried certifications), and there was no cover letter at all.

**Solution.** Four pillars, built in sequence:

1. **Strategy with numbers.** Verified 2026 pay data across private care, institutional, adjacent, and RPN tracks; defined a two-track plan (institutional floor now, private ceiling over 3–6 months, RPN bridge later).
2. **Tooling.** A single phone-first web app that lists direct-employer postings only, shows each job's requirements and application link, and generates a tailored, ATS-compliant resume and cover letter per posting as a downloadable Word file.
3. **Automation.** A keyless daily fetch (SmartRecruiters public API), a GitHub Actions schedule, and automatic redeploys to Netlify and GitHub Pages — so the job board refreshes itself without anyone lifting a finger.
4. **Polish & integrity.** Canadianized, dash-free copy; a harsh 21-point ATS grader displayed in the UI; human-sounding 4-point cover letters; and a strict no-fabrication rule (missing dates and pending licences are surfaced, never invented).

**Results (measured in-session):**

| Metric | Result |
|---|---|
| Direct-employer postings listed (no agencies) | 33 (29 curated + 4 live) |
| Live postings fetched keylessly, with salary | 4 UHN PSW roles, two at **$31.70–$32.61/hr** |
| ATS score on every generated resume | **95/100** (100 once she fills in one date) |
| Cover-letter checks | 6/6, no "Dear Hiring Manager", 4 points + bonus |
| End-to-end tests | 44/44 passed |
| Hosts | Netlify + GitHub Pages, both live and in sync |
| Auto-refresh | Daily 07:30 Toronto, deploy-verified live |

**Lessons.**

- **The margin is the message.** Every agency ad she skips is the spread she keeps. Making "direct employers only" a structural feature, not advice, changed her outcomes.
- **Honesty compounds.** Refusing to fabricate a date or a licence cost a "perfect" score but preserved the thing that actually gets hired — trust.
- **Keyless beats keyed.** The most durable automation is the one that depends on no one's API key.
- **Design for the real user.** Read-aloud, plain labels, and a button that says where it goes turned a developer tool into something a non-technical person will actually use every day.

---

## 8. Deliverables

**Deployed (in the repo, live):**

| File | Purpose |
|---|---|
| `index.html` | Job finder + ATS grader + resume & cover-letter builder |
| `jobs.json` | 33 direct-employer postings |
| `scripts/refresh_jobs.py` | Keyless daily fetch |
| `.github/workflows/refresh-jobs.yml` | 07:30 Toronto schedule + Netlify deploy |
| `README.md` / `netlify.toml` | Docs & config |

**Workspace artifacts (strategy/design work, not deployed):**

| File | Purpose |
|---|---|
| `Jummai_Raji_PSW_Resume.docx` | The upgraded master resume |
| `Jummai_Care_LandingPage.html` | Private-client acquisition page |
| `PSW_Job_Match_Tool.html` | First matching tool (superseded by the consolidated app) |
| `Jummai_Adjacent_Roles_Ladder.html` | Behavioural / DSW / clerical / RPN ladder |
| `Jummai_Job_Posting_Summary.html` | Verdicts per posting |
| `Jummai_Perks_Employers.html` | HOOPP/OMERS/BEGIN perks ranking |
| `Jummai_Email_Templates.txt` | Plain-English emails + phone script |
| `Jummai_Resume_Builder.html` | Standalone browser .docx generator |

---

## 9. Security & housekeeping

- GitHub and Netlify access tokens were used **only** to create the repo, site, and encrypted deploy secrets. They were shared in chat, so they must be treated as compromised and **revoked**: GitHub at github.com/settings/tokens, Netlify at app.netlify.com → User settings → Applications.
- The daily pipeline does **not** depend on them: GitHub Actions uses its built-in `GITHUB_TOKEN`, and the Netlify deploy uses the **encrypted** `NETLIFY_AUTH_TOKEN` / `NETLIFY_SITE_ID` secrets.
- If changes are needed later, mint a fine-grained GitHub token scoped to this repo only (Contents + Pages + Workflows) and a short-lived Netlify token, and revoke both when done.

## 10. What's next (open items)

1. **Balda Care Home dates** — the only thing between 95 and 100 on every resume.
2. **HSCPOA registration** — the day it's issued, add it to the generator and every hospital door opens.
3. **BCLS card** — upgrade from First Aid/CPR to unlock UHN's $31.70–32.61 roles.
4. **Real caseload numbers** — replace "multiple" with actual counts (e.g. "8–10 residents").
5. **More SmartRecruiters employers** — extend `SMARTRECRUITER_EMPLOYERS` in `refresh_jobs.py` as more direct employers are identified.
6. **Optional Adzuna keys** — for broader coverage on top of the keyless source.
