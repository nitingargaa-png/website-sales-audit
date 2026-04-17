# GHL Setup Checklist — Local Home Service Business
## v3.1 — Aligned with SKILL.md v12 (adds GHL Automation Gap Assessment map)
## What changed from v2:
##   - Canadian SMS A2P decision tree (corrected — not just "separate from US")
##   - Voice AI widget setup with Labs activation step (corrected)
##   - GHL Snapshot procedure added (was completely missing)
##   - Domain cutover SOP added (was a one-liner, now a full procedure)
##   - Review request trigger defined (was undefined — "post-job" with no mechanism)
##   - QA acceptance checklist added before every go-live
##   - SerpApi paid plan noted in cost section
##   - Time estimates corrected: demo = 15–30 min, production-ready = 2–4 hrs
## What changed in v3.1 (SKILL.md v12 alignment):
##   - Added GHL Automation Gap Assessment map (TIER 1/2/3) in HOW TO USE
##   - Ties each section to the Automation Gap tier it fulfills for the Talking Points

---

## HOW TO USE THIS

Work through this checklist in order for every new client.
Sections are sequenced by dependency — don't skip ahead.
Estimated time per section is noted. Total: ~8–12 hours for a full Package 2 setup.

---

## GHL AUTOMATION GAP ASSESSMENT — MAP TO SKILL.md v12

SKILL.md v12 requires every audit's Talking Points to assess each automation
below as PRESENT / ABSENT / UNKNOWN based on Phase 1 detection. Use the
sections listed to fulfill each tier for a paying client:

**TIER 1 — CORE (every Package 2+ client gets these; pitch first to any prospect)**

| Automation | Fulfilled in Section | Pitch Angle |
|---|---|---|
| Missed-call text-back | Section 5 | "Every call you miss is likely walking to whoever answers next." |
| 5-min lead follow-up on form submit | Section 4 | "If someone fills out your form at 10pm, are they getting a reply that night?" |
| Online booking calendar | Section 3 | "A calendar on the site means bookings come in while you sleep." |
| Chat widget (SMS capture) | Section 9 | "Someone visiting at 9pm has no way to reach you." |
| CRM pipeline | Section 8 | "There's no central place to see every lead and where it stands." |

**TIER 2 — GROWTH (Package 3 base; add-on for Package 2 clients after 60 days)**

| Automation | Fulfilled in Section | Pitch Angle |
|---|---|---|
| Review request automation (post-job SMS) | Section 6 | "Happy customers aren't leaving reviews because nobody's asking at the right moment." |
| Appointment reminder sequence | Add to Section 3 workflow | "No-shows and late cancels cost time and money." |
| Estimate / invoice follow-up | Add to Section 4 workflow | "Estimates going quiet is one of the most common revenue leaks." |
| Unified inbox (omnichannel) | GHL Conversations (built-in) | "Stop juggling texts, email, and Facebook DMs on separate apps." |
| Call tracking numbers | Add-on — CallRail or GHL LC Phone | "You have no way to know which ads or pages drive calls." |

**TIER 3 — SCALE (Package 3 add-ons; pitch to established operators)**

| Automation | Fulfilled in Section | Pitch Angle |
|---|---|---|
| Voice AI receptionist (overflow + after-hours) | Section 2.5 + Section 7 | "Calls that come in when dispatch is on hold go to voicemail — and then nowhere." |
| Re-engagement / win-back campaign | Custom workflow | "Past customers already trust you — one message can generate bookings for free." |
| Seasonal broadcast campaigns | GHL broadcast (built-in) | "One SMS before furnace season can fill your schedule for weeks." |
| Facebook / Google lead ad integration | GHL integration | "Ad leads sitting in a Meta dashboard are lost by the time you see them." |
| Social DM automation | GHL integration | "An FB message at 8pm unanswered until morning is already hired by your competitor." |
| Referral automation | Custom workflow | "Your happiest customers are your best salespeople — ask them automatically." |
| Workflow AI (intent routing) | GHL Workflow AI | "'Pipe burst' needs a different response than 'seasonal inspection.'" |

Mark each row PRESENT / ABSENT / UNKNOWN during Phase 1 detection (not during
setup). During setup, this map tells you which GHL section fulfills each
committed automation in the client's package.

---

**Before you start: verify GHL plan supports the client count.**
- Starter ($97/month): confirmed up to 3 sub-accounts — verify in your GHL account
  before assuming this. If Starter = 1 sub, you need Unlimited ($297) from client 2.
- **Upgrade trigger: client 4** (not client 3). Math: upgrading Starter → Unlimited = +$200/month.
  Client 3 MRR ($297–$497) is nearly fully consumed by that cost jump. Operate client 3
  on Starter by rotating the demo sub-account slot. Upgrade when client 4 signs —
  by then 4 × $297+ = $1,188+/month covers the $297/month platform cost with margin.
- Unlimited ($297/month): unlimited sub-accounts
- SaaS Pro / Agency Pro ($497/month): unlimited + white-label SaaS Mode

---

## SECTION 0 — PHONE FORWARDING SETUP (READ BEFORE ONBOARDING)
*~15 minutes | Do this during or immediately after the discovery call*

GHL Voice AI answers calls that arrive at a **GHL-provisioned phone number**.
It cannot intercept calls at the client's existing carrier number by itself.
You must configure call forwarding from the client's number to the GHL number.

**Choose one of two paths based on client preference:**

---

### PATH A — Full Forwarding (Recommended for first clients)
All calls to the client's existing number forward to the GHL Voice AI number.
Voice AI answers every call. Owner receives an internal notification for each call
and can call anyone back at any time.

**Who configures it:** Client (takes 2 minutes)
**Carrier independence:** Works on any carrier — mobile, landline, VoIP
**GHL setup:** Set Voice AI agent to PRIMARY mode (answers immediately)

