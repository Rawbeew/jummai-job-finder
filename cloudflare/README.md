# Cloudflare Worker — fresh Ontario jobs → Netlify

This worker keeps `just-hired` (formerly `jummai-job-finder`) full of
**only fresh, direct-employer jobs**.
It runs every 2 hours on Cloudflare (whose IPs Job Bank trusts — GitHub's datacenter
IPs get blocked), fetches Job Bank + UHN, composes `jobs.json`, and redeploys the
static site to Netlify.

## Why this exists
- Job Bank Canada rate-limits / JS-challenges **GitHub Actions** (cloud) IPs → the
  daily GH workflow often got 0 Job Bank results.
- **Cloudflare Workers egress is trusted by Job Bank** (verified live: 25 articles,
  no challenge) → the board gets real Ontario volume.
- This worker is the "push the heavy/architecturally-lagging work off cloud and into
  Cloudflare" piece: no always-on machine, no new API keys (reuses the Netlify token).

## What it does (every 2h on cron `17 */2 * * *`)
1. Fetches **Job Bank Canada** — 5 Ontario queries (PSW / care aide / caregiver /
   home support / DSW) with retry + backoff, dropping out-of-province + agencies
   (VON, Bayshore, CBI, home-care staffing firms) per the "direct employers only"
   rule. Tags region (North York / TTC ≤40min / other Ontario).
2. Fetches **UHN** (SmartRecruiters, keyless) — care + office/admin roles,
   tagged `remote_capable` / `adjacent`.
3. Keeps only postings released within **12h** (fresh-only rule).
4. Fetches the **current live `index.html` + `netlify.toml`** from the site,
   zips them with the fresh `jobs.json` (minimal hand-rolled zip writer —
   no dependency), and **deploys to Netlify** via the API.

## Deploy (from the worker dir in this repo)
```bash
cd cloudflare
export CLOUDFLARE_API_TOKEN=<CF token w/ Workers Scripts: Edit>
export CLOUDFLARE_ACCOUNT_ID=<account id>
wrangler secret put NETLIFY_TOKEN --name jummai-jobs        # Netlify API token (nfp_...)
wrangler secret put NETLIFY_SITE_ID --name jummai-jobs      # 3ba2226e-...
wrangler secret put SITE_ORIGIN --name jummai-jobs          # https://jummai-job-finder.netlify.app
wrangler deploy --name jummai-jobs
```

## Keys / notes
- Worker name: `jummai-jobs`. Endpoint: `https://jummai-jobs.<sub>.workers.dev`.
  `GET /health` → liveness; any other GET triggers a manual run (debug).
- Secrets are injected by Cloudflare (never in code).
- Cron cadence + `AGE_HOURS` (freshness window) are constants at the top of `index.js`.
- The GitHub Actions workflow (`refresh-jobs.yml`) remains as **backup** for the
  UHN/other sources; Cloudflare is the primary Job Bank path.

## How to update / redeploy
Edit `index.js`, then `wrangler deploy --name jummai-jobs` (same env vars). The
repo copy in `cloudflare/` is the source of truth — keep it in sync.
