# Question #252 - Topic 1

A solutions architect needs to design a system to store client case files. The files are core company assets and are important. The number of files will grow over time. The files must be simultaneously accessible from multiple application servers that run on Amazon EC2 instances. The solution must have built-in redundancy. Which solution meets these requirements?

## Options

**A.** Amazon Elastic File System (Amazon EFS)

**B.** Amazon Elastic Block Store (Amazon EBS)

**C.** Amazon S3 Glacier Deep Archive

**D.** AWS Backup

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Store client case files, important, growing. Simultaneous access from multiple EC2 instances. Built-in redundancy.
- **Existing Resources:** Application servers on EC2.
- **Current Issue/Goal:** Shared, redundant file storage.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `simultaneously accessible from multiple` | **EFS** (shared NFS) |
| `built-in redundancy` | EFS replicated across AZs |
| `files... grow over time` | EFS auto-scaling |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Storage / File system
- **Constraints:** Shared, redundant, growing

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **EFS** — NFS file system, có thể mount từ multiple EC2 instances.
- Built-in redundancy (replicated across AZs).
- Auto-scaling — không cần provision capacity.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- EBS — single-attach, không thể shared.

**❌ Đáp án C:**
- Glacier Deep Archive — retrieval time phút→giờ, không simultaneous access.

**❌ Đáp án D:**
- AWS Backup — backup service, không phải primary storage.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"EFS = shared file system for EC2. EBS = single-attach. Glacier = archive (not real-time)"*
