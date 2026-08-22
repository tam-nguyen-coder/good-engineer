# Question #497 - Topic 1

A company has a service that reads and writes large amounts of data from an Amazon S3 bucket in the same AWS Region. The service is deployed on Amazon EC2 instances within the private subnet of a VPC. The service communicates with Amazon S3 over a NAT gateway in the public subnet. However, the company wants a solution that will reduce the data output costs. Which solution will meet these requirements MOST cost-effectively?

## Options

**A.** Provision a dedicated EC2 NAT instance in the public subnet. Configure the route table for the private subnet to use the elastic network interface of this instance as the destination for all S3 traffic.

**B.** Provision a dedicated EC2 NAT instance in the private subnet. Configure the route table for the public subnet to use the elastic network interface of this instance as the destination for all S3 traffic.

**C.** Provision a VPC gateway endpoint. Configure the route table for the private subnet to use the gateway endpoint as the route for all S3 traffic.

**D.** Provision a second NAT gateway. Configure the route table for the private subnet to use this NAT gateway as the destination for all S3 traffic.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 instances trong private subnet đọc/ghi data lớn từ S3 (cùng region). Hiện tại dùng NAT gateway để access S3 → tốn data output costs. Cần giảm chi phí.
- **Existing Resources:** VPC, private subnet, EC2 instances, NAT gateway, S3 bucket.
- **Current Issue/Goal:** Giảm data output costs cho S3 traffic từ private subnet.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `reduce the data output costs` | NAT gateway: charge per GB data processed. VPC Gateway Endpoint: free. |
| `same AWS Region` | Gateway endpoint chỉ hoạt động trong cùng region. |
| `large amounts of data` | Chi phí NAT gateway sẽ rất cao với data lớn. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective (reduce costs)
- **Constraints:** Private subnet EC2 → S3, cùng region.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **VPC Gateway Endpoint** cho S3: cho phép EC2 trong private subnet access S3 trực tiếp qua AWS network, không cần NAT gateway.
- **Gateway endpoint là free** - không charge data processing fees.
- Chỉ cần thêm route trong route table của private subnet trỏ tới gateway endpoint.
- Giảm đáng kể data output costs so với NAT gateway (tính phí per GB).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- **EC2 NAT instance:** Vẫn tốn chi phí instance + data processing. Không rẻ hơn NAT gateway đáng kể. Cần quản lý instance.

**❌ Đáp án B:**
- **NAT instance trong private subnet:** Sai kiến trúc. NAT instance phải ở public subnet để có internet access.

**❌ Đáp án D:**
- **Second NAT gateway:** Tăng chi phí (thêm NAT gateway), không giải quyết vấn đề.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"S3 + VPC + cost saving → Gateway Endpoint (free). NAT gateway = per GB charge."*
