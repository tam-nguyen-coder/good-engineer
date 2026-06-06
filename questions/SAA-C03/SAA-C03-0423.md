# Question #423 - Topic 1

A solutions architect wants to use the following JSON text as an identity-based policy to grant specific permissions: Which IAM principals can the solutions architect attach this policy to? (Choose two.)

## Options

**A.** Role

**B.** Group

**C.** Organization

**D.** Amazon Elastic Container Service (Amazon ECS) resource

**E.** Amazon EC2 resource

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Identity-based IAM policy. Which principals can attach it to?
- **Existing Resources:** N/A
- **Current Issue/Goal:** Identify valid attachable principals for identity-based policies.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `identity-based policy` | Attached to IAM identity: User, Group, Role. |
| `principals` | Entities that can be attached with identity-based policy. |
| `IAM` | IAM Users, Groups, Roles. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** IAM / Policy basics
- **Constraints:** Identity-based policy attachment

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A, B**

**Giải thích:**
- Identity-based policies attach to IAM Users, Groups, or Roles.
- **A:** Role ✓
- **B:** Group ✓

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án C:**
- Organization (AWS Organizations) không phải IAM principal. SCPs attach to OUs, not identity-based.

**❌ Đáp án D:**
- ECS resource: resource-based policy (task role), không phải identity-based.

**❌ Đáp án E:**
- EC2 resource: không có identity. Dùng IAM role cho EC2 (instance profile).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Identity-based policy → User, Group, or Role. Not resource, not organization."*