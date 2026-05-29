# Question #262 - Topic 1

A company plans to use Amazon ElastiCache for its multi-tier web application. A solutions architect creates a Cache VPC for the ElastiCache cluster and an App VPC for the application's Amazon EC2 instances. Both VPCs are in the us-east-1 Region. The solutions architect must implement a solution to provide the application's EC2 instances with access to the ElastiCache cluster. Which solution will meet these requirements MOST cost-effectively?

## Options

**A.** Create a peering connection between the VPCs. Add a route table entry for the peering connection in both VPCs. Configure an inbound rule for the ElastiCache cluster's security group to allow inbound connection from the application's security group.

**B.** Create a Transit VPC. Update the VPC route tables in the Cache VPC and the App VPC to route traffic through the Transit VPC. Configure an inbound rule for the ElastiCache cluster's security group to allow inbound connection from the application's security group.

**C.** Create a peering connection between the VPCs. Add a route table entry for the peering connection in both VPCs. Configure an inbound rule for the peering connection's security group to allow inbound connection from the application's security group.

**D.** Create a Transit VPC. Update the VPC route tables in the Cache VPC and the App VPC to route traffic through the Transit VPC. Configure an inbound rule for the Transit VPC's security group to allow inbound connection from the application's security group.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Cache VPC (ElastiCache) + App VPC (EC2). Both same Region. Need EC2 → ElastiCache access.
- **Existing Resources:** Two VPCs.
- **Current Issue/Goal:** VPC-to-VPC connectivity, most cost-effective.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `both VPCs are in the us-east-1 Region` | Same Region → **VPC peering** (free) |
| `most cost-effectively` | VPC peering (no extra cost) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Networking / VPC
- **Constraints:** Same Region, cost-effective

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **VPC peering** — kết nối 2 VPCs trong cùng Region, free (chỉ trả cho data transfer).
- Route tables + security group (ElastiCache SG allow từ App SG).
- Đơn giản, không cần Transit VPC hay intermediate.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Transit VPC — phức tạp, tốn kém hơn VPC peering.

**❌ Đáp án C:**
- Peering connection's security group — không có khái niệm này.

**❌ Đáp án D:**
- Transit VPC SG — sai approach, tốn kém.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"VPC peering = simplest, cheapest cross-VPC. Transit VPC = more complex"*
