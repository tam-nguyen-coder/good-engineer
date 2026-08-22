# Rotate AWS Secrets Manager secrets

> **Nguồn (AWS official):** https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html
> **Tuần:** 7 — KMS + Secrets + Encryption · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- **Rotation = cập nhật secret định kỳ**: đổi credential ở **CẢ** secret **VÀ** database/service tương ứng — đây là điểm khác biệt lớn nhất so với `Parameter Store` (không có rotation).
- **3 kiểu rotation:**
  1. **Managed rotation** — dịch vụ (managed secret) tự cấu hình & rotate, **KHÔNG dùng Lambda**.
  2. **Managed external secrets rotation** — với secret của đối tác Secrets Manager, cập nhật trên hệ thống đối tác, **không cần Lambda**.
  3. **Rotation by Lambda function** — với các loại secret khác: Secrets Manager dùng **Lambda function** để cập nhật secret và database/service. Đây là kiểu hay gặp nhất trong đề (vd rotate RDS credential).
- **Staging labels (PHẢI nhớ, hay hỏi):** trong quá trình rotate, secret có các version gắn nhãn:
  - `AWSCURRENT` — version đang được dùng (production).
  - `AWSPENDING` — version mới đang trong quá trình rotate (chưa xác nhận).
  - `AWSPREVIOUS` — version cũ trước đó (dùng để rollback).
- **Phản xạ đề:** "tự động xoay vòng credential DB" → **`Secrets Manager` + Lambda rotation** (tích hợp sẵn `RDS`/`Redshift`/`DocumentDB`). Nếu đề chọn `Parameter Store` cho rotation → SAI.
- Bật Lambda rotation → **tính thêm phí Lambda** (managed rotation thì không).

---

## 📄 Nội dung (trích từ tài liệu gốc)

# Rotate AWS Secrets Manager secrets

*Rotation* is the process of periodically updating a secret. When you rotate a secret, you update the credentials in both the secret and the database or service. In Secrets Manager, you can set up automatic rotation for your secrets. There are two forms of rotation:

- **Managed rotation** – For most managed secrets, you use managed rotation, where the service configures and manages rotation for you. Managed rotation doesn't use a Lambda function.
- **Rotate Secrets Manager managed external secrets** – For secrets held by Secrets Manager partners, you use managed external secrets rotation to update the secret on the partner's system. This doesn't require a Lambda function.
- **Rotation by Lambda function** – For other types of secrets, Secrets Manager rotation uses a Lambda function to update the secret and the database or service.

---

### 📝 Ghi chú bổ sung cho DVA-C02 (staging labels — từ tài liệu Secrets Manager)

Khi Secrets Manager rotate một secret, nó tạo version mới và di chuyển các **staging label** giữa các version:

| Staging label | Ý nghĩa |
| --- | --- |
| `AWSCURRENT` | Version hiện hành đang được ứng dụng sử dụng. |
| `AWSPENDING` | Version mới được tạo trong bước rotation, chờ được kiểm thử/kích hoạt trước khi trở thành `AWSCURRENT`. |
| `AWSPREVIOUS` | Version ngay trước `AWSCURRENT` — giữ lại để có thể rollback. |

Quy trình rotation bằng Lambda gồm 4 bước chuẩn (rotation function steps): **createSecret** → **setSecret** → **testSecret** → **finishSecret** (bước cuối đổi nhãn `AWSPENDING` thành `AWSCURRENT`).
