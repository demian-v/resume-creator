#!/usr/bin/env python3
"""
Convert a resume markdown file (following resume-creator skill format) into a styled PDF.

Setup (one-time):
    python3 -m venv .venv && .venv/bin/pip install reportlab --quiet

Usage:
    .venv/bin/python generate_resume_pdf.py --source resume-ats.md --output resume.pdf
"""

import argparse
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


AVAILABLE_WIDTH = LETTER[0] - 0.7 * inch - 0.7 * inch


def escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def normalize_inline_markdown(text: str) -> str:
    text = escape(text.strip())
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<link href="\2" color="navy">\1</link>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    return text


def parse_resume(markdown_text: str) -> dict:
    """
    Parse resume markdown into structured data.

    Supported sections: Professional Summary, Areas of Expertise,
    Professional Experience, Certifications.

    Experience entries:
      - Company:      ### Company Name
      - Main role:    **Job Title** | dates | location
      - Sub-project:  #### Project Name | dates
      - Bullet:       - bullet text
    """
    lines = markdown_text.splitlines()
    data = {
        "name": "",
        "contact_lines": [],
        "summary": [],
        "expertise": "",
        "experience": [],
        "certifications": [],
    }

    current_section = None
    current_company = None
    current_role = None

    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()

        if i == 0 and stripped.startswith("# "):
            data["name"] = stripped[2:].strip()
            i += 1
            while i < len(lines) and lines[i].strip():
                data["contact_lines"].append(lines[i].strip())
                i += 1
            continue

        if stripped.startswith("## "):
            current_section = stripped[3:].strip()
            current_company = None
            current_role = None
            i += 1
            continue

        if current_section == "Professional Summary":
            if stripped:
                data["summary"].append(stripped)
            i += 1
            continue

        if current_section == "Areas of Expertise":
            if stripped:
                data["expertise"] = stripped
            i += 1
            continue

        if current_section == "Professional Experience":
            if stripped.startswith("### "):
                current_company = {"company": stripped[4:].strip(), "entries": []}
                data["experience"].append(current_company)
                current_role = None
                i += 1
                continue

            if stripped.startswith("#### "):
                sub_parts = stripped[5:].strip().split("|", 1)
                if current_company is not None:
                    current_role = {
                        "role": sub_parts[0].strip(),
                        "meta": sub_parts[1].strip() if len(sub_parts) > 1 else "",
                        "bullets": [],
                        "is_subproject": True,
                    }
                    current_company["entries"].append(current_role)
                i += 1
                continue

            if stripped.startswith("**") and stripped.endswith("**") is False:
                role_line = re.match(r"^\*\*(.+?)\*\*\s*\|\s*(.+)$", stripped)
                if role_line and current_company is not None:
                    current_role = {
                        "role": role_line.group(1).strip(),
                        "meta": role_line.group(2).strip(),
                        "bullets": [],
                        "is_subproject": False,
                    }
                    current_company["entries"].append(current_role)
                i += 1
                continue

            if stripped.startswith("- ") and current_role is not None:
                current_role["bullets"].append(stripped[2:].strip())
                i += 1
                continue

            i += 1
            continue

        if current_section == "Certifications":
            if stripped.startswith("- "):
                data["certifications"].append(stripped[2:].strip())
            i += 1
            continue

        i += 1

    return data


