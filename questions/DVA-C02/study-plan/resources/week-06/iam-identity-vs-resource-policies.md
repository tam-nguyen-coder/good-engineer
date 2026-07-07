# IAM — Identity-based vs resource-based policies

> **Nguồn (AWS official):** https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_identity-vs-resource.html
> **Tuần:** 6 — Security I: `IAM` + `STS` + `Cognito` · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- **Identity-based policy:** gắn vào IAM user / group / role. Có thể là **managed** hoặc **inline**. KHÔNG có `Principal`.
- **Resource-based policy:** gắn trực tiếp vào tài nguyên (`S3` bucket, `SQS` queue, VPC endpoint, `KMS` key, `DynamoDB` table/stream…). **CHỈ là inline** (không có managed). CÓ `Principal` — chỉ rõ AI được truy cập.
- **Same-account:** quyền hiệu lực = UNION của identity-based và resource-based; chỉ cần một trong hai `Allow` là được (miễn không có `Deny`).
- **Cross-account:** BẮT BUỘC cả hai — identity-based ở account nguồn (A) PHẢI cho phép gọi, VÀ resource-based ở account đích (B) PHẢI cho phép principal của A. Thiếu một bên là fail.
- Bẫy: **resource-based policy** ≠ **resource-level permissions**. Resource-level = dùng ARN để chỉ định tài nguyên cụ thể trong policy (có thể nằm trong identity-based). Chỉ một số service hỗ trợ resource-based policy.
- `S3` đặc biệt: hỗ trợ cả identity-based, resource-based (bucket policy), VÀ ACL (cơ chế độc lập với IAM).

---

## 📄 Nội dung (trích từ tài liệu gốc)

# Identity-based policies and resource-based policies

A policy is an object in AWS that, when associated with an identity or resource, defines their permissions. When you create a permissions policy to restrict access to a resource, you can choose an *identity-based policy* or a *resource-based policy*.

**Identity-based policies** are attached to an IAM user, group, or role. These policies let you specify what that identity can do (its permissions). For example, you can attach the policy to the IAM user named John, stating that he is allowed to perform the Amazon EC2 `RunInstances` action. Identity-based policies can be **managed or inline**.

**Resource-based policies** are attached to a resource. For example, you can attach resource-based policies to Amazon S3 buckets, Amazon SQS queues, VPC endpoints, AWS Key Management Service encryption keys, Amazon DynamoDB tables and streams, and AWS Sign-In resources. With resource-based policies, you can specify **who** has access to the resource and what actions they can perform on it. **Resource-based policies are inline only, not managed.**

**Note:** *Resource-based* policies differ from *resource-level* permissions. You can attach resource-based policies directly to a resource. Resource-level permissions refer to the ability to use ARNs to specify individual resources in a policy. Resource-based policies are supported only by some AWS services.

### Ví dụ (account 123456789012)
+ **John** – can perform list and read actions on `Resource X`. Granted by the identity-based policy on his user AND the resource-based policy on `Resource X`.
+ **Carlos** – can perform list, read, and write on `Resource Y`, but is **denied** access to `Resource Z`. His identity-based policy allows him access to `Resource Z`, but the `Resource Z` resource-based policy denies that access. **An explicit `Deny` overrides an `Allow`.**
+ **Mary** – can perform list, read, and write on `Resource X`, `Y`, and `Z`. Her identity-based policy allows more than the resource-based policies, but none deny access.
+ **Zhang** – has full access to `Resource Z`. Zhang has **no identity-based policies**, but the `Resource Z` resource-based policy allows him full access. Zhang can also perform list and read on `Resource Y`.

### Cách hai loại policy phối hợp
Identity-based policies and resource-based policies are both permissions policies and are evaluated together. For a request to which only permissions policies apply, AWS first checks all policies for a `Deny`. If one exists, then the request is denied. Then AWS checks for each `Allow`. **If at least one policy statement allows the action in the request, the request is allowed.** It doesn't matter whether the `Allow` is in the identity-based policy or the resource-based policy.

**Important (cross-account):**
This union logic applies **only when the request is made within a single AWS account**. For requests made from one account to another, the requester in `Account A` must have an **identity-based policy** that allows them to make a request to the resource in `Account B`. Also, the **resource-based policy** in `Account B` must allow the requester in `Account A` to access the resource. **There must be policies in BOTH accounts that allow the operation, otherwise the request fails.**

**Note (S3):** Amazon S3 supports identity-based policies and resource-based policies (referred to as *bucket policies*). In addition, Amazon S3 supports a permission mechanism known as an *access control list (ACL)* that is independent of IAM policies and permissions.
