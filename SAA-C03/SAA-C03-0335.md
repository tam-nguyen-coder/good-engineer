# Question #335 - Topic 1

A company is experiencing sudden increases in demand. The company needs to provision large Amazon EC2 instances from an Amazon Machine Image (AMI). The instances will run in an Auto Scaling group. The company needs a solution that provides minimum initialization latency to meet the demand. Which solution meets these requirements?

## Options

**A.** Use the aws ec2 register-image command to create an AMI from a snapshot. Use AWS Step Functions to replace the AMI in the Auto Scaling group.

**B.** Enable Amazon Elastic Block Store (Amazon EBS) fast snapshot restore on a snapshot. Provision an AMI by using the snapshot. Replace the AMI in the Auto Scaling group with the new AMI.

**C.** Enable AMI creation and define lifecycle rules in Amazon Data Lifecycle Manager (Amazon DLM). Create an AWS Lambda function that modifies the AMI in the Auto Scaling group.

**D.** Use Amazon EventBridge to invoke AWS Backup lifecycle policies that provision AMIs. Configure Auto Scaling group capacity limits as an event source in EventBridge.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Sudden demand spikes, cần provision large EC2 instances nhanh chóng với minimum initialization latency. ASG with AMI.
- **Existing Resources:** Auto Scaling group, AMI.
- **Current Issue/Goal:** Giảm initialization latency khi launch instances từ AMI.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `minimum initialization latency` | Cần EBS fast snapshot restore để initialize EBS volumes từ snapshot không bị lazy loading. |
| `EBS fast snapshot restore` | Loại bỏ quá trình lazy loading khi restore snapshot → full performance ngay lập tức. |
| `large Amazon EC2 instances` | EBS volumes lớn có thể mất thời gian initialize → fast snapshot restore khắc phục. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Minimum initialization latency
- **Constraints:** Auto Scaling group, AMI-based, large instances

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- EBS fast snapshot restore: khi enable trên snapshot, EBS volumes restored từ snapshot đó có full performance ngay lập tức (không bị lazy loading).
- AMI được tạo từ snapshot có fast snapshot restore → EC2 instances launch từ AMI này có initialization latency tối thiểu.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- register-image tạo AMI từ snapshot, không giải quyết vấn đề initialization latency. Step Functions không giúp tăng tốc launch.

**❌ Đáp án C:**
- DLM quản lý lifecycle của snapshots, không giảm latency. Lambda replace AMI trong ASG cũng không giúp.

**❌ Đáp án D:**
- AWS Backup provision AMIs nhưng không giải quyết initialization latency.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Minimum initialization latency when launching EC2 → EBS fast snapshot restore (no lazy loading)."*
