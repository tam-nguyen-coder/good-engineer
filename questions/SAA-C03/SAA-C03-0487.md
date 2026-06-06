# Question #487 - Topic 1

A company seeks a storage solution for its application. The solution must be highly available and scalable. The solution also must function as a file system be mountable by multiple Linux instances in AWS and on premises through native protocols, and have no minimum size requirements. The company has set up a Site-to-Site VPN for access from its on-premises network to its VPC. Which storage solution meets these requirements?

## Options

**A.** Amazon FSx Multi-AZ deployments

**B.** Amazon Elastic Block Store (Amazon EBS) Multi-Attach volumes

**C.** Amazon Elastic File System (Amazon EFS) with multiple mount targets

**D.** Amazon Elastic File System (Amazon EFS) with a single mount target and multiple access points

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Cần storage solution: highly available, scalable, file system, mountable bởi nhiều Linux instances (AWS + on-premises), native protocols (NFS), không minimum size. Có Site-to-Site VPN.
- **Existing Resources:** Site-to-Site VPN, VPC.
- **Current Issue/Goal:** Chọn storage đáp ứng HA, scalability, NFS, multi-Linux, on-prem access.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `highly available and scalable` | EFS: regional, tự động scale, HA built-in. |
| `file system` | EFS là NFS file system. EBS là block storage. |
| `mountable by multiple Linux instances` | EFS: nhiều instances mount đồng thời. EBS Multi-Attach: chỉ tối đa 16 instances, single AZ. |
| `native protocols` | EFS dùng NFS (native cho Linux). |
| `no minimum size requirements` | EFS: pay-as-you-go, không minimum. |
| `Site-to-Site VPN` | Kết nối on-prem → VPC để mount EFS. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Storage solution selection
- **Constraints:** HA, scalable, NFS, multi-Linux, on-prem access, no min size.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **EFS** là managed NFS file system, support Linux instances.
- **Multiple mount targets** (một target mỗi AZ) → highly available (nếu một AZ fail, instances ở AZ khác vẫn truy cập được).
- **Scalable:** EFS tự động scale dung lượng.
- **On-prem access:** Qua Site-to-Site VPN, on-prem instances có thể mount EFS bằng NFS.
- **No minimum size:** Pay per GB used.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- **FSx Multi-AZ:** FSx for Windows File Server dùng SMB protocol, không phải native protocol cho Linux (NFS). FSx for Lustor là high-performance compute, không phải general-purpose file system.

**❌ Đáp án B:**
- **EBS Multi-Attach:** Chỉ available cho io1/io2 volumes, tối đa 16 instances, chỉ trong cùng một AZ → không highly available. Không thể mount từ on-premises qua VPN. Block storage, không phải file system.

**❌ Đáp án D:**
- **EFS single mount target:** Chỉ có 1 mount target trong 1 AZ → single point of failure. Không đáp ứng yêu cầu highly available.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"EFS = NFS cho Linux, HA, scalable, on-prem qua VPN. EBS Multi-Attach = single AZ, block storage."*
