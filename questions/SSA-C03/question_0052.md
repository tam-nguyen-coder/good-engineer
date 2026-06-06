# Question #52 - Topic 1

A company wants to migrate its on-premises application to AWS. The application produces output files that vary in size from tens of gigabytes to hundreds of terabytes. The application data must be stored in a standard file system structure. The company wants a solution that scales automatically. is highly available, and requires minimum operational overhead. Which solution will meet these requirements?

## Options

**A.** Migrate the application to run as containers on Amazon Elastic Container Service (Amazon ECS). Use Amazon S3 for storage.

**B.** Migrate the application to run as containers on Amazon Elastic Kubernetes Service (Amazon EKS). Use Amazon Elastic Block Store (Amazon EBS) for storage.

**C.** Migrate the application to Amazon EC2 instances in a Multi-AZ Auto Scaling group. Use Amazon Elastic File System (Amazon EFS) for storage.

**D.** Migrate the application to Amazon EC2 instances in a Multi-AZ Auto Scaling group. Use Amazon Elastic Block Store (Amazon EBS) for storage.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Migrate on-prem app lên AWS. App tạo output files từ tens of GB đến hundreds of TB.
- **Existing Resources:** On-prem application.
- **Current Issue/Goal:** Cần standard file system structure, auto-scale, highly available, minimum operational overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `standard file system structure` | Cần POSIX file system (không phải object storage) |
| `varies in size from tens of GB to hundreds of TB` | Cần storage có khả năng scale lớn |
| `scales automatically` | Storage tự động mở rộng |
| `highly available` | Multi-AZ |
| `minimum operational overhead` | Managed service |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Highly available + scalable + low overhead
- **Constraints:** Standard file system (POSIX), auto-scale, HA, managed

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **Amazon EFS** là managed NFS file system, hỗ trợ standard file system structure (POSIX), tự động scale từ GB đến PB.
- **Multi-AZ Auto Scaling group** cho EC2 instances đảm bảo HA và tính sẵn sàng.
- **Minimum operational overhead** — EFS là fully managed, không cần provision capacity trước.
- Files > 100TB được EFS hỗ trợ tốt (EFS scale tự động).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- S3 là object storage, **không phải standard file system structure** (không hỗ trợ POSIX, locking, etc.).
- ECS không liên quan trực tiếp đến yêu cầu file system.

**❌ Đáp án B:**
- EBS không tự động scale — phải resize thủ công.
- EBS volume gắn vào một EC2 instance duy nhất — không thể share giữa nhiều instances trong ASG (trừ EBS Multi-Attach nhưng giới hạn).
- EBS không phải "standard file system" shared storage.

**❌ Đáp án D:**
- Giống B — EBS không scale tự động, không share được giữa nhiều instances.
- Không phù hợp cho hàng trăm TB data.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"EFS = POSIX file system, auto-scale, shared Multi-AZ. EBS = block storage, single instance, manual scale"*
