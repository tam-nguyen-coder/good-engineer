# Question #377 - Topic 1

A company recently deployed a new auditing system to centralize information about operating system versions, patching, and installed software for Amazon EC2 instances. A solutions architect must ensure all instances provisioned through EC2 Auto Scaling groups successfully send reports to the auditing system as soon as they are launched and terminated. Which solution achieves these goals MOST efficiently?

## Options

**A.** Use a scheduled AWS Lambda function and run a script remotely on all EC2 instances to send data to the audit system.

**B.** Use EC2 Auto Scaling lifecycle hooks to run a custom script to send data to the audit system when instances are launched and terminated.

**C.** Use an EC2 Auto Scaling launch configuration to run a custom script through user data to send data to the audit system when instances are launched and terminated.

**D.** Run a custom script on the instance operating system to send data to the audit system. Configure the script to be invoked by the EC2 Auto Scaling group when the instance starts and is terminated.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Auditing system needs reports từ EC2 instances khi launch và terminate (ASG). Most efficient.
- **Existing Resources:** EC2 Auto Scaling groups, auditing system.
- **Current Issue/Goal:** Report to audit system on instance launch and termination.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `launched and terminated` | Cần hành động ở cả 2 events. |
| `lifecycle hooks` | ASG lifecycle hooks: put instance in pending:wait or terminating:wait state → run custom script. |
| `user data` | Chỉ chạy khi launch, không chạy khi terminate. |
| `most efficiently` | Lifecycle hooks đảm bảo script chạy trước khi instance enters service / terminates. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most efficient
- **Constraints:** Report on launch AND terminate, ASG

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Lifecycle hooks: ASG đưa instance vào trạng thái pending:wait (khi launch) hoặc terminating:wait (khi terminate) → custom script chạy → complete hook để instance tiếp tục.
- Đảm bảo script chạy thành công trước khi instance enters service hoặc bị terminated.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Scheduled Lambda: không real-time, có thể bỏ sót instances (không trigger chính xác khi launch/terminate).

**❌ Đáp án C:**
- User data: chỉ chạy lần đầu khi instance launch, không chạy khi terminate.

**❌ Đáp án D:**
- ASG không có cơ chế invoke script khi start/stop. Lifecycle hooks là cơ chế chính thống.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Run script on launch AND terminate → Lifecycle hooks. User data = launch only. Lambda scheduled = không real-time."*
