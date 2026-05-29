# Question #188 - Topic 1

A company uses Amazon S3 as its data lake. The company has a new partner that must use SFTP to upload data files. A solutions architect needs to implement a highly available SFTP solution that minimizes operational overhead. Which solution will meet these requirements?

## Options

**A.** Use AWS Transfer Family to configure an SFTP-enabled server with a publicly accessible endpoint. Choose the S3 data lake as the destination.

**B.** Use Amazon S3 File Gateway as an SFTP server. Expose the S3 File Gateway endpoint URL to the new partner. Share the S3 File Gateway endpoint with the new partner.

**C.** Launch an Amazon EC2 instance in a private subnet in a VPC. Instruct the new partner to upload files to the EC2 instance by using a VPN. Run a cron job script on the EC2 instance to upload files to the S3 data lake.

**D.** Launch Amazon EC2 instances in a private subnet in a VPC. Place a Network Load Balancer (NLB) in front of the EC2 instances. Create an SFTP listener port for the NLB. Share the NLB hostname with the new partner. Run a cron job script on the EC2 instances to upload files to the S3 data lake.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** S3 data lake, partner needs SFTP to upload. HA, min operational overhead.
- **Existing Resources:** S3 data lake.
- **Current Issue/Goal:** Managed SFTP → S3.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `SFTP` | **AWS Transfer Family** (managed SFTP) |
| `minimizes operational overhead` | Managed service |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Data transfer
- **Constraints:** SFTP, HA, min overhead

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **AWS Transfer Family** — managed SFTP server, tích hợp trực tiếp với S3.
- HA built-in (multi-AZ), không cần quản lý servers.
- Public endpoint partner có thể access mà không cần VPN.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- S3 File Gateway — NFS/SMB, không phải SFTP server.

**❌ Đáp án C:**
- EC2 + VPN + cron — operational overhead, không HA (single instance).

**❌ Đáp án D:**
- EC2 + NLB + cron — operational overhead, phải quản lý EC2 instances.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Transfer Family = managed SFTP to S3. File Gateway = NFS/SMB. EC2 = overhead"*
