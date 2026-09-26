# ✅ Answers & Explanations — DVA-C02 Mock Exam 02

> Chỉ mở sau khi đã hoàn thành toàn bộ 65 câu trong [questions.md](questions.md) với đồng hồ bấm giờ 130 phút.
> Back to [mock index](../README.md) · [master plan](../../DVA-C02-STUDY-PLAN.md)

**Answer key:** 1-A · 2-A · 3-A · 4-A · 5-B · 6-A · 7-A · 8-A · 9-A · 10-A · 11-A · 12-A · 13-A · 14-A · 15-A · 16-A · 17-A · 18-A · 19-A · 20-AB · 21-A · 22-A · 23-A · 24-A · 25-A · 26-A · 27-A · 28-A · 29-A · 30-A · 31-A · 32-A · 33-A · 34-A · 35-A · 36-A · 37-A · 38-A · 39-A · 40-A · 41-A · 42-A · 43-A · 44-A · 45-A · 46-A · 47-A · 48-A · 49-A · 50-A · 51-A · 52-A · 53-A · 54-A · 55-A · 56-A · 57-A · 58-A · 59-A · 60-A · 61-A · 62-A · 63-A · 64-A · 65-A

> 📌 Với câu `Multi` (câu 20), chỉ tính **đúng** khi chọn đủ và đúng cả hai phương án — không có điểm một phần.

---

## 📊 Bảng chấm điểm theo Domain

| Domain | Tỉ trọng | Câu số | Số đúng / Tổng | % | Ngưỡng đạt chuẩn (≥85%) |
|---|---|---|---|---|---|
| **Domain 1 — Development with AWS Services** | 32% | 1 – 21 | ___ / 21 | ___ % | ≥ 18 / 21 (85.7%) |
| **Domain 2 — Security** | 26% | 22 – 38 | ___ / 17 | ___ % | ≥ 14 / 17 (82.4%) |
| **Domain 3 — Deployment** | 24% | 39 – 54 | ___ / 16 | ___ % | ≥ 14 / 16 (87.5%) |
| **Domain 4 — Troubleshooting and Optimization** | 18% | 55 – 65 | ___ / 11 | ___ % | ≥ 9 / 11 (81.8%) |
| **TỔNG CỘNG** | **100%** | **1 – 65** | **___ / 65** | **___ %** | **≥ 55 / 65 (84.6% ~ 85%)** |

> ⚠️ **Đánh giá kết quả Mock 02:**
> - **≥ 55/65 (≥ 85%):** Xuất sắc. Kiến thức về CI/CD pipeline, CodeDeploy hooks, CloudFormation lifecycle và Troubleshooting của bạn rất vững. Sẵn sàng làm tiếp Mock 03.
> - **47 – 54/65 (72% – 84%):** Đạt ngưỡng đỗ lý thuyết nhưng chưa có biên an toàn. Rà soát ngay các câu sai ở domain thấp nhất.
> - **< 47/65 (< 72%):** Chưa đạt. Dành 3 ngày ôn lại toàn bộ lý thuyết và bài tập của domain yếu nhất trong [`../../study-plan/`](../../study-plan/).

---

## 📝 Giải thích chi tiết 65 câu hỏi

### Question 1 — Answer: **A**
- **Why correct:** Khi Lambda được cấu hình kết nối vào VPC (đặt trong private subnet), Lambda sẽ tạo các Elastic Network Interfaces (ENIs) với IP riêng trong subnet đó. Các ENI này **không bao giờ có địa chỉ IPv4 công khai (public IP)**. Do đó, dù VPC có gắn Internet Gateway (IGW), Lambda trong subnet riêng không thể trực tiếp gửi gói tin ra internet. Để truy cập các API công khai của bên thứ ba (như cổng thanh toán), Lambda bắt buộc phải định tuyến lưu lượng qua một **NAT Gateway** đặt trong một public subnet (public subnet này có route `0.0.0.0/0` trỏ tới Internet Gateway).
- **Why the others are wrong:** B sai vì ENI của Lambda không có public IP nên dù gắn IGW trực tiếp vào subnet thì gói tin phản hồi từ internet cũng không thể tìm đường quay lại. C sai vì Lambda không hỗ trợ gán public IPv4 trực tiếp lên ENI của hàm. D sai vì VPC Endpoint chỉ dùng để truy cập các dịch vụ nội bộ của AWS hoặc qua AWS PrivateLink, không dùng cho IP công khai của các cổng thanh toán bên thứ ba.
- 🧠 **Key point / trap:** Lambda trong VPC muốn ra Internet: **Private Subnet (chứa Lambda ENI) → Route `0.0.0.0/0` to NAT Gateway (ở Public Subnet) → Route `0.0.0.0/0` to Internet Gateway**.
- 📎 Source: `AWS Lambda Developer Guide — Configuring a Lambda function to access resources in a VPC`.

---

### Question 2 — Answer: **A**
- **Why correct:** **Provisioned Concurrency** chuẩn bị sẵn (pre-warm) các môi trường thực thi đã được nạp mã nguồn và khởi tạo runtime, giúp loại bỏ hoàn toàn độ trễ khởi động nguội (cold start). Kết hợp Provisioned Concurrency với **Application Auto Scaling** theo lịch trình (**Scheduled Scaling Actions**) cho phép tăng số lượng provisioned concurrency vào 08:50 AM (trước giờ mở app) và giảm về 0 vào 05:10 PM, vừa giải quyết triệt để vấn đề giật lag vừa tối ưu chi phí qua đêm.
- **Why the others are wrong:** B sai vì gửi request ping định kỳ (dummy payload) chỉ giữ ấm được 1 hoặc vài container ngẫu nhiên, không thể đối phó với lượng hàng trăm nghìn người dùng ùa vào cùng một lúc gây ra hàng loạt cold start mới. C sai vì tăng timeout không làm giảm thời gian khởi động runtime (cold start). D sai vì Reserved Concurrency chỉ giới hạn số lượng concurrency tối đa và dự trữ quota từ pool của tài khoản, chứ không giữ ấm container.
- 🧠 **Key point / trap:** Muốn loại bỏ cold start theo khung giờ cố định → **Provisioned Concurrency + Application Auto Scaling scheduled scaling**.
- 📎 Source: `AWS Lambda Developer Guide — Configuring provisioned concurrency for a function`.

---

### Question 3 — Answer: **A**
- **Why correct:** **AWS Lambda Layers** là cơ chế chuẩn để đóng gói các thư viện phụ thuộc (dependencies), SDK tùy chỉnh, hoặc runtime riêng biệt nhằm chia sẻ giữa nhiều hàm Lambda. Thay vì phải đóng gói thư viện 15 MB vào từng file ZIP của 15 hàm (gây phình to kích thước và chậm CI/CD), developer đưa thư viện vào 1 Layer duy nhất và gắn ARN của layer đó vào 15 hàm. Khi hàm chạy, nội dung của layer sẽ được giải nén tự động vào thư mục `/opt`.
- **Why the others are wrong:** B sai vì DynamoDB là cơ sở dữ liệu NoSQL, không dùng để lưu trữ và nạp code thực thi runtime, gây chậm trễ nghiêm trọng. C sai vì biến môi trường (environment variables) có giới hạn dung lượng tối đa chỉ 4 KB. D sai vì chạy `pip install` từ S3 trong mỗi lần gọi hàm làm tăng cold start lên hàng chục giây và tiêu tốn CPU/RAM vô ích.
- 🧠 **Key point / trap:** Chia sẻ code chung, thư viện chung giữa nhiều Lambda → **Lambda Layers** (tối đa 5 layers/hàm, giải nén vào `/opt`).
- 📎 Source: `AWS Lambda Developer Guide — Working with layers`.

---

### Question 4 — Answer: **A**
- **Why correct:** **AWS Lambda Response Streaming** cho phép hàm Lambda gửi dần từng phần dữ liệu (stream) về client qua cơ chế HTTP chunked transfer encoding thay vì phải đợi toàn bộ payload được tạo xong trong bộ nhớ. Tính năng này giúp giảm mạnh chỉ số Time to First Byte (TTFB), tránh tình trạng timeout 504 tại API Gateway hoặc Application Load Balancer (ALB), và hỗ trợ dung lượng response lên tới 20 MB (so với giới hạn 6 MB đồng bộ truyền thống).
- **Why the others are wrong:** B sai vì nén ZIP vẫn yêu cầu hàm phải tạo xong toàn bộ file nén rồi mới trả về một lần, không giảm được TTFB. C sai vì chia nhỏ hàm qua Step Functions rất phức tạp và không hỗ trợ stream HTTP response trực tiếp về browser của người dùng qua ALB. D sai vì tăng `/tmp` chỉ mở rộng ổ đĩa tạm, không làm thay đổi cơ chế đệm response của Lambda.
- 🧠 **Key point / trap:** Tránh timeout khi sinh payload lớn/chậm, giảm TTFB → **Lambda Response Streaming (`awslambda.streamifyResponse`)**.
- 📎 Source: `AWS Lambda Developer Guide — Configuring response streaming for a Lambda function`.

---

### Question 5 — Answer: **B**
- **Why correct:** Cách tính WCU cho giao dịch `TransactWriteItems`:
  1. Giao dịch `TransactWriteItems` tiêu tốn **gấp đôi (2x)** dung lượng ghi tiêu chuẩn vì DynamoDB thực hiện kiểm tra trước (pre-check) và cam kết giao dịch (commit).
  2. Bảng `Products` (item size 2 KB):
     - Ghi thông thường: `ceil(2 KB / 1 KB) = 2 WCU`.
     - Ghi giao dịch: `2 WCU × 2 = 4 WCU` cho mỗi item.
     - Với 20 đơn hàng/giây: `20 × 4 WCU = 80 WCU`.
  3. Bảng `Orders` (item size 1 KB):
     - Ghi thông thường: `ceil(1 KB / 1 KB) = 1 WCU`.
     - Ghi giao dịch: `1 WCU × 2 = 2 WCU` cho mỗi item.
     - Với 20 đơn hàng/giây: `20 × 2 WCU = 40 WCU`.
  - Tổng cộng: `Products` cần **80 WCU**, `Orders` cần **40 WCU**.
- **Why the others are wrong:** A (40 & 20) tính nhầm theo ghi thông thường (quên nhân 2 cho Transaction). C và D tính sai kích thước item và hệ số giao dịch.
- 🧠 **Key point / trap:** `TransactWriteItems` tiêu tốn **2x WCU**; `TransactGetItems` tiêu tốn **2x RCU**.
- 📎 Source: `Amazon DynamoDB Developer Guide — Capacity unit consumption for transactions`.

---

### Question 6 — Answer: **A**
- **Why correct:** **DynamoDB Time to Live (TTL)** tự động xóa các item đã hết hạn mà **không tiêu tốn bất kỳ WCU nào** của bảng và không phát sinh thêm chi phí. Điều kiện bắt buộc là thuộc tính TTL phải lưu trữ mốc thời gian dưới dạng số nguyên **Unix epoch time tính bằng giây (seconds)**.
- **Why the others are wrong:** B sai vì DynamoDB TTL chỉ chấp nhận Unix epoch seconds dạng số nguyên (Number), không hỗ trợ chuỗi ISO-8601. C sai vì viết hàm quét `Scan` và xóa `BatchWriteItem` tiêu tốn rất nhiều RCU/WCU và tốn chi phí vận hành Lambda. D sai vì DynamoDB Streams chỉ phát sinh stream khi có sự kiện thay đổi dữ liệu, bản thân nó không tự xóa item.
- 🧠 **Key point / trap:** DynamoDB TTL: Tiêu tốn **0 WCU**, thuộc tính phải là **Number** biểu diễn **Unix epoch time in seconds**.
- 📎 Source: `Amazon DynamoDB Developer Guide — Using Time to Live (TTL)`.

