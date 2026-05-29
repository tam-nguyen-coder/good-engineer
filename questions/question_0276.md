# Question #276 - Topic 1

A company has a multi-tier application deployed on several Amazon EC2 instances in an Auto Scaling group. An Amazon RDS for Oracle instance is the application's data layer that uses Oracle-specific PL/SQL functions. Traffic to the application has been steadily increasing. This is causing the EC2 instances to become overloaded and the RDS instance to run out of storage. The Auto Scaling group does not have any scaling metrics and defines the minimum healthy instance count only. The company predicts that traffic will continue to increase at a steady but unpredictable rate before leveling off. What should a solutions architect do to ensure the system can automatically scale for the increased traffic? (Choose two.)

## Options

**A.** Configure storage Auto Scaling on the RDS for Oracle instance.

**B.** Migrate the database to Amazon Aurora to use Auto Scaling storage.

**C.** Configure an alarm on the RDS for Oracle instance for low free storage space.

**D.** Configure the Auto Scaling group to use the average CPU as the scaling metric.

**E.** Configure the Auto Scaling group to use the average free memory as the scaling metric.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Multi-tier app, EC2 ASG + RDS Oracle. Traffic increasing. EC2 overloaded + RDS out of storage. ASG has no scaling metrics.
- **Existing Resources:** EC2 ASG, RDS Oracle.
- **Current Issue/Goal:** Auto-scale EC2 + auto-scale RDS storage.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `EC2 instances... overloaded` | **ASG scaling metric** — CPU |
| `RDS instance to run out of storage` | **Storage Auto Scaling** on RDS |
| `Oracle-specific PL/SQL functions` | Cannot migrate to Aurora (Oracle → Aurora không compatible) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Auto Scaling / Database
- **Constraints:** Chọn 2, Oracle-specific, auto-scale

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A và D**

**Giải thích:**
- **A: Storage Auto Scaling** on RDS Oracle — tự động tăng storage khi gần hết.
- **D: ASG average CPU metric** — scale EC2 instances dựa trên CPU utilization.
- Không thể migrate to Aurora vì Oracle-specific PL/SQL.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Migrate to Aurora — Oracle PL/SQL không compatible với Aurora.

**❌ Đáp án C:**
- Alarm on low storage — chỉ thông báo, không tự động scale.

**❌ Đáp án E:**
- Average free memory — CPU là metric phù hợp hơn cho application load.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Storage Auto Scaling = auto increase RDS storage. CPU metric = scale EC2. Oracle = can't migrate to Aurora"*
