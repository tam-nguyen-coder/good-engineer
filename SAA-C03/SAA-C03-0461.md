# Question #461 - Topic 1

A company is developing a mobile gaming app in a single AWS Region. The app runs on multiple Amazon EC2 instances in an Auto Scaling group. The company stores the app data in Amazon DynamoDB. The app communicates by using TCP traffic and UDP traffic between the users and the servers. The application will be used globally. The company wants to ensure the lowest possible latency for all users. Which solution will meet these requirements?

## Options

**A.** Use AWS Global Accelerator to create an accelerator. Create an Application Load Balancer (ALB) behind an accelerator endpoint that uses Global Accelerator integration and listening on the TCP and UDP ports. Update the Auto Scaling group to register instances on the ALB.

**B.** Use AWS Global Accelerator to create an accelerator. Create a Network Load Balancer (NLB) behind an accelerator endpoint that uses Global Accelerator integration and listening on the TCP and UDP ports. Update the Auto Scaling group to register instances on the NLB.

**C.** Create an Amazon CloudFront content delivery network (CDN) endpoint. Create a Network Load Balancer (NLB) behind the endpoint and listening on the TCP and UDP ports. Update the Auto Scaling group to register instances on the NLB. Update CloudFront to use the NLB as the origin.

**D.** Create an Amazon CloudFront content delivery network (CDN) endpoint. Create an Application Load Balancer (ALB) behind the endpoint and listening on the TCP and UDP ports. Update the Auto Scaling group to register instances on the ALB. Update CloudFront to use the ALB as the origin.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Mobile gaming app global users, EC2 Auto Scaling, DynamoDB. App dùng TCP + UDP.
- **Existing Resources:** EC2 instances trong Auto Scaling group, DynamoDB.
- **Current Issue/Goal:** Lowest latency cho global users, hỗ trợ cả TCP và UDP.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `TCP traffic and UDP traffic` | ALB chỉ hỗ trợ HTTP/HTTPS (Layer 7), không hỗ trợ UDP. NLB hỗ trợ TCP + UDP (Layer 4). |
| `lowest possible latency` | Global Accelerator: anycast IP, routing tối ưu qua AWS global network. |
| `global users` | Global Accelerator hoặc CloudFront. CloudFront không hỗ trợ UDP. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Lowest latency
- **Constraints:** Hỗ trợ cả TCP và UDP, global users

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Global Accelerator sử dụng anycast IP để đưa traffic vào AWS global network gần user nhất → giảm latency.
- NLB hoạt động ở Layer 4, hỗ trợ cả TCP và UDP.
- Global Accelerator tích hợp trực tiếp với NLB làm endpoint.
- Auto Scaling group đăng ký instances vào NLB.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- ALB chỉ hỗ trợ HTTP/HTTPS (Layer 7), không hỗ trợ UDP → không đáp ứng yêu cầu.

**❌ Đáp án C:**
- CloudFront không hỗ trợ UDP traffic, chỉ HTTP/HTTPS.

**❌ Đáp án D:**
- CloudFront không hỗ trợ UDP. ALB cũng không hỗ trợ UDP.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"UDP + TCP + global latency → Global Accelerator + NLB. ALB là Layer 7 (HTTP/HTTPS only)."*
