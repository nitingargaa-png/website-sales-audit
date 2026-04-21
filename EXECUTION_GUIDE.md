# Complete Execution Guide
## AI-Powered Local Business Website Agency
## From zero to first client — step by step
### Last updated: March 2026

---

## PART 1: ONE-TIME SETUP (do this once, takes ~60 minutes)

---

### STEP 1 — Confirm your project folder structure

Your Claude Code project lives at:
```
C:\Users\canad\projects\website-sales-audit\
```

After copying all the new files, your folder should look exactly like this:

```
website-sales-audit\
│
├── docs\
│   ├── SKILL.md                          ← website audit skill (v9) ✅
│   ├── SKILL_website-sales-audit.md      ← duplicate for Claude Code context ✅
│   ├── SALES_SCRIPT_v2.md                ← cold call script ✅
│   ├── PACKAGING_PRICING_GUIDE_v2.md     ← pricing guide ✅
│   ├── SYSTEM_DESIGN_v2.1.md             ← full system design ✅
│   ├── AI_Website_Stack_v4.1.md          ← validated tech stack ✅
│   ├── WEBSITE_GENERATION_SKILL.md       ← autonomous Claude Code builder ✅
│   ├── WEBSITE_CLAUDE.md                 ← copy into each client folder as CLAUDE.md ✅
│   ├── CLAUDE_CODE_SETUP.md              ← one-time setup guide for claude-code mode ✅
│   ├── GHL_SETUP_CHECKLIST_v3.md         ← GHL client onboarding procedure ✅
│   │
│   ├── master_prompts\
│   │   ├── universal_rules.txt            ← Layer 1 (every site) ✅
│   │   ├── plumbing_bolt_prompt.txt       ← Bolt/Lovable prompt (plumbing) ✅
│   │   ├── plumbing_gemini_prompt.txt     ← Gemini prompt (plumbing) ✅
│   │   └── plumbing_claude_code_prompt.txt ← Claude Code prompt (plumbing) ✅
│   │
│   └── niches\
│       ├── _NICHE_TEMPLATE.md             ← blank template for new niches ✅
│       ├── generic.md                     ← fallback for unrecognized trades ✅
│       ├── plumbing.md                    ← plumbing niche rules ✅
│       ├── hvac.md                        ← HVAC niche rules ✅
│       ├── electrical.md                  ← electrical niche rules ✅
│       ├── cleaning.md                    ← cleaning niche rules ✅
│       └── roofing.md                     ← roofing niche rules ✅
│
├── execution\  (extraction script lives in ../website-audit-builder — see README.md)
│   ├── generate_website.py                ← prompt package assembler ✅
│   ├── lead_pipeline.py                   ← lead generation pipeline ✅
│   ├── email_verifier.py                  ← email verification ✅
│   ├── utils.py                           ← shared utilities ✅
│   └── claude_extractor.py               ← Claude-based extraction ✅
│
├── input\
│   └── urls.txt                           ← prospect URLs for batch auditing ✅
│
├── output\
│   ├── prompt_packages\                   ← generated prompt files saved here ✅
│   └── mississaugaplumbingservices-2026-03-08.md  ← first audit report ✅
│
├── .env                                   ← API keys — DO NOT share or commit ✅
├── .gitignore                             ← .env must be listed here ✅
├── requirements.txt                       ← Python dependencies ✅
└── CLAUDE.md                              ← Claude Code project config ✅
```

**⚠️ Before running anything:** Run `docs\CLAUDE_CODE_SETUP.md` Steps 1–3 once
to install Puppeteer and Netlify CLI. Takes 5 minutes. Only needed once.

---

### STEP 2 — Verify your .env file

Open `C:\Users\canad\projects\website-sales-audit\.env` and confirm it has:

```
FIRECRAWL_API_KEY=your_firecrawl_key_here
SERPAPI_KEY=your_serpapi_key_here
NETLIFY_AUTH_TOKEN=your_netlify_token_here
NETLIFY_SITE_ID=                          ← leave blank for now (auto-created on first deploy)
```

**NETLIFY_AUTH_TOKEN:** Get this from netlify.com → User Settings → Applications →
Personal access tokens → New access token. Paste it in .env.

