# Question #627 - Topic 1

A company wants to migrate two DNS servers to AWS. The servers host a total of approximately 200 zones and receive 1 million requests each day on average. The company wants to maximize availability while minimizing the operational overhead that is related to the management of the two servers. What should a solutions architect recommend to meet these requirements?

## Options

**A.** Create 200 new hosted zones in the Amazon Route 53 console. Import zone files.

**B.** Launch a single large Amazon EC2 instance. Import zone files. Configure Amazon CloudWatch alarms and notifications to alert the company about any downtime.

**C.** Migrate the servers to AWS by using AWS Server Migration Service (AWS SMS). Configure Amazon CloudWatch alarms and notifications to alert the company about any downtime.

**D.** Launch an Amazon EC2 instance in an Auto Scaling group across two Availability Zones. Import zone files. Set the desired capacity to 1 and the maximum capacity to 3 for the Auto Scaling group. Configure scaling alarms to scale based on CPU utilization.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Migrate 2 DNS servers (~200 zones, 1M requests/day) lên AWS. Cần maximize availability, minimize operational overhead.
- **Existing Resources:** 2 on-premises DNS servers, ~200 zones.
- **Current Issue/Goal:** Managed DNS solution để giảm operational overhead, high availability.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `maximize availability` | Route 53 là managed DNS, 100% SLA. |
| `minimizing operational overhead` | Route 53: không cần quản lý servers, patches, scaling. |
| `200 zones, 1 million requests/day` | Route 53 có thể handle dễ dàng. |
| `management of the two servers` | Không muốn quản lý EC2 instances cho DNS. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Maximize availability, minimize operational overhead
- **Constraints:** ~200 zones, 1M requests/day

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Amazon Route 53 là managed DNS service, không cần quản lý server infrastructure.
- 200 hosted zones, 1M requests/day → Route 53 xử lý dễ dàng với SLA 100%.
- Import zone files từ DNS servers hiện tại.
- Zero server management → minimize operational overhead, maximize availability.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Single EC2 instance: single point of failure, cần quản lý OS, DNS software, patches → operational overhead cao.

**❌ Đáp án C:**
- AWS SMS dùng để migrate servers (VM), vẫn cần quản lý EC2 instances. CloudWatch alarm chỉ thông báo, không giải quyết downtime.

**❌ Đáp án D:**
- EC2 ASG: vẫn cần quản lý OS và DNS software. Desired capacity = 1: single instance, có thể có downtime khi scaling. Operational overhead cao hơn Route 53.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"DNS → Route 53 (managed, 100% SLA). EC2 for DNS = operational overhead. Always prefer managed services."*
