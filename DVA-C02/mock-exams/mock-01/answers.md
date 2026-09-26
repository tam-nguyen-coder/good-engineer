# ✅ Answers & Explanations — DVA-C02 Mock Exam 01

> Chỉ mở sau khi đã hoàn thành toàn bộ 65 câu trong [questions.md](questions.md) với đồng hồ bấm giờ 130 phút.
> Back to [mock index](../README.md) · [master plan](../../DVA-C02-STUDY-PLAN.md)

**Answer key:** 1-A · 2-A · 3-B · 4-A · 5-C · 6-C · 7-AB · 8-A · 9-A · 10-A · 11-A · 12-A · 13-A · 14-AB · 15-A · 16-A · 17-A · 18-AB · 19-A · 20-A · 21-A · 22-A · 23-A · 24-A · 25-A · 26-A · 27-A · 28-A · 29-A · 30-A · 31-A · 32-A · 33-A · 34-A · 35-A · 36-A · 37-A · 38-A · 39-A · 40-A · 41-A · 42-A · 43-A · 44-A · 45-A · 46-A · 47-A · 48-A · 49-A · 50-A · 51-A · 52-A · 53-A · 54-A · 55-A · 56-A · 57-A · 58-A · 59-A · 60-AB · 61-A · 62-A · 63-A · 64-A · 65-AB

> 📌 Với câu `Multi`, chỉ tính **đúng** khi chọn đủ và đúng tất cả các phương án — không có điểm một phần.

---

## 📊 Bảng chấm điểm theo Domain

| Domain | Tỉ trọng | Câu số | Số đúng / Tổng | % | Ngưỡng đạt chuẩn (≥85%) |
|---|---|---|---|---|---|
| **Domain 1 — Development with AWS Services** | 32% | 1 – 21 | ___ / 21 | ___ % | ≥ 18 / 21 (85.7%) |
| **Domain 2 — Security** | 26% | 22 – 38 | ___ / 17 | ___ % | ≥ 14 / 17 (82.4%) |
| **Domain 3 — Deployment** | 24% | 39 – 54 | ___ / 16 | ___ % | ≥ 14 / 16 (87.5%) |
| **Domain 4 — Troubleshooting and Optimization** | 18% | 55 – 65 | ___ / 11 | ___ % | ≥ 9 / 11 (81.8%) |
| **TỔNG CỘNG** | **100%** | **1 – 65** | **___ / 65** | **___ %** | **≥ 55 / 65 (84.6% ~ 85%)** |

> ⚠️ **Đánh giá kết quả:**
> - **≥ 55/65 (≥ 85%):** Xuất sắc. Bạn đã nắm rất vững kiến thức nền tảng và phản xạ cú pháp. Sẵn sàng làm tiếp Mock 02.
> - **47 – 54/65 (72% – 84%):** Đạt ngưỡng đỗ lý thuyết nhưng chưa có biên an toàn. Rà soát ngay các câu sai ở domain thấp nhất.
> - **< 47/65 (< 72%):** Chưa đạt. Dành 3 ngày ôn lại toàn bộ lý thuyết và bài tập của domain yếu nhất trong [`../../study-plan/`](../../study-plan/).

---

## 📝 Giải thích chi tiết 65 câu hỏi

### Question 1 — Answer: **A**
- **Why correct:** Công thức tính Lambda Concurrency: `Concurrency = Invocations Per Second × Average Execution Duration (seconds)`. Ở đây: `50 requests/sec × 4 seconds = 200 concurrent executions`. Vì Amazon S3 là nguồn sự kiện **bất đồng bộ (asynchronous event source)**, khi Lambda bị throttle (vượt quá concurrency), Lambda sẽ tự động giữ event trong hàng đợi nội bộ và thử lại (retry) trong tối đa 6 giờ trước khi hủy hoặc gửi tới Dead Letter Queue/Destination.
- **Why the others are wrong:** B sai vì 12.5 là lấy 50 chia 4 thay vì nhân. C sai vì Lambda hoàn toàn serverless, không tự động provision EC2 instance. D sai vì S3 không gửi thẳng đến DLQ khi throttle mà Lambda queue nội bộ sẽ retry trước.
- 🧠 **Key point / trap:** `Concurrency = Requests/sec × Duration(s)`. Bất đồng bộ (S3, SNS, EventBridge) tự retry đến 6h khi throttle; đồng bộ (API Gateway) trả về lỗi `429 Too Many Requests` ngay lập tức.
- 📎 Source: `AWS Lambda Developer Guide — Managing Concurrency`.

### Question 2 — Answer: **A**
- **Why correct:** Khi Lambda khởi tạo môi trường thực thi (execution environment), bất kỳ code nào đặt ngoài hàm handler (trong global scope) chỉ chạy một lần duy nhất trong quá trình **Cold Start**. Khởi tạo database client và kết nối `client.connect()` bên ngoài handler giúp tái sử dụng connection TCP qua các lần gọi (warm invocations), giảm triệt để độ trễ và tránh cạn kiệt connection pool của database. Không được gọi `client.end()` trong handler vì sẽ đóng kết nối ngay sau mỗi request.
- **Why the others are wrong:** B sai vì tăng memory chỉ tăng CPU/RAM chứ không giải quyết logic mở/đóng connection. C sai vì `/tmp` là ổ đĩa cục bộ, không thể serialize socket TCP connection vào file JSON. D sai vì Provisioned Concurrency 1 chỉ giữ ấm 1 container, không thể xử lý tải lớn đồng thời.
- 🧠 **Key point / trap:** Tái sử dụng đối tượng nặng (DB connection, AWS SDK client, HTTP client) bằng cách khai báo **ngoài handler (Execution Context Reuse)**.
- 📎 Source: `AWS Lambda Developer Guide — Optimizing Node.js functions`.

### Question 3 — Answer: **B**
- **Why correct:** **Lambda Destinations** (On-Failure Destination) vượt trội hơn DLQ truyền thống vì:
  1. Hỗ trợ gửi đầy đủ cả event payload ban đầu lẫn **call stack, error code, function response** (DLQ chỉ gửi payload thô, không kèm thông tin lỗi).
  2. Hỗ trợ nhiều đích đến hơn: SQS, SNS, EventBridge, hoặc một hàm Lambda khác.
  3. Cấu hình hoàn toàn phía Lambda service, không cần viết code `try/catch`.
- **Why the others are wrong:** A kém tối ưu hơn B vì DLQ không chứa metadata lỗi. C tốn công bảo trì code và nếu Lambda bị timeout hoặc crash process thì block `try/catch` sẽ không bao giờ chạy. D phức tạp hóa kiến trúc không cần thiết.
- 🧠 **Key point / trap:** Xử lý lỗi bất đồng bộ Lambda: Ưu tiên **Lambda Destinations (On-Failure)** hơn DLQ vì lưu được cả nguyên nhân gây lỗi (stack trace).
- 📎 Source: `AWS Lambda Developer Guide — Configuring Destinations for Asynchronous Invocation`.

### Question 4 — Answer: **A**
- **Why correct:** Giới hạn tải lên trực tiếp (direct upload) của gói triển khai Lambda (ZIP file) thông qua AWS CLI/API là **50 MB**. Đối với các gói mã nguồn lớn hơn 50 MB (lên đến 250 MB giải nén), bắt buộc phải tải file ZIP lên **Amazon S3** trước, sau đó chỉ định tham số `--s3-bucket` và `--s3-key` trong lệnh `update-function-code`.
- **Why the others are wrong:** B sai vì giới hạn 50 MB direct upload là hard limit không thể yêu cầu tăng quota. C sai vì nén hai lần không giải quyết được định dạng Lambda hỗ trợ. D chia nhỏ hàm gây phức tạp kiến trúc và độ trễ mạng.
- 🧠 **Key point / trap:** Lambda package limit: Direct upload = **50 MB**; Qua Amazon S3 = **250 MB** (unzipped). Trên 250 MB → chuyển sang **Container Image (tối đa 10 GB)**.
- 📎 Source: `AWS Lambda Quotas`.

### Question 5 — Answer: **C**
- **Why correct:** Quy tắc tính RCU của DynamoDB:
  1. Một RCU cho phép thực hiện **1 Strongly Consistent Read** mỗi giây cho item có kích thước tối đa **4 KB**.
  2. Kích thước item là 10 KB → làm tròn lên bội số tiếp theo của 4 KB: `ceil(10 / 4) = 3 RCU` cho mỗi item.
  3. Tổng RCU cần provision: `100 reads/sec × 3 RCU = 300 RCU`.
- **Why the others are wrong:** A (100) nếu mỗi item ≤ 4 KB. B (200) là nếu item 8 KB. D (150) là nếu đọc Eventually Consistent (1 RCU = 2 reads/sec).
- 🧠 **Key point / trap:** Đọc DynamoDB: Luôn làm tròn lên bội số 4 KB (`ceil(Size/4KB)`). Strongly Consistent = 1 RCU/item; Eventually Consistent = chia đôi (`/2`); Transactional = nhân đôi (`×2`).
- 📎 Source: `Amazon DynamoDB Developer Guide — Provisioned Capacity Mode`.

### Question 6 — Answer: **C**
- **Why correct:** Quy tắc tính WCU của DynamoDB:
  1. Một WCU cho phép thực hiện **1 write** mỗi giây cho item có kích thước tối đa **1 KB**.
  2. Kích thước item là 2.5 KB → làm tròn lên bội số tiếp theo của 1 KB: `ceil(2.5 / 1) = 3 WCU` cho mỗi item.
  3. Tổng WCU cần provision: `50 writes/sec × 3 WCU = 150 WCU`.
- **Why the others are wrong:** A (50) nếu item ≤ 1 KB. B (100) nếu item 2 KB. D (200) tính nhầm 4 WCU.
- 🧠 **Key point / trap:** Ghi DynamoDB: Luôn làm tròn lên bội số **1 KB** (`ceil(Size/1KB)`). Transactional writes tốn gấp đôi (`×2 WCU`).
- 📎 Source: `Amazon DynamoDB Developer Guide — Provisioned Capacity Mode`.