**If any key was ever pasted into a document or shared externally:** rotate it now at
the provider dashboard before continuing.

Confirm `.env` is in your `.gitignore`:
```
# .gitignore should contain:
.env
output/prompt_packages/
node_modules/
```

---

### STEP 3 — Install Python dependencies

Open a terminal in your project folder and run:

```bash
cd C:\Users\canad\projects\website-sales-audit

pip install requests python-dotenv
```

Test that the extraction script can find your keys:

```bash
python3 ../website-audit-builder/execution/extract_business_data.py --help
```

You should see the usage instructions, no errors.

---

### STEP 4 — Install Netlify CLI

```bash
npm install -g netlify-cli

# Authenticate (opens browser)
netlify login

# Confirm it worked
netlify status
```

---

### STEP 5 — Verify your CLAUDE.md project config

Open `C:\Users\canad\projects\website-sales-audit\CLAUDE.md`

It should tell Claude Code what this project is. If it doesn't exist or is sparse,
replace it with:

```markdown
# Website Sales Audit — Agency Project

## Project Purpose
AI-powered local home service business website agency.
Sells websites + GHL automation systems to plumbers, HVAC, cleaners, etc.

## Key Commands
- Audit a site: "audit https://[url] and prepare full call prep"
- Generate prompt package: python3 execution/generate_website.py --url https://[url] --mode bolt
- Run extraction only: python3 ../website-audit-builder/execution/extract_business_data.py --url https://[url]

## Key Files
- docs/SKILL.md — website audit skill (v9)
- docs/WEBSITE_GENERATION_SKILL.md — autonomous site builder skill
- docs/master_prompts/universal_rules.txt — Layer 1 rules (every site)
- docs/niches/plumbing.md — plumbing niche rules
- docs/GHL_SETUP_CHECKLIST_v3.md — client onboarding procedure
- ../website-audit-builder/execution/extract_business_data.py — Firecrawl + SerpApi data extraction
- execution/generate_website.py — prompt package assembler

## Skill Trigger
When user says "audit [URL]" — execute docs/SKILL.md
When user says "execute WEBSITE_GENERATION_SKILL" — execute docs/WEBSITE_GENERATION_SKILL.md

## Known Issue
If competitor site fetch hangs 30+ minutes: press Escape, then say:
"stop fetching. write all four report outputs now based on what you gathered,
skip competitor section, save to output/[filename].md"
```

---

### STEP 6 — Create the output/prompt_packages folder

```bash
mkdir C:\Users\canad\projects\website-sales-audit\output\prompt_packages
```

---

## PART 2: THE REPEATABLE WORKFLOW (use this for every prospect)

There are two modes:

- **DEMO MODE** — before client signs. Goal: get a live URL to send in cold outreach.
- **PRODUCTION MODE** — after client signs. Goal: deliver the real site.

---

## DEMO MODE — Finding and closing a prospect

### Phase A: Find a prospect

Use Google Maps or your lead pipeline:
```bash
python3 execution/lead_pipeline.py --search "plumbers in Toronto ON" --limit 5 --dry-run
```

Or just search Google Maps manually for your trade + city.

Target businesses with:
- Bad or missing website
- Good Google reviews (proof the business is real)
- Active GBP listing

---

### Phase B: Run the audit (in Claude Code)

1. Open VS Code
2. Open your project: `C:\Users\canad\projects\website-sales-audit\`
3. Open Claude Code (sidebar or Ctrl+Shift+P → Claude Code)
4. Type exactly:

```
audit https://[prospect-url] and prepare full call prep
```

Example:
```
audit https://mississaugaplumbingservices.com and prepare full call prep
```

**What Claude Code does:**
- Fetches the site
- Runs all 10 audit checks
- Generates 4 outputs: Short report, Medium report, Content Gap Summary, Talking Points
- Saves the report to `output/[businessname]-[date].md`

**If it hangs fetching competitors (30+ min):**
Press Escape, then type:
```
stop fetching. write all four report outputs now based on what you gathered,
skip competitor section, save to output/mississaugaplumbingservices-audit.md
```

---

### Phase C: Generate the demo site prompt

Open a regular terminal (not Claude Code) in your project folder:

**Option A — one command (extraction + generation together):**
```bash
python3 execution/generate_website.py \
  --url https://mississaugaplumbingservices.com \
  --mode bolt
