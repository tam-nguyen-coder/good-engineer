# Rotate AWS KMS keys (automatic / on-demand / manual rotation)

> **Nguồn (AWS official):** https://docs.aws.amazon.com/kms/latest/developerguide/rotate-keys.html
> **Tuần:** 7 — KMS + Secrets + Encryption · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- **Automatic rotation chỉ cho customer managed key**, và **chỉ** với **symmetric encryption key** có key material do AWS KMS sinh (`AWS_KMS` origin). Rotation là **tuỳ chọn** (bật/tắt bất kỳ lúc nào).
- **Rotation period mặc định = 365 ngày**. Từ nay có thể đặt **custom rotation period** qua tham số `RotationPeriodInDays` (không đặt → mặc định 365).
- **AWS managed key**: KMS **luôn tự rotate mỗi năm (~365 ngày)**, bạn KHÔNG bật/tắt được. (Trước May 2022 là ~1.095 ngày / 3 năm.)
- **On-demand rotation**: rotate ngay lập tức bất kể automatic có bật hay không; hỗ trợ symmetric key `AWS_KMS` origin **và** `EXTERNAL` origin (imported). On-demand **không** làm đổi lịch automatic.
- **Manual rotation** (tạo key mới + đổi alias): dùng cho các loại **KHÔNG** hỗ trợ auto/on-demand → **asymmetric key**, **HMAC key**, key trong **custom key store**.
- **Điểm cực hay hỏi:** rotation chỉ đổi **current key material**; KMS **giữ lại toàn bộ key material cũ** → giải mã ciphertext cũ vẫn được (KMS tự chọn đúng version). **Không cần đổi code**, alias giữ nguyên, Key ID giữ nguyên.
- **Rotation KHÔNG re-encrypt dữ liệu cũ, KHÔNG rotate data key đã sinh, KHÔNG khắc phục data key bị lộ.**
- **Quota:** mỗi KMS key tính là **1 key** bất kể có bao nhiêu version key material.
- **Pricing:** KMS tính phí hằng tháng cho **lần rotate thứ 1 và thứ 2**; từ lần 3 trở đi **không tính thêm**.
- **Theo dõi rotation:** `GetKeyRotationStatus`, `ListKeyRotations`; KMS ghi event `KMS CMK Rotation` vào **EventBridge** + `RotateKey` vào **CloudTrail**.
- **Multi-region key:** bật/tắt auto rotation & on-demand **chỉ trên primary key**; key material mới được copy sang tất cả replica (không rời KMS ở dạng plaintext). Bất kỳ replica nào giải mã được ciphertext của nhau.

---

## 📄 Nội dung (trích từ tài liệu gốc)

# Rotate AWS KMS keys

To create new cryptographic material for your customer managed keys, you can create new KMS keys, and then change your applications or aliases to use the new KMS keys. Or, you can rotate the key material associated with an existing KMS key by enabling automatic key rotation or performing on-demand rotation.

By default, when you enable *automatic key rotation* for a KMS key, AWS KMS generates new cryptographic material for the KMS key every year. You can also specify a custom rotation-period to define the number of days after you enable automatic key rotation that AWS KMS will rotate your key material, and the number of days between each automatic rotation thereafter. If you need to immediately initiate key material rotation, you can perform *on-demand rotation*, regardless of whether or not automatic key rotation is enabled. On-demand rotations do not change existing automatic rotation schedules.

You can track the rotation of key material for your KMS keys in Amazon CloudWatch, AWS CloudTrail, and the AWS KMS console. You can also use `GetKeyRotationStatus` operation to verify whether automatic rotation is enabled for a KMS key and identify any in progress on-demand rotations. You can use `ListKeyRotations` operation to view the details of completed rotations.

Key rotation changes only the *current key material*, which is the cryptographic secret that is used in encryption operations. When you use the rotated KMS key to decrypt ciphertext, AWS KMS uses the key material that was used to encrypt it. You cannot select a particular key material for decrypt operations, AWS KMS automatically chooses the correct key material. Because AWS KMS transparently decrypts with the appropriate key material, you can safely use a rotated KMS key in applications and AWS services without code changes.

