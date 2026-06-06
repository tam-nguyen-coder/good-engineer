# Question #629 - Topic 1

A company runs a production database on Amazon RDS for MySQL. The company wants to upgrade the database version for security compliance reasons. Because the database contains critical data, the company wants a quick solution to upgrade and test functionality without losing any data. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Create an RDS manual snapshot. Upgrade to the new version of Amazon RDS for MySQL.

**B.** Use native backup and restore. Restore the data to the upgraded new version of Amazon RDS for MySQL.

**C.** Use AWS Database Migration Service (AWS DMS) to replicate the data to the upgraded new version of Amazon RDS for MySQL.

**D.** Use Amazon RDS Blue/Green Deployments to deploy and test production changes.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Production RDS MySQL, cần upgrade DB version cho security compliance. Critical data, muốn quick upgrade + test functionality, no data loss.
- **Existing Resources:** Amazon RDS for MySQL.
- **Current Issue/Goal:** Database version upgrade với minimal risk và operational overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `upgrade the database version` | RDS version upgrade. |
| `test functionality without losing any data` | Cần staging environment để test. |
| `Blue/Green Deployments` | Tạo staging environment, sync data, test, switch over với minimal downtime. |
| `least operational overhead` | Blue/Green Deployments là managed feature của RDS. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Critical data, test before upgrade, no data loss

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- RDS Blue/Green Deployments: tạo một staging environment (green) song song với production (blue).
- Tự động replicate data từ blue sang green → green luôn đồng bộ.
- Có thể test ứng dụng với green environment trước khi switch.
- Switch nhanh chóng (typically < 1 minute), zero data loss, easy rollback.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Manual snapshot + upgrade: upgrade trực tiếp production, không có cơ hội test trước → rủi ro cao.

**❌ Đáp án B:**
- Native backup và restore: process thủ công, nhiều bước, operational overhead cao.

**❌ Đáp án C:**
- AWS DMS: dùng cho database migration, không phải upgrade tool. Cần tạo target instance, cấu hình replication → operational overhead cao hơn.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"RDS upgrade + test → Blue/Green Deployments (staging + switch). Snapshot/upgrade trực tiếp = risky."*
