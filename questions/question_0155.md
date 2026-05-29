# Question #155 - Topic 1

A large media company hosts a web application on AWS. The company wants to start caching confidential media files so that users around the world will have reliable access to the files. The content is stored in Amazon S3 buckets. The company must deliver the content quickly, regardless of where the requests originate geographically. Which solution will meet these requirements?

## Options

**A.** Use AWS DataSync to connect the S3 buckets to the web application.

**B.** Deploy AWS Global Accelerator to connect the S3 buckets to the web application.

**C.** Deploy Amazon CloudFront to connect the S3 buckets to CloudFront edge servers.

**D.** Use Amazon Simple Queue Service (Amazon SQS) to connect the S3 buckets to the web application.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Media company, confidential files in S3, global users, fast delivery.
- **Existing Resources:** S3 buckets.
- **Current Issue/Goal:** Global content delivery with caching.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `caching` | **CloudFront** (CDN cache) |
| `users around the world` | Need edge locations |
| `deliver the content quickly` | CDN |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Content delivery
- **Constraints:** Global, fast, caching

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **CloudFront** — CDN global với edge servers, cache content gần user.
- Origin là S3 bucket — CloudFront lấy files từ S3 và cache tại edge.
- **Confidential files** — CloudFront hỗ trợ signed URLs/cookies và OAI để secure access.
- Fast delivery — edge locations giảm latency.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- **DataSync** — data transfer tool, không phải content delivery.

**❌ Đáp án B:**
- **Global Accelerator** — cải thiện TCP/UDP routing, không có caching.

**❌ Đáp án D:**
- **SQS** — message queue, không phải content delivery.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"CloudFront = CDN + caching + global edge. DataSync = transfer. Global Accelerator = routing (no cache)"*
