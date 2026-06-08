# Good Engineer — AWS & Agile Exam Study Hub

Welcome to **Good Engineer**, a repository dedicated to study materials and automated video-generation pipelines for technical certifications. This repository serves as a personal content vault for exam questions, structured analyses, and resources.

Currently, it supports:
- **AWS Certified Solutions Architect – Associate (SAA-C03)**
- **AWS Certified Cloud Practitioner (CLF-C02)**
- **Scrum Master (SCRUM-MASTER-1)**

---

## 📂 Repository Layout

```text
├── AWS Certified Solutions Architect Associate SAA-C03.pdf # Official exam dump source PDF
├── aws-saa-c03-analysis-format.md                          # Authoritative format/template for SAA-C03 analyses
├── video_creation_guide.md                                 # Guide for SAA-C03 video generation (vertical layout)
├── video_spec_schema.json                                  # JSON validation schema for question video assets
├── CLAUDE.md                                               # Development workflow and agent conventions
├── questions/                                              # Question bank segmented by certification
│   ├── SAA-C03/                                            # Solutions Architect Associate materials
│   │   ├── raw_text.txt                                    # Extracted plain text from source PDF
│   │   ├── questions.json                                  # Structured JSON representation of all SAA questions
│   │   └── SAA-C03-NNNN.md                                 # One detailed Markdown file per question (e.g. SAA-C03-0001.md)
│   ├── CLF-C02/                                            # Cloud Practitioner materials
│   │   ├── AWS-Certified-Cloud-Practitioner-CLF-C02-chunk-*.json # Structured chunks of CLF-C02 questions
│   │   └── CLF-C02-NNNN.md                                 # One detailed Markdown file per question (e.g. CLF-C02-0001.md)
│   └── SCRUM-MASTER-1/                                     # Scrum Master study materials
│       ├── scrum-master-1.json                             # Structured JSON representation of all Scrum Master questions
│       └── SCRUM-MASTER-1-NNNN.md                          # One detailed Markdown file per question (e.g. SCRUM-MASTER-1-0001.md)
└── outputs/                                                # Build/rendered video outputs
```

---

## 📝 Study Materials & Question Convention

Each question in this repository is analyzed and converted into a self-contained Markdown study file (`questions/<EXAM>/<EXAM>-NNNN.md`).

### Analysis Structure
Every question analysis follows a strict layout (see [aws-saa-c03-analysis-format.md](file:///Users/tam-macmini/develop/good-engineer/aws-saa-c03-analysis-format.md)):
1. **1. CONTEXT & ĐỀ BÀI**: High-level summary of the scenario, existing resources, and the goal/issue.
2. **2. KEYWORDS QUAN TRỌNG**: A 2-column Markdown table mapping key technical terms to hints/clues.
3. **3. YÊU CẦU CỦA ĐỀ**: Specific question type (e.g., *Most cost-effective*, *Highly available*) and constraints.
4. **4. ĐÁP ÁN ĐÚNG**: Verbatim key and detailed explanation of why it fits the scenario.
5. **5. CÁC ĐÁP ÁN SAI**: Step-by-step breakdown of incorrect choices and context on when they *would* be correct.
6. **6. MẸO GHI NHỚ (Memory Hook)**: A concise memory tip prefixed with a brain emoji `🧠`.

### Language & Formatting Guidelines
- **Vietnamese** is used for all explanations, scenarios, and memory hooks.
- **English** is preserved for official AWS service names, options, and technical jargon wrapped in backticks (e.g., `` `S3 Transfer Acceleration` ``, `` `NAT Gateway` ``).
- **Filenames** use zero-padded 4-digit suffixes (e.g., `SAA-C03-0021.md`).

---

## 🎥 Video Generation Pipeline (SAA-C03)

The repository provides a standard workflow for compiling SAA-C03 question-solving videos in a vertical (1080x1920) mobile-friendly format. The guide in [video_creation_guide.md](file:///Users/tam-macmini/develop/good-engineer/video_creation_guide.md) explains the grid layout and design tokens.

### Question Video Assets Structure
When compiling a video project for a specific question, the folder should contain:
```text
aws-saa-c03-q[number]/
├── fonts/             # Space Grotesk & Space Mono (local WOFF2 files)
├── assets/            # Architecture diagrams or visual assets
├── index.html         # Core DOM structure, CSS (AWS Tech Dark), and GSAP animations
├── script.txt         # Voiceover voice script
├── narration.wav      # Generated voiceover audio
├── transcript.json    # Word-aligned timestamps
├── hyperframes.json   # Composition metadata
└── package.json       # Preview/render npm targets
```

### Automation & Rendering Workflow
1. **Synthesize Voiceover** (using Kokoro TTS and the standard `am_adam` voice):
   ```bash
   npx hyperframes tts script.txt --voice am_adam --output narration.wav
   ```
2. **Align Audio Transcription** (generating word-level timestamps with Whisper):
   ```bash
   npx hyperframes transcribe narration.wav --model small.en
   ```
3. **Inline Transcripts**:
   Use `inline_transcript.py` to embed Whisper timestamps into the web build:
   ```bash
   python3 inline_transcript.py .
   ```
4. **Render Video**:
   Run the dev server to preview, or compile the production bundle:
   ```bash
   npm run render
   ```

---

## 🛠️ Development Guidance
For local agents and developers, please refer to [CLAUDE.md](file:///Users/tam-macmini/develop/good-engineer/CLAUDE.md) for environment details and guidelines. Always verify details against the source PDFs and JSON records before altering exam questions or option mappings.
