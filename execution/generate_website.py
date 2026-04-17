#!/usr/bin/env python3
from __future__ import annotations
"""
generate_website.py
Orchestrator: reads structured_input.json → assembles three-layer prompt → saves prompt package.

ARCHITECTURE — IMPORTANT:
This script does NOT invoke Claude Code directly. Python cannot subprocess Claude Code.

Correct workflow:
  DEMO — Claude Code (before client signs):
    1. python3 execution/extract_business_data.py --url https://... → output/structured_input.json
    2. python3 execution/generate_website.py --input output/structured_input.json --mode claude-code
    3. Open output/prompt_packages/[business]_claude-code_prompt.txt
    4. Open VS Code → new empty folder → copy WEBSITE_CLAUDE.md into it as CLAUDE.md
    5. Open Claude Code panel → paste prompt → hit Enter
    6. Claude Code writes index.html + runs screenshot loop
    7. DEPLOY DEMO: drag index.html to netlify.com/drop → live URL
    8. Send URL in cold outreach

  DEMO — Bolt (alternative, no VS Code needed):
    1. python3 execution/extract_business_data.py --url https://...
    2. python3 execution/generate_website.py --input output/structured_input.json --mode bolt
    3. Open output/prompt_packages/[business]_bolt_prompt.txt
    4. Paste into Bolt.new chatbox → attach logo + photos → build
    5. Deploy: bolt.host or netlify deploy --dir=dist --prod

  PRODUCTION (after client signs):
    1. python3 execution/extract_business_data.py --url https://...
    2. python3 execution/generate_website.py --input output/structured_input.json --mode skill-output
    3. Open Claude Code in VS Code
    4. Run: "execute WEBSITE_GENERATION_SKILL.md using [package].json"
    5. Claude Code builds → npm run build → netlify deploy --dir=dist --prod

  SHORTCUT (extraction + generation in one command):
    python3 execution/generate_website.py --url https://example.com --mode claude-code
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# ── Project paths ─────────────────────────────────────────────────────────────
PROJECT_ROOT   = Path(__file__).parent.parent
DOCS_DIR       = PROJECT_ROOT / "docs"
NICHES_DIR     = DOCS_DIR / "niches"
MASTER_DIR     = DOCS_DIR / "master_prompts"
UNIVERSAL_FILE = MASTER_DIR / "universal_rules.txt"
OUTPUT_DIR     = PROJECT_ROOT / "output"
PACKAGES_DIR   = OUTPUT_DIR / "prompt_packages"
EXTRACT_SCRIPT = PROJECT_ROOT / "execution" / "extract_business_data.py"

MODES = {
    "bolt":         "Bolt.new — paste into chatbox (React + Tailwind)",
    "lovable":      "Lovable — paste into chat (same React + Tailwind stack)",
    "gemini":       "Google AI Studio — Gemini 3.1 Pro Preview cinematic prompt",
    "claude-code":  "Claude Code in VS Code — single index.html, no build step",
    "skill-output": "Claude Code skill package — open Claude Code to execute autonomously",
}


def run_extraction(url: str, niche_override: str = "") -> Path:
    print(f"\n🔍 Running extraction for: {url}")
    output_path = OUTPUT_DIR / "structured_input.json"
    cmd = [sys.executable, str(EXTRACT_SCRIPT), "--url", url, "--output", str(output_path)]
    if niche_override:
        cmd += ["--niche", niche_override]
    subprocess.run(cmd, check=True)
    if not output_path.exists():
        print(f"❌ structured_input.json not created at {output_path}")
        sys.exit(1)
    return output_path


def load_structured_input(input_path: Path) -> dict:
    if not input_path.exists():
        print(f"❌ File not found: {input_path}")
        print("   Run: python3 execution/extract_business_data.py --url https://...")
        sys.exit(1)
    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)
    _validate_extraction(data)
    return data


def _validate_extraction(data: dict) -> None:
    errors   = []
    warnings = []

    name  = data.get("BUSINESS_NAME", "").strip()
    phone = data.get("PHONE", "").strip()
    city  = data.get("CITY_PROVINCE", "").strip()

    if not name:
        errors.append("BUSINESS_NAME is empty — cannot build a website without a business name")
    if not city:
        errors.append("CITY_PROVINCE is empty — city/province is required for SEO and map embed")

    if not phone:
        errors.append("PHONE is empty — phone appears in 4 locations; must be correct before building")
    else:
        digits = "".join(c for c in phone if c.isdigit())
        if len(digits) < 10:
            errors.append(
                f"PHONE '{phone}' has only {len(digits)} digits — "
                "must be a full 10-digit number (e.g. (647) 550-4003)"
            )
        elif len(digits) > 11:
            errors.append(
                f"PHONE '{phone}' has {len(digits)} digits — looks like a supplier or fax number was scraped. "
                "Verify this is the correct customer-facing number."
            )
        if digits and digits == digits[0] * len(digits):
            errors.append(f"PHONE '{phone}' is all the same digit — clearly wrong")

    services = data.get("SERVICES_LIST", "").strip()
    if not services:
        warnings.append(
            "SERVICES_LIST is empty — niche default services will be used. "
            "Verify these match what the business actually offers."
        )

    review_count = str(data.get("REVIEW_COUNT", "")).strip()
    reviews_3    = data.get("REVIEWS_3", "").strip()
    if not reviews_3 or "No reviews" in reviews_3:
        warnings.append(
            "REVIEWS_3 is empty — review cards will be blank. "
            "Pull 3 reviews manually from the Google Business Profile."
        )
    if review_count and review_count.isdigit() and int(review_count) > 0 and not reviews_3:
        warnings.append(
            f"GBP shows {review_count} reviews but none were extracted — "
            "SerpApi pull may have failed. Check API quota."
        )

    if warnings:
        print("\n⚠️  EXTRACTION WARNINGS (build will proceed — fix before sending demo):")
        for w in warnings:
            print(f"   • {w}")

    if errors:
        print("\n❌ EXTRACTION ERRORS — cannot build prompt with this data:\n")
        for e in errors:
            print(f"   • {e}")
        print(
            "\n   Fix these in output/structured_input.json, then re-run.\n"
            "   Or re-extract: python3 execution/extract_business_data.py --url https://..."
        )
        sys.exit(1)


def phone_digits(phone: str) -> str:
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) == 10:
        digits = "1" + digits
    return digits


def load_file(path: Path, label: str) -> str:
    if not path.exists():
        print(f"⚠️  {label} not found at {path}")
        return f"# [{label} missing]\n"
    return path.read_text(encoding="utf-8")


def load_prebuilt_prompt(niche: str, mode: str) -> str | None:
    suffix_map = {
        "bolt":        "bolt",
        "lovable":     "bolt",
        "gemini":      "gemini",
        "claude-code": "claude_code",
    }
    suffix = suffix_map.get(mode, "bolt")
    path = MASTER_DIR / f"{niche}_{suffix}_prompt.txt"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None


def parse_niche_variables(niche: str) -> dict:
    niche_path = NICHES_DIR / f"{niche}.md"
    if not niche_path.exists():
        return {}

    content = niche_path.read_text(encoding="utf-8")
    if "## PROMPT_VARIABLES" not in content:
        return {}

    section = content.split("## PROMPT_VARIABLES")[1]
    if "\n## " in section:
        section = section.split("\n## ")[0]

    variables = {}
    for line in section.strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ": " in line:
            key, value = line.split(": ", 1)
            variables[f"[{key.strip()}]"] = value.strip()

    if variables:
        print(f"  ✅ Loaded {len(variables)} niche variables from niches/{niche}.md")
    else:
        print(f"  ⚠️  PROMPT_VARIABLES section in niches/{niche}.md has no parseable entries")
    return variables


def build_places_context(data: dict) -> str:
    """
    Formats Google Places pitch signals into a section for injection into prompts.
    Returns empty string if Places enrichment was skipped or found no signals.
    """
    meta    = data.get("_meta", {})
    signals = meta.get("pitch_signals", [])
    if not meta.get("places_enriched") or not signals:
        return ""

    rating = data.get("RATING_STRING", "")
    lines  = "\n".join(f"  → {s}" for s in signals)

    return f"""
