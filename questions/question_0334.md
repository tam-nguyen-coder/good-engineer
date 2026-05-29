# Question #334 - Topic 1

A company wants to give a customer the ability to use on-premises Microsoft Active Directory to download files that are stored in Amazon S3. The customer's application uses an SFTP client to download the files. Which solution will meet these requirements with the LEAST operational overhead and no changes to the customer's application?

## Options

**A.** Set up AWS Transfer Family with SFTP for Amazon S3. Configure integrated Active Directory authentication.

**B.** Set up AWS Database Migration Service (AWS DMS) to synchronize the on-premises client with Amazon S3. Configure integrated Active Directory authentication.

**C.** Set up AWS DataSync to synchronize between the on-premises location and the S3 location by using AWS IAM Identity Center (AWS Single Sign-On).

**D.** Set up a Windows Amazon EC2 instance with SFTP to connect the on-premises client with Amazon S3. Integrate AWS Identity and Access Management (IAM).

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Customer dùng on-premises AD + SFTP client để download files từ S3. No app changes.
- **Existing Resources:** Files in S3, on-premises AD, SFTP client.
- **Current Issue/Goal:** Allow SFTP access to S3 files with AD auth, least overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `SFTP client` | AWS Transfer Family hỗ trợ SFTP protocol để transfer files ra/vào S3. |
| `on-premises Microsoft Active Directory` | Transfer Family có thể tích hợp AD để xác thực. |
| `no changes to the customer's application` | Giữ nguyên SFTP client. |
| `least operational overhead` | Transfer Family là managed service. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead, no app changes
- **Constraints:** SFTP client, AD authentication, S3 storage

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- AWS Transfer Family: managed SFTP service, hỗ trợ AD authentication, direct access to S3.
- Không cần thay đổi application phía customer (vẫn dùng SFTP client).
- Operational overhead thấp nhất (managed service).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- DMS là database migration service, không hỗ trợ SFTP hay file transfer từ S3.

**❌ Đáp án C:**
- DataSync là data transfer service giữa on-prem và AWS, không phải SFTP server. Customer không thể dùng SFTP client với DataSync.

**❌ Đáp án D:**
- EC2 Windows + tự cài SFTP server → operational overhead cao hơn Transfer Family (phải quản lý instance, patch, security).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"SFTP + S3 + AD auth → AWS Transfer Family (managed SFTP). EC2 self-managed = operational overhead cao hơn."*
