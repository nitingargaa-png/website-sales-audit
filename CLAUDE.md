# Website Sales Audit — AI Agency Project
# Claude Code Project Configuration
# Place this file at: C:\Users\canad\projects\website-sales-audit\CLAUDE.md
# Last updated: April 2026 — v3 (SKILL.md bumped to v12: weighted 0–100 health score,
#                                 research-phase follow-up sequence, de-AI-ify QC pass)

---

## Project Purpose

AI-powered local home service business website agency.
Sells websites + GHL automation systems to plumbers, HVAC, cleaners,
roofers, pest control, landscaping, and other trades.
Primary market: USA + Canada (GTA focus).

---

## Trigger Commands

### Run a website audit
```
audit https://[url] and prepare full call prep
```
Executes: docs/SKILL.md (v11)
Outputs: 4 reports saved to output/[businessname]-[date].md

**What happens under the hood (in order):**
1. Installed audit skills run first (technical + SEO lens) — see Audit Skills section below
2. docs/SKILL.md full audit (business/sales lens)
3. Findings from all skills injected into TALKING POINTS as "Technical Findings" block

**Automatic triage handoff (runs after every audit — do not skip):**
After saving the audit report to output/, immediately run:
```
python3 execution/triage_handoff.py --audit output/[businessname]-[date].md
```
This scores the prospect across all four GHL services (MCTB, VAAI, GRM, WEB)
using the audit findings. Results land in ../ghl-triage/output/ automatically.
If ghl-triage is not set up yet, skip this step and note it for later.

### Build a production site autonomously
```
execute WEBSITE_GENERATION_SKILL.md using output/prompt_packages/[file].json
```
Executes: docs/WEBSITE_GENERATION_SKILL.md
Does: scaffolds React project → builds → deploys to Netlify

---

## Audit Skills — Installed in .agents/skills/

These skills run BEFORE docs/SKILL.md on every `audit` command to add a
technical layer on top of the business/sales lens.

### Skill 1 — seo-audit (coreyhaines31/marketingskills)
**When to invoke:** Always. Primary SEO layer for every prospect audit.
**What it covers:**
- Crawlability and indexation (can Google find and index the site?)
- Title tags, meta descriptions, heading structure, internal linking
- Image optimization and keyword targeting
- Content quality and authority signals
- Local business site-specific guidance
**How findings map to docs/SKILL.md:**
- Indexation issues → reinforces JS-only site flag (Phase 1)
- Missing meta/titles → CHECK 3 (content gaps)
- Authority signals → CHECK 7 (trust / social proof)

### Skill 2 — seo-audit (agricidaniel/claude-seo)
**When to invoke:** Run alongside Skill 1 as a cross-check. Use when Skill 1 findings
feel thin or the site is on an unusual platform (Wix, Squarespace, GHL).
**What it covers:** Complementary SEO audit framework — useful for catching
issues the coreyhaines31 skill misses on non-standard site builds.

### Skill 3 — web-quality-audit (addyosmani/web-quality-skills)
**When to invoke:** Always on mobile-heavy trades (plumbing, HVAC, garage door).
Home service customers search on phones — page speed directly costs calls.
**What it covers:**
- Core Web Vitals (LCP, CLS, FID/INP)
- Page load performance and resource usage
- Mobile responsiveness and touch targets
**How findings map to docs/SKILL.md:**
- Speed issues → CHECK 2 (design/mobile)
- Mobile failures → CHECK 2 and TALKING POINTS

### Skill 4 — accessibility + seo + performance (addyosmani/web-quality-skills)
**When to invoke:** Always — runs alongside web-quality-audit as the full
Addy Osmani quality suite.
**What it covers:**
- `accessibility` — WCAG compliance, color contrast, keyboard navigation,
  screen reader compatibility. Accessibility failures also hurt Google rankings.
- `seo` — Dedicated SEO layer covering structured data, canonical URLs,
  sitemap, robots.txt, and indexability signals.
- `performance` — Deep performance analysis beyond Core Web Vitals — resource
  loading, render blocking, caching, third-party script impact.
**How findings map to docs/SKILL.md:**
- Accessibility failures → CHECK 2 (design/mobile)
- SEO signals → CHECK 3 (content) and TALKING POINTS
- Performance issues → CHECK 2 and TALKING POINTS

### Skill 5 — on-page-seo-auditor + domain-authority-auditor (aaron-he-zhu)
**When to invoke:** Use domain-authority-auditor when prospect has competitors
to compare against — strong outreach hook ("your competitor outranks you").
Use on-page-seo-auditor for deep per-page analysis on higher-value prospects.
**What it covers:**
- On-page optimization per URL
- Domain authority vs. local competitors
**How findings map to docs/SKILL.md:**
- Authority gap vs. competitors → TALKING POINTS cold email hook

