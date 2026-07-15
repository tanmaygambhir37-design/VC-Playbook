"""
pdf_report.py — Investment Memo PDF Export

Renders the same data shown on the Investment Memo page (score, valuation,
mocked AI due-diligence narrative, and next steps) into a formatted PDF using
reportlab, styled like an investment-committee document. The screen and the
PDF are built from the same inputs so they never drift out of sync.
"""

import io

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

NAVY = colors.HexColor("#111827")
BODY_INK = colors.HexColor("#1F2937")
BLUE = colors.HexColor("#2563EB")
MUTED = colors.HexColor("#64748B")
BORDER = colors.HexColor("#E2E8F0")
WHITE = colors.white

RECOMMENDATION_COLORS = {
    "Proceed": colors.HexColor("#10B981"),
    "Watch": colors.HexColor("#F59E0B"),
    "Pass": colors.HexColor("#EF4444"),
}

_styles = getSampleStyleSheet()

TITLE = ParagraphStyle("VCLTitle", parent=_styles["Title"], fontName="Helvetica-Bold",
                        fontSize=23, leading=27, textColor=NAVY, spaceAfter=2, alignment=0)
EYEBROW = ParagraphStyle("VCLEyebrow", parent=_styles["Normal"], fontName="Helvetica-Bold",
                          fontSize=8.5, textColor=BLUE, leading=11, spaceAfter=6)
META = ParagraphStyle("VCLMeta", parent=_styles["Normal"], fontName="Helvetica",
                       fontSize=9.5, textColor=MUTED, spaceAfter=14)
HEADING = ParagraphStyle("VCLHeading", parent=_styles["Heading2"], fontName="Helvetica-Bold",
                          fontSize=11.5, textColor=NAVY, spaceBefore=14, spaceAfter=5)
BODY = ParagraphStyle("VCLBody", parent=_styles["Normal"], fontName="Helvetica",
                       fontSize=9.6, leading=14, textColor=BODY_INK)
SOURCE = ParagraphStyle("VCLSource", parent=_styles["Normal"], fontName="Helvetica-Oblique",
                         fontSize=7.8, textColor=MUTED, spaceBefore=3, spaceAfter=2)
BULLET = ParagraphStyle("VCLBullet", parent=BODY, leftIndent=10, spaceAfter=3)


def _footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 7.3)
    canvas.setFillColor(MUTED)
    canvas.drawString(
        0.75 * inch, 0.5 * inch,
        "VC Playbook · Confidential — illustrative analysis for demonstration purposes only. Not investment advice.",
    )
    canvas.drawRightString(LETTER[0] - 0.75 * inch, 0.5 * inch, f"Page {doc.page}")
    canvas.restoreState()


def _recommendation_banner(recommendation: str, vc_score: float) -> Table:
    color = RECOMMENDATION_COLORS.get(recommendation, MUTED)
    label = f"{recommendation.upper()}  ·  VC SCORE {vc_score:.1f}/100"
    style = ParagraphStyle("BannerText", fontName="Helvetica-Bold", fontSize=13,
                            textColor=WHITE, alignment=TA_CENTER)
    table = Table([[Paragraph(label, style)]], colWidths=[6.5 * inch], rowHeights=[0.42 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    return table


def _metric_row(pairs: list) -> Table:
    n = len(pairs)
    width = 6.5 * inch / n
    value_style = ParagraphStyle("MValue", fontName="Helvetica-Bold", fontSize=12, textColor=NAVY)
    label_style = ParagraphStyle("MLabel", fontName="Helvetica", fontSize=7.2, textColor=MUTED)
    values = [Paragraph(v, value_style) for _, v in pairs]
    labels = [Paragraph(l.upper(), label_style) for l, _ in pairs]
    table = Table([values, labels], colWidths=[width] * n)
    table.setStyle(TableStyle([
        ("TOPPADDING", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 2),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 10),
        ("LINEBELOW", (0, 1), (-1, 1), 0.75, BORDER),
    ]))
    return table


def _narrative_section(section) -> list:
    flow = [Paragraph(section.title.upper(), HEADING), Paragraph(section.paragraph, BODY)]
    meta_bits = [f"Confidence: {section.confidence}"]
    if section.sources:
        meta_bits.append("Sources: " + ", ".join(section.sources))
    flow.append(Paragraph("   ·   ".join(meta_bits), SOURCE))
    return flow


def build_memo_pdf(row: dict, result, valuation: dict, narrative_sections: list,
                    risk_bullets: list, confidence_section, next_steps: list) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=LETTER,
        topMargin=0.75 * inch, bottomMargin=0.85 * inch,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
        title=f"{row['company']} Investment Memo",
    )

    ltv_cac = round(row["ltv_usd"] / row["cac_usd"], 2) if row["cac_usd"] else 0

    story = [
        Paragraph("CONFIDENTIAL &nbsp;·&nbsp; INVESTMENT COMMITTEE MEMO", EYEBROW),
        Paragraph(row["company"], TITLE),
        Paragraph(f"{row['sector']} &nbsp;·&nbsp; {row['stage']} &nbsp;·&nbsp; Prepared by VC Playbook", META),
        _recommendation_banner(result.recommendation, result.total),
        Spacer(1, 12),
        _metric_row([
            ("VC Score", f"{result.total}/100"),
            ("Recommendation", result.recommendation),
            ("LTV : CAC", f"{ltv_cac}x"),
            ("Adjusted Valuation", f"${valuation['adjusted_valuation']}M"),
        ]),
        Spacer(1, 8),
    ]

    for section in narrative_sections:
        story.extend(_narrative_section(section))

    story.append(Paragraph("RISKS &amp; RED FLAGS", HEADING))
    for bullet in risk_bullets:
        story.append(Paragraph(f"•&nbsp; {bullet}", BULLET))
    story.append(Spacer(1, 6))

    story.append(Paragraph("FINANCIAL SNAPSHOT", HEADING))
    story.append(_metric_row([
        ("Revenue (ARR)", f"${row['revenue_usd_k']:.0f}k"),
        ("MoM Growth", f"{row['mom_growth_pct']:.1f}%"),
        ("Monthly Burn", f"${row['monthly_burn_usd_k']:.0f}k"),
        ("Runway", f"{row['runway_months']:.0f} mo"),
        ("Team Size", f"{row['team_size']}"),
    ]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("VALUATION SUMMARY", HEADING))
    story.append(_metric_row([
        ("Raw ARR-Multiple Valuation", f"${valuation['raw_valuation']}M"),
        ("Illiquidity Discount", f"{valuation['illiquidity_discount_pct']:.0f}%"),
        ("Adjusted Valuation", f"${valuation['adjusted_valuation']}M"),
    ]))
    story.append(Spacer(1, 8))

    story.extend(_narrative_section(confidence_section))

    story.append(Paragraph("NEXT STEPS", HEADING))
    for i, step in enumerate(next_steps, start=1):
        story.append(Paragraph(f"{i}.&nbsp; {step}", BULLET))

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return buffer.getvalue()
