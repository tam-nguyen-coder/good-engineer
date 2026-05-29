"""
Script phân tích toàn bộ câu hỏi AWS SAA-C03 bằng API.
Chạy: python3 analyze_questions.py
"""
import os
import json
import time
import re
from pathlib import Path

# ---------------------------------------------------------------------------
ENV_PATH = Path("/Users/tamnguyen/Documents/AWS-SAA-C03/.env")
QUESTIONS_DIR = Path("/Users/tamnguyen/Documents/AWS-SAA-C03/questions")
PROGRESS_FILE = Path("/Users/tamnguyen/Documents/AWS-SAA-C03/.analysis_progress.json")

def read_env():
    env = {}
    with open(ENV_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                env[key.strip()] = val.strip()
    return env

env = read_env()
BASE_URL = env.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
API_KEY = env.get("OPENAI_API_KEY", "")
MODEL = env.get("OPENAI_MODEL", "gpt-4o-mini")
REQUEST_DELAY = float(env.get("REQUEST_DELAY", "0.5"))

# clean url
BASE_URL = re.sub(r"/chat/completions/?$", "", BASE_URL)
BASE_URL = re.sub(r"/$", "", BASE_URL)

# ---------------------------------------------------------------------------
PROMPT_TEMPLATE = """You are an AWS SAA-C03 expert. Analyze the following AWS exam question.

Return your analysis in Vietnamese, but keep all AWS service names, features, and technical terms in English (wrap in backticks).

Use this exact format:

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Brief scenario summary
- **Existing Resources:** What already exists in the architecture
- **Current Issue/Goal:** What the question is asking to solve

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective / Most secure / Least operational overhead / Best performance / Highly available / Fault-tolerant
- **Constraints:** Budget, latency, compliance, data size, region, vpc, etc.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: [A/B/C/D]**

**Giải thích:**
- Why this answer is correct
- Which AWS service is used and its role
- How it solves the requirements

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án [A/B/C/D]:**
- Why it is wrong
- When this answer WOULD be correct (if applicable)

**❌ Đáp án [A/B/C/D]:**
- Same format...

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *One short, memorable sentence or association*

---

Here is the question to analyze:

{question}
"""

# ---------------------------------------------------------------------------
def get_files():
    return sorted(QUESTIONS_DIR.glob("question_*.md"))

def is_done(fp: Path) -> bool:
    try:
        return "## 1. CONTEXT & ĐỀ BÀI" in fp.read_text(encoding="utf-8")
    except Exception:
        return False

def load_prog():
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text())
    return {"completed": [], "failed": []}

def save_prog(p):
    PROGRESS_FILE.write_text(json.dumps(p, indent=2))

def call_api(question_text: str, retries: int = 3):
    import httpx
    url = f"{BASE_URL}/chat/completions"
    prompt = PROMPT_TEMPLATE.format(question=question_text)
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 4096,
    }
    for attempt in range(retries):
        try:
            resp = httpx.post(
                url,
                headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                json=payload,
                timeout=180.0,
            )
            data = resp.json()
            if "error" in data:
                raise RuntimeError(str(data["error"]))
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"    ⚠️ Attempt {attempt+1}/{retries}: {e}")
            if attempt < retries - 1:
                wait = 2 ** attempt
                print(f"    Retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise

def main():
    if not API_KEY or API_KEY == "sk-your-api-key-here":
        print("❌ ERROR: Please fill OPENAI_API_KEY in .env")
        return

    files = get_files()
    total = len(files)
    prog = load_prog()
    completed = set(prog.get("completed", []))
    failed = set(prog.get("failed", []))

    print(f"📚 Total questions: {total}")
    print(f"✅ Already done: {len(completed)}")
    print(f"❌ Previously failed: {len(failed)}")
    print(f"🤖 Model: {MODEL}")
    print(f"🔗 URL: {BASE_URL}/chat/completions")
    print("-" * 50)

    pending = [f for f in files if f.name not in completed and not is_done(f)]
    if not pending:
        print("🎉 All questions analyzed!")
        return

    print(f"⏳ Pending: {len(pending)}\n")

    for idx, fp in enumerate(pending, 1):
        qn = fp.stem.replace("question_", "")
        print(f"[{idx}/{len(pending)}] Analyzing Q{qn}...", flush=True)

        try:
            qt = fp.read_text(encoding="utf-8")
            analysis = call_api(qt)

            with open(fp, "a", encoding="utf-8") as f:
                f.write("\n\n")
                f.write(analysis)
                f.write("\n")

            completed.add(fp.name)
            prog["completed"] = list(completed)
            save_prog(prog)
            print(f"    ✅ Done ({len(analysis)} chars)\n", flush=True)

            time.sleep(REQUEST_DELAY)

        except Exception as e:
            print(f"    ❌ FAILED: {e}\n", flush=True)
            failed.add(fp.name)
            prog["failed"] = list(failed)
            save_prog(prog)
            continue

    print("-" * 50)
    print(f"🎉 Done! Analyzed: {len(completed)}/{total}")
    if failed:
        print(f"⚠️ Failed: {len(failed)} questions. Check {PROGRESS_FILE}")

if __name__ == "__main__":
    main()
