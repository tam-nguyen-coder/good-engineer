# Question #562 - Topic 1

A solutions architect needs to ensure that API calls to Amazon DynamoDB from Amazon EC2 instances in a VPC do not travel across the internet. Which combination of steps should the solutions architect take to meet this requirement? (Choose two.)

## Options

**A.** Create a route table entry for the endpoint.

**B.** Create a gateway endpoint for DynamoDB.

**C.** Create an interface endpoint for Amazon EC2.

**D.** Create an elastic network interface for the endpoint in each of the subnets of the VPC.

**E.** Create a security group entry in the endpoint's security group to provide access.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 instances trong VPC cần gọi DynamoDB API mà không đi qua internet.
- **Existing Resources:** VPC, EC2 instances.
- **Current Issue/Goal:** Kết nối private từ VPC đến DynamoDB (không qua internet).

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `do not travel across the internet` | Cần VPC endpoint |
| `DynamoDB` | Hỗ trợ gateway endpoint |
| `gateway endpoint` | Dùng cho S3 và DynamoDB, thêm route table entry |
| `route table entry` | Cần thêm route cho gateway endpoint |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Multi-select (2 answers)
- **Constraints:** Private connection EC2 → DynamoDB

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A, B**

**Giải thích:**
- **B (Gateway endpoint for DynamoDB):** DynamoDB hỗ trợ gateway endpoint (cùng loại với S3). Gateway endpoint sử dụng AWS PrivateLink để route traffic đến DynamoDB qua AWS internal network.
- **A (Route table entry):** Gateway endpoint yêu cầu thêm một route trong route table của VPC, với đích là prefix list của DynamoDB và target là gateway endpoint ID.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án C (Interface endpoint for EC2):** Interface endpoint dùng cho EC2 là để kết nối đến EC2 service (EC2 API), không phải từ EC2 đến DynamoDB. DynamoDB dùng gateway endpoint, không phải interface endpoint.

**❌ Đáp án D (Elastic network interface):** Gateway endpoint không dùng ENI. Interface endpoint mới dùng ENI. Vì DynamoDB dùng gateway endpoint, không cần ENI.

**❌ Đáp án E (Security group):** Gateway endpoint cho DynamoDB không hỗ trợ security groups. Security groups chỉ dùng cho interface endpoints.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"DynamoDB + S3 = gateway endpoints (need route table entry, no SG, no ENI). Other AWS services = interface endpoints (need ENI, SG)."*
