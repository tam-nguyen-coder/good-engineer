# Question #313 - Topic 1

A company is building a mobile app on AWS. The company wants to expand its reach to millions of users. The company needs to build a platform so that authorized users can watch the company's content on their mobile devices. What should a solutions architect recommend to meet these requirements?

## Options

**A.** Publish content to a public Amazon S3 bucket. Use AWS Key Management Service (AWS KMS) keys to stream content.

**B.** Set up IPsec VPN between the mobile app and the AWS environment to stream content.

**C.** Use Amazon CloudFront. Provide signed URLs to stream content.

**D.** Set up AWS Client VPN between the mobile app and the AWS environment to stream content.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Mobile app với millions of users, authorized users xem content. Cần scalable và secure.
- **Existing Resources:** (none specified)
- **Current Issue/Goal:** Deliver content to authorized mobile users at scale.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `millions of users` | Cần giải pháp global scale → CloudFront CDN. |
| `authorized users` | Cần access control → CloudFront signed URLs. |
| `stream content` | CDN tối ưu cho streaming (cache tại edge). |
| `signed URLs` | CloudFront signed URLs cho phép access control mà không cần authentication infrastructure phức tạp. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which solution meets requirements
- **Constraints:** Millions of users, authorized access, mobile devices

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- CloudFront: CDN global scale, cache content tại edge locations gần users → giảm latency, handle millions of users.
- Signed URLs: kiểm soát access đến content, chỉ authorized users mới có URL hợp lệ.
- Kết hợp S3 làm origin + CloudFront + signed URLs là pattern chuẩn cho secure content delivery.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- S3 public bucket không an toàn (ai cũng có thể access). KMS không kiểm soát access ở application level.

**❌ Đáp án B:**
- IPsec VPN không scale cho millions of users (mỗi user cần VPN connection riêng).

**❌ Đáp án D:**
- AWS Client VPN tương tự: không scale cho millions of users, operational overhead cao.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Millions of users + authorized content → CloudFront + signed URLs. VPN không scale cho millions."*
