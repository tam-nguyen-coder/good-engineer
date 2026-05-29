# Question #372 - Topic 1

A company wants to migrate an Oracle database to AWS. The database consists of a single table that contains millions of geographic information systems (GIS) images that are high resolution and are identified by a geographic code. When a natural disaster occurs, tens of thousands of images get updated every few minutes. Each geographic code has a single image or row that is associated with it. The company wants a solution that is highly available and scalable during such events. Which solution meets these requirements MOST cost-effectively?

## Options

**A.** Store the images and geographic codes in a database table. Use Oracle running on an Amazon RDS Multi-AZ DB instance.

**B.** Store the images in Amazon S3 buckets. Use Amazon DynamoDB with the geographic code as the key and the image S3 URL as the value.

**C.** Store the images and geographic codes in an Amazon DynamoDB table. Configure DynamoDB Accelerator (DAX) during times of high load.

**D.** Store the images in Amazon S3 buckets. Store geographic codes and image S3 URLs in a database table. Use Oracle running on an Amazon RDS Multi-AZ DB instance.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Millions of high-res GIS images, geographic code key. Natural disaster: tens of thousands updates every few minutes. HA + scalable.
- **Existing Resources:** Oracle database with GIS images.
- **Current Issue/Goal:** HA, scalable, cost-effective migration.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `high resolution images` | Lưu trong S3 (scalable, durable, cost-effective cho large files). |
| `geographic code` | Partition key cho DynamoDB (fast lookups). |
| `tens of thousands updates every few minutes` | DynamoDB scalable writes. |
| `most cost-effectively` | S3 cho images + DynamoDB cho metadata (cheaper than RDS Oracle). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective, HA, scalable
- **Constraints:** Millions of images, high update rate during disasters

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- S3: lưu images (pay per GB, unlimited scalability, 11 9s durability).
- DynamoDB: geographic code as partition key, S3 URL as value → fast lookups, auto-scaling writes.
- Cost-effective hơn RDS Oracle (không cần license Oracle, S3 rẻ cho blobs).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- RDS Oracle: expensive (licensing), lưu images trực tiếp trong DB không cost-effective. Không scalable writes như DynamoDB.

**❌ Đáp án C:**
- DynamoDB max item size 400 KB → không thể lưu high-res images trong DynamoDB.

**❌ Đáp án D:**
- RDS Oracle: expensive, không scalable như S3 + DynamoDB.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Images → S3. Metadata + fast lookups → DynamoDB. RDS Oracle = expensive cho blobs."*
