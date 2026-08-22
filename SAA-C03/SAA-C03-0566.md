# Question #566 - Topic 1

A company runs multiple Amazon EC2 Linux instances in a VPC across two Availability Zones. The instances host applications that use a hierarchical directory structure. The applications need to read and write rapidly and concurrently to shared storage. What should a solutions architect do to meet these requirements?

## Options

**A.** Create an Amazon S3 bucket. Allow access from all the EC2 instances in the VPC.

**B.** Create an Amazon Elastic File System (Amazon EFS) file system. Mount the EFS file system from each EC2 instance.

**C.** Create a file system on a Provisioned IOPS SSD (io2) Amazon Elastic Block Store (Amazon EBS) volume. Attach the EBS volume to all the EC2 instances.

**D.** Create file systems on Amazon Elastic Block Store (Amazon EBS) volumes that are attached to each EC2 instance. Synchronize the EBS volumes across the different EC2 instances.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Nhiều EC2 Linux instances (multi-AZ) cần shared storage với hierarchical directory structure. Yêu cầu read/write nhanh và concurrent.
- **Existing Resources:** EC2 Linux instances in VPC, multi-AZ.
- **Current Issue/Goal:** Shared, concurrent, fast, hierarchical filesystem.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `EC2 Linux instances` | Linux → EFS hỗ trợ (NFS) |
| `hierarchical directory structure` | Cần filesystem (không phải object storage) |
| `read and write rapidly and concurrently` | Low latency, shared access |
| `shared storage` | Nhiều instances cùng truy cập |
| `Amazon EFS` | Managed NFS filesystem, shared, scalable |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most appropriate solution
- **Constraints:** Linux, multi-AZ, shared, concurrent read/write, hierarchical

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Amazon EFS là managed NFS filesystem cho Linux EC2 instances. Hỗ trợ hierarchical directory structure.
- EFS có thể được mount từ nhiều EC2 instances cùng lúc (cùng lúc read/write).
- EFS tự động scale storage, hỗ trợ multi-AZ (tạo mount targets trong mỗi AZ).
- Performance modes (General Purpose, Max I/O) và throughput modes (Bursting, Provisioned) đáp ứng yêu cầu performance.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A (S3 bucket):** S3 là object storage (key-value), không hỗ trợ hierarchical directory structure. Có thể dùng S3 với prefix (simulate folder) nhưng không phải filesystem. Latency cao hơn và không hỗ trợ file locking.

**❌ Đáp án C (EBS io2 attach to all):** EBS volume không thể attach đến nhiều EC2 instances cùng lúc (chỉ multi-attach io1/io2 cho một số instance type nhưng giới hạn và không phải multi-AZ). Multi-attach EBS chỉ hỗ trợ tối đa 16 instances trong cùng AZ.

**❌ Đáp án D (EBS per instance + sync):** Mỗi instance có EBS riêng và sync data giữa chúng không đảm bảo "read and write rapidly and concurrently" vì có độ trễ sync. Cũng rất phức tạp để quản lý.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Shared file storage for Linux multi-AZ = EFS (NFS). EBS = single instance. S3 = object storage, not filesystem."*
