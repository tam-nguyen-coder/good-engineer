# Question #260 - Topic 1

A company's compliance team needs to move its file shares to AWS. The shares run on a Windows Server SMB file share. A self-managed on-premises Active Directory controls access to the files and folders. The company wants to use Amazon FSx for Windows File Server as part of the solution. The company must ensure that the on-premises Active Directory groups restrict access to the FSx for Windows File Server SMB compliance shares, folders, and files after the move to AWS. The company has created an FSx for Windows File Server file system. Which solution will meet these requirements?

## Options

**A.** Create an Active Directory Connector to connect to the Active Directory. Map the Active Directory groups to IAM groups to restrict access.

**B.** Assign a tag with a Restrict tag key and a Compliance tag value. Map the Active Directory groups to IAM groups to restrict access.

**C.** Create an IAM service-linked role that is linked directly to FSx for Windows File Server to restrict access.

**D.** Join the file system to the Active Directory to restrict access.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Move Windows SMB file shares to FSx for Windows. On-prem AD controls access. Need AD groups to restrict access after migration.
- **Existing Resources:** FSx for Windows File Server file system.
- **Current Issue/Goal:** Integrate FSx with on-prem AD.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `on-premises Active Directory groups` | Cần **join FSx to AD** |
| `restrict access` | AD groups sẽ control SMB permissions |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Storage / Active Directory
- **Constraints:** AD integration, SMB access control

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **Join FSx to Active Directory** — FSx có thể join on-prem AD qua AD Connector hoặc AWS Managed Microsoft AD.
- AD groups → control access đến SMB shares, folders, files (NTFS permissions).
- Users authenticate với AD credentials.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- AD Connector + map to IAM groups — AD groups không map trực tiếp đến IAM groups.

**❌ Đáp án B:**
- Tags — không liên quan access control.

**❌ Đáp án C:**
- IAM service-linked role — cho service permissions, không cho file-level access.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"FSx join AD = AD groups control SMB access. IAM groups = different from AD groups"*
