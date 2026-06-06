# Question #293 - Topic 1

A company has an on-premises volume backup solution that has reached its end of life. The company wants to use AWS as part of a new backup solution and wants to maintain local access to all the data while it is backed up on AWS. The company wants to ensure that the data backed up on AWS is automatically and securely transferred. Which solution meets these requirements?

## Options

**A.** Use AWS Snowball to migrate data out of the on-premises solution to Amazon S3. Configure on-premises systems to mount the Snowball S3 endpoint to provide local access to the data.

**B.** Use AWS Snowball Edge to migrate data out of the on-premises solution to Amazon S3. Use the Snowball Edge file interface to provide on- premises systems with local access to the data.

**C.** Use AWS Storage Gateway and configure a cached volume gateway. Run the Storage Gateway software appliance on premises and configure a percentage of data to cache locally. Mount the gateway storage volumes to provide local access to the data.

**D.** Use AWS Storage Gateway and configure a stored volume gateway. Run the Storage Gateway software appliance on premises and map the gateway storage volumes to on-premises storage. Mount the gateway storage volumes to provide local access to the data.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** On-premises backup solution end of life. Cần backup lên AWS nhưng vẫn giữ local access to ALL data.
- **Existing Resources:** On-premises backup solution (volume backups).
- **Current Issue/Goal:** Local access to all data + backup to AWS + automatic secure transfer.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `maintain local access to all the data` | Phải có full dataset locally, không chỉ cache một phần. |
| `automatically and securely transferred` | Cần async backup tự động, không phải one-time migration. |
| `stored volume gateway` | Lưu toàn bộ dữ liệu on-premises, async snapshot lên S3. |
| `cached volume gateway` | Chỉ cache dữ liệu thường dùng, phần còn lại lưu trên AWS. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which solution meets requirements
- **Constraints:** Local access to ALL data, automatic backup to AWS

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- Stored volume gateway: toàn bộ dữ liệu lưu on-premises, async snapshot lên S3 → đảm bảo local access to all data.
- Dữ liệu được backup tự động và an toàn qua AWS Storage Gateway (encrypted in transit).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Snowball là one-time migration device, không phải solution cho ongoing backup tự động. Không thể mount Snowball S3 endpoint liên tục.

**❌ Đáp án B:**
- Snowball Edge cũng là one-time device, không phải ongoing backup solution.

**❌ Đáp án C:**
- Cached volume gateway chỉ cache một phần dữ liệu locally → không đáp ứng "maintain local access to all the data".

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"All data locally + AWS backup → Stored Volume Gateway (not cached, not Snowball)."*
