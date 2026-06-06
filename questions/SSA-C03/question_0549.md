# Question #549 - Topic 1

A company has created a multi-tier application for its ecommerce website. The website uses an Application Load Balancer that resides in the public subnets, a web tier in the public subnets, and a MySQL cluster hosted on Amazon EC2 instances in the private subnets. The MySQL database needs to retrieve product catalog and pricing information that is hosted on the internet by a third-party provider. A solutions architect must devise a strategy that maximizes security without increasing operational overhead. What should the solutions architect do to meet these requirements?

## Options

**A.** Deploy a NAT instance in the VPC. Route all the internet-based traffic through the NAT instance.

**B.** Deploy a NAT gateway in the public subnets. Modify the private subnet route table to direct all internet-bound traffic to the NAT gateway.

**C.** Configure an internet gateway and attach it to the VPModify the private subnet route table to direct internet-bound traffic to the internet gateway.

**D.** Configure a virtual private gateway and attach it to the VPC. Modify the private subnet route table to direct internet-bound traffic to the virtual private gateway.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Ứng dụng multi-tier ecommerce: ALB (public subnet), web tier (public subnet), MySQL cluster EC2 (private subnet). MySQL cần lấy product catalog và pricing từ internet (third-party).
- **Existing Resources:** VPC, public subnets (ALB + web tier), private subnets (MySQL EC2).
- **Current Issue/Goal:** Cho MySQL (private subnet) truy cập internet một cách secure, không tăng operational overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `private subnets` | Không có internet access trực tiếp |
| `retrieve product catalog and pricing` | Kết nối ra internet (outbound) |
| `third-party provider` | Ở ngoài AWS, cần internet access |
| `maximizes security` | Secure, không expose private resources |
| `without increasing operational overhead` | Managed service > tự quản lý |
| `NAT gateway` | Managed, cho phép outbound từ private subnet |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most appropriate solution (maximize security, minimize overhead)
- **Constraints:** Private subnet cần outbound internet, security cao, không tăng overhead

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- NAT Gateway là dịch vụ managed, đặt trong public subnet, cho phép các instances trong private subnet kết nối ra internet (outbound) nhưng không cho inbound từ internet.
- Chỉ cần cập nhật route table của private subnet trỏ 0.0.0.0/0 đến NAT Gateway.
- Managed service → không cần quản lý patches, HA (tự động failover trong AZ). AWS chịu trách nhiệm vận hành.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A (NAT instance):** NAT instance là tự quản lý (unmanaged). Phải tự patch OS, cấu hình HA, và xử lý failover. Operational overhead cao hơn NAT Gateway. Không phù hợp với yêu cầu "without increasing operational overhead".

**❌ Đáp án C (IGW vào private subnet):** Internet Gateway (IGW) chỉ có thể gắn vào route table của public subnet. Private subnet không thể trực tiếp route đến IGW. Nếu làm vậy, private subnet sẽ trở thành public subnet – vi phạm security yêu cầu.

**❌ Đáp án D (Virtual Private Gateway):** Virtual Private Gateway (VGW) dùng cho VPN/Direct Connect kết nối on-premises với VPC, không phải để truy cập internet. Không thể dùng VGW để route traffic ra internet.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Private subnet → internet outbound = NAT Gateway (managed). NAT Instance = unmanaged, more overhead. IGW = public subnets only. VGW = VPN/Direct Connect."*