---

### Question 7 — Answer: **A**
- **Why correct:** **Amazon DynamoDB Accelerator (DAX)** là bộ nhớ đệm in-memory hoàn toàn tương thích với API của DynamoDB, mang lại tốc độ phản hồi tính bằng microsecond. DAX có 2 loại cache:
  1. **Item Cache:** Lưu trữ các item riêng lẻ lấy qua `GetItem` hoặc `BatchGetItem`.
  2. **Query Cache:** Lưu trữ kết quả và tham số của các lệnh `Query` và `Scan`.
- **Why the others are wrong:** B sai vì DAX lưu cả `GetItem` trong Item Cache. C sai vì DAX là bộ đệm ghi xuyên suốt (write-through) và trả lời trực tiếp các lệnh đọc trúng cache (cache hit). D sai vì DAX tương thích 100% với DynamoDB SDK, không yêu cầu viết lại code bằng cú pháp Redis.
- 🧠 **Key point / trap:** DAX đọc có 2 loại cache: **Item Cache** (cho GetItem) và **Query Cache** (cho Query/Scan). Tương thích API nguyên bản, không cần sửa logic truy vấn.
- 📎 Source: `Amazon DynamoDB Developer Guide — In-Memory Acceleration with DynamoDB Accelerator (DAX)`.

---

### Question 8 — Answer: **A**
- **Why correct:** **PartiQL for DynamoDB** là ngôn ngữ truy vấn tương thích chuẩn SQL, cho phép lập trình viên và quản trị viên thực thi các câu lệnh quen thuộc như `SELECT`, `INSERT`, `UPDATE`, `DELETE` trên bảng DynamoDB thông qua AWS Console, CLI hoặc SDK.
- **Why the others are wrong:** B sai vì Athena là dịch vụ truy vấn tương tác cho dữ liệu trên S3 hoặc federated query cho data analytics, không phải giao diện truy vấn tác nghiệp trực tiếp chuẩn của DynamoDB. C sai vì Redshift Spectrum dành cho data warehouse truy vấn S3 data lake. D sai vì LSI là cấu trúc chỉ mục phụ, không phải ngôn ngữ truy vấn.
- 🧠 **Key point / trap:** Muốn dùng cú pháp SQL (`SELECT`, `UPDATE`) trên DynamoDB → **PartiQL**.
- 📎 Source: `Amazon DynamoDB Developer Guide — PartiQL: A SQL-Compatible Query Language for DynamoDB`.

---

### Question 9 — Answer: **A**
- **Why correct:** **Amazon API Gateway Canary Release Deployment** cho phép tách một phần trăm lưu lượng truy cập (ví dụ 10%) của một stage cụ thể sang bản dựng mới (canary deployment) trong khi 90% còn lại vẫn đi vào bản ổn định. CloudWatch metrics tự động phân tách theo stage và canary stage để lập trình viên giám sát tỷ lệ lỗi (4xx/5xx) và độ trễ. Sau khi kiểm thử thành công, chỉ cần nhấn "Promote Canary" là 100% traffic chuyển sang bản mới với zero downtime.
- **Why the others are wrong:** B sai vì Route 53 Weighted routing chỉ phân giải DNS ở cấp domain, không quản lý được phiên bản canary và triển khai mượt mà bên trong một API stage. C sai vì stage variable không tự động phân chia tải canary chuẩn hóa. D sai vì thêm ALB phía trước API Gateway gây phức tạp kiến trúc và chi phí không cần thiết.
- 🧠 **Key point / trap:** Triển khai thử nghiệm 10% traffic vào API Gateway REST API → **Canary release deployment on stage**.
- 📎 Source: `Amazon API Gateway Developer Guide — Set up API Gateway Canary Release Deployments`.

---

### Question 10 — Answer: **A**
- **Why correct:** Khi xác thực ứng dụng sử dụng các bearer token tùy biến từ OAuth 2.0 Identity Provider bên ngoài (chứa các custom cryptographic claims, cần gọi endpoint xác minh riêng hoặc kiểm tra phân quyền phức tạp), giải pháp tối ưu là **Lambda Authorizer** (trước đây là Custom Authorizer). Lambda Authorizer sẽ nhận token, thực thi code thẩm định, và trả về một IAM policy cho phép hoặc từ chối truy cập.
- **Why the others are wrong:** B sai vì Cognito User Pool Authorizer chỉ có thể xác thực các token JWT do chính Amazon Cognito User Pools cấp phát, không hỗ trợ các token có claim tùy biến của bên thứ ba. C sai vì API Keys dùng để kiểm soát hạn ngạch và gói cước (usage plans/rate limiting), không phải để xác thực người dùng. D sai vì IAM role yêu cầu ký request bằng AWS SigV4, không phù hợp với các client di động dùng OAuth 2.0 bearer token.
- 🧠 **Key point / trap:** Xác thực token tùy chỉnh / OAuth 2.0 bên thứ ba tại API Gateway → **Lambda Authorizer**. Token Cognito → **Cognito User Pool Authorizer**.
- 📎 Source: `Amazon API Gateway Developer Guide — Use API Gateway Lambda authorizers`.

---

### Question 11 — Answer: **A**
- **Why correct:** API Gateway REST APIs hỗ trợ **Mapping Templates** viết bằng ngôn ngữ **Velocity Template Language (VTL)** tại phần **Integration Request**. Lập trình viên có thể trích xuất các giá trị từ payload JSON gửi lên (ví dụ `$input.path('$.customerId')`) và bọc chúng vào cấu trúc XML mong muốn để gửi thẳng tới backend SOAP/XML mà không cần viết bất kỳ hàm trung gian Lambda nào.
- **Why the others are wrong:** B sai vì AWS WAF là tường lửa ứng dụng web dùng để lọc và chặn mã độc/IP xấu, không có tính năng chuyển đổi định dạng dữ liệu (data transformation). C sai vì Stage Variables chỉ lưu các chuỗi cấu hình cố định. D sai vì Mock Integration trả về phản hồi giả lập, không chuyển tiếp request tới backend service.
- 🧠 **Key point / trap:** Chuyển đổi định dạng JSON ↔ XML tại API Gateway mà không tốn tài nguyên compute → **VTL Mapping Templates trong Integration Request / Response**.
- 📎 Source: `Amazon API Gateway Developer Guide — Mapping template and access logging variable reference`.

---

### Question 12 — Answer: **A**
- **Why correct:** **Amazon S3 Select** cho phép chạy các câu lệnh truy vấn SQL đơn giản trực tiếp trên các file lưu trữ trong S3 (định dạng CSV, JSON, hoặc Apache Parquet). Bằng cách lọc dữ liệu ngay tại S3 và chỉ trả về phần dữ liệu khớp điều kiện (250 MB thay vì tải toàn bộ 50 GB), S3 Select giúp tăng tốc độ xử lý lên tới 400% và tiết kiệm 99% chi phí băng thông truyền tải mạng.
- **Why the others are wrong:** B sai vì Transfer Acceleration chỉ tăng tốc đường truyền qua edge location của CloudFront, ứng dụng vẫn phải tải toàn bộ 50 GB. C sai vì replication sao chép cả file lớn, không lọc được dữ liệu. D sai vì Object Lock dùng để khóa dữ liệu chống xóa (WORM), không liên quan đến truy vấn.
- 🧠 **Key point / trap:** Lọc và chỉ tải một phần dữ liệu nhỏ từ file lớn (CSV/JSON/Parquet) trên S3 bằng SQL → **Amazon S3 Select**. (Lưu ý: AWS đã dừng nhận khách hàng mới cho S3 Select từ giữa 2024 và khuyến nghị Athena/S3 Express, nhưng trong đề thi DVA-C02 hiện hành thì S3 Select vẫn là đáp án chuẩn cho kịch bản SQL lọc trực tiếp trên S3).
- 📎 Source: `Amazon S3 User Guide — Filtering and retrieving data using Amazon S3 Select`.

---

### Question 13 — Answer: **A**
- **Why correct:** **Dead-Letter Queue (DLQ)** trong Amazon SQS là giải pháp chuẩn để cô lập các tin nhắn lỗi ("poison pill" - tin nhắn gây crash worker). Bằng cách thiết lập thuộc tính `RedrivePolicy` với `maxReceiveCount = 3`, khi một tin nhắn được worker lấy về 3 lần mà không xóa thành công (vì worker crash và visibility timeout trôi qua), SQS sẽ tự động chuyển tin nhắn đó sang DLQ, giải phóng hàng đợi chính.
- **Why the others are wrong:** B sai vì `DelaySeconds` chỉ trì hoãn việc hiển thị tin nhắn mới gửi, không cô lập được tin nhắn lỗi. C sai vì kéo dài `MessageRetentionPeriod` chỉ làm tin nhắn lưu lại lâu hơn chứ không ngăn được vòng lặp crash. D sai vì giảm visibility timeout về 0 sẽ làm tin nhắn lỗi tái xuất hiện ngay lập tức, khiến worker crash liên tục và nhanh hơn.
- 🧠 **Key point / trap:** Tránh poison pill loop trong SQS → **Dead-Letter Queue (DLQ) với RedrivePolicy (`maxReceiveCount`)**.
- 📎 Source: `Amazon SQS Developer Guide — Amazon SQS dead-letter queues`.

---

### Question 14 — Answer: **A**
- **Why correct:** Thông số dung lượng của 1 Kinesis Shard:
  - Tốc độ ghi tối đa: **1 MB/giây** và **1,000 records/giây**.
  - Hiện tại có 4 shards → Dung lượng tối đa: 4 MB/s và 4,000 records/s.
  - Lưu lượng đỉnh: 5.5 MB/s và 5,000 records/s.
  - Số shard tối thiểu cần thiết: `ceil(5.5 / 1) = 6 shards` (cung cấp 6 MB/s và 6,000 records/s).
  - Do đó cần **Resharding** (chia nhỏ shard - split shards) để nâng tổng số shard lên ít nhất 6.
- **Why the others are wrong:** B sai vì retention period chỉ quy định thời gian lưu trữ dữ liệu (từ 24h đến 365 ngày), không làm tăng thông lượng ghi. C sai vì Enhanced Fan-Out dùng để tăng thông lượng đọc (read throughput) cho consumer, không hỗ trợ producer ghi dữ liệu. D sai vì đặt partition key là chuỗi cố định sẽ băm toàn bộ dữ liệu vào duy nhất 1 shard (1 MB/s), khiến lỗi throttle trầm trọng hơn.
- 🧠 **Key point / trap:** 1 Kinesis Shard = **1 MB/s ghi (hoặc 1,000 records/s)** & **2 MB/s đọc**. Vượt quá dung lượng ghi → **Reshard (Split shards)**.
- 📎 Source: `Amazon Kinesis Data Streams Developer Guide — Resharding a Stream`.

---

### Question 15 — Answer: **A**
- **Why correct:** Ở chế độ tiêu chuẩn, tất cả các consumer phải chia sẻ chung hạn mức đọc **2 MB/giây trên mỗi shard** thông qua API `GetRecords`. Khi có 3 consumer cùng đọc, mỗi consumer chỉ nhận được trung bình ~0.66 MB/s dẫn đến tranh chấp và lỗi `ReadProvisionedThroughputExceeded`. Tính năng **Enhanced Fan-Out** cho phép mỗi consumer đăng ký riêng biệt qua API `SubscribeToShard`, cung cấp băng thông đọc **riêng biệt 2 MB/giây/shard cho từng consumer** thông qua kết nối HTTP/2 server push.
- **Why the others are wrong:** B sai vì tăng số shard làm tăng chi phí và các consumer vẫn phải chia sẻ băng thông đọc trên từng shard nếu dùng standard polling. C sai vì SQS không đảm bảo thứ tự luồng dữ liệu Kinesis và làm phức tạp kiến trúc. D sai vì Systems Manager không có bộ đệm cho luồng Kinesis.
- 🧠 **Key point / trap:** Nhiều consumer đọc cùng 1 Kinesis Stream bị throttle đọc → Đăng ký **Enhanced Fan-Out (`SubscribeToShard`)** để mỗi consumer có riêng 2 MB/s/shard.
- 📎 Source: `Amazon Kinesis Data Streams Developer Guide — Developing Custom Consumers with Enhanced Fan-Out`.

