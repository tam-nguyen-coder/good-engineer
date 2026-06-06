# Question #560 - Topic 1

A company's solutions architect is designing an AWS multi-account solution that uses AWS Organizations. The solutions architect has organized the company's accounts into organizational units (OUs). The solutions architect needs a solution that will identify any changes to the OU hierarchy. The solution also needs to notify the company's operations team of any changes. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Provision the AWS accounts by using AWS Control Tower. Use account drift notifications to identify the changes to the OU hierarchy.

**B.** Provision the AWS accounts by using AWS Control Tower. Use AWS Config aggregated rules to identify the changes to the OU hierarchy.

**C.** Use AWS Service Catalog to create accounts in Organizations. Use an AWS CloudTrail organization trail to identify the changes to the OU hierarchy.

**D.** Use AWS CloudFormation templates to create accounts in Organizations. Use the drift detection operation on a stack to identify the changes to the OU hierarchy.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** AWS multi-account với Organizations. Accounts được tổ chức thành OUs. Cần phát hiện thay đổi trong OU hierarchy và thông báo cho operations team.
- **Existing Resources:** AWS Organizations, OUs, accounts.
- **Current Issue/Goal:** Phát hiện và notify về thay đổi OU hierarchy, ít operational overhead nhất.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `changes to the OU hierarchy` | Phát hiện khi OU structure bị thay đổi |
| `notify the company's operations team` | Alert/thông báo khi có thay đổi |
| `AWS Control Tower` | Managed service để thiết lập multi-account environment với governance |
| `drift detection` | Phát hiện sự khác biệt giữa cấu hình thực tế và cấu hình mong muốn |
| `LEAST operational overhead` | Giải pháp tự động, managed |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Phát hiện thay đổi OU hierarchy, notify operations team

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- AWS Control Tower cung cấp tính năng drift detection tự động: phát hiện khi OU hierarchy, guardrails, hoặc account structure bị thay đổi không qua Control Tower.
- Control Tower có thể tích hợp với Amazon SNS để gửi thông báo đến operations team.
- Đây là giải pháp managed, không cần tự xây dựng monitoring solution.
- Control Tower là landing zone manager cho Organizations, giúp quản lý multi-account environment one-stop.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B (Control Tower + Config rules):** AWS Config rules kiểm tra resource configurations, không phát hiện thay đổi OU hierarchy. Config rules không có khái niệm "aggregated rules" cho OU hierarchy.

**❌ Đáp án C (Service Catalog + CloudTrail):** Service Catalog không dùng để tạo accounts trong Organizations. CloudTrail organization trail ghi lại API calls nhưng tự phân tích và notify từ CloudTrail không đơn giản – cần kết hợp CloudWatch Events + Lambda, operational overhead cao hơn.

**❌ Đáp án D (CloudFormation + drift detection):** CloudFormation có drift detection nhưng dùng cho stack resources (VPC, EC2, v.v.), không phải cho OU hierarchy trong Organizations.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Control Tower drift detection = auto-detect OU/account changes. CloudTrail = API logging. CloudFormation drift = stack resources, not OUs."*
