# Question #83 - Topic 1

A company's dynamic website is hosted using on-premises servers in the United States. The company is launching its product in Europe, and it wants to optimize site loading times for new European users. The site's backend must remain in the United States. The product is being launched in a few days, and an immediate solution is needed. What should the solutions architect recommend?

## Options

**A.** Launch an Amazon EC2 instance in us-east-1 and migrate the site to it.

**B.** Move the website to Amazon S3. Use Cross-Region Replication between Regions.

**C.** Use Amazon CloudFront with a custom origin pointing to the on-premises servers.

**D.** Use an Amazon Route 53 geoproximity routing policy pointing to on-premises servers.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Dynamic website on-prem US, launch product in Europe, optimize loading times for EU users.
- **Existing Resources:** On-prem servers in US.
- **Current Issue/Goal:** Faster loading for European users, backend stays in US, immediate solution.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `dynamic website` | Không thể host static trên S3 |
| `backend must remain in the United States` | Origin là on-prem US |
| `optimize site loading times` | Cần **CDN** — CloudFront |
| `immediate solution` | Không cần migrate, deploy nhanh |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Performance optimization
- **Constraints:** Backend ở US, dynamic content, immediate

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **CloudFront** với **custom origin** (on-prem servers) — CDN cache content tại edge locations gần user.
- European users được serve từ edge location gần nhất → giảm latency.
- Backend vẫn ở US (origin server).
- Triển khai nhanh — chỉ cần cấu hình CloudFront, không migrate.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- EC2 in us-east-1 không giúp European users — server vẫn ở US.

**❌ Đáp án B:**
- S3 chỉ hỗ trợ **static website**, không phải dynamic.
- Cross-Region Replication không giúp giảm latency cho dynamic content.

**❌ Đáp án D:**
- **Geoproximity routing** chỉ định route traffic đến server gần nhất — nhưng server chỉ có 1 ở US. Không cache như CDN.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"CloudFront + custom origin = CDN cho dynamic website. Backend ở US, edge ở EU = low latency"*
