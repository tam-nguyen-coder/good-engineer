# ✅ Answers & Explanations — DVA-C02 Mock Exam 03

> Chỉ mở sau khi đã hoàn thành toàn bộ 65 câu trong [questions.md](questions.md) với đồng hồ bấm giờ 130 phút.
> Back to [mock index](../README.md) · [master plan](../../DVA-C02-STUDY-PLAN.md)

**Answer key:** 1-A · 2-A · 3-A · 4-A · 5-A · 6-A · 7-A · 8-A · 9-A · 10-A · 11-A · 12-A · 13-A · 14-A · 15-A · 16-A · 17-A · 18-A · 19-A · 20-A · 21-A · 22-A · 23-A · 24-A · 25-A · 26-A · 27-A · 28-A · 29-A · 30-A · 31-A · 32-A · 33-A · 34-A · 35-A · 36-A · 37-A · 38-A · 39-A · 40-A · 41-A · 42-A · 43-A · 44-A · 45-A · 46-A · 47-A · 48-A · 49-A · 50-A · 51-A · 52-A · 53-A · 54-A · 55-A · 56-A · 57-A · 58-A · 59-A · 60-A · 61-A · 62-AB · 63-A · 64-A · 65-A

> 📌 Với câu `Multi` (câu 62), chỉ tính **đúng** khi chọn đủ và đúng cả hai phương án — không có điểm một phần.

---

## 📊 Bảng chấm điểm theo Domain

| Domain | Tỉ trọng | Câu số | Số đúng / Tổng | % | Ngưỡng đạt chuẩn (≥85%) |
|---|---|---|---|---|---|
| **Domain 1 — Development with AWS Services** | 32% | 1 – 21 | ___ / 21 | ___ % | ≥ 18 / 21 (85.7%) |
| **Domain 2 — Security** | 26% | 22 – 38 | ___ / 17 | ___ % | ≥ 14 / 17 (82.4%) |
| **Domain 3 — Deployment** | 24% | 39 – 54 | ___ / 16 | ___ % | ≥ 14 / 16 (87.5%) |
| **Domain 4 — Troubleshooting and Optimization** | 18% | 55 – 65 | ___ / 11 | ___ % | ≥ 9 / 11 (81.8%) |
| **TỔNG CỘNG** | **100%** | **1 – 65** | **___ / 65** | **___ %** | **≥ 55 / 65 (84.6% ~ 85%)** |

> ⚠️ **Đánh giá kết quả Mock 03 (Bộ đề nâng cao - Boss Exam):**
> - **≥ 55/65 (≥ 85%):** Đẳng cấp chuyên gia! Bạn đã làm chủ hoàn toàn các tình huống phức tạp nhất (tính toán dung lượng, xử lý ngoại lệ biên, thiết kế bảo mật OIDC/mTLS, và tối ưu hiệu năng sâu). Bạn chắc chắn 100% đỗ kỳ thi thật với điểm số cao (850 - 950/1000).
> - **47 – 54/65 (72% – 84%):** Đạt ngưỡng an toàn. Xem kỹ lại các bẫy về công thức tính toán RCU/WCU và các header đặc thù của S3/CloudFront.
> - **< 47/65 (< 72%):** Hãy bình tĩnh đọc lại toàn bộ phần giải thích bên dưới, đặc biệt là các ghi chú 🧠 **Key point / trap**.

---

## 📝 Giải thích chi tiết 65 câu hỏi

### Question 1 — Answer: **A**
- **Why correct:** **Lambda Destinations** (On-Failure Destination) là giải pháp hiện đại và tối ưu nhất của AWS để xử lý lỗi bất đồng bộ. Khi hàm gặp ngoại lệ không được bắt, Lambda Destinations sẽ tự động gửi một gói tin JSON chứa đầy đủ: bản ghi gọi hàm gốc (`requestPayload`), thông báo lỗi (`errorMessage`), loại lỗi (`errorType`), và **toàn bộ stack trace** sang đích đến (SQS, SNS, EventBridge, hoặc Lambda khác) mà không cần can thiệp vào mã nguồn hàm.
- **Why the others are wrong:** B sai vì Dead-Letter Queue (DLQ) truyền thống chỉ gửi đúng payload đầu vào ban đầu, hoàn toàn không chứa mã lỗi hay stack trace. C sai vì phải viết code thủ công và nếu hàm bị timeout (hết thời gian thực thi) hoặc bị kill bởi OOM thì khối `try/catch` sẽ không bao giờ được chạy. D sai vì chỉ tăng số lần thử lại chứ không chụp được thông tin lỗi khi thử lại thất bại.
- 🧠 **Key point / trap:** So sánh DLQ vs Destinations: **DLQ** chỉ chứa payload gốc; **Lambda Destinations** chứa cả payload gốc + kết quả trả về/lỗi + stack trace.
- 📎 Source: `AWS Lambda Developer Guide — Configuring destinations for asynchronous invocation`.

---

### Question 2 — Answer: **A**
- **Why correct:** Cách tính RCU cho giao dịch `TransactGetItems`:
  1. `TransactGetItems` thực hiện đọc có tính nhất quán giao dịch (transactional read), tiêu tốn **gấp đôi (2x)** lượng RCU so với đọc Strongly Consistent.
  2. Với 10 item có kích thước 3 KB:
     - Kích thước 3 KB làm tròn lên bội số 4 KB tiếp theo: `ceil(3 KB / 4 KB) = 1` khối 4 KB.
     - Đọc thông thường = 1 RCU.
     - Đọc giao dịch = `1 RCU × 2 = 2 RCU` cho mỗi item.
     - 10 item = `10 × 2 = 20 RCU`.
  3. Với 5 item có kích thước 7 KB:
     - Kích thước 7 KB làm tròn lên bội số 4 KB tiếp theo: `ceil(7 KB / 4 KB) = 2` khối 4 KB.
     - Đọc thông thường = 2 RCU.
     - Đọc giao dịch = `2 RCU × 2 = 4 RCU` cho mỗi item.
     - 5 item = `5 × 4 = 20 RCU`.
  4. Tổng RCU cho 1 giao dịch: `20 + 20 = 40 RCU`.
  5. Ứng dụng thực hiện 4 giao dịch mỗi giây: `40 RCU × 4 = 160 RCU`.
- **Why the others are wrong:** B (80 RCU) là quên nhân đôi cho hệ số giao dịch (chỉ tính theo Strongly Consistent). C (40 RCU) chỉ là dung lượng cho 1 giây nếu chỉ có 1 transaction. D (240 RCU) tính sai kích thước item.
- 🧠 **Key point / trap:** Transactional Read (`TransactGetItems`) = **2 × Strongly Consistent Read** = **`ceil(Size / 4 KB) × 2`** RCUs per item.
- 📎 Source: `Amazon DynamoDB Developer Guide — Capacity unit consumption for transactions`.

---

### Question 3 — Answer: **A**
- **Why correct:** AWS Lambda cho phép tùy chỉnh dung lượng bộ nhớ lưu trữ tạm thời **ephemeral storage (`/tmp`)** từ **512 MB lên đến 10,240 MB (10 GB)**. Điều này cho phép các tác vụ xử lý đồ họa, nén video hoặc học máy có thể tải các tệp tin lớn (lên tới 6 GB) trực tiếp về ổ đĩa cục bộ của container để xử lý bằng các công cụ native như FFmpeg mà không bị giới hạn bộ nhớ RAM.
- **Why the others are wrong:** B sai vì Lambda không hỗ trợ gắn trực tiếp Amazon EBS volumes (chỉ hỗ trợ Amazon EFS). C sai vì dung lượng RAM và dung lượng đĩa `/tmp` được cấu hình độc lập; tăng RAM không tự động tăng dung lượng đĩa `/tmp`. D sai vì Lambda không thể mount S3 như một hệ thống tệp POSIX cục bộ.
- 🧠 **Key point / trap:** Xử lý file lớn trong Lambda: Tùy chỉnh **`/tmp` ephemeral storage (lên tới 10 GB)**. Nếu cần hệ thống tệp dùng chung bền vững → Gắn **Amazon EFS**.
- 📎 Source: `AWS Lambda Developer Guide — Configuring ephemeral storage`.

---

### Question 4 — Answer: **A**
- **Why correct:** **Amazon API Gateway WebSocket API** cung cấp kết nối hai chiều (bidirectional), duy trì liên tục (stateful) giữa client và backend. API Gateway quản lý việc bắt tay kết nối và ánh xạ qua các route đặc thù: `$connect` (khi client kết nối), `$disconnect` (khi ngắt kết nối), và các custom route khi client gửi dữ liệu. Để server chủ động đẩy dữ liệu (push) về client bất kỳ lúc nào, backend chỉ cần gọi API **`@connections`** với định danh kết nối `connectionId` của client đó.
- **Why the others are wrong:** B sai vì kỹ thuật short polling gây quá tải API, lãng phí request và có độ trễ lớn. C sai vì HTTP APIs không hỗ trợ WebSocket hai chiều thực sự. D sai vì tự dựng cụm EC2 chạy socket.io đòi hỏi quản lý hạ tầng, auto scaling phức tạp và chi phí vận hành cao hơn nhiều so với dịch vụ serverless quản lý trọn gói của API Gateway.
- 🧠 **Key point / trap:** Giao tiếp hai chiều thời gian thực serverless → **API Gateway WebSocket API** (lưu `connectionId` và push qua endpoint `@connections`).
- 📎 Source: `Amazon API Gateway Developer Guide — Working with WebSocket APIs`.

---

### Question 5 — Answer: **A**
- **Why correct:** Để tránh việc bán quá số lượng hàng tồn kho (overselling) trong các đợt flash-sale, thao tác trừ kho bắt buộc phải có điều kiện kiểm tra tồn kho còn đủ hay không. Lệnh `UpdateItem` kết hợp với **`ConditionExpression: "stock >= :val"`** đảm bảo rằng việc trừ kho chỉ được thực hiện nếu lượng hàng hiện tại lớn hơn hoặc bằng lượng mua. Nếu hai khách hàng mua cùng lúc và khách hàng thứ hai khiến stock < 0, DynamoDB sẽ từ chối thao tác và trả về lỗi `ConditionalCheckFailedException`.
- **Why the others are wrong:** B sai vì Atomic Counter (`ADD stock :negVal`) chỉ thực hiện cộng/trừ số học vô điều kiện, không thể kiểm tra giá trị sau khi trừ, do đó sẽ làm `stock` âm nếu có nhiều người mua cùng lúc. C sai vì đọc trước (`GetItem`) rồi ghi sau (`PutItem`) là hai thao tác tách rời, gây ra hiện tượng Race Condition (hai người đọc cùng thấy còn 1 hàng và cả hai cùng gửi lệnh mua). D sai vì DAX không cung cấp cơ chế khóa lạc quan để chặn overselling.
- 🧠 **Key point / trap:** Tránh overselling / Race condition trong DynamoDB: Dùng **`UpdateItem` với `ConditionExpression`** (chứ KHÔNG dùng Atomic Counter thuần túy vì Atomic Counter không có điều kiện chặn số âm).
- 📎 Source: `Amazon DynamoDB Developer Guide — Working with items: Conditional updates`.

---

### Question 6 — Answer: **A**
- **Why correct:** Giới hạn kích thước tin nhắn tối đa của Amazon SQS là **256 KB** (đây là hard limit không thể nâng). Để gửi các payload lớn từ 15 MB đến 200 MB (tối đa lên đến 2 GB), AWS cung cấp thư viện **Amazon SQS Extended Client Library** (dành cho Java và Python). Thư viện này tự động tải payload lớn lên một Amazon S3 bucket được chỉ định, sau đó gửi một tin nhắn chứa con trỏ tham chiếu S3 vào hàng đợi SQS. Khi consumer nhận tin, thư viện sẽ tự động tải payload từ S3 về một cách trong suốt.
- **Why the others are wrong:** B sai vì 256 KB là giới hạn phần cứng của dịch vụ SQS, AWS Support không thể tăng giới hạn này. C sai vì nén gzip các file ảnh/scan y tế độ phân giải cao không bao giờ có thể nén từ 200 MB xuống dưới 256 KB được. D sai vì Kinesis Data Streams cũng giới hạn kích thước mỗi bản ghi tối đa chỉ 1 MB.
- 🧠 **Key point / trap:** Tin nhắn SQS vượt quá 256 KB (lên tới 2 GB) → Dùng **Amazon SQS Extended Client Library** kết hợp **Amazon S3**.
- 📎 Source: `Amazon SQS Developer Guide — Managing Amazon SQS messages with Amazon S3 (Amazon SQS Extended Client)`.

