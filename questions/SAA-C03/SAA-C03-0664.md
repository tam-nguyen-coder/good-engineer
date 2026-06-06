# Question #664 - Topic 1

A company has a web application that runs on premises. The application experiences latency issues during peak hours. The latency issues occur twice each month. At the start of a latency issue, the application's CPU utilization immediately increases to 10 times its normal amount. The company wants to migrate the application to AWS to improve latency. The company also wants to scale the application automatically when application demand increases. The company will use AWS Elastic Beanstalk for application deployment. Which solution will meet these requirements?

## Options

**A.** Configure an Elastic Beanstalk environment to use burstable performance instances in unlimited mode. Configure the environment to scale based on requests.

**B.** Configure an Elastic Beanstalk environment to use compute optimized instances. Configure the environment to scale based on requests.

**C.** Configure an Elastic Beanstalk environment to use compute optimized instances. Configure the environment to scale on a schedule.

**D.** Configure an Elastic Beanstalk environment to use burstable performance instances in unlimited mode. Configure the environment to scale on predictive metrics.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Web app on-prem, latency issues twice/month during peak, CPU jumps 10x at start. Migrate to AWS, auto-scale. Use Elastic Beanstalk.
- **Existing Resources:** On-prem web application.
- **Current Issue/Goal:** Auto-scale, handle sudden CPU spikes, improve latency.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `CPU utilization immediately increases to 10 times` | Need burst capacity. Burstable instances (T series) with unlimited mode. |
| `twice each month` | Not predictable enough for scheduled scaling. |
| `scale based on requests` | Dynamic scaling based on request count (reactive). |
| `burstable performance instances unlimited` | T3/T4g unlimited: can burst CPU beyond baseline, pay extra for burst. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements
- **Constraints:** Auto-scale, sudden CPU spikes, Elastic Beanstalk

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **Burstable performance instances (T series) unlimited mode:** có thể burst CPU lên 10x khi cần, phù hợp với pattern CPU spike ngắn.
- **Scale based on requests:** Elastic Beanstalk auto-scaling dựa trên request count → scale khi traffic tăng.
- Kết hợp: burstable instances xử lý CPU spike ngay lập tức, auto-scaling thêm instances cho sustained load.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Compute optimized instances (C series) giá cao hơn, chạy full CPU ổn định nhưng không thiết kế cho burst pattern.
- Scale based on requests: tốt, nhưng compute optimized đắt hơn necessary.

**❌ Đáp án C:**
- Compute optimized: đắt hơn cần thiết.
- Scale on schedule: không phù hợp (chỉ xảy ra 2 lần/tháng, unpredictable specific days).

**❌ Đáp án D:**
- Predictive scaling dựa trên historical data để dự đoán traffic → cần history, không phù hợp cho pattern chỉ 2 lần/tháng.
- Predictive scaling là tính năng của Auto Scaling, Elastic Beanstalk dùng được.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Sudden CPU spikes → burstable unlimited (T series). Scale based on requests for dynamic load."*
