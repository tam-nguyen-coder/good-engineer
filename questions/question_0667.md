# Question #667 - Topic 1

A company is moving its data and applications to AWS during a multiyear migration project. The company wants to securely access data on Amazon S3 from the company's AWS Region and from the company's on-premises location. The data must not traverse the internet. The company has established an AWS Direct Connect connection between its Region and its on-premises location. Which solution will meet these requirements?

## Options

**A.** Create gateway endpoints for Amazon S3. Use the gateway endpoints to securely access the data from the Region and the on-premises location.

**B.** Create a gateway in AWS Transit Gateway to access Amazon S3 securely from the Region and the on-premises location.

**C.** Create interface endpoints for Amazon S3. Use the interface endpoints to securely access the data from the Region and the on-premises location.

**D.** Use an AWS Key Management Service (AWS KMS) key to access the data securely from the Region and the on-premises location.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Access S3 from both AWS Region and on-premises via Direct Connect. No internet traversal.
- **Existing Resources:** Direct Connect connection.
- **Current Issue/Goal:** Secure S3 access without internet.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `must not traverse the internet` | Cần VPC endpoint hoặc Direct Connect VIF. |
| `gateway endpoints for S3` | Free, dùng cho S3 từ trong VPC, có thể route từ on-prem qua Direct Connect. |
| `interface endpoints for S3` | PrivateLink, có phí, cũng có thể truy cập từ on-prem. |
| `Direct Connect` | Kết nối private từ on-prem đến AWS. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements
- **Constraints:** No internet, access from Region + on-prem

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Gateway VPC endpoints cho S3: free, cung cấp access đến S3 từ trong VPC.
- Từ on-premises: traffic đi qua Direct Connect vào VPC, route đến gateway endpoint → private, không qua internet.
- Chi phí thấp nhất (gateway endpoint free).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Transit Gateway dùng để kết nối VPCs với nhau hoặc với on-prem, không phải endpoint cho S3.

**❌ Đáp án C:**
- Interface endpoints (PrivateLink) cho S3 có phí, không cần thiết khi gateway endpoint có sẵn free.

**❌ Đáp án D:**
- KMS key quản lý encryption, không kiểm soát network access.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"S3 access without internet → Gateway VPC Endpoint (free). Direct Connect + route to endpoint."*
