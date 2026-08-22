# AWS KMS keys — Concepts (loại key, key hierarchy, key identifiers)

> **Nguồn (AWS official):** https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html
> **Tuần:** 7 — KMS + Secrets + Encryption · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- **3 loại KMS key** — bẫy kinh điển:
  - **Customer managed key**: bạn tạo & toàn quyền (key policy, IAM, grant, enable/disable, rotation, alias, xoá). **Có phí hằng tháng** + phí sử dụng. Rotation là **tuỳ chọn**. `KeyManager = CUSTOMER`.
  - **AWS managed key** (`aws/<service>`, vd `aws/s3`, `aws/ebs`, `aws/redshift`): AWS tạo giúp bạn, **KHÔNG sửa được** policy/rotation, không dùng trực tiếp trong crypto op. **Không phí hằng tháng**, chỉ trả phí dùng (có service trả hộ). **Bắt buộc rotate mỗi năm (~365 ngày)**. `KeyManager = AWS`. Là loại **legacy** — từ 2021 service mới không tạo nữa.
  - **AWS owned key**: nằm trong account của AWS, dùng chung nhiều account. **Không xem/không audit/không sửa/không xoá được**, **HOÀN TOÀN MIỄN PHÍ**. Rotation do service quyết định.
- Khẩu quyết: **cần control/audit → customer managed**; **cần tiện, khỏi quản → AWS owned**; **AWS managed** ở giữa (xem được metadata + audit CloudTrail nhưng không sửa).
- Alias có prefix `aws/` bị **reserved** cho AWS managed key — bạn không tạo được alias kiểu này.
- **Key hierarchy**: HSM backing key (HBK) là "version" của KMS key, **không bao giờ rời HSM ở dạng plaintext**. Khi rotate → tạo HBK mới, **giữ lại HBK cũ** để giải mã dữ liệu cũ. Cùng 1 logical key (cùng Key ID) dù key material đổi bao nhiêu lần.
- **Data key (CDK)** do HSM sinh, trả về dạng plaintext + ciphertext, dùng cho **envelope encryption** — KMS không lưu ciphertext/plaintext trả về, chỉ chuyển qua TLS.
- **4 dạng key identifier**: Key ARN (đầy đủ nhất), Key ID, Alias ARN, Alias name (`alias/...`). Multi-region key có prefix `mrk-`.
- **Resource control policies (RCP)** của Organization **không áp dụng** cho AWS managed key.

---

## 📄 Nội dung (trích từ tài liệu gốc)

# AWS KMS keys

The KMS keys that you create and manage for use in your own cryptographic applications are of a type known as *customer managed keys*. Customer managed keys can also be used in conjunction with AWS services that use KMS keys to encrypt the data the service stores on your behalf. Customer managed keys are recommended for customers who want full control over the lifecycle and usage of their keys. There is a monthly cost to have a customer managed key in your account. In addition, requests use and/or manage the key incur a usage cost.

There are cases where a customer might want an AWS service to encrypt their data, but they don't want the overhead of managing keys and don't want to pay for a key. An *AWS managed key* is a KMS key that exists in your account, but can only be used under certain circumstances. Specifically, it can only be used in the context of the AWS service you're operating in and it can only be used by principals within the account that the key exists. You cannot manage anything about the lifecycle or permissions of these keys. As you use encryption features in AWS services, you may see AWS managed keys; they use an alias of the form "aws/<service code>". For example, an `aws/ebs` key can only be used to encrypt EBS volumes and only for volumes used by IAM principals in the same account as the key. You cannot share resources encrypted under an AWS managed key with other accounts. While an AWS managed key is free to exist in your account, you are charged for any use of this key type by the AWS service that is assigned to the key.

AWS managed keys are a legacy key type that is no longer being created for new AWS services as of 2021. Instead, new (and legacy) AWS services are using what's known as an *AWS owned key* to encrypt customer data by default. An AWS owned key is a KMS key that is in an account managed by the AWS service, so the service operators have the ability to manage its lifecycle and usage permissions. By using AWS owned keys, AWS services can transparently encrypt your data and allow for easy cross-account or cross-region sharing of data without you needing to worry about key permissions. Because these keys are owned and managed by AWS, you are not charged for their existence or their usage, you cannot change their policies, you cannot audit activities on these keys, and you cannot delete them. Use customer managed keys when control is important, but use AWS owned keys when convenience is most important.

