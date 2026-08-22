# Question #465 - Topic 1

A company is developing an application to support customer demands. The company wants to deploy the application on multiple Amazon EC2 Nitro-based instances within the same Availability Zone. The company also wants to give the application the ability to write to multiple block storage volumes in multiple EC2 Nitro-based instances simultaneously to achieve higher application availability. Which solution will meet these requirements?

## Options

**A.** Use General Purpose SSD (gp3) EBS volumes with Amazon Elastic Block Store (Amazon EBS) Multi-Attach

**B.** Use Throughput Optimized HDD (st1) EBS volumes with Amazon Elastic Block Store (Amazon EBS) Multi-Attach

**C.** Use Provisioned IOPS SSD (io2) EBS volumes with Amazon Elastic Block Store (Amazon EBS) Multi-Attach

**D.** Use General Purpose SSD (gp2) EBS volumes with Amazon Elastic Block Store (Amazon EBS) Multi-Attach

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Application cần write đồng thời vào nhiều block storage volumes từ nhiều EC2 Nitro instances trong cùng AZ.
- **Existing Resources:** EC2 Nitro-based instances.
- **Current Issue/Goal:** Higher application availability bằng cách multi-attach EBS volumes.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `EC2 Nitro-based instances` | Multi-Attach chỉ hỗ trợ trên Nitro-based instances. |
| `within the same Availability Zone` | Multi-Attach chỉ hoạt động trong cùng AZ. |
| `write to multiple block storage volumes simultaneously` | Cần EBS Multi-Attach. |
| `Multi-Attach` | Chỉ hỗ trợ trên io1/io2 volume types (Provisioned IOPS SSD). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Multi-Attach block storage
- **Constraints:** Same AZ, Nitro instances, write simultaneously

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- EBS Multi-Attach: cho phép attach một EBS volume vào nhiều EC2 instances cùng lúc (tối đa 16 instances).
- Chỉ io1/io2 (Provisioned IOPS SSD) hỗ trợ Multi-Attach.
- Tất cả instances phải trong cùng AZ và là Nitro-based.
- Các instances có thể read/write đồng thời (cần cluster-aware filesystem).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A (gp3):**
- gp3 không hỗ trợ Multi-Attach.

**❌ Đáp án B (st1):**
- st1 (Throughput Optimized HDD) không hỗ trợ Multi-Attach.

**❌ Đáp án D (gp2):**
- gp2 không hỗ trợ Multi-Attach.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Multi-Attach = io1/io2 only. gp2/gp3/st1 = không Multi-Attach được."*
