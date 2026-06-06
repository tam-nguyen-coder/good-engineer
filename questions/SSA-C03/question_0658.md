# Question #658 - Topic 1

A company uses an on-premises network-attached storage (NAS) system to provide file shares to its high performance computing (HPC) workloads. The company wants to migrate its latency-sensitive HPC workloads and its storage to the AWS Cloud. The company must be able to provide NFS and SMB multi-protocol access from the file system. Which solution will meet these requirements with the LEAST latency? (Choose two.)

## Options

**A.** Deploy compute optimized EC2 instances into a cluster placement group.

**B.** Deploy compute optimized EC2 instances into a partition placement group.

**C.** Attach the EC2 instances to an Amazon FSx for Lustre file system.

**D.** Attach the EC2 instances to an Amazon FSx for OpenZFS file system.

**E.** Attach the EC2 instances to an Amazon FSx for NetApp ONTAP file system.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Migrate HPC workloads + NAS storage from on-prem to AWS. Need NFS + SMB multi-protocol, low latency.
- **Existing Resources:** On-prem NAS supporting NFS and SMB.
- **Current Issue/Goal:** Low latency, multi-protocol (NFS + SMB) file system.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `latency-sensitive HPC` | Cần cluster placement group (low latency network). |
| `NFS and SMB multi-protocol` | FSx for NetApp ONTAP hỗ trợ cả NFS và SMB. |
| `least latency` | Cluster placement group → low latency between instances. |
| `FSx for Lustre` | Hỗ trợ NFS? Không, Lustre không hỗ trợ SMB. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least latency, meet requirements (choose two)
- **Constraints:** NFS + SMB multi-protocol, HPC low latency

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A và E**

**Giải thích:**
- **A:** Cluster placement group → low latency network giữa các EC2 instances (cần cho HPC).
- **E:** FSx for NetApp ONTAP hỗ trợ cả NFS và SMB multi-protocol đồng thời, phù hợp thay thế on-prem NAS.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Partition placement group dùng cho lớn distributed workloads (Hadoop, HDFS), không tối ưu cho HPC low latency.

**❌ Đáp án C:**
- FSx for Lustre: hỗ trợ POSIX (Linux) nhưng không hỗ trợ SMB protocol.

**❌ Đáp án D:**
- FSx for OpenZFS: hỗ trợ NFS nhưng không hỗ trợ SMB.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"NFS + SMB multi-protocol → FSx for NetApp ONTAP. HPC low latency → Cluster Placement Group."*