### Skill 6 — backlink-analyzer (aaron-he-zhu/seo-geo-claude-skills)
**When to invoke:** When you need a competitor comparison hook for cold outreach.
**What it covers:** Backlink gap analysis — shows who links to competitors but not
the prospect. Strongest when used alongside domain-authority-auditor.
**How findings map to docs/SKILL.md:**
- Competitor authority gap → TALKING POINTS cold email hook

---


### Skill 7 — audit-website (squirrelscan/skills) ← NEW
**When to invoke:** As a cross-check alongside Skill 1 — runs a complementary
website audit framework with a different scoring approach.
**What it covers:** Technical and content audit with structured output format —
useful for catching issues the coreyhaines31 seo-audit misses.
**How findings map to docs/SKILL.md:**
- Technical findings → reinforces Phase 1 feature detection
- Content gaps → CHECK 6 (content clarity)

### Skill 8 — accessibility (addyosmani/web-quality-skills) ← NEW
**When to invoke:** On every audit — accessibility issues hurt Google rankings
for client sites AND make the audit report more compelling.
**What it covers:** WCAG 2.1 AA compliance — contrast, ARIA, keyboard nav,
focus management. Run alongside web-quality-audit as the full quality suite.
**How findings map to docs/SKILL.md:**
- Accessibility failures → CHECK 2 (mobile) and TALKING POINTS
- Google rankings context → adds urgency to website rebuild pitch

---

### How all audit skills feed into the report output

After running all applicable skills, inject a consolidated block into the
TALKING POINTS section of the report:

```
## What Google Sees (That Your Customers Don't)

A technical scan of your site found [N] issues:
- [Plain-English finding from web-quality-audit — e.g. "takes 6+ seconds to load on a phone"]
- [Plain-English finding from seo-audit — e.g. "several pages can't be found by Google"]
- [Plain-English finding from on-page-seo — e.g. "no location info on key service pages"]

These are invisible to visitors but visible to Google — and they affect
how often your phone rings.
```

IMPORTANT: Translate ALL technical findings into plain language.
Apply the BANNED WORDS list from docs/SKILL.md to every skill output before
including it in any report section.

MANDATORY OUTPUT ENFORCEMENT — TALKING POINTS SECTION
Every audit MUST include ALL of the following in the Talking Points output,
every single time, no exceptions:

1. FEATURE DETECTION TABLE — completed with actual detected values, not
   placeholder brackets. Every row must be filled based on Phase 1 findings.

2. GHL AUTOMATION GAP — Tier 1 and Tier 2 sections both present, with each
   item marked PRESENT, ABSENT, or UNKNOWN based on actual detection.

3. COMPETITOR EDGE — at least 1 named local competitor with specific review
   count or differentiator found during Phase 1 research. If no competitor
   was found during scraping, run a Brave Search for "[trade] in [city]"
   before writing the Talking Points. Never leave this section blank.

4. FOLLOW-UP SEQUENCE — all 5 touches (Day 0 / Day 3 / Day 7 / Day 14 / Day 21
   break-up), customized to the actual prospect. Complete the mandatory
   pre-sequence research pack first (#1 issue + quick win + competitor stat +
   ONE live signal from last 30 days). If no live signal can be found, PAUSE
   the sequence before Touch 3 — do not fabricate. Pull specific details from
   the audit. Never use placeholder brackets in final output.
   Source: docs/SKILL.md FOLLOW-UP SEQUENCE block.

5. WEIGHTED HEALTH SCORE — every audit must produce a 0–100 overall score
   (per-area 1–5 × home-services weights) displayed in Report B and in the
   Talking Points Feature Detection section. Score drives pitch tier:
   ≤40 → Package 2 or 3 minimum; 41–65 → Package 1 + automation add-ons;
   66+ → automation-only pitch, no rebuild. Source: docs/SKILL.md Phase 2
   "WEIGHTED HEALTH SCORE" block.

If any of these 5 items is missing from the output, the audit is incomplete.
Run the missing section before declaring the task done.

---

## Marketing Skills — Installed in .agents/skills/

These skills support outreach, copy, and pitch material generation.
They activate automatically when relevant tasks are requested in Claude Code.