### Question 7 — Answer: **A, B**
- **Why correct:**
  - Pattern 1: Cần query đơn hàng theo `CustomerId` (đã là Partition Key của bảng gốc) nhưng sort/filter theo `TotalAmount` → Dùng **Local Secondary Index (LSI)** vì LSI giữ nguyên Partition Key của bảng và chỉ thay đổi Sort Key.
  - Pattern 2: Cần query đơn hàng trên TOÀN BỘ khách hàng theo `OrderStatus` → Bắt buộc dùng **Global Secondary Index (GSI)** với Partition Key là `OrderStatus` và Sort Key là `OrderDate` (GSI có thể có Partition Key hoàn toàn khác với bảng gốc).
- **Why the others are wrong:** C sai vì LSI bắt buộc phải dùng cùng Partition Key với bảng gốc (`CustomerId`). D sai vì GSI có thể tạo bất kỳ lúc nào (không cần đợi 10k items). E sai vì DAX chỉ cấu hình trên cụm cluster của bảng, không bật riêng lẻ trên LSI.
- 🧠 **Key point / trap:** **LSI**: Cùng Partition Key, khác Sort Key, chỉ tạo được lúc `CreateTable`, chia sẻ capacity và giới hạn 10 GB/partition. **GSI**: Khác Partition Key và/hoặc Sort Key, tạo lúc nào cũng được, capacity riêng biệt.
- 📎 Source: `Amazon DynamoDB Developer Guide — Secondary Indexes`.

### Question 8 — Answer: **A**
- **Why correct:** Khi tất cả các thiết bị ghi dữ liệu với partition key là ngày `YYYY-MM-DD`, toàn bộ 25,000 writes/sec trong ngày hôm đó sẽ dồn vào **duy nhất một phân vùng vật lý (physical partition)**. Mỗi phân vùng vật lý của DynamoDB có trần giới hạn tối đa là **1,000 WCU** (hoặc 3,000 RCU). Do đó, dù bảng được provision 35,000 WCU, một phân vùng đơn lẻ không thể nhận quá 1,000 WCU và gây ra `ProvisionedThroughputExceededException` (Hot Partition). Giải pháp chuẩn là **Write Sharding (Salting)**: thêm suffix ngẫu nhiên (ví dụ `.1`, `.2`, ... `.50`) hoặc dùng `DeviceId` làm Partition Key.
- **Why the others are wrong:** B sai vì giới hạn 10 GB chỉ áp dụng cho item collection có LSI, không gây throttle WCU theo cách này. C sai vì DynamoDB hỗ trợ hàng triệu WCU trên toàn bảng. D sai vì DAX là bộ nhớ đệm read (write-through), không giúp phân tán hot partition ghi.
- 🧠 **Key point / trap:** Giới hạn cứng 1 physical partition DynamoDB = **1,000 WCU và 3,000 RCU**. Gặp "hot partition" do ngày tháng/trạng thái → **Write Sharding / Random Suffix**.
- 📎 Source: `Amazon DynamoDB Best Practices — Designing Partition Keys`.

### Question 9 — Answer: **A**
- **Why correct:** **Optimistic Locking (Khóa lạc quan)** trong DynamoDB được triển khai bằng cách lưu thuộc tính `version` trong item. Khi cập nhật:
  ```json
  "ConditionExpression": "version = :expectedVersion",
  "UpdateExpression": "SET balance = balance + :amt, version = version + :one"
  ```
  Nếu có tiến trình khác ghi đè lên trước đó (làm `version` thay đổi), `ConditionExpression` sẽ thất bại với lỗi `ConditionalCheckFailedException`, tiến trình hiện tại sẽ đọc lại giá trị mới và retry với exponential backoff.
- **Why the others are wrong:** B sai vì `TransactWriteItems` là transaction atomic, không phải cơ chế pessimistic lock bảng và tốn gấp đôi capacity. C sai vì đọc nhất quán không ngăn được race condition khi ghi. D sai vì DynamoDB Streams chỉ phát hiện sau khi dữ liệu đã bị ghi đè.
- 🧠 **Key point / trap:** "Prevent lost updates / concurrent updates" → **Optimistic Locking (`version` attribute + `ConditionExpression`)**.
- 📎 Source: `Amazon DynamoDB Developer Guide — Optimistic Locking with Version Number`.

### Question 10 — Answer: **A**
- **Why correct:** DynamoDB Streams ghi lại các thay đổi theo thời gian thực. Khi nối DynamoDB Streams với Lambda qua Event Source Mapping:
  - `BisectBatchOnFunctionError=true`: Khi một batch bị lỗi, Lambda tự động chia đôi batch thành hai nửa nhỏ hơn và thử lại, giúp cô lập chính xác bản ghi bị lỗi (poison pill).
  - `MaximumRecordAgeInSeconds`: Bỏ qua các bản ghi quá hạn để không chặn stream.
  - `On-Failure Destination`: Gửi bản ghi bị lỗi sang SQS queue để lập trình viên xử lý thủ công mà không làm nghẽn stream processing.
- **Why the others are wrong:** B đi vòng qua S3 làm mất tính thời gian thực. C sai vì SNS không thể đăng ký trực tiếp làm target từ DynamoDB table mà không qua Lambda/EventBridge. D sai vì chạy `Scan` định kỳ cực kỳ tốn kém và không phải thời gian thực.
- 🧠 **Key point / trap:** Xử lý lỗi DynamoDB/Kinesis Event Source Mapping: Bật **`BisectBatchOnFunctionError`** và cấu hình **`On-Failure Destination` (SQS/SNS)** để tránh nghẽn luồng xử lý do 1 bản ghi lỗi.
- 📎 Source: `AWS Lambda Developer Guide — Using AWS Lambda with Amazon DynamoDB`.

### Question 11 — Answer: **A**
- **Why correct:** **Amazon API Gateway HTTP API** được thiết kế chuyên biệt cho các ứng dụng serverless hiện đại:
  1. Độ trễ thấp hơn (nhẹ hơn REST API).
  2. Rẻ hơn tới 70% so với REST API ($1.00/million vs $3.50/million).
  3. Hỗ trợ sẵn tích hợp JWT Authorizer (OIDC / OAuth 2.0 / Cognito) mà không cần viết custom Lambda authorizer.
- **Why the others are wrong:** B và C (REST API) đắt hơn và có độ trễ cao hơn, phù hợp khi cần mapping templates, API keys, usage plans, hoặc WAF. D (WebSocket API) là giao tiếp hai chiều liên tục, không phù hợp cho request/response microservice thông thường.
- 🧠 **Key point / trap:** **HTTP API** = Rẻ hơn 70%, độ trễ thấp, native JWT/OIDC auth. **REST API** = Hỗ trợ Request/Response Transformation (VTL mapping templates), API keys, Usage Plans, Caching.
- 📎 Source: `Amazon API Gateway Developer Guide — Choosing between REST APIs and HTTP APIs`.

### Question 12 — Answer: **A**
- **Why correct:** **Stage Variables** trong API Gateway đóng vai trò như biến môi trường. Bằng cách định nghĩa `${stageVariables.lambdaAlias}` trong URI tích hợp của Lambda, API Gateway sẽ tự động chuyển hướng request tới alias tương ứng (`DEV`, `TEST`, `PROD`) của hàm Lambda tùy thuộc vào stage đang phục vụ, cho phép dùng một API definition duy nhất cho mọi môi trường.
- **Why the others are wrong:** B tạo gánh nặng quản lý khi phải duy trì 3 API độc lập. C dựa vào client gửi header là không an toàn và dễ bị can thiệp. D tốn chi phí và tăng độ trễ khi phải tra cứu DynamoDB trên mỗi request.
- 🧠 **Key point / trap:** "Một API Gateway duy nhất route đến các Lambda alias / môi trường khác nhau" → **Stage Variables (`${stageVariables.varName}`)**.
- 📎 Source: `Amazon API Gateway Developer Guide — Using Stage Variables`.

### Question 13 — Answer: **A**
- **Why correct:** API Gateway có tính năng **Request Validation**. Bạn có thể bật validator để kiểm tra tham số query string, headers và payload body (dùng JSON Schema model) ngay tại tầng API Gateway. Nếu request không hợp lệ, API Gateway sẽ trả về lỗi `400 Bad Request` ngay lập tức mà **không gọi xuống Lambda**, giúp tiết kiệm hoàn toàn chi phí thực thi Lambda và giảm tải cho backend.
- **Why the others are wrong:** B sai vì WAF dùng cho bảo mật/chặn tấn công, không dùng để validate schema nghiệp vụ tham số. C sai vì Lambda Authorizer vẫn tốn chi phí thực thi Lambda và dùng cho xác thực/phân quyền, không phải validate payload. D sai vì mapping template chạy sau khi request đã được chấp nhận và không tự động báo lỗi cho client.
- 🧠 **Key point / trap:** Muốn chặn request sai format/thiếu param **trước khi chạm vào Lambda để tiết kiệm tiền** → **API Gateway Request Validation (với JSON Schema Model)**.
- 📎 Source: `Amazon API Gateway Developer Guide — Enable Request Validation`.

### Question 14 — Answer: **A, B**
- **Why correct:** Xử lý CORS trong API Gateway với preflight check (khi có custom header hoặc method khác GET/simple POST):
  1. Trình duyệt sẽ gửi request `OPTIONS` (Preflight). API Gateway cần có phương thức `OPTIONS` trả về các header: `Access-Control-Allow-Origin`, `Access-Control-Allow-Methods`, và `Access-Control-Allow-Headers` chứa các header client gửi lên (như `X-Custom-Auth`).
  2. Khi dùng Lambda Proxy Integration, bản thân code của hàm Lambda khi trả về kết quả cho request chính (`POST`) cũng **bắt buộc phải trả về header `Access-Control-Allow-Origin`** trong response object (`headers: {'Access-Control-Allow-Origin': '...'}`).
- **Why the others are wrong:** C sai vì xóa `OPTIONS` sẽ làm preflight check thất bại 100%. D và E không liên quan đến cơ chế CORS của trình duyệt.
- 🧠 **Key point / trap:** Lỗi CORS trên Lambda Proxy Integration: Bắt buộc cấu hình cả **OPTIONS mock method** trên API Gateway VÀ trả về **header `Access-Control-Allow-Origin` trong chính payload của Lambda**.
- 📎 Source: `Amazon API Gateway Developer Guide — Enabling CORS for a REST API`.

