# Question #494 - Topic 1

A company uses Amazon EC2 instances to host its internal systems. As part of a deployment operation, an administrator tries to use the AWS CLI to terminate an EC2 instance. However, the administrator receives a 403 (Access Denied) error message. The administrator is using an IAM role that has the following IAM policy attached: What is the cause of the unsuccessful request?

## Options

**A.** The EC2 instance has a resource-based policy with a Deny statement.

**B.** The principal has not been specified in the policy statement.

**C.** The "Action" field does not grant the actions that are required to terminate the EC2 instance.

**D.** The request to terminate the EC2 instance does not originate from the CIDR blocks 192.0.2.0/24 or 203.0.113.0/24.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Administrator dùng IAM role để terminate EC2 instance từ CLI nhưng bị 403 Access Denied. IAM policy attached (nội dung không hiển thị trong file).
- **Existing Resources:** EC2 instances, IAM role with policy.
- **Current Issue/Goal:** Tìm nguyên nhân 403 dựa vào options.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `403 (Access Denied)` | IAM policy evaluation: explicit Deny hoặc implicit Deny. |
| `CIDR blocks 192.0.2.0/24 or 203.0.113.0/24` | Gợi ý policy có condition về source IP (aws:SourceIp). |
| `IAM policy attached` | Policy attached to IAM role. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Troubleshooting IAM policy
- **Constraints:** N/A

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- Dựa vào các CIDR blocks được đề cập, IAM policy có condition `aws:SourceIp` chỉ cho phép requests từ các IP trong dải 192.0.2.0/24 hoặc 203.0.113.0/24.
- Administrator đang chạy CLI từ một IP không thuộc các dải này → implicit Deny (policy không grant quyền cho IP đó).
- Đây là nguyên nhân phổ biến gây 403 khi policy có IP restriction.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- EC2 instances không support resource-based policies (EC2 không phải service cho phép resource-based policy như S3, SQS, KMS).

**❌ Đáp án B:**
- Trong IAM identity-based policy, "Principal" không cần thiết (principal là entity được attach policy).

**❌ Đáp án C:**
- Nếu "Action" field không grant terminate, lỗi sẽ là 403 nhưng các CIDR blocks trong đề gợi ý chính xác là về condition IP.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"403 + CIDR blocks trong đề → condition aws:SourceIp chặn. EC2 không có resource-based policy."*