### marketing-psychology (coreyhaines31/marketingskills)
**When to invoke:** When writing homepage hero copy, review section copy, or
any persuasion-heavy section of a demo site or cold email.
**What it covers:** Cialdini principles, social proof frameworks, urgency/scarcity
patterns — applied to marketing copy.
**Best used with:** `copywriting` for execution, `copy-editing` for refinement.

### copywriting (coreyhaines31/marketingskills)
**When to invoke:** When writing any site copy — hero headlines, service
descriptions, about section, review callouts. Also for cold email body copy.
**What it covers:** Conversion-focused copywriting frameworks for marketing pages.
**Best used with:** `marketing-psychology` for psychology-backed copy,
`copy-editing` for refinement after first draft.

### cold-email (coreyhaines31/marketingskills)
**When to invoke:** When drafting outreach emails to prospects from the audit list.
**What it covers:** B2B cold email structure, subject lines, follow-up sequences,
reply-driving frameworks — directly applicable to Animo Automation outreach.
**Best used with:** `copywriting` + `marketing-psychology` for strongest emails.

### copy-editing (coreyhaines31/marketingskills)
**When to invoke:** After any draft copy is written — cold emails, site copy,
audit talking points. Final polish before sending or publishing.
**What it covers:** Removes filler, tightens sentences, improves clarity and flow.

### content-strategy (coreyhaines31/marketingskills)
**When to invoke:** When planning content for a client site — what pages to
build, what topics to cover, how to structure the information architecture.
**What it covers:** Content planning, topic prioritization, audience mapping.

### page-cro (coreyhaines31/marketingskills)
**When to invoke:** When reviewing a built demo site before sending to a prospect,
or auditing a prospect's existing site for conversion gaps.
**What it covers:** Above-fold clarity, CTA placement, form friction, trust signals,
mobile tap targets.
**How findings map to docs/SKILL.md:**
- CRO gaps on prospect site → CHECK 10 (lead capture) and TALKING POINTS

### form-cro (coreyhaines31/marketingskills)
**When to invoke:** When reviewing or building the contact/quote form on any
client site. GHL forms are the primary lead capture — make them convert.
**What it covers:** Form field optimization, friction reduction, trust signals
around forms, confirmation flow best practices.

### ai-seo (coreyhaines31/marketingskills)
**When to invoke:** When building or reviewing any client site for AI search
visibility (AI Overviews, AEO, GEO). Complements seo-audit.
**What it covers:** Structured content for LLM citation, AI Overview optimization,
answer engine optimization patterns.

### seo-geo (resciencelab/opc-skills)
**When to invoke:** For any GTA or DFW prospect — local SEO and geo targeting
is critical for home service businesses competing in specific cities/neighborhoods.
**What it covers:** Local SEO signals, geo metadata, NAP consistency, service
area targeting, neighborhood-level keyword strategy.

### site-architecture (coreyhaines31/marketingskills)
**When to invoke:** When planning a multi-page site build. Run before generating
the prompt package to validate page hierarchy and URL structure.
**What it covers:** Page hierarchy, navigation design, URL structure, internal
linking strategy.

### launch-strategy (coreyhaines31/marketingskills)
**When to invoke:** When a client site is ready to go live — plan the launch,
handoff to GHL, and first 30-day activation sequence.
**What it covers:** Launch planning, go-live checklist, post-launch monitoring,
early traction strategies.

### sales-enablement (coreyhaines31/marketingskills)
**When to invoke:** When creating agency pitch materials — proposals, one-pagers,
objection handling scripts, demo walk-through scripts.
**What it covers:** Sales decks, one-pagers, objection handling, demo scripts —
directly useful for Animo Automation prospect calls.

### customer-research (coreyhaines31/marketingskills)
**When to invoke:** When preparing for a cold outreach campaign to a new niche
or when building a demo site and needing deeper insight into buyer motivations.
**What it covers:** Research frameworks for understanding prospect pain points,
objections, and decision triggers — improves cold email hooks and site copy.

### lead-magnets (coreyhaines31/marketingskills)
**When to invoke:** When building client sites — every home service site should
have a lead magnet (free estimate, free inspection, etc.) as the primary CTA.
**What it covers:** Lead magnet strategy, offer design, placement on site,
GHL integration for lead capture and follow-up automation.

### competitor-teardown (inference-sh-1/skills)
**When to invoke:** When preparing cold outreach — tear down the prospect's top
competitor to build a "here's what they're doing that you're not" hook.
**What it covers:** Competitor site analysis, feature comparison, positioning gaps,
outreach angle generation.
**Best used with:** `backlink-analyzer` + `domain-authority-auditor` for full
competitive picture.

