# Question #421 - Topic 1

A company runs a highly available SFTP service. The SFTP service uses two Amazon EC2 Linux instances that run with elastic IP addresses to accept traffic from trusted IP sources on the internet. The SFTP service is backed by shared storage that is attached to the instances. User accounts are created and managed as Linux users in the SFTP servers. The company wants a serverless option that provides high IOPS performance and highly configurable security. The company also wants to maintain control over user permissions. Which solution will meet these requirements?

## Options

**A.** Create an encrypted Amazon Elastic Block Store (Amazon EBS) volume. Create an AWS Transfer Family SFTP service with a public endpoint that allows only trusted IP addresses. Attach the EBS volume to the SFTP service endpoint. Grant users access to the SFTP service.

**B.** Create an encrypted Amazon Elastic File System (Amazon EFS) volume. Create an AWS Transfer Family SFTP service with elastic IP addresses and a VPC endpoint that has internet-facing access. Attach a security group to the endpoint that allows only trusted IP addresses. Attach the EFS volume to the SFTP service endpoint. Grant users access to the SFTP service.

**C.** Create an Amazon S3 bucket with default encryption enabled. Create an AWS Transfer Family SFTP service with a public endpoint that allows only trusted IP addresses. Attach the S3 bucket to the SFTP service endpoint. Grant users access to the SFTP service.

**D.** Create an Amazon S3 bucket with default encryption enabled. Create an AWS Transfer Family SFTP service with a VPC endpoint that has internal access in a private subnet. Attach a security group that allows only trusted IP addresses. Attach the S3 bucket to the SFTP service endpoint. Grant users access to the SFTP service.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** SFTP service (EC2 Linux + elastic IP + shared storage). Want serverless: Transfer Family + S3. Need high IOPS, configurable security, user control.
- **Existing Resources:** EC2 instances, shared storage, elastic IPs.
- **Current Issue/Goal:** Migrate to serverless SFTP with security + performance.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `serverless` | AWS Transfer Family for SFTP (managed). |
| `accept traffic from internet` | Public endpoint, restrict by source IP. |
| `Trusted IP sources` | Security group hoặc IP whitelist. |
| `S3` | Backend storage cho Transfer Family. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Serverless / Storage
- **Constraints:** Serverless, high IOPS, configurable security, user control

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- AWS Transfer Family SFTP: serverless managed SFTP service.
- S3 bucket làm backend: scalable, durable, high throughput.
- Public endpoint + restrict trusted IPs: internet access + security.
- User management: Transfer Family supports SSH keys + scoped down policies.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- EBS volume không thể attach trực tiếp vào Transfer Family endpoint (EBS chỉ attach được vào EC2).

**❌ Đáp án B:**
- EFS: phù hợp cho shared storage nhưng không có "elastic IP addresses" cho VPC endpoint.
- EFS là throughput-based, không phải "high IOPS".

**❌ Đáp án D:**
- VPC endpoint with internal access trong private subnet → không thể truy cập từ internet. Cần NLB/IGW để internet traffic vào được.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Serverless SFTP = Transfer Family + S3. Public endpoint + IP whitelist."*