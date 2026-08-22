# Question #174 - Topic 1

A company has a multi-tier application that runs six front-end web servers in an Amazon EC2 Auto Scaling group in a single Availability Zone behind an Application Load Balancer (ALB). A solutions architect needs to modify the infrastructure to be highly available without modifying the application. Which architecture should the solutions architect choose that provides high availability?

## Options

**A.** Create an Auto Scaling group that uses three instances across each of two Regions.

**B.** Modify the Auto Scaling group to use three instances across each of two Availability Zones.

**C.** Create an Auto Scaling template that can be used to quickly create more instances in another Region.

**D.** Change the ALB in front of the Amazon EC2 instances in a round-robin configuration to balance traffic to the web tier.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** 6 front-end web servers in ASG, single AZ, behind ALB. Need HA without app modification.
- **Existing Resources:** ALB, Auto Scaling group, EC2 instances.
- **Current Issue/Goal:** HA by distributing across AZs.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `single Availability Zone` | Không HA |
| `without modifying the application` | Multi-AZ ASG, không cần thay đổi code |
| `highly available` | ASG across multiple AZs |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** High Availability
- **Constraints:** No app modification

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **ASG across 2 AZs** — nếu 1 AZ fails, instances ở AZ kia vẫn chạy.
- ALB tự động distribute traffic đến healthy instances across AZs.
- Không cần thay đổi application code.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Cross-Region — overkill, không cần thiết, tốn chi phí và độ trễ.

**❌ Đáp án C:**
- Template for another Region — không tự động, không HA ngay.

**❌ Đáp án D:**
- Round-robin ALB — đã có ALB rồi, không cải thiện HA.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Multi-AZ ASG = HA. Cross-Region = overkill. App modification = not needed"*
