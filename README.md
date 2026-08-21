# just-hired

Fresh-only direct-employer job board. Cloudflare Worker fetches Job Bank + UHN every 2h, only shows last 12h. ATS resume/cover letter generator. Zero stale leads.

## What it does
- Fetches Job Bank Canada + UHN career pages every 2 hours via Cloudflare Worker
- Filters for direct employers only (no staffing agencies)
- Only shows postings from the last 12 hours
- ATS-compliant resume builder + tailored cover letter generator
- Hosted free on Cloudflare Pages + Netlify

## Development approach
This project was built with AI-assisted development (Hermes/Claude) under human direction.
The architecture, Cloudflare Worker design, resume/cover letter prompts were directed by a human;
implementation was done by an LLM under supervision.

## Live
- Netlify: https://just-hired.netlify.app
- GitHub Pages: https://rawbeew.github.io/just-hired/

## Deployment

**Production architecture:**
```
Cloudflare Worker (cron '17 */2 * * *')
  → fetches Job Bank Canada + UHN career pages
  → filters direct-employer, last-12h-only
  → composes jobs.json → redeploys static site via Netlify API
Netlify Pages serves the board + ATS resume generator (client-side)
```

**Environment variables / secrets:**
| Var | Where | Purpose |
|---|---|---|
| `NETLIFY_TOKEN` | Worker secret | deploy API |
| `NETLIFY_SITE_ID` | Worker secret | target site |
| `SITE_ORIGIN` | Worker var | canonical URL for links |

**Reliability choices:**
- Cloudflare Workers egress reaches Job Bank; GitHub Actions runners get JS-challenged — that constraint drove the Worker-cron design
- Static output = zero server to keep alive; deploys are atomic (new jobs.json → instant swap)
- Fresh-only filter means stale data is structurally impossible, not just discouraged

**Cost:** $0. Free tier on both Cloudflare (100k req/day) and Netlify (300 build min/mo) — usage sits far below limits.

## What I would improve next

Honest trade-offs in the current design:

1. **Dedup by posting-hash across refreshes** — each 2h refresh recomputes the board from source. A content hash per posting (title+employer+URL) would let the Worker skip re-listing unchanged jobs and keep a stable "first seen" timestamp.
2. **Alert digest instead of individual pushes** — notifications fire per refresh cycle. A single daily digest (top N new matches, grouped by commute bucket) would be less noisy for the person actually job-hunting.
3. **Resume-tailoring eval set** — the ATS resume/cover-letter generator is prompt-driven with no regression suite. A small set of (job posting, expected resume emphasis) pairs scored on every prompt change would stop silent quality drift.

## License
MIT