### Question 15 — Answer: **A**
- **Why correct:** **S3 Presigned URLs** là giải pháp chuẩn công nghiệp cho việc tải file trực tiếp từ client lên S3:
  1. Lambda backend dùng AWS SDK và IAM role của nó để ký một URL (`getSignedUrl` với action `putObject`) có thời hạn sống (ví dụ 900 giây).
  2. Mobile client nhận URL và thực hiện HTTP `PUT` trực tiếp lên S3.
  3. Không cần cấp IAM user cho client, và file video dung lượng lớn không đi qua Lambda (tránh giới hạn payload 6 MB của Lambda và timeout).
- **Why the others are wrong:** B sai vì SQS chỉ chứa message tối đa 256 KB, không thể chứa file video. C sai vì cấp IAM user cho thiết bị di động vi phạm nghiêm trọng nguyên tắc bảo mật. D sai vì mở public anonymous upload là lỗ hổng bảo mật nghiêm trọng.
- 🧠 **Key point / trap:** Client upload/download file lớn trực tiếp lên S3 mà không cần IAM credential và không làm nghẽn backend → **S3 Presigned URL (với expiration time)**.
- 📎 Source: `Amazon S3 Developer Guide — Uploading Objects Using Presigned URLs`.

### Question 16 — Answer: **A**
- **Why correct:** **Amazon S3 Multipart Upload**:
  1. Cho phép upload file lớn thành nhiều phần độc lập (parts) song song (khuyến nghị cho file > 100 MB, bắt buộc cho file > 5 GB).
  2. Khả năng phục hồi cao: Nếu một part bị lỗi kết nối, chỉ cần tải lại part đó mà không phải upload lại toàn bộ file.
  3. Để tránh phát sinh chi phí lưu trữ cho các part dở dang do người dùng hủy upload, cần thiết lập **S3 Lifecycle Rule** với hành động `AbortIncompleteMultipartUpload`.
- **Why the others are wrong:** B không khắc phục được tình trạng đứt mạng giữa chừng đối với file 20 GB. C DynamoDB giới hạn item 400 KB, không lưu được file 500 MB. D Transfer Acceleration tối ưu định tuyến mạng nhưng không hỗ trợ resume part như Multipart Upload.
- 🧠 **Key point / trap:** File > 100 MB, mạng chập chờn → **Multipart Upload**. Luôn nhớ cấu hình rule **`AbortIncompleteMultipartUpload`** để dọn dẹp các part bị bỏ dở tránh mất tiền oan.
- 📎 Source: `Amazon S3 Developer Guide — Multipart Upload Overview`.

### Question 17 — Answer: **A**
- **Why correct:** **Amazon SQS FIFO (First-In, First-Out)** đảm bảo:
  1. Thứ tự tin nhắn chính xác theo thứ tự gửi.
  2. Xử lý chính xác một lần (Exactly-Once Processing) thông qua `MessageDeduplicationId` hoặc hash SHA-256 của nội dung (Content-Based Deduplication).
  3. Thuộc tính `MessageGroupId` nhóm các tin nhắn của cùng một tài khoản (`AccountId`) lại để xử lý tuần tự nghiêm ngặt, trong khi các `MessageGroupId` khác nhau vẫn có thể được xử lý song song bởi nhiều consumers.
- **Why the others are wrong:** B sai vì Standard queue không đảm bảo thứ tự và có thể phân phối duplicate (At-least-once). C sai vì SNS Standard không đảm bảo thứ tự. D sai vì thiếu `MessageGroupId` sẽ bị lỗi khi gửi vào FIFO queue.
- 🧠 **Key point / trap:** SQS FIFO: Thứ tự nghiêm ngặt + Exactly-once. Phân luồng song song theo khách hàng/entity bằng **`MessageGroupId`**; chống trùng bằng **`MessageDeduplicationId`**.
- 📎 Source: `Amazon SQS Developer Guide — FIFO Queues`.

### Question 18 — Answer: **A, B**
- **Why correct:**
  - Vấn đề duplicate processing: Mặc định Visibility Timeout là 30 giây. Khi worker mất 45 giây để xử lý, sau 30 giây tin nhắn trở lại hiển thị trên queue, dẫn đến worker khác đọc được tin nhắn đó và xử lý lại lần 2. Do đó, cần **tăng Visibility Timeout lên lớn hơn thời gian xử lý** (ví dụ 90 giây).
  - Vấn đề chi phí và cuộc gọi rỗng: Mặc định là Short Polling (trả về ngay cả khi không có message). Cần **bật Long Polling (`ReceiveMessageWaitTimeSeconds = 20`)** để SQS giữ kết nối tối đa 20 giây đợi tin nhắn mới, giảm 99% số lượng call rỗng và giảm chi phí.
- **Why the others are wrong:** C giảm timeout càng làm lỗi duplicate nghiêm trọng hơn. D Short polling làm tăng số lượng API call rỗng. E Kinesis Data Firehose là dịch vụ streaming load vào data lake, không giải quyết bài toán hàng đợi EC2 worker.
- 🧠 **Key point / trap:** Worker mất $X$ giây để xử lý → `VisibilityTimeout` phải $> X$ giây. Giảm chi phí API `ReceiveMessage` và cuộc gọi rỗng → **Long Polling (`WaitTimeSeconds = 20`)**.
- 📎 Source: `Amazon SQS Developer Guide — Message Visibility Timeout & Long Polling`.

### Question 19 — Answer: **A**
- **Why correct:** **Amazon SNS Subscription Filter Policy** cho phép người đăng ký (subscriber) lọc tin nhắn dựa trên các thuộc tính của tin nhắn (`MessageAttributes`). Bằng cách gán Filter Policy `{"order_total": [{"numeric": [">", 1000]}]}` cho subscription của `LargeOrderFulfillmentService`, SNS sẽ tự động lọc và chỉ chuyển tiếp các đơn hàng trên $1,000 vào hàng đợi của dịch vụ này, trong khi hàng đợi của `FraudDetectionService` không có filter policy sẽ nhận tất cả tin nhắn. Không cần viết thêm dòng code định tuyến nào.
- **Why the others are wrong:** B làm tăng trách nhiệm và logic phức tạp trong publisher. C làm tăng tải đọc/xóa vô ích cho các worker. D bổ sung Lambda làm tăng độ trễ và chi phí trung gian không cần thiết.
- 🧠 **Key point / trap:** Phân luồng tin nhắn tự động từ 1 topic SNS tới nhiều queue mà không cần viết code → **SNS Subscription Filter Policies (dựa trên Message Attributes)**.
- 📎 Source: `Amazon SNS Developer Guide — Message Filtering`.

### Question 20 — Answer: **A**
- **Why correct:** **AWS Step Functions Express Workflows** được thiết kế riêng cho các luồng xử lý khối lượng lớn (high-throughput, lên tới hơn 100,000 executions/giây), thời gian thực thi ngắn (tối đa 5 phút), và chi phí cực rẻ (tính trên thời gian chạy và dung lượng bộ nhớ, thay vì tính trên từng bước chuyển state như Standard Workflows).
- **Why the others are wrong:** B (Standard Workflows) chỉ hỗ trợ tối đa 2,000 execution starts/giây và tính phí trên mỗi state transition ($0.025 / 1,000 transitions), sẽ cực kỳ đắt đỏ ở quy mô 15,000 requests/giây. C và D không phải là workflow type độc lập.
- 🧠 **Key point / trap:** **Express Workflows**: Tối đa 5 phút, throughput cao (>100k/s), tính phí theo thời gian chạy (GB-giây). **Standard Workflows**: Chạy tới 1 năm, audit đầy đủ từng bước, tính phí theo State Transition.
- 📎 Source: `AWS Step Functions Developer Guide — Standard vs. Express Workflows`.

### Question 21 — Answer: **A**
- **Why correct:** Chiến lược **Lazy Loading (Cache-Aside)** hoạt động theo quy trình:
  1. Ứng dụng đọc cache trước.
  2. Nếu có dữ liệu (**Cache Hit**) → trả về ngay.
  3. Nếu không có (**Cache Miss**) → ứng dụng đọc dữ liệu từ database, ghi dữ liệu vừa đọc vào cache (kèm TTL để tự động làm mới), rồi trả về cho client.
  Chỉ những dữ liệu thực sự được yêu cầu mới được nạp vào cache.
- **Why the others are wrong:** B là Write-Through kết hợp Write-Back. C không phải mô hình tiêu chuẩn của ElastiCache. D cơ sở dữ liệu quan hệ không tự động forward query kết quả vào Redis.
- 🧠 **Key point / trap:** **Lazy Loading (Cache-Aside)**: Chỉ nạp khi Cache Miss, tránh đầy cache với dữ liệu không ai đọc. **Write-Through**: Cập nhật cache ngay khi có lệnh ghi vào DB, đảm bảo dữ liệu luôn mới nhưng ghi chậm hơn.
- 📎 Source: `Amazon ElastiCache User Guide — Caching Strategies`.

### Question 22 — Answer: **A**
- **Why correct:** Quy trình chuẩn truy cập cross-account trong AWS:
  1. Tại tài khoản đích (Account B): Tạo IAM Role có **Trust Policy** cho phép `Principal: "arn:aws:iam::111122223333:root"` thực hiện hành động `sts:AssumeRole`, và đính kèm Permission Policy cấp quyền `s3:GetObject` trên bucket.
  2. Tại tài khoản nguồn (Account A): Gán quyền cho EC2 Instance Role gọi `sts:AssumeRole` tới ARN của Role bên Account B.
  3. Ứng dụng gọi API `sts:AssumeRole` để nhận credentials tạm thời và đọc S3.
- **Why the others are wrong:** B dùng access key tĩnh là vi phạm chính sách bảo mật cấm long-term credentials. C mở `Principal: "*"` gây nguy cơ bảo mật. D S3 bucket policy không cấp quyền `sts:AssumeRole`.
- 🧠 **Key point / trap:** Truy cập Cross-account an toàn: **STS `AssumeRole`** + **Trust Policy (ở tài khoản đích)** + **Identity Policy (ở tài khoản nguồn)**.
- 📎 Source: `AWS IAM User Guide — Providing Access to an IAM User in Another AWS Account`.

