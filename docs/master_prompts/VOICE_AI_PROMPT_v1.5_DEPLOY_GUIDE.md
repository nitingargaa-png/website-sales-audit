# Voice AI Prompt — v1.5 Deployment Guide
## Universal Template — 22 Niches
## Supersedes: v1.4 Changes Document (April 2026)

This document explains how to deploy the Universal Voice AI Agent Prompt Template v1.5
into a new GHL client sub-account. The v1.5 prompt is a complete, self-contained template
— it replaces and supersedes all previous v1.3 and v1.4 patch notes.

**The v1.5 prompt already includes all fixes that were planned for v1.4:**
- ✅ AI disclosure + call recording disclosure (Section 2.1, 2.3) — hardcoded as first line
- ✅ Address and phone number digit-by-digit TTS (Section 11.1)
- ✅ Voicemail detection for outbound calls (Section 10.17)
- ✅ Emergency escalation with 911 life-safety override (Section 2.7)
- ✅ Emergency per-niche triggers (Section 6.3)
- ✅ Billing/complaint handler with closure line (Section 10.13)
- ✅ Universal System Fallback for any tool failure (Section 10.19)
- ✅ Business hours workflow gating via is_business_hours custom value (Section 4.2)
- ✅ Availability framing custom value — no hardcoded same-day promise (Section 5.3)

Do NOT apply any v1.4 patch notes separately — v1.5 includes everything.

---

## STEP 1 — WHAT TO SWAP PER CLIENT (AMBER SECTIONS)

The template has 14 sections. FIXED sections do not change. SWAP sections change per client:

| Section | What to swap |
|---|---|
| S1.1 | Replace [AGENT_NAME]. Keep ONE niche restriction line — delete other 21 |
| S5.1 | Confirm primary objective matches client workflow |
| S5.2 | DELETE two of three booking mode lines — leave only the one that applies |
| S6.1 | Review call type definitions — adjust escalation thresholds if needed |
| S6.3 | Keep ONE niche emergency trigger block — delete other 21 |
| S7.2 | Trust line and qualification questions already set per niche (Section 8) |
| S7.3 | Quote flow qualification — add niche questions from Section 8 |
| S7.4 | After-hours flow — verify callback framing matches client preference |
| S8.1 | Keep ONE niche qualification block — delete other 21 |

---

## STEP 2 — CUSTOM VALUES TO CREATE IN GHL BEFORE DEPLOYING

The v1.5 prompt references 10 Custom Values. All must be created in GHL Settings →
Custom Values BEFORE pasting the prompt. If any are missing, the agent reads them
as blank text — potentially aloud to callers.

| Custom Value Key | Type | Default Value | Notes |
|---|---|---|---|
| business_name | Text | [Client Business Name] | Required — agent uses in greeting |
| business_phone | Text | [Client Phone] | For callback references |
| business_address | Text | [Client Address] | Service area context |
| service_area | Text | [City, Neighborhoods] | Used in Section 9.11 area check |
| owner_callback_time | Text | as soon as possible | Used in emergency + after-hours flows |
| is_business_hours | Text | false | ⚠ SET BY WORKFLOW — not manually. Must exist before workflow can write to it. Default 'false' = safe (after-hours behaviour until workflow sets correctly) |
| availability_framing | Text | In most cases we can get someone out the same day. | Swap during busy periods — see S5.3 |
| sms_active | Text | FALSE | Toggle to TRUE after A2P approval only |
| emergency_available | Text | yes | yes/no — referenced in after-hours flow |
| owner_callback_time | Text | as soon as possible | Short-form — do NOT use {{owner_callback_time}} shorthand |

**Two new Custom Values added in v1.5 vs previous setup:**
- `is_business_hours` — must be created AND set by a GHL workflow trigger (time-based)
- `availability_framing` — replaces any hardcoded same-day promise in the prompt

---

## STEP 3 — BUSINESS HOURS WORKFLOW (REQUIRED BEFORE GO-LIVE)

v1.5 moves all business hours gating OUT of the prompt and into a GHL workflow.
The prompt cannot check the time reliably — this was a known failure mode in v1.3.

**Build this workflow before deploying any client:**

```
Trigger: Inbound Call Received (or call routes to Voice AI agent)

Branch A — Within business hours:
  Action: Set Custom Value → is_business_hours = true
  Then: Route call to Voice AI agent

Branch B — Outside business hours:
  Action: Set Custom Value → is_business_hours = false
  Then: Route call to Voice AI agent

The agent reads {{custom_values.is_business_hours}} at the start of Section 4
and branches to standard flow (true) or after-hours flow (false).
```

**Critical:** Create the `is_business_hours` custom value FIRST (Step 2 above).
Without it existing, the workflow write will fail silently.

**Test both paths explicitly:** Force the value to 'true', make a test call.
Force to 'false', make another. Confirm correct routing both times.

---

## STEP 4 — POST-CALL WORKFLOW (M-C1)

The v1.5 prompt references post-call automation in Section 12.3.
M-C1 is NOT a native GHL feature — it must be built and published as a custom workflow.

**Recommended M-C1 structure (race condition fix applied):**

```
Trigger: Transcript Generated (preferred) OR Call Status = Completed + Wait 60 seconds

PATH A — fires immediately on call end:
  → Add Tag: ai-voice-lead (or niche-specific tag)
  → Create Opportunity: AI Lead Pipeline, Stage 1
  → Internal Notification to owner (no merge fields — just "New Voice AI call received")

PATH B — fires on Transcript Generated trigger:
  → Add Note: {{call.summary}} and {{call.transcript}}
  → Second internal notification with summary (optional)
```

Use the "Transcript Generated" trigger for PATH B to avoid the race condition where
summary merge fields are blank at call-end time.

---

## STEP 5 — FINAL QA BEFORE GO-LIVE

Run the full test matrix from the v1.5 Appendix Step 10. Minimum required tests:

- [ ] Business hours standard booking — confirm is_business_hours = true routing
- [ ] After-hours non-emergency — confirm is_business_hours = false routing
- [ ] Emergency call — confirm niche trigger fires, owner notified immediately
- [ ] Life-safety scenario (gas smell / electric shock) — confirm 911 redirect fires (S2.7)
- [ ] Pricing objection — confirm 3-push sequence, then owner callback offer
- [ ] "Speak to a real person" — confirm transfer fires + failure fallback
- [ ] Phone/address read-back — confirm digit-by-digit (S11.1)
- [ ] Booking action success — confirm verbal confirmation AFTER system confirms
- [ ] Booking action failure — confirm switch to Universal System Fallback (S10.19)
- [ ] Billing/complaint caller — confirm capture + closure line with callback timeframe

After all tests pass: re-export GHL snapshot as AI Agent System v4.4.

---

## VERSION LOG

| Version | Date | Changes |
|---|---|---|
| v1.3 | March 2026 | Initial 11-section structure; garage door niche |
| v1.4 | April 2026 | Planned patch (recording disclosure, TTS fix, voicemail, emergency escalation) |
| v1.5 | April 2026 | Universal 14-section template; 22 niches; 57 total fixes; business hours workflow gating; availability framing; life-safety 911 override; Universal System Fallback; v1.4 patches incorporated and superseded |
