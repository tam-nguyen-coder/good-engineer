# Question #88 - Topic 1

A survey company has gathered data for several years from areas in the United States. The company hosts the data in an Amazon S3 bucket that is 3 TB in size and growing. The company has started to share the data with a European marketing firm that has S3 buckets. The company wants to ensure that its data transfer costs remain as low as possible. Which solution will meet these requirements?

## Options

**A.** Configure the Requester Pays feature on the company's S3 bucket.

**B.** Configure S3 Cross-Region Replication from the company's S3 bucket to one of the marketing firm's S3 buckets.

**C.** Configure cross-account access for the marketing firm so that the marketing firm has access to the company's S3 bucket.

**D.** Configure the company's S3 bucket to use S3 Intelligent-Tiering. Sync the S3 bucket to one of the marketing firm's S3 buckets.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** US company shares S3 data (3TB+) with European marketing firm.
- **Existing Resources:** S3 bucket in US.
- **Current Issue/Goal:** Minimize data transfer costs for the company.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `data transfer costs remain as low as possible` | Company không muốn trả tiền transfer |
| `Requester Pays` | **Requester Pays** — người tải data trả phí |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost optimization
- **Constraints:** Share data with external party, minimize company's costs

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **Requester Pays** — marketing firm (requester) trả phí data transfer và request.
- Company không mất phí khi marketing firm tải data.
- Marketing firm có S3 buckets riêng nên có thể trả phí.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- **Cross-Region Replication** — company trả phí replication (data transfer + request).

**❌ Đáp án C:**
- Cross-account access — company vẫn trả phí data transfer khi marketing firm đọc data.

**❌ Đáp án D:**
- Intelligent-Tiering là storage class, không giúp giảm data transfer costs.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Requester Pays = người tải trả tiền. Cross-Region Replication = chủ bucket trả tiền"*