```

**Option B — two commands (if you want to verify extracted data first):**
```bash
# Step 1: Extract business data
python3 ../website-audit-builder/execution/extract_business_data.py \
  --url https://mississaugaplumbingservices.com \
  --business "Mississauga Plumbing Services" \
  --city "Mississauga ON"

# Step 2: Review output/structured_input.json, fix anything wrong, then:
python3 execution/generate_website.py \
  --input output/structured_input.json \
  --mode bolt
```

Option B is recommended for your first few prospects — it lets you verify
the extracted data before building the prompt.

**What this does:**
1. Runs Firecrawl to scrape the site
2. Runs SerpApi to pull their GBP (rating, reviews, phone, address)
3. Detects niche (plumbing)
4. Loads `docs/master_prompts/universal_rules.txt` (Layer 1)
5. Loads `docs/master_prompts/plumbing_bolt_prompt.txt` (pre-built Layer 3)
6. Fills all 13 variables ([BUSINESS_NAME], [PHONE], [REVIEW_COUNT], etc.)
7. Saves the complete ready-to-paste prompt to:
   `output/prompt_packages/mississauga_plumbing_services_bolt_prompt_[date].txt`

**Output in terminal:**
```
✅ Saved → output/prompt_packages/mississauga_plumbing_services_bolt_prompt_20260314.txt

Next:
  1. Open the prompt file above
  2. Attach logo + photos in Bolt.new chatbox
  3. Paste and build
  4. DEPLOY: netlify deploy --dir=dist --prod
```

---

### Phase D: Manually verify the extracted data

Before building — open `output/structured_input.json` and verify:

```json
{
  "BUSINESS_NAME": "Mississauga Plumbing Services",   ← correct?
  "PHONE": "(647) 550-4003",                          ← correct? call it to verify
  "CITY_PROVINCE": "Mississauga, ON",                 ← correct?
  "SERVICES_LIST": "Emergency Plumbing, Drain...",    ← looks right?
  "SERVICE_AREAS": "Mississauga, Brampton...",        ← specific neighborhoods?
  "REVIEWS_3": "Review 1: \"Great service...\""       ← real reviews from GBP?
  "REVIEW_COUNT": "166",                              ← number from GBP?
  "RATING_STRING": "4.9★ (166 Google Reviews)"       ← looks right?
}
```

**Fix anything wrong directly in the JSON file**, then re-run generate_website.py
with `--input output/structured_input.json` instead of `--url`:

```bash
python3 execution/generate_website.py \
  --input output/structured_input.json \
  --mode bolt
```

**Before pasting into Bolt — do a final bracket check on the output prompt file:**
```bash
grep -o "\[.*\]" output/prompt_packages/[filename].txt
```
Any `[REMAINING_BRACKET]` in the output means a variable wasn't filled.
Fix it in structured_input.json and re-run — do not paste an unfilled prompt into Bolt.

---

### Phase E: Build the demo site in Bolt.new

1. Open https://bolt.new (free, no account needed)
2. **Before pasting the prompt** — attach files in the chatbox:
   - Logo (download from the URL in structured_input.json → LOGO_URL)
   - 2-3 job photos (download from PHOTO_URLS)
3. Open the generated prompt file from `output/prompt_packages/`
4. **Copy the entire contents** and paste into Bolt's chatbox
5. Send — Bolt builds the site (~2-5 minutes)
6. Review the output in Bolt's preview panel

**Common fixes to request in Bolt chat:**
- "Make the phone number in the header a clickable red button"
- "Move emergency services to the first two cards in the services grid"
- "The trust bar needs more whitespace between items"

---

### Phase F: Deploy the demo to Netlify

**Option 1 — Netlify CLI (recommended, faster):**
```bash
# Inside the Bolt project directory (after downloading)
cd path/to/bolt-project
npm run build
netlify deploy --dir=dist --prod
```
⚠️ `--dir=dist` is mandatory. Vite builds to `dist/`. Without this flag,
Netlify deploys source files and the site breaks.

**Option 2 — Netlify Drop (no CLI needed, easiest for first demo):**
1. In Bolt, click Download (gets you a ZIP file)
2. Extract the ZIP
3. Run `npm run build` in the extracted folder
4. Go to netlify.com/drop
5. Drag the `dist/` folder into the browser
6. Get your live URL instantly (e.g., `demo-mississauga-plumbing.netlify.app`)

**Fix index.html before deploying** (do this in the extracted folder):
- Remove: `<script async src="...bolt.new/badge.js...">`
- Replace: `<link rel="icon" href="/vite.svg">` with a proper favicon

---

### Phase G: Cold outreach

Now you have a live URL. Use SALES_SCRIPT_v2.md for the call.

**The only goal of the first contact: get them to view the demo link.**
Do not pitch pricing. Do not pitch features. One goal: "Can I send you a link?"

**Cold call opener** (from SALES_SCRIPT_v2.md):
```
"Hi, is this [Owner Name]? My name is [Your Name] — I'm a web consultant.
I noticed your Google listing has [X] five-star reviews but I couldn't find
them anywhere on your website. I actually built a quick preview showing what
your site could look like with those reviews front and centre — do you have
30 seconds for me to send you the link?"
```

**Follow-up DM/email if no answer:**
```
Subject: Built something for [Business Name]

