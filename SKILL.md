---
name: resume-creator
description: Guides users through building a complete, ATS-optimized resume using a proven 2026 methodology. Use when the user wants to create, rewrite, or improve a resume. Covers keyword strategy, a 5-section template, the Badass Bullet Point Formula, Professional Summary generation, and PDF export via a bundled script. Outputs a ready-to-paste markdown source and a styled 2-page PDF.
---

# Resume Creator

Builds ATS-optimized, 2-page resumes following Greg Langstaff's 2026 methodology. Walk through the workflow below, gathering input at each step before writing.

---

## Workflow

**Step 1 — Gather inputs.** Ask the user for:
- Target job title and/or a job posting to pull keywords from
- Industry and total years of experience
- 3–5 key achievements with numbers (revenue, %, time saved, team size, etc.)
- Contact info: full name, phone, city/state, email, LinkedIn URL
- Work history: job titles, companies, dates, locations, 1–2 sentence context per role
- Education: credential type, field, school, city/state (omit if irrelevant — use Certifications instead)
- Certifications, awards (optional)

**Step 2 — Build the Areas of Expertise grid.** Extract keywords from the job posting into 3 categories:
1. Industry Terminology
2. Job Specific Skills
3. Equipment or Software

Format as a **4-column bullet grid** (12–16 terms). These are the primary ATS keyword injection points.

**Step 3 — Generate Professional Summary.** Use titled-sentence style (recommended) or straight paragraph:
- **Titled-sentence style**: each sentence starts with a bold keyword topic. Example: `Test Infrastructure: Built 2,000+ TestRail test cases and cut suite creation from 2–3 days to 5–6 hours.`
- **Straight paragraph style**: plain sentences, no titles.

3–5 sentences. No em dashes. No fluff. Preview real strengths supported by the resume.

**Step 4 — Write experience entries.** For each role:
- Header line: `Job Title | Start Date – End Date` (or Present)
- Second line: `**Company Name**, City, ST`
- Bullets using the **Badass Bullet Point Formula** (3–6 per role, 5–8 for the most recent senior role):
  `[Action Verb] + [Specific / Quantifiable Detail] + [Result]`
- Every bullet proves impact — no responsibility lists.

For roles with multiple sub-projects under one title, use sub-project headers (see Markdown Format below).

**Step 5 — Write Certifications.** When the user has no relevant education degree, replace the Education section with Certifications:
- `**Certificate Name**, Organization | YEAR`

**Step 6 — Assemble** the full resume using the structure below. Output as a markdown file named `[firstname-lastname]-resume-ats.md`.

**Step 7 — Generate PDF.** Run the bundled script to produce a styled PDF:

```bash
# One-time setup (from the project directory)
python3 -m venv .venv && .venv/bin/pip install reportlab --quiet

# Generate
.venv/bin/python scripts/generate_resume_pdf.py \
  --source [firstname-lastname]-resume-ats.md \
  --output [firstname-lastname]-resume.pdf
```

If the output spills past 2 pages, tighten by removing redundant bullets (not by shrinking fonts). If page 2 has large empty space, add a short Technical Toolkit paragraph at the end.

---

## Resume Structure (2-page template)

### Page 1

```
YOUR NAME                          ← centered, 21pt bold, dark navy
Professional Title  |  Professional Title   ← dual titles if targeting 2 role types
Phone  |  City, ST  |  email  |  LinkedIn URL

PROFESSIONAL SUMMARY -----------------------------------------------
[3–5 sentences. Titled-sentence or straight paragraph. No em dashes.]

AREAS OF EXPERTISE -------------------------------------------------
• Keyword 1        • Keyword 4        • Keyword 7        • Keyword 10
• Keyword 2        • Keyword 5        • Keyword 8        • Keyword 11
• Keyword 3        • Keyword 6        • Keyword 9        • Keyword 12

PROFESSIONAL EXPERIENCE --------------------------------------------
Company Name — Context Description
**Job Title** | Start – End | Location

  • Action Verb + Specific Detail + Result
  • (5–8 bullets for top role, 3–5 for others)

**Second Role at Same Company** | Start – End | Location

  • bullet
```

### Page 2

```
PROFESSIONAL EXPERIENCE CONTINUED ----------------------------------
[Continue remaining roles in same format]

CERTIFICATIONS -----------------------------------------------------
• **Certificate Name**, Organization | YEAR
```

---

## Markdown Format Reference

The bundled `generate_resume_pdf.py` script parses this exact markdown format:

```markdown
# Full Name
Professional Title  |  Professional Title
Phone  |  City, ST  |  email  |  [linkedin.com/in/handle](url)

## Professional Summary
[one or more non-empty lines — the parser reads each line as its own summary paragraph]

## Areas of Expertise
Keyword 1 | Keyword 2 | Keyword 3 | Keyword 4 | Keyword 5 | ...

## Professional Experience

### Company Name — Context
**Job Title** | Start – End | Location

- Bullet one
- Bullet two

**Second Role** | Start – End | Location

- Bullet one

#### Sub-project Name | Start – End

- Bullet under sub-project

### Next Company
**Job Title** | Start – End | Location

- Bullet

## Certifications

- **Certificate Name**, Organization | YEAR
```

**Key format rules:**
- `### ` = company header
- `**Title** | dates` = main role (bold in PDF)
- `#### Name | dates` = sub-project under a role (bold, slightly indented spacing, visually subordinate)
- `## Areas of Expertise` keywords separated by `|` → rendered as 4-column grid
- First two lines after `# Name` become the header block: line 1 = title (larger bold), line 2+ = contact info
- Certifications section replaces Education when no relevant degree

---

## Design Specification

| Element | Spec |
|---|---|
| Page size | US Letter, margins 0.7" left/right, 0.65" top, 0.6" bottom |
| Name | Helvetica-Bold, 22pt, centered, near-black `#111111` |
| Dual title line | Helvetica-Bold, 11pt, centered, `#1F2937` |
| Contact line | Helvetica, 9.4pt, centered, gray `#6B7280` |
| Section headers | Helvetica-Bold, 11.6pt, UPPERCASE, navy `#16324F`, `spaceBefore=11` |
| Summary text | Helvetica, 9.5pt, leading 13, supports multi-line titled-sentence paragraphs |
| Company name | Helvetica-Bold, 10.9pt, `#111827`, `spaceBefore=7` |
| Main role line | Helvetica, 9.5pt, role bolded inline, metadata gray |
| Sub-project line | Helvetica, 9.4pt, role bolded inline, `spaceBefore=5` |
| Bullet text | Helvetica, 9.3pt, leading 12, compact list spacing |
| Certifications | Single-column bullet list, 8.9pt, compact leading 10.6 |
| AoE grid | 4-column Table (no visible borders), 9.2pt, bullet prefix |
| Color scheme | Navy `#16324F` + white — no color accents in body |
| Length | Exactly 2 pages — do not compress to 1 |

---

## ATS Rules

- **No tables, columns, text boxes, or graphics** in the body (the AoE grid uses an invisible Table — text remains extractable).
- **Keywords**: pulled from the target job posting → inject into Areas of Expertise first, then echo the most important ones in the Summary.
- **Hook fast**: name, dual titles, and summary must lead with clear value.
- **Metrics beat responsibilities**: every bullet in the top role should have a number or concrete outcome.