---

### Question 16 — Answer: **A**
- **Why correct:** Trong ngôn ngữ định nghĩa Amazon States Language (ASL) của Step Functions:
  - Khối `Retry` được dùng để tự động thử lại khi gặp lỗi tạm thời (như HTTP 500) với các tham số: `ErrorEquals`, `IntervalSeconds`, `MaxAttempts`, và `BackoffRate`.
  - Khối `Catch` bắt các lỗi nghiệp vụ không thể khắc phục (như HTTP 400 - số thẻ sai) và điều hướng thực thi sang một bước kế tiếp (`Next: "SendFailureNotification"`) mà không thử lại.
- **Why the others are wrong:** B sai vì viết vòng lặp tự chế trong container làm mất đi khả năng quan sát trạng thái và quản lý luồng của Step Functions. C sai vì `Choice` state chỉ có thể kiểm tra kết quả của các state đã chạy trước đó, không thể dự đoán mã lỗi HTTP của tác vụ sắp chạy. D sai vì Step Functions không gắn DLQ trực tiếp bên trong activity worker theo cách này.
- 🧠 **Key point / trap:** Xử lý lỗi trong Step Functions: Lỗi tạm thời (500) → **`Retry` (với exponential backoff)**; Lỗi dữ liệu/nghiệp vụ (400) → **`Catch` (chuyển sang error handler state)**.
- 📎 Source: `AWS Step Functions Developer Guide — Error handling in Step Functions`.

---

### Question 17 — Answer: **A**
- **Why correct:** Trong Task state của Step Functions:
  - **`ResultPath`** chỉ định đường dẫn JSON nơi kết quả của tác vụ (ví dụ `{"creditScore": 750}`) sẽ được chèn vào payload đầu vào ban đầu. Đặt `ResultPath: "$.ratingDetails"` sẽ giữ nguyên toàn bộ thông tin khách hàng ở payload gốc và bổ sung thêm trường `ratingDetails` chứa điểm tín dụng.
- **Why the others are wrong:** B sai vì `InputPath` dùng để chọn lọc một phần của payload đầu vào gửi cho tác vụ. C sai vì `OutputPath` dùng để lọc bớt dữ liệu trước khi chuyển sang state tiếp theo (nếu đặt `OutputPath: "$.ratingDetails"` thì toàn bộ thông tin khách hàng ban đầu sẽ bị vứt bỏ, chỉ giữ lại `ratingDetails`). D sai vì `Parameters` dùng để tái cấu trúc dữ liệu gửi vào tác vụ.
- 🧠 **Key point / trap:** Muốn giữ nguyên đầu vào và gộp thêm kết quả của Task vào một trường mới → **`ResultPath: "$.fieldName"`**. Muốn vứt bỏ kết quả chỉ giữ đầu vào → `ResultPath: null`.
- 📎 Source: `AWS Step Functions Developer Guide — Input and Output Processing in Step Functions`.

---

### Question 18 — Answer: **A**
- **Why correct:** **S3 Lifecycle Rules** cung cấp các hành động chuyên biệt để quản lý chi phí phiên bản:
  1. `NoncurrentVersionExpiration`: Tự động xóa vĩnh viễn các phiên bản cũ sau một số ngày nhất định (ở đây là 30 ngày) kể từ khi chúng trở thành noncurrent.
  2. `ExpiredObjectDeleteMarkers`: Tự động xóa các delete marker đã hết hạn (khi đối tượng không còn bất kỳ phiên bản nào khác phía dưới nó), giúp dọn dẹp triệt để metadata và tiết kiệm chi phí.
- **Why the others are wrong:** B sai vì tắt Versioning (Suspend) không tự động xóa các phiên bản cũ đã tồn tại trước đó. C sai vì viết hàm Lambda quét và xóa hàng triệu phiên bản vừa tốn kém chi phí thực thi vừa phát sinh chi phí gọi API S3 List/Delete. D sai vì S3 Object Lock ngăn chặn việc xóa file, đi ngược lại mục tiêu dọn dẹp rác.
- 🧠 **Key point / trap:** Dọn dẹp phiên bản cũ và marker rác trên S3 → S3 Lifecycle rule với **`NoncurrentVersionExpiration`** và **`ExpiredObjectDeleteMarkers`**.
- 📎 Source: `Amazon S3 User Guide — Managing your storage lifecycle`.

---

### Question 19 — Answer: **A**
- **Why correct:** Trình duyệt web áp dụng chính sách Same-Origin Policy đối với các tài nguyên web fonts (`.woff2`, `.ttf`) và các lệnh gọi `fetch/XHR`. Khi website tại `https://portal.example.com` tải font từ S3 bucket `s3://company-assets-prod` (khác origin), S3 phải trả về các HTTP headers xác nhận CORS. Cấu hình CORS trên S3 bucket phải khai báo `AllowedOrigins` chứa origin gọi tới (`https://portal.example.com`) và `AllowedMethods` là `GET`, `HEAD`.
- **Why the others are wrong:** B sai vì S3 Bucket Policy cấp quyền truy cập tầng IAM/Storage, nhưng trình duyệt web kiểm tra CORS headers ở tầng HTTP; thiếu CORS configuration thì dù file public trình duyệt vẫn chặn. C và D hoàn toàn không liên quan đến cơ chế CORS của trình duyệt.
- 🧠 **Key point / trap:** Trình duyệt báo lỗi `No 'Access-Control-Allow-Origin' header` khi tải font/ảnh/AJAX từ S3 → Bắt buộc cấu hình **CORS (Cross-Origin Resource Sharing)** trên chính S3 bucket đó.
- 📎 Source: `Amazon S3 User Guide — Configuring cross-origin resource sharing (CORS)`.

---

### Question 20 — Answer: **A, B**
- **Why correct:** Amazon SQS FIFO queue hỗ trợ loại bỏ tin nhắn trùng lặp (deduplication) trong cửa sổ 5 phút bằng 2 cơ chế:
  1. **Cung cấp `MessageDeduplicationId` tường minh:** Ứng dụng gửi tin nhắn chỉ định một chuỗi định danh duy nhất (ví dụ TransactionID) trong thuộc tính `MessageDeduplicationId`.
  2. **Bật Content-Based Deduplication trên queue:** SQS sẽ tự động tạo `MessageDeduplicationId` bằng cách băm mã SHA-256 nội dung của `MessageBody`. Nếu hai tin nhắn có cùng body gửi đến trong vòng 5 phút, tin nhắn thứ hai sẽ bị hủy bỏ.
- **Why the others are wrong:** C sai vì `ReceiveMessageWaitTimeSeconds` là thời gian long polling khi consumer nhận tin, không liên quan đến deduplication. D sai vì visibility timeout quản lý thời gian ẩn tin nhắn khi worker đang xử lý. E sai vì `MessageGroupId` dùng để đảm bảo thứ tự tuần tự nghiêm ngặt cho từng nhóm tin nhắn, không dùng để chống trùng lặp.
- 🧠 **Key point / trap:** SQS FIFO Deduplication: Hoặc chỉ định rõ **`MessageDeduplicationId`**, hoặc bật **Content-Based Deduplication (SHA-256)** trên hàng đợi. Cửa sổ deduplication là **5 phút**.
- 📎 Source: `Amazon SQS Developer Guide — FIFO queue logic`.

---

### Question 21 — Answer: **A**
- **Why correct:** Trong Amazon DynamoDB, khi ứng dụng ghi hoặc cập nhật một item trên bảng gốc có chứa thuộc tính được chiếu (projected) vào Global Secondary Index (GSI), DynamoDB phải ghi đồng bộ dữ liệu đó vào cả bảng gốc lẫn GSI. Nếu GSI không được cấp phát đủ Write Capacity Units (ở đây GSI chỉ có 100 WCU trong khi bảng gốc ghi 600 WCU), việc ghi vào GSI sẽ bị nghẽn. Để bảo vệ tính nhất quán, DynamoDB sẽ **throttle trực tiếp thao tác ghi trên bảng gốc** và trả về `ProvisionedThroughputExceededException`.
- **Why the others are wrong:** B sai vì bảng gốc có 1,000 WCU và chỉ tiêu thụ 600 WCU nên bản thân bảng gốc không hề bị quá tải. C sai vì thao tác ghi vào GSI tiêu thụ WCU chứ không phải RCU. D sai vì DynamoDB không bao giờ tự động xóa dữ liệu khi quá tải.
- 🧠 **Key point / trap:** Bảng gốc DynamoDB còn dư WCU nhưng vẫn bị `ProvisionedThroughputExceededException` khi ghi → **GSI bị thiếu WCU (GSI Write Throttling)**. Luôn đảm bảo GSI có WCU ≥ WCU của base table.
- 📎 Source: `Amazon DynamoDB Developer Guide — Provisioned Throughput Considerations for Global Secondary Indexes`.

---

### Question 22 — Answer: **A**
- **Why correct:** Lỗ hổng **Confused Deputy** xảy ra khi một bên thứ ba (ở đây là SaaS vendor) có quyền hạn cao bị một kẻ tấn công (khách hàng xấu) lợi dụng để truy cập tài nguyên của một nạn nhân khác. Bằng cách yêu cầu bên thứ ba cung cấp một mã bí mật duy nhất **`sts:ExternalId`** trong khối `Condition` của Role Trust Policy, role ở Account B chỉ cho phép assume khi vendor truyền chính xác `ExternalId` được sinh riêng cho khách hàng đó.
- **Why the others are wrong:** B sai vì các lệnh gọi từ SaaS vendor bắt nguồn từ hạ tầng AWS của vendor, không thể giới hạn bằng địa chỉ IP on-premises của khách hàng. C sai vì xoay vòng khóa KMS không ngăn chặn được việc giả mạo vai trò assume role. D sai vì chia sẻ IAM user access key là hành vi vi phạm nghiêm trọng nguyên tắc bảo mật AWS.
- 🧠 **Key point / trap:** Chống Confused Deputy khi cho phép tài khoản bên thứ 3 (SaaS vendor) assume role vào tài khoản của mình → Bắt buộc dùng **`sts:ExternalId`** trong `Condition` của Trust Policy.
- 📎 Source: `AWS IAM User Guide — How to use an external ID when granting access to your AWS resources to a third party`.

---

### Question 23 — Answer: **A**
- **Why correct:** Biến điều kiện **`aws:RequestTag/${TagKey}`** kiểm tra các cặp key-value của thẻ (tag) được truyền trực tiếp trong request API đang thực thi (ví dụ khi gọi lệnh `RunInstances` có kèm tag `Environment = Development`). Nếu request không chứa tag này, câu lệnh Deny hoặc điều kiện Allow sẽ chặn thao tác ngay lập tức.
- **Why the others are wrong:** B sai vì `aws:PrincipalTag` kiểm tra tag được gắn trên chính người dùng hoặc role đang gọi API (caller), không phải tag gắn trên tài nguyên EC2 được tạo ra. C sai vì `MultiFactorAuthPresent` kiểm tra xác thực hai lớp (MFA). D sai vì `SourceIp` kiểm tra địa chỉ IP của client gọi API.
- 🧠 **Key point / trap:** Kiểm tra tag gửi kèm trong request tạo tài nguyên → **`aws:RequestTag`**. Kiểm tra tag của người đang gọi API → **`aws:PrincipalTag`**. Kiểm tra tag đã có sẵn trên tài nguyên đích → **`aws:ResourceTag`**.
- 📎 Source: `AWS IAM User Guide — AWS global condition context keys`.

