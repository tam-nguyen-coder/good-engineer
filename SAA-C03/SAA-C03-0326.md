# Question #326 - Topic 1

An image hosting company uploads its large assets to Amazon S3 Standard buckets. The company uses multipart upload in parallel by using S3 APIs and overwrites if the same object is uploaded again. For the first 30 days after upload, the objects will be accessed frequently. The objects will be used less frequently after 30 days, but the access patterns for each object will be inconsistent. The company must optimize its S3 storage costs while maintaining high availability and resiliency of stored assets. Which combination of actions should a solutions architect recommend to meet these requirements? (Choose two.)

## Options

**A.** Move assets to S3 Intelligent-Tiering after 30 days.

**B.** Configure an S3 Lifecycle policy to clean up incomplete multipart uploads.

**C.** Configure an S3 Lifecycle policy to clean up expired object delete markers.

**D.** Move assets to S3 Standard-Infrequent Access (S3 Standard-IA) after 30 days.

**E.** Move assets to S3 One Zone-Infrequent Access (S3 One Zone-IA) after 30 days.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Large assets in S3 Standard, multipart upload, overwrites. Frequent access first 30 days, less frequent + inconsistent after 30 days. Optimize cost, high availability, resiliency.
- **Existing Resources:** S3 Standard buckets.
- **Current Issue/Goal:** Cost optimization, HA, resiliency.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `access patterns will be inconsistent` | Intelligent-Tiering tự động chuyển đổi giữa access tiers dựa trên access pattern. |
| `Intelligent-Tiering` | Auto move objects giữa Frequent Access và Infrequent Access dựa trên usage. |
| `multipart upload` | Failed uploads tạo parts không complete → tốn cost. |
| `clean up incomplete multipart uploads` | Lifecycle policy: xóa incomplete multipart upload parts để tiết kiệm cost. |
| `high availability and resiliency` | Không dùng One Zone (kém HA). Intelligent-Tiering duy trì HA. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Choose two, cost optimization
- **Constraints:** HA, resiliency, inconsistent access after 30 days

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A và B**

**Giải thích:**
- **A (Intelligent-Tiering):** Sau 30 days, access inconsistent → Intelligent-Tiering tự động move objects giữa Frequent và Infrequent Access tiers dựa trên actual usage → tối ưu cost mà không cần predict pattern.
- **B (Cleanup incomplete multipart uploads):** Multipart upload có thể tạo parts không complete → lifecycle policy delete các parts sau 1-7 days → tiết kiệm cost.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án C:**
- Expired object delete markers chỉ áp dụng cho buckets có versioning enabled, không liên quan đến scenario này.

**❌ Đáp án D:**
- S3 Standard-IA: cost thấp hơn Standard nhưng có retrieval fee. Không tối ưu cho access patterns inconsistent (vì không biết khi nào object được access).

**❌ Đáp án E:**
- S3 One Zone-IA: không đáp ứng "high availability and resiliency" (dữ liệu chỉ ở 1 AZ).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Inconsistent access → S3 Intelligent-Tiering (auto). Multipart upload → lifecycle cleanup incomplete parts. One Zone = không HA."*
