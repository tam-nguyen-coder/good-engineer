# Question #70 - Topic 1

A company's HTTP application is behind a Network Load Balancer (NLB). The NLB's target group is configured to use an Amazon EC2 Auto Scaling group with multiple EC2 instances that run the web service. The company notices that the NLB is not detecting HTTP errors for the application. These errors require a manual restart of the EC2 instances that run the web service. The company needs to improve the application's availability without writing custom scripts or code. What should a solutions architect do to meet these requirements?

## Options

**A.** Enable HTTP health checks on the NLB, supplying the URL of the company's application.

**B.** Add a cron job to the EC2 instances to check the local application's logs once each minute. If HTTP errors are detected. the application will restart.

**C.** Replace the NLB with an Application Load Balancer. Enable HTTP health checks by supplying the URL of the company's application. Configure an Auto Scaling action to replace unhealthy instances.

**D.** Create an Amazon Cloud Watch alarm that monitors the UnhealthyHostCount metric for the NLB. Configure an Auto Scaling action to replace unhealthy instances when the alarm is in the ALARM state.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** HTTP app sau NLB, NLB không detect HTTP errors, cần manual restart EC2.
- **Existing Resources:** NLB, EC2 ASG.
- **Current Issue/Goal:** Auto-detect HTTP errors, replace unhealthy instances, no custom scripts.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `HTTP errors` | Layer 7 — NLB là layer 4, không hiểu HTTP |
| `without writing custom scripts or code` | Không dùng cron job, Lambda, etc. |
| `manual restart of the EC2 instances` | Cần auto health check + auto replacement |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** High Availability
- **Constraints:** No custom code, HTTP health check

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **NLB chỉ hỗ trợ TCP/health check (layer 4)** — không thể detect HTTP errors.
- **ALB hỗ trợ HTTP health checks (layer 7)** — có thể check specific URL path và HTTP status code.
- Auto Scaling action với ALB health check → tự động replace unhealthy instances.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- **NLB không hỗ trợ HTTP health checks** — chỉ TCP, HTTPS (nhưng không check nội dung response).

**❌ Đáp án B:**
- **Cron job** là custom script — vi phạm "without writing custom scripts or code".

**❌ Đáp án D:**
- UnhealthyHostCount metric chỉ phản ánh số lượng target unhealthy — NLB vẫn không detect được HTTP errors để đánh dấu target unhealthy.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"NLB = Layer 4 (TCP health check). ALB = Layer 7 (HTTP health check). HTTP errors → ALB"*
