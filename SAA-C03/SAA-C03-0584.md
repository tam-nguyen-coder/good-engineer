# Question #584 - Topic 1

A company is deploying an application that processes large quantities of data in parallel. The company plans to use Amazon EC2 instances for the workload. The network architecture must be configurable to prevent groups of nodes from sharing the same underlying hardware. Which networking solution meets these requirements?

## Options

**A.** Run the EC2 instances in a spread placement group.

**B.** Group the EC2 instances in separate accounts.

**C.** Configure the EC2 instances with dedicated tenancy.

**D.** Configure the EC2 instances with shared tenancy.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Parallel data processing, cần prevent groups of nodes from sharing same underlying hardware.
- **Existing Resources:** EC2 instances.
- **Current Issue/Goal:** Đảm bảo các instance không nằm trên cùng physical hardware.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `prevent groups of nodes from sharing the same underlying hardware` | Spread placement group: mỗi instance nằm trên different rack/hardware. |
| `spread placement group` | Tối đa 7 instances per AZ, mỗi instance trên different physical hardware. |
| `parallel` | Cần fault isolation. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Network architecture
- **Constraints:** Prevent same underlying hardware, parallel processing

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Spread placement group: mỗi EC2 instance được đặt trên different physical rack/hardware.
- Đảm bảo không có 2 instance nào chia sẻ cùng underlying hardware → tránh single point of failure hardware.
- Phù hợp với parallel processing cần fault isolation.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Separate accounts: không liên quan đến placement trên hardware.

**❌ Đáp án C:**
- Dedicated tenancy: instance chạy trên dedicated host/server, nhưng vẫn có thể nhiều instances trên cùng hardware.

**❌ Đáp án D:**
- Shared tenancy: mặc định, không đảm bảo separation.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Separate underlying hardware → Spread placement group (each instance = different rack). Dedicated tenancy ≠ hardware separation."*
