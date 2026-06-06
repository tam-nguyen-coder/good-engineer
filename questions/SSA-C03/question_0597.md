# Question #597 - Topic 1

A company hosts an internal serverless application on AWS by using Amazon API Gateway and AWS Lambda. The company's employees report issues with high latency when they begin using the application each day. The company wants to reduce latency. Which solution will meet these requirements?

## Options

**A.** Increase the API Gateway throttling limit.

**B.** Set up a scheduled scaling to increase Lambda provisioned concurrency before employees begin to use the application each day.

**C.** Create an Amazon CloudWatch alarm to initiate a Lambda function as a target for the alarm at the beginning of each day.

**D.** Increase the Lambda function memory.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** API Gateway + Lambda, employees report high latency at start of each day.
- **Existing Resources:** API Gateway, Lambda.
- **Current Issue/Goal:** Reduce latency caused by cold starts at beginning of day.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `high latency when they begin using the application each day` | Lambda cold starts: khi không có traffic qua đêm, functions bị cold start sáng hôm sau. |
| `provisioned concurrency` | Keep Lambda functions warm, eliminate cold starts. |
| `scheduled scaling` | Dùng schedule để tăng provisioned concurrency trước giờ employees bắt đầu làm việc. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Reduce latency
- **Constraints:** Internal app, daily usage pattern

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Provisioned concurrency: giữ Lambda functions initialized sẵn sàng → zero cold start latency.
- Scheduled scaling: tăng lên trước giờ làm việc, giảm xuống sau giờ làm → cost-effective.
- Giải quyết đúng nguyên nhân: cold start sau thời gian không hoạt động.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- API Gateway throttling limit: giới hạn số requests, không ảnh hưởng cold start latency.

**❌ Đáp án C:**
- CloudWatch alarm + Lambda: không trực tiếp giải quyết cold starts. Alarm không pre-warm functions.

**❌ Đáp án D:**
- Tăng memory: có thể giảm cold start một chút nhưng không triệt để. Tốn thêm cost.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Daily cold start latency → Scheduled provisioned concurrency (pre-warm before work hours). Memory increase = marginal improvement."*