---

### Question 24 — Answer: **A**
- **Why correct:** Amazon SQS hỗ trợ **Resource-based Policy (Queue Policy)**. Bằng cách gắn trực tiếp một chính sách lên hàng đợi ở Account A cho phép ARN của Lambda execution role ở Account B thực hiện hành động `sqs:SendMessage`, Lambda có thể gửi tin nhắn thẳng tới SQS mà không cần thực hiện thao tác chuyển đổi role (`sts:AssumeRole`) hay quản lý thông tin xác thực tạm thời, tối ưu hiệu năng và đơn giản hóa mã nguồn.
- **Why the others are wrong:** B hoạt động được nhưng tốn thêm bước gọi API STS, tốn thời gian trễ và phức tạp hóa code Lambda. C vi phạm nguyên tắc bảo mật khi hardcode access key của IAM user. D sai vì không thể gộp hai tài khoản AWS thành một.
- 🧠 **Key point / trap:** Cấp quyền cross-account tới dịch vụ hỗ trợ Resource-based Policy (S3, SQS, SNS, KMS) → **Gắn Resource-based Policy cho phép Principal từ tài khoản khác**, không cần `sts:AssumeRole`.
- 📎 Source: `Amazon SQS Developer Guide — Basic examples of Amazon SQS policies`.

---

### Question 25 — Answer: **A**
- **Why correct:** Các ứng dụng Single Page Application (SPA) chạy trên trình duyệt web của người dùng được coi là "Public Clients" vì mã nguồn JavaScript hiển thị công khai, không thể lưu trữ an toàn mã bí mật `client_secret`. Chuẩn OAuth 2.0 khuyến nghị sử dụng luồng **Authorization Code Grant kết hợp với PKCE (Proof Key for Code Exchange)** và không sử dụng client secret, giúp ngăn chặn triệt để nguy cơ đánh cắp authorization code qua tấn công trung gian.
- **Why the others are wrong:** B sai vì Implicit Grant đã bị loại bỏ khỏi chuẩn OAuth 2.1 do trả token trực tiếp trên URL hash fragment rất dễ bị lộ, và SPA cũng không được chứa client secret. C sai vì Client Credentials dành riêng cho giao tiếp machine-to-machine giữa các server backend. D sai vì ROPC (truyền username/password thô) là luồng lỗi thời và không an toàn.
- 🧠 **Key point / trap:** Xác thực Single Page Apps (React/Vue/Angular) với Cognito → **Authorization Code Grant with PKCE (không dùng client secret)**.
- 📎 Source: `Amazon Cognito Developer Guide — Understanding Cognito user pool OAuth 2.0 grant types`.

---

### Question 26 — Answer: **A**
- **Why correct:** Các token do Cognito User Pool cấp phát (ID Token, Access Token) là các chuỗi JWT theo chuẩn OIDC/OAuth 2.0. Các dịch vụ AWS gốc (như Amazon S3, DynamoDB) không chấp nhận JWT bearer token trực tiếp trong header để phân quyền. Để tương tác với S3, ứng dụng di động phải gửi ID Token lên **Amazon Cognito Identity Pools (Federated Identities)**. Identity Pool sẽ kiểm tra tính hợp lệ và gọi AWS STS để đổi lấy **bộ thông tin xác thực AWS tạm thời** (`AccessKeyId`, `SecretAccessKey`, `SessionToken`) tương ứng với IAM Role của người dùng.
- **Why the others are wrong:** B sai vì S3 REST API không chấp nhận Cognito JWT token trực tiếp. C sai vì AWS CLI không thể chạy trên thiết bị di động để đổi token. D sai vì tạo IAM user cho hàng nghìn khách hàng là sai kiến trúc và chạm giới hạn quota của IAM.
- 🧠 **Key point / trap:** **User Pools = Authentication (cấp JWT tokens)**. **Identity Pools = Authorization (đổi token lấy temporary AWS credentials để gọi trực tiếp các dịch vụ AWS như S3, DynamoDB)**.
- 📎 Source: `Amazon Cognito Developer Guide — Common Amazon Cognito scenarios`.

---

### Question 27 — Answer: **A**
- **Why correct:** Khi thực hiện thao tác cross-account có liên quan đến AWS KMS Customer Managed Key (CMK), bắt buộc phải có sự cho phép từ **cả hai phía**:
  1. **KMS Key Policy ở Account A** (tài khoản sở hữu key) phải cấp quyền cho Account B (hoặc ARN của role Account B) thực thi `kms:GenerateDataKey` và `kms:Decrypt`.
  2. **IAM Policy ở Account B** (tài khoản người gọi) phải cho phép role đó gọi các API KMS trên ARN của khóa ở Account A.
  Nếu thiếu một trong hai chính sách này, yêu cầu sẽ bị chặn ngay lập tức với lỗi `Access Denied`.
- **Why the others are wrong:** B sai vì tạo khóa mới ở Account B không thể mã hóa/giải mã đối tượng trong bucket của Account A. C sai vì chuyển sang SSE-S3 sẽ làm mất quyền kiểm soát chi tiết của Customer Managed Key theo yêu cầu của doanh nghiệp. D sai vì không thể vô hiệu hóa (disable) một key policy mà không khóa luôn quyền truy cập của mọi người.
- 🧠 **Key point / trap:** Truy cập KMS CMK cross-account: **Key Policy (Account A) PHẢI cho phép Account B VÀ Identity Policy (Account B) PHẢI cho phép gọi Key ARN**.
- 📎 Source: `AWS KMS Developer Guide — Allowing users in other accounts to use a KMS key`.

---

### Question 28 — Answer: **A**
- **Why correct:** **AWS KMS Encryption Context** là một tập hợp các cặp key-value chứa dữ liệu bổ sung cần xác thực (**Additional Authenticated Data - AAD**). Dữ liệu này không bị mã hóa bí mật nhưng được liên kết mật mã vào bản mã (ciphertext). Khi giải mã (`Decrypt`), người gọi bắt buộc phải cung cấp chính xác các cặp key-value đã dùng khi mã hóa. Điều này ngăn chặn việc tráo đổi dữ liệu mã hóa giữa các bản ghi của các nhân viên khác nhau.
- **Why the others are wrong:** B sai vì Key Policy quản lý phân quyền người dùng, không gắn chặt theo từng item cụ thể. C sai vì Key Alias chỉ là tên gọi đại diện thân thiện của khóa. D sai vì chữ ký bất đối xứng dùng để xác thực tính toàn vẹn của thông điệp, không phải AAD cho envelope encryption.
- 🧠 **Key point / trap:** Ngăn chặn đánh tráo ciphertext giữa các bản ghi, cung cấp Additional Authenticated Data (AAD) trong KMS → **Encryption Context**.
- 📎 Source: `AWS KMS Developer Guide — Encryption Context`.

---

### Question 29 — Answer: **A**
- **Why correct:** **AWS Secrets Manager Multi-Region Secret Replication** cho phép cấu hình nhân bản một secret từ Region chính (`us-east-1`) sang các Region phụ (`us-west-2`). Secrets Manager sẽ tự động đồng bộ hóa giá trị bí mật, tự động quản lý mã hóa bằng khóa KMS tại Region đích, giúp ứng dụng khi failover sang Region phụ có thể đọc secret ngay lập tức với độ trễ thấp và độ khả dụng cao.
- **Why the others are wrong:** B sai vì viết script tự chế đồng bộ qua cron tiềm ẩn lỗi, không đồng bộ được vòng quay khóa (rotation) và tốn công bảo trì. C sai vì Secret ARN có định dạng gắn liền với Region cụ thể, không thể dùng trực tiếp qua VPC peering mà không sao chép secret. D vi phạm nghiêm trọng nguyên tắc an toàn thông tin khi lưu mật khẩu trong Git.
- 🧠 **Key point / trap:** Đồng bộ bí mật giữa các Region phục vụ Disaster Recovery → **Secrets Manager Multi-Region Replication**.
- 📎 Source: `AWS Secrets Manager User Guide — Replicating secrets across AWS Regions`.

---

### Question 30 — Answer: **A**
- **Why correct:** AWS Systems Manager Parameter Store cung cấp kiểu tham số **`SecureString`** chuyên dùng cho dữ liệu nhạy cảm. Dữ liệu này được tự động mã hóa ở trạng thái nghỉ (at rest) bằng AWS KMS (hoặc khóa mặc định `aws/ssm`, hoặc Customer Managed Key). Khi Lambda lấy giá trị, nó cần cờ `--with-decryption` và quyền gọi `kms:Decrypt`.
- **Why the others are wrong:** B sai vì kiểu `String` lưu trữ dạng văn bản thuần (plaintext), không được mã hóa at-rest. C sai vì `StringList` là danh sách phân tách bằng dấu phẩy ở dạng plaintext, mã hóa base64 không phải là mã hóa an toàn. D sai vì không tồn tại kiểu dữ liệu `SecureBinary` trong Parameter Store.
- 🧠 **Key point / trap:** Lưu dữ liệu nhạy cảm trong Parameter Store → Kiểu **`SecureString`** kết hợp **AWS KMS**.
- 📎 Source: `AWS Systems Manager User Guide — Managing parameter tiers and types`.

---

### Question 31 — Answer: **A**
- **Why correct:** **AWS IAM Policy Simulator** là công cụ chuyên dụng cho phép kiểm thử, gỡ lỗi và thẩm định các chính sách IAM (cả Identity-based lẫn Resource-based). Lập trình viên có thể mô phỏng xem một danh sách các hành động API (như `s3:GetObject`, `dynamodb:PutItem`) sẽ được Chấp thuận (Allowed) hay Từ chối (Denied) dưới các điều kiện ngữ cảnh khác nhau mà không cần thực sự thực thi các hành động đó trên tài nguyên thật.
- **Why the others are wrong:** B sai vì CloudTrail chỉ ghi lại nhật ký các sự kiện API đã xảy ra trong quá khứ, không có khả năng dự đoán hay giả lập chính sách chưa áp dụng. C sai vì AWS Config dùng để đánh giá độ tuân thủ của cấu hình tài nguyên hiện có. D sai vì Amazon Inspector dùng để quét lỗ hổng bảo mật và phơi nhiễm mạng trên EC2/ECR/Lambda.
- 🧠 **Key point / trap:** Kiểm tra tính đúng đắn của chính sách IAM mà không chạm vào tài nguyên thật → **IAM Policy Simulator**.
- 📎 Source: `AWS IAM User Guide — Testing IAM policies with the IAM policy simulator`.

---

### Question 32 — Answer: **A**
- **Why correct:** **Amazon S3 Object Lock** hỗ trợ mô hình WORM (Write Once, Read Many). Ở chế độ **Compliance Mode**:
  - Không một người dùng nào—kể cả tài khoản **root** của tài khoản AWS—có thể ghi đè hoặc xóa phiên bản đối tượng được bảo vệ cho đến khi thời hạn lưu trữ (retention period) kết thúc.
  - Thời hạn lưu trữ không thể bị rút ngắn.
  Ngược lại, ở chế độ **Governance Mode**, các tài khoản có quyền đặc thù (`s3:BypassGovernanceRetention`) vẫn có thể can thiệp hoặc xóa đối tượng.
- **Why the others are wrong:** B sai vì Governance Mode cho phép tài khoản có quyền vượt rào xóa file. C sai vì Lifecycle rules có thể xóa các phiên bản nếu được cấu hình. D sai vì tài khoản root luôn có quyền sửa hoặc xóa bucket policy.
- 🧠 **Key point / trap:** Lưu trữ dữ liệu tuân thủ pháp luật, cấm xóa tuyệt đối (kể cả Root User) → **S3 Object Lock in Compliance Mode**. Cho phép admin xóa khi cần thiết → **Governance Mode**.
- 📎 Source: `Amazon S3 User Guide — Locking objects using S3 Object Lock`.

