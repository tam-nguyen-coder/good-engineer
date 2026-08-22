# Question #121 - Topic 1

A company is running an online transaction processing (OLTP) workload on AWS. This workload uses an unencrypted Amazon RDS DB instance in a Multi-AZ deployment. Daily database snapshots are taken from this instance. What should a solutions architect do to ensure the database and snapshots are always encrypted moving forward?

## Options

**A.** Encrypt a copy of the latest DB snapshot. Replace existing DB instance by restoring the encrypted snapshot.

**B.** Create a new encrypted Amazon Elastic Block Store (Amazon EBS) volume and copy the snapshots to it. Enable encryption on the DB instance.

**C.** Copy the snapshots and enable encryption using AWS Key Management Service (AWS KMS) Restore encrypted snapshot to an existing DB instance.

**D.** Copy the snapshots to an Amazon S3 bucket that is encrypted using server-side encryption with AWS Key Management Service (AWS KMS) managed keys (SSE-KMS).

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Unencrypted RDS Multi-AZ với daily snapshots. Cần encrypt từ bây giờ.
- **Existing Resources:** RDS DB instance (unencrypted), daily snapshots.
- **Current Issue/Goal:** Encrypt DB + snapshots moving forward.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `snapshots are always encrypted moving forward` | Encrypt snapshot → restore → new encrypted DB |
| `unencrypted` | Không thể enable encryption trực tiếp trên existing DB |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / Encryption
- **Constraints:** RDS, snapshot encryption

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **Encrypt a copy of the latest snapshot** — tạo bản sao có encrypt.
- **Restore từ encrypted snapshot** → DB instance mới đã được encrypt.
- Đây là cách duy nhất để encrypt RDS DB instance.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- RDS không cho phép can thiệp EBS trực tiếp.
- Không thể "enable encryption on existing DB instance".

**❌ Đáp án C:**
- Không thể restore encrypted snapshot vào existing unencrypted instance.

**❌ Đáp án D:**
- Copy snapshot ra S3 — RDS không restore từ S3.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Encrypt snapshot copy → restore → new encrypted DB. Cannot enable encryption on existing RDS directly"*