### Question 23 — Answer: **A**
- **Why correct:** API **`sts:AssumeRoleWithWebIdentity`** được thiết kế đặc thù cho các ứng dụng di động/web công khai. Ứng dụng client sau khi xác thực thành công với các nhà cung cấp IdP tương thích OIDC/OAuth 2.0 (Google, Apple, Facebook, Amazon, Cognito) sẽ nhận được một JWT token. Client gửi token này tới `AssumeRoleWithWebIdentity` để đổi lấy **temporary AWS credentials** gắn với một IAM role có quyền ghi vào Kinesis.
- **Why the others are wrong:** B (`GetSessionToken`) dùng cho IAM user có sẵn trong account (thường dùng khi có MFA). C (`AssumeRole`) yêu cầu phải có sẵn IAM credential để gọi. D (`GetFederationToken`) dành cho custom identity broker ở server-side.
- 🧠 **Key point / trap:** Đăng nhập qua mạng xã hội / OIDC (Google, Apple, Cognito) → Đổi lấy AWS credentials tạm thời bằng **`sts:AssumeRoleWithWebIdentity`**.
- 📎 Source: `AWS STS Developer Guide — AssumeRoleWithWebIdentity`.

### Question 24 — Answer: **A**
- **Why correct:** Thứ tự đánh giá chính sách IAM trong AWS: **Explicit Deny > Explicit Allow > Default Deny (Implicit Deny)**. Nếu có bất kỳ chính sách nào áp dụng mà chứa statement `Deny` (dù là SCP, Permissions Boundary, hay Resource Policy), request sẽ bị **từ chối ngay lập tức**, không có ngoại lệ. Trong đề bài, bucket policy chứa explicit Deny khi kết nối không bảo mật (`aws:SecureTransport: false`), do đó request qua HTTP sẽ bị chặn.
- **Why the others are wrong:** B và C sai vì Allow không bao giờ thắng được Explicit Deny. D sai vì Permissions Boundary không liên quan đến việc đánh giá statement Deny trong bucket policy.
- 🧠 **Key point / trap:** Trong AWS IAM: **Một Explicit Deny duy nhất đập tan mọi Explicit Allow**. Bắt buộc HTTPS trên S3 bằng điều kiện `"aws:SecureTransport": "false"` kèm `"Effect": "Deny"`.
- 📎 Source: `AWS IAM User Guide — Policy Evaluation Logic`.

### Question 25 — Answer: **A**
- **Why correct:** **IAM Permission Boundary** là công cụ quản trị bảo mật cho phép ủy quyền (delegation). Người quản trị tạo một policy boundary xác định trần quyền tối đa (ví dụ chỉ được làm việc với Lambda, S3, DynamoDB). Khi cấp quyền cho junior developer tạo role (`iam:CreateRole`), quản trị viên cài điều kiện `Condition` yêu cầu role mới tạo bắt buộc phải được đính kèm boundary này. Nếu junior developer cố tình tạo role có quyền Administrator, boundary sẽ cắt toàn bộ quyền vượt trần, ngăn chặn hoàn toàn việc leo thang đặc quyền (privilege escalation).
- **Why the others are wrong:** B SCP chỉ áp dụng trên AWS Organizations OU/Account, không thể gắn trực tiếp vào IAM user group. C Session policy chỉ áp dụng khi assume role trong phiên làm việc. D hạn chế này không đáp ứng yêu cầu ủy quyền tạo role.
- 🧠 **Key point / trap:** Ủy quyền tạo role cho dev mà không lo bị leo quyền Admin → **IAM Permissions Boundary** (đặt trần quyền tối đa).
- 📎 Source: `AWS IAM User Guide — Permissions Boundaries for IAM Entities`.

### Question 26 — Answer: **A**
- **Why correct:** API `kms:Encrypt` của AWS KMS có giới hạn cứng: chỉ nhận plaintext tối đa **4 KB** (4,096 bytes). Đối với dữ liệu lớn hơn 4 KB (như file 50 MB), bắt buộc phải dùng kỹ thuật **Mã hóa phong bì (Envelope Encryption)**:
  1. Gọi `kms:GenerateDataKey` để KMS trả về: Plaintext Data Key (key thô) và Ciphertext Data Key (key đã được mã hóa bằng CMK).
  2. Ứng dụng dùng Plaintext Data Key để mã hóa file 50 MB cục bộ (ví dụ qua thuật toán AES-256).
  3. Xóa ngay Plaintext Data Key khỏi RAM để đảm bảo an toàn.
  4. Lưu file đã mã hóa cùng với Ciphertext Data Key lên S3.
- **Why the others are wrong:** B Base64 chỉ làm tăng kích thước dữ liệu thêm 33%, không vượt qua được giới hạn 4 KB. C KMS hoàn toàn độc lập với định dạng file. D Chia nhỏ file 50 MB thành các mẩu 4 KB và gọi KMS hàng nghìn lần sẽ gây nghẽn API throttle và chi phí khổng lồ.
- 🧠 **Key point / trap:** Dữ liệu $> 4\text{ KB}$ cần mã hóa bằng KMS → Bắt buộc dùng **Envelope Encryption với `kms:GenerateDataKey`**.
- 📎 Source: `AWS KMS Developer Guide — Envelope Encryption`.

### Question 27 — Answer: **A**
- **Why correct:** **Customer Managed Key (CMK)** trong AWS KMS mang lại quyền kiểm soát toàn diện:
  - Khách hàng tự quản lý key policy, gán tag, tạo grant.
  - Hỗ trợ bật tính năng tự động xoay vòng key hàng năm (Automatic rotation mỗi 365 ngày).
  - Có thể disable key ngay lập tức hoặc lên lịch xóa (từ 7 đến 30 ngày) khi có sự cố.
  - Mọi thao tác sử dụng key đều được ghi log chi tiết trong CloudTrail.
- **Why the others are wrong:** B (AWS Managed Key như `aws/s3`) không thể thay đổi key policy, không thể tự disable hoặc xóa. C (AWS Owned Key) do AWS dùng nội bộ, khách hàng không thể xem hay quản lý. D (SSE-C) đẩy toàn bộ việc quản lý và xoay key về client, không tận dụng được KMS.
- 🧠 **Key point / trap:** Cần toàn quyền kiểm soát key policy, bật/tắt key tức thì, tự động xoay key hàng năm → Chọn **Customer Managed Key (CMK)**.
- 📎 Source: `AWS KMS Developer Guide — Customer Keys and AWS Keys`.

### Question 28 — Answer: **A**
- **Why correct:** KMS Key Policy là cơ chế kiểm soát truy cập chính của KMS. Khác với các tài nguyên AWS khác, chính sách IAM gắn trên User/Role (kể cả quyền `AdministratorAccess`) **hoàn toàn vô hiệu** đối với KMS key trừ khi trong chính sách KMS Key Policy có một statement ủy quyền cho tài khoản root của AWS Account:
  ```json
  "Principal": { "AWS": "arn:aws:iam::<account-id>:root" },
  "Action": "kms:*",
  "Resource": "*"
  ```
  Statement này ủy quyền cho tài khoản sử dụng các IAM policy để phân quyền cho key. Nếu thiếu statement này, chỉ những principal được ghi danh trực tiếp trong Key Policy mới có quyền thao tác.
- **Why the others are wrong:** B Grant là tùy chọn, không bắt buộc cho quyền quản trị. C sai vì IAM user hoàn toàn có thể quản trị key nếu được ủy quyền. D `CreateAlias` không giải quyết được lỗi phân quyền access denied.
- 🧠 **Key point / trap:** Muốn IAM policy (kể cả Administrator) có tác dụng trên KMS Key → Key Policy bắt buộc phải chứa statement cho phép **`arn:aws:iam::<account-id>:root`**.
- 📎 Source: `AWS KMS Developer Guide — Default Key Policy and Delegating to IAM`.

### Question 29 — Answer: **A**
- **Why correct:** **KMS Grants** được thiết kế riêng biệt cho các trường hợp cấp quyền động, ngắn hạn và linh hoạt mà không cần chỉnh sửa Key Policy. Kích thước Key Policy bị giới hạn ở 32 KB, nếu liên tục thêm/sửa principal cho hàng nghìn worker chạy ngắn hạn sẽ làm phình policy và gây lỗi `LimitExceededException`. Dùng `kms:CreateGrant` cho phép gán quyền decrypt cho role của worker và sau đó dọn dẹp bằng `kms:RetireGrant`.
- **Why the others are wrong:** B tạo hàng nghìn IAM role mỗi ngày sẽ vượt hạn mức IAM entity quota. C dùng wildcard `*` vi phạm nghiêm trọng least privilege. D master key không bao giờ có thể export ra ngoài dưới dạng plaintext để lưu vào cache.
- 🧠 **Key point / trap:** Cấp quyền KMS tạm thời, linh hoạt cho hàng nghìn tác vụ/worker mà không làm chạm trần kích thước 32 KB của Key Policy → **KMS Grants (`CreateGrant` / `RetireGrant`)**.
- 📎 Source: `AWS KMS Developer Guide — Grants in AWS KMS`.

### Question 30 — Answer: **A**
- **Why correct:** **Asymmetric KMS Keys (Khóa bất đối xứng)**:
  - Khóa riêng (Private Key) được bảo vệ tuyệt đối bên trong phần cứng KMS HSM và không bao giờ rời khỏi KMS. Bên phát hành phần mềm gọi API `kms:Sign` để tạo chữ ký số bằng Private Key này.
  - Khóa công khai (Public Key) có thể tải về công khai qua API `kms:GetPublicKey`. Bên nhận (hàng triệu thiết bị client ngoài internet) có thể nhúng Public Key này và dùng các thư viện mã hóa chuẩn để xác thực chữ ký hoàn toàn offline mà không cần tài khoản AWS hay gọi API KMS.
- **Why the others are wrong:** B Khóa đối xứng dùng chung 1 key cho cả mã hóa và giải mã; chia sẻ cho client ngoài sẽ làm lộ bí mật và client có thể giả mạo chữ ký. C HMAC cũng là khóa đối xứng, chia sẻ secret key sẽ bị lộ. D Private key của KMS không thể export ra ngoài.
- 🧠 **Key point / trap:** Ký số phần mềm phát hành ra ngoài để client verify offline mà không cần AWS credentials → **Asymmetric KMS Key Pair (`SIGN_VERIFY`)** + **`kms:GetPublicKey`**.
- 📎 Source: `AWS KMS Developer Guide — Asymmetric Keys in AWS KMS`.

