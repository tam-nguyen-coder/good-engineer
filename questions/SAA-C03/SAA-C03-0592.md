# Question #592 - Topic 1

A company uses AWS and sells access to copyrighted images. The company's global customer base needs to be able to access these images quickly. The company must deny access to users from specific countries. The company wants to minimize costs as much as possible. Which solution will meet these requirements?

## Options

**A.** Use Amazon S3 to store the images. Turn on multi-factor authentication (MFA) and public bucket access. Provide customers with a link to the S3 bucket.

**B.** Use Amazon S3 to store the images. Create an IAM user for each customer. Add the users to a group that has permission to access the S3 bucket.

**C.** Use Amazon EC2 instances that are behind Application Load Balancers (ALBs) to store the images. Deploy the instances only in the countries the company services. Provide customers with links to the ALBs for their specific country's instances.

**D.** Use Amazon S3 to store the images. Use Amazon CloudFront to distribute the images with geographic restrictions. Provide a signed URL for each customer to access the data in CloudFront.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Bán copyrighted images, global customers, cần deny access from specific countries, minimize costs.
- **Existing Resources:** AWS.
- **Current Issue/Goal:** Secure content delivery + geo-restriction + cost-effective.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `global customer base` | Cần CDN (CloudFront) cho fast access. |
| `deny access to users from specific countries` | CloudFront geo-restriction (whitelist/blacklist countries). |
| `copyrighted images` | Cần signed URLs để bảo vệ content. |
| `minimize costs` | S3 + CloudFront là cost-effective cho global content delivery. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Minimize costs + secure delivery
- **Constraints:** Global, geo-restriction, copyrighted content

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- S3: lưu trữ images chi phí thấp.
- CloudFront: CDN global, giảm latency cho users.
- Geo-restriction: block/allow countries.
- Signed URLs: bảo vệ copyrighted images, chỉ authorized users mới access được.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- MFA + public bucket: không geo-restriction. Public bucket ai cũng access được (nếu biết URL). Không bảo vệ copyrighted content.

**❌ Đáp án B:**
- IAM user mỗi customer: không scalable, operational overhead cực cao. Không geo-restriction.

**❌ Đáp án C:**
- EC2 + ALB: đắt hơn S3 + CloudFront. Deploy ở từng quốc gia: phức tạp, tốn kém.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Global copyrighted content → S3 + CloudFront + geo-restriction + signed URLs. EC2 = too expensive."*
