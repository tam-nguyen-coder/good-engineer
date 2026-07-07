# STS — AssumeRole API Reference

> **Nguồn (AWS official):** https://docs.aws.amazon.com/STS/latest/APIReference/API_AssumeRole.html
> **Tuần:** 6 — Security I: `IAM` + `STS` + `Cognito` · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- `AssumeRole` trả về temporary credentials gồm **access key ID + secret access key + security (session) token**. Dùng cho same-account hoặc **cross-account**.
- **`DurationSeconds`:** min **900s (15 phút)**, max **43200s (12 giờ)** — nhưng chặn trên bởi *max session duration* của role (từ 1h đến 12h). **Mặc định 3600s (1 giờ).**
- **Role chaining** (dùng creds tạm để assume role tiếp) giới hạn session tối đa **1 giờ** — truyền `DurationSeconds` > 1h khi chaining sẽ FAIL.
- **KHÔNG thể** dùng credentials từ `AssumeRole` để gọi `GetFederationToken` hay `GetSessionToken`.
- **Session policy** (inline hoặc tối đa **10 managed policy ARN**): quyền kết quả = **INTERSECTION** của identity-based policy của role VÀ session policy. Session policy KHÔNG cấp được nhiều quyền hơn role. Plaintext policy tối đa **2.048 ký tự**.
- **MFA:** truyền `SerialNumber` (ARN/serial thiết bị MFA) + `TokenCode` (6 chữ số TOTP) khi trust policy có điều kiện `aws:MultiFactorAuthPresent`.
- **Trust policy** của role quyết định AI được assume (đóng vai trò như resource-based policy). Cross-account: account đích phải trust account nguồn, và user nguồn phải có quyền `sts:AssumeRole` với ARN của role đích.
- **Session tags:** tối đa **50 tag**; key ≤ 128 ký tự, value ≤ 256 ký tự. `ExternalId` chống "confused deputy" khi cấp quyền cho bên thứ ba.

---

## 📄 Nội dung (trích từ tài liệu gốc)

# AssumeRole

Returns a set of temporary security credentials that you can use to access AWS resources. These temporary credentials consist of an **access key ID, a secret access key, and a security token**. Typically, you use `AssumeRole` within your account or for cross-account access.

**Permissions**
The temporary security credentials created by `AssumeRole` can be used to make API calls to any AWS service **with the following exception: You cannot call the AWS STS `GetFederationToken` or `GetSessionToken` API operations.**

(Optional) You can pass inline or managed **session policies**. You can pass a single JSON policy document to use as an inline session policy. You can also specify **up to 10 managed policy ARNs**. The plaintext for both inline and managed session policies **can't exceed 2,048 characters**. The resulting session's permissions are the **intersection of the role's identity-based policy and the session policies**. You cannot use session policies to grant more permissions than those allowed by the identity-based policy of the role that is being assumed.

When you create a role, you create two policies: a **role trust policy** that specifies *who* can assume the role, and a **permissions policy** that specifies *what* can be done with the role.