The KMS key is the same logical resource, regardless of whether or how many times its key material changes. The properties of the KMS key do not change.

You might decide to create a new KMS key and use it in place of the original KMS key. This has the same effect as rotating the key material in an existing KMS key, so it's often thought of as manually rotating the key. Manual rotation is a good choice when you want to rotate KMS keys that are not eligible for automatic or on-demand key rotation, including asymmetric KMS keys, HMAC KMS keys and KMS keys in custom key stores.

**Note:** Key rotation has no effect on the data that the KMS key protects. It does not rotate the data keys that the KMS key generated or re-encrypt any data protected by the KMS key. Key rotation will not mitigate the effect of a compromised data key.

**Key rotation and pricing:** AWS KMS charges a monthly fee for first and second rotation of key material maintained for your KMS key. This price increase is capped at the second rotation, and any subsequent rotations will not be billed.

**Key rotation and quotas:** Each KMS key counts as one key when calculating key resource quotas, regardless of the number of rotated key material versions.

## Why rotate KMS keys?

Cryptographic best practices discourage extensive reuse of keys that encrypt data directly, such as the data keys that AWS KMS generates. When 256-bit data keys encrypt millions of messages they can become exhausted and begin to produce ciphertext with subtle patterns that clever actors can exploit to discover the bits in the key. It's best to use data keys once, or just a few times, to mitigate this key exhaustion.

However, KMS keys are most often used as *wrapping keys*, also known as *key-encryption keys*. Instead of encrypting data, wrapping keys encrypt the data keys that encrypt your data. As such, they are used far less often than data keys, and are almost never reused enough to risk key exhaustion.

Despite this very low exhaustion risk, you might be required to rotate your KMS keys due to business or contract rules or government regulations. When you are compelled to rotate KMS keys, we recommend that you use automatic key rotation where it is supported, use on-demand rotation if automatic rotation is not supported, and manual key rotation when neither automatic nor on-demand key rotation is supported.

## How key rotation works

AWS KMS key rotation is designed to be transparent and easy to use. AWS KMS supports optional automatic and on-demand key rotation only for customer managed keys.

**Automatic key rotation** — AWS KMS rotates the KMS key automatically on the next rotation date defined by your rotation period. You don't need to remember or schedule the update.
- Automatic key rotation is supported only on symmetric encryption KMS keys with key material that AWS KMS generates (`AWS_KMS` origin).
- Automatic rotation is optional for customer managed KMS keys. AWS KMS always rotates the key material for AWS managed KMS keys every year. Rotation of AWS owned KMS keys is managed by the AWS service that owns the key.

**On-demand rotation** — Immediately initiate rotation of the key material associated with your KMS key, regardless of whether or not automatic key rotation is enabled.
- On-demand key rotation is supported on symmetric encryption KMS keys with key material that AWS KMS generates (`AWS_KMS` origin) and symmetric encryption KMS keys with imported key material (`EXTERNAL` origin).

**Manual rotation** — Neither automatic nor on-demand key rotation is supported for the following types of KMS keys, but you can rotate these KMS keys manually:
- Asymmetric KMS keys
- HMAC KMS keys
- KMS keys in custom key stores

**Managing key material** — AWS KMS retains all key material for a KMS key with `AWS_KMS` origin, even if key rotation is disabled. AWS KMS deletes key material only when you delete the KMS key. You manage the key materials for symmetric encryption keys with `EXTERNAL` origin.

**Using key material** — When you use a rotated KMS key to encrypt data, AWS KMS uses the current key material. When you use the rotated KMS key to decrypt ciphertext, AWS KMS uses the same version of the key material that was used to encrypt it. You cannot select a particular version of the key material for decrypt operations, AWS KMS automatically chooses the correct version.