|  | Customer managed keys | AWS managed keys | AWS owned keys |
| --- | --- | --- | --- |
| **Key policy** | Exclusively controlled by the customer | Controlled by service; viewable by customer | Exclusively controlled and only viewable by the AWS service that encrypts your data |
| **Logging** | CloudTrail customer trail or event data store | CloudTrail customer trail or event data store | Not viewable by the customer |
| **Lifecycle management** | Customer manages rotation, deletion and Regional location | AWS KMS manages rotation (annual), deletion, and Regional location | AWS service manages rotation, deletion, and Regional location |
| **Pricing** | Monthly fee for existence of keys (pro-rated hourly). Also charged for key usage | No monthly fee; but the caller is charged for API usage on these keys | No charges to customer |

The KMS keys that you create are customer managed keys. AWS services that use KMS keys to encrypt your service resources often create keys for you. KMS keys that AWS services create in your AWS account are AWS managed keys. KMS keys that AWS services create in a service account are AWS owned keys.

| Type of KMS key | Can view KMS key metadata | Can manage KMS key | Created in my AWS account | Automatic rotation | Pricing |
| --- | --- | --- | --- | --- | --- |
| Customer managed key | Yes | Yes | Yes | Optional. | Monthly fee (pro-rated hourly) + Per-use fee |
| AWS managed key | Yes | No | Yes | Required. Every year (approximately 365 days). | No monthly fee + Per-use fee (some AWS services pay this fee for you) |
| AWS owned key | No | No | No | The AWS service manages the rotation strategy | No fees |

## Customer managed keys

The KMS keys that you create are *customer managed keys*. Customer managed keys are KMS keys in your AWS account that you create, own, and manage. You have full control over these KMS keys, including establishing and maintaining their key policies, IAM policies, and grants, enabling and disabling them, rotating their cryptographic material, adding tags, creating aliases that refer to the KMS keys, and scheduling the KMS keys for deletion.

To definitively identify a customer managed key, use the `DescribeKey` operation. For customer managed keys, the value of the `KeyManager` field of the `DescribeKey` response is `CUSTOMER`.

Customer managed keys incur a monthly fee and a fee for use in excess of the free tier. They are counted against the AWS KMS quotas for your account.

## AWS managed keys

*AWS managed keys* are KMS keys in your account that are created, managed, and used on your behalf by an AWS service integrated with AWS KMS.

In general, unless you are required to control the encryption key that protects your resources, an AWS managed key is a good choice. You don't have to create or maintain the key or its key policy, and there's never a monthly fee for an AWS managed key.

You have permission to view the AWS managed keys in your account, view their key policies, and audit their use in AWS CloudTrail logs. However, you cannot change any properties of AWS managed keys, rotate them, change their key policies, or schedule them for deletion. And, you cannot use AWS managed keys in cryptographic operations directly; the service that creates them uses them on your behalf.

Resource control policies in your organization do not apply to AWS managed keys.

You can identify AWS managed keys by their aliases, which have the format `aws/{service-name}`, such as `aws/redshift`. For AWS managed keys, the value of the `KeyManager` field of the `DescribeKey` response is `AWS`.

**All AWS managed keys are automatically rotated every year. You cannot change this rotation schedule.**

**Note:** In May 2022, AWS KMS changed the rotation schedule for AWS managed keys from every three years (approximately 1,095 days) to every year (approximately 365 days).

There is no monthly fee for AWS managed keys. They can be subject to fees for use in excess of the free tier, but some AWS services cover these costs for you.

AWS managed keys do not count against resource quotas on the number of KMS keys in each Region of your account. But when used on behalf of a principal in your account, the KMS keys count against request quotas.

## AWS owned keys

*AWS owned keys* are a collection of KMS keys that an AWS service owns and manages for use in multiple AWS accounts. Although AWS owned keys are not in your AWS account, an AWS service can use an AWS owned key to protect the resources in your account.

In general, unless you are required to audit or control the encryption key that protects your resources, an AWS owned key is a good choice. AWS owned keys are completely free of charge (no monthly fees or usage fees), they do not count against the AWS KMS quotas for your account, and they're easy to use. You don't need to create or maintain the key or its key policy.

The rotation of AWS owned keys varies across services.

## AWS KMS key hierarchy

