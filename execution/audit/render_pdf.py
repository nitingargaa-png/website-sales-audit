"""
render_pdf.py — one-page branded PDF. The lead magnet artifact.

reportlab chosen over weasyprint: weasyprint needs GTK on Windows, which is a
known pain path on this box. reportlab is pure Python.

ONE PAGE. Two practitioners said it unprompted: a one-page summary beats a
20-page report every time. If content overflows, cut findings — never spill
to page 2.
"""
import datetime as dt
import os
from typing import Dict, Any, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                               TableStyle, PageBreak)

from . import checklist
from .score import AREA_LABELS, BAND_LABEL

NAVY = colors.HexColor("#1B2A4A")
RED = colors.HexColor("#C0392B")
AMBER = colors.HexColor("#D68910")
GREEN = colors.HexColor("#1E8449")
GREY = colors.HexColor("#6B7280")

BAND_COLOR = {"red": RED, "yellow": AMBER, "green": GREEN}


def _styles(agency_name: str):
    ss = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("t", parent=ss["Heading1"], fontSize=17,
                                textColor=NAVY, spaceAfter=2, leading=20),
        "sub": ParagraphStyle("s", parent=ss["Normal"], fontSize=8.5,
                              textColor=GREY, spaceAfter=10),
        "h": ParagraphStyle("h", parent=ss["Heading2"], fontSize=10.5,
                            textColor=NAVY, spaceBefore=9, spaceAfter=4),
        "h2": ParagraphStyle("h2", parent=ss["Heading2"], fontSize=8.5,
                             textColor=NAVY, spaceBefore=5, spaceAfter=2),
        "body": ParagraphStyle("b", parent=ss["Normal"], fontSize=8.8,
                               leading=11.5, spaceAfter=3),
        "small": ParagraphStyle("sm", parent=ss["Normal"], fontSize=7.2,
                                textColor=GREY, leading=9),
        "score": ParagraphStyle("sc", parent=ss["Heading1"], fontSize=26,
                                alignment=1, spaceAfter=1),
        "band": ParagraphStyle("bd", parent=ss["Normal"], fontSize=9,
                               alignment=1, textColor=GREY),
    }


def _fmt(rng, unit="", dp=1) -> str:
    if not rng:
        return "not measured"
    lo, hi = rng
    if abs(hi - lo) < (0.05 if dp == 1 else 0.005):
        return f"{lo:.{dp}f}{unit}"
    return f"{lo:.{dp}f}–{hi:.{dp}f}{unit}"