To assume a role from a different account, your AWS account must be trusted by the role (defined in the role's trust policy). A user who wants to access a role in a different account must also have permissions delegated from the account administrator (a policy that allows the user to call `AssumeRole` for the ARN of the role in the other account).

To allow a user to assume a role in the **same account**: attach a policy to the user that allows `AssumeRole`, OR add the user as a principal directly in the role's trust policy (the trust policy acts as an IAM resource-based policy).

**Using MFA with AssumeRole**
(Optional) You can include MFA information when you call `AssumeRole`. The trust policy of the role being assumed includes a condition that tests for MFA authentication, e.g.:
`"Condition": {"Bool": {"aws:MultiFactorAuthPresent": true}}`
To use MFA, you pass values for the `SerialNumber` and `TokenCode` parameters.

## Request Parameters

**DurationSeconds**
The duration, in seconds, of the role session. The value can range from **900 seconds (15 minutes) up to the maximum session duration set for the role**. The maximum session duration setting can have a value from **1 hour to 12 hours**. If you specify a value higher than this setting (or the administrator setting, whichever is lower), the operation fails.
**Role chaining limits your AWS CLI or AWS API role session to a maximum of one hour.** You can specify a parameter value of up to 43200 seconds (12 hours), depending on the maximum session duration setting for your role. However, if you assume a role using role chaining and provide a `DurationSeconds` value greater than one hour, the operation fails.
By default, the value is set to `3600` seconds.
Type: Integer · Valid Range: Minimum value of **900**. Maximum value of **43200**. · Required: No

**ExternalId**
A unique identifier that might be required when you assume a role in another account. A cross-account role is usually set up to trust everyone in an account; the external ID ensures only someone with the ID can assume the role.
Type: String · Length: Min 2, Max 1224. · Pattern: `[\w+=,.@:\/-]*` · Required: No

**Policy**
An IAM policy in JSON format to use as an inline session policy. The resulting session's permissions are the intersection of the role's identity-based policy and the session policies.
Type: String · Length: Minimum length of 1. (plaintext ≤ 2,048 chars) · Required: No

**PolicyArns.member.N**
The ARNs of the IAM managed policies to use as managed session policies. The policies must exist in the same account as the role. **You can provide up to 10 managed policy ARNs.** However, the plaintext for both inline and managed session policies can't exceed 2,048 characters.
Type: Array of PolicyDescriptorType objects · Required: No

**ProvidedContexts.member.N**
A list of previously acquired trusted context assertions (JSON array), signed and encrypted by AWS STS.
Type: Array of ProvidedContext objects · Array Members: Min 1, Max 5 items. · Required: No

**RoleArn**
The Amazon Resource Name (ARN) of the role to assume.
Type: String · Length: Min 20, Max 2048. · **Required: Yes**

**RoleSessionName**
An identifier for the assumed role session. In cross-account scenarios, the role session name is visible to, and can be logged by, the account that owns the role (appears in CloudTrail). It's also used in the ARN of the assumed role principal.
Type: String · Length: Min 2, Max 64. · Pattern: `[\w+=,.@-]*` · **Required: Yes**

**SerialNumber**
The identification number of the MFA device associated with the user making the call. Specify if the trust policy of the role requires MFA. Value is a hardware serial number (e.g. `GAHT12345678`) or an ARN for a virtual device (e.g. `arn:aws:iam::123456789012:mfa/user`).
Type: String · Length: Min 9, Max 256. · Required: No

**SourceIdentity**
The source identity specified by the principal calling `AssumeRole`. Persists across chained role sessions. Cannot begin with `aws:`.
Type: String · Length: Min 2, Max 64. · Required: No

**Tags.member.N**
A list of session tags. **You can pass up to 50 session tags.** Key ≤ 128 characters, value ≤ 256 characters. Session tags override a role tag with the same key. Tag key–value pairs are not case sensitive, but case is preserved.
Type: Array of Tag objects · Array Members: Max 50 items. · Required: No

**TokenCode**
The value provided by the MFA device, if the role's trust policy requires MFA. If required and the value is missing or expired, the call returns an "access denied" error. **Fixed length of 6** numeric digits. Pattern: `[\d]*` · Required: No

**TransitiveTagKeys.member.N**
A list of keys for session tags to set as **transitive** (pass to subsequent sessions in a role chain).
Type: Array of strings · Array Members: Max 50 items. · Length: Min 1, Max 128. · Required: No

## Response Elements

**AssumedRoleUser** — The ARN and the assumed role ID. Includes the `RoleSessionName` you specified. Type: AssumedRoleUser object.

**Credentials** — The temporary security credentials, which include **an access key ID, a secret access key, and a security (or session) token**. The size of the security token is not fixed; make no assumptions about the maximum size. Type: Credentials object.

**PackedPolicySize** — A percentage value indicating the packed size of the session policies and session tags combined. The request fails if greater than 100 percent. Type: Integer · Valid Range: Min 0.

**SourceIdentity** — The source identity specified by the principal calling `AssumeRole`.

## Errors

**ExpiredToken** — The web identity token passed is expired or not valid. HTTP 400.
**MalformedPolicyDocument** — The policy document was malformed. HTTP 400.
**PackedPolicyTooLarge** — The total packed size of session policies and session tags combined was too large. HTTP 400.
**RegionDisabled** — AWS STS is not activated in the requested region for the account. The administrator must activate STS in that region via the IAM console. HTTP 403.

## Example — Sample Request

```
https://sts.amazonaws.com/
?Version=2011-06-15
&Action=AssumeRole
&RoleSessionName=testAR
&RoleArn=arn:aws:iam::123456789012:role/demo
&PolicyArns.member.1.arn=arn:aws:iam::123456789012:policy/demopolicy1
&PolicyArns.member.2.arn=arn:aws:iam::123456789012:policy/demopolicy2
&Policy=JSON-IAM-POLICY
&DurationSeconds=3600
&ExternalId=123ABC
&SourceIdentity=Alice
&AUTHPARAMS
```

## Example — Sample Response

```
<AssumeRoleResponse xmlns="https://sts.amazonaws.com/doc/2011-06-15/">
  <AssumeRoleResult>
  <SourceIdentity>Alice</SourceIdentity>
    <AssumedRoleUser>
      <Arn>arn:aws:sts::123456789012:assumed-role/demo/TestAR</Arn>
      <AssumedRoleId>ARO123EXAMPLE123:TestAR</AssumedRoleId>
    </AssumedRoleUser>
    <Credentials>
      <AccessKeyId>ASIAIOSFODNN7EXAMPLE</AccessKeyId>
      <SecretAccessKey>wJalrXUtnFEMI/K7MDENG/bPxRfiCYzEXAMPLEKEY</SecretAccessKey>
      <SessionToken>AQoDYXdzEPT//////////wEXAMPLEtc764bNrC9SAPBSM22wDOk4x4HIZ8j4FZTwdQW...==</SessionToken>
      <Expiration>2019-11-09T13:34:41Z</Expiration>
    </Credentials>
    <PackedPolicySize>6</PackedPolicySize>
  </AssumeRoleResult>
  <ResponseMetadata>
    <RequestId>c6104cbe-af31-11e0-8154-cbc7ccf896c7</RequestId>
  </ResponseMetadata>
</AssumeRoleResponse>
```
