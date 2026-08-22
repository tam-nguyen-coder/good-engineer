# Question #357 - Topic 1

A gaming company is moving its public scoreboard from a data center to the AWS Cloud. The company uses Amazon EC2 Windows Server instances behind an Application Load Balancer to host its dynamic application. The company needs a highly available storage solution for the application. The application consists of static files and dynamic server-side code. Which combination of steps should a solutions architect take to meet these requirements? (Choose two.)

## Options

**A.** Store the static files on Amazon S3. Use Amazon CloudFront to cache objects at the edge.

**B.** Store the static files on Amazon S3. Use Amazon ElastiCache to cache objects at the edge.

**C.** Store the server-side code on Amazon Elastic File System (Amazon EFS). Mount the EFS volume on each EC2 instance to share the files.

**D.** Store the server-side code on Amazon FSx for Windows File Server. Mount the FSx for Windows File Server volume on each EC2 instance to share the files.

**E.** Store the server-side code on a General Purpose SSD (gp2) Amazon Elastic Block Store (Amazon EBS) volume. Mount the EBS volume on each EC2 instance to share the files.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Windows EC2 + ALB, public scoreboard. Need HA storage for static files and dynamic server-side code.
- **Existing Resources:** Windows EC2 instances, ALB.
- **Current Issue/Goal:** Highly available storage cho static files + shared server-side code.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Windows Server instances` | Cần SMB share → FSx for Windows File Server. EFS = NFS (Linux). |
| `static files` | S3 + CloudFront: best practice cho static content HA global. |
| `dynamic server-side code` | Cần shared file system giữa Windows EC2 instances. |
| `Amazon FSx for Windows File Server` | Managed Windows SMB file share, HA. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Choose two
- **Constraints:** Windows, static files + server-side code sharing

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A (static files) và D (server-side code)**

**Giải thích:**
- **A:** Static files → S3 (durable, HA) + CloudFront (global caching, low latency).
- **D:** Dynamic server-side code → FSx for Windows File Server (SMB file share cho Windows EC2 instances, HA).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- ElastiCache là in-memory cache, không phải storage cho static files.

**❌ Đáp án C:**
- EFS là NFS (Linux), không compatible với Windows Server instances.

**❌ Đáp án E:**
- EBS volume chỉ attach được 1 EC2 instance → không shared storage.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Windows + static files → S3 + CloudFront. Windows + shared code → FSx for Windows (SMB). EBS = 1 instance. EFS = Linux."*