Hi [Name],

I work with [trade] businesses in [city] and noticed your [X] Google reviews
aren't showing on your website — you're leaving trust on the table.

I built a free preview using your actual business info:
[YOUR NETLIFY URL]

Takes 30 seconds to look at. Happy to walk you through it if you're interested.

— [Your Name]
[Your phone]
```

---

## PRODUCTION MODE — After client signs

> **Architecture decision — read before building anything:**
>
> This system has two prompt modes. They produce fundamentally different outputs
> and are NOT interchangeable:
>
> | Mode | Output | Use for |
> |---|---|---|
> | `--mode claude-code` | Single `index.html`, no build step | **Demo only** — fast, drag-and-drop to Netlify Drop |
> | `--mode skill-output` | Full React + Tailwind project via `WEBSITE_GENERATION_SKILL.md` | **Production only** — client delivery |
>
> **Rule: Never deliver `--mode claude-code` output as a production site.**
> The single-file HTML output is demo-grade — no component architecture, no build
> optimisation, limited maintainability. It exists solely to generate a shareable
> URL quickly for cold outreach.
>
> **Rule: Always use `--mode skill-output` for client delivery.**
> This triggers `WEBSITE_GENERATION_SKILL.md`, which scaffolds a proper React/Vite
> project, runs a build, and deploys via `netlify deploy --dir=dist --prod`.

### Step 1: Collect setup fee

Don't start production work until you have the deposit.
Recommended: 50% of setup fee upfront, 50% on go-live.

---

### Step 2: Run production extraction + package

```bash
python3 execution/generate_website.py \
  --url https://[client-url] \
  --mode skill-output
```

This creates: `output/prompt_packages/[client]_claude_code_package_[date].json`

---

### Step 3: Build the production site in Claude Code

1. Open VS Code with your project
2. Open Claude Code
3. Type:

```
execute WEBSITE_GENERATION_SKILL.md using output/prompt_packages/[client]_claude_code_package_[date].json
```

**What Claude Code does autonomously:**
1. Reads the JSON package
2. Checks Node.js version and Netlify CLI auth
3. Scaffolds a new React + Tailwind project with `npm create vite@latest`
4. Builds all components (Header, Hero, TrustBar, Services, Process, Reviews,
   ServiceAreas, Booking, Contact, Footer)
5. Places all 6 GHL placeholder divs
6. Runs `npm run build` (verifies no errors)
7. Deploys: `netlify deploy --dir=dist --prod`
8. Returns a live Netlify URL

**If it gets stuck:** Check the terminal for errors. Most common:
- Missing `netlify-cli` → run `npm install -g netlify-cli`
- Auth error → run `netlify login`
- Build error → Claude Code will attempt to fix it automatically

---

### Step 4: Run the QA checklist

Before sharing the URL with the client, open `docs/GHL_SETUP_CHECKLIST_v3.md`
and run every item in **Section 11 — QA Acceptance Checklist**.

Key items to check on a real iPhone (not DevTools):
- Tap-to-call opens the phone dialer
- Sticky header stays visible while scrolling
- All 6 GHL placeholder divs visible (dashed borders)
- No placeholder text remains ([BUSINESS_NAME], Lorem Ipsum)
- Footer copyright shows current year

---

### Step 5: Set up GHL (follow checklist in order)

Open `docs/GHL_SETUP_CHECKLIST_v3.md` and work through sections 1–10 in order.

**Critical dependencies:**
- Section 8 (CRM Pipeline) BEFORE Section 4 (Lead Follow-Up Workflow)
- Section 1.5 (A2P SMS Registration) BEFORE activating ANY SMS workflow
- Voice AI Labs must be enabled BEFORE the inline widget works

**For Voice AI widget specifically:**

The inline voice widget and floating chat widget have different setup steps:

```
FLOATING CHAT WIDGET:
  GHL script → before </body> in index.html ✅ standard