---

### Question 7 — Answer: **A**
- **Why correct:** Theo mặc định, SQS FIFO queue hỗ trợ tối đa 300 transactions/giây (hoặc 3,000 TPS nếu dùng batching). Để hỗ trợ lưu lượng cực lớn lên tới hàng chục nghìn TPS (như 15,000 TPS trong kịch bản), AWS cung cấp chế độ **High Throughput for FIFO Queues**. Lập trình viên kích hoạt bằng cách đặt **`DeduplicationScope` thành `messageGroup`** và **`FifoThroughputLimit` thành `perMessageGroupId`**. Khi mỗi khách hàng có một `MessageGroupId` riêng biệt, SQS sẽ phân bổ tải song song trên nhiều partition nội bộ, cho phép mở rộng thông lượng theo tỷ lệ số lượng message group.
- **Why the others are wrong:** B sai vì SQS Standard không đảm bảo thứ tự nghiêm ngặt (FIFO) và có thể gây trùng lặp tin nhắn. C sai vì tự tạo 50 queue riêng biệt và tự băm làm tăng đáng kể độ phức tạp kiến trúc và bảo trì. D sai vì tăng visibility timeout không làm tăng thông lượng xử lý của hàng đợi.
- 🧠 **Key point / trap:** SQS FIFO cần vượt qua ngưỡng 3,000 TPS (đạt 30,000+ TPS) → Bật **High Throughput Mode** với `DeduplicationScope: messageGroup` và `FifoThroughputLimit: perMessageGroupId`.
- 📎 Source: `Amazon SQS Developer Guide — High throughput for FIFO queues`.

---

### Question 8 — Answer: **A**
- **Why correct:** **AWS Lambda Function URLs** cung cấp một endpoint HTTPS chuyên dụng trực tiếp cho hàm Lambda mà không cần phải triển khai hay trả phí cho Amazon API Gateway hay Application Load Balancer. Khi làm việc với các webhook công khai từ bên thứ ba (như Stripe), ta cấu hình `AuthType: NONE` (bảo mật qua chữ ký webhook ở tầng ứng dụng) và cấu hình CORS trực tiếp trên Function URL. Đây là giải pháp đơn giản nhất và tiết kiệm chi phí nhất (hoàn toàn miễn phí thêm).
- **Why the others are wrong:** B và C hoạt động được nhưng phát sinh thêm chi phí duy trì hàng tháng và phức tạp hóa cấu hình không cần thiết cho một webhook đơn lẻ. D sai vì CloudFront không thể trỏ trực tiếp vào ARN nội bộ của Lambda mà không thông qua Function URL hoặc API Gateway/ALB.
- 🧠 **Key point / trap:** Cần endpoint HTTPS trực tiếp cho 1 hàm Lambda đơn lẻ (webhook), chi phí thấp nhất, không cần tính năng nâng cao của API Gateway → **Lambda Function URLs (`AuthType: NONE`)**.
- 📎 Source: `AWS Lambda Developer Guide — Lambda function URLs`.

---

### Question 9 — Answer: **A**
- **Why correct:** Amazon DynamoDB Global Tables sử dụng cơ chế giải quyết xung đột **Last Writer Wins (LWW)**. Khi có hai thao tác ghi đồng thời vào cùng một thuộc tính ở hai Region khác nhau, DynamoDB sẽ so sánh mốc thời gian (timestamp) mà các bản ghi được áp dụng tại các Region nội bộ và bản ghi có timestamp muộn nhất sẽ được chấp nhận ghi đè lên toàn bộ các Region bản sao.
- **Why the others are wrong:** B sai vì DynamoDB Global Tables không sử dụng mô hình two-phase locking để trả về lỗi xung đột giao dịch xuyên Region. C và D là các đáp án phi lý không có trong kiến trúc phân tán của DynamoDB.
- 🧠 **Key point / trap:** Giải quyết xung đột ghi đồng thời trong DynamoDB Global Tables: Cơ chế **Last Writer Wins (LWW)** dựa trên reconciliation timestamps.
- 📎 Source: `Amazon DynamoDB Developer Guide — Conflict resolution in Global Tables`.

---

### Question 10 — Answer: **A**
- **Why correct:** Trong AWS Step Functions, trạng thái **`Map` state ở chế độ Distributed Mode** được thiết kế riêng để xử lý song song dữ liệu quy mô lớn (lên tới hàng triệu đối tượng S3 hoặc hàng gigabyte dữ liệu). Chế độ này sử dụng đối tượng `ItemReader` để đọc danh sách tệp trực tiếp từ Amazon S3 mà không bị giới hạn 25,000 event trong execution history của Standard workflow, và có thể mở rộng tới **10,000 child workflow executions** chạy đồng thời.
- **Why the others are wrong:** B sai vì xử lý 500,000 tệp trong một hàm Lambda đơn lẻ sẽ vượt quá giới hạn thời gian chạy 15 phút và giới hạn bộ nhớ của Lambda. C sai vì trạng thái `Parallel` chỉ dùng để chạy cố định một số nhánh độc lập xác định từ trước, không thể scale động cho 500,000 tác vụ. D sai vì Express Workflow có thời gian chạy tối đa chỉ 5 phút.
- 🧠 **Key point / trap:** Xử lý hàng trăm nghìn tệp trên S3 hoặc tập dữ liệu khổng lồ trong Step Functions → **Distributed Map state (`ItemReader` from S3)**.
- 📎 Source: `AWS Step Functions Developer Guide — Using Distributed Map in Step Functions`.

---

### Question 11 — Answer: **A**
- **Why correct:** Amazon API Gateway có một giới hạn cứng (hard limit) là **29 giây cho Integration Timeout**. Giới hạn này áp dụng cho cả REST APIs và HTTP APIs và **không thể yêu cầu tăng quota**. Khi backend Lambda chạy lâu hơn 29 giây (ở đây là 45s - 3 phút), API Gateway sẽ tự động ngắt kết nối và trả về lỗi `HTTP 504 Gateway Timeout`. Giải pháp chuẩn của AWS là chuyển sang mô hình xử lý bất đồng bộ: API Gateway gọi Lambda bất đồng bộ (`X-Amz-Invocation-Type: Event`) hoặc khởi chạy một AWS Step Functions execution, lập tức trả về mã `HTTP 202 Accepted` kèm theo một `taskId`, sau đó client sẽ thăm dò (polling) hoặc nhận webhook khi hoàn thành.
- **Why the others are wrong:** B sai vì tăng memory không giải quyết được nếu thuật toán vẫn mất hơn 29 giây. C sai vì giới hạn 29s của API Gateway là hard limit không thể nâng. D sai vì HTTP API cũng có giới hạn integration timeout tối đa là 30 giây (hoặc 29 giây với private integrations).
- 🧠 **Key point / trap:** API Gateway timeout cứng tại **29 giây**. Tác vụ chạy lâu (> 29s) → Bắt buộc chuyển sang **Bất đồng bộ (Async invocation `202 Accepted` / Step Functions)**.
- 📎 Source: `Amazon API Gateway Developer Guide — API Gateway quotas and limits`.

---

### Question 12 — Answer: **A**
- **Why correct:** Đây là bẫy kinh điển và quan trọng nhất trong kỳ thi DVA-C02 về DynamoDB:
  1. Trong DynamoDB, **`FilterExpression` được thực hiện SAU KHI thao tác đọc dữ liệu đã hoàn tất**. Dung lượng RCU bị tiêu tốn dựa trên **tổng số lượng dữ liệu được đọc trước khi lọc**, chứ không phụ thuộc vào số lượng item trả về cho client sau khi lọc!
  2. Câu lệnh `Query` với `KeyConditionExpression` quét qua toàn bộ 10,000 nhân viên của phòng ban `ENG`.
  3. Kích thước mỗi item là 2 KB → Mỗi item chiếm: `ceil(2 KB / 4 KB) = 1` khối 4 KB.
  4. Nếu là Strongly Consistent: 10,000 item × 1 RCU = 10,000 RCU.
  5. Đề bài yêu cầu tính cho **Eventually Consistent Read** (1 RCU cho 2 lần đọc 4 KB): `10,000 / 2 = 2,500 RCU`.
  - Dù chỉ có 100 active nhân viên được trả về, bảng vẫn bị trừ đủ **2,500 RCU**.
- **Why the others are wrong:** B (25 RCU) là bẫy nếu thí sinh nghĩ chỉ tính RCU cho 100 item trả về (`100 × 0.5 = 50 / 2 = 25`). C (5,000 RCU) tính sai kích thước item. D (50 RCU) tính nhầm cho 100 item.
- 🧠 **Key point / trap:** `FilterExpression` trong DynamoDB **KHÔNG LÀM GIẢM RCU**. RCU luôn tính trên **toàn bộ dữ liệu được đọc bởi `KeyConditionExpression` (hoặc toàn bảng nếu là `Scan`)** trước khi bộ lọc filter được áp dụng!
- 📎 Source: `Amazon DynamoDB Developer Guide — Query operations in DynamoDB`.

---

### Question 13 — Answer: **A**
- **Why correct:** **Amazon SNS Subscription Filter Policies** cho phép các subscriber (như hàng đợi SQS) tự định nghĩa các quy tắc lọc dựa trên các thuộc tính của tin nhắn (`MessageAttributes`). SNS sẽ tự động đánh giá các điều kiện chuỗi (ví dụ `category = "PHARMACY"`) hoặc điều kiện phạm vi số (ví dụ `orderValue >= 500`) để chỉ chuyển tiếp các tin nhắn thỏa mãn điều kiện vào hàng đợi tương ứng, loại bỏ nhu cầu phải viết code lọc trung gian.
- **Why the others are wrong:** B tốn chi phí vận hành Lambda và làm tăng độ trễ kiến trúc. C đòi hỏi bên gửi (publisher) phải biết logic nghiệp vụ để gửi vào nhiều topic khác nhau, vi phạm nguyên tắc phân tách trách nhiệm (decoupling). D sai vì SQS DLQ không có tính năng lọc tin nhắn theo header HTTP.
- 🧠 **Key point / trap:** Lọc tin nhắn từ SNS vào các SQS queues khác nhau mà không cần viết code compute trung gian → **SNS Subscription Filter Policies**.
- 📎 Source: `Amazon SNS Developer Guide — Amazon SNS message filtering`.

---

### Question 14 — Answer: **A**
- **Why correct:** Trong Amazon DynamoDB, khi một bảng có một hoặc nhiều **Local Secondary Index (LSI)**, DynamoDB sẽ áp đặt một giới hạn cứng: **kích thước của một Item Collection (tập hợp tất cả các item có cùng một Partition Key trên bảng gốc và trên toàn bộ các LSI) không được vượt quá 10 GB**. Khi một thiết bị IoT ghi dữ liệu liên tục trong 6 tháng vượt qua 10 GB, DynamoDB sẽ chặn toàn bộ thao tác ghi mới cho Partition Key đó với lỗi `ItemCollectionSizeLimitExceededException`. Để giải quyết triệt để, kiến trúc phải chuyển sang sử dụng **Global Secondary Index (GSI)** vì GSI không bị giới hạn 10 GB item collection.
- **Why the others are wrong:** B sai vì đây là giới hạn logic của item collection có LSI, không phải dung lượng lưu trữ của Region. C sai vì item của cảm biến rất nhỏ, không vi phạm giới hạn 400 KB/item. D sai vì LSI dùng chung WCU của bảng gốc, không có cơ chế auto scaling riêng.
- 🧠 **Key point / trap:** Lỗi `ItemCollectionSizeLimitExceededException` (vượt quá 10 GB cho 1 partition key) → Do dùng **LSI**. Giải pháp: Chuyển sang dùng **Global Secondary Index (GSI)**.
- 📎 Source: `Amazon DynamoDB Developer Guide — Item collections in DynamoDB`.

---

### Question 15 — Answer: **A**
- **Why correct:** Để đảm bảo lưu lượng truy cập API Gateway hoàn toàn nằm trong mạng nội bộ và không bao giờ đi ra internet công cộng:
  1. Cấu hình kiểu endpoint của API Gateway là **Private**.
  2. Tạo một **Interface VPC Endpoint** (`com.amazonaws.region.execute-api`) được cấp phát bởi AWS PrivateLink trong VPC của khách hàng.
  3. Gắn một **API Gateway Resource Policy** chỉ cho phép truy cập nếu giá trị điều kiện `aws:sourceVpce` khớp với ID của VPC Endpoint vừa tạo.