---

### Question 33 — Answer: **A**
- **Why correct:** Amazon Cognito User Pool Hosted UI cho phép tùy biến giao diện:
  1. Cấu hình **Custom Domain** (ví dụ `auth.example.com`). Yêu cầu bắt buộc là chứng chỉ SSL/TLS từ AWS Certificate Manager (ACM) phải được tạo tại Region **`us-east-1`** (vì hạ tầng phân phối Hosted UI của Cognito dựa trên CloudFront).
  2. Tải lên logo doanh nghiệp và tùy chỉnh mã CSS thông qua bảng điều khiển User Pool.
- **Why the others are wrong:** B sai vì tự dựng web trên EC2 làm tăng chi phí vận hành và rủi ro bảo mật không cần thiết. C sai vì Cognito Hosted UI có hỗ trợ đầy đủ custom branding và custom domain. D sai vì NGINX reverse proxy không phải là giải pháp tiêu chuẩn được khuyến nghị trên AWS.
- 🧠 **Key point / trap:** Custom domain cho Cognito Hosted UI: Chứng chỉ ACM **bắt buộc phải nằm ở `us-east-1`** (tương tự như CloudFront).
- 📎 Source: `Amazon Cognito Developer Guide — Customizing the built-in sign-in web UI`.

---

### Question 34 — Answer: **A**
- **Why correct:** Phân tích chi phí:
  - **AWS Systems Manager Parameter Store (Standard tier):** Hoàn toàn **miễn phí** lưu trữ cho tối đa 10,000 tham số/Region, không mất phí request tiêu chuẩn. Phù hợp tuyệt đối cho 2,500 tham số cấu hình không nhạy cảm.
  - **AWS Secrets Manager:** Chi phí **$0.40/secret/tháng** + $0.05 trên mỗi 10,000 API calls. Chỉ nên dùng cho 10 mật khẩu cơ sở dữ liệu thực sự cần tính năng tự động xoay vòng khóa (automatic rotation) bằng Lambda.
  - Nếu lưu cả 2,510 tham số vào Secrets Manager, công ty sẽ tốn hơn **$1,000 mỗi tháng** một cách lãng phí!
- **Why the others are wrong:** B tốn hơn $1,000/tháng. C và D đòi hỏi thêm code truy vấn phức tạp và chi phí dung lượng/thao tác đọc ghi không tối ưu bằng Parameter Store.
- 🧠 **Key point / trap:** Tối ưu chi phí cấu hình: Dữ liệu cấu hình thông thường / số lượng lớn → **SSM Parameter Store (Free)**. Bí mật cần tự động rotate mật khẩu (DB credentials) → **Secrets Manager**.
- 📎 Source: `AWS Systems Manager Pricing & AWS Secrets Manager Pricing`.

---

### Question 35 — Answer: **A**
- **Why correct:** **IAM Role Session Tags** cho phép các nhà cung cấp định danh bên ngoài (qua SAML 2.0 hoặc OIDC) truyền các thuộc tính người dùng (như `Department`, `CostCenter`, `Project`) vào phiên làm việc tạm thời của AWS STS dưới dạng các session tags. Trong chính sách IAM, ta có thể dùng biến điều kiện `${aws:PrincipalTag/Department}` để triển khai **Kiểm soát truy cập dựa trên thuộc tính (ABAC)**, giúp chỉ một chính sách duy nhất có thể tự động phân quyền chính xác cho hàng nghìn người dùng.
- **Why the others are wrong:** B sai vì Permissions Boundary chỉ quy định trần quyền tối đa mà một IAM entity có thể có, không truyền thuộc tính từ IdP vào session. C sai vì SCPs chỉ áp dụng ở cấp tổ chức AWS Organizations cho tài khoản hoặc OU. D sai vì Access Analyzer dùng để phát hiện tài nguyên bị chia sẻ ra ngoài.
- 🧠 **Key point / trap:** Truyền thuộc tính từ SAML/OIDC IdP vào AWS session để viết chính sách ABAC linh hoạt (`${aws:PrincipalTag/Key}`) → **Role Session Tags**.
- 📎 Source: `AWS IAM User Guide — Passing session tags in AWS STS`.

---

### Question 36 — Answer: **A**
- **Why correct:** API **`kms:ReEncrypt`** cho phép giải mã dữ liệu mã hóa dưới một KMS CMK cũ và lập tức mã hóa lại nó dưới một KMS CMK mới **hoàn toàn bên trong phần cứng bảo mật (HSM) của AWS KMS**. Dữ liệu dạng văn bản gốc (plaintext) không bao giờ bị lộ ra bộ nhớ của ứng dụng hay truyền tải qua đường truyền mạng của caller.
- **Why the others are wrong:** B sai vì gọi `kms:Decrypt` sẽ trả dữ liệu thô (plaintext) về cho máy chủ ứng dụng trước khi mã hóa lại, gây nguy cơ rò rỉ dữ liệu trong bộ nhớ RAM hoặc network sniff. C sai vì `GenerateDataKey` tạo khóa dữ liệu mới, không thực hiện chuyển đổi ciphertext hiện có. D sai vì `UpdateKey` chỉ sửa mô tả hoặc metadata của khóa, không mã hóa lại dữ liệu.
- 🧠 **Key point / trap:** Đổi khóa mã hóa dữ liệu mà không làm lộ plaintext ra ngoài ứng dụng/mạng → **`kms:ReEncrypt`**.
- 📎 Source: `AWS KMS API Reference — ReEncrypt`.

---

### Question 37 — Answer: **A**
- **Why correct:** Để cho phép một Amazon SNS topic ở Account B có thể đẩy tin nhắn vào hàng đợi Amazon SQS ở Account A, cần cấu hình một **SQS Queue Policy** tại Account A:
  - Hành động: `sqs:SendMessage`.
  - Principal: Tài khoản Account B (hoặc `*` kết hợp condition).
  - Điều kiện: `"ArnEquals": {"aws:SourceArn": "arn:aws:sns:region:AccountB:OrderEventsTopic"}`.
  Điều kiện `aws:SourceArn` là bắt buộc theo nguyên tắc Least Privilege để đảm bảo chỉ duy nhất topic được chỉ định mới có thể đẩy tin vào hàng đợi.
- **Why the others are wrong:** B sai vì IAM policy gắn vào root user ở Account A không cấp quyền truy cập từ tài nguyên bên ngoài vào SQS. C sai vì S3 policy chỉ dùng cho S3 bucket. D vi phạm nghiêm trọng an toàn thông tin khi mở public hàng đợi cho toàn thế giới.
- 🧠 **Key point / trap:** Cho phép SNS đẩy vào SQS cross-account: **SQS Queue Policy cấp `sqs:SendMessage` với condition `aws:SourceArn` trỏ về chính xác ARN của SNS Topic**.
- 📎 Source: `Amazon SNS Developer Guide — Sending Amazon SNS messages to an Amazon SQS queue in a different account`.

---

### Question 38 — Answer: **A**
- **Why correct:** Quy trình 4 bước tiêu chuẩn của hàm Lambda xoay vòng khóa bí mật (Rotation Function) trong AWS Secrets Manager:
  1. **`createSecret`:** Tạo ra mật khẩu mới ngẫu nhiên và lưu thành phiên bản có nhãn tạm thời `AWSPENDING`.
  2. **`setSecret`:** Cập nhật thông tin đăng nhập/mật khẩu mới này trực tiếp vào hệ thống đích (ví dụ gửi lệnh `ALTER USER` vào Amazon RDS).
  3. **`testSecret`:** Dùng mật khẩu mới trong nhãn `AWSPENDING` để kiểm tra kết nối thử nghiệm xem đăng nhập vào database có thành công không.
  4. **`finishSecret`:** Đánh dấu thành công bằng cách chuyển nhãn trạng thái `AWSCURRENT` sang phiên bản mới và lưu trữ phiên bản cũ thành `AWSPREVIOUS`.
- **Why the others are wrong:** B, C, D đều là các từ ngữ tự chế không đúng với 4 phương thức trong giao thức xoay vòng chuẩn của AWS Secrets Manager.
- 🧠 **Key point / trap:** 4 bước rotation Lambda của Secrets Manager: **`createSecret` → `setSecret` → `testSecret` → `finishSecret`**.
- 📎 Source: `AWS Secrets Manager User Guide — How rotation works`.

---

### Question 39 — Answer: **A**
- **Why correct:** Trong AWS CodeDeploy dành cho Lambda:
  - Cấu hình **`Linear`** dịch chuyển lưu lượng theo từng bước đều đặn theo thời gian. `LambdaLinear10PercentEvery10Minutes` sẽ chuyển 10% mỗi 10 phút (mất 100 phút để chuyển toàn bộ 100%).
  - Cấu hình **`Canary`** dịch chuyển một phần nhỏ trước, chờ đợi kiểm tra, rồi lập tức chuyển toàn bộ phần còn lại (ví dụ `LambdaCanary10Percent10Minutes` chỉ chuyển 10% đầu tiên, đợi 10 phút, rồi nhảy vọt từ 10% lên 100%).
- **Why the others are wrong:** B sai vì Canary chỉ chia làm 2 đợt (10% rồi 90%), không phải chia đều mỗi 10 phút. C sai vì Canary với chu kỳ 5 phút. D sai vì AllAtOnce chuyển 100% ngay lập tức trong một bước duy nhất.
- 🧠 **Key point / trap:** Chuyển đều đặn `X%` mỗi `Y` phút → **`Linear`**. Chuyển thử `X%`, đợi `Y` phút, rồi chuyển hết `(100 - X)%` còn lại → **`Canary`**.
- 📎 Source: `AWS CodeDeploy User Guide — Deployment configurations on an AWS Lambda compute platform`.

---

### Question 40 — Answer: **A**
- **Why correct:** Trình tự các lifecycle hooks trong triển khai CodeDeploy Blue/Green cho **Amazon ECS**:
  1. `BeforeInstall` → `Install` → `AfterInstall` (khởi tạo bộ tác vụ mới).
  2. `AllowTestTraffic` → **`AfterAllowTestTraffic`** (đây là nơi chạy các bài kiểm thử tự động / integration tests trên Test Listener).
  3. **`BeforeAllowTraffic`** → `AllowTraffic` (chuyển hướng lưu lượng Production Listener sang target group mới) → `AfterAllowTraffic`.
- **Why the others are wrong:** B là trình tự lifecycle hooks dành cho nền tảng EC2 / On-Premises. C là trình tự hooks dành cho nền tảng AWS Lambda (`BeforeAllowTraffic`, `AfterAllowTraffic`). D là thứ tự bị thiếu nhiều bước quan trọng.
- 🧠 **Key point / trap:** CodeDeploy ECS Hooks có bước đặc thù: **`AfterAllowTestTraffic`** (chạy test trên cổng kiểm thử) trước khi bước vào **`BeforeAllowTraffic`** (chuẩn bị chuyển traffic thật).
- 📎 Source: `AWS CodeDeploy User Guide — Lifecycle hooks for an Amazon ECS deployment`.

---