**Rotation period** — Rotation period defines the number of days after you enable automatic key rotation that AWS KMS will rotate your key material, and the number of days between each automatic key rotation thereafter. If you do not specify a value for `RotationPeriodInDays` when you enable automatic key rotation, the default value is **365 days**. You can use the `kms:RotationPeriodInDays` condition key to further constrain the values that principals can specify.

**Rotation date** — Reflects the date when the current key material for a KMS key was updated either as a result of automatic (scheduled) rotation or an on-demand key rotation. AWS KMS automatically rotates the KMS key on the rotation date defined by your rotation period. The default rotation period is 365 days.

### Customer managed keys
Because automatic key rotation is optional on customer managed keys and can be enabled and disabled at any time, the rotation date depends on the date that rotation was most recently enabled.

For example, if you create a customer managed key on January 1, 2022, and enable automatic key rotation with the default rotation period of 365 days on March 15, 2022, AWS KMS rotates the key material on March 15, 2023, March 15, 2024, and every 365 days thereafter.

- **Disable key rotation** — If you disable automatic key rotation at any point, the KMS key continues to use the version of the key material it was using when rotation was disabled. If you enable automatic key rotation again, AWS KMS rotates the key material based on the new rotation-enable date.
- **Disabled KMS keys** — While a KMS key is disabled, AWS KMS does not rotate it. When the KMS key is re-enabled, if the key material is past its last scheduled rotation date, AWS KMS rotates it immediately.
- **KMS keys pending deletion** — While a KMS key is pending deletion, AWS KMS does not rotate it. The key rotation status is set to `false`. If deletion is canceled, the previous key rotation status is restored.

### AWS managed keys
AWS KMS automatically rotates AWS managed keys every year (approximately 365 days). You cannot enable or disable key rotation for AWS managed keys. The key material for an AWS managed key is first rotated one year after its creation date, and every year (approximately 365 days from the last rotation) thereafter. In May 2022, AWS KMS changed the rotation schedule for AWS managed keys from every three years (approximately 1,095 days) to every year (approximately 365 days).

### AWS owned keys
You cannot enable or disable key rotation for AWS owned keys. The key rotation strategy for an AWS owned key is determined by the AWS service that creates and manages the key.

### Rotating multi-Region keys
The rotation behavior differs depending on whether the key material is generated by AWS KMS (`AWS_KMS` origin) or imported (`EXTERNAL` origin).

**Multi-Region keys with `AWS_KMS` origin** — You can enable and disable automatic rotation and perform on-demand rotation. Key rotation is a shared property of multi-Region keys. You enable and disable automatic key rotation only on the primary key. You initiate on-demand rotation only on the primary key.
- When AWS KMS synchronizes the multi-Region keys, it copies the key rotation property setting from the primary key to all of its related replica keys.
- When AWS KMS rotates the key material, it creates new key material for the primary key and then copies the new key material across Region boundaries to all related replica keys. The key material never leaves AWS KMS unencrypted.
- AWS KMS does not encrypt any data with the new key material until that key material is available in the primary key and every one of its replica keys.
- Any multi-Region key can decrypt any ciphertext encrypted by a related multi-Region key, even if the ciphertext was encrypted before the key was created.

**Multi-Region keys with `EXTERNAL` origin** — You can perform on-demand rotation. You initiate on-demand rotation only on the primary key after importing the new key material into the primary key and each replica key. You must import the same key material into each replica key individually.

**Monitoring key rotation** — When AWS KMS rotates the key material for an AWS managed key or customer managed key, it writes a `KMS CMK Rotation` event to Amazon EventBridge and a `RotateKey` event to your AWS CloudTrail log. You can use `ListKeyRotations` operation to view the details of completed rotations.

**Eventual consistency** — Key rotation is subject to the same eventual consistency effects as other AWS KMS management operations. However, rotating key material does not cause any interruption or delay in cryptographic operations. The current key material is used in cryptographic operations until the new key material is available throughout AWS KMS.
