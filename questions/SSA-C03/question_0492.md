# Question #492 - Topic 1

A company has multiple AWS accounts for development work. Some staff consistently use oversized Amazon EC2 instances, which causes the company to exceed the yearly budget for the development accounts. The company wants to centrally restrict the creation of AWS resources in these accounts. Which solution will meet these requirements with the LEAST development effort?

## Options

**A.** Develop AWS Systems Manager templates that use an approved EC2 creation process. Use the approved Systems Manager templates to provision EC2 instances.

**B.** Use AWS Organizations to organize the accounts into organizational units (OUs). Define and attach a service control policy (SCP) to control the usage of EC2 instance types.

**C.** Configure an Amazon EventBridge rule that invokes an AWS Lambda function when an EC2 instance is created. Stop disallowed EC2 instance types.

**D.** Set up AWS Service Catalog products for the staff to create the allowed EC2 instance types. Ensure that staff can deploy EC2 instances only by using the Service Catalog products.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Multiple dev accounts, staff dùng oversized EC2 instances → vượt budget. Cần centrally restrict resource creation.
- **Existing Resources:** Multiple AWS accounts.
- **Current Issue/Goal:** Chặn việc tạo EC2 instances không được phép (oversized), với least development effort.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `centrally restrict` | SCP: central policy áp dụng cho nhiều accounts. |
| `least development effort` | SCP chỉ cần define policy, không cần code. |
| `oversized Amazon EC2 instances` | Cần restrict instance types được phép launch. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least development effort
- **Constraints:** Centrally restrict EC2 instance types across multiple accounts.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **AWS Organizations + SCP:** Tổ chức accounts vào OUs, define SCP deny EC2:RunInstances với instance types không được phép.
- SCP được attach vào OU → áp dụng cho tất cả accounts trong OU.
- **Không cần code** - chỉ cần JSON policy.
- **Preventive control:** Chặn trước khi resource được tạo (không phải reactive như EventBridge).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- **Systems Manager templates:** Chỉ hướng dẫn, không prevent user tạo EC2 trực tiếp từ console/CLI.

**❌ Đáp án C:**
- **EventBridge + Lambda:** Reactive - EC2 đã được tạo rồi mới stop. Tốn chi phí cho resources đã tạo. Development effort cao hơn SCP.

**❌ Đáp án D:**
- **Service Catalog:** User vẫn có thể tạo EC2 trực tiếp ngoài Service Catalog. Service Catalog là "guidance", không phải "enforcement".

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Chặn resource creation → SCP (preventive, zero code). EventBridge + Lambda = reactive (tốn tiền)."*