---
GOOGLE REPUTATION SIGNALS (reference these in outreach and pitch):
Rating: {rating}
Pitch angles detected:
{lines}
---"""


def fill_variables(template: str, data: dict, niche: str = "") -> str:
    phone = data.get("PHONE", "")
    city_province = data.get("CITY_PROVINCE", "")
    city_only = city_province.split(",")[0].strip() if city_province else ""

    # Build Google Reviews URL from place_id
    place_id = data.get("_meta", {}).get("place_id", "") or data.get("place_id", "")
    if place_id:
        google_reviews_url = f"https://search.google.com/local/reviews?placeid={place_id}"
    else:
        biz  = data.get("BUSINESS_NAME", "").replace(" ", "+")
        city = data.get("CITY_PROVINCE", "").replace(" ", "+")
        google_reviews_url = f"https://www.google.com/search?q={biz}+{city}+reviews"

    replacements = {
        "[BUSINESS_NAME]":      data.get("BUSINESS_NAME", ""),
        "[PHONE]":              phone,
        "[PHONE_DIGITS]":       phone_digits(phone),
        "[CITY_PROVINCE]":      city_province,
        "[CITY]":               city_only,
        "[SERVICES_LIST]":      data.get("SERVICES_LIST", ""),
        "[SERVICE_AREAS]":      data.get("SERVICE_AREAS", ""),
        "[REVIEWS_3]":          data.get("REVIEWS_3", "(No reviews — add manually from GBP)"),
        "[REVIEW_COUNT]":       str(data.get("REVIEW_COUNT", "")),
        "[YEARS_IN_BUSINESS]":  data.get("YEARS_IN_BUSINESS", "10+"),
        "[RATING_STRING]":      data.get("RATING_STRING", ""),
        "[LOGO_URL]":           data.get("LOGO_URL", ""),
        "[NICHE]":              data.get("_meta", {}).get("niche", niche),
        "[USE_JS_YEAR]":        "",
        "[PLACES_CONTEXT]":     build_places_context(data),
        "[GOOGLE_REVIEWS_URL]": google_reviews_url,
    }

    if niche:
        replacements.update(parse_niche_variables(niche))

    result = template
    for _ in range(2):
        for k, v in replacements.items():
            result = result.replace(k, str(v) if v else "")
    return result


def _bolt_routing_note(data: dict) -> str:
    """
    Returns a Bolt/React-specific routing instruction block.
    Injected when PAGE_MODE is multi to force React Router v6 implementation.
    Without this, Bolt defaults to single-page anchor-scroll regardless of instructions.
    """
    nav_pages  = data.get("NAV_PAGES", [])
    page_count = len(nav_pages) if nav_pages else 0

    if page_count < 2:
        return ""  # single-page — no routing needed

    proposed_list = ", ".join(nav_pages[:6]) if nav_pages else "Home, Services, About, Contact"

    return f"""

