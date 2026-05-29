# Question #274 - Topic 1

A company runs an application on Amazon EC2 instances. The company needs to implement a disaster recovery (DR) solution for the application. The DR solution needs to have a recovery time objective (RTO) of less than 4 hours. The DR solution also needs to use the fewest possible AWS resources during normal operations. Which solution will meet these requirements in the MOST operationally efficient way?

## Options

**A.** Create Amazon Machine Images (AMIs) to back up the EC2 instances. Copy the AMIs to a secondary AWS Region. Automate infrastructure deployment in the secondary Region by using AWS Lambda and custom scripts.

**B.** Create Amazon Machine Images (AMIs) to back up the EC2 instances. Copy the AMIs to a secondary AWS Region. Automate infrastructure deployment in the secondary Region by using AWS CloudFormation.

**C.** Launch EC2 instances in a secondary AWS Region. Keep the EC2 instances in the secondary Region active at all times.

**D.** Launch EC2 instances in a secondary Availability Zone. Keep the EC2 instances in the secondary Availability Zone active at all times.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 app DR. RTO < 4 hours. Fewest resources during normal ops. Most operationally efficient.
- **Existing Resources:** EC2 instances.
- **Current Issue/Goal:** Backup and restore approach.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `fewest possible AWS resources during normal operations` | **Backup and restore** (pilot light / no active resources) |
| `RTO of less than 4 hours` | Backup and restore có thể đạt RTO < 4h |
| `most operationally efficient` | **CloudFormation** để automate deployment |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Disaster Recovery
- **Constraints:** RTO < 4h, minimal resources normally

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **AMI** — back up EC2 instances.
- Copy AMI sang secondary Region.
- **CloudFormation** — automate deploy infrastructure từ AMI → RTO < 4h.
- Zero active resources in DR Region → fewest resources.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Lambda + custom scripts — operational overhead cao hơn CloudFormation.

**❌ Đáp án C:**
- Active EC2 in DR Region — resources chạy liên tục, tốn chi phí.

**❌ Đáp án D:**
- Active EC2 in secondary AZ — cùng Region, không cross-Region DR, resources chạy liên tục.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"AMI + CloudFormation = backup and restore (lowest cost). Active resources = always running (more cost)"*
