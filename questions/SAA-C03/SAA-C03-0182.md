# Question #182 - Topic 1

A company wants to migrate its MySQL database from on premises to AWS. The company recently experienced a database outage that significantly impacted the business. To ensure this does not happen again, the company wants a reliable database solution on AWS that minimizes data loss and stores every transaction on at least two nodes. Which solution meets these requirements?

## Options

**A.** Create an Amazon RDS DB instance with synchronous replication to three nodes in three Availability Zones.

**B.** Create an Amazon RDS MySQL DB instance with Multi-AZ functionality enabled to synchronously replicate the data.

**C.** Create an Amazon RDS MySQL DB instance and then create a read replica in a separate AWS Region that synchronously replicates the data.

**D.** Create an Amazon EC2 instance with a MySQL engine installed that triggers an AWS Lambda function to synchronously replicate the data to an Amazon RDS MySQL DB instance.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** MySQL migration to AWS. Previous outage → need HA + min data loss.
- **Existing Resources:** On-prem MySQL.
- **Current Issue/Goal:** Multi-node synchronous replication.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `every transaction on at least two nodes` | **Multi-AZ** (synchronous standby) |
| `minimizes data loss` | Synchronous replication |
| `reliable database solution` | RDS Multi-AZ |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** HA / Disaster Recovery
- **Constraints:** Synchronous replication, at least 2 nodes

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **RDS MySQL Multi-AZ** — synchronous replication từ primary → standby ở AZ khác.
- Automated failover nếu primary fails → HA.
- Mỗi transaction được ghi đồng bộ trên 2 nodes → minimize data loss.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- RDS không hỗ trợ synchronous replication đến 3 nodes.

**❌ Đáp án C:**
- Read replica — asynchronous replication, có thể mất dữ liệu.

**❌ Đáp án D:**
- EC2 MySQL + Lambda — overly complex, không reliable, synchronous qua Lambda không đảm bảo.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"RDS Multi-AZ = sync replication to standby. Read replica = async. 3 nodes sync = not supported"*
