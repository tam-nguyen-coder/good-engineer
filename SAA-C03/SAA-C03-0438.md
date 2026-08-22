# Question #438 - Topic 1

A company wants to share accounting data with an external auditor. The data is stored in an Amazon RDS DB instance that resides in a private subnet. The auditor has its own AWS account and requires its own copy of the database. What is the MOST secure way for the company to share the database with the auditor?

## Options

**A.** Create a read replica of the database. Configure IAM standard database authentication to grant the auditor access.

**B.** Export the database contents to text files. Store the files in an Amazon S3 bucket. Create a new IAM user for the auditor. Grant the user access to the S3 bucket.

**C.** Copy a snapshot of the database to an Amazon S3 bucket. Create an IAM user. Share the user's keys with the auditor to grant access to the object in the S3 bucket.

**D.** Create an encrypted snapshot of the database. Share the snapshot with the auditor. Allow access to the AWS Key Management Service (AWS KMS) encryption key.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** RDS database (private subnet) with accounting data. Auditor has own AWS account, needs own copy.
- **Existing Resources:** RDS DB instance in private subnet.
- **Current Issue/Goal:** Share DB copy securely with external account.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `external auditor` | Separate AWS account → cross-account sharing. |
| `own copy of the database` | Share snapshot, not live access. |
| `most secure` | Encrypted snapshot + KMS cross-account access. |
| `private subnet` | DB not publicly accessible. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / Cross-account
- **Constraints:** Own copy, external account, most secure

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- Encrypted RDS snapshot: data encrypted at rest.
- Share snapshot with auditor's AWS account.
- Allow access to KMS key (cross-account KMS policy) → auditor decrypt và restore snapshot.
- Auditor có copy riêng trong account của họ → kiểm soát access.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Read replica + IAM auth: auditor access vào company's account, không phải own copy. Security risk.

**❌ Đáp án B:**
- Export to S3 + IAM user: IAM user trong company account → auditor access vào company account. S3 không encrypted snapshot.

**❌ Đáp án C:**
- Snapshot to S3? RDS snapshots không thể copy trực tiếp ra S3 bucket. Chia sẻ access keys → insecure.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Share DB with external account → encrypted snapshot + KMS cross-account. No live access."*