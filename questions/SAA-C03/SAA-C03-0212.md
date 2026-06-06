# Question #212 - Topic 1

A company needs to export its database once a day to Amazon S3 for other teams to access. The exported object size varies between 2 GB and 5 GB. The S3 access pattern for the data is variable and changes rapidly. The data must be immediately available and must remain accessible for up to 3 months. The company needs the most cost-effective solution that will not increase retrieval time. Which S3 storage class should the company use to meet these requirements?

## Options

**A.** S3 Intelligent-Tiering

**B.** S3 Glacier Instant Retrieval

**C.** S3 Standard

**D.** S3 Standard-Infrequent Access (S3 Standard-IA)

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Daily DB export to S3, 2-5GB files. Variable access pattern. Immediate availability, 3-month retention. Most cost-effective, no increased retrieval time.
- **Existing Resources:** DB export.
- **Current Issue/Goal:** Optimal storage class for variable access.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `access pattern... variable and changes rapidly` | **S3 Intelligent-Tiering** (auto-moves data) |
| `immediately available` | Standard tier |
| `most cost-effective` | Intelligent-Tiering tự động tối ưu cost |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Storage / Cost optimization
- **Constraints:** Variable access, immediate, 3 months

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **S3 Intelligent-Tiering** — tự động di chuyển objects giữa frequent/infrequent access tiers dựa trên access pattern.
- Không retrieval fee, không retrieval time penalty.
- Phù hợp cho variable/unpredictable access patterns.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Glacier Instant Retrieval — có retrieval cost, min 90 days storage charge.

**❌ Đáp án C:**
- S3 Standard — cost cao hơn Intelligent-Tiering cho data ít accessed.

**❌ Đáp án D:**
- S3 Standard-IA — retrieval fee, không tối ưu nếu access pattern thay đổi.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Intelligent-Tiering = auto-optimize for variable access. Standard = more cost for infrequent. IA/Glacier = retrieval fees"*
