# Question #44 - Topic 1

A company has an Amazon S3 bucket that contains critical data. The company must protect the data from accidental deletion. Which combination of steps should a solutions architect take to meet these requirements? (Choose two.)

## Options

**A.** Enable versioning on the S3 bucket.

**B.** Enable MFA Delete on the S3 bucket.

**C.** Create a bucket policy on the S3 bucket.

**D.** Enable default encryption on the S3 bucket.

**E.** Create a lifecycle policy for the objects in the S3 bucket.



---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty sở hữu một `Amazon S3 bucket` chứa dữ liệu quan trọng (critical data).
- **Existing Resources:** `S3 bucket` đã tồn tại.
- **Current Issue/Goal:** Phải bảo vệ dữ liệu khỏi bị xóa vô ý (`accidental deletion`). Cần chọn **hai** bước phù hợp.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| `accidental deletion` | Xóa vô ý — yêu cầu ngăn chặn việc dữ liệu bị xóa vĩnh viễn do nhầm lẫn |
| `versioning` | Lưu trữ nhiều phiên bản của object; khi xóa sẽ tạo `delete marker` thay vì xóa object vật lý |
| `MFA Delete` | Yêu cầu xác thực đa yếu tố để xóa vĩnh viễn một phiên bản object hoặc để `suspend versioning` |
| `bucket policy` | Kiểm soát quyền truy cập cấp bucket (IAM policy dạng JSON) |
| `default encryption` | Mã hóa dữ liệu tĩnh (`encryption at rest`) |
| `lifecycle policy` | Tự động chuyển storage class hoặc xóa object theo thời gian |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Multiple choice — chọn **2 đáp án**
- **Constraints:** Tập trung vào việc **ngăn xóa vô ý**, không yêu cầu bảo mật dữ liệu (confidentiality) hay tối ưu chi phí lưu trữ

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A và B**

**Giải thích:**
- **`Enable versioning` (A):** Khi bật versioning trên `S3 bucket`, việc xóa một object chỉ tạo ra `delete marker`. Object gốc vẫn còn tồn tại ở dạng previous version và có thể được khôi phục bằng cách xóa `delete marker`. Đây là tuyến phòng thủ đầu tiên chống xóa vĩnh viễn do vô ý.
- **`Enable MFA Delete` (B):** Yêu cầu người dùng cung cấp `MFA` (Multi-Factor Authentication) khi thực hiện các thao tác xóa vĩnh viễn một version cụ thể hoặc khi `suspend versioning`. Kết hợp với versioning, đây là cơ chế mạnh mẽ nhất để ngăn chặn xóa vô ý hoặc xóa ác ý trên `S3`.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án C — `Create a bucket policy on the S3 bucket`:** Bucket policy chỉ kiểm soát quyền truy cập (ví dụ: chặn `s3:DeleteObject` với một số principal). Tuy nhiên, nếu root account hoặc admin có quyền hợp lệ thao tác nhầm, policy không ngăn được việc xóa vĩnh viễn dữ liệu. Nó giải quyết vấn đề **authorization**, không phải **accidental deletion recovery**.

**❌ Đáp án D — `Enable default encryption`:** Default encryption chỉ đảm bảo `encryption at rest` (mã hóa dữ liệu khi lưu trữ), bảo vệ tính bảo mật (`confidentiality`) chứ không bảo vệ dữ liệu khỏi bị xóa.

**❌ Đáp án E — `Create a lifecycle policy`:** Lifecycle policy dùng để chuyển đổi object sang storage class rẻ hơn (ví dụ: `S3 Glacier`) hoặc tự động xóa object sau một khoảng thời gian (`expiration`). Thậm chí nó còn có thể gây ra việc xóa dữ liệu, chứ không ngăn chặn xóa vô ý.

## 6. MẸO GHI NHỚ
🧠 *"Chống xóa vô ý trên S3 = Versioning + MFA Delete."*
- `Versioning` giữ lại dữ liệu cũ dưới dạng previous versions khi bị xóa (tạo `delete marker`).
- `MFA Delete` bắt buộc xác thực MFA để xóa vĩnh viễn một version hoặc suspend versioning.
- `Encryption` (D) = bảo mật; `Bucket policy` (C) = kiểm soát truy cập; `Lifecycle` (E) = quản lý vòng đời & chi phí.
