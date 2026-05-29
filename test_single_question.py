import os
import re

# Read .env manually
def read_env():
    env = {}
    with open("/Users/tamnguyen/Documents/AWS-SAA-C03/.env") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                env[key.strip()] = val.strip()
    return env

env = read_env()
BASE_URL = env["OPENAI_BASE_URL"]
API_KEY = env["OPENAI_API_KEY"]
MODEL = env["OPENAI_MODEL"]

print(f"Base URL: {BASE_URL}")
print(f"Model: {MODEL}")
print(f"API Key: {API_KEY[:15]}...")

# Read question file
with open("/Users/tamnguyen/Documents/AWS-SAA-C03/questions/question_0002.md") as f:
    question_text = f.read()

SYSTEM_PROMPT = """Bạn là chuyên gia AWS SAA-C03. Phân tích câu hỏi trắc nghiệm theo format:

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** ...
- **Existing Resources:** ...
- **Current Issue/Goal:** ...

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** ...
- **Constraints:** ...

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: X**
**Giải thích:** ...

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án X:** ...

## 6. MẸO GHI NHỚ
🧠 *...*

QUY TẮC: Tiếng Việt + giữ nguyên AWS keywords tiếng Anh trong backticks. Chỉ trả nội dung phân tích."""

# Use httpx directly since openai SDK might have issues
import httpx
import json

payload = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question_text}
    ],
    "temperature": 0.3,
    "max_tokens": 2048
}

print("\n🚀 Calling API...")
try:
    response = httpx.post(
        f"{BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json=payload,
        timeout=120.0
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if "error" in data:
        print(f"❌ Error: {json.dumps(data['error'], indent=2)}")
    else:
        content = data["choices"][0]["message"]["content"]
        print("\n" + "="*60)
        print(content)
        print("="*60)
except Exception as e:
    print(f"❌ Exception: {e}")