**Script for client:**
> "What we'll do is forward your main number to your new AI receptionist number.
> Takes about 2 minutes on your phone. You keep your existing number — nothing
> changes on your end. The AI answers, captures the lead, and you get notified
> immediately. You can call anyone back from your own number as normal."

**Setup instruction for client (mobile — works on Rogers, Bell, Telus, AT&T, Verizon, T-Mobile):**
> Go to your phone's Settings → Phone → Call Forwarding → turn ON → enter the GHL number.
> Or dial: **\*72[GHL number]** then press Call. (Example: \*724699492095)
> To turn off: dial **\*73** then press Call.

---

### PATH B — Forward on No Answer (After-hours feel, owner still gets first ring)
Calls ring the client's phone first. If unanswered after N rings, they forward
to the GHL Voice AI number. Owner handles daytime calls personally; AI catches
everything unanswered.

**Who configures it:** Client (carrier-dependent, 2–5 minutes)
**Limitation:** True time-of-day routing (after 5pm only) is NOT available on
most consumer/SMB plans without a VoIP middleware layer (RingCentral, OpenPhone).
Do not promise time-of-day routing unless you also sell a VoIP layer.
**GHL setup:** Set Voice AI agent to BACKUP mode OR keep on PRIMARY with working hours set

**Carrier-specific setup codes:**

| Carrier | Forward on No Answer Code | Cancel Code | Notes |
|---|---|---|---|
| Rogers (Canada) | \*61\*[GHL number]# | \*61# | Standard mobile |
| Bell (Canada) | \*61\*[GHL number]# | #61# | Some Bell plans use portal instead |
| Telus (Canada) | \*61\*[GHL number]# | \*61# | Same as Rogers |
| AT&T (USA) | \*61\*[GHL number]# | \*61# | Postpaid mobile |
| Verizon (USA) | \*71[GHL number] | \*710 | Simple format |
| T-Mobile (USA) | \*61\*[GHL number]\*11\*[rings]# | ##61# | [rings] = 5, 10, 15, 20, 25, or 30 seconds |
| Comcast Business | Via admin portal | Via admin portal | Star codes not supported |
| Shaw/Telus Business | Via admin portal | Via admin portal | Use MyAccount online |

**Note on ring count:** Most carriers default to 4–5 rings (~20–25 seconds) before forwarding.
This is sufficient — clients rarely want to adjust it.

---

### PATH C — Port the Number into GHL (Upsell, $250 fee)
Client's existing number is permanently transferred into GHL.
Voice AI uses the client's own number directly — no forwarding required.
**Timeline:** 2–4 weeks. Client must authorize with current carrier.
**Use case:** Clients who insist on using their existing number for the AI receptionist
and do not want call forwarding.

> **Default messaging for all clients:**
> "You get a dedicated AI receptionist number. You can add it to your website,
> Google Business Profile, and anywhere you advertise. Your existing number stays
> exactly as-is. If you want the AI to also catch calls to your main number,
> we set up simple forwarding — takes 2 minutes."

---


---

## KB MAINTENANCE PROCESS

**When a client's prices, services, hours, or promotions change:**

1. Client submits update request via email or text to you (set this expectation at onboarding)
2. Open GHL sub-account → AI Agents → Knowledge Base → [Client KB]
3. Edit the relevant Rich Text section (pricing, services list, hours, etc.)
4. Save → confirm KB status is still **Active** (status can revert — check it)
5. Test both agents: make a test call and a test chat asking about the changed information
6. Reply to client confirming the update is live

**Important:** The Voice AI agent and Conversation AI bot share one KB.
One edit affects both agents simultaneously. There is no channel-specific override —
if Voice AI and Chat AI need different information (e.g., different emergency pricing),
you must either split the KB into two separate KBs (one per agent) or handle the
difference in the agent prompt itself.

**SLA commitment to clients:** Respond to KB update requests within 24 hours.
Updates take 10–15 minutes. Charge for time if updates become frequent
(>2 per month) — include a clause in your service agreement.

**Proactive KB review:** Review each client's KB quarterly. Check for:
- Prices that may have changed (seasonal HVAC pricing, material cost increases)
- Services added or discontinued
- Hours changes (holiday schedules, expanded coverage)
- New service areas


## SECTION 1 — ACCOUNT & SUBACCOUNT SETUP
*~30 minutes*

- [ ] Create new Sub-Account in GHL for this client
- [ ] Set: business name, address, phone, timezone, industry
- [ ] Connect existing phone OR provision new GHL local number
      (Local GHL number is strongly recommended — required for missed call text-back)
- [ ] Verify number can send AND receive SMS (send a test from another phone)
- [ ] Set up client email address (name@businessdomain.com via Google Workspace or Namecheap)
- [ ] Set business hours in account settings
- [ ] Add client as User with their own login (limited access — no billing view)

**Naming convention for sub-accounts:**
  Format: [Trade] — [City] — [Business Name Short]
  Example: Plumbing — Mississauga — MPS
  Reason: At 10+ clients, consistent naming prevents confusion in the agency dashboard.

---

## SECTION 1.5 — SMS COMPLIANCE REGISTRATION ⚠️ DO NOT SKIP
*~20 minutes setup + 24–72 hours for carrier approval*

> **⚠️ MANDATORY BEFORE ANY SMS WORKFLOW GOES LIVE**
> Unregistered numbers are silently blocked or throttled within days of first volume.
> Register IMMEDIATELY after provisioning the number — approval takes 24–72 hours.

### Canadian Clients (GTA focus) — Decision Tree

**Step 1: When was the GHL number purchased?**

  BEFORE March 26, 2025 → Canada-only messaging (CA→CA) does NOT require A2P.
  But: if ANY messages will go to US numbers → A2P is mandatory regardless of purchase date.
  Recommended: Register A2P anyway — Canadian carriers are aligning with US rules.

  ON OR AFTER March 26, 2025 → A2P registration OR Persona verification required for CA→CA.
  If messages go to US numbers → A2P registration is mandatory (no Persona option).

