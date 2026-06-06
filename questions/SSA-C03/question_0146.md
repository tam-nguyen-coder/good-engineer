# Question #146 - Topic 1

A company runs a stateless web application in production on a group of Amazon EC2 On-Demand Instances behind an Application Load Balancer. The application experiences heavy usage during an 8-hour period each business day. Application usage is moderate and steady overnight. Application usage is low during weekends. The company wants to minimize its EC2 costs without affecting the availability of the application. Which solution will meet these requirements?

## Options

**A.** Use Spot Instances for the entire workload.

**B.** Use Reserved Instances for the baseline level of usage. Use Spot instances for any additional capacity that the application needs.

**C.** Use On-Demand Instances for the baseline level of usage. Use Spot Instances for any additional capacity that the application needs.

**D.** Use Dedicated Instances for the baseline level of usage. Use On-Demand Instances for any additional capacity that the application needs.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Stateless web app, EC2 On-Demand + ALB. Heavy 8hrs weekday, moderate overnight, low weekend.
- **Existing Resources:** EC2 instances behind ALB.
- **Current Issue/Goal:** Minimize costs, không ảnh hưởng availability.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `baseline level of usage` | Phần capacity ổn định → **Reserved Instances** |
| `additional capacity` | Peak có thể dùng **Spot** |
| `without affecting availability` | Baseline phải reliable |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost optimization
- **Constraints:** Không ảnh hưởng availability

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **Reserved Instances** cho baseline — chạy 24/7, discount lớn, reliable.
- **Spot Instances** cho additional capacity — rẻ, stateless nên không sợ bị reclaim.
- Kết hợp RI + Spot = tối ưu cost cho predictable baseline + variable peak.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Spot cho entire workload — có thể bị terminate, ảnh hưởng availability.

**❌ Đáp án C:**
- On-Demand cho baseline — đắt hơn RI.

**❌ Đáp án D:**
- Dedicated Instances — đắt nhất, không cần thiết.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"RI = baseline (reliable + cheap). Spot = additional (cheapest). On-Demand = fallback (most expensive)"*
