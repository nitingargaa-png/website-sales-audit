# WEBSITE_GENERATION_SKILL.md
# Claude Code Autonomous Website Builder
# Version: 2.0 — March 2026
#
# HOW TO INVOKE:
#   In Claude Code: "execute WEBSITE_GENERATION_SKILL.md using output/prompt_packages/[file].json"
#
# Claude Code will: read the package → scaffold React project → pull 21st.dev components → build → deploy
# Total human effort: one command.

---

## YOUR ROLE

You are an autonomous website builder. You receive a Claude Code skill package (JSON file)
and build a complete, production-ready React + Tailwind website for a local home service business.

You do NOT ask clarifying questions. You execute fully and return a live Netlify URL.

---

## PHASE 1 — READ THE PACKAGE

Read the JSON package file provided. Extract:
- `business_data` → the 6 prompt variables
- `assembled_prompt` → the pre-assembled three-layer prompt
- `niche` → trade type
- `_meta.netlify_deploy_command` → must be `netlify deploy --dir=dist --prod`

If the package file is not found or malformed:
> ⚠️ Package file not found or invalid JSON. Check the path and try again.

---

## PHASE 2 — ENVIRONMENT CHECK

Before building, verify prerequisites:

```bash
# Check Node.js
node --version
# Must be 18+. If not: instruct user to install Node 18+ before continuing.

# Check Netlify CLI
netlify --version
# If missing: npm install -g netlify-cli

# Check Netlify auth
netlify status
# If not logged in: netlify login (opens browser)
# OR verify NETLIFY_AUTH_TOKEN is set in .env

# Check .env for required keys
cat .env | grep NETLIFY
# Must have NETLIFY_AUTH_TOKEN
# NETLIFY_SITE_ID is optional — omit to create new site automatically

# Check frontend-design skill (CLAUDE.md in project root IS the skill — no npm needed)
ls docs/WEBSITE_CLAUDE.md && echo "design rules ok" || echo "WEBSITE_CLAUDE.md missing from docs/"

# Check Puppeteer
node -e "require('puppeteer')" 2>/dev/null && echo "puppeteer ok" || echo "missing"
# If missing: npm install -g puppeteer
```

If any prerequisite fails, stop and report exactly what needs to be fixed.
Do NOT proceed without a working Netlify CLI authentication and frontend-design skill.

---

## PHASE 3 — SCAFFOLD REACT PROJECT

```bash
# Create project with Vite
npm create vite@latest [business-name-kebab] -- --template react
cd [business-name-kebab]
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

Configure `tailwind.config.js`:
```js
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: { extend: {} },
  plugins: [],
}
```

Add to `src/index.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

---

## PHASE 3B — SELECT 21ST.DEV COMPONENTS (quality gate before building)

Before writing any section code, select designer-built components from 21st.dev
to replace generic AI-generated equivalents. This is what separates premium
agency output from generic vibe-coded sites.

Go to https://21st.dev and select ONE component per category below.
Copy the prompt from each → paste into the build prompt for that section.

**Required selections (choose one per row):**

| Section | 21st.dev category | What to search | Why |
|---|---|---|---|
| Hero background | Backgrounds | "dot grid" or "background paths" | Removes flat color hero |
| Service cards | Cards | "glassmorphism" or "feature card" | Removes generic white boxes |
| CTA buttons | Buttons | "shimmer" or "gradient button" | Removes default Tailwind button |
| Trust bar / Stats | Stats | "stats counter" or "animated stats" | Adds motion to static numbers |

**How to use each component:**
1. Go to 21st.dev → search the category
2. Click the component you want
3. Click "Copy Prompt" → select "Claude Code" as the target
4. The copied text is a component specification
5. Paste it into the assembled_prompt alongside the section instructions
6. Claude Code will implement the designer component instead of generating generic code

**If 21st.dev is unavailable:** proceed with standard implementation but note
in the output summary that manual component upgrade is recommended.

**Niche-specific component recommendations:**

| Niche | Hero bg | Cards | Special |
|---|---|---|---|
| Plumbing | Dark dot grid (navy) | bordered cards with hover lift | Emergency banner with pulse animation |
| HVAC | Gradient mesh (navy→blue) | icon-forward feature cards | Seasonal toggle (heating/cooling) |
| Electrical | Dark grid with amber glow | stat cards with counters | Safety badge component |
| Cleaning | Light dot grid (green tint) | clean minimal cards | Before/after toggle card |
| Roofing | Warm gradient (navy→dark) | testimonial cards with photos | Financing badge component |

---

## PHASE 4 — BUILD THE SITE

Using the `assembled_prompt` from the package plus the 21st.dev component
specifications selected in Phase 3B, build the complete site:

**Files to create:**
- `src/App.jsx` — main component with all sections
- `src/components/Header.jsx` — sticky header with tap-to-call
- `src/components/Hero.jsx` — hero section with 21st.dev background
- `src/components/TrustBar.jsx` — trust bar with animated stats
- `src/components/Services.jsx` — services card grid with 21st.dev cards
- `src/components/Process.jsx` — 4-step process
- `src/components/Reviews.jsx` — testimonial cards
- `src/components/ServiceAreas.jsx` — neighborhoods + Google Maps iFrame
- `src/components/Booking.jsx` — GHL calendar placeholder
- `src/components/Contact.jsx` — GHL form placeholder
- `src/components/Footer.jsx` — 4-column footer
- `public/favicon.svg` — trade-appropriate SVG favicon (wrench, flame, bolt, etc.)

**MANDATORY — All 6 GHL placeholder divs must be present:**

```html
<!-- 1. Voice AI inline — between hero and trust bar (in JSX as placeholder) -->
<div id="ghl-voice-inline" style="...dashed border placeholder...">
  🎙️ Voice AI Widget — activates after GHL setup
</div>
<!-- GHL SETUP — DUAL PLACEMENT (read carefully):
  Floating chat widget: place JS before </body> in index.html — standard.
  Inline voice widget: DO NOT place JS before <div id="root">.
  The ghl-voice-inline div lives inside React — it doesn't exist until React mounts.
  Script before root will fail silently (widget reverts to floating mode).

  OPTION B (recommended): Keep ghl-voice-inline in JSX, use useEffect to inject script.
  This keeps the widget inside the React component tree — correct position in section flow.
    useEffect(() => {
      const s = document.createElement('script');
      s.innerHTML = `/* GHL widget init */`;
      document.getElementById('ghl-voice-inline').appendChild(s);
    }, []);

  OPTION A (fallback only — use if Option B causes hydration issues):
  Move ghl-voice-inline OUT of React JSX entirely, into index.html as static HTML OUTSIDE
  <div id="root">. Warning: this places the widget outside the React section flow,
  which can break scroll positioning and layout on some page structures.
    <div id="ghl-voice-inline"></div>
    <script>/* GHL inline widget JS */</script>
    <div id="root"></div>

  Steps:
  1. Enable Voice AI in sub-account Labs first
  2. Sites → Chat Widget → New → select Voice AI type
  3. Style tab → Widget Placement → Embedded/Inline
  4. Copy JS snippet → apply using Option A or B above -->

<!-- 2. Booking calendar -->
<div id="ghl-calendar" ...>Booking Calendar loads here (GHL embed)</div>

<!-- 3. Contact form -->
<div id="ghl-contact-form" ...>Contact Form loads here (GHL embed)</div>

<!-- 4. Live reviews -->
<div id="ghl-reviews" ...>Live Google Reviews load here (GHL embed)</div>

<!-- 5. Pay invoice — in footer -->
<a href="#" id="ghl-payment-link" ...>Pay Invoice</a>

<!-- 6. Chat widget — last element before </body> (floating — standard placement) -->
<div id="ghl-chat-widget"></div>
<!-- GHL: paste floating chat/voice widget JS snippet here before </body> -->
```

**index.html requirements:**
```html
<!-- Update all of these before deploying: -->
<title>[BUSINESS_NAME] | [Trade] in [City]</title>
<meta name="description" content="[BUSINESS_NAME] — [trade] in [CITY_PROVINCE]. [RATING_STRING]. Call [PHONE].">
<meta property="og:title" content="[BUSINESS_NAME] | [City] [Trade]">
<meta property="og:description" content="[RATING_STRING]. Serving [SERVICE_AREAS].">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<!-- REMOVE any Bolt/Lovable/Vite builder badge scripts -->
<!-- REMOVE: <script async src="...bolt.new/badge.js..."> -->
```

**Critical code rules:**
- Every phone number: `<a href="tel:+1[PHONE_DIGITS]">[PHONE]</a>` — no exceptions
- Copyright: `© {new Date().getFullYear()} [BUSINESS_NAME]` — never hardcode year
- No video backgrounds
- No Lorem Ipsum in final output
- No purple colors — if Tailwind default is generating purple, override explicitly
- Mobile-first: 390px viewport as design baseline

---

## PHASE 5 — BUILD AND VERIFY

```bash
# Run the build
npm run build

# Verify dist/ was created
ls dist/
# Must show: index.html, assets/ folder
# If dist/ is empty or missing: check for build errors and fix before deploying
```

**Visual quality check before deploying:**
Open the built site in browser. Take a screenshot at 390px. Verify:
- No purple colors anywhere (Tailwind contamination)
- Hero background is NOT flat color — has texture or gradient from 21st.dev component
- Service cards have hover effect and visual depth
- Phone button visible immediately without scrolling on mobile
- All 6 GHL placeholder divs show with dashed borders

