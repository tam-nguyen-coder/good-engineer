# Question #646 - Topic 1

A solutions architect needs to host a high performance computing (HPC) workload in the AWS Cloud. The workload will run on hundreds of Amazon EC2 instances and will require parallel access to a shared file system to enable distributed processing of large datasets. Datasets will be accessed across multiple instances simultaneously. The workload requires access latency within 1 ms. After processing has completed, engineers will need access to the dataset for manual postprocessing. Which solution will meet these requirements?

## Options

**A.** Use Amazon Elastic File System (Amazon EFS) as a shared file system. Access the dataset from Amazon EFS.

**B.** Mount an Amazon S3 bucket to serve as the shared file system. Perform postprocessing directly from the S3 bucket.

**C.** Use Amazon FSx for Lustre as a shared file system. Link the file system to an Amazon S3 bucket for postprocessing.

**D.** Configure AWS Resource Access Manager to share an Amazon S3 bucket so that it can be mounted to all instances for processing and postprocessing.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** HPC workload, hundreds of EC2 instances, parallel shared file system, sub-1ms latency, simultaneous access to datasets. Engineers need postprocessing access after.
- **Existing Resources:** EC2 instances for HPC.
- **Current Issue/Goal:** High-performance shared file system with S3 integration for postprocessing.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `HPC workload` | High Performance Computing → cần high throughput, low latency. |
| `hundreds of EC2 instances` | Many clients simultaneously accessing. |
| `parallel access` | Shared file system cần hỗ trợ nhiều client. |
| `within 1 ms` | FSx for Lustre có latency sub-millisecond. |
| `postprocessing` | Engineers cần access sau khi compute xong → S3 là persistent storage. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements (performance + postprocessing)
- **Constraints:** Sub-1ms latency, hundreds instances, parallel access

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- FSx for Lustre được thiết kế cho HPC, cung cấp throughput cao, latency sub-millisecond.
- Hỗ trợ hàng trăm instances truy cập đồng thời (POSIX-compliant shared file system).
- Link với S3 bucket: dữ liệu được lazy load từ S3 vào Lustre khi xử lý, sau đó kết quả có thể được export lại S3 cho postprocessing.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- EFS latency không đảm bảo dưới 1ms cho HPC workloads. EFS phù hợp cho general-purpose file storage.

**❌ Đáp án B:**
- S3 không phải file system (object storage). Mount S3 bằng công cụ third-party không đáp ứng latency và POSIX requirements.

**❌ Đáp án D:**
- AWS RAM chia sẻ S3 bucket, nhưng S3 vẫn là object store, không phải shared file system với POSIX semantics.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"HPC + sub-1ms + parallel access = FSx for Lustre. Link to S3 for postprocessing."*
