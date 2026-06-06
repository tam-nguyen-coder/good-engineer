# Question #299 - Topic 1

A research laboratory needs to process approximately 8 TB of data. The laboratory requires sub-millisecond latencies and a minimum throughput of 6 GBps for the storage subsystem. Hundreds of Amazon EC2 instances that run Amazon Linux will distribute and process the data. Which solution will meet the performance requirements?

## Options

**A.** Create an Amazon FSx for NetApp ONTAP file system. Sat each volume' tiering policy to ALL. Import the raw data into the file system. Mount the fila system on the EC2 instances.

**B.** Create an Amazon S3 bucket to store the raw data. Create an Amazon FSx for Lustre file system that uses persistent SSD storage. Select the option to import data from and export data to Amazon S3. Mount the file system on the EC2 instances.

**C.** Create an Amazon S3 bucket to store the raw data. Create an Amazon FSx for Lustre file system that uses persistent HDD storage. Select the option to import data from and export data to Amazon S3. Mount the file system on the EC2 instances.

**D.** Create an Amazon FSx for NetApp ONTAP file system. Set each volume's tiering policy to NONE. Import the raw data into the file system. Mount the file system on the EC2 instances.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** 8 TB data, sub-millisecond latency, 6 GBps throughput, hundreds of Linux EC2 instances processing.
- **Existing Resources:** Hundreds of Linux EC2 instances.
- **Current Issue/Goal:** High-performance shared storage cho HPC workload.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `sub-millisecond latencies` | Cực kỳ low latency → cần SSD, không phải HDD. |
| `minimum throughput of 6 GBps` | Rất cao → FSx for Lustre là lựa chọn hàng đầu cho HPC throughput. |
| `hundreds of EC2 instances` | Cần shared file system scalable. |
| `Amazon Linux` | Linux-based → EFS, FSx for Lustre đều compatible. |
| `FSx for Lustre` | High-performance file system cho HPC, hỗ trợ sub-ms latency và GBps throughput. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which solution meets performance requirements
- **Constraints:** Sub-ms latency, 6 GBps throughput, shared access, 8 TB

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- FSx for Lustre persistent SSD là lựa chọn tối ưu cho HPC: sub-millisecond latency, hàng GBps throughput, hỗ trợ hundreds of clients.
- Tích hợp S3: import raw data từ S3, export kết quả về S3.
- SSD (persistent) đáp ứng sub-ms latency (HDD không đạt).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- FSx for NetApp ONTAP không đạt throughput 6 GBps cho HPC workload (thiết kế cho enterprise storage, không phải HPC).

**❌ Đáp án C:**
- FSx for Lustre HDD không đáp ứng sub-millisecond latency (HDD có latency cao hơn SSD).

**❌ Đáp án D:**
- FSx for NetApp ONTAP không phù hợp cho HPC throughput cao.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"HPC + sub-ms latency + GBps throughput → FSx for Lustre SSD. Không dùng NetApp ONTAP hay HDD."*