### customer-persona (inference-sh-1/skills)
**When to invoke:** When entering a new niche or building a demo site — understand
who the customer is before writing copy or structuring the site.
**What it covers:** Customer persona building — demographics, pain points, buying
triggers, objections, preferred channels. Improves targeting per trade.

### press-release-writing (inference-sh-1/skills)
**When to invoke:** When a client site launches or when announcing agency news —
Animo Automation client wins, new market expansion, etc.
**What it covers:** Press release structure, headline writing, distribution strategy.

### social-content (coreyhaines31/marketingskills)
**When to invoke:** When building a client's social media presence at launch —
Facebook, Google Business Profile posts, and service announcements.
**What it covers:** Social media content creation, platform-specific formatting,
content calendars — useful for client onboarding and launch strategy.
**Best used with:** `launch-strategy` for coordinated go-live content.

### pricing-strategy (coreyhaines31/marketingskills)
**When to invoke:** When structuring or refining Animo Automation's own packages
(Foundation, Growth System, Voice AI) or advising clients on service pricing.
**What it covers:** Pricing frameworks, packaging strategy, anchoring,
value-based pricing — applicable to both agency pricing and client site pricing pages.

### programmatic-seo (coreyhaines31/marketingskills)
**When to invoke:** When building client sites with multiple service pages —
plumbing in Mississauga, plumbing in Brampton, plumbing in Oakville, etc.
**What it covers:** Scaling SEO content across location and service variations —
templates, internal linking strategy, page structure for programmatic pages.

### marketing-ideas (coreyhaines31/marketingskills)
**When to invoke:** When brainstorming outreach angles for a new niche or
when a cold email campaign needs fresh hooks.
**What it covers:** Marketing ideation frameworks — generates niche-specific
campaign ideas, offer angles, and positioning concepts.

### ad-creative (coreyhaines31/marketingskills)
**When to invoke:** When a client asks about running Google or Facebook ads
alongside their new site — or when building ad landing pages.
**What it covers:** Ad creative generation — headlines, descriptions, primary text,
A/B variants for Google Ads and Meta campaigns.

### analytics-tracking (coreyhaines31/marketingskills)
**When to invoke:** When setting up or auditing Google Analytics / GA4 on a
client site at launch. Ensures tracking is correctly configured before go-live.
**What it covers:** GA4 setup, event tracking, conversion goals, UTM parameters —
proves ROI to clients by showing calls and form fills attributed to the new site.

### referral-program (coreyhaines31/marketingskills)
**When to invoke:** When advising clients on growing their customer base, or
when planning Animo Automation's own agency referral strategy.
**What it covers:** Referral program design, incentive structures, referral
tracking — useful for client retention and agency word-of-mouth growth.

### free-tool-strategy (coreyhaines31/marketingskills)
**When to invoke:** When planning Animo Automation's own lead generation —
e.g. a free website grader, audit tool, or ROI calculator as a lead magnet.
**What it covers:** Free tool as marketing strategy — concept, build, distribution,
and conversion path from tool user to paying client.

### churn-prevention (coreyhaines31/marketingskills)
**When to invoke:** When a client shows signs of disengaging — use to plan
a save offer, check-in sequence, or value demonstration before they cancel.
**What it covers:** Churn detection signals, save offers, dunning flows,
win-back sequences — directly applicable to Animo Automation's MRR retention.

### revops (coreyhaines31/marketingskills)
**When to invoke:** When structuring Animo Automation's own CRM pipeline,
lead routing, or reporting setup in GHL.
**What it covers:** Revenue operations — lead lifecycle, scoring, routing,
pipeline management, CRM automation. Maps directly to GHL workflow design.

### signup-flow-cro (coreyhaines31/marketingskills)
**When to invoke:** When optimizing the client onboarding flow after they
sign up — reducing friction from "signed" to "live and activated."
**What it covers:** Signup and activation flow optimization — reducing drop-off,
improving first-value time, onboarding sequence design.

---

## Brave Search Skills — Installed in .agents/skills/

These skills give Claude Code access to Brave's search APIs for prospect research.
Complement firecrawl scraping with live search data.

### web-search (brave/brave-search-skills)
**When to invoke:** During prospect research — search for business information,
reviews, mentions, and competitive data not available via direct site scrape.
**What it covers:** General web search via Brave API — privacy-focused, no Google.

### news-search (brave/brave-search-skills)
**When to invoke:** When researching a prospect's industry for recent news —
useful for adding timely context to cold emails ("I saw [industry news]...").
**What it covers:** Recent news search — returns current articles and events.