INLINE VOICE WIDGET (ghl-voice-inline):
  ⚠️ Do NOT place before <div id="root"> — div doesn't exist yet.

  Option A (recommended):
  In index.html, place OUTSIDE the React root as static HTML:
    <div id="ghl-voice-inline"></div>
    <script>/* GHL inline widget JS here */</script>
    <div id="root"></div>

  Option B:
  In the React component that renders the placeholder:
    useEffect(() => {
      const s = document.createElement('script');
      s.innerHTML = `/* GHL widget init */`;
      document.getElementById('ghl-voice-inline').appendChild(s);
    }, []);
```

After adding the snippet, redeploy:
```bash
netlify deploy --dir=dist --prod
```

---

### Step 6: Point client's domain to Netlify

Follow **Section 12 — Domain Cutover SOP** in GHL_SETUP_CHECKLIST_v3.md.

Summary:
1. In Netlify: Site Settings → Domain Management → Add Custom Domain
2. In client's registrar (GoDaddy, Namecheap, etc.): update A record or CNAME
3. Wait 24–48 hours for DNS propagation
4. Netlify auto-provisions SSL once DNS resolves
5. Test everything again on the custom domain

---

### Step 7: Build GHL Master Snapshot (after first client is fully live)

This is the highest-leverage step that saves 3+ hours on every future client.

In GHL Agency Dashboard → Snapshots → Create New Snapshot:
- Name: "Home Services — Base v1 — March 2026"
- Include: Workflows ✅, Pipelines ✅, Calendars ✅, Chat Widgets ✅, Custom Fields ✅, Tags ✅
- Exclude: Contacts ❌, Conversations ❌

Every new client from this point: Create Sub-Account → Apply Snapshot → update
business-specific fields → activate.

---

## PART 3: REFERENCE — What document does what

| Document | When you use it |
|---|---|
| `SKILL.md` | Claude Code reads this automatically when you say "audit [URL]" |
| `WEBSITE_GENERATION_SKILL.md` | Claude Code reads this when you say "execute WEBSITE_GENERATION_SKILL.md using [package]" |
| `universal_rules.txt` | `generate_website.py` reads this automatically — you never touch it directly |
| `plumbing_bolt_prompt.txt` | `generate_website.py` uses this automatically for plumbing prospects |
| `plumbing.md` | `generate_website.py` reads this automatically for niche rules |
| `_NICHE_TEMPLATE.md` | You fill this in when adding a new niche (HVAC, cleaning, etc.) |
| `GHL_SETUP_CHECKLIST_v3.md` | You work through this manually for every new client |
| `SALES_SCRIPT_v2.md` | You read this before every cold call |
| `PACKAGING_PRICING_GUIDE_v2.md` | You reference this when a prospect asks about pricing |
| `SYSTEM_DESIGN_v2.1.md` | Reference doc — share with LLMs for peer review |
| `AI_Website_Stack_v4.1.md` | Reference doc — share with LLMs for peer review |

---

## PART 4: ADDING A NEW NICHE

When you're ready to target HVAC, cleaning, pest control, etc.:

**Website prompt — add a new niche overlay:**
1. Copy `docs/niches/_NICHE_TEMPLATE.md`
2. Rename to `docs/niches/hvac.md` (or whichever trade)
3. Fill in every field (takes 15–30 minutes)
4. Copy `docs/master_prompts/plumbing_bolt_prompt.txt`
5. Rename to `docs/master_prompts/hvac_bolt_prompt.txt`
6. Adapt the prompt for HVAC-specific sections
7. Test: `python3 execution/generate_website.py --url https://[hvac-site] --mode bolt`