**Step 2: What is the messaging direction?**

  CA→CA only:   Register A2P OR complete Persona verification in GHL
  CA→US any:    A2P brand + campaign registration is MANDATORY
  CA→CA+US mix: A2P mandatory (treat as CA→US)

**Step 3: CASL compliance (required for ALL Canadian clients regardless of A2P)**

  CASL (Canada's Anti-Spam Legislation) applies to ALL commercial text messages:
  - [ ] Collect **valid consent** before sending commercial messages.
        CASL distinguishes two types:
        • Express consent: customer explicitly opted in (checkbox on booking form, verbal "yes")
        • Implied consent: existing business relationship (they hired you, gave you their number,
          or their number is in a public business directory AND they are a business)
        Cold leads from a Voice AI call or missed call do NOT automatically have implied consent
        for commercial follow-up messages. Treat them as requiring express consent.
  - [ ] **M-C3 lead nurture — FIRST MESSAGE MUST BE A CONSENT REQUEST, not a commercial offer:**
        Wrong (CASL violation): "Hi, we'd love to help with your plumbing needs! Call us at..."
        Correct: "Hi, this is [Business Name]. We'd like to follow up on your inquiry.
        Reply YES to receive updates, or STOP to opt out."
        Only send commercial messages (quotes, promotions, follow-ups) AFTER receiving YES.
        Tag contacts with `sms-consent-given` before any commercial SMS workflow continues.
  - [ ] Include sender identification in every message: "— [Business Name]"
  - [ ] Include STOP opt-out instruction in first message:
        "Reply STOP to unsubscribe"
        French opt-out keywords (ARRET, FIN, DÉSABONNER): legally required for
        Quebec-based recipients under Quebec's Charter of the French Language.
        For GTA/Ontario-only campaigns, English STOP is sufficient under CASL.
        Supporting French keywords is recommended as a carrier best practice
        regardless of province.
  - [ ] Build quiet hours into workflows: no SMS before 9am or after 9pm local time
  - [ ] GHL's built-in opt-out management handles STOP commands automatically — verify it's on

### US Clients — A2P 10DLC (standard)

  **⚡ Submit A2P on Day 1 of sub-account setup — not when you're ready to launch.**
  Approval takes 24–72 hours minimum; some campaigns take 7–14 days if TCR flags
  anything. If you wait until the site is live to register, SMS workflows are dead
  on arrival and you lose the missed-call text-back window that justifies the retainer.

  - [ ] GHL → Settings → Phone Numbers → A2P Registration
  - [ ] Register Brand: legal business name, EIN, address, website
  - [ ] Register Campaign: use case = "Lead follow-up and appointment reminders for local home service business"
  - [ ] Campaign type: Low Volume Mixed (correct for most small trades clients)
  - [ ] Submit and note the date — 24–72 hours to approve; log it in prospects.csv
  - [ ] Do NOT activate SMS workflows until status shows "Active"
  - [ ] If status stays "Pending" past 72 hours: check GHL support → TCR flagged
        common issues: mismatched brand name, missing website, PO Box address

  **Pre-A2P SMS hard lockdown — use all three layers before any client goes live:**
  - [ ] Layer 1 (Hard block): Do NOT provision or assign any SMS-capable sending
        number to the sub-account until A2P is approved. Without a valid From number,
        no workflow can physically send SMS. Platform-level block — no logic required.
  - [ ] Layer 2 (Operational gate): Keep ALL SMS-sending workflows in Draft
        (unpublished) state until A2P is approved. Promote to Published in one
        batch change the day approval is confirmed.
  - [ ] Layer 3 (Account-level kill switch): GHL → Settings → Business Info → SMS
        → toggle "Disable SMS" ON during setup. Toggle OFF only after A2P approval.
        This setting overrides all workflows regardless of their published state.
  Note: The `sms_active = FALSE` custom value is a fourth redundant check — keep it,
  but treat it as a backup, not the primary compliance control. A misconfigured
  workflow that skips the custom value check can still fire SMS if layers 1–3 aren't
  in place. Layers 1–3 are platform-enforced; the custom value is logic-enforced.

### Both US and Canadian

  - [ ] After approval confirmed, send one test SMS through GHL to verify delivery
  - [ ] Check that merge fields resolve (see Section 4 merge field note)

---

## SECTION 2 — WEBSITE & FORMS
*~1 hour (site already built externally via Bolt/Lovable — this section = integration only)*

> **Time estimate correction (from peer review):**
> Demo build: 15–30 minutes in Bolt/Lovable using the niche prompt.
> Production-ready delivery: 2–4 hours total including QA, image cleanup,
> GHL widget activation, and client approval round.
> "5 minutes per site" = first draft only, not client-ready delivery.

- [ ] Site is deployed to Netlify (live URL confirmed)
- [ ] Site was deployed with: `netlify deploy --dir=dist --prod`
      `dist/` is Vite's default build output. If `vite.config.js` overrides
      `build.outDir`, deploy that folder instead. Generated configs should always
      set `build: { outDir: 'dist' }` explicitly.
- [ ] All 6 GHL placeholder divs are present in the deployed site
- [ ] Quote Request Form connected → triggers Lead Follow-Up Workflow (Section 4)
- [ ] Phone number on all pages uses href="tel:+1[digits]" — verified tappable on real iPhone
- [ ] "Book an Appointment" button linked to GHL calendar (Section 3)
- [ ] Test every form: submit real test → confirm lead in CRM
- [ ] Confirm site loads correctly on iPhone Safari (not just Chrome DevTools)
- [ ] Complete QA Checklist (Section 11) before sharing link with client

> **⚠️ Netlify account-level suspension risk (critical at 5+ clients):**
> Free tier = 100GB bandwidth + 300 build minutes/month, applied across the ENTIRE account.
> When any limit is hit, ALL sites on the account pause simultaneously until next month.
> One client traffic spike can take all clients offline at once.
> At 5+ clients: upgrade to Netlify Pro ($19/month) OR use separate Netlify accounts
> per client to isolate overage risk. Monitor usage at Team Settings → Usage.

---

## SECTION 2.5 — VOICE AI AGENT SETUP (v1.5 Universal Template)
*~25–35 minutes per client | Use Appendix Step sequence from prompt template*

> **PREREQUISITE:** Voice AI Labs must be enabled in this sub-account before the agent
> will function. GHL sub-account → Settings → Labs → toggle ON "Voice AI."

### Step 1 — Create Custom Values (before pasting prompt)
All 10 custom values must exist in GHL BEFORE the prompt is pasted.
Missing values = agent reads blank text aloud to callers.

GHL: Settings → Custom Values → + Add Value (Text field for all)

| Custom Value Key | Default to Set | Notes |
|---|---|---|
| business_name | [Client Business Name] | Required in greeting |
| business_phone | [Client Phone] | Callback references |
| business_address | [Client Address] | Context only |
| service_area | [City, Neighborhoods] | Used in area-check handler |
| owner_callback_time | as soon as possible | Emergency + after-hours flows |
| is_business_hours | false | ⚠ DO NOT set manually — set by workflow (Step 2). Default 'false' = safe fallback |
| availability_framing | In most cases we can get someone out the same day. | Update during busy periods |
| sms_active | FALSE | Toggle to TRUE after A2P only |
| emergency_available | yes | yes/no |

**Two custom values that are NEW vs previous setup:**
- `is_business_hours` — must be created here AND written by the business hours workflow
- `availability_framing` — replaces any hardcoded same-day language in the prompt

### Step 2 — Build Business Hours Workflow (before go-live)
GHL Voice AI cannot check the current time reliably in the prompt — this fails silently.
All hours gating must happen at the workflow level.

```
Trigger: Inbound Call Received (before routing to Voice AI agent)
Branch A — Within business hours:
  → Set Custom Value: is_business_hours = true
  → Route call to Voice AI agent
Branch B — Outside business hours:
  → Set Custom Value: is_business_hours = false
  → Route call to Voice AI agent
```

Test both values explicitly before go-live. Verify routing in both directions.

### Step 3 — Create Voice AI Agent
- [ ] GHL → AI Agents → + Create Agent → Voice AI
- [ ] Paste v1.5 Universal Template prompt (after completing SWAP items below)
- [ ] Voice: select per client preference (Jessica = garage door demo default)
- [ ] Model: GPT-4o
- [ ] Attach Knowledge Base (confirm KB status = Active)
- [ ] Assign phone number
- [ ] Disable Welcome Message (required for web widget calls)

### Step 4 — SWAP Items in Prompt Before Pasting
Delete the sections that DON'T apply; keep only what matches this deployment:
- [ ] S1.1: Replace [AGENT_NAME] → keep ONE niche restriction line, delete 21 others
- [ ] S5.2: DELETE two booking mode lines → leave only the applicable one
- [ ] S6.3: Keep ONE niche emergency trigger block → delete 21 others
- [ ] S8.1: Keep ONE niche qualification block → delete 21 others
- [ ] Confirm booking mode matches client workflow (BOOK DIRECTLY / CAPTURE ONLY / BOTH BY URGENCY)

### Step 5 — Build M-C1 Post-Call Workflow (not a native GHL feature)
```
PATH A — fires immediately on Call Completed:
  → Add Tag: ai-voice-lead
  → Create Opportunity: AI Lead Pipeline, Stage 1
  → Internal notification to owner (no merge fields — just alert text)

PATH B — fires on Transcript Generated trigger:
  → Add Note: {{call.summary}} and {{call.transcript}}
  → Optional: second internal notification with summary
```

Use "Transcript Generated" trigger for PATH B to avoid race condition where
summary merge fields are blank at call-end time.

### Step 6 — Run Go-Live Test Matrix (minimum 10 calls)
See v1.5 Appendix Step 10 for full test matrix. Minimum before any client goes live:
- [ ] Business hours standard booking (is_business_hours = true)
- [ ] After-hours non-emergency (is_business_hours = false)
- [ ] Emergency call — niche trigger fires, owner notified
- [ ] Life-safety scenario — 911 redirect fires (Section 2.7 of prompt)
- [ ] Pricing objection — 3-push sequence, then owner callback offer
- [ ] "Speak to a real person" — transfer fires + failure fallback
- [ ] Phone/address read-back — digit-by-digit confirmed
- [ ] Booking action failure — Universal System Fallback fires (S10.19)

---

## SECTION 3 — APPOINTMENT BOOKING CALENDAR
*~45 minutes*

- [ ] GHL → Calendars → Create Calendar
      Name: "Book a Free Estimate" or "Schedule a Service Call"
- [ ] Set availability (actual days/hours the client takes appointments)
- [ ] Appointment duration: 30 or 60 minutes for estimates
- [ ] Buffer time: 15–30 min between appointments
- [ ] Minimum scheduling notice (4 hours or same-day — confirm with client)
- [ ] Confirmation message: customized for this trade
- [ ] Auto confirmation: SMS + email to customer on booking
- [ ] Reminders: SMS 24 hours before + SMS 2 hours before
- [ ] Business owner notification on new booking
- [ ] Embed calendar in website booking section (replace ghl-calendar placeholder div)
- [ ] Test: book a fake appointment, confirm all notifications fire

---

## SECTION 4 — LEAD FOLLOW-UP WORKFLOW
*~1 hour*

> **⚠️ PREREQUISITE:** Build Section 8 (CRM Pipeline) first.
> This workflow references pipeline stages that must already exist.

> **MERGE FIELDS — READ BEFORE BUILDING:**
> Use {{ }} picker in GHL message editor. Never type [First Name] literally.
> Common fields:
>   {{contact.first_name}}, {{contact.phone}}, {{contact.email}}
>   {{location.name}} = business name, {{location.phone}} = business phone
> Always preview workflow messages to confirm fields resolve before activating.

Trigger: Form Submitted

- [ ] Step 1 — Wait: 1 minute (prevents GHL hiccup on immediate trigger before contact created)
- [ ] Step 2 — SMS to lead:
      "Hi {{contact.first_name}}, thanks for reaching out to {{location.name}}!
      We got your request and will call you shortly. Urgent? Call {{location.phone}}.
      — [Owner First Name]"
- [ ] Step 3 — Email to lead: friendly confirmation, their service request, phone number, booking link
- [ ] Step 4 — Internal SMS to owner:
      "New lead: {{contact.first_name}} {{contact.last_name}}, {{contact.phone}},
      Service: {{contact.service_needed}}"
- [ ] Step 5 — Tag: "New Lead — Website Form"
- [ ] Step 6 — Move to pipeline stage: "New Lead"
- [ ] Step 7 — Create task: "Call {{contact.first_name}} back — website inquiry" — Due: Today
- [ ] Save and activate
- [ ] Test with real form submission — confirm all messages + pipeline stage + task

---

## SECTION 5 — MISSED CALL TEXT-BACK
*~30 minutes*

> **⚠️ Only works if calls route through the GHL phone number.**
> Discuss with client and pick one routing option before setup:
>
> Option 1 — New GHL number as primary (best for new clients — update website + GBP)
> Option 2 — Forward existing number to GHL: Rogers/Bell dial *72 + GHL number
> Option 3 — GHL tracking number on website only (misses calls from trucks/cards)
>
> After choosing: test by calling the number, letting it ring to voicemail,
> and confirming the text-back fires within 60 seconds.

Trigger: Missed Call (Inbound)

- [ ] Step 1 — Wait: 1 minute
- [ ] Step 2 — SMS to caller:
      "Hi, sorry we just missed your call! This is {{location.name}}.
      We'll get back to you shortly — or if it's urgent, try {{location.phone}}.
      What were you calling about?"
- [ ] Step 3 — Internal SMS to owner: "Missed call from {{contact.phone}}. Auto-text sent."
- [ ] Step 4 — Tag: "Missed Call — Needs Follow-Up"
- [ ] Step 5 — Task: "Follow up missed call — {{contact.phone}}" — Due: Today
- [ ] Test: call the number, don't answer, confirm text fires within 60 seconds

---

## SECTION 6 — AUTOMATED REVIEW REQUEST
*~45 minutes*

**The trigger problem (confirmed in peer review — must be solved for this to work):**
GHL's review request fires on a pipeline stage change. But home service clients
without FSM software have no automatic way to trigger "Job Completed."
Define the trigger before you build the workflow — pick one option with the client:

  Option A — Technician submits a GHL form from their phone after each job
    Build a simple GHL form: "Job Complete" with fields: Customer Name, Phone, Service Done
    Form submission → triggers review request workflow
    Client shares the form URL on their phone's home screen

  Option B — Owner manually moves the contact to "Job Completed" in GHL CRM
    Requires daily habit — works if owner is disciplined about pipeline management
    Simplest — no extra form needed

  Option C — Missed-call text-back as proxy
    When caller replies to the text-back and books/confirms job → owner marks complete
    Less reliable but zero added friction

  **Recommended: Option A (form) for tech-forward clients, Option B for others.**
  Document which option you chose in the client file.

**Build the workflow:**

Trigger: Pipeline Stage Changed → "Job Completed"

- [ ] Step 1 — Wait: 2 hours (let customer settle before asking)
- [ ] Step 2 — SMS to customer:
      "Hi {{contact.first_name}}, it was great working with you!
      If you have 60 seconds, a Google review would mean the world to us:
      [Google Review Link] — [Owner First Name] at {{location.name}}"
- [ ] Step 3 — Wait: 3 days
- [ ] Step 4 — Follow-up SMS (always sends — GHL cannot detect if review was posted):
      "Hi {{contact.first_name}}, just checking in — if you had a good experience,
      a quick Google review helps other homeowners find us: [Google Review Link]
      Thanks so much! — {{location.name}}"
- [ ] Step 5 — Tag: "Review Requested ×2"

**Get the Google Review link:**
- GBP → Get More Reviews → Copy link → shorten with bit.ly for cleaner SMS

- [ ] Connect GBP: GHL → Settings → Integrations → Google
- [ ] Train client on chosen trigger method (Option A, B, or C above)
- [ ] Test: manually move test contact to "Job Completed" → confirm texts fire

---

## SECTION 7 — VOICE AI WIDGET (inline embed)
*~45 minutes*

> **This feature requires Labs activation per sub-account — do not skip this step.**
> The widget will silently fail to load if Labs is not enabled first.

**Setup steps in order:**

- [ ] Step 1 — Enable in Labs:
      GHL sub-account → Settings → Labs → toggle ON "Voice AI" or "Voice AI Chat Widget"
      (Labs toggle names may vary slightly — look for any Voice AI option)

- [ ] Step 2 — Create widget:
      Sites → Chat Widget → + Create New Widget → select "Voice AI" as widget type

- [ ] Step 3 — Configure:
      - Style tab → Widget Placement → select "Embedded/Inline"
        (NOT Sticky — Sticky floats in corner; Embedded renders inline where you place it)
      - Set greeting, agent name, and response behavior
      - Set office hours (show "We're open" vs "We're closed — leave a message")

- [ ] Step 4 — Copy the JS snippet from the widget builder

- [ ] Step 5 — Paste into the deployed site:

      ⚠️ DUAL PLACEMENT APPROACH — inline vs floating widgets work differently:

      FLOATING CHAT WIDGET (id="ghl-chat-widget"):
      Place JS snippet before </body> in index.html. Works fine here because
      the widget appends to <body> which already exists before React mounts.

      ```html
      <!-- In index.html, before </body> -->
      <div id="ghl-chat-widget"></div>
      <script><!-- Paste floating chat widget JS here --></script>
      </body>
      ```

      INLINE VOICE WIDGET (id="ghl-voice-inline"):
      ⚠️ Do NOT place this script before <div id="root">. The placeholder div
      lives inside the React component tree — it doesn't exist in the DOM until
      React mounts. Script before <div id="root"> fails silently (widget falls
      back to floating mode).

      Use ONE of these two correct approaches:

      Option A — Static HTML outside React root (simplest):
      ```html
      <!-- In index.html <body>, AFTER the script tags, OUTSIDE <div id="root"> -->
      <div id="ghl-voice-inline" style="width:100%;"></div>
      <script><!-- Paste GHL Voice AI inline widget JS here --></script>
      <div id="root"></div>
      ```
      Then remove the ghl-voice-inline div from your React JSX entirely —
      it now exists as a static HTML element above the React root.

      Option B — useEffect inside React component (if Option A breaks layout):
      In the React component that renders the inline placeholder:
      ```jsx
      useEffect(() => {
        // GHL inline widget script runs here after component mounts
        // div already exists in DOM at this point
        const script = document.createElement('script');
        script.innerHTML = `/* your GHL widget init code */`;
        document.getElementById('ghl-voice-inline').appendChild(script);
      }, []);
      ```

- [ ] Step 6 — Redeploy: `netlify deploy --dir=dist --prod`

- [ ] Step 7 — Test on mobile: open the site, confirm the inline voice widget
      renders between the hero and trust bar sections

---

## SECTION 8 — CRM PIPELINE SETUP
*~30 minutes — BUILD THIS BEFORE SECTION 4*

- [ ] GHL → CRM → Pipelines → Create Pipeline
      Name: "[Business Name] — Jobs Pipeline"

Stages:
- [ ] New Lead
- [ ] Contacted
- [ ] Estimate Sent
- [ ] Booked
- [ ] Job Completed  ← triggers review request (Section 6)
- [ ] Won — Paid
- [ ] Lost (add a note field — why did we lose this?)

- [ ] Confirm Lead Follow-Up Workflow references "New Lead" stage
- [ ] Walk client through moving contacts between stages (5-minute training)
- [ ] Show them how to log a note after every call

---

## SECTION 8.5 — GHL MASTER SNAPSHOT ⭐ NEW — DO THIS AFTER FIRST CLIENT
*~1 hour (one time only — saves 3+ hours on every subsequent client)*

> **This step was completely missing from v2. It's the highest-leverage operational
> improvement in this checklist. Do it after your first client is fully configured.**

A GHL Snapshot captures your entire sub-account configuration — all workflows,
pipelines, calendar settings, chat widget, and templates — as a reusable template.
Every new client starts from this instead of a blank sub-account.

**Result: GHL setup time drops from 6–10 hours to 30–45 minutes per client.**

**How to create a Snapshot:**

- [ ] Confirm first client's sub-account is fully configured and tested
- [ ] GHL Agency Dashboard (not sub-account) → Snapshots → Create New Snapshot
- [ ] Name it: "Home Services — Base v1 — [Month Year]"
- [ ] Select what to include:
      ✅ Workflows (all automations)
      ✅ Pipelines
      ✅ Calendars
      ✅ Chat Widgets
      ✅ Custom Fields
      ✅ Tags
      ❌ Contacts (never include real client contacts in a Snapshot)
      ❌ Conversations
- [ ] Save the Snapshot

**How to apply a Snapshot to a new client:**

- [ ] GHL → Create New Sub-Account → select your Snapshot from the dropdown
- [ ] All workflows, pipelines, and settings are pre-configured
- [ ] Update: business name, phone number, email, widget colors, calendar hours
- [ ] Replace all "[Business Name]" placeholders in workflow messages with merge fields
      (the Snapshot preserves message templates — update placeholders before activating)
- [ ] Run SMS test to confirm A2P is registered and messages deliver
- [ ] Activate workflows

**Voice AI Snapshot — IMPORTANT UPDATE (2026):**
GHL now supports Voice AI configurations in snapshots. When creating or re-exporting
your snapshot, ensure "Voice AI" is ticked in the snapshot component list.
This clones the agent prompt, call flow, and workflows — only the assigned phone number
must be set manually after import (phone numbers cannot transfer via snapshot).
This reduces per-client Voice AI setup from 30 min manual recreation to ~5–10 min.

**Snapshot versioning:**
After every major workflow improvement, create a new Snapshot version:
  "Home Services — Base v2 — [Month Year]"
Keep old versions archived — don't overwrite. Label clearly.

---

### POST-IMPORT VALIDATION CHECKLIST
*Run these 5 tests immediately after applying a Snapshot to a new sub-account.
Do not activate any client workflows until all 5 pass.*

**Test 1 — Voice AI fires correctly:**
- [ ] Assign a phone number to the Voice AI agent in the new sub-account
- [ ] Call the number from another phone
- [ ] Confirm: agent answers, greets correctly, responds to a test inquiry
- [ ] Confirm: M-C1 (Voice AI Call Complete Handler) fires after call ends
- [ ] Confirm: internal notification reaches you (Vinesh or agency email) — NOT empty

**Test 2 — Internal notification recipients are correct:**
- [ ] Open M-C6 (Internal Notification Hub) → check recipient list
- [ ] Staff member records do NOT transfer via snapshot — recipient may show blank or broken
- [ ] Re-add the correct notification recipient (agency account or client staff member)
- [ ] Repeat for M-C1, M-C5 (Emergency Alert) — both send internal notifications

**Test 3 — Calendar reference is correct:**
- [ ] Open M-C4 (Appointment Confirmation) → open the "Book Appointment" or calendar action
- [ ] Confirm the calendar referenced is the NEW client's calendar, not the agency default
- [ ] If wrong: re-select calendar from dropdown inside the workflow action
- [ ] Book a test appointment — confirm it appears in the correct calendar

**Test 4 — Primary Conversation AI bot is active:**
- [ ] GHL → AI Agents → Conversation AI → confirm the intended bot shows "Primary"
- [ ] Send a test chat message via the chat widget
- [ ] Confirm the bot responds (not Live Chat / no response = bot not set as primary)

**Test 5 — Custom fields are present and correct:**
- [ ] GHL → Settings → Custom Fields → confirm all 10 AI intake fields are listed
- [ ] Open any contact → confirm the custom field group "AI Intake Data" is visible
- [ ] If any fields are missing: re-create them manually (field definitions usually transfer,
      but verify — field IDs may regenerate and break workflow references)
- [ ] Open M-C1 → confirm the "Add Note" action still shows the correct merge fields
      (not "Missing field" warnings)

---

## SECTION 9 — CHAT WIDGET (standard SMS capture)
*~1 hour*

- [ ] GHL → Sites → Chat Widget → Create widget
- [ ] Type: "SMS Chat" (captures phone number immediately — better than live chat)
- [ ] Greeting: "Hi! 👋 How can [Business Name] help you today? Leave your number and we'll text you right back."
- [ ] Color: match client brand
- [ ] Office hours: show "We're open!" vs after-hours message
- [ ] After-hours message: "Thanks! We're closed right now but will get back to you first thing in the morning. Emergency? Call [Phone]."
- [ ] Connect to Lead Follow-Up Workflow (Section 4)
- [ ] Embed code: paste into site before </body> (the ghl-chat-widget div)
- [ ] For React/Netlify: place in index.html, not in JSX (avoids hydration conflicts)
- [ ] Test: open site in incognito window, chat, confirm lead in GHL

---

## SECTION 10 — GOOGLE BUSINESS PROFILE
*~1 hour (scratch) or 30 min (optimization)*

- [ ] Claim and verify GBP listing (pre-check: is it already claimed? by whom?)
- [ ] Business name: exact operating name — no keyword stuffing
- [ ] Primary category: specific trade (e.g., "Plumber" not "Home Services")
- [ ] Phone: use GHL tracking number (so calls log in CRM)
- [ ] Website: link to new Netlify site
- [ ] Hours: complete and accurate including holidays
- [ ] Services: every service with description
- [ ] Photos: logo, cover, 5–10 job photos
- [ ] Business description: 750 chars, mentions city, services, years, differentiator
- [ ] Q&A: pre-populate 5 common questions
- [ ] Connect GBP to GHL: Settings → Integrations → Google (for review management)
- [ ] Enable Google Business Messages in GHL → Integrations → Google
      (pulls GBP inquiry messages into GHL inbox — significant win for GTA contractors)

---

## SECTION 11 — QA ACCEPTANCE CHECKLIST ⛔ MANDATORY BEFORE EVERY GO-LIVE
*~30 minutes — do this before sharing the site URL with anyone*

> **Every reviewer flagged QA as a critical missing piece. No site goes live
> without passing every item below.**

### Mobile Device Tests (use a real iPhone, not just browser DevTools)
- [ ] Site loads on iPhone Safari (most common for trades customers)
- [ ] Site loads on Android Chrome
- [ ] Sticky header visible and stays at top while scrolling
- [ ] Phone number tap-to-call works (tapping opens the phone dialer)
- [ ] Hero CTA button is tappable and not overlapped by header
- [ ] No horizontal scroll at 390px width
- [ ] Text is readable without zooming
- [ ] All 6 GHL placeholder divs visible (dashed borders confirm placement)

### Desktop Tests
- [ ] Site loads at 1440px width
- [ ] Navigation links scroll to correct sections
- [ ] Google Maps iFrame loads (correct city/area shown)
- [ ] Footer 4-column layout intact

### Content Checks
- [ ] All phone instances use actual phone number (no "[PHONE]" literal text remaining)
- [ ] Business name appears correctly (no template placeholder text)
- [ ] All 3 review cards show real review text (not placeholder)
- [ ] Service areas list specific neighborhoods (not "Greater Toronto Area")
- [ ] No Lorem Ipsum text anywhere
- [ ] Copyright year is current and dynamic (not hardcoded)
- [ ] Favicon is professional (no Vite lightning bolt, no blank square)

### Technical Checks
- [ ] HTTPS active (Netlify provides automatically — green padlock in browser)
- [ ] Page title correct: "[Business Name] | [Trade] in [City]"
- [ ] Meta description correct (shows in browser tab on hover, used by Google)
- [ ] OG tags correct (test with opengraph.xyz — paste the URL)
- [ ] No builder badge scripts in page source (View Source → search "bolt.new" / "lovable")
- [ ] Lighthouse score: Performance ≥ 75, Accessibility ≥ 80 (run in Chrome DevTools)

### GHL Integration Checks (run after widgets are connected)
- [ ] Submit test form → contact appears in CRM → follow-up SMS fires → task created
- [ ] Call business number → let ring → miss it → text-back fires within 60 seconds
- [ ] Book test appointment → confirmation SMS fires → calendar shows appointment
- [ ] Move test contact to "Job Completed" → review request SMS fires after 2 hours
- [ ] Chat widget visible on site → submit test chat → appears in GHL inbox
- [ ] Voice AI inline widget renders between hero and trust bar (after Labs setup)

### Analytics Setup
- [ ] GA4 tracking code installed (paste in index.html <head>) — confirms traffic
- [ ] Google Search Console: site verified, sitemap submitted
- [ ] GBP UTM tracking: links from GBP to site use ?utm_source=gbp

---

## SECTION 12 — DOMAIN CUTOVER SOP
*~30 minutes + 24–48 hours DNS propagation*

> **"Point client's domain to Netlify" was a one-liner in v2. It is not a one-liner.**
> Follow this full procedure to avoid client downtime and missed calls.

**Before starting:**
- [ ] Confirm client owns the domain (has registrar login credentials)
- [ ] **Lower DNS TTL 24–48 hours BEFORE cutover day:**
      Log into the registrar NOW → find the current A/CNAME record → change TTL
      from default (typically 3600–86400 seconds) down to **300 seconds (5 minutes)**.
      This means if something goes wrong during cutover, a revert propagates in
      5 minutes instead of 24 hours. After the new site is confirmed live and stable
      for 48 hours, raise TTL back to 3600.
- [ ] Check current DNS: whatsmydns.net → enter domain → see current nameservers/records
- [ ] Note current A/CNAME record (save it — you may need to revert)
- [ ] Warn client: DNS changes take 24–48 hours to propagate globally
      Tell them: "Your site may be briefly unreachable during this window — plan accordingly"
- [ ] Schedule cutover for a low-traffic time (Tuesday–Thursday, 10am–2pm recommended)

**Steps:**

- [ ] In Netlify: Site Settings → Domain Management → Add Custom Domain → enter client domain
- [ ] Netlify shows the DNS records to add — note them

- [ ] In client's registrar (GoDaddy, Namecheap, Google Domains, etc.):
  - [ ] Go to DNS Management for the domain
  - [ ] For APEX domain (example.com):
        Add/update A record → IP address provided by Netlify
        OR add ALIAS/ANAME record → [site].netlify.app (if registrar supports ALIAS)
  - [ ] For www subdomain (www.example.com):
        Add/update CNAME record → [site].netlify.app
  - [ ] Save changes

- [ ] Wait 30 minutes, then check propagation: whatsmydns.net
- [ ] Netlify automatically provisions SSL (HTTPS) after DNS propagates — this takes 1–5 minutes
- [ ] Verify: open https://[client-domain] — confirms SSL active, site loads correctly

**Common registrar-specific notes:**
  GoDaddy: DNS → Manage → Update A record (TTL: 600 recommended)
  Namecheap: Advanced DNS → Host Records → update A + CNAME
  Google Domains: DNS → Custom Records
  Squarespace: Domains → DNS → Advanced Settings (may need to disconnect their builder first)

- [ ] After SSL confirmed: test all forms, tap-to-call, and GHL widgets on custom domain
- [ ] Update GBP: change the website link from old URL to new custom domain
- [ ] Update any GHL subaccount settings that reference the old URL

**Rollback procedure (if something goes wrong):**
  Restore original A record in registrar → old site reappears within 1–2 hours
  Contact client immediately if rollback is needed

---

## SECTION 13 — CLIENT HANDOFF
*~1 hour*

- [ ] Walk client through their GHL dashboard (15-minute video call or screen share)
- [ ] Show them: how leads appear, how to move pipeline stages, how to see reviews
- [ ] Set up their GHL mobile app (they can respond to chats on their phone)
- [ ] Send 1-page "How to use your new system" PDF — written in plain language
- [ ] Schedule 2-week check-in call to review performance
- [ ] Get testimonial request ready (send at the 30-day mark, not the day of handoff)

---

## MONTHLY MAINTENANCE CHECKLIST (retainer clients)
*~1–2 hours/month per client — batch all clients on one day per week*

- [ ] Pipeline audit: any leads stuck > 7 days? Alert client
- [ ] Workflow logs: GHL → Automation → Workflows → [workflow] → Logs tab
      Look for: failed sends, unresolved merge fields, stuck contacts
- [ ] New Google reviews: respond to all in GBP within 48 hours
- [ ] GBP listing: any Google-suggested edits? New Q&A to answer?
- [ ] Website: broken links? Outdated seasonal content?
- [ ] Pull monthly report: GHL → Reporting → new leads, bookings, reviews, missed calls
- [ ] Send client 1-paragraph update with those numbers
- [ ] SerpApi plan check: if running >10 extractions/day, verify on paid plan ($50–75/month Basic)
      Free tier rate limits will silently fail at agency volume

---

## COST STRUCTURE (updated from peer review)
*Correct cost model per client at different scale points*

**GHL platform (per client share):**

| Active Clients | GHL Share | + SMS Usage | Total Platform COGS |
|---|---|---|---|
| 3 clients | ~$99–$166 | ~$10–15 | ~$109–$181 |
| 5 clients | ~$60–$99 | ~$10–15 | ~$70–$114 |
| 10 clients | ~$30–$50 | ~$10–15 | ~$40–$65 |
| 20 clients | ~$15–$25 | ~$10–15 | ~$25–$40 |

*Range reflects Unlimited ($297) vs SaaS Pro ($497) plan.*

**Voice AI clients (Package 3) — additional costs:**
- GHL AI Employee: $97/month per sub-account (required for full Voice AI features)
- LC Phone usage: per-SMS and per-minute charges (pass through to client via SaaS Mode re-billing)
- Corrected Package 3 COGS: ~$130–$180/month minimum (not $57 as previously stated)
- Margin at $497 retainer: still strong, but ~60–65% not ~85%

**Enable SaaS Mode re-billing before first client goes live.**
Without it, high-volume client months hit your agency bill directly.

**SerpApi:** Free tier sufficient for < 5 extractions/day.
At agency volume (10+ prospects/day), upgrade to SerpApi Basic: ~$50–75/month.
Add to agency overhead budget, not per-client COGS.

---

## CLIENT OFFBOARDING (when retainer cancels)

- [ ] Export contacts: GHL → Contacts → Export CSV → send to client
- [ ] Transfer domain (if registered for them): point nameservers to their new host
- [ ] GHL-native sites: cannot be exported to other platforms — disclose this at onboarding
- [ ] Archive sub-account: do NOT delete for 90 days minimum
- [ ] Cancel any integrations specific to this client (bit.ly links, Google Workspace)
- [ ] Send offboarding summary with exported data and next steps

---

*v3 — Updated March 2026 per 5-LLM peer review. Next review: when first client completes 90 days.*
