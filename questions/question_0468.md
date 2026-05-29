# Question #468 - Topic 1

A company is developing a microservices application that will provide a search catalog for customers. The company must use REST APIs to present the frontend of the application to users. The REST APIs must access the backend services that the company hosts in containers in private VPC subnets. Which solution will meet these requirements?

## Options

**A.** Design a WebSocket API by using Amazon API Gateway. Host the application in Amazon Elastic Container Service (Amazon ECS) in a private subnet. Create a private VPC link for API Gateway to access Amazon ECS.

**B.** Design a REST API by using Amazon API Gateway. Host the application in Amazon Elastic Container Service (Amazon ECS) in a private subnet. Create a private VPC link for API Gateway to access Amazon ECS.

**C.** Design a WebSocket API by using Amazon API Gateway. Host the application in Amazon Elastic Container Service (Amazon ECS) in a private subnet. Create a security group for API Gateway to access Amazon ECS.

**D.** Design a REST API by using Amazon API Gateway. Host the application in Amazon Elastic Container Service (Amazon ECS) in a private subnet. Create a security group for API Gateway to access Amazon ECS.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Microservices app search catalog, REST APIs frontend, backend containers trong private subnets.
- **Existing Resources:** Containers on ECS in private subnets.
- **Current Issue/Goal:** REST API từ frontend → backend services trong private VPC.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `REST APIs` | Cần dùng REST API, không phải WebSocket. |
| `private VPC subnets` | Backend services không public → API Gateway cần private VPC link. |
| `private VPC link` | Cho phép API Gateway access resources trong VPC mà không qua internet. |
| `security group` | Security group không thể attach vào API Gateway. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** REST API to private VPC
- **Constraints:** REST APIs, private subnets, containers

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- REST API: đề yêu cầu REST APIs → dùng API Gateway REST API.
- Private VPC link: cho phép API Gateway kết nối đến NLB (hoặc ALB) trong private subnet, traffic không qua internet.
- ECS trong private subnet an toàn, không public exposure.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- WebSocket API: không phải REST API, không phù hợp yêu cầu.

**❌ Đáp án C:**
- WebSocket API: không phải REST.
- Security group không thể gán trực tiếp cho API Gateway → API Gateway không nằm trong VPC.

**❌ Đáp án D:**
- Security group không thể gán cho API Gateway.
- Cần VPC link để API Gateway kết nối vào private subnet, security group không đủ.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"API Gateway → private VPC = Private VPC Link (không phải security group). REST thì dùng REST API, không phải WebSocket."*