- **Why the others are wrong:** B sai vì Regional API cùng với NAT Gateway vẫn sẽ định tuyến gói tin đi ra internet công cộng trước khi quay lại API Gateway. C sai vì Edge-Optimized dùng mạng CloudFront công cộng toàn cầu, không phải mạng riêng. D sai vì AWS API Gateway là dịch vụ đa người dùng (multi-tenant), không hỗ trợ VPC peering trực tiếp vào tài khoản dịch vụ.
- 🧠 **Key point / trap:** Private API Gateway: **Endpoint Type = Private + Interface VPC Endpoint (`execute-api`) + Resource Policy với `aws:sourceVpce`**.
- 📎 Source: `Amazon API Gateway Developer Guide — Creating a private REST API in Amazon API Gateway`.

---

### Question 16 — Answer: **A**
- **Why correct:** Các phiên bản của AWS Lambda Layer là **bất biến (immutable)**. Khi chạy lệnh `publish-layer-version`, Lambda không bao giờ ghi đè lên phiên bản cũ mà luôn tạo ra một phiên bản mới với một ARN hoàn toàn mới (ví dụ đuôi kết thúc là `:3`). Các hàm Lambda đang cấu hình trỏ vào phiên bản cũ (đuôi `:2`) sẽ tiếp tục sử dụng mã nguồn của phiên bản `:2`. Để áp dụng bản vá mới, lập trình viên bắt buộc phải cập nhật cấu hình của từng hàm Lambda để trỏ tới ARN phiên bản mới `:3`.
- **Why the others are wrong:** B sai vì Lambda Layers có hiệu lực ngay lập tức, không mất 24 giờ. C sai vì người dùng không có quyền truy cập vào máy chủ dịch vụ của Lambda. D sai vì chỉ upload lại code của hàm mà không cập nhật cấu hình Layer ARN thì hàm vẫn gắn với layer cũ.
- 🧠 **Key point / trap:** Lambda Layers có tính chất **Immutable (bất biến)**. Publish layer mới → Phải cập nhật tường minh **ARN mới** trên từng hàm Lambda.
- 📎 Source: `AWS Lambda Developer Guide — Working with layers`.

---

### Question 17 — Answer: **A**
- **Why correct:** Trong Amazon DynamoDB, lệnh `BatchWriteItem` (hoặc `BatchGetItem`) được thiết kế để không bao giờ thất bại toàn bộ nếu có một vài item gặp vấn đề về throughput. Thay vào đó, API sẽ ghi thành công tối đa các item có thể và trả về các item chưa kịp ghi trong một map có tên là **`UnprocessedItems`** mà **không ném ra bất kỳ Exception nào**. Do đó, code ứng dụng bắt buộc phải chủ động kiểm tra xem `UnprocessedItems` có rỗng hay không, và nếu có dữ liệu thì phải tự thực hiện vòng lặp thử lại (retry loop) với thuật toán **Exponential Backoff and Jitter**.
- **Why the others are wrong:** B sai vì AWS SDK không ném ra exception khi có `UnprocessedItems`, nên khối catch sẽ không bao giờ được kích hoạt, hơn nữa việc gửi lại cả 25 item sẽ gây ghi đè trùng lặp các item đã thành công. C sai vì tăng WCU cực lớn vừa lãng phí chi phí vừa không giải quyết được các đỉnh tải đột biến tạm thời. D sai vì `PutItem` tuần tự từng item làm giảm mạnh hiệu năng nạp dữ liệu theo lô.
- 🧠 **Key point / trap:** Xử lý `BatchWriteItem` / `BatchGetItem`: Luôn kiểm tra **`UnprocessedItems` / `UnprocessedKeys`** trong kết quả trả về và retry với **Exponential Backoff**.
- 📎 Source: `Amazon DynamoDB API Reference — BatchWriteItem`.

---

### Question 18 — Answer: **A**
- **Why correct:** Amazon SQS cung cấp tính năng bản địa **Dead-Letter Queue (DLQ) Redrive** trực tiếp trên AWS Console hoặc qua API **`StartMessageMoveTask`**. Tính năng này cho phép di chuyển hàng loạt tin nhắn từ DLQ quay trở lại hàng đợi nguồn ban đầu (hoặc một hàng đợi tùy chỉnh khác) hoàn toàn tự động ở phía backend của AWS mà không cần lập trình viên phải viết script trung gian hay duy trì máy chủ để kéo và đẩy tin nhắn.
- **Why the others are wrong:** B hoạt động được nhưng tốn công viết mã, dễ gây lỗi, tốn chi phí compute và chậm hơn nhiều so với tính năng quản lý tự động của SQS. C làm mất sạch dữ liệu kinh doanh của 25,000 giao dịch. D sai vì hoán đổi URL sẽ biến DLQ thành hàng đợi chính và làm xáo trộn toàn bộ luồng xử lý lỗi của hệ thống.
- 🧠 **Key point / trap:** Đẩy tin nhắn từ DLQ về lại hàng đợi chính sau khi fix bug → Dùng **SQS Dead-Letter Queue Redrive (`StartMessageMoveTask`)**.
- 📎 Source: `Amazon SQS Developer Guide — Dead-letter queue redrive`.

---

### Question 19 — Answer: **A**
- **Why correct:** **AWS Lambda SnapStart for Java** (hỗ trợ Java 11 và Java 17 trở lên) giúp giảm thời gian khởi động nguội (cold start) lên tới **90%** (từ 10 giây xuống còn vài trăm mili giây) hoàn toàn miễn phí. Khi một phiên bản hàm được publish, Lambda sẽ khởi chạy hàm, nạp toàn bộ lớp (classes), khởi tạo framework (Spring Boot), sau đó chụp lại ảnh chụp nhanh (snapshot) của toàn bộ Firecracker microVM đã khởi tạo và lưu vào bộ nhớ cache. Khi có yêu cầu mới, Lambda chỉ việc khôi phục trực tiếp từ snapshot thay vì khởi động máy ảo Java từ đầu.
- **Why the others are wrong:** B sai vì Response Streaming dùng để stream HTTP response từng phần, không làm giảm thời gian khởi động máy ảo JVM. C tốn nhiều công sức biên dịch AOT phức tạp và có thể gặp lỗi không tương thích thư viện so với tính năng một-click SnapStart. D sai vì tăng `/tmp` không can thiệp vào quá trình khởi tạo JVM.
- 🧠 **Key point / trap:** Giảm triệt để Cold Start cho các hàm Java (Spring Boot) trên Lambda mà không mất phí duy trì container → Bật **AWS Lambda SnapStart**.
- 📎 Source: `AWS Lambda Developer Guide — Improving startup performance with Lambda SnapStart`.

---

### Question 20 — Answer: **A**
- **Why correct:** **Amazon EventBridge Schema Registry** tự động thu thập và lưu trữ cấu trúc schema của các sự kiện chạy qua event bus (thông qua tính năng Schema Discovery). Đặc biệt, EventBridge Schema Registry cho phép lập trình viên tạo và tải về **Code Bindings** (các model / classes định kiểu sẵn cho Java, Python, TypeScript) để nhúng trực tiếp vào IDE (VS Code, IntelliJ) qua AWS Toolkit. Điều này giúp tận dụng tính năng tự động gợi ý code (autocomplete) và kiểm tra kiểu dữ liệu tĩnh khi biên dịch, loại bỏ hoàn toàn các lỗi chính tả khi truy cập thuộc tính JSON.
- **Why the others are wrong:** B sai vì API Gateway model validation chỉ áp dụng cho REST API endpoints, không quản lý được các event chạy trên EventBridge bus. C và D không có khả năng sinh code bindings tự động cho các ngôn ngữ lập trình.
- 🧠 **Key point / trap:** Tự động phát hiện schema sự kiện và sinh mã nguồn định kiểu (Code Bindings) cho TypeScript/Python → **EventBridge Schema Registry**.
- 📎 Source: `Amazon EventBridge User Guide — Amazon EventBridge schema registry`.

---

### Question 21 — Answer: **A**
- **Why correct:** AWS AppSync hỗ trợ truyền dữ liệu thời gian thực (real-time data push) một cách tự nhiên thông qua **GraphQL Subscriptions**. Khi ứng dụng client gửi một truy vấn subscription, AppSync sẽ tự động thiết lập và duy trì một kết nối WebSocket an toàn giữa client và AppSync. Bất cứ khi nào có một GraphQL Mutation làm thay đổi dữ liệu trong DynamoDB, AppSync sẽ tự động đẩy bản cập nhật mới nhất qua kết nối WebSocket đó tới toàn bộ các client đang lắng nghe.
- **Why the others are wrong:** B sai vì polling tiêu tốn pin thiết bị và tài nguyên máy chủ. C và D sai vì AppSync không sử dụng hàng đợi SQS hay Kinesis Video Streams để đẩy dữ liệu thời gian thực tới ứng dụng di động.
- 🧠 **Key point / trap:** Đẩy dữ liệu thời gian thực từ AWS AppSync tới thiết bị người dùng → Dùng **GraphQL Subscriptions (qua WebSockets)**.
- 📎 Source: `AWS AppSync Developer Guide — Real-time data with GraphQL subscriptions`.

---

### Question 22 — Answer: **A**
- **Why correct:** **IAM Permissions Boundary** là một tính năng kiểm soát truy cập nâng cao cho phép quản trị viên ủy quyền (delegate) việc tạo role cho các developer mà không sợ họ leo thang đặc quyền (privilege escalation). Bằng cách gắn một chính sách yêu cầu rằng bất kỳ role nào được tạo (`iam:CreateRole`) bắt buộc phải đính kèm một Permissions Boundary được chỉ định, role mới tạo ra sẽ không bao giờ có thể vượt qua ranh giới quyền hạn tối đa đó, ngay cả khi developer cố tình gắn policy `AdministratorAccess` vào role mới.
- **Why the others are wrong:** B sai vì Service Control Policies (SCPs) chỉ có thể gắn vào tài khoản AWS, OU hoặc Root trong AWS Organizations, không thể gắn trực tiếp vào một IAM User. C chỉ bảo vệ đăng nhập console, không ngăn chặn được API calls leo thang quyền. D làm tê liệt công việc của lập trình viên.
- 🧠 **Key point / trap:** Ủy quyền tạo IAM Role nhưng ngăn chặn leo thang đặc quyền → Dùng **IAM Permissions Boundary**.
- 📎 Source: `AWS IAM User Guide — Permissions boundaries for IAM entities`.

---

### Question 23 — Answer: **A**
- **Why correct:** **AWS KMS Multi-Region Keys** (`mrk-`) là các khóa Customer Managed Keys có cùng ID, cùng key material và cùng cấu hình nhưng được nhân bản và tồn tại độc lập tại nhiều AWS Region khác nhau. Dữ liệu được mã hóa bằng Multi-Region Key tại `us-east-1` có thể được giải mã trực tiếp cục bộ tại `eu-central-1` bằng khóa bản sao tương ứng mà **không cần thực hiện bất kỳ lệnh gọi API mạng nào xuyên Region**, đảm bảo độ trễ giải mã thấp nhất và tính khả dụng độc lập.
- **Why the others are wrong:** B sai vì gọi `kms:ReEncrypt` xuyên Region làm tăng đáng kể độ trễ mạng và tạo sự phụ thuộc vào sự sẵn sàng của `us-east-1`. C sai vì phần cứng bảo mật KMS HSM không bao giờ cho phép xuất khóa riêng tư đối xứng/bất đối xứng ở dạng văn bản gốc. D phức tạp và tốn kém chi phí hơn nhiều so với tính năng KMS Multi-Region Keys bản địa.
- 🧠 **Key point / trap:** Giải mã dữ liệu ở Region khác với độ trễ thấp mà không cần gọi API xuyên Region → **AWS KMS Multi-Region Keys (`mrk-`)**.
- 📎 Source: `AWS KMS Developer Guide — Multi-Region keys in AWS KMS`.

---