def render(path: str, url: str, m: Dict[str, Any], psi: Dict[str, Any],
           verdicts: Dict[str, Optional[str]], sc: Dict[str, Any],
           judged: Optional[Dict[str, Any]],
           agency_name: str = "Animo Automation",
           agency_contact: str = "") -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    st = _styles(agency_name)
    name = (judged or {}).get("business_name") or url
    band_name = sc.get("band")
    score = sc.get("site_score")

    doc = SimpleDocTemplate(
        path, pagesize=letter,
        leftMargin=0.7 * inch, rightMargin=0.7 * inch,
        topMargin=0.6 * inch, bottomMargin=0.55 * inch,
        title=f"Website Review — {name}", author=agency_name)

    el = []
    el.append(Paragraph(f"Website Review: {name}", st["title"]))
    el.append(Paragraph(
        f"{url} &nbsp;·&nbsp; Reviewed {dt.date.today().strftime('%d %B %Y')}",
        st["sub"]))

    # --- score block ---
    if score is not None:
        sty = ParagraphStyle("sc2", parent=st["score"],
                             textColor=BAND_COLOR.get(band_name, NAVY))
        el.append(Paragraph(f"{score}<font size=13>/100</font>", sty))
        label = BAND_LABEL.get(band_name, "").split(" ", 1)
        el.append(Paragraph(label[1] if len(label) > 1 else "", st["band"]))
        if sc.get("renormalised"):
            missing = ", ".join(AREA_LABELS[k].lower() for k in sc["unscored"])
            el.append(Paragraph(f"({missing} not measured)", st["small"]))
    el.append(Spacer(1, 10))

    # --- measured table ---
    el.append(Paragraph("What we measured", st["h"]))
    rows = [["", "Your site", "Target", ""]]

    if psi.get("measured"):
        rows.append(["Loading speed (phone)", _fmt(psi.get("lcp_s"), "s"),
                     "under 2.5s", verdicts.get("lcp") or "—"])
        if psi.get("inp_ms"):
            rows.append(["Responsiveness", _fmt(psi["inp_ms"], "ms", 0),
                         "under 200ms", verdicts.get("inp") or "—"])
        rows.append(["Layout stability", _fmt(psi.get("cls"), "", 2),
                     "under 0.1", verdicts.get("cls") or "—"])
    else:
        rows.append(["Loading speed (phone)", "not measured", "under 2.5s", "—"])

    rows.append(["Secure connection", "Yes" if m["https"] else "No",
                 "Yes", "PASS" if m["https"] else "FAIL"])
    if m.get("tel_js_only"):
        rows.append(["Tap-to-call on phone", "Only after scripts run",
                     "Always", "FAIL"])
    else:
        rows.append(["Tap-to-call on phone", "Yes" if m["tel_href"] else "No",
                     "Yes", "PASS" if m["tel_href"] else "FAIL"])
    if m.get("title_len"):
        rows.append(["Page title length", f"{m['title_len']} chars",
                     "55–60", "PASS" if m["title_ok"] else "FAIL"])
    else:
        rows.append(["Page title", "missing", "55–60", "FAIL"])
    rows.append(["Business info for Google",
                 "Present" if m["localbusiness_jsonld"] else "Missing",
                 "Present", "PASS" if m["localbusiness_jsonld"] else "FAIL"])

    t = Table(rows, colWidths=[2.3 * inch, 1.5 * inch, 1.2 * inch, 0.6 * inch])
    tstyle = [
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TEXTCOLOR", (0, 0), (-1, 0), GREY),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.HexColor("#E5E7EB")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#F9FAFB")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for i, r in enumerate(rows[1:], 1):
        if r[3] == "FAIL":
            tstyle.append(("TEXTCOLOR", (3, i), (3, i), RED))
            tstyle.append(("FONTNAME", (3, i), (3, i), "Helvetica-Bold"))
        elif r[3] == "PASS":
            tstyle.append(("TEXTCOLOR", (3, i), (3, i), GREEN))
    t.setStyle(TableStyle(tstyle))
    el.append(t)

    if psi.get("measured"):
        src = "real visitor data" if psi["source"] == "field" else "simulated test"
        lcp = psi.get("lcp_s")
        # Only boast about a range when there IS one. On 2026-07-16 the report
        # said "Speed varies between tests, so we show the range" next to
        # "25.0–25.0s" from 2 runs — one call had timed out and the other two
        # agreed exactly. Claiming a range you aren't showing undercuts the
        # credibility the sentence exists to build.
        spread = (lcp[1] - lcp[0]) if lcp else 0
        note = (" Speed varies between tests, so we show the range."
                if spread >= 0.15 else "")
        el.append(Spacer(1, 3))
        el.append(Paragraph(
            f"Source: Google PageSpeed Insights · {src} · "
            f"{psi['runs_ok']} run{'s' if psi['runs_ok'] != 1 else ''} · "
            f"{dt.date.today().isoformat()}.{note}", st["small"]))

    # --- findings ---
    if judged and judged.get("top_findings"):
        el.append(Paragraph("The three things costing you most", st["h"]))
        for i, f in enumerate(judged["top_findings"][:3], 1):
            el.append(Paragraph(
                f"<b>{i}. {f.get('evidence','')}</b>", st["body"]))
            el.append(Paragraph(
                f"&nbsp;&nbsp;&nbsp;{f.get('impact','')}", st["body"]))
            el.append(Paragraph(
                f"&nbsp;&nbsp;&nbsp;<i>Fix: {f.get('fix','')}</i>", st["body"]))

    if judged and judged.get("working"):
        el.append(Paragraph("What's working", st["h"]))
        for w in judged["working"][:3]:
            el.append(Paragraph(f"• {w}", st["body"]))

    el.append(Spacer(1, 8))
    el.append(Paragraph(
        f"<font color='#6B7280'>Prepared by {agency_name}"
        + (f" · {agency_contact}" if agency_contact else "") + "</font>",
        st["small"]))

    # ================= PAGE 2 — everything we checked =====================
    # Page 1 is the pitch (practitioner advice: "a one-page summary beats a
    # 20-page report every time"). Page 2 is the evidence you point at when
    # the owner asks "how did you get 1/5?". Deliberately separate.
    cl = checklist.build(m, psi, verdicts)
    el.append(PageBreak())
    el.append(Paragraph("Everything we checked", st["title"]))
    el.append(Paragraph(
        f"{name} · {url}", st["sub"]))

    mark_style = {
        checklist.PASS: (GREEN, "PASS"),
        checklist.FAIL: (RED, "NEEDS WORK"),
        checklist.WARN: (AMBER, "CHECK"),
        checklist.NOT_CHECKED: (GREY, "NOT CHECKED"),
    }

    for title, key in checklist.GROUPS:
        items = cl.get(key, [])
        if not items:
            continue
        p, f, n = checklist.counts(items)
        el.append(Paragraph(
            f"{title} <font size=6.5 color='#6B7280'>"
            f"({p} passed · {f} need work · {n} not checked)</font>", st["h2"]))

        rows = []
        for label, status, detail in items:
            colr, word = mark_style.get(status, (GREY, status))
            txt = label
            if detail:
                txt += f" <font size=6.5 color='#6B7280'>— {detail}</font>"
            rows.append([Paragraph(txt, st["body"]),
                         Paragraph(f"<font color='#{colr.hexval()[2:]}'>"
                                   f"<b>{word}</b></font>", st["small"])])
        t = Table(rows, colWidths=[5.15 * inch, 1.05 * inch])
        t.setStyle(TableStyle([
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 1.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
            ("LINEBELOW", (0, 0), (-1, -2), 0.25,
             colors.HexColor("#F0F0F0")),
        ]))
        el.append(t)

    el.append(Spacer(1, 4))
    el.append(Paragraph(
        "<b>NOT CHECKED</b> means we could not judge it from outside your "
        "website. Button sizes, photo quality, and overall look need a person "
        "to open the site on a real phone — we have not guessed at them.",
        st["small"]))

    doc.build(el)
    return path
