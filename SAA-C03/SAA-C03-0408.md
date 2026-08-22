# Question #408 - Topic 1

A company runs an application that receives data from thousands of geographically dispersed remote devices that use UDP. The application processes the data immediately and sends a message back to the device if necessary. No data is stored. The company needs a solution that minimizes latency for the data transmission from the devices. The solution also must provide rapid failover to another AWS Region. Which solution will meet these requirements?

## Options

**A.** Configure an Amazon Route 53 failover routing policy. Create a Network Load Balancer (NLB) in each of the two Regions. Configure the NLB to invoke an AWS Lambda function to process the data.

**B.** Use AWS Global Accelerator. Create a Network Load Balancer (NLB) in each of the two Regions as an endpoint. Create an Amazon Elastic Container Service (Amazon ECS) cluster with the Fargate launch type. Create an ECS service on the cluster. Set the ECS service as the target for the NLB. Process the data in Amazon ECS.

**C.** Use AWS Global Accelerator. Create an Application Load Balancer (ALB) in each of the two Regions as an endpoint. Create an Amazon Elastic Container Service (Amazon ECS) cluster with the Fargate launch type. Create an ECS service on the cluster. Set the ECS service as the target for the ALB. Process the data in Amazon ECS.

**D.** Configure an Amazon Route 53 failover routing policy. Create an Application Load Balancer (ALB) in each of the two Regions. Create an Amazon Elastic Container Service (Amazon ECS) cluster with the Fargate launch type. Create an ECS service on the cluster. Set the ECS service as the target for the ALB. Process the data in Amazon ECS.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Thousands of remote devices send UDP data. Process immediately, respond if needed. Minimize latency + rapid cross-region failover.
- **Existing Resources:** Remote devices (UDP), AWS infrastructure.
- **Current Issue/Goal:** Low-latency ingestion for UDP, fast regional failover.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `UDP` | ALB không hỗ trợ UDP. NLB hỗ trợ UDP + TCP. |
| `minimizes latency` | Global Accelerator: anycast IP, traffic đi AWS edge → optimal path. |
| `rapid failover` | Global Accelerator: failover nhanh hơn DNS-based (Route 53). |
| `no data is stored` | In-memory processing, không cần database. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Performance / Networking
- **Constraints:** UDP, low latency, rapid cross-region failover

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- AWS Global Accelerator: anycast IP → giảm latency + rapid failover (< 1 phút, nhanh hơn DNS TTL).
- NLB: hỗ trợ UDP (ALB không support UDP).
- ECS Fargate: xử lý data (serverless, không quản lý infrastructure).
- NLB → ECS service: forward UDP traffic tới container.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- NLB không thể invoke Lambda (NLB targets: EC2, IP, ALB, không phải Lambda).
- Route 53 failover: chậm hơn Global Accelerator (DNS caching).

**❌ Đáp án C:**
- ALB không hỗ trợ UDP (chỉ HTTP/HTTPS/gRPC).

**❌ Đáp án D:**
- ALB không hỗ trợ UDP + Route 53 failover chậm hơn Global Accelerator.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"UDP + low latency + rapid failover = Global Accelerator + NLB. ALB không support UDP."*

