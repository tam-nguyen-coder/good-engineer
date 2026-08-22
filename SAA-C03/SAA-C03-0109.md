# Question #109 - Topic 1

A company needs to store data in Amazon S3 and must prevent the data from being changed. The company wants new objects that are uploaded to Amazon S3 to remain unchangeable for a nonspecific amount of time until the company decides to modify the objects. Only specific users in the company's AWS account can have the ability 10 delete the objects. What should a solutions architect do to meet these requirements?

## Options

**A.** Create an S3 Glacier vault. Apply a write-once, read-many (WORM) vault lock policy to the objects.

**B.** Create an S3 bucket with S3 Object Lock enabled. Enable versioning. Set a retention period of 100 years. Use governance mode as the S3 bucket’s default retention mode for new objects.

**C.** Create an S3 bucket. Use AWS CloudTrail to track any S3 API events that modify the objects. Upon notification, restore the modified objects from any backup versions that the company has.

**D.** Create an S3 bucket with S3 Object Lock enabled. Enable versioning. Add a legal hold to the objects. Add the s3:PutObjectLegalHold permission to the IAM policies of users who need to delete the objects.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** S3 data immutable cho đến khi company quyết định modify. Chỉ specific users được delete.
- **Existing Resources:** S3 bucket.
- **Current Issue/Goal:** WORM protection with flexible duration (legal hold).

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `nonspecific amount of time` | Không cố định retention period — cần **legal hold** |
| `prevent the data from being changed` | WORM protection |
| `Only specific users can delete` | IAM permissions cho legal hold |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Compliance / Security
- **Constraints:** Flexible retention, specific users can delete

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **S3 Object Lock legal hold** — protection vô thời hạn, không cần retention period.
- Legal hold có thể được thêm/gỡ bởi users có `s3:PutObjectLegalHold` permission.
- **Versioning** required cho Object Lock.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Glacier Vault Lock — cho archived data, không phải active S3.

**❌ Đáp án B:**
- Governance mode có thể bị bypass bởi users có quyền.
- Retention period 100 năm là cố định, không "nonspecific amount of time".

**❌ Đáp án C:**
- CloudTrail + restore — reactive, không preventive. Không ngăn chặn modification.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Legal hold = WORM vô thời hạn, flexible. Retention period = fixed duration. Governance mode = có thể bypass"*
