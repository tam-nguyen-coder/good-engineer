# Question #76 - Topic 1

A company receives 10 TB of instrumentation data each day from several machines located at a single factory. The data consists of JSON files stored on a storage area network (SAN) in an on-premises data center located within the factory. The company wants to send this data to Amazon S3 where it can be accessed by several additional systems that provide critical near-real-time analytics. A secure transfer is important because the data is considered sensitive. Which solution offers the MOST reliable data transfer?

## Options

**A.** AWS DataSync over public internet

**B.** AWS DataSync over AWS Direct Connect

**C.** AWS Database Migration Service (AWS DMS) over public internet

**D.** AWS Database Migration Service (AWS DMS) over AWS Direct Connect

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** 10TB/day JSON data từ factory → S3, near-real-time analytics, sensitive data.
- **Existing Resources:** SAN on-prem, S3 bucket.
- **Current Issue/Goal:** Most reliable data transfer, secure.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `10 TB of instrumentation data each day` | Large volume — cần high bandwidth |
| `JSON files` | File data, không phải database |
| `most reliable` | Direct Connect (dedicated, stable) |
| `DataSync` | File transfer service (JSON files) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Data transfer
- **Constraints:** 10TB/day, sensitive, reliable, near-real-time

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **AWS DataSync** — chuyên cho file transfer on-prem ↔ AWS, tự động, encrypt in transit.
- **Direct Connect** — dedicated private connection, consistent performance, không qua public internet → **most reliable**.
- DataSync + DX = reliable, secure, high throughput cho 10TB/day.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- DataSync over public internet — vẫn hoạt động nhưng public internet có thể unreliable (congestion, packet loss).

**❌ Đáp án C:**
- **AWS DMS** — dành cho database migration, không phải file/JSON data.
- Public internet — unreliable.

**❌ Đáp án D:**
- DMS không phù hợp cho JSON files (database migration only).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"DataSync = file transfer. DMS = database migration. Direct Connect = most reliable. JSON files → DataSync"*
