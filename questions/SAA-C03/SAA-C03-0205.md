# Question #205 - Topic 1

A company hosts a marketing website in an on-premises data center. The website consists of static documents and runs on a single server. An administrator updates the website content infrequently and uses an SFTP client to upload new documents. The company decides to host its website on AWS and to use Amazon CloudFront. The company's solutions architect creates a CloudFront distribution. The solutions architect must design the most cost-effective and resilient architecture for website hosting to serve as the CloudFront origin. Which solution will meet these requirements?

## Options

**A.** Create a virtual server by using Amazon Lightsail. Configure the web server in the Lightsail instance. Upload website content by using an SFTP client.

**B.** Create an AWS Auto Scaling group for Amazon EC2 instances. Use an Application Load Balancer. Upload website content by using an SFTP client.

**C.** Create a private Amazon S3 bucket. Use an S3 bucket policy to allow access from a CloudFront origin access identity (OAI). Upload website content by using the AWS CLI.

**D.** Create a public Amazon S3 bucket. Configure AWS Transfer for SFTP. Configure the S3 bucket for website hosting. Upload website content by using the SFTP client.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Static website on single server, SFTP upload. Move to AWS + CloudFront. Cost-effective + resilient origin.
- **Existing Resources:** Static content, SFTP workflow.
- **Current Issue/Goal:** Best CloudFront origin for static site.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `static documents` | **S3** — perfect for static hosting |
| `most cost-effective and resilient` | **S3 private bucket + OAI** |
| `CloudFront` | S3 origin with OAI |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Static website / CDN
- **Constraints:** Cost-effective, resilient, CloudFront origin

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **Private S3 bucket + OAI** — best practice cho CloudFront origin.
- S3 is cost-effective (pay per GB) và resilient (11 9's durable).
- AWS CLI để upload → admin chuyển từ SFTP sang CLI.
- OAI đảm bảo chỉ CloudFront mới access được S3.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Lightsail — single server, không resilient, cost cao hơn S3.

**❌ Đáp án B:**
- ASG + ALB — overkill cho static site, đắt.

**❌ Đáp án D:**
- Public S3 bucket + Transfer for SFTP — public bucket kém secure, Transfer for SFTP tốn thêm chi phí.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Private S3 + OAI = secure, cost-effective, resilient. Lightsail/EC2 = more cost, less resilient"*
