# IAM — Policy evaluation logic (Deny > Allow > implicit Deny)

> **Nguồn (AWS official):** https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html
> **Tuần:** 6 — Security I: `IAM` + `STS` + `Cognito` · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- **Thứ tự đánh giá bất di bất dịch:** explicit `Deny` > explicit `Allow` > implicit `Deny` (mặc định). Chỉ cần MỘT explicit `Deny` là request bị chặn, bất kể có bao nhiêu `Allow`.
- **Identity-based + resource-based (trong CÙNG account):** kết quả là **UNION** (hợp) của hai loại — action được phép nếu identity-based HOẶC resource-based HOẶC cả hai cho phép. Nhưng explicit `Deny` ở bất kỳ đâu vẫn override.
- **Identity-based + permissions boundary:** kết quả là **INTERSECTION** (giao) — action phải được cho phép ở CẢ HAI. Thêm boundary có thể thu hẹp quyền.
- **Identity-based + SCP/RCP (Organizations):** kết quả là **INTERSECTION** của cả 3 (user policy + SCP + RCP) — action phải được cho phép ở cả ba loại.
- **Bẫy hay gặp:** "cross-account" thì UNION không còn đúng — request phải được cho phép ở CẢ identity-based (account nguồn) LẪN resource-based (account đích).
- Nhớ 3 bước AWS xử lý mỗi request: (1) Authentication → (2) Processing the request context → (3) Evaluating allow/deny.

---

## 📄 Nội dung (trích từ tài liệu gốc)

# Policy evaluation logic

When a principal tries to use the AWS Management Console, the AWS API, or the AWS CLI, that principal sends a *request* to AWS. When an AWS service receives the request, AWS completes several steps to determine whether to allow or deny the request.

1. **Authentication** – AWS first authenticates the principal that makes the request, if necessary. This step is not necessary for a few services, such as Amazon S3, that allow some requests from anonymous users.
2. **Processing the request context** – AWS processes the information gathered in the request to determine which policies apply to the request.
3. **How AWS enforcement code logic evaluates requests to allow or deny access** – AWS evaluates all of the policy types and the order of the policies affects how they are evaluated. AWS then processes the policies against the request context to determine whether the request is allowed or denied.

## Evaluating identity-based policies with resource-based policies

Identity-based policies and resource-based policies grant permissions to the identities or resources to which they are attached. When an IAM entity (user or role) requests access to a resource **within the same account**, AWS evaluates all the permissions granted by the identity-based and resource-based policies. The resulting permissions are the **union** of the permissions of the two types. If an action is allowed by an identity-based policy, a resource-based policy, or both, then AWS allows the action. **An explicit deny in either of these policies overrides the allow.**

## Evaluating identity-based policies with permissions boundaries

When AWS evaluates the identity-based policies and permissions boundary for a user, the resulting permissions are the **intersection** of the two categories. That means that when you add a permissions boundary to a user with existing identity-based policies, you might **reduce** the actions that the user can perform. Alternatively, when you remove a permissions boundary from a user, you might increase the actions they can perform. An explicit deny in either of these policies overrides the allow.

## Evaluating identity-based policies with AWS Organizations SCPs or RCPs

When a user belongs to an account that is a member of an organization and accesses a resource that doesn't have a resource-based policy configured, the resulting permissions are the **intersection** of the user's policies, service control policies (SCPs), and resource control policy (RCP). This means that an action must be **allowed by all three policy types**. An explicit deny in the identity-based policy, an SCP, or an RCP overrides the allow.

You can learn whether your account is a member of an organization in AWS Organizations. Organization members might be affected by an SCP or RCP. To view this data using the AWS CLI command or AWS API operation, you must have permissions for the `organizations:DescribeOrganization` action for your AWS Organizations entity. You must have additional permissions to perform the operation in the AWS Organizations console. To learn whether an SCP or RCP is denying access to a specific request, or to change your effective permissions, contact your AWS Organizations administrator.