The system picks up the new niche automatically — no code changes needed.

**Voice AI agent — already covered for all 22 niches:**
The v1.5 Universal Voice AI Prompt Template covers 22 home service niches natively.
To deploy a new niche (e.g., HVAC):
1. Open the v1.5 template in GHL Agent Studio
2. Replace [AGENT_NAME] with the client's agent name
3. Keep ONLY the HVAC niche restriction line (Section 1.1) — delete 21 others
4. Keep ONLY the HVAC emergency trigger block (Section 6.3) — delete 21 others
5. Keep ONLY the HVAC qualification questions (Section 8.1) — delete 21 others
6. Delete two of three booking mode lines (Section 5.2) — leave only the applicable one
7. Update all Custom Values for this client (see GHL_SETUP_CHECKLIST Section 2.5)
8. Run the go-live test matrix

No separate niche prompt files needed for Voice AI. The v1.5 template is universal.

---

## PART 5: DAILY OPERATING RHYTHM

### Finding prospects (30 min/day)
```bash
python3 execution/lead_pipeline.py --search "plumbers in Mississauga ON" --limit 10
```
Or search Google Maps manually. Target: 3-5 audits per week.

### Running audits (10 min each, in Claude Code)
```
audit https://[url] and prepare full call prep
```

### Generating demo prompts (5 min each, in terminal)
```bash
python3 execution/generate_website.py --url https://[url] --mode bolt
```

### Building demos (15-30 min each, in Bolt.new)
Paste prompt → attach logo + photos → review → fix → deploy to Netlify.

### Cold outreach (30 min/day)
Use the live Netlify URL. One goal: get them to view the demo.

### Client onboarding (2-4 hours, after signing)
Follow GHL_SETUP_CHECKLIST_v3.md Sections 1-10 in order.

---

## PART 6: COSTS AT EACH STAGE

### Pre-revenue (right now)
| Tool | Cost |
|---|---|
| Bolt.new (demos) | $0 free tier |
| Netlify (hosting) | $0 free tier |
| SerpApi | $0 free tier (<5 extractions/day) |
| Firecrawl | $0–$50/month (check current status at app.firecrawl.dev → Billing — promo with Lovable expired ~Jan 2026) |
| **Total** | **$0** |

### First client signed
| Tool | Cost |
|---|---|
| GHL Starter ($97/mo — covers 3 sub-accounts) | $97 |
| Lovable Pro (production sites) | $25 |
| **Total** | **$122/month** |

### At 5+ clients
| Tool | Cost |
|---|---|
| GHL Unlimited | $297 |
| Lovable Pro | $25 |
| Netlify Pro (critical at 5+ sites) | $19 |
| SerpApi Basic (if >5 extractions/day) | $50–75 |
| **Total** | **~$391-416/month** |

**⚠️ Netlify free tier suspension risk at 5+ clients:**
100GB bandwidth + 300 build minutes per month apply **account-wide**.
If any single site triggers the limit, **ALL client sites are paused until the
next billing cycle** — not just the offending site. This is harsher than most
users expect. Upgrade to Netlify Pro ($19/month) at 5 clients — not when it breaks.

**Netlify scaling path — plan now, execute on schedule:**

| Milestone | Action | Reason |
|---|---|---|
| Client 1–4 | Single Netlify account, free tier | Sufficient for demos + early clients |
| Client 5 | Upgrade to Netlify Pro ($19/month) | Prevents account-wide pause |
| Client 5+ | Move to per-client Netlify accounts | One noisy client cannot take down others |
| Client 50+ | Migrate to Cloudflare Pages | Free: unlimited sites + bandwidth; React/Vite compatible |

**Per-client Netlify accounts (implement at client 5):**
Use one Netlify account per client (their business email or your agency email +alias).
Bandwidth overage on one site does not affect any other client.
Cost: $0 per account on free tier; $19/month per account only if that specific client needs Pro.