### Question 24 — Answer: **A**
- **Why correct:** **Amazon Cognito Pre-Token Generation Lambda Trigger** cho phép lập trình viên can thiệp vào quy trình sinh token ngay trước khi Amazon Cognito cấp phát OIDC ID Token và Access Token cho người dùng. Hàm Lambda trigger này có thể truy vấn các cơ sở dữ liệu bên ngoài (như RDS PostgreSQL), bổ sung thêm các custom claims (ví dụ `tenant_id`, `role`, `tier`) hoặc ghi đè các OAuth scopes trực tiếp vào trong payload của token JWT.
- **Why the others are wrong:** B sai vì Post-Confirmation chỉ chạy sau khi người dùng xác thực email/số điện thoại thành công, không can thiệp vào quá trình cấp phát token lúc đăng nhập. C sai vì Pre-Sign-up chạy trước khi đăng ký tài khoản. D sai vì Custom Authentication Challenge dùng cho luồng đăng nhập không mật khẩu (passwordless), không dùng để sửa đổi claim của token.
- 🧠 **Key point / trap:** Chèn thêm custom claims hoặc sửa đổi scopes vào JWT token trước khi trả về client → **Cognito Pre-Token Generation Lambda Trigger**.
- 📎 Source: `Amazon Cognito Developer Guide — Pre token generation Lambda trigger`.

---

### Question 25 — Answer: **A**
- **Why correct:** Chiến lược xoay vòng thông tin đăng nhập **Multi-User (Alternating Users)** trong AWS Secrets Manager duy trì hai tài khoản database riêng biệt (ví dụ `User_A` và `User_B`). Trong khi ứng dụng đang hoạt động bình thường với `User_A`, Secrets Manager sẽ tiến hành đổi mật khẩu cho `User_B` trên RDS, kiểm tra kết nối của `User_B`, và cập nhật secret trỏ sang `User_B`. Sau đó, ứng dụng sẽ chuyển sang dùng `User_B`. Trong toàn bộ quá trình, không bao giờ có thời điểm kết nối database bị ngắt, đảm bảo tính sẵn sàng cao tuyệt đối và zero downtime.
- **Why the others are wrong:** B sai vì Single-User rotation sẽ đổi mật khẩu trực tiếp trên user duy nhất đang chạy, trong khoảng thời gian giữa lúc đổi trên DB đến lúc ứng dụng lấy mật khẩu mới, mọi request gửi tới DB đều sẽ bị lỗi `Access Denied`. C vi phạm chính sách bảo mật tuân thủ. D vi phạm nghiêm trọng nguyên tắc an toàn thông tin khi nhúng mật khẩu vào container image.
- 🧠 **Key point / trap:** Xoay vòng mật khẩu database với Secrets Manager không gây downtime → Chiến lược **Multi-User (Alternating Users) Rotation**.
- 📎 Source: `AWS Secrets Manager User Guide — Alternating users rotation strategy`.

---

### Question 26 — Answer: **A**
- **Why correct:** Sử dụng **OpenID Connect (OIDC)** là tiêu chuẩn vàng của AWS để tích hợp các hệ thống CI/CD bên ngoài (như GitHub Actions, GitLab CI) mà không cần lưu trữ bất kỳ access key dài hạn nào. Lập trình viên thiết lập một Identity Provider OIDC trong IAM trỏ tới GitHub, tạo một IAM Role với Trust Policy cho phép hành động `sts:AssumeRoleWithWebIdentity`, và dùng điều kiện `token.actions.githubusercontent.com:sub` để chỉ cho phép các workflow chạy trên đúng repository/branch mong muốn được cấp phát thông tin xác thực AWS tạm thời ngắn hạn.
- **Why the others are wrong:** B và C là những lỗ hổng bảo mật cực kỳ nghiêm trọng, dẫn đến nguy cơ bị chiếm quyền toàn bộ tài khoản AWS. D không giải quyết bài toán CI/CD an toàn của GitHub Actions hiện tại.
- 🧠 **Key point / trap:** Cấp quyền an toàn cho GitHub Actions triển khai lên AWS không dùng Access Key dài hạn → **OIDC Identity Federation (`sts:AssumeRoleWithWebIdentity`)**.
- 📎 Source: `AWS IAM User Guide — Creating OpenID Connect (OIDC) identity providers`.

---

### Question 27 — Answer: **A**
- **Why correct:** **AWS KMS Grants** là một cơ chế phân quyền theo chương trình (programmatic, ephemeral delegation) cho phép ủy quyền tạm thời và chi tiết việc sử dụng một KMS Customer Managed Key cho một IAM principal khác (ví dụ cho phép worker gọi `Decrypt` trong một khoảng thời gian nhất định). Grants có thể được tạo bằng lệnh `CreateGrant` và thu hồi tức thì bằng lệnh `RevokeGrant` mà hoàn toàn **không cần chỉnh sửa hay triển khai lại tài liệu JSON Key Policy** tĩnh của khóa.
- **Why the others are wrong:** B sai vì sửa Key Policy tĩnh là thao tác quản trị phức tạp, không linh hoạt, có giới hạn kích thước tài liệu policy (32 KB) và khó thu hồi tự động. C vi phạm nguyên tắc bảo mật. D sai vì Alias chỉ là tên gọi đại diện, không cấp quyền giải mã.
- 🧠 **Key point / trap:** Phân quyền dùng khóa KMS tạm thời, linh hoạt theo chương trình, không sửa Key Policy tĩnh → Dùng **AWS KMS Grants (`CreateGrant`)**.
- 📎 Source: `AWS KMS Developer Guide — Grants in AWS KMS`.

---

### Question 28 — Answer: **A**
- **Why correct:** Khi tạo một S3 Pre-signed PUT URL từ AWS Lambda, lập trình viên có thể chỉ định các tham số ràng buộc mã hóa máy chủ: `ServerSideEncryption: "aws:kms"` và `SSEKMSKeyId: <KMS_KEY_ARN>`. Chữ ký mật mã của URL sẽ bao gồm các tham số này. Khi client thực hiện lệnh HTTP PUT tải file lên S3, client **bắt buộc phải truyền các HTTP headers tương ứng** (ví dụ `x-amz-server-side-encryption: aws:kms` và `x-amz-server-side-encryption-aws-kms-key-id`). Nếu client không gửi đúng các header này, chữ ký sẽ không khớp và S3 sẽ từ chối tải file lên ngay lập tức.
- **Why the others are wrong:** B sai vì Pre-signed URL hoàn toàn hỗ trợ ràng buộc các header mã hóa KMS. C sai vì nếu client không gửi header khớp với chữ ký của Pre-signed URL thì request sẽ bị lỗi `SignatureDoesNotMatch`. D sai vì Pre-signed URL hỗ trợ đầy đủ cả SSE-S3 lẫn SSE-KMS.
- 🧠 **Key point / trap:** Bắt buộc client mã hóa KMS khi dùng Pre-signed URL: Truyền tham số mã hóa lúc sinh URL và yêu cầu client gửi kèm header **`x-amz-server-side-encryption: aws:kms`**.
- 📎 Source: `Amazon S3 User Guide — Uploading objects using presigned URLs with server-side encryption`.

---

### Question 29 — Answer: **A**
- **Why correct:** AWS Systems Manager Parameter Store hỗ trợ tổ chức tham số theo dạng cây phân cấp (path hierarchy, ví dụ `/app/env/param`). Lệnh **`get-parameters-by-path`** kết hợp với tham số **`--recursive`** cho phép truy xuất toàn bộ các tham số nằm bên trong một nhánh cây trong một lệnh gọi duy nhất. Tùy chọn **`--with-decryption`** đảm bảo các tham số kiểu `SecureString` sẽ được tự động giải mã sang văn bản gốc trước khi trả về cho ứng dụng.
- **Why the others are wrong:** B sai vì `get-parameter` chỉ lấy duy nhất một tham số cụ thể và không hỗ trợ ký tự đại diện wildcard `*`. C sai vì `get-parameters` yêu cầu truyền danh sách đầy đủ tên từng tham số, không hỗ trợ quét theo đường dẫn cha. D sai vì `describe-parameters` chỉ trả về metadata (mô tả, ngày tạo, phiên bản) chứ không trả về giá trị (value) của tham số.
- 🧠 **Key point / trap:** Lấy tất cả tham số trong một thư mục phân cấp của Parameter Store → **`aws ssm get-parameters-by-path --path ... --recursive --with-decryption`**.
- 📎 Source: `AWS Systems Manager User Guide — Working with parameter hierarchies`.

---

### Question 30 — Answer: **A**
- **Why correct:** Quy tắc đánh giá chính sách (Policy Evaluation Logic) cơ bản và quan trọng nhất của AWS IAM:
  1. Mặc định là Từ chối (Default Deny).
  2. Bất kỳ một điều khoản Cho phép tường minh nào (Explicit Allow) sẽ mở quyền truy cập.
  3. **MỘT ĐIỀU KHOẢN TỪ CHỐI TƯỜNG MINH (EXPLICIT DENY) LUÔN CHIẾN THẮNG MỌI ĐIỀU KHOẢN CHO PHÉP (EXPLICIT ALLOW)**, bất kể điều khoản Deny đó nằm ở SCP, Permissions Boundary, Identity-based Policy hay Resource-based Policy.
  Vì S3 Bucket Policy có lệnh Deny tường minh trên thư mục `/confidential/*`, Alice sẽ bị từ chối truy cập ngay lập tức (`Access Denied`).
- **Why the others are wrong:** B và C sai vì Explicit Deny luôn có độ ưu tiên cao nhất trong toàn bộ hệ thống đánh giá quyền của AWS. D là câu nói đùa vô lý.
- 🧠 **Key point / trap:** Logic đánh giá IAM Policy: **Explicit Deny > Explicit Allow > Default Deny**.
- 📎 Source: `AWS IAM User Guide — Determining whether a request is allowed or denied`.

---

### Question 31 — Answer: **A**
- **Why correct:** Để bắt buộc mọi kết nối tới Amazon S3 phải sử dụng HTTPS (TLS) và từ chối các kết nối HTTP không an toàn, mẫu thiết kế chuẩn của AWS là viết một statement trong S3 Bucket Policy với:
  - `"Effect": "Deny"`
  - `"Action": "s3:*"`
  - `"Condition": {"Bool": {"aws:SecureTransport": "false"}}`
  Biến điều kiện toàn cục `aws:SecureTransport` mang giá trị `true` nếu request sử dụng giao thức HTTPS và mang giá trị `false` nếu request sử dụng HTTP thông thường. Khi kết hợp với chỉ thị `Deny`, bất kỳ request HTTP nào cũng sẽ bị chặn hoàn toàn.
- **Why the others are wrong:** B sai vì điều kiện chuỗi `aws:Protocol` không phải là condition key toàn cục hợp lệ của AWS IAM/S3 và dùng `Allow` không ngăn chặn được các quyền được cấp từ nơi khác. C và D không có tính năng ép buộc giao thức truyền tải mạng lúc in-transit.
- 🧠 **Key point / trap:** Ép buộc HTTPS/TLS trên S3 Bucket Policy: **`Effect: Deny` kết hợp condition `"Bool": {"aws:SecureTransport": "false"}`**.
- 📎 Source: `AWS Knowledge Center — How can I use a bucket policy to enforce that requests to my Amazon S3 bucket use HTTPS?`

---

### Question 32 — Answer: **A**
- **Why correct:** Trong Amazon Cognito User Pools, lập trình viên có thể cấu hình Multi-Factor Authentication (MFA) để sử dụng mã phần mềm **Time-based One-time Password (TOTP) software token** (tương thích với các ứng dụng xác thực như Google Authenticator, Microsoft Authenticator, Authy). Bằng cách kích hoạt TOTP và tắt tính năng SMS text message MFA, ứng dụng sẽ loại bỏ được rủi ro bị tấn công hoán đổi SIM (SIM-swapping) và đáp ứng các tiêu chuẩn tuân thủ tài chính nghiêm ngặt.
- **Why the others are wrong:** B sai vì gửi mã qua email không phải là chuẩn MFA được Cognito hỗ trợ tự động dưới dạng phương thức chính và email vẫn tiềm ẩn rủi ro chiếm đoạt hòm thư. C sai vì Identity Pool dùng để cấp quyền AWS credentials, không quản lý phương thức MFA lúc đăng nhập người dùng. D sai vì Cognito User Pools hỗ trợ đầy đủ TOTP software tokens.
- 🧠 **Key point / trap:** Cognito MFA an toàn chống SIM-swapping → Chọn phương thức **Time-based One-time Password (TOTP) software token**.
- 📎 Source: `Amazon Cognito Developer Guide — Adding multi-factor authentication (MFA) to a user pool`.

---

