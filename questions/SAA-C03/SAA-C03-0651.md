# Question #651 - Topic 1

A company stores a large volume of image files in an Amazon S3 bucket. The images need to be readily available for the first 180 days. The images are infrequently accessed for the next 180 days. After 360 days, the images need to be archived but must be available instantly upon request. After 5 years, only auditors can access the images. The auditors must be able to retrieve the images within 12 hours. The images cannot be lost during this process. A developer will use S3 Standard storage for the first 180 days. The developer needs to configure an S3 Lifecycle rule. Which solution will meet these requirements MOST cost-effectively?

## Options

**A.** Transition the objects to S3 One Zone-Infrequent Access (S3 One Zone-IA) after 180 days. S3 Glacier Instant Retrieval after 360 days, and S3 Glacier Deep Archive after 5 years.

**B.** Transition the objects to S3 One Zone-Infrequent Access (S3 One Zone-IA) after 180 days. S3 Glacier Flexible Retrieval after 360 days, and S3 Glacier Deep Archive after 5 years.

**C.** Transition the objects to S3 Standard-Infrequent Access (S3 Standard-IA) after 180 days, S3 Glacier Instant Retrieval after 360 days, and S3 Glacier Deep Archive after 5 years.

**D.** Transition the objects to S3 Standard-Infrequent Access (S3 Standard-IA) after 180 days, S3 Glacier Flexible Retrieval after 360 days, and S3 Glacier Deep Archive after 5 years.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Image files lifecycle: 0-180d readily available, 180-360d infrequent, after 360d need archive with instant retrieval, after 5 years archived (12h retrieval for auditors). Cannot lose data.
- **Existing Resources:** S3 bucket with S3 Standard for first 180d.
- **Current Issue/Goal:** Cost-effective lifecycle transitions.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `cannot be lost` | Không dùng One Zone-IA (single AZ, risk data loss). |
| `available instantly upon request` | Sau 360d → Glacier Instant Retrieval (ms retrieval). |
| `within 12 hours` | Sau 5 năm → Glacier Deep Archive (12h retrieval) hoặc Glacier Flexible Retrieval (1-12h). Deep Archive rẻ hơn. |
| `S3 Standard-IA` | Durable (multi-AZ), chi phí thấp cho infrequent access. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective
- **Constraints:** Cannot lose data (durability), instant retrieval after 360d, 12h retrieval after 5 years

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- 0-180d: S3 Standard (đã được chọn).
- 180-360d: S3 Standard-IA (infrequent access, multi-AZ durable, rẻ hơn Standard).
- 360d-5y: Glacier Instant Retrieval (archive nhưng instant retrieval).
- Sau 5y: Glacier Deep Archive (rẻ nhất, retrieval 12h phù hợp).
- Standard-IA giữ durability (không dùng One Zone-IA).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- One Zone-IA: chỉ 1 AZ → risk data loss (violate "cannot be lost").

**❌ Đáp án B:**
- One Zone-IA: risk data loss.
- Glacier Flexible Retrieval: retrieval 1-5 phút đến 12h, không instant.

**❌ Đáp án D:**
- Glacier Flexible Retrieval: không instant (1-5 phút đến 12h), trong khi yêu cầu "available instantly".

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Can't lose data → avoid One Zone-IA. Instant retrieval → Glacier Instant Retrieval. Deep Archive = 12h retrieval."*
