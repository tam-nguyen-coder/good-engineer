# Question #127 - Topic 1

A media company is evaluating the possibility of moving its systems to the AWS Cloud. The company needs at least 10 TB of storage with the maximum possible I/O performance for video processing, 300 TB of very durable storage for storing media content, and 900 TB of storage to meet requirements for archival media that is not in use anymore. Which set of services should a solutions architect recommend to meet these requirements?

## Options

**A.** Amazon EBS for maximum performance, Amazon S3 for durable data storage, and Amazon S3 Glacier for archival storage

**B.** Amazon EBS for maximum performance, Amazon EFS for durable data storage, and Amazon S3 Glacier for archival storage

**C.** Amazon EC2 instance store for maximum performance, Amazon EFS for durable data storage, and Amazon S3 for archival storage

**D.** Amazon EC2 instance store for maximum performance, Amazon S3 for durable data storage, and Amazon S3 Glacier for archival storage

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Media company: 10TB video processing (max I/O), 300TB media content (durable), 900TB archive.
- **Existing Resources:** Chưa có.
- **Current Issue/Goal:** Match storage services to requirements.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `maximum possible I/O performance` | **EBS io1/io2** (provisioned IOPS) |
| `very durable storage` | **S3** (99.999999999% durability) |
| `archival media` | **S3 Glacier** (cheapest) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Storage
- **Constraints:** Performance, durability, archive

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **EBS** (io1/io2) — provisioned IOPS cho video processing, consistent high performance.
- **S3** — 11 9's durability cho media content.
- **S3 Glacier** — archival storage rẻ nhất.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- EFS không thể đạt I/O performance như EBS provisioned IOPS.

**❌ Đáp án C:**
- **Instance store** — ephemeral, data mất khi instance stop.
- EFS + S3 — EFS không "very durable" bằng S3 cho 300TB.

**❌ Đáp án D:**
- Instance store — không persistent, không phù hợp cho 10TB dữ liệu quan trọng cho video processing.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"EBS = max IOPS. S3 = max durability. Glacier = cheapest archive. Instance store = ephemeral"*
