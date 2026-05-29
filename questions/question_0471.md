# Question #471 - Topic 1

A company is creating an application that runs on containers in a VPC. The application stores and accesses data in an Amazon S3 bucket. During the development phase, the application will store and access 1 TB of data in Amazon S3 each day. The company wants to minimize costs and wants to prevent traffic from traversing the internet whenever possible. Which solution will meet these requirements?

## Options

**A.** Enable S3 Intelligent-Tiering for the S3 bucket

**B.** Enable S3 Transfer Acceleration for the S3 bucket

**C.** Create a gateway VPC endpoint for Amazon S3. Associate this endpoint with all route tables in the VPC

**D.** Create an interface endpoint for Amazon S3 in the VPC. Associate this endpoint with all route tables in the VPC

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Container app trong VPC, access S3 bucket, 1TB/day traffic.
- **Existing Resources:** Containers in VPC, S3 bucket.
- **Current Issue/Goal:** Minimize costs, prevent internet traffic.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `prevent traffic from traversing the internet` | Dùng VPC endpoint để traffic qua AWS network, không qua internet. |
| `minimize costs` | Gateway endpoint: free, không tính phí. Interface endpoint: tính phí ($/hour + data processing). |
| `1 TB of data each day` | Volume lớn → cần endpoint miễn phí để tiết kiệm. |
| `gateway VPC endpoint` | Free, dùng route table, hỗ trợ S3 và DynamoDB. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Minimize costs, keep traffic off internet
- **Constraints:** 1TB/day, containers in VPC

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Gateway VPC endpoint cho S3: free, không mất phí.
- Traffic từ container đến S3 đi qua AWS network, không qua internet.
- Associate với route tables: tự động thêm route đến S3.
- 1TB/day → gateway endpoint tiết kiệm rất nhiều so với interface endpoint (tính phí data processing).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Intelligent-Tiering: tối ưu storage cost, không giải quyết vấn đề network/internet traffic.

**❌ Đáp án B:**
- S3 Transfer Acceleration: tăng tốc upload qua AWS edge, không ngăn internet traffic. Tốn thêm phí.

**❌ Đáp án D:**
- Interface endpoint: tính phí ($0.01/hour + $0.01/GB data processing). Với 1TB/day, chi phí rất cao so với gateway endpoint (free).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"VPC → S3 không qua internet + tiết kiệm = Gateway Endpoint (free). Interface endpoint = tốn phí."*
