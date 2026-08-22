# Question #573 - Topic 1

A company wants to use an event-driven programming model with AWS Lambda. The company wants to reduce startup latency for Lambda functions that run on Java 11. The company does not have strict latency requirements for the applications. The company wants to reduce cold starts and outlier latencies when a function scales up. Which solution will meet these requirements MOST cost-effectively?

## Options

**A.** Configure Lambda provisioned concurrency.

**B.** Increase the timeout of the Lambda functions.

**C.** Increase the memory of the Lambda functions.

**D.** Configure Lambda SnapStart.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Lambda Java 11 functions, muốn giảm cold start latency và outlier latencies khi scale up.
- **Existing Resources:** Lambda functions Java 11.
- **Current Issue/Goal:** Giảm cold start, cost-effective, không strict latency requirements.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Java 11` | Lambda SnapStart hỗ trợ Java 11+ (cả Java 17, 21). |
| `cold starts` | SnapStart giảm cold start bằng cách snapshot execution environment. |
| `no strict latency` | Không cần provisioned concurrency (đắt). SnapStart là cost-effective choice. |
| `MOST cost-effectively` | SnapStart miễn phí, không tốn thêm chi phí. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effectively
- **Constraints:** Java 11, reduce cold starts, no strict latency

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- Lambda SnapStart: tạo snapshot của execution environment sau initialization → khởi động nhanh hơn.
- Hỗ trợ Java 11 (và Java 17, 21).
- Miễn phí → cost-effective nhất.
- Giảm cold start mà không cần provisioned concurrency (tốn phí).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Provisioned concurrency giảm cold start nhưng tốn phí (pay for always-on capacity). Không cost-effective.

**❌ Đáp án B:**
- Tăng timeout không giảm cold start latency; chỉ ảnh hưởng max execution time.

**❌ Đáp án C:**
- Tăng memory có thể giảm cold start một chút (vì CPU proportional), nhưng không hiệu quả bằng SnapStart và tốn thêm chi phí.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Java cold start → SnapStart (free). Provisioned concurrency = expensive. Memory increase = marginal + costly."*