### Question 31 — Answer: **A**
- **Why correct:** Mô hình phân định trách nhiệm rõ ràng của Amazon Cognito:
  - **Cognito User Pool (Authentication - Xác thực):** Đóng vai trò là thư mục người dùng (User Directory), quản lý đăng ký, đăng nhập, quên mật khẩu, MFA và trả về các token JWT (ID token, Access token, Refresh token).
  - **Cognito Identity Pool (Authorization - Phân quyền):** Đóng vai trò liên kết danh tính, nhận JWT token từ User Pool (hoặc Google/Apple) để đổi lấy **temporary AWS credentials (STS)** từ một IAM role đã cấu hình. IAM role này có thể dùng policy variable `${cognito-identity.amazonaws.com:sub}` để phân quyền cho mỗi user chỉ được ghi vào folder riêng của mình trong S3.
- **Why the others are wrong:** B đảo ngược hoàn toàn chức năng của hai dịch vụ. C User Pool không cấp được temporary AWS credentials để client gọi trực tiếp S3 API. D Cognito Sync chỉ dùng đồng bộ dữ liệu nhỏ dạng key-value giữa các thiết bị.
- 🧠 **Key point / trap:** **User Pool** = Quản lý user, cấp JWT tokens. **Identity Pool** = Đổi token lấy AWS credentials tạm thời để truy cập tài nguyên AWS (S3, DynamoDB).
- 📎 Source: `Amazon Cognito Developer Guide — Common Scenarios`.

### Question 32 — Answer: **A**
- **Why correct:** **Pre token generation Lambda trigger** được Amazon Cognito kích hoạt đồng bộ ngay trước khi phát hành token (ID token và Access token). Nó cho phép lập trình viên tùy biến, thêm hoặc sửa đổi các claims (ví dụ thêm `tenant_id`, nhóm quyền doanh nghiệp) trực tiếp vào trong payload của JWT token.
- **Why the others are wrong:** B (Post confirmation) chạy sau khi user xác minh tài khoản, không chạy khi đăng nhập phát hành token. C (Pre sign-up) chạy khi user đăng ký. D (Custom message) dùng để tùy biến nội dung email/SMS gửi mã xác nhận.
- 🧠 **Key point / trap:** Muốn chèn thêm custom claims (`tenant_id`, role) vào JWT token trước khi trả về cho client → **Pre token generation trigger**.
- 📎 Source: `Amazon Cognito Developer Guide — Pre Token Generation Lambda Trigger`.

### Question 33 — Answer: **A**
- **Why correct:** **AWS Secrets Manager** hỗ trợ tính năng tự động xoay vòng mật khẩu (Automatic Rotation) tích hợp sẵn cho các cơ sở dữ liệu Amazon RDS và Amazon Aurora. Secrets Manager cung cấp sẵn các Lambda template luân chuyển thông tin xác thực theo quy trình 4 bước (`createSecret`, `setSecret`, `testSecret`, `finishSecret`) mà không cần lập trình viên phải tự viết và kiểm thử code xoay vòng.
- **Why the others are wrong:** B SSM Parameter Store không có tính năng tự động xoay vòng native out-of-the-box, đòi hỏi phải tự viết code Lambda và EventBridge rất tốn công. C và D không đáp ứng yêu cầu tự động và vi phạm quy chuẩn bảo mật.
- 🧠 **Key point / trap:** Mật khẩu Database RDS cần **tự động xoay định kỳ (Automatic Rotation)** ít tốn công nhất → Chọn **AWS Secrets Manager** (có sẵn built-in rotation Lambda templates).
- 📎 Source: `AWS Secrets Manager User Guide — Rotating Secrets`.

### Question 34 — Answer: **A**
- **Why correct:** Gọi `GetSecretValue` trên mỗi invocation với tần suất 5,000 req/s sẽ ngay lập tức chạm ngưỡng giới hạn API rate limit của Secrets Manager và tốn chi phí khổng lồ ($0.05/10,000 API calls). AWS cung cấp thư viện **Secrets Manager Client-Side Caching**. Khi khởi tạo cache ngoài hàm handler, các container Lambda ấm (warm containers) sẽ tái sử dụng secret đã lưu trong bộ nhớ RAM qua các lần gọi, giảm số lượng API calls hơn 99% và tự động làm mới secret khi hết hạn TTL.
- **Why the others are wrong:** B tăng RAM không nâng quota API của Secrets Manager. C lưu trong environment variable sẽ để lộ secret dạng plaintext trên console và không thể tự xoay vòng mật khẩu mà không redeploy code. D nâng quota vẫn không giải quyết được chi phí hàng nghìn USD tiền gọi API mỗi tháng.
- 🧠 **Key point / trap:** Tránh lỗi throttling và tiết kiệm tiền khi đọc Secrets Manager trong Lambda tần suất cao → Dùng **Secrets Manager Client-side Caching Library** khởi tạo **ngoài handler**.
- 📎 Source: `AWS Secrets Manager User Guide — Cache Secrets with Secrets Manager Caching Libraries`.

### Question 35 — Answer: **A**
- **Why correct:** **AWS Systems Manager Parameter Store** hỗ trợ cấu trúc phân cấp dạng cây thư mục (Hierarchical Paths, tối đa 15 cấp), ví dụ: `/production/order-service/db_url`. Cấu trúc này mang lại hai lợi ích lớn:
  1. Cho phép ứng dụng tải toàn bộ tham số của một service trong 1 lần gọi API duy nhất thông qua `ssm:GetParametersByPath --path "/production/order-service"`.
  2. Dễ dàng viết chính sách IAM phân quyền theo tiền tố đường dẫn, ví dụ `Resource: "arn:aws:ssm:*:*:parameter/development/*"`.
- **Why the others are wrong:** B tên phẳng không dùng được `GetParametersByPath`. C lưu toàn bộ vào 1 chuỗi JSON sẽ bị giới hạn kích thước (4 KB/8 KB) và không phân quyền chi tiết được. D tạo nhiều account chỉ để lưu biến cấu hình là bất hợp lý.
- 🧠 **Key point / trap:** Quản lý cấu hình nhiều môi trường và lấy tất cả cấu hình trong 1 API call → **SSM Parameter Store Hierarchies (`GetParametersByPath`)**.
- 📎 Source: `AWS Systems Manager User Guide — Working with Parameter Store Hierarchies`.

### Question 36 — Answer: **A**
- **Why correct:** Để bắt buộc kết nối bảo mật HTTPS vào S3, giải pháp chuẩn là thêm một statement trong S3 Bucket Policy với:
  - `"Effect": "Deny"`
  - `"Action": "s3:*"`
  - `"Condition": {"Bool": {"aws:SecureTransport": "false"}}`
  Điều này sẽ từ chối mọi yêu cầu gửi qua giao thức HTTP không mã hóa đối với tất cả người dùng (kể cả root hoặc admin).
- **Why the others are wrong:** B chỉ kiểm tra thuật toán mã hóa at-rest (SSE), không kiểm tra kết nối in-transit. C không áp dụng cho các user khác ngoài root. D CORS không chặn được request trực tiếp từ client không phải browser.
- 🧠 **Key point / trap:** Bắt buộc HTTPS (Encryption in-transit) trên S3: Dùng điều kiện **`aws:SecureTransport = false`** với **`Effect: Deny`** trong Bucket Policy.
- 📎 Source: `AWS Knowledge Center — How to enforce HTTPS only on Amazon S3`.

### Question 37 — Answer: **A**
- **Why correct:** Khi thực hiện thao tác `PutObject` lên S3 và yêu cầu mã hóa Server-Side Encryption với Customer Managed Key trong KMS (SSE-KMS), client phải gửi hai HTTP headers:
  1. `x-amz-server-side-encryption: aws:kms`
  2. `x-amz-server-side-encryption-aws-kms-key-id: <KMS-Key-ARN>` (hoặc Key Alias)
  Bucket policy có thể kiểm tra hai header này trong điều kiện `StringEquals` để từ chối các request không tuân thủ.
- **Why the others are wrong:** B là header của SSE-C (Customer-provided key). C và D không phải header dùng để kích hoạt mã hóa SSE-KMS.
- 🧠 **Key point / trap:** Header upload S3 với KMS: **`x-amz-server-side-encryption: aws:kms`** và **`x-amz-server-side-encryption-aws-kms-key-id`**.
- 📎 Source: `Amazon S3 Developer Guide — Protecting Data Using Server-Side Encryption with KMS`.

### Question 38 — Answer: **A**
- **Why correct:** Lệnh **`aws sts get-session-token`** được thiết kế riêng cho các IAM User để lấy thông tin xác thực tạm thời khi cần thỏa mãn điều kiện Multi-Factor Authentication (MFA). Người dùng cung cấp số serial của thiết bị MFA và mã code 6 số hiện tại (`--token-code`), STS sẽ trả về credentials tạm thời có context `"aws:MultiFactorAuthPresent": "true"`.
- **Why the others are wrong:** B (`assume-role`) dùng để chuyển sang một role khác, không phải duy trì danh tính IAM user hiện tại để thao tác MFA. C (`get-federation-token`) dùng cho custom federated users. D (`get-caller-identity`) chỉ hiển thị thông tin danh tính hiện tại mà không cấp thêm token mới.
- 🧠 **Key point / trap:** IAM user cần xác thực MFA qua CLI để thực thi các lệnh yêu cầu MFA → **`aws sts get-session-token`**.
- 📎 Source: `AWS STS Developer Guide — GetSessionToken`.

### Question 39 — Answer: **A**
- **Why correct:** Trong file `buildspec.yml` của AWS CodeBuild, các lệnh đăng nhập vào container registry (như `aws ecr get-login-password | docker login`) hoặc kiểm tra các điều kiện tiên quyết bắt buộc phải được đặt trong phase **`pre_build`**. Nếu bước đăng nhập thất bại, build sẽ dừng ngay trước khi chạy lệnh build tốn thời gian.
- **Why the others are wrong:** `install` dùng để cài đặt runtime và package dependencies (như `apt-get` hoặc `npm install`). `build` dùng để chạy lệnh compile/docker build và unit test. `post_build` dùng để tag, push image lên ECR hoặc gửi thông báo.
- 🧠 **Key point / trap:** Thứ tự phase CodeBuild: **`install`** (cài tools) → **`pre_build`** (login ECR, tiền xử lý) → **`build`** (compile, test, docker build) → **`post_build`** (docker push, packaging).
- 📎 Source: `AWS CodeBuild User Guide — Build Spec Reference`.