### Question 41 — Answer: **A**
- **Why correct:** **CloudFormation Stack Policy** là một tài liệu JSON định nghĩa các hành động cập nhật được phép hoặc bị cấm trên các tài nguyên cụ thể trong stack. Theo mặc định, tất cả các tài nguyên đều có thể bị cập nhật trong quá trình update stack. Bằng cách thiết lập một Stack Policy với chỉ thị `Deny` cho các hành động `Update:Replace` và `Update:Delete` nhắm vào logical ID `ProductionDatabase`, lập trình viên có thể thoải mái sửa đổi các tài nguyên khác mà không bao giờ sợ sơ suất làm xóa hoặc thay thế database.
- **Why the others are wrong:** B sai vì Permissions Boundary giới hạn quyền IAM của user, nhưng nếu user có quyền gọi `UpdateStack` thì CloudFormation vẫn có thể thay thế DB nếu không có Stack Policy chặn. C và D không can thiệp được vào hành vi thay thế tài nguyên bên trong một stack CloudFormation.
- 🧠 **Key point / trap:** Ngăn chặn vô tình xóa hoặc thay thế tài nguyên quan trọng trong quá trình cập nhật CloudFormation stack → **CloudFormation Stack Policy**.
- 📎 Source: `AWS CloudFormation User Guide — Preventing updates to stack resources`.

---

### Question 42 — Answer: **A**
- **Why correct:** Thuộc tính **`DeletionPolicy: Snapshot`** trong CloudFormation quy định rằng khi stack bị xóa hoặc khi tài nguyên bị loại bỏ khỏi template, AWS sẽ tự động chụp một bản sao lưu (snapshot) cuối cùng trước khi tài nguyên đó bị hủy. Tính năng này được hỗ trợ trên các dịch vụ lưu trữ trạng thái quan trọng như Amazon DynamoDB, Amazon RDS, Amazon Redshift, Amazon ElastiCache.
- **Why the others are wrong:** B sai vì `DeletionPolicy: Retain` sẽ giữ nguyên tài nguyên đang chạy chứ không chụp snapshot. C sai vì `DeletionPolicy: Delete` là hành vi mặc định (xóa hẳn không lưu vết). D sai vì `UpdatePolicy` dùng để cấu hình cập nhật cuốn chiếu (rolling updates) cho ASG, không phải xử lý khi xóa tài nguyên.
- 🧠 **Key point / trap:** Tự động tạo snapshot sao lưu trước khi xóa tài nguyên trong CloudFormation → **`DeletionPolicy: Snapshot`**. Giữ nguyên tài nguyên → **`DeletionPolicy: Retain`**.
- 📎 Source: `AWS CloudFormation User Guide — DeletionPolicy attribute`.

---

### Question 43 — Answer: **A**
- **Why correct:** Lệnh **`sam local start-api`** khởi chạy một máy chủ HTTP cục bộ trên máy tính lập trình viên, giả lập môi trường Amazon API Gateway và tự động chuyển các HTTP request tới các container Docker chạy mã nguồn Lambda tương ứng. Lệnh này hỗ trợ hot-reloading (sửa code thấy kết quả ngay).
- **Why the others are wrong:** B sai vì `sam local invoke` dùng để thực thi trực tiếp một hàm đơn lẻ với một file sự kiện giả lập (event JSON), không khởi tạo web server HTTP để gửi request từ browser hay Postman. C sai vì `sam deploy --dry-run` không dùng để chạy thử nghiệm API cục bộ. D sai vì không có lệnh chuẩn `sam test`.
- 🧠 **Key point / trap:** Khởi chạy máy chủ HTTP API Gateway cục bộ bằng SAM CLI → **`sam local start-api`**.
- 📎 Source: `AWS Serverless Application Model Developer Guide — sam local start-api`.

---

### Question 44 — Answer: **A**
- **Why correct:** AWS Elastic Beanstalk sử dụng thư mục **`.ebextensions`** đặt ở thư mục gốc (root) của gói mã nguồn ứng dụng để chứa các tệp cấu hình nâng cao. Các tệp này bắt buộc phải có phần mở rộng là **`.config`** (ví dụ `.ebextensions/packages.config`) và được viết theo định dạng YAML hoặc JSON để cài đặt phần mềm Linux, cấu hình file hệ thống, hay thiết lập biến môi trường.
- **Why the others are wrong:** B sai vì đặt trong `src/beanstalk.json` sẽ không được Elastic Beanstalk nhận diện. C sai vì `appspec.yml` là tệp điều khiển của dịch vụ AWS CodeDeploy. D sai vì `buildspec.yml` là tệp cấu hình quy trình build của AWS CodeBuild.
- 🧠 **Key point / trap:** Cấu hình tùy biến sâu cho Elastic Beanstalk EC2 instances → Thư mục **`.ebextensions/*.config`** ở root của source bundle.
- 📎 Source: `AWS Elastic Beanstalk Developer Guide — Advanced environment customization with configuration files (.ebextensions)`.

---

### Question 45 — Answer: **A**
- **Why correct:** Trên các nền tảng Elastic Beanstalk sử dụng Amazon Linux 2 trở lên, tệp **`Procfile`** đặt tại thư mục gốc của mã nguồn ứng dụng được sử dụng để định nghĩa các tiến trình cần chạy đồng thời (ví dụ tiến trình web server phục vụ traffic người dùng và tiến trình background worker xử lý tác vụ ngầm từ SQS). Cú pháp chuẩn có dạng: `web: <command>` và `<process_name>: <command>`.
- **Why the others are wrong:** B sai vì `appspec.yml` là của CodeDeploy. C sai vì `docker-compose.yml` chỉ dùng cho kiến trúc Multi-container Docker, không phải chuẩn Procfile của Node.js Beanstalk. D sai vì chỉ khai báo trong `package.json` thì Beanstalk chỉ chạy được một lệnh `npm start` mặc định, không quản lý được đa tiến trình độc lập.
- 🧠 **Key point / trap:** Khởi chạy nhiều tiến trình (web + background worker) trong Elastic Beanstalk Amazon Linux 2 → Tệp **`Procfile`**.
- 📎 Source: `AWS Elastic Beanstalk Developer Guide — Configuring your application with a Procfile`.

---

### Question 46 — Answer: **A**
- **Why correct:** Các tham số triển khai cuốn chiếu (Rolling Update) trong Amazon ECS:
  - **`minimumHealthyPercent`:** Ngưỡng năng lực tối thiểu bắt buộc phải duy trì tính theo % số lượng task mong muốn (desired count = 4). Yêu cầu không bao giờ được giảm dưới 4 task (100% dung lượng) → `minimumHealthyPercent = 100`.
  - **`maximumPercent`:** Ngưỡng năng lực tối đa được phép vượt lên trong quá trình cập nhật. Yêu cầu không được vượt quá 6 task (`6 / 4 = 150%`) → `maximumPercent = 150`.
  - Khi đó, ECS sẽ khởi tạo tối đa 2 task mới (tổng 6 task), chờ chúng khỏe mạnh (healthy) rồi mới tắt 2 task cũ, luôn đảm bảo ít nhất 4 task hoạt động.
- **Why the others are wrong:** B sai vì 50% cho phép ECS tắt 2 task cũ trước khi tạo task mới, gây giảm dung lượng xuống còn 2 task. C sai vì 0% cho phép tắt sạch toàn bộ hệ thống. D sai vì `maximumPercent = 100` kết hợp `minimum = 100` sẽ khiến ECS không thể khởi chạy thêm task mới nào và quá trình deployment sẽ bị kẹt.
- 🧠 **Key point / trap:** ECS Rolling Update: Giữ nguyên năng lực tối thiểu `N` task → **`minimumHealthyPercent = 100`**. Giới hạn tối đa không vượt quá `M` task → **`maximumPercent = (M / N) * 100`**.
- 📎 Source: `Amazon ECS Developer Guide — Rolling update parameters`.

---

### Question 47 — Answer: **A**
- **Why correct:** Trong AWS CodePipeline, các artifact trung gian (mã nguồn, file build) được lưu trữ trong một Amazon S3 bucket đóng vai trò là Artifact Store. Để mã hóa các tệp này bằng Customer Managed Key (CMK), ta cấu hình tham số `encryptionKey` với ARN của khóa KMS trong định nghĩa của Pipeline, đồng thời đảm bảo Service Role của CodePipeline và CodeBuild có quyền `kms:GenerateDataKey` và `kms:Decrypt` trên khóa đó.
- **Why the others are wrong:** B vi phạm an ninh nghiêm trọng khi nhúng khóa bí mật vào mã nguồn. C vi phạm an ninh khi đưa thông tin nhạy cảm lên Git. D sai vì CodePipeline hoàn toàn hỗ trợ mã hóa S3 artifact store bằng KMS CMK tùy chỉnh.
- 🧠 **Key point / trap:** Mã hóa CodePipeline Artifact Store bằng KMS CMK tùy biến → Cấu hình **KMS Key ARN trong Artifact Store S3 bucket** của pipeline và cấp quyền IAM cho pipeline role.
- 📎 Source: `AWS CodePipeline User Guide — Configure server-side encryption for artifacts stored in Amazon S3 for CodePipeline`.

---

### Question 48 — Answer: **A**
- **Why correct:** **CloudFormation Nested Stacks** cho phép lập trình viên chia nhỏ một kiến trúc hạ tầng khổng lồ thành các mẫu template chuyên biệt, có tính tái sử dụng cao (như template cho mạng VPC, template cho database, template cho bảo mật). Mẫu gốc (Root Stack) sẽ tham chiếu tới các template con lưu trên Amazon S3 thông qua kiểu tài nguyên `AWS::CloudFormation::Stack`. Đây là giải pháp tiêu chuẩn duy nhất để vượt qua giới hạn cứng **500 tài nguyên** trên một template của CloudFormation.
- **Why the others are wrong:** B sai vì giới hạn 500 tài nguyên/template là hạn mức cứng của dịch vụ CloudFormation, không thể yêu cầu tăng quota. C sai vì viết shell script làm mất đi hoàn toàn khả năng theo dõi trạng thái, rollback và drift detection tự động của Infrastructure as Code. D sai vì DynamoDB không giải quyết được việc định nghĩa hạ tầng CloudFormation.
- 🧠 **Key point / trap:** Vượt quá giới hạn 500 tài nguyên CloudFormation, mô đun hóa hạ tầng → **CloudFormation Nested Stacks (`AWS::CloudFormation::Stack`)**.
- 📎 Source: `AWS CloudFormation User Guide — Working with nested stacks`.

---

### Question 49 — Answer: **A**
- **Why correct:** Bộ công cụ trợ giúp CloudFormation Helper Scripts:
  1. Khai báo các gói cài đặt, tệp tin và lệnh thực thi trong phần metadata **`AWS::CloudFormation::Init`**.
  2. Trong User Data của EC2, gọi tiện ích **`cfn-init`** để đọc và thực thi cấu hình từ metadata.
  3. Sau khi cài đặt xong, gọi tiện ích **`cfn-signal`** gửi tín hiệu mã trạng thái (exit code 0 nếu thành công) về cho CloudFormation.
  4. Trên tài nguyên EC2 trong template, khai báo **`CreationPolicy`** để CloudFormation tạm dừng và chờ nhận đủ tín hiệu thành công từ `cfn-signal` trước khi chuyển trạng thái stack sang `CREATE_COMPLETE`.
- **Why the others are wrong:** B sai vì `cfn-hup` là tiến trình chạy nền để phát hiện và áp dụng các cập nhật metadata sau này, không dùng để gửi tín hiệu khởi tạo ban đầu. C sai vì `sam build` dành cho serverless. D sai vì `aws deploy create-deployment` là lệnh kích hoạt CodeDeploy.
- 🧠 **Key point / trap:** Tự động cài đặt phần mềm và báo hiệu CloudFormation chờ EC2 sẵn sàng: **`AWS::CloudFormation::Init` + `cfn-init` + `cfn-signal` + `CreationPolicy`**.
- 📎 Source: `AWS CloudFormation User Guide — CloudFormation helper scripts reference`.

---

