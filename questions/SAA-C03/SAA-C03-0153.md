# Question #153 - Topic 1

A company sells ringtones created from clips of popular songs. The files containing the ringtones are stored in Amazon S3 Standard and are at least 128 KB in size. The company has millions of files, but downloads are infrequent for ringtones older than 90 days. The company needs to save money on storage while keeping the most accessed files readily available for its users. Which action should the company take to meet these requirements MOST cost-effectively?

## Options

**A.** Configure S3 Standard-Infrequent Access (S3 Standard-IA) storage for the initial storage tier of the objects.

**B.** Move the files to S3 Intelligent-Tiering and configure it to move objects to a less expensive storage tier after 90 days.

**C.** Configure S3 inventory to manage objects and move them to S3 Standard-Infrequent Access (S3 Standard-1A) after 90 days.

**D.** Implement an S3 Lifecycle policy that moves the objects from S3 Standard to S3 Standard-Infrequent Access (S3 Standard-1A) after 90 days.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Ringtones in S3 Standard, millions of files, >128KB. Downloads infrequent after 90 days.
- **Existing Resources:** S3 Standard.
- **Current Issue/Goal:** Cost savings, keep frequently accessed files available.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `infrequent for ringtones older than 90 days` | Access pattern rõ ràng: hot 90 ngày, cold sau đó |
| `most cost-effectively` | **S3 Lifecycle policy** (không có monitoring phí) |
| `at least 128 KB in size` | Đủ lớn để Standard-IA có lợi |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost optimization
- **Constraints:** Known access pattern, millions of files

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **S3 Lifecycle policy** — Standard → Standard-IA after 90 ngày.
- Standard-IA rẻ hơn Standard cho infrequent access, vẫn immediately accessible.
- **Known access pattern** → lifecycle policy đơn giản và rẻ hơn Intelligent-Tiering (không có monitoring fee).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Standard-IA ngay từ đầu — không optimal vì files có thể được access thường xuyên trong 90 ngày đầu.

**❌ Đáp án B:**
- Intelligent-Tiering — có monitoring fee cho mỗi object (với millions of files, fee này đáng kể).

**❌ Đáp án C:**
- S3 Inventory — chỉ report, không tự động move objects.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Lifecycle = cost-effective cho known pattern. Intelligent-Tiering = monitoring fee per object. Inventory = report only"*
