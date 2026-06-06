# Question #455 - Topic 1

A company uses AWS Organizations. The company wants to operate some of its AWS accounts with different budgets. The company wants to receive alerts and automatically prevent provisioning of additional resources on AWS accounts when the allocated budget threshold is met during a specific period. Which combination of solutions will meet these requirements? (Choose three.)

## Options

**A.** Use AWS Budgets to create a budget. Set the budget amount under the Cost and Usage Reports section of the required AWS accounts.

**B.** Use AWS Budgets to create a budget. Set the budget amount under the Billing dashboards of the required AWS accounts.

**C.** Create an IAM user for AWS Budgets to run budget actions with the required permissions.

**D.** Create an IAM role for AWS Budgets to run budget actions with the required permissions.

**E.** Add an alert to notify the company when each account meets its budget threshold. Add a budget action that selects the IAM identity created with the appropriate config rule to prevent provisioning of additional resources.

**F.** Add an alert to notify the company when each account meets its budget threshold. Add a budget action that selects the IAM identity created with the appropriate service control policy (SCP) to prevent provisioning of additional resources.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** AWS Organizations, different budgets per account. Alert + auto-prevent provisioning when threshold met.
- **Existing Resources:** AWS Organizations, multiple accounts.
- **Current Issue/Goal:** Budget alerts + automatic resource prevention.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `budget threshold` | AWS Budgets: set budget amount. |
| `prevent provisioning` | Budget action with SCP (service control policy). |
| `IAM role` | Budget actions need IAM role (not user). |
| `Choose three` | 3 answers required. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost management / Governance
- **Constraints:** Budget alerts + auto prevention

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B, D, F**

**Giải thích:**
- **B:** AWS Budgets created under Billing dashboards.
- **D:** IAM role for Budgets to execute budget actions (not IAM user).
- **F:** Alert + budget action with SCP to prevent resource provisioning.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Budgets are set under Billing console, not Cost and Usage Reports.

**❌ Đáp án C:**
- IAM user: service should use IAM role for cross-account actions.

**❌ Đáp án E:**
- Config rule không prevent provisioning (detective, not preventive).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Budget threshold reached → Budgets + IAM role + SCP budget action (prevent resources)."*