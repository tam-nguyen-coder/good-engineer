# Question #277 - Topic 1

A company provides an online service for posting video content and transcoding it for use by any mobile platform. The application architecture uses Amazon Elastic File System (Amazon EFS) Standard to collect and store the videos so that multiple Amazon EC2 Linux instances can access the video content for processing. As the popularity of the service has grown over time, the storage costs have become too expensive. Which storage solution is MOST cost-effective?

## Options

**A.** Use AWS Storage Gateway for files to store and process the video content.

**B.** Use AWS Storage Gateway for volumes to store and process the video content.

**C.** Use Amazon EFS for storing the video content. Once processing is complete, transfer the files to Amazon Elastic Block Store (Amazon EBS).

**D.** Use Amazon S3 for storing the video content. Move the files temporarily over to an Amazon Elastic Block Store (Amazon EBS) volume attached to the server for processing.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Video content, EC2 Linux instances process videos. Using EFS Standard, storage costs too high.
- **Existing Resources:** EC2 instances, EFS.
- **Current Issue/Goal:** Reduce storage costs.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `storage costs have become too expensive` | EFS đắt → **S3** rẻ hơn |
| `multiple... EC2 Linux instances` | S3 scalable concurrent access |
| `processing` | Cần EBS for temp processing |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Storage / Cost optimization
- **Constraints:** Reduce cost, EC2 processing

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **S3** — rẻ hơn EFS cho video storage.
- Copy file từ S3 → **EBS volume** (tạm thời) → EC2 process.
- Sau processing, kết quả lưu lại S3.
- Cost-effective: S3 ($23/TB) vs EFS Standard ($30/TB) + Infrequent Access ($16/TB).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Storage Gateway for files — hybrid, không cost-effective hơn S3.

**❌ Đáp án B:**
- Volume gateway — block storage, không phù hợp video content.

**❌ Đáp án C:**
- EFS + EBS — vẫn dùng EFS đắt.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"S3 = cheapest for video storage. EBS = temp processing. EFS = expensive for large-scale"*
