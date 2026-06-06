# Question #230 - Topic 1

A company is concerned that two NAT instances in use will no longer be able to support the traffic needed for the company's application. A solutions architect wants to implement a solution that is highly available, fault tolerant, and automatically scalable. What should the solutions architect recommend?

## Options

**A.** Remove the two NAT instances and replace them with two NAT gateways in the same Availability Zone.

**B.** Use Auto Scaling groups with Network Load Balancers for the NAT instances in different Availability Zones.

**C.** Remove the two NAT instances and replace them with two NAT gateways in different Availability Zones.

**D.** Replace the two NAT instances with Spot Instances in different Availability Zones and deploy a Network Load Balancer.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Two NAT instances can't handle traffic. Need HA, fault tolerant, auto-scalable.
- **Existing Resources:** NAT instances.
- **Current Issue/Goal:** Replace with managed NAT gateways.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `highly available, fault tolerant` | **NAT gateways in different AZs** |
| `automatically scalable` | NAT Gateway tự động scale (up to 45 Gbps) |
| `NAT instances` | Self-managed, thay bằng managed service |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Networking / NAT
- **Constraints:** HA, fault tolerant, auto-scalable

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **NAT Gateway** — managed service, tự động scale.
- **Two NAT gateways in different AZs** — HA (nếu 1 AZ fails, AZ kia vẫn hoạt động).
- Each NAT Gateway trong AZ của nó, route table per AZ.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Same AZ — không fault tolerant (AZ failure).

**❌ Đáp án B:**
- ASG + NLB cho NAT instances — vẫn quản lý instances.

**❌ Đáp án D:**
- Spot Instances — có thể bị reclaim, không reliable.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"NAT Gateway = managed, auto-scale. Multi-AZ = HA. NAT instances = more overhead"*
