# Question #656 - Topic 1

A company runs a website that stores images of historical events. Website users need the ability to search and view images based on the year that the event in the image occurred. On average, users request each image only once or twice a year. The company wants a highly available solution to store and deliver the images to users. Which solution will meet these requirements MOST cost-effectively?

## Options

**A.** Store images in Amazon Elastic Block Store (Amazon EBS). Use a web server that runs on Amazon EC2.

**B.** Store images in Amazon Elastic File System (Amazon EFS). Use a web server that runs on Amazon EC2.

**C.** Store images in Amazon S3 Standard. Use S3 Standard to directly deliver images by using a static website.

**D.** Store images in Amazon S3 Standard-Infrequent Access (S3 Standard-IA). Use S3 Standard-IA to directly deliver images by using a static website.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Historical images, users search/view by year, each image requested only 1-2 times/year. Need HA and cost-effective.
- **Existing Resources:** Website for image storage and delivery.
- **Current Issue/Goal:** Highly available, low-cost storage for very infrequently accessed images.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `once or twice a year` | Very infrequent access → S3 Standard-IA rẻ hơn S3 Standard. |
| `highly available` | S3 Standard-IA là multi-AZ, durable, HA. |
| `S3 Standard-IA` | Chi phí lưu trữ thấp hơn Standard, phù hợp data ít truy cập. |
| `static website` | S3 hỗ trợ static website hosting, không cần web server. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective
- **Constraints:** Highly available, very infrequent access

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- S3 Standard-IA: chi phí lưu trữ thấp hơn Standard (~50%), phù hợp data hiếm khi truy cập.
- S3 static website hosting: deliver images trực tiếp, không cần EC2.
- Highly available: S3 Standard-IA lưu trữ multi-AZ.
- Phù hợp use case: images chỉ được request 1-2 lần/năm.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- EBS không thể share giữa nhiều instances, cần EC2.
- Single point of failure (EBS in 1 AZ).
- Tốn kém (EC2 + EBS).

**❌ Đáp án B:**
- EFS + EC2: tốn kém hơn S3 static website.
- EFS có phí per GB cao hơn S3.

**❌ Đáp án C:**
- S3 Standard: chi phí cao hơn Standard-IA cho data ít truy cập.
- Use case này không cần truy xuất thường xuyên → Standard-IA đủ.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Infrequent access (1-2x/year) → S3 Standard-IA. Cheaper than Standard, same HA."*