**If build fails:**
1. Read the error output carefully
2. Fix the specific error (usually an import or JSX syntax issue)
3. Run `npm run build` again
4. Do NOT proceed to deploy until build succeeds cleanly

---

## PHASE 6 — DEPLOY

**Choose path based on situation:**

| Situation | Deploy command |
|---|---|
| Demo for prospect (quick) | `netlify deploy --dir=dist --prod` |
| Production client, ongoing updates | Push to GitHub → connect Vercel → auto-deploy |

**Path A — Netlify (demos and quick deploys):**
```bash
# ⚠️ --dir=dist is the correct flag for standard Vite builds (default outDir)
# If vite.config.js overrides build.outDir, deploy THAT folder instead
# Generated vite.config.js should always explicitly set: build: { outDir: 'dist' }

netlify deploy --dir=dist --prod
```

**Path B — GitHub + Vercel (production clients):**
```bash
git init
git add .
git commit -m "Initial build: [BUSINESS_NAME]"
git remote add origin [GITHUB_REPO_URL]
git push -u origin main
# Then: connect repo to Vercel → deploy → every future git push auto-deploys
```

**If NETLIFY_SITE_ID is not set:** Netlify CLI creates a new site automatically
and returns a live URL like `https://[random-name].netlify.app`. Save this URL.

**If deploy fails with auth error:**
```bash
netlify login
netlify deploy --dir=dist --prod
```

**After successful deploy:**
- Copy the live URL from the CLI output
- Open the URL in a browser and verify the site loads correctly
- Test tap-to-call on a mobile device (critical)

---

## PHASE 7 — POST-DEPLOY VERIFICATION

Run these checks immediately after deploy:

```
✅ Site loads at the Netlify/Vercel URL
✅ Mobile viewport correct at 390px (test in DevTools or real iPhone)
✅ Sticky header visible and scrolls correctly
✅ Every phone number tappable (href="tel:..." on real mobile)
✅ Hero CTA button works
✅ Hero background has texture/gradient — NOT flat color
✅ No purple colors anywhere on the page
✅ Service cards have hover effect (lift + shadow)
✅ All 6 GHL placeholder divs present and visible (dashed borders show)
✅ Google Maps iFrame loads (may need manual coordinate update)
✅ Footer copyright shows current year (not hardcoded)
✅ No Vite default favicon (no orange lightning bolt)
✅ No builder badge scripts in page source
✅ OG title and description set correctly
✅ HTTPS active (Netlify/Vercel provides automatically)
```

Report any failures with specific steps to fix.

---

## PHASE 8 — OUTPUT SUMMARY

Output this block when complete:

```
=====================================
WEBSITE BUILD COMPLETE
=====================================
Business:    [BUSINESS_NAME]
Niche:       [niche]
Live URL:    [netlify/vercel URL]
Built:       [timestamp]
21st.dev components used: [list which components were pulled]

NEXT STEPS:
1. Send this URL in cold outreach email/DM
2. Test tap-to-call on a real iPhone Safari
3. When client signs → GHL setup:
   a. Create sub-account
   b. Enable Voice AI in Labs
   c. Replace GHL placeholder divs with real snippets
   d. Activate: missed call text-back, review requests
   e. Complete GHL_SETUP_CHECKLIST_v3.md in order

GHL VOICE AI WIDGET (inline div between hero + trust bar):
  Sub-account → Sites → Chat Widget → New → Voice AI type
  Style tab → Widget Placement → Embedded/Inline
  Copy JS snippet → replace ghl-voice-inline div comment

DOMAIN CUTOVER (when client is ready):
  See docs/DOMAIN_CUTOVER_SOP.md for full DNS process.
=====================================
```

---

## KNOWN ISSUES & FIXES

| Issue | Fix |
|---|---|
| `netlify deploy` deploys source files | Always use `--dir=dist` flag |
| Build fails on JSX syntax | Check for missing closing tags or unclosed expressions |
| Google Maps iFrame shows wrong city | Update coordinates in iFrame src attribute manually |
| GHL widget blocked by CSP | Not an issue on standard Netlify — only if custom CSP headers added |
| React hydration race with GHL inline widget | Do NOT place inline widget script before `<div id="root">`. Use Option A (static HTML outside root) or Option B (useEffect) |
| Competitor site fetch hangs 30+ min | Press Escape → "stop fetching, write all outputs based on what you have" |
| Vite favicon still showing | Replace `/public/vite.svg` with custom `/public/favicon.svg` |
| Purple colors appearing | Tailwind default — override with niche color palette in tailwind.config.js theme.extend.colors |
| 21st.dev unavailable | Proceed with standard implementation, note in output summary that component upgrade is recommended |
| Generic-looking hero | Pull "background paths" or "dot grid" from 21st.dev — flat color hero is the #1 quality signal of AI-generated sites |
