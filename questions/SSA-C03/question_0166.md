# Question #166 - Topic 1

Organizers for a global event want to put daily reports online as static HTML pages. The pages are expected to generate millions of views from users around the world. The files are stored in an Amazon S3 bucket. A solutions architect has been asked to design an efficient and effective solution. Which action should the solutions architect take to accomplish this?

## Options

**A.** Generate presigned URLs for the files.

**B.** Use cross-Region replication to all Regions.

**C.** Use the geoproximity feature of Amazon Route 53.

**D.** Use Amazon CloudFront with the S3 bucket as its origin.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Global event, static HTML pages in S3, millions of views worldwide.
- **Existing Resources:** S3 bucket with files.
- **Current Issue/Goal:** Efficient global content delivery.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `millions of views from users around the world` | CDN — **CloudFront** |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Content delivery / CDN
- **Constraints:** Efficient + effective

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **CloudFront** — CDN, cache content tại edge locations gần user → giảm latency, giảm load trên origin (S3).
- Static HTML pages cached at edge → millions of users served efficiently.
- S3 bucket as origin → tích hợp dễ dàng.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Presigned URLs — cho temporary access, không cải thiện global performance.

**❌ Đáp án B:**
- Cross-Region replication — tốn chi phí, không cache ở edge, mỗi Region vẫn chỉ có 1 replica.

**❌ Đáp án C:**
- Route 53 geoproximity — DNS routing, không cache content.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"CloudFront = global CDN. Presigned URLs = temp access. CRR = replication, not caching"*