**GCP billing alert — Google Places API:**
Set a billing alert at $50/month in your Google Cloud Console (Billing → Budgets & Alerts).
Current cost: ~$0.10–$0.15/prospect (Basic + Contact SKUs combined). At 50 prospects/week
(~200/month), you are at ~$20–30/month — well within the $200/month GCP free credit.
The alert is a safeguard against unexpected SKU tier changes or batch script runaway.

---

## PART 7: QUICK COMMAND REFERENCE

```bash
# Audit a prospect (run in Claude Code, not terminal)
"audit https://[url] and prepare full call prep"

# Extract business data only
python3 ../website-audit-builder/execution/extract_business_data.py --url https://[url] --business "Name" --city "City ST"

# Generate Bolt.new demo prompt
python3 execution/generate_website.py --url https://[url] --mode bolt

# Generate Lovable prompt (same as bolt, different label)
python3 execution/generate_website.py --url https://[url] --mode lovable

# Generate Gemini/AI Studio prompt
python3 execution/generate_website.py --url https://[url] --mode gemini

# Generate Claude Code skill package (production)
python3 execution/generate_website.py --url https://[url] --mode skill-output

# Use existing structured_input.json (skip re-extraction)
python3 execution/generate_website.py --input output/structured_input.json --mode bolt

# Override niche detection
python3 execution/generate_website.py --url https://[url] --mode bolt --niche hvac

# Deploy to Netlify (run inside the built project folder)
netlify deploy --dir=dist --prod

# Execute production build (run in Claude Code)
"execute WEBSITE_GENERATION_SKILL.md using output/prompt_packages/[file].json"
```

---

## PART 8: FIRST WEEK CHECKLIST

- [ ] Copy all new files to correct locations (Part 1, Step 1)
- [ ] Verify .env has all 3 keys (Firecrawl, SerpApi, Netlify)
- [ ] Run `pip install requests python-dotenv`
- [ ] Run `npm install -g netlify-cli` and `netlify login`
- [ ] Verify CLAUDE.md project config
- [ ] Create `output/prompt_packages/` folder
- [ ] Test extraction: `python3 ../website-audit-builder/execution/extract_business_data.py --url https://mississaugaplumbingservices.com --business "Mississauga Plumbing Services" --city "Mississauga ON"`
- [ ] Confirm structured_input.json was created in output/
- [ ] Test prompt generation: `python3 execution/generate_website.py --input output/structured_input.json --mode bolt`
- [ ] Confirm prompt file appears in output/prompt_packages/
- [ ] Review the prompt file — confirm variables filled correctly
- [ ] Paste prompt into Bolt.new and build the demo site
- [ ] Deploy to Netlify (bolt.host or netlify.com/drop)
- [ ] Send cold outreach to mississaugaplumbingservices.com with the live URL
- [ ] Verify GHL Starter account sub-account limit in your GHL dashboard
- [ ] Verify Firecrawl billing status at app.firecrawl.dev → Billing (promo with Lovable expired ~Jan 2026)

---

## PART 8: DATA HANDLING & PRIVACY (M4)

You collect prospect PII (phone numbers, addresses, review texts, email addresses)
via automated scraping before any business relationship exists. Handle it carefully.

**Prospect data lifecycle:**

| Stage | What you have | Retention rule |
|---|---|---|
| Extracted (not contacted) | structured_input.json, audit report | Delete after 60 days if not contacted |
| Demo sent (no response) | Above + demo URL | Delete demo + data after 30 days of no response |
| Active prospect (follow-up) | Above + outreach log | Keep until 14 days after final touch |
| Signed client | All of the above | Archive encrypted; retain for contract term + 1 year |
| Lost / declined | All | Delete within 14 days of final "no" |

**Demo site rules (C1 from peer review):**
- Every demo URL must have `<meta name="robots" content="noindex,nofollow">` in `<head>`
- Every demo must show the "Demo Preview — Not Live" banner until signed
- Share demo URLs only with the specific prospect — do not post publicly
- Delete Netlify demo sites within 30 days if prospect does not convert
  Netlify: Site Settings → Danger Zone → Delete Site

**File hygiene:**
```bash
# Check for unfilled prompt packages older than 30 days
find output/prompt_packages/ -name "*.txt" -mtime +30 -type f

# Check for structured_input.json files (should never be more than 1 at a time)
ls -la output/*.json

# Archive a converted client's data
mkdir -p clients/[business-slug]/
mv output/structured_input.json clients/[business-slug]/
mv output/[audit-report].md clients/[business-slug]/
# Then encrypt the clients/ folder or store in a password-protected location
```