def build_pdf(data: dict, output_path: Path) -> None:
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=LETTER,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.6 * inch,
        title=f"{data['name']} Resume",
        author=data["name"],
    )

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ResumeName",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=25,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#111111"),
            spaceAfter=3,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ResumeTitle",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=13.5,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#1F2937"),
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ResumeContact",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.4,
            leading=12.5,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#6B7280"),
            spaceAfter=0,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionTitle",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11.6,
            leading=14,
            alignment=TA_LEFT,
            textColor=colors.HexColor("#16324F"),
            spaceBefore=11,
            spaceAfter=2,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SummaryResume",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            alignment=TA_LEFT,
            textColor=colors.black,
            spaceAfter=2,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CompanyStyle",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=10.9,
            leading=13.2,
            textColor=colors.HexColor("#111827"),
            spaceBefore=7,
            spaceAfter=2,
        )
    )
    styles.add(
        ParagraphStyle(
            name="RoleMetaStyle",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=11.8,
            textColor=colors.black,
            spaceBefore=2,
            spaceAfter=1,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BulletStyle",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.3,
            leading=12,
            leftIndent=0,
            firstLineIndent=0,
            textColor=colors.black,
            spaceAfter=0,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SubProjectStyle",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.4,
            leading=11.6,
            textColor=colors.black,
            spaceBefore=5,
            spaceAfter=1,
        )
    )
    styles.add(
        ParagraphStyle(
            name="AoECell",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=11.8,
            leftIndent=0,
            firstLineIndent=0,
            textColor=colors.black,
            spaceAfter=0,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CertStyle",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8.9,
            leading=10.6,
            leftIndent=0,
            firstLineIndent=0,
            textColor=colors.black,
            spaceAfter=0,
        )
    )

    story = []

    story.append(Paragraph(escape(data["name"]), styles["ResumeName"]))
    if data["contact_lines"]:
        story.append(Paragraph(
            normalize_inline_markdown(data["contact_lines"][0]),
            styles["ResumeTitle"],
        ))
    for contact_line in data["contact_lines"][1:]:
        story.append(Paragraph(normalize_inline_markdown(contact_line), styles["ResumeContact"]))

    story.append(Spacer(1, 5))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#9AA5B1")))
    story.append(Spacer(1, 5))

    def add_section(title: str):
        story.append(Paragraph(escape(title.upper()), styles["SectionTitle"]))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#D1D5DB")))
        story.append(Spacer(1, 4))

    add_section("Professional Summary")
    for summary_line in data["summary"]:
        story.append(Paragraph(normalize_inline_markdown(summary_line), styles["SummaryResume"]))
    story.append(Spacer(1, 1))

    add_section("Areas of Expertise")
    expertise_items = [s.strip() for s in data["expertise"].split("|") if s.strip()]
    rows = []
    for i in range(0, len(expertise_items), 4):
        chunk = expertise_items[i:i + 4]
        while len(chunk) < 4:
            chunk.append("")
        rows.append([
            Paragraph("• " + escape(cell) if cell else "", styles["AoECell"])
            for cell in chunk
        ])

    col_w = AVAILABLE_WIDTH / 4
    tbl = Table(rows, colWidths=[col_w] * 4, hAlign="LEFT")
    tbl.setStyle(TableStyle([
        ("FONTNAME",      (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9.3),
        ("ALIGN",         (0, 0), (-1, -1), "LEFT"),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("TOPPADDING",    (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 2))

    add_section("Professional Experience")
    for company in data["experience"]:
        story.append(Paragraph(escape(company["company"]), styles["CompanyStyle"]))
        for entry in company["entries"]:
            role_meta = f"<b>{escape(entry['role'])}</b>"
            if entry["meta"]:
                role_meta += f' <font color="#6B7280">| {escape(entry["meta"])}</font>'
            if entry.get("is_subproject"):
                story.append(Paragraph(role_meta, styles["SubProjectStyle"]))
            else:
                story.append(Paragraph(role_meta, styles["RoleMetaStyle"]))
            bullet_items = [
                ListItem(Paragraph(normalize_inline_markdown(bullet), styles["BulletStyle"]))
                for bullet in entry["bullets"]
            ]
            if bullet_items:
                story.append(
                    ListFlowable(
                        bullet_items,
                        bulletType="bullet",
                        start="circle",
                        leftPadding=14,
                        bulletFontName="Helvetica",
                        bulletFontSize=7,
                        bulletColor=colors.HexColor("#16324F"),
                        spaceBefore=3,
                        spaceAfter=4,
                    )
                )
            else:
                story.append(Spacer(1, 1))

    add_section("Certifications")
    if data["certifications"]:
        cert_items = [
            ListItem(Paragraph(normalize_inline_markdown(item), styles["CertStyle"]))
            for item in data["certifications"]
        ]
        story.append(
            ListFlowable(
                cert_items,
                bulletType="bullet",
                start="circle",
                leftPadding=14,
                bulletFontName="Helvetica",
                bulletFontSize=6.5,
                bulletColor=colors.HexColor("#16324F"),
                spaceBefore=0,
                spaceAfter=0,
            )
        )

    def add_page_number(canvas, doc_obj):
        page_num = canvas.getPageNumber()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#6B7280"))
        canvas.drawRightString(
            doc_obj.pagesize[0] - doc_obj.rightMargin,
            0.35 * inch,
            f"Page {page_num}",
        )

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert resume markdown to PDF")
    parser.add_argument("--source", default="resume-ats.md", help="Input markdown file")
    parser.add_argument("--output", default="resume.pdf", help="Output PDF file")
    args = parser.parse_args()

    source = Path(args.source)
    if not source.exists():
        print(f"Error: source file not found: {source}")
        raise SystemExit(1)

    data = parse_resume(source.read_text(encoding="utf-8"))
    build_pdf(data, Path(args.output))
    print(f"Created {args.output}")


if __name__ == "__main__":
    main()
