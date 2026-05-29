# Question #607 - Topic 1

A company has migrated a two-tier application from its on-premises data center to the AWS Cloud. The data tier is a Multi-AZ deployment of Amazon RDS for Oracle with 12 TB of General Purpose SSD Amazon Elastic Block Store (Amazon EBS) storage. The application is designed to process and store documents in the database as binary large objects (blobs) with an average document size of 6 MB. The database size has grown over time, reducing the performance and increasing the cost of storage. The company must improve the database performance and needs a solution that is highly available and resilient. Which solution will meet these requirements MOST cost-effectively?

## Options

**A.** Reduce the RDS DB instance size. Increase the storage capacity to 24 TiB. Change the storage type to Magnetic.

**B.** Increase the RDS DB instance size. Increase the storage capacity to 24 TiB. Change the storage type to Provisioned IOPS.

**C.** Create an Amazon S3 bucket. Update the application to store documents in the S3 bucket. Store the object metadata in the existing database.

**D.** Create an Amazon DynamoDB table. Update the application to use DynamoDB. Use AWS Database Migration Service (AWS DMS) to migrate data from the Oracle database to DynamoDB.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** RDS for Oracle Multi-AZ, 12 TB GP2, lưu documents dạng BLOB (6 MB average). DB size lớn → performance giảm, cost tăng.
- **Existing Resources:** RDS for Oracle Multi-AZ, 12 TB GP2 EBS.
- **Current Issue/Goal:** Improve database performance, highly available, resilient, most cost-effective.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `binary large objects (blobs)` | File/document → nên tách khỏi database, lưu ở object storage (S3). |
| `6 MB average document size` | Quá lớn lưu trong DB → gây bloating, performance degradation. |
| `reducing performance, increasing cost` | DB phình to do BLOBs → cần offload BLOBs ra S3. |
| `highly available and resilient` | S3 có sẵn 99.999999999% durability, Multi-AZ. Metadata vẫn lưu trong RDS. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective
- **Constraints:** Improve performance, highly available, resilient

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Offload BLOBs từ RDS sang S3: S3 là object storage tối ưu cho file/large objects.
- Metadata (ID, path, description) vẫn giữ trong RDS Oracle.
- Giảm dung lượng RDS → cải thiện performance (backup, query).
- S3 durable (99.999999999%), highly available, cost-effective.
- Chi phí thấp hơn tăng instance size + Provisioned IOPS.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Magnetic là HDD cũ, chậm. Giảm instance size + tăng storage không giải quyết gốc vấn đề.
- Không cải thiện performance.

**❌ Đáp án B:**
- Tăng instance size + Provisioned IOPS → rất tốn kém.
- Giải pháp "thêm tiền" thay vì giải quyết root cause (BLOBs).

**❌ Đáp án D:**
- DynamoDB giới hạn item size 400 KB → không thể lưu 6 MB documents.
- Migrate từ Oracle sang DynamoDB là thay đổi lớn, không cost-effective.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"BLOB > 1 MB → offload lên S3, metadata trong DB. Đừng nhồi BLOB vào RDS."*