**Canadian law (PIPEDA):** You are collecting business contact data, which is
generally considered business information rather than personal information under
PIPEDA — however, sole proprietors' data is personal information. Maintain
a light-touch approach: collect only what you need, use it only for the stated
purpose (building their website), and delete it when the relationship ends.

---

## PROSPECTS TRACKER (input/prospects.csv)

Track every prospect in `input/prospects.csv`. This file is gitignored.
Update it after every outreach action.

**Status values:** `prospect` → `demo_sent` → `call_booked` → `negotiating` → `signed` / `lost`

**Quick update commands:**
```bash
# View current pipeline
cat input/prospects.csv | column -t -s ','

# Add a new prospect manually
echo "https://url.com,Business Name,plumbing,2026-03-15,,,,,false,prospect,,,," >> input/prospects.csv
```

extract_business_data.py appends a new row automatically on each extraction.
If the URL already exists in the CSV, it updates the audit_date only — no duplicates.

---

*This guide covers the complete system. For detailed GHL setup instructions,
refer to GHL_SETUP_CHECKLIST_v3.md. For pricing conversations, refer to
PACKAGING_PRICING_GUIDE_v2.md. For cold call scripts, refer to SALES_SCRIPT_v2.md.*

---

## CLIENT OFFBOARDING SOP

Use this when a client cancels their retainer. Work through it in order.

### Step 1 — Receive and acknowledge cancellation (Day 1)
- Cancellation requires 30 days written notice (per PACKAGING_PRICING_GUIDE)
- Reply within 24 hours confirming receipt and final billing date
- Issue final invoice if any balance outstanding

### Step 2 — Export client data from GHL (before access is removed)
- **Contacts:** GHL sub-account → Contacts → Export (CSV). Save to `clients/[slug]/contacts-export-YYYY-MM-DD.csv`
- **Opportunities:** GHL → Pipelines → export or screenshot each stage
- **Call logs:** GHL → Reporting → Calls → filter by date range → screenshot or export
- **Conversation history:** GHL → Conversations → export if available; otherwise screenshot key threads
- **Workflows:** Screenshot each published workflow's trigger + action sequence for your records
- **KB content:** Copy all Knowledge Base text to a `.md` file in `clients/[slug]/kb-backup.md`
- Save all exports to `clients/[slug]/` — encrypt folder or store in password-protected location

### Step 3 — Netlify site handoff or deletion
- **If client wants to keep the site:** Transfer Netlify site to a new account under their email.
  Netlify: Team Settings → Transfer Site Ownership. DNS stays pointed; no downtime.
- **If client does not want the site:** Delete the Netlify site.
  Netlify: Site Settings → Danger Zone → Delete Site.
  Confirm DNS records are updated if custom domain was in use.

### Step 4 — GHL sub-account wind-down
- Unpublish all active workflows in the sub-account
- Remove the client's GHL phone number (release it — do not let it sit idle and accrue charges)
- Remove the client user login from the sub-account
- Archive or delete the sub-account (GHL: Agency → Sub-Accounts → Archive)
  Note: Archived sub-accounts still count toward your plan limit on Starter.
  Delete entirely if you need the slot.

### Step 5 — Domain and DNS
- If you managed the client's domain DNS: notify the client to update nameservers
  to point to their new host, or transfer domain registrar account to them
- Remove any Netlify custom domain entries

### Step 6 — Internal records
- Update `input/prospects.csv`: change status to `churned`, add churn date and reason
- Move client folder from `clients/[slug]/` to `clients/archive/[slug]/`
- Note reason for churn — use this to identify patterns after 3+ churns

### Step 7 — Final communication
Send a professional close-out email:
> "Thanks for working with us. Your data has been exported and is available on request
> for 60 days. After that, it will be securely deleted per our data retention policy.
> If you ever want to restart, reach out — we'll still have your audit and setup notes."

**Data retention after offboarding:** Delete exported contact/opportunity data after 60 days
unless the client requests a copy. Archive the site audit report and KB backup indefinitely
(these contain no personal data — just business configuration).