### Question 33 — Answer: **A**
- **Why correct:** Để ký số dữ liệu (Digital Signature) mà không bao giờ làm lộ khóa riêng tư (private key), dịch vụ **AWS KMS Asymmetric Keys** là giải pháp tối ưu. Lập trình viên tạo một cặp khóa bất đối xứng với Key Usage là **`SIGN_VERIFY`** và Key Spec là `RSA_4096` hoặc `ECC_NIST_P256`. Thao tác ký được thực hiện an toàn bên trong phần cứng KMS HSM thông qua API **`kms:Sign`**. Khóa công khai (public key) có thể được xuất ra và phân phối cho các thiết bị IoT để chúng kiểm tra chữ ký xác thực mà không ai có thể can thiệp hay trích xuất khóa riêng tư ra khỏi AWS.
- **Why the others are wrong:** B sai vì khóa đối xứng (Symmetric Key) dùng cùng một khóa để mã hóa và giải mã, không thể phân phối cho thiết bị IoT mà không làm lộ bí mật. C và D sai vì lưu file private key trên S3 hay Parameter Store vẫn có rủi ro bị tải về hoặc lộ lọt ra môi trường bên ngoài.
- 🧠 **Key point / trap:** Ký số không làm lộ Private Key ra ngoài máy chủ → Dùng **Asymmetric KMS Key với Key Usage `SIGN_VERIFY` + API `kms:Sign`**.
- 📎 Source: `AWS KMS Developer Guide — Asymmetric keys in AWS KMS`.

---

### Question 34 — Answer: **A**
- **Why correct:** **Mutual TLS (mTLS)** cho phép xác thực hai chiều giữa client và server trực tiếp tại tầng truyền tải (TLS layer) trong quá trình bắt tay (handshake). Amazon API Gateway hỗ trợ mTLS trên các **Custom Domain Names**. Để triển khai, lập trình viên tải gói chứng chỉ Certificate Authority (CA bundle / truststore) lên một **Amazon S3 bucket**, sau đó liên kết truststore này với Custom Domain trong API Gateway. Khi client gọi tới, API Gateway sẽ tự động xác minh chứng chỉ của client với CA trong truststore trước khi cho phép request đi tiếp.
- **Why the others are wrong:** B sai vì AWS WAF hoạt động ở tầng ứng dụng (L7), không thực hiện được việc bắt tay xác thực chứng chỉ số X.509 ở tầng truyền tải (TLS). C sai vì API Keys dùng để giới hạn lưu lượng, không phải là xác thực danh tính bảo mật mạnh. D sai vì Cognito User Pool không hỗ trợ xác thực mTLS trực tiếp tại tầng TLS.
- 🧠 **Key point / trap:** Xác thực chứng chỉ client trực tiếp tại API Gateway ở tầng Transport → Cấu hình **Mutual TLS (mTLS)** trên **Custom Domain** với **S3 Truststore**.
- 📎 Source: `Amazon API Gateway Developer Guide — Configuring mutual TLS for a REST API`.

---

### Question 35 — Answer: **A**
- **Why correct:** Khi mã hóa số lượng lớn bản ghi bằng Envelope Encryption, việc gọi API `kms:GenerateDataKey` cho từng bản ghi riêng lẻ sẽ nhanh chóng làm cạn kiệt hạn ngạch RPS của KMS (gây lỗi `KMS ThrottlingException`) và làm tăng vọt chi phí API. Thư viện **AWS Encryption SDK** cung cấp thành phần **Caching Cryptographic Materials Manager (Caching CMM)**. Caching CMM sẽ lưu trữ các khóa dữ liệu (data keys) trong bộ nhớ RAM cục bộ theo thời gian sống (TTL) hoặc số lượng bản ghi tối đa, cho phép tái sử dụng khóa dữ liệu để mã hóa nhiều bản ghi mà không cần gọi lại AWS KMS, vừa tối ưu hiệu năng vừa tiết kiệm chi phí.
- **Why the others are wrong:** B sai vì base64 chỉ là định dạng mã hóa ký tự, không phải là thuật toán mã hóa bảo mật. C và D là các hành vi vi phạm bảo mật nghiêm trọng.
- 🧠 **Key point / trap:** Giảm chi phí và tránh throttle KMS khi mã hóa khối lượng lớn bản ghi với AWS Encryption SDK → Sử dụng **Caching CMM (Caching Cryptographic Materials Manager)**.
- 📎 Source: `AWS Encryption SDK Developer Guide — Caching cryptographic materials`.

---

### Question 36 — Answer: **A**
- **Why correct:** Quyền **`iam:PassRole`** là một cơ chế bảo mật trọng yếu của AWS nhằm ngăn chặn việc người dùng gán một vai trò có quyền hạn cao cho một dịch vụ mà bản thân họ không có quyền sở hữu. Khi một lập trình viên tạo hoặc cập nhật một dịch vụ AWS (như hàm Lambda, máy chủ EC2, hay tác vụ ECS) và muốn dịch vụ đó thực thi dưới một IAM Role nhất định, lập trình viên đó bắt buộc phải có quyền `iam:PassRole` trên chính ARN của role đó.
- **Why the others are wrong:** B sai vì sửa Trust Policy cần quyền `iam:UpdateAssumeRolePolicy`. C sai vì IAM User và IAM Role là hai thực thể hoàn toàn tách biệt, không thể "chuyển đổi" qua lại bằng lệnh này. D sai vì lỗi nêu rõ nguyên nhân là thiếu quyền `iam:PassRole`.
- 🧠 **Key point / trap:** Khi gắn một IAM Role vào Lambda / EC2 / ECS mà bị lỗi `AccessDeniedException` → Kiểm tra quyền **`iam:PassRole`** của user đang thực hiện lệnh.
- 📎 Source: `AWS IAM User Guide — Granting a user permissions to pass a role to an AWS service`.

---

### Question 37 — Answer: **A**
- **Why correct:** Gọi API `GetSecretValue` trực tiếp trong mỗi request ở mức tải 5,000 req/s sẽ gây nghẽn nghiêm trọng vì Secrets Manager có giới hạn hạn ngạch API và chi phí $0.05 trên mỗi 10,000 lần gọi. Thư viện **AWS Secrets Manager Caching Client** (hỗ trợ Java, Python, Go, .NET) tự động lưu trữ giá trị bí mật trong bộ nhớ RAM của môi trường thực thi Lambda với thời gian TTL có thể cấu hình (ví dụ 1 giờ). Các lần gọi ấm (warm invocations) tiếp theo sẽ đọc trực tiếp từ bộ nhớ đệm, triệt tiêu hoàn toàn lỗi throttle và tiết kiệm hơn 99% chi phí API.
- **Why the others are wrong:** B sai vì nâng quota không giải quyết được chi phí phát sinh khổng lồ do gọi API liên tục. C và D là những sai lầm bảo mật nghiêm trọng khi lưu token thanh toán trong Git hoặc code frontend.
- 🧠 **Key point / trap:** Tránh throttle và giảm chi phí khi đọc Secrets Manager từ Lambda tải cao → Sử dụng **AWS Secrets Manager Caching Client Library**.
- 📎 Source: `AWS Secrets Manager User Guide — Cache secrets in memory`.

---

### Question 38 — Answer: **A**
- **Why correct:** **Amazon S3 Block Public Access (BPA)** được thiết kế như một chốt chặn bảo mật tập trung (centralized guardrail). Khi tính năng S3 Block Public Access được bật ở **cấp độ tài khoản AWS (Account level)**, các thiết lập này có **độ ưu tiên cao nhất** và sẽ ghi đè (override) lên mọi chính sách Bucket Policy hay danh sách kiểm soát quyền (ACL) ở cấp độ từng bucket con bên dưới. Do đó, dù lập trình viên có tạo một Bucket Policy cho phép `Principal: "*"`, toàn bộ các đối tượng bên trong bucket vẫn hoàn toàn an toàn và được bảo vệ ở chế độ riêng tư (private).
- **Why the others are wrong:** B sai vì cấu hình Block Public Access ở cấp tài khoản luôn ghi đè lên cấu hình của bucket đơn lẻ. C sai vì AWS không bao giờ tự ý xóa bucket của khách hàng. D sai vì S3 là dịch vụ lưu trữ đối tượng qua HTTP REST API, không kết nối qua SSH.
- 🧠 **Key point / trap:** **S3 Block Public Access ở cấp Account luôn có độ ưu tiên cao nhất**, vô hiệu hóa mọi nỗ lực mở public bucket bằng Bucket Policy hay ACL.
- 📎 Source: `Amazon S3 User Guide — Blocking public access to your Amazon S3 storage`.

---

### Question 39 — Answer: **A**
- **Why correct:** AWS CodeBuild hỗ trợ tính năng **Build Caching** mạnh mẽ:
  1. **Local Caching:** Lưu trữ bộ nhớ đệm cục bộ ngay trên máy chủ build host, bao gồm chế độ lưu thư mục tùy chỉnh (Custom directory cache cho thư mục chứa dependencies như `~/.m2/repository` của Maven hoặc `~/.npm`) và **Docker layer cache mode** (lưu lại các layer Docker đã build trước đó).
  2. **Amazon S3 Caching:** Tải tệp nén bộ nhớ đệm lên một S3 bucket giữa các lần build.
  Việc cấu hình cache này giúp CodeBuild không phải tải lại hàng nghìn thư viện từ internet trong mỗi lần chạy, giúp giảm thời gian build từ 18 phút xuống còn vài phút.
- **Why the others are wrong:** B sai vì tăng cấu hình CPU/RAM chỉ tăng tốc độ biên dịch mã nguồn, không giải quyết được thời gian nghẽn mạng do tải hàng gigabyte dependencies từ xa. C sai vì tự dựng EC2 tốn công bảo trì và mất tính serverless của CodeBuild. D vi phạm nguyên tắc quản lý mã nguồn khi đưa các file binary nặng vào Git.
- 🧠 **Key point / trap:** Tăng tốc quy trình build trong CodeBuild bằng cách tái sử dụng dependencies và Docker layers → Cấu hình **Build Caching (Local Custom/Docker Cache hoặc S3 Cache)** trong `buildspec.yml`.
- 📎 Source: `AWS CodeBuild User Guide — Build caching in AWS CodeBuild`.

---

### Question 40 — Answer: **A**
- **Why correct:** Trình tự các lifecycle hooks hợp lệ trong tệp `appspec.yml` khi triển khai ứng dụng lên nền tảng **Amazon EC2 / On-Premises**:
  1. `ApplicationStop`: Dừng ứng dụng đang chạy hiện tại một cách an toàn.
  2. `DownloadBundle`: (CodeDeploy agent thực hiện) Tải gói mã nguồn về máy.
  3. `BeforeInstall`: Chạy các tác vụ chuẩn bị (sao lưu, giải mã cấu hình).
  4. `Install`: (CodeDeploy agent thực hiện) Sao chép các tệp tin vào thư mục đích.
  5. `AfterInstall`: Cấu hình ứng dụng, phân quyền thư mục.
  6. `ApplicationStart`: Khởi động dịch vụ hoặc máy chủ web.
  7. `ValidateService`: Chạy script kiểm tra xem ứng dụng đã hoạt động khỏe mạnh hay chưa (ví dụ gọi `curl http://localhost/health`).
- **Why the others are wrong:** B là lifecycle hooks dành riêng cho nền tảng AWS Lambda. C là lifecycle hooks dành cho nền tảng Amazon ECS. D chứa các hook không tồn tại trong đặc tả AppSpec của EC2.
- 🧠 **Key point / trap:** Thứ tự lifecycle hooks của CodeDeploy trên EC2: **`ApplicationStop` → `BeforeInstall` → `AfterInstall` → `ApplicationStart` → `ValidateService`**.
- 📎 Source: `AWS CodeDeploy User Guide — AppSpec 'hooks' section for an EC2/On-Premises deployment`.

---

