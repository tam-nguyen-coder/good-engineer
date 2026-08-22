# Question #261 - Topic 1

A company recently announced the deployment of its retail website to a global audience. The website runs on multiple Amazon EC2 instances behind an Elastic Load Balancer. The instances run in an Auto Scaling group across multiple Availability Zones. The company wants to provide its customers with different versions of content based on the devices that the customers use to access the website. Which combination of actions should a solutions architect take to meet these requirements? (Choose two.)

## Options

**A.** Configure Amazon CloudFront to cache multiple versions of the content.

**B.** Configure a host header in a Network Load Balancer to forward traffic to different instances.

**C.** Configure a Lambda@Edge function to send specific objects to users based on the User-Agent header.

**D.** Configure AWS Global Accelerator. Forward requests to a Network Load Balancer (NLB). Configure the NLB to set up host-based routing to different EC2 instances.

**E.** Configure AWS Global Accelerator. Forward requests to a Network Load Balancer (NLB). Configure the NLB to set up path-based routing to different EC2 instances.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Global retail website, serve different content version based on device type.
- **Existing Resources:** EC2 + ELB + ASG multi-AZ.
- **Current Issue/Goal:** Device-based content variation at edge.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `different versions of content based on the devices` | **CloudFront** + **Lambda@Edge** (User-Agent) |
| `global audience` | CloudFront edge |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** CDN / Edge computing
- **Constraints:** Chọn 2, device-based routing

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A và C**

**Giải thích:**
- **A: CloudFront** — cache multiple content versions, global edge delivery.
- **C: Lambda@Edge** — inspect **User-Agent** header, serve appropriate content version.
- NLB không hỗ trợ host-based hay path-based routing (ALB mới hỗ trợ).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- NLB host header — NLB không hỗ trợ host-based routing (ALB mới có).

**❌ Đáp án D:**
- NLB host-based routing — sai, NLB layer 4.

**❌ Đáp án E:**
- NLB path-based routing — sai, NLB không hỗ trợ.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"CloudFront + Lambda@Edge = device-based content at edge. NLB = layer 4 (no host/path routing)"*
