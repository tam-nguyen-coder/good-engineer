# Question #232 - Topic 1

A company runs demonstration environments for its customers on Amazon EC2 instances. Each environment is isolated in its own VPC. The company's operations team needs to be notified when RDP or SSH access to an environment has been established.

## Options

**A.** Configure Amazon CloudWatch Application Insights to create AWS Systems Manager OpsItems when RDP or SSH access is detected.

**B.** Configure the EC2 instances with an IAM instance profile that has an IAM role with the AmazonSSMManagedInstanceCore policy attached.

**C.** Publish VPC flow logs to Amazon CloudWatch Logs. Create required metric filters. Create an Amazon CloudWatch metric alarm with a notification action for when the alarm is in the ALARM state.

**D.** Configure an Amazon EventBridge rule to listen for events of type EC2 Instance State-change Notification. Configure an Amazon Simple Notification Service (Amazon SNS) topic as a target. Subscribe the operations team to the topic.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Demo environments in isolated VPCs. Need notification when RDP/SSH access established.
- **Existing Resources:** EC2 instances in VPCs.
- **Current Issue/Goal:** Detect SSH/RDP connections.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `RDP or SSH access` | TCP port 3389 (RDP) and 22 (SSH) |
| `notified when... access has been established` | **VPC Flow Logs** capture connection events |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Monitoring / Security
- **Constraints:** Detect SSH/RDP, send notification

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **VPC Flow Logs** → CloudWatch Logs — ghi lại tất cả network traffic.
- **Metric filter** — lọc traffic trên port 22 (SSH) và 3389 (RDP).
- **CloudWatch alarm** + SNS notification — gửi alert khi phát hiện.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- CloudWatch Application Insights — cho application health, không phải RDP/SSH detection.

**❌ Đáp án B:**
- SSM ManagedInstanceCore — cho Systems Manager access, không phải notification.

**❌ Đáp án D:**
- EC2 State-change Notification — detect instance start/stop, không phải RDP/SSH.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"VPC Flow Logs + Metric Filter = detect SSH/RDP. State change = start/stop, not connections"*
