---
version: alpha
name: Jummai's Job Finder
description: Warm, trustworthy, high-contrast job board in service of a job seeker — every decision exists to help one person land a PSW role fast.
colors:
  primary: "#211D19"
  accent: "#B5503A"
  accent-strong: "#9C4430"
  accent-soft: "#F6E8E1"
  neutral: "#FAF9F5"
  neutral-card: "#FFFDFB"
  body: "#423E38"
  muted: "#6F6A62"
  faint: "#9A948B"
  hairline: "#E6DFD3"
  good: "#3F7D5C"
  warn: "#9A6A20"
  bad: "#B4453A"
typography:
  body:
    fontFamily: "Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif"
    fontSize: 15px
    fontWeight: 400
    lineHeight: 1.55
  h1:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: 34px
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: "-0.02em"
  h2:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: 23px
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "-0.01em"
  label-caps:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: 10.5px
    fontWeight: 600
    letterSpacing: "0.08em"
    textTransform: uppercase
rounded:
  sm: 8px
  md: 10px
  lg: 16px
  pill: 999px
spacing:
  xs: 6px
  sm: 12px
  md: 16px
  lg: 24px
  xl: 32px
elevation:
  card:
    backgroundColor: "{colors.neutral-card}"
    border: "1px solid {colors.hairline}"
    borderRadius: "{rounded.md}"
  card-hover:
    backgroundColor: "{colors.neutral-card}"
    border: "1px solid {colors.accent-strong}"
    borderRadius: "{rounded.md}"
    boxShadow: "0 6px 20px -8px oklch(30% 0.05 30 / 0.18)"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.neutral}"
    rounded: "{rounded.pill}"
    padding: "10px 18px"
  button-primary-hover:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.neutral}"
    rounded: "{rounded.pill}"
  match-percent:
    backgroundColor: "{colors.accent-soft}"
    textColor: "{colors.accent-strong}"
    rounded: "{rounded.md}"
  highlight-box:
    backgroundColor: "{colors.accent-soft}"
    border: "1px solid {colors.hairline}"
    rounded: "{rounded.md}"
---

## Overview

Jummai's Job Finder is a **single purpose**: help one recently-graduated PSW
land a well-paying role in Toronto within 30 days of graduating. It is not a
generic job aggregator — it is a personal, trustworthy board. Every visual
decision reinforces clarity, warmth, and urgency: calm backgrounds, one strong
interaction accent (coral), and clear match % so the job seeker sees at a glance
which postings to prioritize.

## Colors

- **Primary ink (#211D19)** — headlines and the primary button. Rooted, calm, always readable.
- **Accent coral (#B5503A)** — the *only* interactive color on the page. Used for the match % and hover states. Matches `--coral` / `--coral-deep` in the current `:root`.
- **Neutral canvas (#FAF9F5 → card #FFFDFB)** — warm off-white, not clinical. Easy on the eyes for long scanning sessions.
- **Semantic** — `good` (green) for positive matches, `warn` (amber) for closing-soon / caution, `bad` (red) for deal-breakers.

## Typography

Inter (system fallback stack) everywhere. Body 15px/1.55 for comfortable
scanning. All-caps micro-labels at 10.5px with wide letter-spacing for section
headers and stat labels (the `.lbl` / `.cap` pattern). One clear heading scale:
34px hero, 23px section, ~16px job titles.

## Layout & Spacing

Content lives on a centered column with a max width. Cards are separated by
consistent 14px gaps and grouped under labeled sections so the eye can skip
straight to the "evergreen / always-hiring" zone. Generous header padding (56px)
gives the page an authoritative, editorial feel rather than a cramped dashboard.

## Elevation & Depth

Cards use subtle 1px hairlines rather than heavy shadows — warmth over
shadow-box. On hover, the accent border plus a soft drop shadow lift the job
card just enough to signal "this one is worth opening."

## Shapes

Rounded-corners language: 10px cards, 8px small elements, 999px pills for
filter chips and buttons. No sharp corners — soft but not childish.

## Components

- **Filter chips (`.fbtn`)** — pill toggles; active state fills ink on canvas for
  unmistakable state.
- **Stat cards (`.stat`)** — big number + all-caps label; gold variant tints the
  number coral for the headline metric.
- **Job card (`.job`)** — title, employer badge, meta line, match box on the
  right with match % in accent-strong.
- **Highlight box (`.hl`)** — warm coral-soft panel for "required for you"
  breakdowns and evergreen always-hiring lists.
- **Button primary** — ink pill, coral on hover, white text. One strong CTA.

## Do's and Don'ts

- DO keep the match % the visual anchor — it is the whole point.
- DO use the coral accent sparingly so it never gets washed out.
- DON'T introduce a second interactive color — that dilutes urgency.
- DON'T add heavy shadows; warmth comes from color, not depth.
- DO keep it mobile-first readable during a rushed subway scroll.
