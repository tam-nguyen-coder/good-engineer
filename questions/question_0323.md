# Question #323 - Topic 1

A company's facility has badge readers at every entrance throughout the building. When badges are scanned, the readers send a message over HTTPS to indicate who attempted to access that particular entrance. A solutions architect must design a system to process these messages from the sensors. The solution must be highly available, and the results must be made available for the company's security team to analyze. Which system architecture should the solutions architect recommend?

## Options

**A.** Launch an Amazon EC2 instance to serve as the HTTPS endpoint and to process the messages. Configure the EC2 instance to save the results to an Amazon S3 bucket.

**B.** Create an HTTPS endpoint in Amazon API Gateway. Configure the API Gateway endpoint to invoke an AWS Lambda function to process the messages and save the results to an Amazon DynamoDB table.

**C.** Use Amazon Route 53 to direct incoming sensor messages to an AWS Lambda function. Configure the Lambda function to process the messages and save the results to an Amazon DynamoDB table.

**D.** Create a gateway VPC endpoint for Amazon S3. Configure a Site-to-Site VPN connection from the facility network to the VPC so that sensor data can be written directly to an S3 bucket by way of the VPC endpoint.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Badge readers gửi HTTPS messages khi scan. Cần highly available system để process và lưu kết quả cho security team analyze.
- **Existing Resources:** Badge readers (HTTPS).
- **Current Issue/Goal:** Highly available processing + storage for analysis.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `HTTPS endpoint` | API Gateway cung cấp HTTPS endpoint managed, highly available. |
| `highly available` | Cần serverless: API Gateway + Lambda + DynamoDB đều HA. |
| `security team to analyze` | DynamoDB lưu results, có thể query/export để analyze. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Highly available architecture
- **Constraints:** HTTPS endpoint, process + store messages

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- API Gateway: managed HTTPS endpoint, highly available, scalable.
- Lambda: serverless compute, auto-scale, HA.
- DynamoDB: managed NoSQL database, HA, phù hợp lưu structured event data.
- Cả 3 services đều highly available và không cần quản lý infrastructure.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Single EC2 instance không highly available (nếu instance fails → mất khả năng nhận messages).

**❌ Đáp án C:**
- Route 53 là DNS, không thể direct incoming HTTPS messages tới Lambda. Route 53 không phải HTTP endpoint.

**❌ Đáp án D:**
- Gateway VPC endpoint + VPN: phức tạp, không phải HTTPS endpoint. Sensor không thể gửi HTTPS trực tiếp tới S3.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"HTTPS sensor + HA → API Gateway + Lambda + DynamoDB (serverless, HA). EC2 single instance = không HA."*