Your key hierarchy starts with a top-level logical key, an AWS KMS key. A KMS key represents a container for top-level key material and is uniquely defined within the AWS service namespace with an Amazon Resource Name (ARN). The ARN includes a uniquely generated key identifier, a *key ID*. Upon reception, AWS KMS requests the creation of an initial HSM backing key (HBK) to be placed into the KMS key container. The HBK is generated on an HSM in the domain and is designed never to be exported from the HSM in plaintext. Instead, the HBK is exported encrypted under HSM-managed domain keys. These exported HBKs are referred to as exported key tokens (EKTs).

Within the hierarchy of a specific KMS key, the HBK can be thought of as a version of the KMS key. When you want to rotate the KMS key through AWS KMS, a new HBK is created and associated with the KMS key as the active HBK for the KMS key. The older HBKs are preserved and can be used to decrypt and verify previously protected data. But only the active cryptographic key can be used to protect new information.

You can make requests through AWS KMS to use your KMS keys to directly protect information or request additional HSM-generated keys that are protected under your KMS key. These keys are called customer data keys, or CDKs. CDKs can be returned encrypted as ciphertext (CT), in plaintext, or both. All objects encrypted under a KMS key (either customer-supplied data or HSM-generated keys) can be decrypted only on an HSM via a call through AWS KMS.

The returned ciphertext, or the decrypted payload, is never stored within AWS KMS. The information is returned to you over your TLS connection to AWS KMS. This also applies to calls made by AWS services on your behalf.

| Key | Description | Lifecycle |
| --- | --- | --- |
| **Domain key** | A 256-bit AES-GCM key only in memory of an HSM used to wrap versions of the KMS keys, the HSM backing keys. | Rotated daily¹ |
| **HSM backing key** | A 256-bit symmetric key or RSA or elliptic curve private key, used to protect customer data and keys and stored encrypted under domain keys. One or more HSM backing keys comprise the KMS key, represented by the keyId. | Rotated yearly² (optional config.) |
| **Derived encryption key** | A 256-bit AES-GCM key only in memory of an HSM used to encrypt customer data and keys. Derived from an HBK for each encryption. | Used once per encrypt and regenerated on decrypt |
| **Customer data key** | User-defined symmetric or asymmetric key exported from HSM in plaintext and ciphertext. Encrypted under an HSM backing key and returned to authorized users over TLS channel. | Rotation and use controlled by application |

¹ AWS KMS might from time to time relax domain key rotation to at most weekly to account for domain administration and configuration tasks.
² Default AWS managed keys created and managed by AWS KMS on your behalf are automatically rotated annually.

## Key identifiers (KeyId)

Key identifiers act like names for your KMS keys. You use them to indicate which KMS keys you want to use in AWS KMS API operations, key policies, IAM policies, and grants. The key identifier values are completely unrelated to the key material associated with the KMS key.

AWS KMS supports the following key identifiers:

**Key ARN** — The Amazon Resource Name (ARN) of a KMS key. A unique, fully qualified identifier that includes the AWS account, Region, and the key ID.

```
arn:<partition>:kms:<region>:<account-id>:key/<key-id>
```

Example (single-Region):
```
arn:aws:kms:us-west-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab
```

The key-id element of multi-Region keys begins with the `mrk-` prefix:
```
arn:aws:kms:us-west-2:111122223333:key/mrk-1234abcd12ab34cd56ef1234567890ab
```

**Key ID** — Uniquely identifies a KMS key within an account and Region.
```
1234abcd-12ab-34cd-56ef-1234567890ab
```
Multi-Region key IDs begin with `mrk-`:
```
mrk-1234abcd12ab34cd56ef1234567890ab
```

**Alias ARN** — The ARN of an AWS KMS alias. At any given time, an alias ARN identifies one particular KMS key. Because you can change the KMS key associated with the alias, the alias ARN can identify different KMS keys at different times.
```
arn:<partition>:kms:<region>:<account-id>:alias/<alias-name>
```
```
arn:aws:kms:us-west-2:111122223333:alias/ExampleAlias
```

**Alias name** — A string of up to 256 characters. In the AWS KMS API, alias names always begin with `alias/`.
```
alias/<alias-name>
```
```
alias/ExampleAlias
```
The `aws/` prefix for an alias name is reserved for AWS managed keys. You cannot create an alias with this prefix. For example, the alias name of the AWS managed key for Amazon S3 is `alias/aws/s3`.

**Note:** When using the AWS KMS API, be careful about the key identifier that you use. Different APIs require different key identifiers. In general, use the most complete and practical key identifier for your task.
