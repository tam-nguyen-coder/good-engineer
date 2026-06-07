# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal Vietnamese-language study material for the **AWS Certified Solutions Architect – Associate (SAA-C03)** exam. It is a **content repository, not a code repository** — there is no build, lint, or test pipeline. The "development" workflow is authoring and refining question analyses.

## Repository layout

```
AWS-SAA-C03.pdf                      # Source: official exam dump PDF
aws-saa-c03-analysis-format.md       # Authoritative template for every analysis
questions/
  CLF-C02/                           # JSON chunks for Cloud Practitioner
  SCRUM-MASTER-1/                    # JSON for Scrum Master
  SAA-C03/                           # Subfolder for Solutions Architect Associate SAA-C03
    raw_text.txt                     # Raw text extracted from the PDF
    questions.json                   # Structured JSON of all questions (source of truth)
    SAA-C03-0001.md ... SAA-C03-0684.md # One Markdown file per question (684 total)
.vscode/settings.json                # Disables Python language server
```

## Question file convention

Every file in `questions/SAA-C03/SAA-C03-NNNN.md` is a self-contained study note with two parts:

1. **Header** — the original exam question and four options (A/B/C/D) verbatim.
2. **Analysis** — following the strict template in `aws-saa-c03-analysis-format.md` with six sections:
   1. CONTEXT & ĐỀ BÀI
   2. KEYWORDS QUAN TRỌNG
   3. YÊU CẦU CỦA ĐỀ
   4. ĐÁP ÁN ĐÚNG
   5. CÁC ĐÁP ÁN SAI
   6. MẸO GHI NHỚ (Memory Hook)

When creating or editing a question file, **read `aws-saa-c03-analysis-format.md` first** and follow it exactly — section headings, ordering, and structure are not negotiable.

### Filename convention

- Format: `SAA-C03-NNNN.md` with zero-padded 4-digit numeric suffix (e.g., `SAA-C03-0001.md`, `SAA-C03-0684.md`).
- Numbering matches the question's position in the source PDF / `questions.json`.
- The old naming (`question_0001.md` or `question_001.md`) was updated — do not reintroduce it.

### Language and formatting conventions

- **Vietnamese** is the language of analysis prose (headings, explanations, memory hooks).
- **English AWS service / feature names are preserved** in backticks: `` `S3 Transfer Acceleration` ``, `` `Cross-Region Replication` ``, `` `Multi-AZ` ``, etc.
- Memory hooks use the brain emoji prefix: `🧠`.
- The keywords table in section 2 must be a Markdown table with exactly two columns: `Keyword` and `Ý nghĩa / Gợi ý`.

## Source-of-truth data

`questions.json` and `raw_text.txt` are the structured/text extractions of the source PDF. They are the reference when a question file's question text or options need to be verified or corrected — never invent wording that isn't in these files.

## History to be aware of

Commit `5dead8e` (most recent) cleaned out automation that previously generated the analyses:

- `analyze_questions.py`, `extract_questions.py`, `test_single_question.py` (deleted)
- `analyze.log`, `.analysis_progress.json`, `.env` (deleted)

These scripts are **not** part of the repo anymore. If a task seems to call for re-extracting from the PDF, regenerate against the existing `questions.json` / `raw_text.txt` rather than reimplementing the deleted pipeline.
