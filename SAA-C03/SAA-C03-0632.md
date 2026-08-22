# Question #632 - Topic 1

A company is creating a new application that will store a large amount of data. The data will be analyzed hourly and will be modified by several Amazon EC2 Linux instances that are deployed across multiple Availability Zones. The needed amount of storage space will continue to grow for the next 6 months. Which storage solution should a solutions architect recommend to meet these requirements?

## Options

**A.** Store the data in Amazon S3 Glacier. Update the S3 Glacier vault policy to allow access to the application instances.

**B.** Store the data in an Amazon Elastic Block Store (Amazon EBS) volume. Mount the EBS volume on the application instances.

**C.** Store the data in an Amazon Elastic File System (Amazon EFS) file system. Mount the file system on the application instances.

**D.** Store the data in an Amazon Elastic Block Store (Amazon EBS) Provisioned IOPS volume shared between the application instances.

## 1. CONTEXT & DE BAI
- **Scenario:** Luu tru data lon, duoc analyze hourly, modified by nhieu EC2 Linux instances across multiple AZs. Storage can continue growing for 6 months.
- **Existing Resources:** EC2 Linux instances in multiple AZs.
- **Current Issue/Goal:** Shared file system, scalable, accessible from multiple AZs.

## 2. KEYWORDS QUAN TRONG
| Keyword | Y nghia / Goi y |
|---------|-----------------|
| `several Amazon EC2 Linux instances` | Can shared storage, nhieu instances cung truy cap. |
| `multiple Availability Zones` | Storage phai truy cap duoc tu nhieu AZ. |
| `continue to grow` | Can scalable storage, khong can provision truoc. |
| `Amazon EFS` | Managed NFS filesystem, scalable, accessible from multiple AZs. |
| `EBS volume` | Chi attach duoc 1 EC2 instance trong 1 AZ (tru Multi-Attach EBS, nho). |

## 3. YEU CAU CUA DE
- **Question type:** Meet requirements
- **Constraints:** Multiple instances, multiple AZs, growing storage, Linux

## 4. DAP AN DUNG
**Dap an: C**

**Giai thich:**
- Amazon EFS: NFS file system dung chung cho nhieu EC2 instances, co the truy cap tu nhieu AZ cung luc.
- Tu dong scale dung luong (pay-per-use), khong can provision truoc => phu hop voi storage dang tang.
- Hoat dong tot voi Linux instances.

## 5. CAC DAP AN SAI
**Dap an A:**
- S3 Glacier: dung cho archive, khong phu hop cho data duoc analyze hourly (retrieval time lau).

**Dap an B:**
- EBS volume: chi co the attach vao 1 EC2 instance trong 1 Availability Zone, khong the share cho nhieu instances o nhieu AZs.

**Dap an D:**
- EBS Provisioned IOPS: van la EBS, khong the share cho nhieu instances o nhieu AZs.
- Multi-Attach EBS chi ho tro cho io1/io2 va gioi han so instances.

## 6. MEO GHI NHO (Memory Hook)
*"Multiple EC2, multiple AZs, growing => EFS (shared NFS). EBS = single instance/single AZ."*