### local-pois (brave/brave-search-skills)
**When to invoke:** When researching local competitors in a prospect's service area.
**What it covers:** Local Points of Interest — business listings, locations, ratings
for a geographic area. Useful for competitor mapping in GTA/DFW.

### local-descriptions (brave/brave-search-skills)
**When to invoke:** When building prospect profiles — get rich local business
descriptions to supplement Firecrawl data.
**What it covers:** Detailed local business descriptions from Brave's local index.

---

## Firecrawl Skills — Installed in .agents/skills/

These skills give Claude Code granular control over how prospect sites are scraped.
They complement `../website-audit-builder/execution/extract_business_data.py` and activate automatically.

### firecrawl (firecrawl/cli)
**When to invoke:** Automatically during any data extraction task.
**What it covers:** Core Firecrawl skill — general scraping best practices.

### firecrawl-scrape (firecrawl/cli)
**When to invoke:** Single page extraction — homepage, about, contact pages.
**What it covers:** Structured single-page scraping with content extraction.

### firecrawl-agent (firecrawl/cli)
**When to invoke:** When Claude Code needs to navigate and interact with a site
to extract data (e.g., JS-rendered content, paginated results).
**What it covers:** Agentic crawling — follows links, fills forms, extracts data.

### firecrawl-search (firecrawl/cli)
**When to invoke:** When searching for prospect information across the web
(reviews, citations, mentions, competitor data).
**What it covers:** Web search via Firecrawl — returns structured results.

### firecrawl-crawl (firecrawl/cli)
**When to invoke:** Full site crawl — use for deeper prospect research or
when building a comprehensive audit of a larger site.
**What it covers:** Multi-page crawl with sitemap discovery and link following.

### firecrawl-download (firecrawl/cli)
**When to invoke:** When downloading assets from a prospect's site — logos,
images, PDFs — for use in demo builds or audit reports.
**What it covers:** Asset downloading via Firecrawl — retrieves files from URLs.

### firecrawl-map (firecrawl/cli)
**When to invoke:** Before auditing or rebuilding a prospect's site — maps the
full site structure to understand page count, hierarchy, and URL patterns.
**What it covers:** Site map extraction — returns all URLs discovered on a domain.

