# Question #600 - Topic 1

A company is planning to migrate a TCP-based application into the company's VPC. The application is publicly accessible on a nonstandard TCP port through a hardware appliance in the company's data center. This public endpoint can process up to 3 million requests per second with low latency. The company requires the same level of performance for the new public endpoint in AWS. What should a solutions architect recommend to meet this requirement?

## Options

**A.** Deploy a Network Load Balancer (NLB). Configure the NLB to be publicly accessible over the TCP port that the application requires.

**B.** Deploy an Application Load Balancer (ALB). Configure the ALB to be publicly accessible over the TCP port that the application requires.

**C.** Deploy an Amazon CloudFront distribution that listens on the TCP port that the application requires. Use an Application Load Balancer as the origin.

**D.** Deploy an Amazon API Gateway API that is configured with the TCP port that the application requires. Configure AWS Lambda functions with provisioned concurrency to process the requests.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** TCP-based application, public, nonstandard TCP port, 3 million requests/second, low latency. Migrate from on-prem hardware appliance to AWS.
- **Existing Resources:** On-prem hardware appliance.
- **Current Issue/Goal:** AWS solution đạt same performance (high throughput, low latency).

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `TCP-based` | Layer 4 (TCP/UDP). |
| `3 million requests per second` | Cần high throughput. NLB hỗ trợ hàng triệu requests/sec. |
| `low latency` | NLB: ultra low latency (Layer 4). |
| `nonstandard TCP port` | ALB chỉ support HTTP/HTTPS (standard ports). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Performance + compatibility
- **Constraints:** TCP, high throughput, low latency, nonstandard port

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- NLB hoạt động ở Layer 4 (TCP/UDP), hỗ trợ bất kỳ TCP port nào (bao gồm nonstandard ports).
- NLB có thể xử lý hàng triệu requests/second với ultra low latency.
- NLB public-facing: internet-facing NLB với Elastic IP.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- ALB là Layer 7 (HTTP/HTTPS), không hỗ trợ nonstandard TCP ports và không thể xử lý pure TCP traffic.

**❌ Đáp án C:**
- CloudFront chỉ hỗ trợ HTTP/HTTPS, không hỗ trợ nonstandard TCP ports. Không thể thay thế cho TCP application.

**❌ Đáp án D:**
- API Gateway chỉ hỗ trợ HTTP/HTTPS/WebSocket, không support raw TCP. Lambda không xử lý TCP connections hiệu quả như NLB.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"TCP + nonstandard port + high throughput → NLB (Layer 4, ultra low latency). ALB/CloudFront/API Gateway = HTTP/HTTPS only."*
