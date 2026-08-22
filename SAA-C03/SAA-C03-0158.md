# Question #158 - Topic 1

A solutions architect is optimizing a website for an upcoming musical event. Videos of the performances will be streamed in real time and then will be available on demand. The event is expected to attract a global online audience. Which service will improve the performance of both the real-time and on-demand streaming?

## Options

**A.** Amazon CloudFront

**B.** AWS Global Accelerator

**C.** Amazon Route 53

**D.** Amazon S3 Transfer Acceleration

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Musical event, video streaming real-time + on-demand, global audience.
- **Existing Resources:** Chưa có.
- **Current Issue/Goal:** Improve both live and on-demand streaming performance.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `streamed in real time` | Live streaming |
| `available on demand` | VOD (Video on Demand) |
| `global online audience` | CDN edge |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Media streaming
- **Constraints:** Both live + on-demand, global

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **Amazon CloudFront** — hỗ trợ cả **live streaming** (với AWS Media Services) và **on-demand streaming**.
- Edge locations cache content gần user → giảm latency cho global audience.
- CloudFront supports both HLS and DASH protocols.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Global Accelerator — cải thiện TCP/UDP routing, không có streaming-specific features.

**❌ Đáp án C:**
- Route 53 — DNS routing, không improve streaming performance.

**❌ Đáp án D:**
- S3 Transfer Acceleration — fast upload to S3, không phải streaming delivery.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"CloudFront = live + on-demand streaming + global edge. S3 TA = upload acceleration only"*
