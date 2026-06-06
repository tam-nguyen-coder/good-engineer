# Question #34 - Topic 1

A company hosts its multi-tier applications on AWS. For compliance, governance, auditing, and security, the company must track configuration changes on its AWS resources and record a history of API calls made to these resources. What should a solutions architect do to meet these requirements?

## Options

**A.** Use AWS CloudTrail to track configuration changes and AWS Config to record API calls.

**B.** Use AWS Config to track configuration changes and AWS CloudTrail to record API calls.

**C.** Use AWS Config to track configuration changes and Amazon CloudWatch to record API calls.

**D.** Use AWS CloudTrail to track configuration changes and Amazon CloudWatch to record API calls.



 ---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Một công ty triển khai ứng dụng `multi-tier` trên `AWS`
- **Existing Resources:** Ứng dụng `multi-tier` đang chạy trên môi trường `AWS`
- **Current Issue/Goal:** Công ty cần đáp ứng các yêu cầu về `compliance`, `governance`, `auditing`, và `security` bằng cách theo dõi `configuration changes` trên `AWS resources` và ghi lại lịch sử các `API calls` thực hiện trên các resource này

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| track `configuration changes` | Chỉ `AWS Config` — dịch vụ chuyên `configuration management` và lưu trữ `configuration history` |
| record history of `API calls` | Chỉ `AWS CloudTrail` — dịch vụ `auditing` ghi lại mọi