### Question 40 — Answer: **A**
- **Why correct:** CodeBuild hỗ trợ cơ chế lưu cache (Caching). Bằng cách khai báo thư mục lưu trữ thư viện của Maven (`/root/.m2/**/*`) hoặc npm (`node_modules/**/*`) vào mục `cache.paths` trong file `buildspec.yml` và kích hoạt chế độ cache của project (lưu vào S3 hoặc local cache), các lần build tiếp theo sẽ tái sử dụng các dependency đã tải về thay vì tải lại toàn bộ từ internet, giảm thời gian build từ 15 phút xuống chỉ còn vài chục giây.
- **Why the others are wrong:** B chạy lệnh compile trong `post_build` không làm giảm thời gian tải dependency. C SQS không dùng để lưu trữ file build artifact. D tăng timeout chỉ làm kéo dài thời gian chờ tối đa, không giải quyết nguyên nhân gốc rễ.
- 🧠 **Key point / trap:** Tăng tốc độ build trong CodeBuild: Cấu hình **`cache.paths`** trong `buildspec.yml` để cache thư mục dependencies (`.m2`, `node_modules`).
- 📎 Source: `AWS CodeBuild User Guide — Build Cache`.

### Question 41 — Answer: **A**
- **Why correct:** `buildspec.yml` tích hợp sẵn khả năng đọc dữ liệu từ AWS Secrets Manager và SSM Parameter Store một cách an toàn mà không làm lộ dữ liệu trong console logs hay git repo:
  ```yaml
  env:
    parameter-store:
      API_URL: "/production/api/url"
    secrets-manager:
      DB_PASSWORD: "prod/db/secret:password"
  ```
  CodeBuild sẽ tự động gọi API lấy giá trị và gán vào biến môi trường khi container khởi động.
- **Why the others are wrong:** B `env.variables` dùng cho biến plaintext không nhạy cảm. C hardcode secret trong script vi phạm tiêu chuẩn bảo mật. D `artifacts` dùng để chỉ định file đầu ra sau khi build xong.
- 🧠 **Key point / trap:** Nạp secret/config vào CodeBuild an toàn: Khai báo dưới **`env.secrets-manager`** và **`env.parameter-store`** trong `buildspec.yml`.
- 📎 Source: `AWS CodeBuild User Guide — Environment Variables in Buildspec`.

### Question 42 — Answer: **A**
- **Why correct:** Trong file `appspec.yml` triển khai lên EC2/On-Premises của AWS CodeDeploy, hook **`ApplicationStop`** là lifecycle event hook đầu tiên được thực thi trước khi CodeDeploy agent tải gói mã nguồn mới (`DownloadBundle`). Đây là nơi thích hợp nhất để dừng service hiện tại một cách an toàn (gracefully stop service) hoặc gỡ instance ra khỏi load balancer.
- **Why the others are wrong:** `BeforeInstall` chạy sau khi gói bundle đã được tải về, thích hợp cho việc giải mã file hoặc backup file cũ. `AfterInstall` chạy sau khi file mới đã được copy vào thư mục đích. `ApplicationStart` dùng để khởi động lại service.
- 🧠 **Key point / trap:** Dừng ứng dụng cũ trước khi cài đè ứng dụng mới trên EC2 CodeDeploy: Hook **`ApplicationStop`**.
- 📎 Source: `AWS CodeDeploy User Guide — AppSpec 'hooks' Section for EC2/On-Premises`.

### Question 43 — Answer: **A**
- **Why correct:** Thứ tự thực thi chính xác của các lifecycle event hooks trong AWS CodeDeploy cho EC2 In-Place deployment:
  1. `ApplicationStop` (Dừng ứng dụng cũ)
  2. `DownloadBundle` (Reserved - agent tải file từ S3/GitHub)
  3. `BeforeInstall` (Chuẩn bị trước khi copy file)
  4. `Install` (Reserved - agent giải nén/copy file đến thư mục đích)
  5. `AfterInstall` (Cấu hình quyền file, migrate database)
  6. `ApplicationStart` (Khởi động service ứng dụng)
  7. `ValidateService` (Chạy smoke test kiểm tra trạng thái HTTP health check)
- **Why the others are wrong:** Các phương án B, C, D đều xáo trộn thứ tự các bước logic của quá trình cài đặt.
- 🧠 **Key point / trap:** Câu thần chú nhớ thứ tự Hook CodeDeploy EC2: **Stop → BeforeInstall → Install → AfterInstall → Start → Validate**.
- 📎 Source: `AWS CodeDeploy User Guide — Lifecycle Event Hook Order`.

### Question 44 — Answer: **A**
- **Why correct:** Triển khai Lambda với CodeDeploy chỉ hỗ trợ hai hook:
  1. **`BeforeAllowTraffic`**: Kích hoạt một hàm Lambda kiểm thử (validation function) TRƯỚC KHI lưu lượng truy cập bắt đầu chuyển sang phiên bản mới. Nếu hàm test báo lỗi hoặc trả về thất bại cho CodeDeploy, quá trình deployment sẽ dừng lại ngay lập tức và tự động rollback.
  2. **`AfterAllowTraffic`**: Kích hoạt sau khi toàn bộ lưu lượng đã chuyển sang phiên bản mới.
- **Why the others are wrong:** B `AfterAllowTraffic` chạy khi traffic đã chuyển xong, không ngăn chặn được lỗi tiếp cận người dùng. C và D (`BeforeInstall`, `ValidateService`) là các hook của EC2, không tồn tại trong Lambda deployment.
- 🧠 **Key point / trap:** Chạy validation test trước khi chuyển traffic sang Lambda version mới: Dùng hook **`BeforeAllowTraffic`** trong `appspec.yaml`.
- 📎 Source: `AWS CodeDeploy User Guide — AppSpec 'hooks' Section for AWS Lambda`.

### Question 45 — Answer: **A**
- **Why correct:** Trong mô hình Blue/Green của Amazon ECS với CodeDeploy:
  - Khi có test listener, CodeDeploy sẽ định tuyến lưu lượng thử nghiệm (test traffic) tới green task set thông qua hook `AllowTestTraffic`.
  - Hook **`AfterAllowTestTraffic`** là nơi bạn chỉ định một hàm Lambda để thực hiện các bài kiểm tra tích hợp (integration tests) thông qua test listener (port 8443) để đảm bảo container mới hoạt động hoàn hảo trước khi bắt đầu chuyển đổi lưu lượng thực tế (production traffic).
- **Why the others are wrong:** `BeforeInstall` và `AfterInstall` chạy trước khi test listener được kết nối. `BeforeAllowTraffic` chạy sau khi quá trình test kết thúc và chuẩn bị chuyển production traffic.
- 🧠 **Key point / trap:** Chạy integration test trên cổng Test Listener trong ECS Blue/Green deployment: Dùng hook **`AfterAllowTestTraffic`**.
- 📎 Source: `AWS CodeDeploy User Guide — AppSpec 'hooks' Section for Amazon ECS`.

### Question 46 — Answer: **A**
- **Why correct:** AWS CodeDeploy hỗ trợ tính năng **Automatic Rollbacks**. Lập trình viên có thể cấu hình Deployment Group tự động rollback trong hai trường hợp:
  1. Khi deployment gặp lỗi (lifecycle event hook trả về non-zero exit code).
  2. Khi các ngưỡng báo động CloudWatch Alarm bị vi phạm (ví dụ metric `HTTPCode_Target_5XX_Count` vượt ngưỡng). Khi alarm chuyển sang trạng thái `ALARM`, CodeDeploy lập tức dừng tiến trình và triển khai lại phiên bản hoạt động tốt gần nhất.
- **Why the others are wrong:** B tự viết script gọi CLI phức tạp và dễ phát sinh lỗi. C và D không phải là cơ chế rollback của CodeDeploy.
- 🧠 **Key point / trap:** Tự động rollback deployment khi ứng dụng bị lỗi 5XX: Bật **Rollback on alarm** trong CodeDeploy và liên kết với **CloudWatch Alarm**.
- 📎 Source: `AWS CodeDeploy User Guide — Configure Automatic Rollbacks`.

### Question 47 — Answer: **A**
- **Why correct:** AWS CodePipeline cung cấp loại action **Manual Approval** (`Category: Approval`, `Provider: Manual`). Khi pipeline chạy đến action này, nó sẽ tạm dừng và gửi thông báo qua Amazon SNS (được đăng ký tới email của người phê duyệt). Người có thẩm quyền chỉ cần bấm link trong email hoặc vào Console để xem xét và nhấn "Approve" hoặc "Reject".
- **Why the others are wrong:** B Lambda timeout tối đa chỉ được 15 phút, không thể sleep 24h. C SQS không tương tác dừng pipeline native. D Branch protection chỉ áp dụng khi merge pull request trong Git, không kiểm soát được quá trình deploy sau khi đã build artifact.
- 🧠 **Key point / trap:** Thêm bước phê duyệt thủ công trước khi deploy trong CodePipeline: Thêm action **Approval / Manual** kết hợp **Amazon SNS topic**.
- 📎 Source: `AWS CodePipeline User Guide — Add a Manual Approval Action`.

### Question 48 — Answer: **A**
- **Why correct:** Trước đây, CodePipeline dùng cơ chế Polling (định kỳ vài phút quét repo một lần) làm chậm trễ tiến trình CI/CD. AWS khuyến nghị cấu hình kích hoạt theo sự kiện (Event-driven): Khi có commit mới đẩy lên branch `main`, AWS CodeCommit sẽ phát sinh sự kiện `referenceUpdated` đẩy vào **Amazon EventBridge**. EventBridge rule sẽ bắt sự kiện này và kích hoạt CodePipeline chạy ngay lập tức trong vòng vài giây.
- **Why the others are wrong:** B CodePipeline không có nút chỉnh polling frequency. C tạo worker riêng chạy polling rất tốn kém và không chuẩn cloud-native. D SNS không nhận biết được thay đổi commit trong Git.
- 🧠 **Key point / trap:** Kích hoạt CodePipeline ngay khi có commit mới (thay thế polling): Sử dụng **Amazon EventBridge Rule** bắt sự kiện từ repository.
- 📎 Source: `AWS CodePipeline User Guide — Trigger Pipeline on Changes with EventBridge`.

