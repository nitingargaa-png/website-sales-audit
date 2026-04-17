# CLAUDE.md — Website Project Rules
# Copy this file into every new client website folder.
# Claude Code reads this before every action in this project.
# Last updated: March 2026

---

## PROJECT CONTEXT

This is a local home service business website built for a digital agency.
Goal: high-converting lead generation site with GHL automation placeholders.
The site will be handed off to GHL once client signs.

---

## OUTPUT FORMAT

- Single file: index.html
- ALL CSS inline in <style> tag
- ALL JS inline in <script> tag before </body>
- No React, no Vite, no npm, no build step required
- Mobile-first: design at 390px, scale up to desktop

---

## MANDATORY FIRST STEPS (before writing any code)

1. Confirm CLAUDE.md exists in this project folder (this file IS the design skill).
   If it does not exist: stop and tell the user to copy WEBSITE_CLAUDE.md here as CLAUDE.md.

2. Create screenshots/ folder for the Puppeteer screenshot loop:
   mkdir screenshots

---

## COLOR RULES (non-negotiable)

Navy #1a3a6b  = trust elements (header bg, section headings, footer)
Red  #e84040  = emergency/CTA elements ONLY (phone buttons, 24/7 badges)
Text #1a1a1a  = body copy
Bg   #f7f9fc  = alternating section backgrounds
White #ffffff = cards, inputs

NEVER use purple. Purple = generic AI output. If you see it, remove it.

---

## PHONE NUMBER RULE

Every single phone number on the page must use:
  href="tel:+1XXXXXXXXXX"

No exceptions. Plain text phone numbers with no tel: link = failure.

---

## GHL PLACEHOLDER RULE

All 6 GHL divs must be present before any deploy:

  id="ghl-voice-inline"    between Hero and Trust Bar
  id="ghl-calendar"        Booking section
  id="ghl-reviews"         below review cards
  id="ghl-contact-form"    Contact section
  id="ghl-payment-link"    Footer Pay Invoice button
  id="ghl-chat-widget"     last element before </body>

Each must have:
  - A dashed border: border:2px dashed #cccccc
  - Visible placeholder text describing what loads there
  - An HTML comment: <!-- GHL: paste [widget type] snippet here -->

---

## SCREENSHOT LOOP RULE

After writing Hero, Services, and Reviews sections:
  - Take a Puppeteer screenshot at 390px width
  - Check for: purple colors, overflow, phone button visibility, spacing
  - Fix issues before continuing
  - Save screenshots to screenshots/ folder

---

## SECTION ORDER (do not reorder)

1.  Sticky header
2.  Hero
3.  GHL voice widget placeholder
4.  Trust bar
5.  Services grid
6.  Why Choose Us
7.  How It Works (4 steps)
8.  Reviews
9.  GHL reviews placeholder
10. Service Areas + Google Maps iFrame
11. Booking (id="booking")
12. Contact form (id="contact")
13. Footer + GHL chat widget

---

## CODE QUALITY RULES

- html { scroll-behavior: smooth; }
- Copyright year: document.getElementById('year').textContent = new Date().getFullYear();
  Never hardcode the year.
- Sticky header gets box-shadow on scroll via JS scroll event listener
- IntersectionObserver: fade-in each section as user scrolls into view
- No Lorem Ipsum in final output
- No external image URLs (blocked at runtime in demo environments)
- No blank space below footer
- No builder badge scripts in <head>

---

## DEPLOY CHECKLIST (run before sharing any URL)

  [ ] All 6 GHL placeholder IDs present
  [ ] All phone numbers use tel: href
  [ ] No purple colors anywhere
  [ ] Sticky header scrolls correctly
  [ ] Site looks correct at 390px (mobile)
  [ ] No blank space below footer
  [ ] Year shows dynamically (not hardcoded)
  [ ] No builder badge in page source

---

## DEPLOY COMMANDS

Demo (prospect):    Drag index.html to netlify.com/drop → live URL
Production client:  git push to GitHub → connect Vercel → auto-deploy
