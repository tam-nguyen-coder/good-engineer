# 📂 Tài nguyên Tuần 7 — KMS + Secrets + Encryption

> Crawl từ tài liệu AWS chính thức. Về [file học Tuần 7](../../week-07.md) · [Kế hoạch tổng](../../../DVA-C02-STUDY-PLAN.md)

| # | Tài nguyên (file local) | Chủ đề | Nguồn AWS |
|---|---|---|---|
| 1 | [kms-concepts.md](kms-concepts.md) | `KMS` keys: 3 loại key (customer managed / AWS managed `aws/<service>` / AWS owned), pricing, key hierarchy (HBK), key identifiers, alias | https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html |
| 2 | [kms-key-rotation.md](kms-key-rotation.md) | Rotation: automatic (365 ngày, chỉ symmetric CMK) vs on-demand vs manual (asymmetric/HMAC); giữ key material cũ để giải mã dữ liệu cũ; AWS managed key auto-rotate hằng năm | https://docs.aws.amazon.com/kms/latest/developerguide/rotate-keys.html |
| 3 | [secrets-manager-intro.md](secrets-manager-intro.md) | `Secrets Manager`: bỏ hard-coded credential, rotate tự động, mã hoá KMS (`aws/secretsmanager` free), tính phí; chọn IAM/KMS/ACM cho loại secret khác | https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html |
| 4 | [secrets-manager-rotation.md](secrets-manager-rotation.md) | Rotation: managed vs managed external vs Lambda; staging labels `AWSCURRENT`/`AWSPENDING`/`AWSPREVIOUS`; 4 bước rotation function | https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html |
| 5 | [ssm-parameter-store.md](ssm-parameter-store.md) | `Parameter Store`: String/StringList/SecureString (KMS), `--with-decryption`, hierarchy theo path, standard free, tích hợp Lambda/ECS/CFN | https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html |
| 6 | [ssm-parameter-store-tiers.md](ssm-parameter-store-tiers.md) | Tiers: Standard (10k param, 4 KB, free) vs Advanced (100k, 8 KB, policy, cross-account, tính phí); nâng cấp một chiều | https://docs.aws.amazon.com/systems-manager/latest/userguide/parameter-store-advanced-parameters.html |
| 7 | [acm-overview.md](acm-overview.md) | `ACM`: cấp + tự gia hạn cert TLS (free), regional resource, cert cho CloudFront BẮT BUỘC ở us-east-1, wildcard, import cert bên thứ 3 | https://docs.aws.amazon.com/acm/latest/userguide/acm-overview.html |

## Gợi ý thứ tự đọc
1. **`KMS` nền tảng (1 → 2):** nắm 3 loại key + pricing (file 1) trước, rồi rotation (file 2) — đây là cụm số liệu hay hỏi nhất (4 KB envelope, 365 ngày, giữ backing key cũ). Ghép với luồng envelope encryption trong file tuần.
2. **`Secrets Manager` (3 → 4):** đọc intro để biết "bỏ hard-code + rotate" rồi tới rotation & staging labels. Keyword "tự động xoay credential DB" → chốt `Secrets Manager`.
3. **`Parameter Store` (5 → 6):** so với Secrets Manager — nhớ `--with-decryption`, standard free, và bảng tier Standard vs Advanced (một chiều, 4 KB→8 KB).
4. **`ACM` (7):** đọc cuối — keyword "cert TLS tự gia hạn" → `ACM`; nhớ bẫy CloudFront = `us-east-1`.

## 🔑 Số liệu chốt nhanh (cross-check với file tuần)
- `KMS` encrypt trực tiếp: **≤ 4 KB** → lớn hơn dùng **envelope encryption** (`GenerateDataKey`).
- Automatic rotation CMK: mặc định **365 ngày**, chỉ **symmetric** `AWS_KMS` origin; giữ **key material cũ** để giải mã dữ liệu cũ.
- AWS managed key `aws/<service>`: **bắt buộc rotate ~365 ngày**, không sửa được.
- `Parameter Store`: Standard **10.000 param / 4 KB / free**; Advanced **100.000 / 8 KB / có policy / tính phí**; nâng cấp **một chiều**.
- `Secrets Manager` staging labels: `AWSCURRENT` / `AWSPENDING` / `AWSPREVIOUS`.
- `ACM` cert cho **CloudFront** phải ở **`us-east-1`**; cert là **regional**, không copy giữa region.