### Question 49 — Answer: **A**
- **Why correct:** Quy trình triển khai chuẩn của AWS Serverless Application Model (SAM) CLI:
  1. `sam build`: Đóng gói mã nguồn và cài đặt dependencies vào thư mục `.aws-sam`.
  2. `sam deploy --guided` (hoặc `sam deploy -g`): Hướng dẫn người dùng qua giao diện dòng lệnh tương tác để nhập stack name, region, S3 deployment bucket, quyền IAM và lưu cấu hình vào `samconfig.toml`.
- **Why the others are wrong:** B, C, D chứa các lệnh không tồn tại trong SAM CLI (như `sam run`, `sam compile`, `sam publish`).
- 🧠 **Key point / trap:** Chuỗi lệnh deploy SAM chuẩn: **`sam build`** → **`sam deploy --guided`**.
- 📎 Source: `AWS SAM Developer Guide — Building and Deploying Serverless Applications`.

### Question 50 — Answer: **A**
- **Why correct:** Dòng khai báo `Transform: AWS::Serverless-2016-10-31` ở đầu template là macro bắt buộc để AWS CloudFormation nhận diện đây là template SAM. Macro này sẽ biên dịch các cú pháp tài nguyên serverless viết tắt (như `AWS::Serverless::Function`, `AWS::Serverless::Api`, `AWS::Serverless::SimpleTable`) thành các tài nguyên CloudFormation mở rộng tương đương (`AWS::Lambda::Function`, `AWS::IAM::Role`, `AWS::ApiGateway::RestApi`).
- **Why the others are wrong:** B là phiên bản định dạng template chuẩn của CloudFormation, không kích hoạt SAM macro. C là một resource type, không phải header chuyển đổi. D chỉ là phần mô tả.
- 🧠 **Key point / trap:** Macro bắt buộc của SAM trong CloudFormation template: **`Transform: AWS::Serverless-2016-10-31`**.
- 📎 Source: `AWS SAM Developer Guide — Anatomy of a SAM Template`.

### Question 51 — Answer: **A**
- **Why correct:** Hàm nội tại **`!Ref`** khi được gọi với tên tài nguyên `AWS::S3::Bucket` sẽ trả về chính **tên của bucket (Bucket Name)**. Do đó, để truyền tên bucket vào biến môi trường của Lambda, chỉ cần viết `!Ref MyBucketResource`.
- **Why the others are wrong:** B `!GetAtt MyBucketResource.Arn` trả về chuỗi ARN đầy đủ (`arn:aws:s3:::bucket-name`), không phải tên bucket. C `!ImportValue` dùng để lấy giá trị output được export từ một stack CloudFormation khác. D `!Sub` trong trường hợp này không lấy được tên bucket tạo tự động ngẫu nhiên.
- 🧠 **Key point / trap:** Với tài nguyên S3 Bucket trong CloudFormation: **`!Ref` trả về Bucket Name**; **`!GetAtt Resource.Arn` trả về Bucket ARN**.
- 📎 Source: `AWS CloudFormation User Guide — Ref Function`.

### Question 52 — Answer: **A**
- **Why correct:** Chính sách **Rolling with additional batch** của Elastic Beanstalk:
  - Khởi chạy một batch instance mới bổ sung trước khi đưa bất kỳ instance cũ nào ra khỏi trạng thái phục vụ.
  - Sau khi batch mới vượt qua health check, phiên bản mới được deploy tiếp cho các instance cũ theo từng đợt.
  - Đảm bảo hệ thống luôn duy trì **100% dung lượng (Full capacity)** trong suốt quá trình cập nhật mà không làm giảm hiệu năng phục vụ người dùng.
- **Why the others are wrong:** B `All at once` gây downtime toàn bộ. C `Rolling` làm giảm dung lượng của hệ thống trong lúc đang deploy batch đầu tiên. D Blue/Green yêu cầu tạo environment URL thứ hai và swap CNAME bên ngoài.
- 🧠 **Key point / trap:** Beanstalk deployment: Cần **duy trì 100% dung lượng** mà không tạo môi trường mới → **Rolling with additional batch**.
- 📎 Source: `AWS Elastic Beanstalk Developer Guide — Deployment Policies`.

### Question 53 — Answer: **A**
- **Why correct:** Chính sách **Immutable** của Elastic Beanstalk:
  1. Khởi chạy một Auto Scaling group hoàn toàn mới song song với ASG hiện tại và deploy phiên bản mới lên các instance mới này.
  2. Kiểm tra health check kỹ lưỡng. Nếu thành công, toàn bộ traffic được chuyển sang và ASG cũ bị terminate.
  3. Nếu phiên bản mới bị lỗi hoặc fail health check, Beanstalk chỉ việc terminate ASG mới mà **không hề làm ảnh hưởng hay thay đổi bất kỳ thứ gì trên các instance cũ đang chạy** → Rollback an toàn và nhanh nhất, zero-downtime.
- **Why the others are wrong:** Rolling và All at once làm thay đổi trực tiếp (in-place) trên các instance hiện tại. Traffic splitting là phương pháp thử nghiệm canary theo tỷ lệ phần trăm chứ không phải tạo song song toàn bộ rồi swap an toàn như Immutable.
- 🧠 **Key point / trap:** Beanstalk: Triển khai trên ASG tạm thời mới, an toàn tuyệt đối, rollback ngay không ảnh hưởng môi trường cũ → **Immutable Deployment**.
- 📎 Source: `AWS Elastic Beanstalk Developer Guide — Immutable Environment Updates`.

### Question 54 — Answer: **A**
- **Why correct:** Phân biệt rõ hai loại IAM Role trong Amazon ECS Task Definition:
  1. **Task Execution Role (Hạ tầng / Agent):** Dùng bởi ECS Container Agent (hoặc Fargate infrastructure) để thiết lập môi trường: kéo image từ ECR (`ecr:GetAuthorizationToken`, `ecr:BatchGetImage`), gửi container log tới CloudWatch Logs, hoặc đọc bí mật từ Secrets Manager/SSM.
  2. **Task Role (Ứng dụng / Container):** Cấp quyền trực tiếp cho mã nguồn ứng dụng chạy bên trong container để tương tác với các dịch vụ AWS (như gọi `dynamodb:PutItem`, đọc S3, gửi tin nhắn SQS).
- **Why the others are wrong:** B đảo ngược hoàn toàn chức năng của hai role. C Fargate quản lý serverless nên không cấp quyền qua phần cứng host. D hardcode access key trong Docker image là vi phạm bảo mật nghiêm trọng.
- 🧠 **Key point / trap:** **Task Execution Role** = ECS Agent dùng (pull image ECR, ghi logs). **Task Role** = Code trong container dùng (gọi DynamoDB, S3).
- 📎 Source: `Amazon ECS Developer Guide — Task Execution Role vs Task Role`.

### Question 55 — Answer: **A**
- **Why correct:** Để ghi metric tùy chỉnh độ phân giải cao (**High-Resolution Metric**) với chu kỳ 1 giây trong Amazon CloudWatch, trong lệnh gọi `PutMetricData` (hoặc file cấu hình agent), lập trình viên phải đặt tham số **`StorageResolution = 1`**. Điều này cho phép lưu trữ và truy vấn metric ở các chu kỳ 1s, 5s, 10s, 30s hoặc bội số của 60s, và cho phép tạo High-Resolution Alarm với chu kỳ 10s hoặc 30s.
- **Why the others are wrong:** B không thể đặt chu kỳ alarm 1 giây nếu metric không được xuất bản với `StorageResolution = 1`. C Detailed Monitoring của EC2 chỉ có độ phân giải tối đa là 1 phút (không phải 1 giây). D CloudWatch hỗ trợ 1 giây qua High-Resolution metrics.
- 🧠 **Key point / trap:** Metric độ phân giải cao 1 giây trong CloudWatch: Đặt tham số **`StorageResolution = 1`** trong lệnh gọi `PutMetricData`.
- 📎 Source: `Amazon CloudWatch User Guide — Publishing High-Resolution Metrics`.

### Question 56 — Answer: **A**
- **Why correct:** Trong Amazon CloudWatch, một metric được xác định duy nhất bởi: `Namespace + MetricName + Danh sách Dimensions đầy đủ`. CloudWatch **không tự động tổng hợp (rollup/aggregate)** dữ liệu trên các dimension khác nhau đối với custom metrics. Nếu bạn publish metric với dimensions `{Environment=Prod, Region=us-east-1}`, bạn chỉ có thể query đúng cặp dimension này; nếu chỉ query `{Environment=Prod}`, CloudWatch sẽ coi đó là một chuỗi thời gian hoàn toàn khác và trả về không có dữ liệu (No Data), trừ khi dùng tính năng Metric Math (`SEARCH`).
- **Why the others are wrong:** B custom metrics có thể có tối đa 30 dimensions. C detailed monitoring chỉ dành cho dịch vụ AWS (như EC2), không áp dụng cho logic dimension của custom metric. D custom metrics được lưu trữ tối đa 15 tháng tùy độ phân giải.
- 🧠 **Key point / trap:** CloudWatch **không tự động gộp (aggregate) các dimensions của custom metric**. Query bắt buộc phải khớp chính xác bộ dimensions đã xuất bản, hoặc phải dùng **Metric Math `SEARCH()`**.
- 📎 Source: `Amazon CloudWatch User Guide — Metric Dimensions`.

### Question 57 — Answer: **A**
- **Why correct:** **CloudWatch Embedded Metric Format (EMF)** cho phép ứng dụng (đặc biệt là Lambda và ECS/Fargate) ghi các dòng log có cấu trúc JSON đặc biệt (`_aws.CloudWatchMetrics`) ra `stdout`. Dịch vụ CloudWatch Logs khi nhận log sẽ tự động trích xuất các thông số đó thành Custom Metrics trong CloudWatch một cách bất đồng bộ mà **không cần ứng dụng phải gọi API `PutMetricData` đồng bộ**, giúp giảm tối đa độ trễ, tránh lỗi throttle API và tiết kiệm chi phí.
- **Why the others are wrong:** B ghi vào S3 không tự động biến thành CloudWatch metric thời gian thực. C đưa vào SQS và dựng EC2 làm phức tạp hóa kiến trúc serverless. D chạy thread riêng trong Lambda có thể bị đóng băng khi Lambda container freeze sau khi trả về response.
- 🧠 **Key point / trap:** Xuất bản custom metric tần suất cực lớn từ Lambda mà không bị throttle và không tốn tiền API `PutMetricData` → Dùng **Embedded Metric Format (EMF)**.
- 📎 Source: `Amazon CloudWatch User Guide — Ingesting High-Cardinality Metrics with EMF`.

