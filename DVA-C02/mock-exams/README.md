# 🎯 Mock Exams — AWS Certified Developer – Associate (DVA-C02) (65 câu · 130 phút)

> Ba bộ đề **full-length, canh giờ, phân bổ chuẩn 4 domain**, mô phỏng chính xác định dạng, phong cách và độ khó kỳ thi AWS DVA-C02 (với biên độ khó tăng cường để đảm bảo chắc chắn đậu).
> Khác với các câu hỏi theo chủ đề trong [`../study-plan/`](../study-plan/): ở đó bạn luyện **từng mảng kiến thức**, ở đây bạn luyện **phản xạ tổng hợp của một Developer dưới áp lực 2 phút/câu**.
> Về [Kế hoạch tổng DVA-C02](../DVA-C02-STUDY-PLAN.md) · [Tuần 9 — Ôn tập tổng lực](../study-plan/week-09/README.md) · [Tuần 10 — Tuần chốt](../study-plan/week-10/README.md)

---

## 📚 Ba bộ đề Full-Length

| Mock | Sắc thái & Trọng tâm | Dùng khi nào |
|---|---|---|
| [**Mock 01**](mock-01/questions.md) — *Cốt lõi Serverless, Cơ sở dữ liệu & Nền tảng Bảo mật* | Nặng về **Serverless Fundamentals (Lambda, DynamoDB, API Gateway, S3)**, cấu hình IAM Policy, KMS Envelope Encryption, CodeBuild phases và xử lý bất đồng bộ SQS/SNS. Đo lường phản xạ cú pháp, thông số và các bẫy cơ bản. | Ngay sau khi hoàn thành Tuần 8. Bài đo đường cơ sở (Baseline). |
| [**Mock 02**](mock-02/questions.md) — *Quy trình Triển khai CI/CD, Điều phối & Chẩn đoán Sự cố* | Nặng về **Deployment & Troubleshooting (CodeDeploy Lifecycle Hooks, ECS Task/Execution Roles, Beanstalk Policies, CloudWatch Metrics/Alarms, X-Ray Tracing)**. Đề xuất hiện nhiều log lỗi, CLI outputs, cấu hình file `appspec.yml`/`buildspec.yml`/CloudFormation SAM template. | Sau khi review và vá các lỗ hổng từ Mock 01 (Tuần 9). |
| [**Mock 03**](mock-03/questions.md) — *Kiến trúc Nâng cao, Đánh đổi Hiệu năng & Tình huống Thực chiến Khó nhất* | **Khó nhất và sát đề thi thật nhất**: Cả bốn phương án đều khả thi về mặt kỹ thuật; **qualifier trong đề** (chi phí tối thiểu, độ trễ thấp nhất, không downtime, idempotency, strict ordering) quyết định đáp án đúng. Đòi hỏi tính toán RCU/WCU, Kinesis shards, optimistic locking, token claims injection. | Bài tổng duyệt cuối cùng trước khi đặt lịch thi (Tuần 10). |

Mỗi bộ mock gồm 2 file:
- `questions.md`: Toàn bộ 65 câu hỏi bằng tiếng Anh (chuẩn format Pearson VUE), phân bổ đầy đủ 4 Domain.
- `answers.md`: Bảng đáp án tổng hợp (`Answer key`), bảng chấm điểm theo 4 domain, giải thích chi tiết (*Why correct*, *Why others are wrong*, 🧠 *Key point / trap*, 📎 *Source* trỏ về tài liệu AWS Docs / Study plan).

---

## 📊 Cấu trúc & Tỉ trọng — Chuẩn kỳ thi DVA-C02

| Hạng mục | Mock này | Đề thi thật AWS DVA-C02 |
|---|---|---|
| **Số câu hỏi** | **65 câu** | 65 câu (50 câu tính điểm + 15 câu thử nghiệm unscored) |
| **Thời gian làm bài** | **130 phút** (~2 phút/câu) | 130 phút |
| **Hình thức câu hỏi** | **Single Choice** (1 đáp án) · **Multiple Response** (chọn 2 hoặc 3) | Single Choice · Multiple Response |
| **Điểm đậu chính thức** | 720 / 1000 (~72%) | 720 / 1000 (scaled score) |
| **Ngưỡng đậu cá nhân khuyến nghị** | **≥ 85% (55/65 câu)** | Để có biên an toàn chắc chắn đậu phòng thi |

### Phân bổ Domain chính xác trên mỗi đề 65 câu:

