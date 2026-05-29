# Question #510 - Topic 1

A global marketing company has applications that run in the ap-southeast-2 Region and the eu-west-1 Region. Applications that run in a VPC in eu-west-1 need to communicate securely with databases that run in a VPC in ap-southeast-2. Which network design will meet these requirements?

## Options

**A.** Create a VPC peering connection between the eu-west-1 VPC and the ap-southeast-2 VPC. Create an inbound rule in the eu-west-1 application security group that allows traffic from the database server IP addresses in the ap-southeast-2 security group.

**B.** Configure a VPC peering connection between the ap-southeast-2 VPC and the eu-west-1 VPC. Update the subnet route tables. Create an inbound rule in the ap-southeast-2 database security group that references the security group ID of the application servers in eu-west-1.

**C.** Configure a VPC peering connection between the ap-southeast-2 VPC and the eu-west-1 VPC. Update the subnet route tables. Create an inbound rule in the ap-southeast-2 database security group that allows traffic from the eu-west-1 application server IP addresses.

**D.** Create a transit gateway with a peering attachment between the eu-west-1 VPC and the ap-southeast-2 VPC. After the transit gateways are properly peered and routing is configured, create an inbound rule in the database security group that references the security group ID of the application servers in eu-west-1.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Cross-region VPC connectivity (eu-west-1 → ap-southeast-2). App servers eu-west-1 cần giao tiếp secure với database ap-southeast-2.
- **Existing Resources:** VPC in eu-west-1 (app), VPC in ap-southeast-2 (database).
- **Current Issue/Goal:** Kết nối cross-region VPC, secure communication.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `VPC in eu-west-1` and `VPC in ap-southeast-2` | Cross-region VPC peering được hỗ trợ. |
| `security group ID` | Cross-region VPC peering không hỗ trợ reference SG ID từ region khác. |
| `communicate securely` | Cần private connection (VPC peering hoặc TGW). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Network design
- **Constraints:** Cross-region, secure, app-to-database

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Cross-region VPC peering là giải pháp đơn giản và hiệu quả để kết nối VPC ở 2 region khác nhau.
- Vì security group ID không thể reference cross-region, phải dùng IP addresses/CIDR để allow traffic.
- Đáp án C: VPC peering + route tables + inbound rule in database SG allowing app server IPs → đúng pattern.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Inbound rule sai hướng: application SG cần allow traffic FROM database (outbound từ app đến DB), không phải allow traffic FROM database IP (inbound).
- App servers cần gửi request đến DB, DB mới cần allow inbound từ app IPs.

**❌ Đáp án B:**
- Cross-region VPC peering không hỗ trợ reference security group ID từ region khác. SG ID chỉ có thể dùng trong cùng region.
- Đây là limitation quan trọng cần nhớ.

**❌ Đáp án D:**
- Transit Gateway peering attachment hỗ trợ cross-region, nhưng SG reference cross-region vẫn không được (giống B).
- Thêm TGW vào làm phức tạp hơn mà không giải quyết được vấn đề.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Cross-region VPC peering: dùng IP CIDR trong SG rules (không reference được SG ID từ region khác)."*
