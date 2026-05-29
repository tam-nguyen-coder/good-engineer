# Question #167 - Topic 1

A company runs a production application on a fleet of Amazon EC2 instances. The application reads the data from an Amazon SQS queue and processes the messages in parallel. The message volume is unpredictable and often has intermittent traffic. This application should continually process messages without any downtime. Which solution meets these requirements MOST cost-effectively?

## Options

**A.** Use Spot Instances exclusively to handle the maximum capacity required.

**B.** Use Reserved Instances exclusively to handle the maximum capacity required.

**C.** Use Reserved Instances for the baseline capacity and use Spot Instances to handle additional capacity.

**D.** Use Reserved Instances for the baseline capacity and use On-Demand Instances to handle additional capacity.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 fleet processing SQS messages in parallel. Unpredictable traffic, intermittent bursts. No downtime allowed.
- **Existing Resources:** SQS queue, EC2 instances.
- **Current Issue/Goal:** Cost-effective capacity planning, no downtime.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `continually process messages without any downtime` | Cannot use **Spot only** (can be interrupted) |
| `intermittent traffic` | **Reserved for baseline + On-Demand for burst** |
| `most cost-effectively` | Reserved là rẻ nhất, On-Demand linh hoạt cho burst |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost optimization / Compute
- **Constraints:** No downtime, cost-effective, unpredictable traffic

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **Reserved Instances** — rẻ hơn On-Demand ~40-60%, dùng cho baseline capacity.
- **On-Demand Instances** — thêm cho burst traffic, không bị interruption như Spot.
- Đảm bảo no downtime và cost-effective.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Spot only — có thể bị reclaim, gây downtime.

**❌ Đáp án B:**
- Reserved only — phải mua cho max capacity, lãng phí khi traffic thấp.

**❌ Đáp án C:**
- Reserved baseline + Spot burst — Spot có thể bị reclaim, gây downtime.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Reserved = baseline (cheapest). On-Demand = burst (no interruption). Spot = cheapest but interruptible"*