### Question 58 — Answer: **A**
- **Why correct:** **CloudWatch Metric Filter** cho phép quét các log event trong Log Group theo pattern đã định (ví dụ tìm từ khóa `FATAL_ERROR`) và tự động tăng giá trị của một Custom Metric tương ứng. Sau đó, chỉ cần tạo một CloudWatch Alarm trên metric này với điều kiện `Threshold > 5` trong chu kỳ 10 phút và gắn action gửi thông báo vào SNS topic. Giải pháp này hoàn toàn không cần can thiệp hay sửa đổi mã nguồn ứng dụng.
- **Why the others are wrong:** B polling log bằng Lambda tốn kém và không chuẩn hóa. C Athena chạy theo cron không đảm bảo cảnh báo thời gian thực. D CloudTrail Insights giám sát bất thường của các lời gọi API quản trị, không đọc log bên trong ứng dụng.
- 🧠 **Key point / trap:** Trích xuất cảnh báo từ file log mà không cần sửa code ứng dụng → Tạo **Metric Filter trên CloudWatch Log Group** → Liên kết với **CloudWatch Alarm**.
- 📎 Source: `Amazon CloudWatch Logs User Guide — Creating Metric Filters`.

### Question 59 — Answer: **A**
- **Why correct:** **Amazon CloudWatch Synthetics Canaries** là các đoạn script (viết bằng Node.js hoặc Python sử dụng Puppeteer/Playwright) chạy theo lịch trình định kỳ (ví dụ mỗi 5 phút) để mô phỏng chính xác hành vi của người dùng: gửi HTTP POST request, kiểm tra mã HTTP status 200, kiểm tra nội dung response và đo lường độ trễ. Canaries giúp giám sát endpoint từ ngoài vào trong ngay cả khi không có người dùng thật đang truy cập.
- **Why the others are wrong:** B CloudTrail chỉ ghi lại các lệnh gọi AWS API quản trị. C VPC Flow Logs chỉ ghi lại metadata IP/port ở tầng network. D X-Ray Sampling rules chỉ điều tiết tỷ lệ trace request thật.
- 🧠 **Key point / trap:** Giám sát chủ động (Synthetic monitoring) endpoint API theo định kỳ để phát hiện lỗi trước người dùng → **CloudWatch Synthetics Canaries**.
- 📎 Source: `Amazon CloudWatch User Guide — Using Synthetic Monitoring`.

### Question 60 — Answer: **A, B**
- **Why correct:** **CloudWatch Logs Subscription Filters** hỗ trợ truyền log theo thời gian thực (real-time stream) tới 3 dịch vụ AWS sau:
  1. **Amazon Kinesis Data Streams**
  2. **AWS Lambda**
  3. **Amazon Kinesis Data Firehose**
  Từ Kinesis Data Streams hoặc Lambda, lập trình viên có thể dễ dàng chuyển tiếp dữ liệu log vào Elasticsearch/OpenSearch cluster.
- **Why the others are wrong:** C S3 không thể làm đích đến trực tiếp của Subscription Filter (phải thông qua Kinesis Data Firehose; lệnh Export to S3 là batch chứ không phải real-time). D và E SNS và DynamoDB không được hỗ trợ làm direct destination cho Subscription Filter.
- 🧠 **Key point / trap:** 3 đích đến trực tiếp duy nhất của CloudWatch Logs Subscription Filter: **Lambda**, **Kinesis Data Streams**, và **Kinesis Data Firehose**.
- 📎 Source: `Amazon CloudWatch Logs User Guide — Real-time Processing with Subscriptions`.

### Question 61 — Answer: **A**
- **Why correct:** Trong kiến trúc AWS X-Ray, mã nguồn ứng dụng sử dụng X-Ray SDK để tạo các trace subsegment, sau đó gửi các gói tin UDP này tới cổng **UDP 2000** cục bộ. **AWS X-Ray Daemon** là một tiến trình chạy ngầm (chạy trên EC2, ECS sidecar, hoặc On-Premises) có nhiệm vụ lắng nghe trên cổng UDP 2000, gom nhóm các segment này lại và thực hiện gọi HTTPS an toàn lên dịch vụ AWS X-Ray API (`xray:PutTraceSegments`).
- **Why the others are wrong:** B CloudWatch Agent gửi metric và log, không đảm nhận việc nhận UDP trace của X-Ray SDK (trừ khi dùng OpenTelemetry collector). C SSM Agent dùng để quản lý máy ảo từ xa. D CodeDeploy Agent dùng để triển khai mã nguồn.
- 🧠 **Key point / trap:** Thành phần chạy ngầm lắng nghe port **UDP 2000** để gửi trace segments lên X-Ray trên EC2/ECS → **AWS X-Ray Daemon**.
- 📎 Source: `AWS X-Ray Developer Guide — The AWS X-Ray Daemon`.

### Question 62 — Answer: **A**
- **Why correct:** Phân biệt rõ giữa Annotation và Metadata trong AWS X-Ray:
  - **Annotations**: Là các cặp key-value đơn giản (string, number, boolean) được **đánh chỉ mục (Indexed)**. Dùng để tìm kiếm, lọc và phân nhóm trace trên X-Ray Console hoặc thông qua Filter Expressions (ví dụ `annotation.customerTier = "PLATINUM"`).
  - **Metadata**: Có thể chứa các đối tượng tùy ý phức tạp (như mảng, payload JSON lớn), **không được đánh chỉ mục (Not Indexed)**. Dùng để lưu dữ liệu phục vụ điều tra gỡ lỗi khi đã mở một trace cụ thể.
- **Why the others are wrong:** B đưa payload lớn vào annotation sẽ vi phạm giới hạn kích thước và số lượng annotation của X-Ray. C metadata không được đánh chỉ mục nên không thể dùng để filter hay search trace. D gán ngược chức năng của hai thành phần.
- 🧠 **Key point / trap:** **Annotations = Indexed (dùng để tìm kiếm, filter trên Service Map)**; **Metadata = Not Indexed (dùng để lưu dữ liệu debug chi tiết)**.
- 📎 Source: `AWS X-Ray Developer Guide — Annotations and Metadata`.

### Question 63 — Answer: **A**
- **Why correct:** Quy tắc lấy mẫu (**Sampling Rules**) của AWS X-Ray bao gồm hai thông số chính:
  1. **Reservoir size (Hồ chứa)**: Số lượng request tối thiểu chắc chắn được ghi nhận (trace) mỗi giây. Ở đây yêu cầu "ít nhất 1 request mỗi giây" → Đặt `Reservoir = 1`.
  2. **Fixed rate (Tỷ lệ cố định)**: Tỷ lệ phần trăm các request bổ sung vượt quá kích thước reservoir sẽ được lấy mẫu. Ở đây yêu cầu 5% → Đặt `Fixed rate = 0.05` (hoặc 5%).
- **Why the others are wrong:** B đặt reservoir 50 và rate 1% không đúng yêu cầu. C đặt 100% sẽ làm tăng chi phí tối đa. D CloudWatch Logs không thay thế được tính năng trace phân tán của X-Ray.
- 🧠 **Key point / trap:** Cấu hình X-Ray Sampling: **`Reservoir`** = số trace cố định được ghi nhận mỗi giây; **`FixedRate`** = % các request vượt reservoir được lấy mẫu tiếp theo.
- 📎 Source: `AWS X-Ray Developer Guide — Sampling Rules`.

### Question 64 — Answer: **A**
- **Why correct:** Khi các microservices giao tiếp qua HTTP, ngữ cảnh phân tán (Distributed Trace Context) phải được truyền dọc theo chuỗi gọi hàm để X-Ray liên kết các segment thành một Trace Tree hoàn chỉnh. Service gọi (Service A) phải chèn HTTP header **`X-Amzn-Trace-Id`** vào request gửi sang Service B:
  `X-Amzn-Trace-Id: Root=1-5759e988-bd862e3fe1be46a994272793;Parent=53995cbe419fe7c0;Sampled=1`
  Service B đọc header này để tạo subsegment con nối tiếp vào segment cha.
- **Why the others are wrong:** B truyền qua S3 làm tăng độ trễ và không chuẩn hóa. C việc nằm cùng subnet không tự động liên kết luồng gọi tầng ứng dụng. D X-Ray không tự động biết các cuộc gọi HTTP nếu không có trace header được truyền qua SDK.
- 🧠 **Key point / trap:** Truyền context X-Ray giữa các microservices qua HTTP: Bắt buộc inject header **`X-Amzn-Trace-Id`**.
- 📎 Source: `AWS X-Ray Developer Guide — Tracing Header`.

### Question 65 — Answer: **A, B**
- **Why correct:** Hai phương pháp hợp lệ để cập nhật file tĩnh trên CloudFront edge cache:
  1. **Tạo CloudFront Invalidation:** Gửi lệnh invalidate đường dẫn `/main.js` (hoặc `/*`) để xóa bỏ file đang lưu tại các edge location, buộc edge fetch phiên bản mới từ S3 trong lần request tiếp theo.
  2. **Dùng tên file có version (Object Versioning):** Đây là best practice của AWS (ví dụ `main.v2.js` hoặc `main.abcdef12.js`). Khi code HTML trỏ tới tên file mới, CloudFront sẽ xem đó là một tài nguyên hoàn toàn mới và tải ngay lập tức mà không cần tốn chi phí invalidation.
- **Why the others are wrong:** C đổi tên bucket làm gián đoạn toàn bộ website. D xóa distribution gây downtime lớn và mất thời gian tạo lại (10-15 phút). E Minimum TTL không nhận giá trị âm (-1) và không xóa được các object đã lỡ được cache.
- 🧠 **Key point / trap:** Cập nhật nội dung cache CloudFront ngay lập tức: Dùng **CloudFront Invalidation (`/*`)** hoặc best practice là **Object Versioning trong tên file (`app.v2.js`)**.
- 📎 Source: `Amazon CloudFront Developer Guide — Updating Existing Files Using Object Versioning & Invalidations`.
