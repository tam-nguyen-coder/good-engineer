# Question #332 - Topic 1

A company needs to provide its employees with secure access to confidential and sensitive files. The company wants to ensure that the files can be accessed only by authorized users. The files must be downloaded securely to the employees' devices. The files are stored in an on-premises Windows file server. However, due to an increase in remote usage, the file server is running out of capacity. . Which solution will meet these requirements?

## Options

**A.** Migrate the file server to an Amazon EC2 instance in a public subnet. Configure the security group to limit inbound traffic to the employees' IP addresses.

**B.** Migrate the files to an Amazon FSx for Windows File Server file system. Integrate the Amazon FSx file system with the on-premises Active Directory. Configure AWS Client VPN.

**C.** Migrate the files to Amazon S3, and create a private VPC endpoint. Create a signed URL to allow download.

**D.** Migrate the files to Amazon S3, and create a public VPC endpoint. Allow employees to sign on with AWS IAM Identity Center (AWS Single Sign-On).

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** On-premises Windows file server sắp hết capacity, remote employees cần secure access to confidential files.
- **Existing Resources:** On-premises Windows file server, Active Directory (implied by Windows AD integration).
- **Current Issue/Goal:** Migrate files, secure access for remote employees, authorized users only.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Windows file server` | FSx for Windows File Server là managed Windows file storage. |
| `authorized users` | on-premises AD authentication. |
| `securely to the employees' devices` | AWS Client VPN cho secure remote access. |
| `on-premises Active Directory` | FSx for Windows tích hợp AD để xác thực users. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which solution meets requirements
- **Constraints:** Secure access, authorized users, migrate from Windows file server

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- FSx for Windows File Server: managed SMB file server, scalable, giải quyết capacity issue.
- Integrate với on-premises AD → dùng existing credentials để authorize users.
- AWS Client VPN: secure tunnel cho remote employees download files.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- EC2 in public subnet: security group filter by IP. IP của employees có thể thay đổi (remote/VPN). Không scalable.

**❌ Đáp án C:**
- S3 + signed URLs: thay đổi cách access files (không còn SMB/Windows file share). Employees không thể mount as network drive.

**❌ Đáp án D:**
- S3 public VPC endpoint không secure (public). IAM Identity Center không phải AD authentication.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Windows file server + AD + remote access → FSx for Windows + Client VPN. S3 = không SMB, khác access pattern."*
