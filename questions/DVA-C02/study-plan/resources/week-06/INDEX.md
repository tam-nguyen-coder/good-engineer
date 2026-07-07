# 📂 Tài nguyên Tuần 6 — IAM + STS + Cognito

> Crawl từ tài liệu AWS chính thức. Về [file học Tuần 6](../../week-06.md) · [Kế hoạch tổng](../../../DVA-C02-STUDY-PLAN.md)

| # | Tài nguyên (file local) | Chủ đề | Nguồn AWS |
|---|---|---|---|
| 1 | [iam-policy-evaluation-logic.md](iam-policy-evaluation-logic.md) | Quy tắc đánh giá quyền: explicit `Deny` > explicit `Allow` > implicit `Deny`; UNION (id+resource same-account), INTERSECTION (permissions boundary, SCP/RCP) | https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html |
| 2 | [iam-policy-json-elements.md](iam-policy-json-elements.md) | Phần tử JSON policy: `Version`/`Effect`/`Action`/`Resource`/`Condition`/`Principal`; các cặp loại trừ (`Action`/`NotAction`…) | https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements.html |
| 3 | [iam-identity-vs-resource-policies.md](iam-identity-vs-resource-policies.md) | Identity-based (managed/inline, không `Principal`) vs resource-based (inline only, có `Principal`); logic same-account vs cross-account | https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_identity-vs-resource.html |
| 4 | [sts-temporary-credentials.md](sts-temporary-credentials.md) | Temporary credentials: STS global endpoint, federation OIDC/SAML, cross-account, EC2 roles; khuyến nghị `Cognito` cho mobile | https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp.html |
| 5 | [sts-assumerole-api.md](sts-assumerole-api.md) | `AssumeRole`: `DurationSeconds` 900s–43200s (default 3600s), role chaining ≤ 1h, session policy (INTERSECTION, ≤10 ARN/2048 ký tự), MFA, trust policy | https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html |
| 6 | [cognito-user-pools.md](cognito-user-pools.md) | `User Pool` = AUTHENTICATION → JWT; OIDC IdP, federation social/SAML/OIDC, managed login (Hosted UI), MFA, groups, Lambda triggers, M2M | https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-identity-pools.html |
| 7 | [cognito-identity-pools.md](cognito-identity-pools.md) | `Identity Pool` = AUTHORIZATION → temp AWS creds qua `AssumeRoleWithWebIdentity`; authenticated & unauthenticated (guest) role | https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-identity.html |

## Gợi ý thứ tự đọc
1. **IAM policy core (1 → 2 → 3):** trước hết nắm quy tắc đánh giá quyền (Deny > Allow > implicit Deny) và union/intersection, rồi cú pháp phần tử JSON (thấy `Principal` = resource-based), rồi phân biệt identity-based vs resource-based + logic cross-account. Đây là cụm bị hỏi nhiều nhất của Domain 2.
2. **STS (4 → 5):** đọc tổng quan temporary credentials và 4 tình huống (federation/cross-account/EC2), rồi đào sâu `AssumeRole` — thuộc số liệu `DurationSeconds` (900s–43200s, default 3600s), giới hạn role chaining 1h, session policy là INTERSECTION.
3. **Cognito (6 → 7):** User Pool trước (authentication → JWT), Identity Pool sau (authorization → AWS credentials). Ghi nhớ phản xạ: "đăng nhập / trả JWT" → **User Pool**; "client gọi thẳng AWS / cần credentials" → **Identity Pool**. Luồng kết hợp: User Pool → JWT → Identity Pool → temp AWS creds → gọi thẳng DynamoDB/S3.
