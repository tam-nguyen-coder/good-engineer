# Question #302 - Topic 1

A company wants to create a mobile app that allows users to stream slow-motion video clips on their mobile devices. Currently, the app captures video clips and uploads the video clips in raw format into an Amazon S3 bucket. The app retrieves these video clips directly from the S3 bucket. However, the videos are large in their raw format. Users are experiencing issues with buffering and playback on mobile devices. The company wants to implement solutions to maximize the performance and scalability of the app while minimizing operational overhead. Which combination of solutions will meet these requirements? (Choose two.)

## Options

**A.** Deploy Amazon CloudFront for content delivery and caching.

**B.** Use AWS DataSync to replicate the video files across AW'S Regions in other S3 buckets.

**C.** Use Amazon Elastic Transcoder to convert the video files to more appropriate formats.

**D.** Deploy an Auto Sealing group of Amazon EC2 instances in Local Zones for content delivery and caching.

**E.** Deploy an Auto Scaling group of Amazon EC2 instances to convert the video files to more appropriate formats.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Mobile app upload/download raw video từ S3. Videos large, buffering issues. Cần maximize performance & scalability, minimize operational overhead.
- **Existing Resources:** S3 bucket với raw video files.
- **Current Issue/Goal:** Giảm buffering, cải thiện playback, scalable, managed services.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `buffering and playback` | Video raw quá lớn → cần transcoding và CDN. |
| `Amazon CloudFront` | CDN: cache nội dung tại edge, giảm latency cho global users. |
| `Amazon Elastic Transcoder` | Managed media transcoding service → convert raw video sang format phù hợp cho mobile (smaller, streamable). |
| `minimizing operational overhead` | Dùng managed services (Elastic Transcoder, CloudFront), không tự quản EC2. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Choose two, maximize performance & scalability, minimize operational overhead
- **Constraints:** Mobile streaming, reduce buffering

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A (CloudFront) và C (Elastic Transcoder)**

**Giải thích:**
- CloudFront: CDN cache video tại edge locations, giảm latency và buffering cho users worldwide.
- Elastic Transcoder: Convert raw video sang format nhỏ hơn (H.264, H.265) phù hợp mobile streaming → giảm buffering và cải thiện playback.
- Cả hai đều là managed services → minimize operational overhead.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- DataSync replication across regions không giúp giảm buffering hay transcoding. Chỉ copy data.

**❌ Đáp án D:**
- Auto Scaling EC2 trong Local Zones cho content delivery → operational overhead cao hơn CloudFront managed service.

**❌ Đáp án E:**
- EC2 Auto Scaling để convert video → operational overhead cao hơn Elastic Transcoder (managed).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Large video + buffering + mobile → Elastic Transcoder (transcode) + CloudFront (CDN). Managed services cho operational overhead thấp."*
