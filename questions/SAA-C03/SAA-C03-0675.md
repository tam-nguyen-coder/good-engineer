# Question #675 - Topic 1

A company uses Amazon EC2 instances and Amazon Elastic Block Store (Amazon EBS) volumes to run an application. The company creates one snapshot of each EBS volume every day to meet compliance requirements. The company wants to implement an architecture that prevents the accidental deletion of EBS volume snapshots. The solution must not change the administrative rights of the storage administrator user. Which solution will meet these requirements with the LEAST administrative effort?

## Options

**A.** Create an IAM role that has permission to delete snapshots. Attach the role to a new EC2 instance. Use the AWS CLI from the new EC2 instance to delete snapshots.

**B.** Create an IAM policy that denies snapshot deletion. Attach the policy to the storage administrator user.

**C.** Add tags to the snapshots. Create retention rules in Recycle Bin for EBS snapshots that have the tags.

**D.** Lock the EBS snapshots to prevent deletion.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Daily EBS snapshots for compliance. Prevent accidental deletion. Cannot change admin rights.
- **Existing Resources:** EBS volumes and snapshots.
- **Current Issue/Goal:** Prevent accidental deletion without changing IAM permissions.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `accidental deletion` | Recycle Bin giữ lại deleted snapshots trong retention period. |
| `must not change the administrative rights` | Không thể modify IAM policy của admin. |
| `Recycle Bin` | Service giữ deleted resources trước khi permanently delete. |
| `least administrative effort` | Recycle Bin (có sẵn) > Lock snapshots (phải enable). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least administrative effort
- **Constraints:** Cannot change admin rights, prevent accidental deletion

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Recycle Bin cho EBS snapshots: khi snapshot bị delete, nó vào Recycle Bin (không mất ngay).
- Retention rules: giữ snapshot trong Recycle Bin trong thời gian config.
- Tag để xác định snapshots nào được bảo vệ.
- Không cần thay đổi IAM permissions → không ảnh hưởng admin rights.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Không giải quyết accidental deletion prevention.
- Tạo IAM role + EC2 instance → phức tạp.

**❌ Đáp án B:**
- Thay đổi IAM policy → violates "not change administrative rights".

**❌ Đáp án D:**
- EBS snapshot locking là feature mới, nhưng không phải tất cả regions support.
- Lock vĩnh viễn → không thể delete ngay cả khi cần.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Accidental deletion protection → Recycle Bin (safety net, no IAM changes)."*
