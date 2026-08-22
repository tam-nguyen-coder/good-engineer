# Question #610 - Topic 1

A company deploys Amazon EC2 instances that run in a VPC. The EC2 instances load source data into Amazon S3 buckets so that the data can be processed in the future. According to compliance laws, the data must not be transmitted over the public internet. Servers in the company's on- premises data center will consume the output from an application that runs on the EC2 instances. Which solution will meet these requirements?

## Options

**A.** Deploy an interface VPC endpoint for Amazon EC2. Create an AWS Site-to-Site VPN connection between the company and the VPC.

**B.** Deploy a gateway VPC endpoint for Amazon S3. Set up an AWS Direct Connect connection between the on-premises network and the VPC.

**C.** Set up an AWS Transit Gateway connection from the VPC to the S3 buckets. Create an AWS Site-to-Site VPN connection between the company and the VPC.

**D.** Set up proxy EC2 instances that have routes to NAT gateways. Configure the proxy EC2 instances to fetch S3 data and feed the application instances.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 trong VPC load data lên S3. Data không được truyền qua public internet. On-prem servers consume output từ EC2 application.
- **Existing Resources:** EC2 instances in VPC, on-premises data center.
- **Current Issue/Goal:** Private connectivity: EC2 → S3 (no internet) và On-prem → VPC (no internet).

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `must not be transmitted over the public internet` | Cần private connectivity. |
| `EC2 → S3` | Gateway VPC Endpoint for S3 (kết nối trực tiếp, không qua internet). |
| `on-premises → VPC` | AWS Direct Connect (private dedicated connection). |
| `compliance laws` | Yêu cầu nghiêm ngặt về đường truyền private. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements (compliance)
- **Constraints:** No public internet, EC2 to S3, on-prem to VPC

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Gateway VPC Endpoint for S3: cho phép EC2 instances trong VPC truy cập S3 qua AWS private network, không qua internet.
- AWS Direct Connect: kết nối private dedicated từ on-premises data center đến VPC, không qua internet.
- Cả hai đều đảm bảo compliance: không có dữ liệu nào đi qua public internet.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Interface VPC endpoint for EC2 → dùng để kết nối đến EC2 API, không phải S3.
- Site-to-Site VPN đi qua internet (dù encrypted), không đáp ứng "not over public internet" strictly.

**❌ Đáp án C:**
- Transit Gateway kết nối VPC với nhau hoặc với on-prem, không kết nối trực tiếp VPC đến S3.
- Site-to-Site VPN đi qua internet.

**❌ Đáp án D:**
- NAT gateway dùng để outbound internet access → vi phạm compliance.
- Proxy EC2 instances + NAT là giải pháp dùng internet.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"EC2 → S3 (no internet) = Gateway Endpoint. On-prem → AWS (no internet) = Direct Connect."*
