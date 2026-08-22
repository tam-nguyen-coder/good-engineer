# Question #173 - Topic 1

A gaming company hosts a browser-based application on AWS. The users of the application consume a large number of videos and images that are stored in Amazon S3. This content is the same for all users. The application has increased in popularity, and millions of users worldwide accessing these media files. The company wants to provide the files to the users while reducing the load on the origin. Which solution meets these requirements MOST cost-effectively?

## Options

**A.** Deploy an AWS Global Accelerator accelerator in front of the web servers.

**B.** Deploy an Amazon CloudFront web distribution in front of the S3 bucket.

**C.** Deploy an Amazon ElastiCache for Redis instance in front of the web servers.

**D.** Deploy an Amazon ElastiCache for Memcached instance in front of the web servers.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Gaming app, millions of users, videos/images in S3, same content for all. Reduce origin load.
- **Existing Resources:** App on web servers, S3 bucket.
- **Current Issue/Goal:** Reduce origin load, cost-effective.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `millions of users worldwide` | Cần **CDN** |
| `same for all users` | Static content, perfectly cacheable |
| `reducing the load on the origin` | Edge caching |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** CDN / Caching
- **Constraints:** Reduce origin load, cost-effective, global

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **CloudFront** — CDN cache videos/images tại edge locations.
- Static content same for all users → tỉ lệ cache hit cao → giảm load trên S3 origin.
- Cost-effective so với serving trực tiếp từ S3 cho millions of users.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Global Accelerator — cải thiện routing, không cache content, không giảm origin load.

**❌ Đáp án C:**
- ElastiCache Redis — in-memory cache cho dynamic data, không phù hợp media files.

**❌ Đáp án D:**
- ElastiCache Memcached — tương tự Redis, không phù hợp.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"CloudFront + S3 = CDN for static media. Global Accelerator = routing only. ElastiCache = dynamic data cache"*
