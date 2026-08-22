# Question #591 - Topic 1

A company runs a container application by using Amazon Elastic Kubernetes Service (Amazon EKS). The application includes microservices that manage customers and place orders. The company needs to route incoming requests to the appropriate microservices. Which solution will meet this requirement MOST cost-effectively?

## Options

**A.** Use the AWS Load Balancer Controller to provision a Network Load Balancer.

**B.** Use the AWS Load Balancer Controller to provision an Application Load Balancer.

**C.** Use an AWS Lambda function to connect the requests to Amazon EKS.

**D.** Use Amazon API Gateway to connect the requests to Amazon EKS.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EKS container app với microservices (customers + orders), cần route requests đến đúng microservice.
- **Existing Resources:** EKS cluster.
- **Current Issue/Goal:** Request routing to microservices, cost-effective.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `route incoming requests to the appropriate microservices` | Cần path-based hoặc host-based routing (Layer 7). |
| `microservices` | ALB hỗ trợ path-based routing đến các services khác nhau. |
| `Application Load Balancer` | Layer 7: path-based, host-based routing. |
| `Network Load Balancer` | Layer 4: TCP/UDP, không path-based routing. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effectively
- **Constraints:** EKS, microservices routing

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- AWS Load Balancer Controller on EKS tự động provision ALB cho Kubernetes Ingress.
- ALB hỗ trợ path-based routing (e.g., /customers → customer service, /orders → order service).
- Cost-effective: ALB tính phí theo thời gian + LCU, phù hợp cho microservices routing.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- NLB là Layer 4, không path-based routing → không thể route requests based on path/host.

**❌ Đáp án C:**
- Lambda không phải là API gateway/load balancer cho EKS. Phức tạp và không phù hợp.

**❌ Đáp án D:**
- API Gateway có thể route requests, nhưng tốn thêm chi phí so với ALB + Load Balancer Controller (service tích hợp sẵn với EKS).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Microservices routing → ALB (path-based). NLB = Layer 4 only. API Gateway = extra cost."*