| Domain | Tên Domain | Tỉ trọng chính thức | Số câu trên mỗi Mock |
|---|---|---|---|
| **Domain 1** | **Development with AWS Services** | **32%** | **21 câu** (Câu 1 – 21) |
| **Domain 2** | **Security** | **26%** | **17 câu** (Câu 22 – 38) |
| **Domain 3** | **Deployment** | **24%** | **16 câu** (Câu 39 – 54) |
| **Domain 4** | **Troubleshooting and Optimization** | **18%** | **11 câu** (Câu 55 – 65) |
| **TỔNG** | | **100%** | **65 câu** |

---

## 💡 Đặc thù đề thi DVA-C02 & Chiến lược làm bài

Khác với Solutions Architect (SAA) vốn thiên về *thiết kế kiến trúc cấp cao*, đề thi Developer (DVA) tập trung vào **cách triển khai, cú pháp, mã nguồn SDK/CLI, cấu hình file và chẩn đoán sự cố**:

1. **Phân biệt rạch ròi API Action & Configuration:**
   - Mã hoá dữ liệu > 4 KB: Phải dùng **`kms:GenerateDataKey`** (Envelope Encryption), không thể gọi trực tiếp `kms:Encrypt`.
   - Cross-account access: Phải cấu hình **`sts:AssumeRole`** kèm **Trust Policy** ở tài khoản đích.
   - Tránh cold start: Dùng **Provisioned Concurrency**, trong khi **Reserved Concurrency** dùng để giới hạn trần & bảo vệ tài nguyên downstream.
2. **Nắm vững vòng đời Deploy (CodeDeploy & Beanstalk):**
   - Thứ tự Hooks EC2: `ApplicationStop` → `DownloadBundle` → `BeforeInstall` → `Install` → `AfterInstall` → `ApplicationStart` → `ValidateService`.
   - Thứ tự Hooks Lambda: `BeforeAllowTraffic` → `AfterAllowTraffic`.
   - Thứ tự Hooks ECS: `BeforeInstall` → `Install` → `AfterInstall` → `AllowTestTraffic` → `AfterAllowTestTraffic` → `BeforeAllowTraffic` → `AllowTraffic` → `AfterAllowTraffic`.
   - Beanstalk: Phân biệt rõ `Immutable` (tạo ASG mới song song, rollback an toàn nhất), `Rolling with additional batch` (giữ full capacity, tiết kiệm chi phí), và `Traffic splitting` (canary test).
3. **Tối ưu hoá chi phí & độ trễ:**
   - Secrets Manager: Sử dụng **Client-side Caching library** và khởi tạo ngoài handler Lambda.
   - SQS vs Kinesis: Kinesis hỗ trợ multiple consumers song song (Enhanced Fan-Out 2MB/s/shard) và replay dữ liệu tới 365 ngày; SQS không có replay.
   - DynamoDB: Tránh `Scan`, ưu tiên `Query` với Key Condition Expression; dùng Optimistic Locking với `version` attribute và `ConditionExpression`.
4. **Cảnh giác bẫy dịch vụ Out-of-Scope:**
   - Các dịch vụ như `QuickSight`, `Rekognition`, `Polly`, `WorkSpaces`, `AppStream`, `Storage Gateway` là **out-of-scope** của DVA-C02. Nếu xuất hiện trong đáp án, 99% đó là **mồi nhử**.
   - Lưu ý: `Amazon Athena` và `Amazon Route 53` là **IN-SCOPE** (đừng loại trừ nhầm).

---

## ⏱️ Hướng dẫn luyện đề đạt hiệu quả tối đa

1. **Bật đồng hồ đếm ngược 130 phút:** Làm liên tục, không tra cứu tài liệu, không bấm dừng giữa chừng.
2. **Duy trì tốc độ 1.5 – 2 phút/câu:** Nếu gặp câu phân vân quá 2 phút, đánh dấu lại (flag), chọn tạm một phương án khả dĩ nhất và đi tiếp. Không được để trống bất kỳ câu nào.
3. **Tự chấm điểm ngay sau khi nộp:** Mở `answers.md`, so sánh với `Answer key` và điền số câu đúng vào bảng phân tích 4 domain.
4. **Phân tích 100% câu sai & câu đoán may:** Đọc kỹ phần *Why correct* và *Why others are wrong*, ghi chú lại bẫy đề (🧠 *Key point / trap*).
5. **Cơ chế van an toàn:**
   - **≥ 85% trên cả 3 Mock:** Đủ điều kiện đăng ký thi thật với sự tự tin 100% đậu.
   - **75% – 84%:** Còn một số vùng kiến thức hổng. Quay lại tài liệu của Domain có điểm thấp nhất trong [`../study-plan/`](../study-plan/) ôn lại 2-3 ngày rồi làm đề tiếp theo.
   - **< 75%:** Dừng làm mock mới. Dành 1 tuần ôn lại toàn bộ lý thuyết và hands-on lab của các domain dưới ngưỡng.
