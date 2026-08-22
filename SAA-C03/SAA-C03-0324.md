# Question #324 - Topic 1

A company wants to implement a disaster recovery plan for its primary on-premises file storage volume. The file storage volume is mounted from an Internet Small Computer Systems Interface (iSCSI) device on a local storage server. The file storage volume holds hundreds of terabytes (TB) of data. The company wants to ensure that end users retain immediate access to all file types from the on-premises systems without experiencing latency. Which solution will meet these requirements with the LEAST amount of change to the company's existing infrastructure?

## Options

**A.** Provision an Amazon S3 File Gateway as a virtual machine (VM) that is hosted on premises. Set the local cache to 10 TB. Modify existing applications to access the files through the NFS protocol. To recover from a disaster, provision an Amazon EC2 instance and mount the S3 bucket that contains the files.

**B.** Provision an AWS Storage Gateway tape gateway. Use a data backup solution to back up all existing data to a virtual tape library. Configure the data backup solution to run nightly after the initial backup is complete. To recover from a disaster, provision an Amazon EC2 instance and restore the data to an Amazon Elastic Block Store (Amazon EBS) volume from the volumes in the virtual tape library.

**C.** Provision an AWS Storage Gateway Volume Gateway cached volume. Set the local cache to 10 TB. Mount the Volume Gateway cached volume to the existing file server by using iSCSI, and copy all files to the storage volume. Configure scheduled snapshots of the storage volume. To recover from a disaster, restore a snapshot to an Amazon Elastic Block Store (Amazon EBS) volume and attach the EBS volume to an Amazon EC2 instance.

**D.** Provision an AWS Storage Gateway Volume Gateway stored volume with the same amount of disk space as the existing file storage volume. Mount the Volume Gateway stored volume to the existing file server by using iSCSI, and copy all files to the storage volume. Configure scheduled snapshots of the storage volume. To recover from a disaster, restore a snapshot to an Amazon Elastic Block Store (Amazon EBS) volume and attach the EBS volume to an Amazon EC2 instance.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** On-premises iSCSI file storage (hundreds of TB). Cần DR plan, end users cần immediate local access không latency, least infrastructure change.
- **Existing Resources:** iSCSI device, local storage server.
- **Current Issue/Goal:** DR plan, không latency cho local users, least change.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `iSCSI` | Block storage protocol → Volume Gateway (iSCSI), không phải File Gateway (NFS/SMB). |
| `immediate access to all file types` | Cần local access không latency → stored volume (all data locally). |
| `without experiencing latency` | Stored volume: all data on-premises, không phải fetch từ AWS. |
| `least amount of change` | Stored volume dùng iSCSI → tương thích infrastructure hiện tại. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least amount of change to existing infrastructure
- **Constraints:** iSCSI, no latency, hundreds of TB, DR

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- Stored volume gateway: toàn bộ dữ liệu lưu on-premises (zero latency cho local users), async snapshot lên AWS cho DR.
- iSCSI protocol → compatible với existing infrastructure, không cần thay đổi.
- Snapshot schedule → backup lên S3, có thể restore thành EBS volume cho DR trên EC2.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- S3 File Gateway dùng NFS, không phải iSCSI → cần modify applications. 10 TB cache quá nhỏ cho hundreds of TB.

**❌ Đáp án B:**
- Tape Gateway dùng cho backup (VTL), không phải primary storage. Users không thể access files trực tiếp từ VTL.

**❌ Đáp án C:**
- Cached volume: primary data ở AWS, cache 10 TB on-premises → có thể gây latency cho data không cached.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"No latency + iSCSI → Stored Volume Gateway (all data local, async backup). Cached = latency cho data không cache."*