### Question 41 — Answer: **A**
- **Why correct:** AWS CodePipeline hỗ trợ danh mục hành động **Approval** với kiểu hành động **`Manual`**. Khi được cấu hình giữa hai giai đoạn (ví dụ giữa Staging và Production), pipeline sẽ tạm dừng tiến trình thực thi và gửi một thông báo tới một **Amazon SNS topic**. Người có thẩm quyền (QA Lead) sẽ nhận được email chứa đường link dẫn tới bảng điều khiển CodePipeline để xem xét kết quả test và bấm "Approve" (để pipeline tiếp tục chạy sang Production) hoặc "Reject" (để hủy đợt phát hành).
- **Why the others are wrong:** B sai vì Lambda chạy tối đa chỉ được 15 phút, không thể sleep 7 ngày và cách làm này vô cùng lãng phí. C sai vì chia thành hai pipeline ở hai tài khoản khác nhau làm mất đi tính liên tục và khả năng theo dõi tiến trình thống nhất của CI/CD. D sai vì vô hiệu hóa git merge commits không giải quyết được việc kiểm duyệt trong pipeline.
- 🧠 **Key point / trap:** Dừng pipeline chờ người kiểm duyệt trước khi deploy lên Prod → Thêm **Manual Approval Action** kết hợp **Amazon SNS Topic**.
- 📎 Source: `AWS CodePipeline User Guide — Add a manual approval action to a pipeline`.

---

### Question 42 — Answer: **A**
- **Why correct:** Để chia sẻ giá trị tài nguyên giữa các CloudFormation stack độc lập với nhau (Cross-Stack References):
  1. Trong stack xuất bản (`NetworkStack`), định nghĩa tài nguyên muốn chia sẻ trong phần **`Outputs`** và gắn thuộc tính **`Export: Name: <ExportName>`**.
  2. Trong stack tiêu thụ (`AppStack`), sử dụng hàm nội tại **`Fn::ImportValue`** (hoặc cú pháp viết tắt `!ImportValue <ExportName>`) để lấy giá trị đó.
- **Why the others are wrong:** B sai vì hardcode giá trị làm mất đi tính tự động và nếu subnet bị thay đổi thì template sẽ bị hỏng. C tốn công bảo trì và làm chậm quá trình triển khai CloudFormation. D sai vì gộp chung một template lớn vi phạm nguyên tắc phân tách trách nhiệm và dễ chạm giới hạn 500 tài nguyên.
- 🧠 **Key point / trap:** Chia sẻ giá trị giữa các CloudFormation Stacks: **`Export: Name:` trong `Outputs` kết hợp hàm `Fn::ImportValue`**.
- 📎 Source: `AWS CloudFormation User Guide — Exporting stack output values`.

---

### Question 43 — Answer: **A**
- **Why correct:** **CloudFormation Custom Resources** (`Custom::MyCustomType` hoặc `AWS::CloudFormation::CustomResource`) cho phép lập trình viên nhúng logic tùy biến vào quy trình cấp phát của CloudFormation thông qua **AWS Lambda**. Khi stack được tạo, cập nhật hoặc xóa, CloudFormation sẽ gửi một sự kiện (event) tới hàm Lambda. Hàm Lambda thực thi các tác vụ (như kết nối vào database trong VPC chạy lệnh SQL tạo bảng), sau đó gửi một phản hồi trạng thái (`SUCCESS` hoặc `FAILED`) kèm dữ liệu về một presigned URL trên Amazon S3 thông qua thư viện trợ giúp **`cfn-response`**.
- **Why the others are wrong:** B sai vì `Parameters` chỉ dùng để nhận giá trị đầu vào cho template, không có tính năng thực thi lệnh SQL. C sai vì `WaitCondition` chỉ dùng để chờ tín hiệu từ EC2 instance, không tự chạy lệnh database. D sai vì Stack Policy dùng để khóa tài nguyên chống sửa đổi, không chạy được SQL.
- 🧠 **Key point / trap:** Thực thi các tác vụ tùy biến không có sẵn trong CloudFormation (như khởi tạo schema DB, gọi API ngoài) → Dùng **Custom Resources (`AWS::CloudFormation::CustomResource`) kết hợp AWS Lambda**.
- 📎 Source: `AWS CloudFormation User Guide — Custom resources`.

---

### Question 44 — Answer: **A**
- **Why correct:** Trong các mẫu AWS Serverless Application Model (SAM), phần **`Globals:`** là một khu vực cấu hình cấp cao nhất cho phép định nghĩa các thuộc tính dùng chung cho tất cả các tài nguyên không máy chủ cùng loại trong template. Khai báo các thuộc tính `Runtime`, `Timeout`, `MemorySize`, và `Environment` bên dưới mục `Globals: Function:` sẽ tự động áp dụng các cấu hình này cho toàn bộ 12 hàm `AWS::Serverless::Function`, giúp mã nguồn template ngắn gọn, sạch sẽ và dễ bảo trì.
- **Why the others are wrong:** B sai vì `Metadata` chỉ chứa dữ liệu mô tả hoặc thông tin định tuyến cho các công cụ như CloudFormation Designer, không có tính kế thừa cấu hình runtime. C sai vì IAM policy quản lý phân quyền, không quản lý thông số cấu hình tài nguyên của hàm. D sai vì SAM hỗ trợ tính năng Globals rất mạnh mẽ.
- 🧠 **Key point / trap:** Chia sẻ cấu hình chung (Runtime, Timeout, Memory) cho nhiều Lambda trong AWS SAM → Sử dụng phần **`Globals: Function:`**.
- 📎 Source: `AWS Serverless Application Model Developer Guide — Globals section`.

---

### Question 45 — Answer: **A**
- **Why correct:** Chính sách triển khai **Traffic Splitting** trong AWS Elastic Beanstalk cung cấp giải pháp kiểm thử canary an toàn:
  1. Khởi tạo một tập hợp các máy chủ EC2 mới chạy phiên bản ứng dụng mới.
  2. Tách một tỷ lệ nhỏ lưu lượng truy cập thực tế của người dùng (ví dụ 10%) chuyển sang cụm máy chủ mới trong một khoảng thời gian đánh giá (evaluation period).
  3. Trong suốt thời gian này, Elastic Beanstalk theo dõi sát sao tình trạng sức khỏe của ứng dụng và các CloudWatch Alarms. Nếu phát sinh lỗi, hệ thống sẽ tự động hủy đợt phát hành và chuyển 100% traffic quay về phiên bản cũ ngay lập tức mà không làm gián đoạn người dùng.
  4. Nếu không có lỗi, 100% lưu lượng sẽ được chuyển mượt mà sang phiên bản mới.
- **Why the others are wrong:** B sai vì All at once gây downtime và không có kiểm thử canary. C và D cập nhật trực tiếp trên cụm máy chủ hiện có theo từng đợt, không có cơ chế tách lưu lượng theo tỷ lệ phần trăm và đánh giá qua alarm như Traffic Splitting.
- 🧠 **Key point / trap:** Triển khai Canary với tách % lưu lượng và tự động rollback dựa trên CloudWatch Alarms trong Elastic Beanstalk → **Traffic Splitting Deployment**.
- 📎 Source: `AWS Elastic Beanstalk Developer Guide — Traffic splitting deployments`.

---

### Question 46 — Answer: **A**
- **Why correct:** Phân biệt rõ hai loại IAM Role trong Amazon ECS Task Definition:
  1. **Task Execution Role (`executionRoleArn`):** Cấp quyền cho **chính ECS Container Agent và hạ tầng AWS Fargate**. Role này cần các quyền như tải container image từ kho lưu trữ bảo mật Amazon ECR (`ecr:GetAuthorizationToken`, `ecr:BatchGetImage`) và đẩy log hệ thống lên Amazon CloudWatch Logs (`logs:CreateLogStream`, `logs:PutLogEvents`).
  2. **Task Role (`taskRoleArn`):** Cấp quyền cho **mã nguồn ứng dụng đang chạy bên trong container**. Khi code trong container gọi AWS SDK (ví dụ `dynamodb:PutItem`, `s3:GetObject`), AWS SDK sẽ tự động lấy thông tin xác thực từ Task Role này.
- **Why the others are wrong:** B sai vì đảo ngược vai trò của hai role và bỏ trống Execution Role sẽ khiến Fargate không thể kéo image từ ECR. C sai vì người dùng không thể can thiệp vào máy chủ ảo hóa Fargate. D vi phạm nghiêm trọng nguyên tắc an toàn thông tin.
- 🧠 **Key point / trap:** ECS: **`executionRoleArn`** dành cho ECS Agent kéo image ECR và ghi logs; **`taskRoleArn`** dành cho mã nguồn ứng dụng truy cập DynamoDB/S3.
- 📎 Source: `Amazon ECS Developer Guide — Amazon ECS task execution IAM role & Task IAM role`.

---

### Question 47 — Answer: **A**
- **Why correct:** **CloudFormation Drift Detection** cho phép lập trình viên phát hiện các thay đổi cấu hình tài nguyên được thực hiện bên ngoài quyền quản lý của CloudFormation (ví dụ một kỹ sư dùng giao diện Web Console hoặc AWS CLI để trực tiếp sửa Security Group rule hay đổi cỡ instance RDS). Khi kích hoạt Drift Detection, CloudFormation sẽ so sánh cấu hình thực tế hiện tại của tài nguyên trên AWS với cấu hình được định nghĩa trong mẫu template của stack và thông báo trạng thái `DRIFTED` kèm theo chi tiết các thuộc tính bị thay đổi.
- **Why the others are wrong:** B sai vì CloudTrail chỉ liệt kê danh sách các sự kiện API thô, rất khó để đối chiếu và phát hiện độ lệch cấu hình so với template CloudFormation. C và D không phải là công cụ kiểm tra độ lệch và có thể làm mất dữ liệu hoặc gián đoạn dịch vụ.
- 🧠 **Key point / trap:** Phát hiện tài nguyên bị sửa đổi thủ công ngoài luồng so với mẫu CloudFormation → Chạy **CloudFormation Drift Detection**.
- 📎 Source: `AWS CloudFormation User Guide — Detecting unmanaged configuration changes to stacks and resources`.

---

### Question 48 — Answer: **A**
- **Why correct:** Theo mặc định, các container biên dịch của AWS CodeBuild chạy bên ngoài mạng VPC của khách hàng (chỉ có kết nối internet công cộng). Do đó, khi các script kiểm thử tích hợp (integration tests) cố gắng kết nối tới cơ sở dữ liệu Amazon Aurora nằm trong private subnet của VPC, kết nối sẽ bị chặn và timeout. Để khắc phục, lập trình viên cấu hình **VPC Access** trong dự án CodeBuild, chọn VPC, các private subnets và một Security Group. CodeBuild sẽ tạo các ENI bên trong subnet đó và cho phép giao tiếp nội bộ tới Aurora database.
- **Why the others are wrong:** B sai vì gán public IP cho cơ sở dữ liệu nội bộ vi phạm chính sách an ninh mạng. C sai vì lưu mật khẩu trong Secrets Manager chỉ cung cấp chuỗi xác thực, không giải quyết được vấn đề định tuyến mạng ở tầng kết nối TCP. D sai vì không thể tải toàn bộ cơ sở dữ liệu lớn vào ổ đĩa của CodeBuild.
- 🧠 **Key point / trap:** CodeBuild cần kết nối vào tài nguyên trong mạng riêng (RDS, ElastiCache, VPC Endpoint) → Bật **VPC Access** trong cấu hình dự án CodeBuild.
- 📎 Source: `AWS CodeBuild User Guide — Accessing a VPC from AWS CodeBuild`.

---

### Question 49 — Answer: **A**
- **Why correct:** Trạng thái **`UPDATE_ROLLBACK_FAILED`** xảy ra khi quá trình cập nhật CloudFormation gặp sự cố, hệ thống cố gắng quay lui (rollback) về trạng thái cũ nhưng một tài nguyên nào đó không thể hoàn tác (ví dụ S3 bucket được yêu cầu xóa nhưng bên trong đang chứa dữ liệu, dẫn đến thao tác xóa bị từ chối). Để khôi phục stack, lập trình viên phải khắc phục nguyên nhân chặn (xóa sạch file trong S3 bucket) hoặc gọi lệnh **`ContinueUpdateRollback`** kèm theo tham số **`ResourcesToSkip`** để yêu cầu CloudFormation bỏ qua tài nguyên bị kẹt và tiếp tục hoàn tất rollback stack về trạng thái `UPDATE_ROLLBACK_COMPLETE`.
- **Why the others are wrong:** B là giải pháp tiêu cực không thực tế. C sai vì stack đang ở trạng thái lỗi rollback không thể tiếp nhận lệnh `CreateStack` hay `UpdateStack` thông thường. D sai vì stack hoàn toàn có thể được khôi phục thông qua `ContinueUpdateRollback`.
- 🧠 **Key point / trap:** Khôi phục stack bị kẹt ở trạng thái `UPDATE_ROLLBACK_FAILED` → Xử lý nguyên nhân gây kẹt và gọi lệnh **`ContinueUpdateRollback` (có thể kết hợp `ResourcesToSkip`)**.
- 📎 Source: `AWS CloudFormation User Guide — Continue rollback on an update rollback failure`.

