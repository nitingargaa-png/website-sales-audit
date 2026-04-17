# CLAUDE_CODE_SETUP.md
# One-time setup for Claude Code website building workflow
# Run these commands ONCE — they apply globally to all future projects
# Last updated: March 2026

---

## WHAT THIS SETS UP

1. Frontend Design Skill — stops generic AI/purple output automatically
2. Puppeteer — enables screenshot loop for self-correction
3. Netlify CLI — for demo deploys (drag-drop is fine too)

---

## STEP 1 — Copy WEBSITE_CLAUDE.md into every new client project (most important)

For every new client website folder, copy WEBSITE_CLAUDE.md into it as CLAUDE.md:

    copy docs\WEBSITE_CLAUDE.md C:\Users\canad\projects\[client-name-website]\CLAUDE.md

This IS the design skill. Claude Code reads CLAUDE.md before every action and enforces:
color rules (no purple), phone number format, GHL placeholder divs, section order,
screenshot loop, and deploy checklist automatically. No npm install needed.

Verify the copy worked:

    type C:\Users\canad\projects\[client-name-website]\CLAUDE.md

You should see the color rules and section order. If you do, you're set.

---

## STEP 2 — Install Puppeteer

Open terminal (VS Code terminal or Command Prompt):

    npm install -g puppeteer

What it does: Allows Claude Code to take screenshots of the site it's building
at 390px (iPhone width) and self-correct visual issues before asking you to review.

---

## STEP 3 — Install Netlify CLI (optional — for CLI deploys)

    npm install -g netlify-cli
    netlify login

What it does: Lets you deploy from terminal with one command.
Alternative: Just drag index.html to netlify.com/drop — no CLI needed for demos.

---

## STEP 4 — Per-Client Project Setup (do this for every new client)

When starting a new client website in Claude Code:

1. Create new folder:
   mkdir C:\Users\canad\projects\[client-name-website]

2. Copy WEBSITE_CLAUDE.md into it as CLAUDE.md:
   copy docs\WEBSITE_CLAUDE.md C:\Users\canad\projects\[client-name-website]\CLAUDE.md

3. Open that folder in VS Code:
   File → Open Folder → select [client-name-website]

4. Generate the prompt:
   python3 execution/generate_website.py --url https://[prospect-url] --mode claude-code

5. Open the prompt file from output/prompt_packages/
   Copy the contents → paste into Claude Code panel → hit Enter

6. Claude Code will:
   - Read CLAUDE.md ✅ (enforces design rules automatically)
   - Build index.html
   - Run screenshot loop at 390px
   - Self-correct any issues
   - Report when complete

7. Deploy demo:
   Drag index.html to netlify.com/drop → live URL in 30 seconds

---

## HOW THE SCREENSHOT LOOP WORKS

Claude Code creates this file automatically (screenshot_check.js):

    const puppeteer = require('puppeteer');
    (async () => {
      const browser = await puppeteer.launch();
      const page = await browser.newPage();
      await page.setViewport({ width: 390, height: 844 }); // iPhone 14
      await page.goto('file://' + require('path').resolve('index.html'));
      await page.screenshot({
        path: 'screenshots/check-' + Date.now() + '.png',
        fullPage: true
      });
      await browser.close();
      console.log('Screenshot saved to screenshots/');
    })();

Claude Code runs this after writing Hero, Services, and Reviews sections.
It checks the screenshot for:
  - Purple colors (Tailwind contamination)
  - Horizontal overflow at 390px
  - Phone button visibility without scrolling
  - Card spacing and readability

It fixes issues before continuing. You see the corrections happen in real time.

---

## FULL WORKFLOW AFTER SETUP

For every new prospect:

    # Step 1 — Generate the prompt (30 seconds)
    cd C:\Users\canad\projects\website-sales-audit
    python3 execution/generate_website.py --url https://prospect-site.com --mode claude-code

    # Step 2 — Set up client folder (1 minute)
    mkdir C:\Users\canad\projects\prospect-name-website
    copy docs\WEBSITE_CLAUDE.md C:\Users\canad\projects\prospect-name-website\CLAUDE.md

    # Step 3 — Open in VS Code + Claude Code
    Open folder in VS Code
    Paste prompt from output/prompt_packages/ into Claude Code panel

    # Step 4 — Wait for build (5-10 minutes)
    Claude Code builds, screenshots, self-corrects, completes

    # Step 5 — Deploy demo (30 seconds)
    Drag index.html to netlify.com/drop

    # Step 6 — Send outreach
    Send Netlify URL to prospect

Total time per prospect after setup: ~15 minutes
