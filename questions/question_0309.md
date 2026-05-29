# Question #309 - Topic 1

A solutions architect needs to optimize storage costs. The solutions architect must identify any Amazon S3 buckets that are no longer being accessed or are rarely accessed. Which solution will accomplish this goal with the LEAST operational overhead?

## Options

**A.** Analyze bucket access patterns by using the S3 Storage Lens dashboard for advanced activity metrics.

**B.** Analyze bucket access patterns by using the S3 dashboard in the AWS Management Console.

**C.** Turn on the Amazon CloudWatch BucketSizeBytes metric for buckets. Analyze bucket access patterns by using the metrics data with Amazon Athena.

**D.** Turn on AWS CloudTrail for S3 object monitoring. Analyze bucket access patterns by using CloudTrail logs that are integrated with Amazon CloudWatch Logs.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Cần tối ưu S3 storage cost bằng cách tìm buckets ít/không được access.
- **Existing Resources:** S3 buckets.
- **Current Issue/Goal:** Identify rarely/unused S3 buckets với least operational overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `S3 Storage Lens` | Dashboard có sẵn với advanced metrics: usage, activity, cost optimization. |
| `least operational overhead` | Không cần cấu hình phức tạp, dùng managed dashboard. |
| `advanced activity metrics` | Storage Lens cung cấp "Last accessed date", "Inactive buckets" metrics. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Identify rarely/unused S3 buckets

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- S3 Storage Lens là managed dashboard cung cấp sẵn advanced metrics như "Last accessed date", "Inactive buckets", "Storage usage trends".
- Không cần cấu hình gì thêm (chỉ cần enable Storage Lens) → operational overhead thấp nhất.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- S3 dashboard trong AWS Console chỉ hiện basic metrics (bucket size, object count), không có access pattern analysis.

**❌ Đáp án C:**
- CloudWatch BucketSizeBytes chỉ show bucket size, không phải access patterns. Cần Athena + CloudWatch Logs → operational overhead cao.

**❌ Đáp án D:**
- CloudTrail + CloudWatch Logs cần cấu hình, query logs → operational overhead cao hơn Storage Lens.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"S3 Storage Lens = sẵn dashboard + inactive bucket metrics. Không cần cấu hình CloudTrail/Athena."*