---

### Question 50 — Answer: **A**
- **Why correct:** Trong AWS CodeDeploy, bạn có thể cấu hình **Deployment Alarms** trong cài đặt của **Deployment Group**. Bằng cách liên kết một Amazon CloudWatch Alarm (đo lường lỗi 5XX hoặc độ trễ) và kích hoạt tùy chọn **Automatic Rollback**, CodeDeploy sẽ liên tục giám sát trạng thái của alarm trong suốt quá trình dịch chuyển lưu lượng truy cập (ví dụ trong 5 phút của bản canary). Nếu alarm chuyển sang trạng thái `ALARM`, CodeDeploy sẽ lập tức dừng đợt triển khai và đảo ngược 100% traffic quay trở lại phiên bản cũ mà không cần sự can thiệp thủ công của con người.
- **Why the others are wrong:** B sai vì viết script tự chế thiếu độ tin cậy và không tận dụng được tính năng quản lý tự động tích hợp sẵn của CodeDeploy. C sai vì `appspec.yml` quản lý các lifecycle hooks và file mapping, không phải nơi cấu hình CloudWatch alarms của deployment group. D sai vì CodeDeploy hỗ trợ cực kỳ mạnh mẽ tính năng tự động rollback theo alarms.
- 🧠 **Key point / trap:** Tự động rollback trong CodeDeploy khi phát hiện lỗi trong quá trình Canary → Cấu hình **Deployment Alarms + Automatic Rollback** trong **Deployment Group**.
- 📎 Source: `AWS CodeDeploy User Guide — Monitoring deployments with Amazon CloudWatch alarms and automatic rollback`.

---

### Question 51 — Answer: **A**
- **Why correct:** Tính năng **AWS SAM Accelerate** được kích hoạt thông qua lệnh **`sam sync --watch`**. Trong quá trình phát triển tích cực, lệnh này lắng nghe các thay đổi mã nguồn cục bộ và thực hiện đồng bộ trực tiếp (direct synchronization) code của hàm Lambda, OpenAPI definition của API Gateway, hoặc cấu hình Step Functions lên môi trường đám mây AWS mà **hoàn toàn bỏ qua quy trình tạo Change Set và cập nhật stack của CloudFormation**. Nhờ đó, thời gian triển khai từ khi sửa code tới khi thử nghiệm trên AWS được rút ngắn từ vài phút xuống chỉ còn vài giây.
- **Why the others are wrong:** B, C, D đều là các lệnh không tồn tại trong bộ công cụ chuẩn của AWS SAM CLI.
- 🧠 **Key point / trap:** Đồng bộ code serverless lên AWS siêu tốc trong lúc code (bỏ qua CloudFormation) → Lệnh **`sam sync --watch`** (SAM Accelerate).
- 📎 Source: `AWS Serverless Application Model Developer Guide — Accelerating serverless development with sam sync`.

---

### Question 52 — Answer: **A**
- **Why correct:** Kiến trúc của **AWS Elastic Beanstalk Worker Environment**:
  1. Elastic Beanstalk tự động tạo một hàng đợi Amazon SQS và cài đặt một tiến trình chạy nền độc quyền của AWS có tên là **`sqsd` (SQS Daemon)** trên từng máy chủ EC2 worker.
  2. Tiến trình `sqsd` liên tục thực hiện long-polling để lấy các tin nhắn từ hàng đợi SQS.
  3. Khi nhận được tin nhắn, `sqsd` sẽ đóng gói nội dung tin nhắn và gửi một HTTP request phương thức **`POST`** tới ứng dụng web chạy cục bộ trên máy chủ tại địa chỉ **`http://localhost/`**.
  4. Nếu ứng dụng trả về mã HTTP `200 OK`, `sqsd` sẽ tự động xóa tin nhắn khỏi hàng đợi SQS. Nhờ đó, lập trình viên chỉ cần viết ứng dụng nhận HTTP request thông thường mà không cần viết code kết nối SDK tới SQS.
- **Why the others are wrong:** B, C, D đều mô tả sai kiến trúc hoạt động của Elastic Beanstalk Worker tier.
- 🧠 **Key point / trap:** Cơ chế hoạt động của Elastic Beanstalk Worker Environment: Daemon **`sqsd`** đọc tin nhắn từ SQS và **HTTP POST tới `http://localhost/`** của ứng dụng.
- 📎 Source: `AWS Elastic Beanstalk Developer Guide — Elastic Beanstalk worker environments`.

---

### Question 53 — Answer: **A**
- **Why correct:** Trong kiến trúc monorepo (nhiều microservices nằm chung một Git repository), AWS CodePipeline theo mặc định sẽ kích hoạt bất cứ khi nào có commit mới đẩy lên branch. Để kích hoạt có chọn lọc:
  - Cấu hình GitHub gửi webhook sự kiện push tới **Amazon EventBridge**.
  - Viết các quy tắc **EventBridge Rules** để lọc nội dung sự kiện JSON của GitHub (kiểm tra mảng các tệp bị sửa đổi `modified_files`). Nếu các tệp nằm trong thư mục `/service-a/`, EventBridge sẽ chỉ kích hoạt duy nhất `Pipeline-A`, ngăn chặn việc kích hoạt lãng phí các pipeline khác.
- **Why the others are wrong:** B sai vì CodePipeline không có tính năng tự động lọc theo thư mục con trong monorepo nếu không dùng EventBridge. C làm mất đi giá trị của mô hình monorepo và gây khó khăn cho việc quản lý mã nguồn. D sai vì gộp chung một pipeline gây thắt cổ chai và mất tính độc lập của các vi dịch vụ.
- 🧠 **Key point / trap:** Kích hoạt CodePipeline có chọn lọc cho từng dịch vụ trong Git Monorepo → Sử dụng **Amazon EventBridge Rules lọc theo đường dẫn tệp thay đổi**.
- 📎 Source: `AWS DevOps Blog — Multi-pipeline triggers with GitHub and Amazon EventBridge`.

---

### Question 54 — Answer: **A**
- **Why correct:** Để có thể sử dụng các cú pháp rút gọn của AWS Serverless Application Model (SAM) bên trong một mẫu CloudFormation thông thường (chẳng hạn như tài nguyên `AWS::Serverless::Function`, `AWS::Serverless::Api`, `AWS::Serverless::SimpleTable`), phần khai báo cấp cao nhất của template bắt buộc phải chứa macro chuyển đổi:
  **`Transform: AWS::Serverless-2016-10-31`**
  Khi CloudFormation gặp khai báo này, nó sẽ gọi hệ thống chuyển đổi macro của SAM để tự động dịch các tài nguyên rút gọn này thành hàng chục tài nguyên CloudFormation nguyên bản (như `AWS::Lambda::Function`, `AWS::IAM::Role`, `AWS::Lambda::Permission`) trước khi tiến hành khởi tạo stack.
- **Why the others are wrong:** B là phiên bản định dạng template chuẩn của CloudFormation, không kích hoạt macro SAM. C chỉ là phần mô tả văn bản. D không phải là macro hợp lệ của AWS.
- 🧠 **Key point / trap:** Khai báo bắt buộc để dùng tài nguyên Serverless trong CloudFormation: **`Transform: AWS::Serverless-2016-10-31`**.
- 📎 Source: `AWS CloudFormation User Guide — AWS::Serverless transform`.

---

### Question 55 — Answer: **A**
- **Why correct:** **CloudWatch Metric Math** cung cấp hàm **`SEARCH()`** cho phép truy vấn và tổng hợp các metric một cách linh hoạt và động (dynamic query). Cú pháp:
  `SEARCH('{AWS/EC2,AutoScalingGroupName} MetricName="CPUUtilization"', 'Average', 300)`
  sẽ tự động tìm kiếm tất cả các metric `CPUUtilization` thuộc về nhóm Auto Scaling group được chỉ định. Bất cứ khi nào Auto Scaling mở rộng (scale out) thêm máy chủ mới hoặc thu hẹp (scale in) máy chủ cũ, hàm `SEARCH()` sẽ tự động đưa các metric của máy chủ mới vào đồ thị bảng điều khiển mà không đòi hỏi bất kỳ sự can thiệp thủ công nào.
- **Why the others are wrong:** B sai vì gọi API tạo alarm cho từng instance mới là giải pháp thủ công, kém hiệu quả và dễ lỗi. C sai vì Detailed Monitoring chỉ tăng tần suất đo đạc, không giải quyết việc tự động gom nhóm trên dashboard. D sai vì SQS không phải là công cụ trực quan hóa dữ liệu CloudWatch.
- 🧠 **Key point / trap:** Tự động tổng hợp và vẽ đồ thị các instances động trong Auto Scaling Group trên CloudWatch → Sử dụng hàm **Metric Math `SEARCH()`**.
- 📎 Source: `Amazon CloudWatch User Guide — Using search expressions in metric math`.

---

### Question 56 — Answer: **A**
- **Why correct:** Các custom metric tiêu chuẩn trong Amazon CloudWatch có độ phân giải tối thiểu là 1 phút (60 giây). Để phục vụ các hệ thống tài chính hoặc giao dịch tần suất cao đòi hỏi độ trễ phản hồi cực thấp, CloudWatch hỗ trợ tính năng **High-Resolution Custom Metrics** với độ phân giải có thể xuống tới **1 giây**. Để xuất bản metric này, lập trình viên gọi API `PutMetricData` và chỉ định thuộc tính **`StorageResolution: 1`** bên trong đối tượng `MetricDatum`.
- **Why the others are wrong:** B sai vì bất kỳ tài khoản AWS nào cũng có thể gọi API xuất bản metric phân giải cao mà không cần gói hỗ trợ doanh nghiệp. C sai vì gọi 60 lần nhưng nếu không chỉ định `StorageResolution: 1` thì CloudWatch vẫn sẽ tự động gộp (aggregate) các điểm dữ liệu đó vào chung một block 1 phút. D không liên quan đến việc giám sát metric thời gian thực.
- 🧠 **Key point / trap:** Xuất bản metric thời gian thực dưới 1 phút (1 giây) lên CloudWatch → Đặt **`StorageResolution: 1`** trong lệnh `PutMetricData`.
- 📎 Source: `Amazon CloudWatch User Guide — Publishing high-resolution metrics`.

---

### Question 57 — Answer: **A**
- **Why correct:** Trong AWS X-Ray, quy tắc lấy mẫu (Sampling Rules) được điều khiển bởi hai tham số quan trọng:
  1. **`ReservoirSize` (Kích thước hồ chứa):** Số lượng request tối thiểu được đảm bảo lấy mẫu và ghi nhận trace mỗi giây (ở đây yêu cầu tối thiểu 1 req/s → `ReservoirSize = 1`). Khi số lượng request thấp, hồ chứa này đảm bảo luôn có dữ liệu trace để giám sát.
  2. **`FixedRate` (Tỷ lệ cố định):** Tỷ lệ phần trăm các request bổ sung vượt quá kích thước hồ chứa sẽ được lấy mẫu (ở đây yêu cầu 5% → `FixedRate = 0.05`).
- **Why the others are wrong:** B sai vì `FixedRate = 1.0` tương đương 100% (sẽ ghi nhận toàn bộ request gây tốn kém chi phí cực lớn). C sai vì hoán đổi giá trị của hai trường. D sai vì X-Ray không sử dụng cấu hình kiểu `SamplingMode: Random`.
- 🧠 **Key point / trap:** Cấu hình X-Ray Sampling Rules: **`ReservoirSize`** = số request tối thiểu/giây; **`FixedRate`** = % request vượt quá hồ chứa được lấy mẫu (ví dụ 0.05 = 5%).
- 📎 Source: `AWS X-Ray Developer Guide — Sampling rules`.

---

### Question 58 — Answer: **A**
- **Why correct:** Sự khác biệt cốt lõi giữa Annotations và Metadata trong AWS X-Ray:
  - **Annotations (Chú thích):** Là các cặp key-value đơn giản (chuỗi, số, boolean) **được đánh chỉ mục (indexed)** bởi hệ thống X-Ray. Nhờ được lập chỉ mục, người dùng có thể sử dụng chúng trong thanh tìm kiếm (Filter Expressions) của bảng điều khiển X-Ray để lọc và phân nhóm các trace (ví dụ `annotation.customerTier = "PLATINUM"`).
  - **Metadata (Siêu dữ liệu):** Là các cặp key-value có thể chứa bất kỳ kiểu dữ liệu phức tạp nào (đối tượng JSON, danh sách mảng lồng nhau, payload lớn) nhưng **KHÔNG được đánh chỉ mục**. Dữ liệu này chỉ có thể xem được khi bạn mở chi tiết một trace cụ thể để phân tích lỗi.
