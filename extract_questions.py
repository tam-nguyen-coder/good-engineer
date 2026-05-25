import pdfplumber
import re
import json
import os

pdf_path = "/Users/tamnguyen/Documents/AWS-SAA-C03/AWS Certified Solutions Architect Associate SAA-C03.pdf"
output_dir = "/Users/tamnguyen/Documents/AWS-SAA-C03/questions"
os.makedirs(output_dir, exist_ok=True)

# Extract all text
all_text = ""
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            all_text += text + "\n"

# Save raw text for inspection
with open(os.path.join(output_dir, "raw_text.txt"), "w", encoding="utf-8") as f:
    f.write(all_text)

print(f"Total characters extracted: {len(all_text)}")

# Parse questions using regex
# Pattern: Question #N Topic M
question_pattern = re.compile(r'Question\s+#(\d+)\s+Topic\s+(\d+)\s*(.*?)(?=Question\s+#\d+\s+Topic\s+\d+|\Z)', re.DOTALL)

questions = []
for match in question_pattern.finditer(all_text):
    q_num = match.group(1)
    topic = match.group(2)
    content = match.group(3).strip()
    
    # Extract options: look for A., B., C., D. (and possibly E.) at start of lines
    # Split by newline and find option lines
    lines = content.split('\n')
    question_lines = []
    options = {}
    current_option = None
    
    for line in lines:
        line_stripped = line.strip()
        # Match option lines like "A. ..." or "A) ..."
        opt_match = re.match(r'^([A-E])[\.\)]\s*(.*)', line_stripped)
        if opt_match:
            current_option = opt_match.group(1)
            options[current_option] = opt_match.group(2)
        elif current_option:
            # Continue previous option
            options[current_option] += " " + line_stripped
        else:
            question_lines.append(line_stripped)
    
    question_text = " ".join(question_lines).strip()
    
    questions.append({
        "question_number": int(q_num),
        "topic": int(topic),
        "question_text": question_text,
        "options": options
    })

print(f"Total questions parsed: {len(questions)}")

# Save as JSON
with open(os.path.join(output_dir, "questions.json"), "w", encoding="utf-8") as f:
    json.dump(questions, f, indent=2, ensure_ascii=False)

# Also create individual markdown files for first few to verify
for q in questions[:5]:
    md_path = os.path.join(output_dir, f"question_{q['question_number']:03d}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Question #{q['question_number']} - Topic {q['topic']}\n\n")
        f.write(f"{q['question_text']}\n\n")
        f.write("## Options\n\n")
        for opt, text in q['options'].items():
            f.write(f"**{opt}.** {text}\n\n")

print("Done! Check questions/ folder.")
