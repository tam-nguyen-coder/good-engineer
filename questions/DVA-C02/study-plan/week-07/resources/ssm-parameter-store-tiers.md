# Parameter Store — Managing tiers (Standard vs Advanced)

> **Nguồn (AWS official):** https://docs.aws.amazon.com/systems-manager/latest/userguide/parameter-store-advanced-parameters.html
> **Tuần:** 7 — KMS + Secrets + Encryption · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- **Số PHẢI NHỚ (bảng so sánh tier):**
  - **Standard** (mặc định): tối đa **10.000 param/account/region**, value tối đa **4 KB**, **không** parameter policy, **không** share cross-account, **MIỄN PHÍ**.
  - **Advanced**: tối đa **100.000 param**, value tối đa **8 KB**, **có** parameter policy, **share cross-account được**, **TÍNH PHÍ**.
- **Chiều nâng cấp một chiều (bẫy đề):** nâng standard → advanced được, nhưng **KHÔNG hạ advanced → standard được**, vì:
  1. Sẽ **cắt** value từ 8 KB xuống 4 KB → mất dữ liệu.
  2. Xoá các **policy** đang gắn.
  3. Đổi cơ chế encryption.
  → Muốn "hạ tier" thì phải **xoá và tạo lại** dưới dạng standard param.
- **Khi nào dùng advanced:** cần giới hạn cao hơn (>10k param), value lớn hơn 4 KB, hoặc cần **parameter policies** (vd expiration, notification khi không rotate).
- SecureString mã hoá qua KMS (cả 2 tier); chi tiết xem "How Parameter Store uses AWS KMS".

---

## 📄 Nội dung (trích từ tài liệu gốc)

# Managing tiers

Parameter Store includes *standard parameters* and *advanced parameters*. You individually configure parameters to use either the standard-parameter tier (the default tier) or the advanced-parameter tier.

You can change a standard parameter to an advanced parameter at any time. You **can't** change an advanced parameter to a standard parameter for the following reasons:
- Reverting would cause the system to truncate the size of the parameter from 8 KB to 4 KB, resulting in data loss.
- Reverting would remove policies attached to the parameter.
- Reverting would change the parameter encryption.

**Note:** If you no longer need an advanced parameter, or if you no longer want to incur charges for an advanced parameter, delete it and recreate it as a new standard parameter.

## Standard and advanced parameters

The following table describes the differences between parameter tiers.

| Feature | Standard | Advanced |
| --- | --- | --- |
| Maximum parameters (per AWS account and AWS Region) | 10,000 | 100,000 |
| Maximum value size | 4 KB | 8 KB |
| Parameter policies | Not supported | Supported |
| Share parameters across AWS accounts | Not supported | Supported |
| Cost | No additional charge | Charges apply |

**Topics**
- Standard and advanced parameters
- Specifying a default parameter tier
- Changing a standard parameter to an advanced parameter