- **Why the others are wrong:** B sai vì ghi `rawPayloadData` (5 KB JSON) vào Annotations sẽ làm quá tải chỉ mục và vi phạm giới hạn kích thước của Annotation (tối đa 50 annotations/trace). C sai vì nếu ghi `customerTier` vào Metadata thì sẽ không thể sử dụng bộ lọc tìm kiếm trên giao diện console. D không tận dụng tính năng trace liên kết của X-Ray.
- 🧠 **Key point / trap:** X-Ray: **Annotations = Có lập chỉ mục (dùng để search/filter traces)**; **Metadata = Không lập chỉ mục (dùng để lưu debug payload xem chi tiết)**.
- 📎 Source: `AWS X-Ray Developer Guide — Adding annotations and metadata to subsegments`.

---

### Question 59 — Answer: **A**
- **Why correct:** **CloudWatch Embedded Metric Format (EMF)** là giải pháp tối ưu cho các ứng dụng Serverless hiệu năng cao. Thay vì phải thực hiện một lệnh gọi API mạng đồng bộ `PutMetricData` (làm chậm thời gian phản hồi của Lambda từ 50-100ms và tốn chi phí), ứng dụng chỉ cần in một chuỗi JSON có cấu trúc đặc biệt ra luồng xuất chuẩn (`stdout`). CloudWatch Logs sẽ tiếp nhận dòng log này và một hệ thống ngầm phía sau của AWS sẽ tự động trích xuất các thông số và phát hành thành các CloudWatch Custom Metrics hoàn toàn bất đồng bộ mà không làm chậm ứng dụng.
- **Why the others are wrong:** B sai vì tự duy trì một EC2 instance đi ngược lại nguyên lý kiến trúc không máy chủ và tốn kém chi phí. C phức tạp hóa kiến trúc khi phải thêm SQS và Lambda trung gian chỉ để gửi metric. D sai vì file tạm trong `/tmp` sẽ bị xóa mất và không tự chuyển thành metric được.
- 🧠 **Key point / trap:** Tạo custom metric từ Lambda không làm tăng độ trễ mạng và không bị throttle API → Sử dụng **CloudWatch Embedded Metric Format (EMF)** in ra `stdout`.
- 📎 Source: `Amazon CloudWatch User Guide — Ingesting high-cardinality logs and generating metrics with CloudWatch Embedded Metric Format`.

---

### Question 60 — Answer: **A**
- **Why correct:** Trong Amazon CloudFront:
  - **Cache Policy:** Định nghĩa các thành phần (headers, query strings, cookies) được đưa vào **Cache Key**. Để tối ưu hóa tỷ lệ trúng bộ nhớ đệm (Cache Hit Ratio), **KHÔNG ĐƯỢC** đưa `User-Agent` vào Cache Policy vì mỗi trình duyệt và thiết bị có chuỗi User-Agent khác nhau, việc đưa vào Cache Key sẽ khiến CloudFront phải lưu hàng triệu bản sao riêng lẻ và làm Cache Hit Ratio giảm về gần 0%.
  - **Origin Request Policy:** Định nghĩa các dữ liệu mà CloudFront sẽ chuyển tiếp (forward) tới máy chủ gốc (origin) nhưng **KHÔNG tham gia vào Cache Key**. Cấu hình chuyển tiếp `User-Agent` và `Authorization` trong Origin Request Policy cho phép backend nhận đủ thông tin để xác thực và phục vụ mà vẫn duy trì Cache Hit Ratio tối đa tại Edge.
- **Why the others are wrong:** B sai vì đưa vào Cache Policy sẽ làm vỡ vụn bộ nhớ đệm. C làm mất hoàn toàn lợi ích tăng tốc của mạng CDN. D làm mất khả năng nhận diện thiết bị của máy chủ gốc.
- 🧠 **Key point / trap:** Chuyển tiếp header cho Origin mà không làm vỡ cache key trên CloudFront: Cấu hình trong **Origin Request Policy** (chứ KHÔNG đưa vào Cache Policy).
- 📎 Source: `Amazon CloudFront Developer Guide — Controlling origin requests`.

---

### Question 61 — Answer: **A**
- **Why correct:** Mô hình đọc tiêu chuẩn (Standard Consumer Polling) của Kinesis sử dụng API `GetRecords` qua giao thức HTTP/1.1 polling. Các consumer phải gửi yêu cầu thăm dò liên tục và thường có độ trễ truyền dữ liệu từ 1,000ms đến 1,500ms. Trong khi đó, **Enhanced Fan-Out (EFO)** sử dụng kết nối HTTP/2 server push thông qua API **`SubscribeToShard`**. Dữ liệu được máy chủ Kinesis chủ động đẩy ngay lập tức về consumer khi có bản ghi mới, giảm độ trễ truyền tải từ đầu đến cuối xuống trung bình chỉ còn **~70 mili giây**.
- **Why the others are wrong:** B sai vì tăng số shard chỉ làm tăng thông lượng (throughput), không làm giảm độ trễ truyền tải của phương thức polling tiêu chuẩn. C sai vì thời gian lưu trữ không ảnh hưởng tới độ trễ truyền gói tin. D sai vì S3 không phải là dịch vụ streaming thời gian thực.
- 🧠 **Key point / trap:** Giảm độ trễ truyền tải Kinesis từ ~1s xuống dưới 100ms (~70ms) → Sử dụng **Enhanced Fan-Out (`SubscribeToShard` qua HTTP/2 push)**.
- 📎 Source: `Amazon Kinesis Data Streams Developer Guide — Developing Custom Consumers with Enhanced Fan-Out`.

---

### Question 62 — Answer: **A, B**
- **Why correct:** Hiện tượng **Cache Stampede (Thundering Herd)** xảy ra khi một key cực "hot" bị hết hạn, dẫn đến hàng trăm tiến trình cùng phát hiện cache miss và đồng loạt truy vấn cơ sở dữ liệu cùng một thời điểm. Hai giải pháp chuẩn mực để giải quyết vấn đề này:
  1. **Triển khai Khóa Phân tán (Distributed Mutex Lock):** Tiến trình đầu tiên phát hiện cache miss sẽ chiếm khóa (lock key). Chỉ duy nhất tiến trình này được phép truy vấn database và cập nhật lại cache; các tiến trình khác sẽ chờ hoặc tạm thời nhận dữ liệu cũ (stale data).
  2. **Làm mới bộ nhớ đệm sớm theo xác suất (Probabilistic Early Expiration / Thuật toán XFetch):** Trước khi key thực sự hết hạn, hệ thống dựa trên một thuật toán xác suất để một worker tiến hành làm mới key đó chạy nền một cách bất đồng bộ, đảm bảo key không bao giờ rơi vào trạng thái hết hạn hoàn toàn khi có người dùng truy cập.
- **Why the others are wrong:** C sai vì đặt TTL = 0 giây sẽ biến cache thành vô dụng và khiến toàn bộ request đánh thẳng vào DB. D và E không giải quyết được hiện tượng quá tải DB mà còn làm vấn đề nghiêm trọng hơn.
- 🧠 **Key point / trap:** Chống sập DB do Cache Stampede / Thundering Herd: **Distributed Mutex Lock** hoặc **Probabilistic Early Expiration (XFetch)**.
- 📎 Source: `Amazon ElastiCache for Redis Best Practices — Caching strategies and cache stampede`.

---

### Question 63 — Answer: **A**
- **Why correct:** Hạn mức yêu cầu của Amazon S3: Mỗi **tiền tố được phân vùng (partitioned prefix)** trong một S3 bucket hỗ trợ tối đa **3,500 yêu cầu PUT/POST/DELETE** và **5,500 yêu cầu GET/HEAD** mỗi giây. Khi tải lên 20,000 ảnh/giây mà toàn bộ các file đều dùng chung tiền tố ngày tháng `/2026/09/26/`, lưu lượng đã vượt quá xa hạn mức 3,500 PUT/s của một tiền tố duy nhất, dẫn đến lỗi `HTTP 503 Slow Down`. Giải pháp chuẩn là phân tán dữ liệu ra nhiều tiền tố độc lập bằng cách thêm mã băm ngẫu nhiên (hash prefix) hoặc Customer ID vào đầu đường dẫn (ví dụ `s3://bucket/<hash>/2026/09/26/image.jpg`).
- **Why the others are wrong:** B sai vì S3 không giới hạn số lượng đối tượng lưu trong bucket. C sai vì Transfer Acceleration chỉ tối ưu đường truyền mạng, không thay đổi giới hạn TPS trên từng prefix của S3. D sai vì lớp lưu trữ Intelligent-Tiering chỉ tối ưu chi phí lưu trữ, không can thiệp vào hạn mức request rate.
- 🧠 **Key point / trap:** Giới hạn request S3 trên 1 prefix: **3,500 PUT/POST/DELETE và 5,500 GET mỗi giây**. Bị lỗi `503 Slow Down` do tải cao → **Phân tán tiền tố (Prefix Partitioning / Hash Prefix)**.
- 📎 Source: `Amazon S3 User Guide — Optimizing Amazon S3 performance`.

---

### Question 64 — Answer: **A**
- **Why correct:** **CloudWatch Composite Alarms** cho phép kết hợp nhiều cảnh báo số liệu (metric alarms) lại với nhau bằng các toán tử logic Boolean (`AND`, `OR`, `NOT`). Bằng cách tạo một Composite Alarm với biểu thức:
  `ALARM("HighCPUUtilization") AND ALARM("LowFreeMemory")`
  cảnh báo chỉ kích hoạt và gửi tin nhắn thông báo (paging alert) khi và chỉ khi CẢ HAI điều kiện đều vi phạm cùng lúc, giúp giảm triệt để hiện tượng báo động giả và loại bỏ tình trạng "ngộ độc cảnh báo" (alert fatigue) cho đội ngũ vận hành.
- **Why the others are wrong:** B sai vì tăng thời gian đánh giá lên 7 ngày làm mất tính kịp thời khi có sự cố khẩn cấp. C sai vì Logs Insights dùng để truy vấn nhật ký log, không tạo ra cảnh báo kết hợp trạng thái. D là hành vi bỏ mặc hệ thống không an toàn.
- 🧠 **Key point / trap:** Kết hợp nhiều cảnh báo CloudWatch bằng điều kiện logic (`AND`, `OR`) để giảm báo động giả → **CloudWatch Composite Alarms**.
- 📎 Source: `Amazon CloudWatch User Guide — Creating a composite alarm`.

---

### Question 65 — Answer: **A**
- **Why correct:** Amazon API Gateway sử dụng thuật toán **Token Bucket** để kiểm soát và điều tiết lưu lượng (throttling):
  - **Burst Capacity (Dung lượng xô):** Số lượng token tối đa mà xô có thể chứa tại một thời điểm (ở đây là 1,000 tokens).
  - **Rate Limit (Tốc độ nạp):** Tốc độ nạp lại token vào xô theo thời gian (500 tokens/giây).
  Khi client gửi một đợt bùng nổ 1,200 request trong 100ms, nó đã tiêu thụ hết toàn bộ 1,000 token của xô và 200 request vượt quá sẽ bị từ chối ngay lập tức với mã lỗi **`HTTP 429 Too Many Requests`**. Để xử lý lỗi này, phía ứng dụng client bắt buộc phải triển khai thuật toán thử lại với độ trễ tăng dần kết hợp biến động ngẫu nhiên (**Exponential Backoff and Jitter**).
- **Why the others are wrong:** B sai vì đổi IP không giải quyết được việc cạn kiệt token trên Usage Plan của API key. C sai vì lỗi 429 được trả về trực tiếp từ tầng API Gateway trước khi request chạm tới Lambda. D sai vì HTTPS không liên quan tới thuật toán token bucket.
- 🧠 **Key point / trap:** API Gateway Throttling sử dụng **Token Bucket Algorithm**. Client gặp lỗi HTTP 429 → Bắt buộc áp dụng **Exponential Backoff and Jitter**.
- 📎 Source: `Amazon API Gateway Developer Guide — Throttle API requests for better throughput`.
