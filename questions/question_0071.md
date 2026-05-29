# Question #71 - Topic 1

A company runs a shopping application that uses Amazon DynamoDB to store customer information. In case of data corruption, a solutions architect needs to design a solution that meets a recovery point objective (RPO) of 15 minutes and a recovery time objective (RTO) of 1 hour. What should the solutions architect recommend to meet these requirements?

## Options

**A.** Configure DynamoDB global tables. For RPO recovery, point the application to a different AWS Region.

**B.** Configure DynamoDB point-in-time recovery. For RPO recovery, restore to the desired point in time.

**C.** Export the DynamoDB data to Amazon S3 Glacier on a daily basis. For RPO recovery, import the data from S3 Glacier to DynamoDB.

**D.** Schedule Amazon Elastic Block Store (Amazon EBS) snapshots for the DynamoDB table every 15 minutes. For RPO recovery, restore the DynamoDB table by using the EBS snapshot.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** DynamoDB cho customer info, cần backup/restore khi data corruption.
- **Existing Resources:** DynamoDB table.
- **Current Issue/Goal:** RPO 15 phút, RTO 1 giờ.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `data corruption` | Cần point-in-time recovery để restore trước corruption |
| `RPO of 15 minutes` | Mất tối đa 15 phút dữ liệu |
| `RTO of 1 hour` | Khôi phục trong 1 giờ |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Disaster Recovery
- **Constraints:** RPO 15 min, RTO 1 hour

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **DynamoDB point-in-time recovery (PITR)** — continuous backup trong 35 ngày gần nhất, granularity 1 giây.
- RPO 15 phút — hoàn toàn đáp ứng (có thể restore đến bất kỳ điểm nào trong 1 giây).
- RTO 1 giờ — restore từ PITR thường trong vài phút đến vài chục phút.
- **Data corruption:** PITR cho phép restore về thời điểm trước corruption.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Global tables replicate data liên tục — nếu corruption xảy ra ở primary, nó cũng replicate sang secondary. Không giúp khôi phục từ corruption.

**❌ Đáp án C:**
- Daily S3 Glacier export → RPO = 1 ngày, không đáp ứng 15 phút.

**❌ Đáp án D:**
- DynamoDB không dùng EBS — không thể snapshot DynamoDB bằng EBS. Sai hoàn toàn về mặt kỹ thuật.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"PITR = continuous backup (35 days), 1-second granularity. Global tables ≠ DR từ corruption"*
