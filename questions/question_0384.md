# Question #384 - Topic 1

A company runs an application on Amazon EC2 Linux instances across multiple Availability Zones. The application needs a storage layer that is highly available and Portable Operating System Interface (POSIX)-compliant. The storage layer must provide maximum data durability and must be shareable across the EC2 instances. The data in the storage layer will be accessed frequently for the first 30 days and will be accessed infrequently after that time. Which solution will meet these requirements MOST cost-effectively?

## Options

**A.** Use the Amazon S3 Standard storage class. Create an S3 Lifecycle policy to move infrequently accessed data to S3 Glacier.

**B.** Use the Amazon S3 Standard storage class. Create an S3 Lifecycle policy to move infrequently accessed data to S3 Standard-Infrequent Access (S3 Standard-IA).

**C.** Use the Amazon Elastic File System (Amazon EFS) Standard storage class. Create a lifecycle management policy to move infrequently accessed data to EFS Standard-Infrequent Access (EFS Standard-IA).

**D.** Use the Amazon Elastic File System (Amazon EFS) One Zone storage class. Create a lifecycle management policy to move infrequently accessed data to EFS One Zone-Infrequent Access (EFS One Zone-IA).

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 Linux multi-AZ, cần HA, POSIX-compliant, shareable, durable storage. Frequent access first 30 days, then infrequent.
- **Existing Resources:** EC2 Linux instances (multi-AZ).
- **Current Issue/Goal:** Cost-effective storage, POSIX, shareable, HA.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `POSIX-compliant` | EFS (NFS) is POSIX-compliant. S3 is not POSIX. |
| `highly available` | EFS Standard (multi-AZ), not One Zone. |
| `shareable across EC2 instances` | EFS shared file system (NFS mount). |
| `frequently → infrequently` | EFS lifecycle management → EFS Standard-IA. |
| `maximum data durability` | EFS Standard (multi-AZ, 11 9s durability). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective
- **Constraints:** POSIX, HA, shareable, multi-AZ

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- EFS Standard: POSIX-compliant, HA (multi-AZ), shareable across EC2 instances, maximum durability.
- EFS lifecycle management: tự động move data xuống EFS Standard-IA sau 30 days → cost-effective.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- S3 không POSIX-compliant (không mount được như file system trừ khi dùng third-party).

**❌ Đáp án B:**
- S3 không POSIX-compliant.

**❌ Đáp án D:**
- EFS One Zone: không highly available (single AZ). Không đáp ứng HA requirement.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"POSIX + HA + shared → EFS Standard (multi-AZ). Lifecycle → IA after 30 days. S3 = không POSIX. One Zone = không HA."*