### Question 50 — Answer: **A**
- **Why correct:** Khi môi trường biên dịch trong AWS CodeBuild đòi hỏi các công cụ thử nghiệm chuyên biệt hoặc trình biên dịch phiên bản cũ không có sẵn trong các container chuẩn do AWS quản lý, giải pháp tối ưu là tự đóng gói một **Custom Docker Image**. Lập trình viên build image, đẩy lên kho lưu trữ **Amazon ECR** (hoặc Docker Hub), và cấu hình CodeBuild project sử dụng image tùy chỉnh này làm build environment.
- **Why the others are wrong:** B sai vì yêu cầu AWS Support thêm trình biên dịch cũ vào image tiêu chuẩn là bất khả thi và không thực tế. C sai vì cài đặt lại trình biên dịch trong `post_build` thì đã quá muộn (code cần biên dịch ở phase `build`), hơn nữa việc cài đặt lặp đi lặp lại trong buildspec làm kéo dài thời gian build lãng phí. D sai vì CodeBuild hoàn toàn hỗ trợ custom Docker image từ ECR.
- 🧠 **Key point / trap:** CodeBuild cần phần mềm/trình biên dịch tùy biến hoặc legacy → Đóng gói **Custom Docker Image đẩy lên Amazon ECR**.
- 📎 Source: `AWS CodeBuild User Guide — Docker images provided by CodeBuild & Custom Docker images`.

---

### Question 51 — Answer: **A**
- **Why correct:** Trong AWS CodeDeploy, bạn có thể tạo cấu hình triển khai tùy chỉnh (**Custom Deployment Configuration**) với tham số **`minimumHealthyHosts`**:
  - Khi có 20 instances và muốn triển khai theo từng đợt 5 instances (luôn duy trì tối thiểu 15 instances khỏe mạnh phục vụ khách), ta cấu hình `minimumHealthyHosts` là kiểu số lượng **`HOST_COUNT: 15`** hoặc phần trăm **`FLEET_PERCENT: 75%`** (`15 / 20 = 75%`). Nếu số lượng instance khỏe mạnh tụt xuống dưới 15 (tức có hơn 2 máy bị lỗi trong đợt triển khai 5 máy), CodeDeploy sẽ lập tức dừng đợt triển khai.
- **Why the others are wrong:** B sai vì viết vòng lặp bash thủ công thiếu các cơ chế kiểm tra sức khỏe tự động, không có khả năng rollback tự động và không thể kiểm soát tập trung. C sai vì Elastic Beanstalk quản lý triển khai ứng dụng web trọn gói, không phải công cụ để cấu hình nhóm máy chủ CodeDeploy độc lập. D sai vì gán thủ công từng bước duyệt cho 20 máy là phi lý và không tự động hóa.
- 🧠 **Key point / trap:** Kiểm soát số lượng máy chủ cập nhật cùng lúc trong CodeDeploy → Tạo Custom Deployment Configuration với **`minimumHealthyHosts` (`HOST_COUNT` hoặc `FLEET_PERCENT`)**.
- 📎 Source: `AWS CodeDeploy User Guide — Working with deployment configurations`.

---

### Question 52 — Answer: **A**
- **Why correct:** AWS CodePipeline hỗ trợ chính thức 6 nhóm danh mục hành động (Action Categories) trong các stage của pipeline:
  1. **`Source`:** Lấy mã nguồn (CodeCommit, S3, GitHub, Bitbucket, ECR).
  2. **`Build`:** Biên dịch và kiểm thử mã nguồn (CodeBuild, Jenkins).
  3. **`Test`:** Chạy các bộ test tự động (CodeBuild, Device Farm, bên thứ ba).
  4. **`Deploy`:** Triển khai sản phẩm (CodeDeploy, CloudFormation, ECS, S3, Elastic Beanstalk).
  5. **`Approval`:** Phê duyệt thủ công qua email/SNS trước khi bước sang giai đoạn tiếp theo.
  6. **`Invoke`:** Kích hoạt các hàm không máy chủ (AWS Lambda, AWS Step Functions).
- **Why the others are wrong:** B, C, D đều chứa các tên hành động không tồn tại trong đặc tả danh mục hành động chính thức của AWS CodePipeline.
- 🧠 **Key point / trap:** 6 action types chính thức của CodePipeline: **Source, Build, Test, Deploy, Approval, Invoke**.
- 📎 Source: `AWS CodePipeline User Guide — Valid action types in CodePipeline`.

---

### Question 53 — Answer: **A**
- **Why correct:** **AWS SAM Policy Templates** cung cấp một danh mục các chính sách IAM được đóng gói sẵn theo nguyên tắc đặc quyền tối thiểu (least privilege). Thay vì phải viết hàng chục dòng JSON IAM phức tạp, lập trình viên chỉ cần khai báo một dòng ngắn gọn như:
  ```yaml
  Policies:
    - DynamoDBCrudPolicy:
        TableName: !Ref MyTable
  ```
  SAM sẽ tự động chuyển đổi nó thành chính sách IAM đầy đủ với các quyền `dynamodb:GetItem`, `PutItem`, `UpdateItem`, `DeleteItem` chỉ trên bảng đó.
- **Why the others are wrong:** B sai vì Permissions Boundary giới hạn quyền tối đa chứ không cấp quyền thao tác dữ liệu. C sai vì SCPs áp dụng ở cấp độ tổ chức AWS Organizations. D sai vì CloudFormation Metadata chỉ lưu thông tin cấu hình, không cấp quyền IAM thực thi.
- 🧠 **Key point / trap:** Cấp quyền nhanh gọn, chuẩn least privilege cho Lambda trong AWS SAM → **SAM Policy Templates** (ví dụ `DynamoDBCrudPolicy`, `S3ReadPolicy`, `SQSPollerPolicy`).
- 📎 Source: `AWS Serverless Application Model Developer Guide — SAM policy templates`.

---

### Question 54 — Answer: **A**
- **Why correct:** CloudFormation tự động xác định thứ tự tạo tài nguyên khi có sự phụ thuộc tường minh thông qua các hàm nội tại như `!Ref` hoặc `!GetAtt`. Tuy nhiên, trong trường hợp một EC2 instance cần gửi lưu lượng ra internet ngay trong quá trình chạy script User Data, nó ngầm phụ thuộc vào việc Internet Gateway đã được gắn thành công vào VPC (`AWS::VPCGatewayAttachment`). Vì giữa EC2 và VPCGatewayAttachment không có tham chiếu `!Ref` trực tiếp, ta bắt buộc phải khai báo thuộc tính **`DependsOn: VPCGatewayAttachment`** trên tài nguyên EC2 để ép CloudFormation phải chờ gắn xong gateway mới khởi tạo instance.
- **Why the others are wrong:** B sai vì tham chiếu Security Group không chứng minh được Internet Gateway đã gắn vào VPC thành công. C sai vì WaitCondition dùng để chờ tín hiệu từ instance, không giải quyết được thứ tự phụ thuộc tài nguyên VPC. D sai vì chia tài khoản mạng là sai kiến trúc.
- 🧠 **Key point / trap:** Ép thứ tự khởi tạo tài nguyên trong CloudFormation khi không có `!Ref` hay `!GetAtt` trực tiếp → Dùng thuộc tính **`DependsOn`**.
- 📎 Source: `AWS CloudFormation User Guide — DependsOn attribute`.

---

### Question 55 — Answer: **A**
- **Why correct:** Cú pháp truy vấn của **CloudWatch Logs Insights** sử dụng các toán tử đường ống (pipe `|`) đặc thù:
  ```sql
  fields @timestamp, @message, durationMs
  | filter durationMs > 0
  | sort durationMs desc
  | limit 20
  ```
  Câu lệnh này lọc ra các log có `durationMs > 0`, sắp xếp giảm dần theo thời lượng xử lý, và lấy 20 bản ghi chậm nhất.
- **Why the others are wrong:** B sai vì Logs Insights không hỗ trợ cú pháp SQL tiêu chuẩn (`SELECT ... FROM log_group`). C sai vì Logs Insights không phải là shell terminal Linux để chạy lệnh `grep` hay `head`. D sai vì gom nhóm theo thời gian `bin(5m)` chỉ đếm số lượng, không trả về danh sách 20 request cụ thể chạy chậm nhất.
- 🧠 **Key point / trap:** Cú pháp CloudWatch Logs Insights: Sử dụng cấu trúc pipeline nối nhau bằng dấu gạch đứng: **`fields ... | filter ... | sort ... desc | limit 20`**.
- 📎 Source: `Amazon CloudWatch Logs User Guide — CloudWatch Logs Insights query syntax`.

---

### Question 56 — Answer: **A**
- **Why correct:** Thuộc tính **`TreatMissingData`** trong CloudWatch Alarms cho phép xác định cách thức cảnh báo phản ứng khi không có điểm dữ liệu nào được phát ra (ví dụ các dịch vụ Lambda không có traffic vào ban đêm):
  - **`notBreaching`:** Coi việc thiếu dữ liệu là bình thường (nằm trong ngưỡng an toàn). Điều này ngăn chặn cảnh báo rơi vào trạng thái `ALARM` hoặc `INSUFFICIENT_DATA` gây báo động giả lúc nửa đêm.
  - **`breaching`:** Coi việc thiếu dữ liệu là vi phạm (chuyển sang `ALARM`).
  - **`ignore`:** Giữ nguyên trạng thái cảnh báo hiện tại.
  - **`missing`:** Chuyển trạng thái sang `INSUFFICIENT_DATA` (hành vi mặc định).
- **Why the others are wrong:** B sai vì `breaching` sẽ lập tức kích hoạt báo động khi không có khách truy cập. C sai vì tăng thời gian đánh giá lên 24 giờ sẽ làm tê liệt khả năng phát hiện sự cố nhanh chóng. D sai vì duy trì một máy ảo EC2 chỉ để gửi metric số 0 làm phá vỡ mô hình serverless và lãng phí tiền bạc.
- 🧠 **Key point / trap:** Tránh báo động giả cho CloudWatch Alarm khi dịch vụ serverless không có lưu lượng truy cập → **`TreatMissingData: notBreaching`**.
- 📎 Source: `Amazon CloudWatch User Guide — Configuring how CloudWatch alarms treat missing data`.

---

### Question 57 — Answer: **A**
- **Why correct:** Mức độ sử dụng bộ nhớ RAM (Memory Utilization), dung lượng swap, và không gian đĩa trống là các chỉ số ở **cấp độ hệ điều hành bên trong máy ảo (OS-level metrics)**. Trình quản lý máy ảo (hypervisor) của AWS bên ngoài chỉ có thể nhìn thấy mức tiêu thụ CPU, lượng I/O đĩa đọc/ghi vật lý, và lưu lượng mạng vào/ra. Để thu thập và đẩy chỉ số `mem_used_percent` lên CloudWatch, lập trình viên bắt buộc phải cài đặt và cấu hình **Unified CloudWatch Agent** bên trong máy chủ EC2.
- **Why the others are wrong:** B sai vì Detailed Monitoring chỉ tăng tần suất thu thập các chỉ số mặc định từ 5 phút xuống 1 phút, không có khả năng thâm nhập vào HĐH để đọc RAM. C sai vì mọi loại EC2 instance đều hỗ trợ CloudWatch Agent thu thập RAM. D sai vì CloudTrail chỉ ghi log các lệnh gọi API quản trị, không đo lường tài nguyên phần cứng.
- 🧠 **Key point / trap:** EC2 thiếu metric Memory/RAM và Disk Space → Bắt buộc cài đặt **Unified CloudWatch Agent**. Detailed Monitoring **KHÔNG** cung cấp metric Memory.
- 📎 Source: `Amazon CloudWatch User Guide — Collecting metrics and logs from Amazon EC2 instances with the CloudWatch Agent`.

---

