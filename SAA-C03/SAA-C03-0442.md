# Question #442 - Topic 1

A company stores several petabytes of data across multiple AWS accounts. The company uses AWS Lake Formation to manage its data lake. The company's data science team wants to securely share selective data from its accounts with the company's engineering team for analytical purposes. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Copy the required data to a common account. Create an IAM access role in that account. Grant access by specifying a permission policy that includes users from the engineering team accounts as trusted entities.

**B.** Use the Lake Formation permissions Grant command in each account where the data is stored to allow the required engineering team users to access the data.

**C.** Use AWS Data Exchange to privately publish the required data to the required engineering team accounts.

**D.** Use Lake Formation tag-based access control to authorize and grant cross-account permissions for the required data to the engineering team accounts.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Petabytes across multiple accounts. Lake Formation data lake. Securely share selective data cross-account to engineering team.
- **Existing Resources:** Lake Formation, multiple AWS accounts.
- **Current Issue/Goal:** Cross-account data sharing. Least ops overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Lake Formation` | Centralized data lake permissions. |
| `selective data` | Fine-grained access control. |
| `cross-account` | Lake Formation tag-based access control (LF-TBAC). |
| `least operational overhead` | Tag-based: set once, propagate. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Data governance / Cross-account
- **Constraints:** Selective sharing, multiple accounts, least overhead

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- Lake Formation tag-based access control (LF-TBAC): gán tags cho data (database, table, column).
- Grant permissions dựa trên tags → tự động áp dụng cho resources có tags đó.
- Cross-account sharing: share tags + grant access → data science team tự access data được authorized.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Copy data to common account: data duplication, chi phí lưu trữ tăng, không scalable.

**❌ Đáp án B:**
- Grant permissions per account: phải thực hiện ở mỗi account → operational overhead cao.

**❌ Đáp án C:**
- AWS Data Exchange: cho external data products (bên thứ ba), không phải internal sharing.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Lake Formation cross-account sharing → LF-TBAC (tag-based). No data copy needed."*