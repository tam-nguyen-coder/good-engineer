# Question #154 - Topic 1

A company needs to save the results from a medical trial to an Amazon S3 repository. The repository must allow a few scientists to add new files and must restrict all other users to read-only access. No users can have the ability to modify or delete any files in the repository. The company must keep every file in the repository for a minimum of 1 year after its creation date. Which solution will meet these requirements?

## Options

**A.** Use S3 Object Lock in governance mode with a legal hold of 1 year.

**B.** Use S3 Object Lock in compliance mode with a retention period of 365 days.

**C.** Use an IAM role to restrict all users from deleting or changing objects in the S3 bucket. Use an S3 bucket policy to only allow the IAM role.

**D.** Configure the S3 bucket to invoke an AWS Lambda function every time an object is added. Configure the function to track the hash of the saved object so that modified objects can be marked accordingly.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Medical trial results S3. Few scientists add new files. All others read-only. No modify/delete. Minimum 1 year retention.
- **Existing Resources:** Chưa có.
- **Current Issue/Goal:** WORM + retention, immutable.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `No users can modify or delete` | **S3 Object Lock compliance mode** |
| `minimum of 1 year` | Retention period 365 days |
| `compliance mode` | Không ai (kể cả root) có thể override |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Compliance / Security
- **Constraints:** WORM, 1 year retention

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **Object Lock compliance mode** — strictest WORM: không ai có thể delete/modify trong retention period.
- **Retention period 365 days** — đáp ứng 1 năm.
- Compliance mode không thể bypass kể cả root user.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- **Governance mode** — có thể bị bypass bởi users có `s3:BypassGovernanceRetention`.
- Legal hold là vô thời hạn, không phải retention period cố định.

**❌ Đáp án C:**
- IAM role + bucket policy — có thể bị thay đổi, không đảm bảo immutable.

**❌ Đáp án D:**
- Lambda hash tracking — reactive, không preventive. Không ngăn modification/deletion.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Compliance mode = no one can delete (even root). Governance mode = can be bypassed. Lambda = reactive, not preventive"*
