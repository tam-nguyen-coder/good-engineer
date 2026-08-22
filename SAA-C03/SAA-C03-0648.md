# Question #648 - Topic 1

A weather forecasting company needs to process hundreds of gigabytes of data with sub-millisecond latency. The company has a high performance computing (HPC) environment in its data center and wants to expand its forecasting capabilities. A solutions architect must identify a highly available cloud storage solution that can handle large amounts of sustained throughput. Files that are stored in the solution should be accessible to thousands of compute instances that will simultaneously access and process the entire dataset. What should the solutions architect do to meet these requirements?

## Options

**A.** Use Amazon FSx for Lustre scratch file systems.

**B.** Use Amazon FSx for Lustre persistent file systems.

**C.** Use Amazon Elastic File System (Amazon EFS) with Bursting Throughput mode.

**D.** Use Amazon Elastic File System (Amazon EFS) with Provisioned Throughput mode.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** HPC weather forecasting, hundreds of GB data, sub-ms latency, thousands of instances simultaneously accessing, sustained throughput, highly available.
- **Existing Resources:** On-premises HPC, expanding to cloud.
- **Current Issue/Goal:** HA cloud storage for HPC + sustained throughput + low latency.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `sub-millisecond latency` | FSx for Lustre đáp ứng (EFS không đảm bảo sub-ms). |
| `highly available` | Persistent (multi-AZ) ≠ Scratch (single AZ, no HA). |
| `sustained throughput` | FSx for Lustre persistent cung cấp sustained throughput. |
| `thousands of compute instances simultaneously` | FSx for Lustre scale tốt hơn EFS cho số lượng lớn clients. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements
- **Constraints:** HA, sub-ms latency, sustained throughput, many concurrent instances

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- FSx for Lustre persistent: cung cấp sustained throughput (không phụ thuộc burst credits), sub-ms latency.
- Highly available: persistent mode có auto-healing và replica trong cùng AZ (persistent 1) hoặc multi-AZ.
- Designed cho HPC workloads với hàng ngàn clients.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Scratch file system: không HA (không replica), data mất nếu server fail. Phù hợp cho temporary data.

**❌ Đáp án C:**
- EFS Bursting Throughput: throughput phụ thuộc vào burst credits, không đảm bảo sustained throughput cho HPC.

**❌ Đáp án D:**
- EFS Provisioned Throughput: có thể provision throughput nhưng latency không đảm bảo sub-ms, và không scale tốt cho thousands instances như FSx for Lustre.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"HPC + HA + sustained throughput = FSx for Lustre Persistent. Scratch = no HA."*
