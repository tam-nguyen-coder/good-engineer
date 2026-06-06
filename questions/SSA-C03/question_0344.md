# Question #344 - Topic 1

A company has a Java application that uses Amazon Simple Queue Service (Amazon SQS) to parse messages. The application cannot parse messages that are larger than 256 KB in size. The company wants to implement a solution to give the application the ability to parse messages as large as 50 MB. Which solution will meet these requirements with the FEWEST changes to the code?

## Options

**A.** Use the Amazon SQS Extended Client Library for Java to host messages that are larger than 256 KB in Amazon S3.

**B.** Use Amazon EventBridge to post large messages from the application instead of Amazon SQS.

**C.** Change the limit in Amazon SQS to handle messages that are larger than 256 KB.

**D.** Store messages that are larger than 256 KB in Amazon Elastic File System (Amazon EFS). Configure Amazon SQS to reference this location in the messages.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Java app dùng SQS parse messages, max 256 KB. Cần parse messages up to 50 MB. Fewest code changes.
- **Existing Resources:** Java application, SQS queue.
- **Current Issue/Goal:** Handle large messages (>256 KB) up to 50 MB.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Amazon SQS Extended Client Library for Java` | Client library tự động store messages >256 KB trong S3, chỉ gửi S3 reference trong SQS. |
| `FEWEST changes to the code` | Extended Client Library: thay đổi code minimal (chỉ cần add library). |
| `256 KB` | SQS max message size (hard limit, không thể change). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Fewest changes to the code
- **Constraints:** SQS, messages up to 50 MB

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- SQS Extended Client Library: tự động phát hiện messages >256 KB → lưu trong S3 → gửi S3 object reference qua SQS.
- Consumer cũng dùng Extended Client Library tự động resolve reference → đọc message từ S3.
- Application code changes minimal: chỉ cần thay đổi SQS client initialization.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- EventBridge có max size tương tự (256 KB với default, 64 KB với custom). Phải rewrite application để dùng EventBridge thay SQS.

**❌ Đáp án C:**
- SQS max message size không thể thay đổi (256 KB là hard limit).

**❌ Đáp án D:**
- EFS: không thể "configure SQS to reference this location". Phải custom implement → nhiều code changes.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"SQS > 256 KB → Extended Client Library (lưu S3, reference trong SQS). SQS hard limit = 256 KB, không change được."*