### Question 58 — Answer: **A**
- **Why correct:** Trong AWS X-Ray:
  - Một **Segment** đại diện cho tài nguyên máy tính phục vụ request (ví dụ toàn bộ hàm Lambda hoặc máy chủ web).
  - Một **Subsegment** đại diện cho một khối công việc chi tiết bên trong mã nguồn ứng dụng (ví dụ một phép tính toán phức tạp, một truy vấn database, hoặc một lệnh gọi API downstream). Bằng cách bao bọc hàm tính toán bằng một custom subsegment (thông qua `AWSXRay.captureFunc()` hoặc `segment.addNewSubsegment()`), thời gian chạy 3 giây của phép tính sẽ hiển thị thành một thanh tiến trình độc lập và rõ ràng trên dòng thời gian (timeline trace) của X-Ray.
- **Why the others are wrong:** B sai vì Annotation là các cặp key-value được lập chỉ mục dùng để lọc và tìm kiếm trace trong search bar, không tạo ra các khối trực quan trên đồ thị thời gian. C sai vì Metadata lưu dữ liệu debug tùy ý không lập chỉ mục. D sai vì `PutMetricData` gửi dữ liệu sang CloudWatch Metrics, không tác động đến trace map của X-Ray.
- 🧠 **Key point / trap:** Muốn đo đạc và tách riêng thời gian chạy của một đoạn mã nội bộ trên biểu đồ X-Ray → Tạo **Custom Subsegment**.
- 📎 Source: `AWS X-Ray Developer Guide — Generating subsegments with the AWS X-Ray SDK`.

---

### Question 59 — Answer: **A**
- **Why correct:** Trên môi trường **Amazon ECS với AWS Fargate Launch Type**, người dùng không có quyền truy cập vào máy chủ EC2 bên dưới để cài đặt phần mềm hệ thống. Mẫu thiết kế chuẩn mực (standard pattern) của AWS để chạy AWS X-Ray Daemon trên Fargate là khai báo nó như một **Sidecar Container** (`amazon/aws-xray-daemon`) chạy song song trong cùng một Task Definition với container ứng dụng, chia sẻ chung mạng localhost và lắng nghe các gói tin UDP trên cổng `2000`.
- **Why the others are wrong:** B sai vì nhồi nhét daemon vào chung Dockerfile của ứng dụng vi phạm nguyên tắc "một container - một tiến trình" và làm khó quản lý log. C sai vì Fargate hỗ trợ X-Ray rất tốt thông qua mô hình sidecar container. D sai vì định tuyến UDP qua VPC Peering tới một EC2 khác gây tăng độ trễ và tốn chi phí truyền dữ liệu mạng.
- 🧠 **Key point / trap:** Chạy X-Ray Daemon trên Amazon ECS Fargate → Triển khai dưới dạng **Sidecar Container trong cùng ECS Task Definition (port 2000/udp)**.
- 📎 Source: `AWS X-Ray Developer Guide — Running the X-Ray daemon on Amazon ECS`.

---

### Question 60 — Answer: **A**
- **Why correct:** Trong Amazon Kinesis Data Streams, một **Shard Iterator** có vòng đời tối đa là **300 giây (5 phút)**. Nếu ứng dụng tiêu thụ (consumer) mất nhiều hơn 5 phút để xử lý một lô dữ liệu (batch) trước khi gọi lệnh `GetRecords` tiếp theo, iterator đó sẽ bị hết hạn và Kinesis sẽ ném ra ngoại lệ **`ExpiredIteratorException`**. Cách khắc phục là giảm dung lượng lô dữ liệu (`Limit` parameter) để việc xử lý hoàn tất dưới 5 phút, hoặc bắt ngoại lệ này để gọi `GetShardIterator` lấy iterator mới bắt đầu từ `SequenceNumber` của bản ghi cuối cùng đã xử lý thành công.
- **Why the others are wrong:** B sai vì Kinesis Shard không bị xóa vì lý do này; dữ liệu được lưu từ 24h đến 365 ngày. C sai vì IAM role session timeout mặc định thường là 1 giờ, không phải 5 phút. D sai vì Kinesis hỗ trợ batch lên tới 10,000 records hoặc 10 MB.
- 🧠 **Key point / trap:** Lỗi `ExpiredIteratorException` trong Kinesis Consumer → Do thời gian xử lý lô vượt quá **300 giây (5 phút)**. Khắc phục: Giảm kích thước batch hoặc xin lại iterator mới.
- 📎 Source: `Amazon Kinesis Data Streams Developer Guide — Troubleshooting Amazon Kinesis Data Streams Consumers`.

---

### Question 61 — Answer: **A**
- **Why correct:** Sự khác biệt cốt lõi giữa hai chế độ ElastiCache for Redis:
  - **Cluster Mode Disabled:** Toàn bộ cụm chỉ có duy nhất **1 Shard**. Mọi thao tác ghi (Write) bắt buộc phải đi vào duy nhất 1 Primary node. Các node replica chỉ phục vụ đọc (Read). Do đó, chế độ này **không thể mở rộng dung lượng ghi (Write Capacity)** theo chiều ngang.
  - **Cluster Mode Enabled:** Dữ liệu được băm (hash slots) và phân vùng trên nhiều Shard độc lập (tối đa 500 shards). Mỗi shard có một Primary node riêng xử lý việc ghi, cho phép mở rộng quy mô năng lực ghi theo chiều ngang không giới hạn.
- **Why the others are wrong:** B sai vì thêm read replica chỉ tăng thông lượng đọc, hoàn toàn không hỗ trợ chia tải ghi cho Primary node. C sai vì Memcached là kiến trúc thuần cache in-memory đa luồng nhưng thiếu các cấu trúc dữ liệu nâng cao và tính năng bền vững của Redis. D sai vì Multi-AZ chỉ đảm bảo tính sẵn sàng cao khi node chính sập, không tăng năng lực ghi.
- 🧠 **Key point / trap:** Mở rộng năng lực ghi (Scale Write Throughput) cho Redis → Bắt buộc chuyển sang **Redis Cluster Mode Enabled** (nhiều shards với nhiều primary nodes).
- 📎 Source: `Amazon ElastiCache for Redis User Guide — Scaling ElastiCache for Redis Clusters`.

---

### Question 62 — Answer: **A**
- **Why correct:** Kiến trúc Serverless với AWS Lambda có khả năng scale đồng thời lên hàng nghìn hàm trong vài giây. Mỗi hàm Lambda thường mở một kết nối TCP riêng biệt tới cơ sở dữ liệu quan hệ, dễ dàng làm cạn kiệt số lượng kết nối tối đa (`max_connections`) của PostgreSQL/MySQL. **Amazon RDS Proxy** được thiết kế chuyên biệt để đặt giữa Lambda và Aurora/RDS, thực hiện dồn và tái sử dụng kết nối (**Connection Pooling & Multiplexing**), bảo vệ bộ nhớ và CPU của database, loại bỏ hoàn toàn các lỗi cạn kiệt kết nối.
- **Why the others are wrong:** B sai vì nâng cấp cấu hình instance class vô cùng tốn kém và chỉ dời vấn đề đi một khoảng ngắn chứ không giải quyết tận gốc hiện tượng bão kết nối từ Lambda. C sai vì bóp nghẹt concurrency của Lambda xuống 10 sẽ làm sụp đổ toàn bộ hiệu năng và gây nghẽn ứng dụng. D sai vì S3 không thể thay thế một cơ sở dữ liệu quan hệ ACID.
- 🧠 **Key point / trap:** Lambda quy mô lớn làm cạn kiệt kết nối cơ sở dữ liệu quan hệ (RDS/Aurora) → Giải pháp số 1 là **Amazon RDS Proxy**.
- 📎 Source: `Amazon RDS User Guide — Managing connections with Amazon RDS Proxy`.

---

### Question 63 — Answer: **A**
- **Why correct:** Khi Amazon CloudWatch Logs đẩy log sang AWS Lambda thông qua Subscription Filter, payload dữ liệu gửi trong thuộc tính `event.awslogs.data` được định dạng là một chuỗi **Base64** đại diện cho một luồng byte nhị phân đã được **nén bằng thuật toán GZIP**. Do đó, bên trong code của hàm Lambda, lập trình viên bắt buộc phải thực hiện 3 bước:
  1. Giải mã Base64 sang Buffer nhị phân (`Buffer.from(event.awslogs.data, 'base64')`).
  2. Giải nén luồng nhị phân bằng GZIP (`zlib.gunzipSync(buffer)`).
  3. Chuyển chuỗi UTF-8 thu được sang đối tượng JSON (`JSON.parse(result)`).
- **Why the others are wrong:** B sai vì Subscription Filter luôn gửi dữ liệu nén gzip + base64 theo thiết kế của AWS để tiết kiệm băng thông mạng. C sai vì `PutLogEvents` là API đẩy log lên CloudWatch, không dùng để giải mã sự kiện nhận về. D sai vì ép kiểu nhị phân trực tiếp sang Map sẽ gây crash chương trình.
- 🧠 **Key point / trap:** Xử lý CloudWatch Logs Subscription Filter trong Lambda: Bắt buộc **Base64 decode → GZIP decompress → JSON parse**.
- 📎 Source: `Amazon CloudWatch Logs User Guide — Using CloudWatch Logs subscription filters with AWS Lambda`.

---

### Question 64 — Answer: **A**
- **Why correct:** Khi tính năng caching của API Gateway Stage được bật tùy chọn **"Require authorization"** cho việc hủy bộ nhớ đệm (cache invalidation), API Gateway sẽ kiểm tra quyền IAM của client gửi request với header `Cache-Control: max-age=0`. Để client có thể ép API Gateway bỏ qua cache và lấy dữ liệu mới từ backend, danh tính IAM của client phải được cấp quyền **`execute-api:InvalidateCache`** trên ARN của API Gateway stage/method đó.
- **Why the others are wrong:** B sai vì đổi sang POST chỉ bỏ qua cache của method POST, không giải quyết được việc xóa cache cho method GET. C sai vì xóa và tạo lại stage làm gián đoạn hệ thống và mất hết cấu hình đang chạy. D sai vì tăng kích thước cache không cấp quyền xác thực cho client.
- 🧠 **Key point / trap:** Hủy cache API Gateway với `Cache-Control: max-age=0` khi có bật xác thực → Cấp quyền IAM **`execute-api:InvalidateCache`**.
- 📎 Source: `Amazon API Gateway Developer Guide — Invalidate an API Gateway method cache`.

---

### Question 65 — Answer: **A**
- **Why correct:** Trong tiêu chuẩn HTTP Caching (RFC 7234):
  - **`s-maxage` (Shared Max-Age):** Chỉ định thị riêng cho các máy chủ proxy công cộng và mạng CDN (như Amazon CloudFront). Thiết lập `s-maxage=3600` thông báo cho CloudFront lưu trữ bản sao phản hồi tại các Edge Location trong **1 giờ**.
  - **`max-age`:** Chỉ định thị thời gian bộ nhớ đệm cho các trình duyệt web riêng lẻ của người dùng cuối. Thiết lập `max-age=60` buộc trình duyệt phải kiểm tra lại với CloudFront sau **1 phút**.
  - Do đó directive chính xác là: `Cache-Control: max-age=60, s-maxage=3600`.
- **Why the others are wrong:** B sai vì đảo ngược giá trị (khiến browser lưu 1 giờ còn CloudFront chỉ lưu 1 phút, làm tăng tải origin). C sai vì `no-cache, no-store` cấm hoàn toàn việc cache trên cả browser lẫn CDN. D sai vì `ttl=3600` không phải là cú pháp hợp lệ của HTTP header `Cache-Control`.
- 🧠 **Key point / trap:** HTTP Cache-Control: **`s-maxage`** dành cho CDN / Shared Proxy (CloudFront); **`max-age`** dành cho Private Browser Cache.
- 📎 Source: `Amazon CloudFront Developer Guide — Managing how long content stays in the cache (expiration)`.
