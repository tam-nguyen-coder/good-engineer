# Question #162 - Topic 1

A company wants to use high performance computing (HPC) infrastructure on AWS for financial risk modeling. The company's HPC workloads run on Linux. Each HPC workflow runs on hundreds of Amazon EC2 Spot Instances, is short-lived, and generates thousands of output files that are ultimately stored in persistent storage for analytics and long-term future use. The company seeks a cloud storage solution that permits the copying of on-premises data to long-term persistent storage to make data available for processing by all EC2 instances. The solution should also be a high performance file system that is integrated with persistent storage to read and write datasets and output files. Which combination of AWS services meets these requirements?

## Options

**A.** Amazon FSx for Lustre integrated with Amazon S3

**B.** Amazon FSx for Windows File Server integrated with Amazon S3

**C.** Amazon S3 Glacier integrated with Amazon Elastic Block Store (Amazon EBS)

**D.** Amazon S3 bucket with a VPC endpoint integrated with an Amazon Elastic Block Store (Amazon EBS) General Purpose SSD (gp2) volume

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** HPC financial risk modeling, Linux, hundreds of Spot Instances, short-lived, thousands of output files.
- **Existing Resources:** On-prem data.
- **Current Issue/Goal:** High-performance file system + persistent storage (S3), shared across instances.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `HPC workloads on Linux` | **FSx for Lustre** (high-performance, Linux) |
| `high performance file system` | Lustre = HPC-grade |
| `integrated with persistent storage` | FSx for Lustre integrates with **S3** |
| `hundreds of EC2 Spot Instances` | Shared file system needed |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** HPC Storage
- **Constraints:** High performance, persistent, shared

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **FSx for Lustre** — high-performance file system designed for HPC, Linux-compatible.
- **Integrated with S3** — data từ on-prem copied vào S3 (persistent), FSx for Lustre đọc/ghi từ S3.
- Output files từ HPC jobs có thể lưu vào S3 qua FSx.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- FSx for Windows — Windows file server, không phù hợp HPC Linux.

**❌ Đáp án C:**
- S3 Glacier + EBS — Glacier chậm, EBS không shared.

**❌ Đáp án D:**
- S3 + EBS gp2 — không high-performance file system.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"FSx for Lustre + S3 = HPC storage (Linux). FSx for Windows = Windows only. EBS = not shared"*