### firecrawl-instruct (firecrawl/cli)
**When to invoke:** When you need specific data fields extracted from a prospect
site using natural language instructions (e.g., "extract all phone numbers and
service areas from this page").
**What it covers:** Instruction-based extraction — extracts structured data
from pages using plain English directives.

---

## Agent Productivity Skills — Installed in .agents/skills/

These improve how Claude Code handles complex multi-step tasks in this project.

### writing-plans (obra/superpowers)
**When to invoke:** Before writing any long-form output — cold email sequences,
audit reports, site copy briefs. Creates a structured plan before execution.

### executing-plans (obra/superpowers)
**When to invoke:** After writing-plans — converts the plan into executed output.
Use together: writing-plans → executing-plans → copy-editing.

### verification-before-completion (obra/superpowers)
**When to invoke:** Automatically — forces Claude Code to verify all outputs
meet requirements before declaring a task complete. Reduces errors on site builds
and audit reports.

### writing-skills (obra/superpowers)
**When to invoke:** Automatically on any writing task — improves overall quality
of copy, reports, and outreach materials.

### brainstorming (obra/superpowers)
**When to invoke:** When stuck on outreach angle, niche positioning, or audit
talking points. Use before writing cold emails for new niches.

### systematic-debugging (obra/superpowers)
**When to invoke:** Automatically — Claude Code uses this when Python scripts
throw errors. Speeds up diagnosis and fix cycles.

### subagent-driven-development + dispatching-parallel-agents (obra/superpowers)
**When to invoke:** Automatically on batch prospect audits. Allows Claude Code
to run multiple audit tasks in parallel — significantly faster for large batches.

### using-superpowers (obra/superpowers)
**When to invoke:** At the start of any new Claude Code session — orients
Claude Code on how to use the full superpowers skill suite effectively.
Run once per session when using multiple obra/superpowers skills together.

### finishing-a-development-branch (obra/superpowers)
**When to invoke:** After completing a site build or audit batch — ensures
all loose ends are tied up before declaring work done.
**What it covers:** Branch completion checklist — final review, cleanup,
commit hygiene, handoff readiness verification.

### receiving-code-review + requesting-code-review (obra/superpowers)
**When to invoke:** When reviewing built site code before delivery, or when
asking Claude Code to review its own output.
**What it covers:** Structured code review process — both giving and receiving
feedback on generated code, with specific criteria and response patterns.

### skill-creator (anthropics/skills)
**When to invoke:** When you want to create a custom skill for Animo Automation
workflows — e.g. a "GHL Voice AI deployment" skill or "prospect audit pipeline" skill.
**What it covers:** Step-by-step skill creation, testing, and iteration. Lets you
package any repeatable workflow into a reusable skill.

### internal-comms (anthropics/skills)
**When to invoke:** When writing internal documents — SOPs, team updates,
process docs, onboarding guides for Animo Automation.
**What it covers:** Internal communication writing — clear, structured docs
for internal use rather than client-facing copy.

### doc-coauthoring (anthropics/skills)
**When to invoke:** When collaborating on longer documents — proposal drafts,
system design docs, packaging/pricing guides.
**What it covers:** Structured document co-authoring — iterative drafting,
section ownership, revision tracking.

### proactive-agent (halthelobster/proactive-agent)
**When to invoke:** Automatically — makes Claude Code flag issues, gaps, and
opportunities without waiting to be asked. Particularly useful during audits
where the agent should surface insights unprompted.
**What it covers:** Proactive issue flagging, opportunity surfacing, and
initiative-taking behaviors in agentic workflows.

### planning-with-files (othmanadi/planning-with-files)
**When to invoke:** When managing a batch of prospect audits or coordinating
multi-step workflows across files. Structured planning using the filesystem.
**What it covers:** File-based planning workflows — task tracking, progress
management, and structured execution using markdown files as state.

---

## Key File Locations

### Skills (Claude Code reads these automatically)
- `docs/SKILL.md` — website audit skill (v12) — only modify with explicit user approval
- `docs/SKILL_website-sales-audit.md` — duplicate of SKILL.md for Claude Code context loading
- `docs/WEBSITE_GENERATION_SKILL.md` — autonomous site builder
- `docs/WEBSITE_CLAUDE.md` — copy into every new client project folder as CLAUDE.md (design rules)
- `docs/CLAUDE_CODE_SETUP.md` — one-time setup guide for claude-code mode (run before first use)

### Prompt System (3-layer architecture)
- `docs/master_prompts/universal_rules.txt` — Layer 1: rules for every site
- `docs/master_prompts/plumbing_bolt_prompt.txt` — Bolt/Lovable prompt (plumbing)
- `docs/master_prompts/plumbing_gemini_prompt.txt` — Gemini cinematic prompt (plumbing)
- `docs/master_prompts/plumbing_claude_code_prompt.txt` — Claude Code single-file prompt (plumbing)
- `docs/niches/plumbing.md` — Layer 3: plumbing niche rules
- `docs/niches/hvac.md` — Layer 3: HVAC niche rules
- `docs/niches/electrical.md` — Layer 3: electrical niche rules
- `docs/niches/cleaning.md` — Layer 3: cleaning niche rules
- `docs/niches/roofing.md` — Layer 3: roofing niche rules
- `docs/niches/generic.md` — fallback niche for unrecognized trades
- `docs/niches/_NICHE_TEMPLATE.md` — blank template for new niches

### Execution Scripts
- `execution/generate_website.py` — prompt package assembler (orchestrator)
- `execution/triage_handoff.py` — post-audit GHL triage handoff (auto + manual)

### Reference Docs
- `docs/GHL_SETUP_CHECKLIST_v3.md` — complete GHL client onboarding procedure
- `docs/SALES_SCRIPT_v2.md` — cold call script
- `docs/PACKAGING_PRICING_GUIDE_v2.md` — packages and pricing
- `docs/SYSTEM_DESIGN_v2.1.md` — full system design (peer-reviewed)
- `docs/AI_Website_Stack_v4.1.md` — validated tech stack decisions
- `EXECUTION_GUIDE.md` — complete step-by-step operating guide

### Outputs
- `output/` — audit reports saved here
- `output/structured_input.json` — latest extraction result
- `output/prompt_packages/` — generated prompt files

---

## Known Issue — Competitor Fetch Hang

If Claude Code hangs for 30+ minutes fetching competitor sites:
1. Press Escape
2. Type exactly:
   "stop fetching. write all four report outputs now based on what you gathered,
   skip competitor section, save to output/[businessname]-audit.md"
3. After the audit saves, still run the triage handoff:
   `python3 execution/triage_handoff.py --audit output/[businessname]-audit.md`

---

## Triage Handoff — All Three Modes

**Mode 1 — Automatic (default after every audit):**
```bash
python3 execution/triage_handoff.py --audit output/[businessname]-[date].md
```
Runs all four services. Scores from audit findings — no re-fetch needed.

**Mode 2 — Manual, specific service:**
```bash
python3 execution/triage_handoff.py --audit output/[file].md --service MCTB
```

**Mode 3 — Batch (catch up on existing audit files):**
```bash
python3 execution/triage_handoff.py --batch
python3 execution/triage_handoff.py --batch --force   # re-triage already-done files
python3 execution/triage_handoff.py --batch --dry-run # preview without running
```

Triage results always land in: `../ghl-triage/output/`
Handoff log (tracks what's been triaged): `output/triage_handoff_log.json`

---

## API Keys

All keys are in `.env` at project root. NEVER include keys in any document.
Required keys:
- FIRECRAWL_API_KEY
- SERPAPI_KEY
- NETLIFY_AUTH_TOKEN
- NETLIFY_SITE_ID (optional — auto-created on first deploy)

---

## First Prospect

mississaugaplumbingservices.com
- Audit score: 1/10 red
- 166 Google reviews (4.9 stars) — hidden on site
- JS-only build (not indexable)
- No tap-to-call, no lead capture
- Audit report: output/mississaugaplumbingservices-2026-03-08.md
- Demo site: https://mississauga-plumbing-l1i4.bolt.host

---

## Deploy Command (always use this exact flag)

```bash
netlify deploy --dir=dist --prod
```
`--dir=dist` is mandatory. Vite builds to dist/. Without it, Netlify deploys
source files and the site breaks.
-------------------------------------------------------------------------

## Environment & Operator Notes

Reference section for dev-environment and operator-workflow patterns
that span multiple fixes and sessions. Patterns worth remembering
between sessions live here.

### Development environment

- Windows 11 Home, PowerShell 5.x + git-bash via Claude Code.
- Git config: `core.autocrlf=true` globally; `.gitattributes
  * text=auto eol=lf` in each repo overrides it per-repo.
- Git pager disabled globally (`core.pager ""`).
- `python3` alias is broken on this box (Microsoft Store stub); use
  `python` or `py`.

**PowerShell file-handling gotchas.** PS 5.x has several traps for any
workflow that edits files. Use this as a pre-flight checklist when a
command is about to write or read bytes:

- `Set-Content -Encoding UTF8` and `Out-File -Encoding utf8` both
  silently write a BOM. Git renders the BOM as garbage in commit
  subjects and hook output. Fix: use
  `[System.IO.File]::WriteAllText("$PWD\<file>", $content,
  [System.Text.UTF8Encoding]::new($false))`.
- `[System.IO.File]::ReadAllText` and `WriteAllText` do NOT respect
  PowerShell's `cwd` — they use the .NET process working directory
  (`C:\Windows\System32` when PS launches normally). Always prepend
  `"$PWD\"` explicitly for both read and write.
- `Add-Content` writes `\r\n` line endings even when the target file's
  existing lines are `\n`. Produces mixed line endings silently. Use
  `[System.IO.File]::WriteAllText` with an explicit `\n` string
  (`` `n `` in a double-quoted PS string is LF) when appending to a
  file with known LF endings.
- `Get-Content` strips blank lines in its display output. Do not trust
  it for byte-accurate verification of commit-message or manifest
  structure. Use `python -c "print(repr(open('FILE','rb').read()))"`
  for byte-level inspection.
- `Get-Content` without `-Encoding UTF8` renders UTF-8 em-dashes as
  mojibake. Pass the flag explicitly for display, or use the Python
  repr pattern above.
- Multi-command pastes into the PS prompt can silently concatenate
  (e.g., `certutil -hashfile X SHA256certutil -hashfile X SHA256`).
  Paste single commands one line at a time; verify the prompt
  returned between each.

### Three-site cp1252 pattern

Modern Windows Python can crash on em-dashes and other non-cp1252
characters when stdout is piped or running under certain subprocess
contexts, even though interactive `sys.stdout.encoding` reports
`utf-8`. Fix is a byte-identical 8-line stdout/stderr reconfigure
block with a `hasattr` guard for Python <3.7 compatibility.

- **This repo's site:** `execution/triage_handoff.py` (Fix 11,
  `3e10e58`).
- **See also** the sibling sites in the other two repos: `ghl-triage`
  (`prospect_triage.py`) and `website-audit-builder`
  (`execution/extract_business_data.py`). Same patch, different
  consumer.

**Verification patterns for pre-patch repro on a fresh box:**
- PowerShell: `[Console]::OutputEncoding`
- Either shell: `python -c "import sys; print(sys.stdout.encoding)"`

Interactive stdout often reports `utf-8` on modern Windows Python
regardless of `chcp` or `PYTHONIOENCODING`. Pre-patch repro can be
hard to force on some operator boxes — fix still needed for fresh
machines, CI, and subprocess pipes.

### Commit body compose mechanism

Use this 8-step sequence for any commit body containing quotes,
em-dashes, Unicode, or other escape-fragile characters. Heredocs
(`<<'EOF'`) are deprecated for this purpose — they have a recurring
backslash-escape bug class that mechanisms, not guidelines, prevent.

1. Apply edits (Update / str_replace — these do NOT auto-stage).
2. Post-edit verification (AST, grep sweeps, `diff --stat`, parity hook).
3. Write commit body to temp file via Write tool.
4. Integrity checks on temp file: 8 content greps (section headers
   unique, zero backslashes, expected line count) + 4 on-disk byte
   checks (`head -1` for subject, first-byte hexdump for BOM, `file`
   for CRLF, `sha256` for paper trail) + 2 anchor-specific greps
   where applicable.
5. `cat` print the body for operator eyeball.
6. `git add <files>` — explicit; tool-based edits do not auto-stage.
7. `git commit -F <temp-file>`.
8. Post-commit verification (9 steps including grep-for-backslashes
   on committed body via `git log -1 --format=%B`).

**Case studies.** The file-based mechanism exists because two
heredoc-based commit attempts shipped with backslash-quote escape
sequences leaked into the committed body: orphan `34a36c1`
(pre-amend fix 17) and orphan `68fbff2` (pre-amend fix 17b), both
in `website-audit-builder`. Both were amended away; the orphans
will be garbage-collected. A written guideline to use single-quoted
heredocs with zero escapes existed after the first occurrence and
still failed on the second. Mechanisms beat guidelines under
execution pressure.

**Write-tool echo display bug.** The Write tool's echo of file
contents has cosmetic rendering issues (subject-line character wrap,
line-number skips). On-disk bytes are correct. The four on-disk byte
checks in step 4 above exist specifically to verify this — echo is
not a reliable preview.

**Temp file location.** Used
`/c/Users/canad/AppData/Local/Temp/<fix>_body.txt` with git-bash.
The `commit -F` pattern is cross-platform; the path literal isn't.

### Diagram-tree edits — annotation vs EDIT

When a filename reference sits inside an indented ASCII/Unicode
directory tree, repointing to an absolute or relative sibling path
produces structurally wrong diagrams (the sibling path visually
appears to live inside the local folder). Correct pattern is to
annotate the parent folder line instead. Example:

```
execution/  (extraction script lives in ../website-audit-builder — see README.md)
```

Locked as canonical after Fix 12's Edit 18 (`a02608f`, in this repo).
Applies to any doc that contains indented directory-tree diagrams.

### Fix 16 schema-drift guidance

Multi-repo backlog entries must anchor every file reference to a
specific repo+path. Do not carry file-name-only references across
handoff boundaries — session-context bleed will silently relocate
sites between repos. Fix 15's commit message referred to
`extract_business_data.py` as "the third cp1252 site in this repo"
(ghl-triage); the file actually lives in `website-audit-builder`.
Handoff docs carried the claim forward until Fix 16's P2 discovery
sweep caught it. Pattern: every file reference in a commit message,
handoff, or backlog entry gets `<repo>/<relative-path>` explicitly.

### Dict-keyed handoff log

This repo is the producer side of the cross-repo prospect handoff.
The canonical log is a URL-keyed dict written to disk by
`execution/triage_handoff.py`. For schema and rationale, read the
module itself — the shape is defined there and kept in sync with
consumer code in `ghl-triage`. Pattern worth flagging: dict-keyed
(not list-keyed) so same-URL re-handoffs overwrite in place rather
than duplicate.

Consumer side is `ghl-triage` via `--from-audit`. See
`ghl-triage/CLAUDE.md` § "Environment & Operator Notes" for the
consumer-side reference.

### Synthetic-fixture-vs-real-producer coverage

A passing test suite against synthetic fixtures does not prove the
consumer handles real producer output. Fix 14 canonicalized this as
a general lesson: synthetic fixtures test the code path the author
imagined; real producer output exercises the code path real data
takes. The five pre-Fix-14 synthetic fixtures all used inline-list
YAML form (what a human hand-writes); the real producer emits
block-list form (what PyYAML defaults to). A single real-producer
fixture added during Fix 7 or Fix 8 would have caught the parser
gap that Fix 14 fixed. When producing output consumed by
`ghl-triage`, actively generate the canonical PyYAML shape rather
than the human-readable one — consumer tolerance covers correctness,
but matching the canonical shape avoids silent-mismatch surprises.