================================================================================
CRITICAL ROUTING REQUIREMENT — READ BEFORE WRITING ANY CODE
================================================================================

PAGE_MODE: multi — This site has {page_count} pages: {proposed_list}

You MUST implement this as a TRUE multi-page React application using React Router v6.

REQUIRED IMPLEMENTATION:
  1. Install react-router-dom: it must be in package.json dependencies
  2. Wrap App in <BrowserRouter> (or use createBrowserRouter)
  3. Create a separate React component file for EACH page:
       src/pages/Home.tsx
       src/pages/Services.tsx
       src/pages/About.tsx
       src/pages/Contact.tsx
       (one file per page in PROPOSED list)
  4. Define <Routes> in App.tsx:
       <Route path="/" element={{<Home />}} />
       <Route path="/services" element={{<Services />}} />
       <Route path="/about" element={{<About />}} />
       <Route path="/contact" element={{<Contact />}} />
       (one Route per page)
  5. Use <Link to="/services"> in the nav — NEVER use <a href="#services">
  6. Each page component renders its OWN full layout with its own hero,
     content sections, and CTA — not just a scroll anchor on a long page

FORBIDDEN:
  ❌ Do NOT build a single long scrollable page
  ❌ Do NOT use anchor hash links (#services) for page navigation
  ❌ Do NOT put all content in one App.tsx component
  ❌ Do NOT use useRef() or scrollIntoView() for "page" switching

DEPLOY REMINDER:
  netlify deploy --dir=dist --prod  ← --dir=dist is MANDATORY for Vite builds
================================================================================
"""


def assemble_bolt_prompt(data: dict, niche: str) -> str:
    prebuilt = load_prebuilt_prompt(niche, "bolt")
    if prebuilt:
        print(f"  ✅ Using pre-built {niche}_bolt_prompt.txt")
        prompt = fill_variables(prebuilt, data, niche=niche)
        prompt += _bolt_routing_note(data)
        return _inject_structure_block(prompt, data)

    print(f"  ⚠️  No pre-built prompt for '{niche}' — assembling from layers")
    universal = load_file(UNIVERSAL_FILE, "universal_rules.txt")
    niche_content = load_file(NICHES_DIR / f"{niche}.md", f"niches/{niche}.md")
    phone = data.get("PHONE", "")
    tel = phone_digits(phone)

    raw_prompt = f"""================================================================================
{niche.upper()} — BOLT.NEW / LOVABLE PROMPT
Business: {data.get('BUSINESS_NAME', '')}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
================================================================================

Build a complete, mobile-first, high-converting {niche} business website for:

Business: {data.get('BUSINESS_NAME', '')}
Phone: {phone}  —  ALL instances must use href="tel:+{tel}"
City/Province: {data.get('CITY_PROVINCE', '')}
Services: {data.get('SERVICES_LIST', '')}
Service Areas: {data.get('SERVICE_AREAS', '')}
Years in business: {data.get('YEARS_IN_BUSINESS', '')}
Google rating: {data.get('RATING_STRING', '')}

Reviews (display verbatim in 3 quote cards):
{data.get('REVIEWS_3', '(No reviews extracted — paste 3 from GBP manually)')}

{build_places_context(data)}

Attach logo + job photos in chatbox before sending this prompt.

---

LAYER 1 — UNIVERSAL RULES (apply to every site):
{universal}

---

LAYER 3 — NICHE RULES ({niche}):
{niche_content}

---

DEPLOY COMMAND (run after build):
  netlify deploy --dir=dist --prod
  ⚠️  --dir=dist is MANDATORY — React/Vite builds to dist/, not project root.

REMOVE from index.html before deploying:
  - Any builder badge script tags (Bolt, Lovable, Vite default favicon)
  - Replace /vite.svg favicon with appropriate trade icon
================================================================================
"""
    prompt = fill_variables(raw_prompt, data, niche=niche)
    prompt += _bolt_routing_note(data)
    return _inject_structure_block(prompt, data)


def assemble_gemini_prompt(data: dict, niche: str) -> str:
    prebuilt = load_prebuilt_prompt(niche, "gemini")
    if prebuilt:
        return fill_variables(prebuilt, data, niche=niche)
    base = assemble_bolt_prompt(data, niche)
    return f"""================================================================================
{niche.upper()} — GOOGLE AI STUDIO PROMPT (Gemini 3.1 Pro Preview)
Set thinking level: HIGH
Output: Complete multi-file React/Vite/Tailwind project
================================================================================

{base}

GEMINI-SPECIFIC ADDITIONS:
- Use CSS keyframe animations for hero entrance (fade + slide up)
- Add scroll-triggered section reveals via IntersectionObserver
- Add subtle parallax on hero background image
- CSS blur + scale transitions on service card hover
- Output ALL files completely: App.tsx, components/, index.html, tailwind.config.js
- Do NOT truncate or summarize any file

CONVERTER PROMPT (paste after site is generated, for single-file HTML demo):
"Rewrite this entire React/Vite app as a single self-contained vanilla HTML file.
Inline all CSS in <style> and all JS in <script>. Do not compress — rewrite
completely. Output only the complete HTML file, nothing else."
================================================================================
"""


def _inject_structure_block(prompt: str, data: dict) -> str:
    """
    Appends the SITE STRUCTURE DECISION block (with PAGE_MODE token) to the prompt.
    Called by assemble_claude_code_prompt() on all three return paths.
    Uses importlib to load findings_to_layer2.py by absolute path — no sys.path needed.
    """
    try:
        import importlib.util
        module_path = Path(__file__).parent / "findings_to_layer2.py"
        if not module_path.exists():
            print(f"  ⚠️  Structure block skipped: findings_to_layer2.py not found at {module_path}")
            return prompt

        spec   = importlib.util.spec_from_file_location("findings_to_layer2", module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        structure_block = module.rules_site_structure(data)
        if structure_block.strip():
            nav_pages  = data.get("NAV_PAGES", [])
            page_count = len(nav_pages) if nav_pages else 0
            mode_label = "multi" if page_count >= 2 else "single"
            print(f"  ✅ Structure block injected — {page_count} pages detected, PAGE_MODE: {mode_label}")
            separator  = "\n\n" + "=" * 80 + "\n"
            separator += "SITE STRUCTURE — READ THIS BEFORE WRITING ANY CODE\n"
            separator += "=" * 80 + "\n\n"
            return prompt + separator + structure_block
    except Exception as e:
        print(f"  ⚠️  Structure block skipped: {e}")
    return prompt


def assemble_claude_code_prompt(data: dict, niche: str) -> str:
    universal_path = DOCS_DIR / "master_prompts" / "universal_claude_code_prompt.txt"

    niche_path = NICHES_DIR / f"{niche}.md"
    has_prompt_vars = (
        niche_path.exists()
        and "## PROMPT_VARIABLES" in niche_path.read_text(encoding="utf-8")
    )
    if universal_path.exists() and has_prompt_vars:
        print(f"  ✅ Using universal_claude_code_prompt.txt + {niche}.md PROMPT_VARIABLES")
        template = universal_path.read_text(encoding="utf-8")
        prompt = fill_variables(template, data, niche=niche)
        return _inject_structure_block(prompt, data)

    prebuilt = load_prebuilt_prompt(niche, "claude-code")
    if prebuilt:
        print(f"  ⚠️  Using legacy {niche}_claude_code_prompt.txt — add PROMPT_VARIABLES to migrate")
        prompt = fill_variables(prebuilt, data, niche=niche)
        return _inject_structure_block(prompt, data)

    print(f"  ⚠️  No claude-code prompt or PROMPT_VARIABLES for '{niche}' — wrapping bolt prompt")
    base = assemble_bolt_prompt(data, niche)
    prompt = f"""================================================================================
{niche.upper()} — CLAUDE CODE PROMPT (VS Code)
Business: {data.get('BUSINESS_NAME', '')}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Mode: Single index.html — no build step required
================================================================================

BEFORE WRITING ANY CODE:
1. Confirm CLAUDE.md exists in this project folder.
   If missing: copy WEBSITE_CLAUDE.md from docs/ into this folder as CLAUDE.md

================================================================================

{base}

================================================================================
CLAUDE CODE OUTPUT REQUIREMENTS
================================================================================

- Single file: index.html in current workspace folder
- ALL CSS inline in <style> tag — no external stylesheets
- ALL JS inline in <script> tag — no external scripts
- No React, no Vite, no npm, no build step
- Preview by opening index.html directly in Chrome

SCREENSHOT LOOP (mandatory after Hero, Services, Reviews sections):
  node screenshot_check.js
  Check for: purple colors, mobile overflow, phone button visibility

DEPLOY:
  Demo:       Drag index.html to netlify.com/drop → live URL in 30 seconds
  Production: git push to GitHub → connect Vercel → auto-deploys on every push
================================================================================
"""
    return _inject_structure_block(prompt, data)


def assemble_skill_package(data: dict, niche: str) -> dict:
    return {
        "_meta": {
            "type":         "claude_code_skill_package",
            "skill":        "docs/WEBSITE_GENERATION_SKILL.md",
            "created":      datetime.now().isoformat(),
            "instructions": (
                "1. Open Claude Code in VS Code. "
                "2. Say: 'execute WEBSITE_GENERATION_SKILL.md using this file'. "
                "3. Claude Code builds the React project, runs npm run build, "
                "   then deploys with: netlify deploy --dir=dist --prod"
            ),
            "netlify_deploy_command":    "netlify deploy --dir=dist --prod",
            "netlify_dir_flag_note":     "--dir=dist is MANDATORY. Vite builds to dist/, not root.",
            "prerequisites": [
                "netlify-cli installed globally: npm install -g netlify-cli",
                "NETLIFY_AUTH_TOKEN in .env",
                "NETLIFY_SITE_ID in .env (omit to create new site automatically)",
                "WEBSITE_CLAUDE.md copied into client project folder as CLAUDE.md (design rules)",
                "puppeteer: npm install -g puppeteer",
            ],
        },
        "business_data":     data,
        "niche":             niche,
        "assembled_prompt":  assemble_bolt_prompt(data, niche),
        "universal_rules_path": str(UNIVERSAL_FILE),
        "niche_file_path":      str(NICHES_DIR / f"{niche}.md"),
    }


def save_output(content: str | dict, business_name: str, mode: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in business_name.lower())
    ts   = datetime.now().strftime("%Y%m%d")
    if mode == "skill-output":
        path = out_dir / f"{safe}_claude_code_package_{ts}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
    else:
        path = out_dir / f"{safe}_{mode}_prompt_{ts}.txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    return path


def main():
    parser = argparse.ArgumentParser(
        description="Generate website prompt package for a given business URL or input file."
    )
    parser.add_argument("--input",  help="Path to structured_input.json")
    parser.add_argument("--url",    help="Website URL (runs extraction automatically)")
    parser.add_argument("--mode",   default="bolt", choices=list(MODES),
                        help=f"Output mode. Options: {', '.join(MODES.keys())}")
    parser.add_argument("--niche",  help="Override niche detection")
    parser.add_argument("--output", help="Output directory override")
    args = parser.parse_args()

    if not args.input and not args.url:
        print("❌ Provide --input PATH or --url URL")
        print("\nExamples:")
        print("  python3 execution/generate_website.py --url https://example.com --mode claude-code")
        print("  python3 execution/generate_website.py --input output/structured_input.json --mode bolt")
        sys.exit(1)

    input_path = run_extraction(args.url, args.niche or "") if args.url else Path(args.input)
    data         = load_structured_input(input_path)
    business     = data.get("BUSINESS_NAME", "unknown")
    niche        = args.niche or data.get("_meta", {}).get("niche", "generic")
    out_dir      = Path(args.output) if args.output else PACKAGES_DIR

    print(f"\n{'='*60}")
    print(f"Building prompt package")
    print(f"  Business : {business}")
    print(f"  Niche    : {niche}")
    print(f"  Mode     : {args.mode} — {MODES[args.mode]}")
    if data.get("_meta", {}).get("places_enriched"):
        signals = data["_meta"].get("pitch_signals", [])
        print(f"  Places   : ✅ enriched — {len(signals)} pitch signal(s) injected")
    print(f"{'='*60}")

    if args.mode in ("bolt", "lovable"):
        content = assemble_bolt_prompt(data, niche)
    elif args.mode == "gemini":
        content = assemble_gemini_prompt(data, niche)
    elif args.mode == "claude-code":
        content = assemble_claude_code_prompt(data, niche)
    else:
        content = assemble_skill_package(data, niche)

    saved = save_output(content, business, args.mode, out_dir)

    print(f"\n✅ Saved → {saved}")

    if args.mode in ("bolt", "lovable"):
        print("\nNext:")
        print("  1. Open the prompt file above")
        print("  2. Attach logo + photos in Bolt/Lovable chatbox")
        print("  3. Paste and build")
        print("  4. DEPLOY: netlify deploy --dir=dist --prod  ← --dir=dist MANDATORY")

    elif args.mode == "gemini":
        print("\nNext: Open AI Studio → Gemini 3.1 Pro Preview → thinking HIGH → paste prompt")

    elif args.mode == "claude-code":
        print("\nNext:")
        print("  1. Create a new empty folder for this client")
        print("  2. Copy docs/WEBSITE_CLAUDE.md into that folder as CLAUDE.md")
        print("  3. Open the folder in VS Code")
        print("  4. Open Claude Code panel (spark icon in sidebar)")
        print("  5. Paste the prompt file contents → hit Enter")
        print("  6. Claude Code builds index.html + runs screenshot loop")
        print("  7. DEPLOY DEMO: drag index.html to netlify.com/drop → live URL")
        print("  8. Send that URL in cold outreach")
        print("\n  ⚠️  First time setup (run once globally):")
        print("  npm install -g puppeteer")

    else:
        print(f"\nNext:")
        print(f"  1. Open Claude Code in VS Code")
        print(f"  2. Say: 'execute WEBSITE_GENERATION_SKILL.md using {saved}'")
        print(f"  3. Claude Code builds → deploys with: netlify deploy --dir=dist --prod")


if __name__ == "__main__":
    main()
