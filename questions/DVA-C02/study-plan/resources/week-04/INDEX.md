# 📂 Tài nguyên Tuần 4 — API Gateway + S3

> Crawl từ tài liệu AWS chính thức. Về [file học Tuần 4](../../week-04.md) · [Kế hoạch tổng](../../../DVA-C02-STUDY-PLAN.md)

| # | Tài nguyên (file local) | Chủ đề | Nguồn AWS |
|---|---|---|---|
| 1 | [apigw-rest-vs-http.md](apigw-rest-vs-http.md) | `REST API` vs `HTTP API` — bảng so sánh tính năng, chọn loại nào | https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-vs-rest.html |
| 2 | [apigw-stage-variables.md](apigw-stage-variables.md) | Stage variables — biến môi trường theo stage, trỏ backend/`Lambda alias` | https://docs.aws.amazon.com/apigateway/latest/developerguide/stage-variables.html |
| 3 | [apigw-lambda-authorizer.md](apigw-lambda-authorizer.md) | `Lambda authorizer` — `TOKEN` vs `REQUEST`, workflow, caching, code mẫu | https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-use-lambda-authorizer.html |
| 4 | [apigw-cors.md](apigw-cors.md) | CORS — simple/non-simple, preflight `OPTIONS`, proxy vs non-proxy | https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-cors.html |
| 5 | [s3-presigned-url.md](s3-presigned-url.md) | `presigned URL` — quyền kế thừa, hạn dùng (12h console / 7 ngày CLI), lỗi hay gặp | https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html |
| 6 | [s3-multipart-upload.md](s3-multipart-upload.md) | `multipart upload` — 3 bước, part 1–10.000, chi phí part dở dang, ETag | https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html |
| 7 | [s3-server-side-encryption.md](s3-server-side-encryption.md) | Server-side encryption — `SSE-S3` / `SSE-KMS` / `DSSE-KMS` / `SSE-C` | https://docs.aws.amazon.com/AmazonS3/latest/userguide/serv-side-encryption.html |

## Gợi ý thứ tự đọc
1. **apigw-rest-vs-http** — nắm bức tranh tổng: khi nào `REST API`, khi nào `HTTP API` (nền cho mọi câu chọn loại API).
2. **apigw-stage-variables** — hiểu cơ chế 1 API nhiều stage trỏ backend khác nhau (kết nối với `Lambda alias` tuần 3).
3. **apigw-lambda-authorizer** — đào sâu `TOKEN` vs `REQUEST` + luồng trả IAM policy (mảng authorizer hay thi).
4. **apigw-cors** — chốt phần API Gateway: bẫy proxy vs non-proxy, preflight.
5. **s3-presigned-url** — chuyển sang S3 góc dev: quyền kế thừa + hạn dùng (số liệu bẫy).
6. **s3-multipart-upload** — số liệu part/ETag/chi phí, lifecycle abort.
7. **s3-server-side-encryption** — 4 kiểu mã hoá, phân biệt `SSE-KMS` (audit/rotation) vs `SSE-C` (khách giữ khoá).
