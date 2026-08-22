# Question #97 - Topic 1

A company has a large Microsoft SharePoint deployment running on-premises that requires Microsoft Windows shared file storage. The company wants to migrate this workload to the AWS Cloud and is considering various storage options. The storage solution must be highly available and integrated with Active Directory for access control. Which solution will satisfy these requirements?

## Options

**A.** Configure Amazon EFS storage and set the Active Directory domain for authentication.

**B.** Create an SMB file share on an AWS Storage Gateway file gateway in two Availability Zones.

**C.** Create an Amazon S3 bucket and configure Microsoft Windows Server to mount it as a volume.

**D.** Create an Amazon FSx for Windows File Server file system on AWS and set the Active Directory domain for authentication.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** SharePoint trên Windows, cần shared file storage, HA, AD integration.
- **Existing Resources:** On-prem SharePoint deployment.
- **Current Issue/Goal:** Migrate to AWS, HA + AD integrated storage.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Microsoft Windows shared file storage` | SMB protocol |
| `highly available` | Multi-AZ |
| `integrated with Active Directory` | Native AD integration |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Storage + Migration
- **Constraints:** Windows, HA, AD

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **Amazon FSx for Windows File Server** — managed Windows file server, hỗ trợ SMB.
- **Highly available** — Multi-AZ configuration.
- **Active Directory integration** — native support, tự động join domain.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- **EFS** là NFS (Linux/Unix), không hỗ trợ Windows SMB.
- EFS không native AD integration.

**❌ Đáp án B:**
- Storage Gateway File Gateway — có thể dùng SMB nhưng không native HA như FSx Multi-AZ.

**❌ Đáp án C:**
- S3 + mount as volume — không phải giải pháp chuẩn, không HA, không AD integration.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"FSx for Windows = SMB + AD + Multi-AZ. EFS = NFS (Linux). SharePoint = Windows → FSx"*
