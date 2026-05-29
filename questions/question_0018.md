# Question #18 - Topic 1

An application development team is designing a microservice that will convert large images to smaller, compressed images. When a user uploads an image through the web interface, the microservice should store the image in an Amazon S3 bucket, process and compress the image with an AWS Lambda function, and store the image in its compressed form in a different S3 bucket. A solutions architect needs to design a solution that uses durable, stateless components to process the images automatically. Which combination of actions will meet these requirements? (Choose two.)

## Options

**A.** Create an Amazon Simple Queue Service (Amazon SQS) queue. Configure the S3 bucket to send a notification to the SQS queue when an image is uploaded to the S3 bucket.

**B.** Configure the Lambda function to use the Amazon Simple Queue Service (Amazon SQS) queue as the invocation source. When the SQS message is successfully processed, delete the message in the queue.

**C.** Configure the Lambda function to monitor the S3 bucket for new uploads. When an uploaded image is detected, write the file name to a text file in memory and use the text file to keep track of the images that were processed.

**D.** Launch an Amazon EC2 instance to monitor an Amazon Simple Queue Service (Amazon SQS) queue. When items are added to the queue, log the file name in a text file on the EC2 instance and invoke the Lambda function.

**E.** Configure an Amazon EventBridge (Amazon CloudWatch Events) event to monitor the S3 bucket. When an image is uploaded, send an alert to an Amazon ample Notification Service (Amazon SNS) topic with the application owner's email address for further processing.



## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Team phát triển thiết kế microservice để nén ảnh lớn thành ảnh nhỏ hơn. Khi người dùng upload ảnh qua web, microservice cần lưu ảnh vào một `Amazon S3` bucket, xử lý/nén bằng `AWS Lambda`, rồi lưu ảnh đã nén vào `S3 bucket` khác.
- **Existing Resources:** `Amazon S3`, `AWS Lambda`.
- **Current Issue/Goal:** Cần thiết kế giải pháp sử dụng các thành phần **bền vững (durable)** và **phi trạng thái (stateless)** để xử lý ảnh **tự động**. Chọn **2 đáp án** đúng.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| `durable` | Dữ liệu/job không bị mất nếu component xử lý gặp lỗi. Cần dùng hàng đợi như `Amazon SQS` để lưu trữ sự kiện. |
| `stateless` | Không lưu trạng thái xử lý (như danh sách file đã xử lý) trên disk/memory cục bộ của compute instance. |
| `process automatically` | Toàn bộ pipeline chạy tự động, không cần can thiệp thủ công (không gửi email cho con người xử lý). |
| `S3 event notification` | `S3` có thể phát thông báo sự kiện đến `SQS`, `SNS`, hoặc `Lambda`. |
| `Lambda event source mapping` | Lambda tự động poll message từ `SQS` và tự xóa message khỏi queue sau khi xử lý thành công. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Multiple choice (Choose two) — chọn tổ hợp kiến trúc phù hợp.
- **Constraints:** Durable, stateless, automatic. Không dùng server EC2 để giám sát. Không lưu state vào file text cục bộ.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A và B**

**Giải thích:**
- **A:** Tạo `Amazon SQS` queue và cấu hình `S3 event notification` để gửi message vào queue khi có ảnh mới được upload. Điều này đảm bảo tính **durable** — nếu `Lambda` bị lỗi, không khả dụng hoặc bị throttle, sự kiện vẫn được giữ lại trong `SQS` để xử lý lại sau.
- **B:** Cấu hình `Lambda` sử dụng `SQS` làm nguồn kích hoạt (event source mapping). Khi message được xử lý thành công, `Lambda` service **tự động xóa message khỏi queue**. Cách này hoàn toàn **stateless**: `Lambda` chỉ cần đọc object key từ message body để xử lý, không cần ghi nhớ trạng thái ra disk hay memory cục bộ.

Tổ hợp **A + B** tạo thành pipeline tiêu chuẩn: `S3` -> `SQS` -> `Lambda` -> `S3`, đáp ứng đầy đủ 3 yêu cầu durable, stateless và automatic.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án C:**
- `Lambda` không thể tự "monitor" liên tục `S3` bucket; nó là dịch vụ event-driven, phải được trigger bởi event source.
- Việc ghi tên file vào **text file trong memory** để theo dõi là **stateful**. Khi execution environment của `Lambda` bị recycle, file này bị mất, dẫn đến xử lý trùng lặp hoặc bỏ sót file. Trực tiếp vi phạm yêu cầu stateless.

**❌ Đáp án D:**
- Dùng `Amazon EC2` để poll `SQS` và log file vào disk cục bộ là **stateful**, không durable (nếu instance fail, dữ liệu trạng thái có nguy cơ mất), và không tự động hoá/serverless.
- Việc EC2 invoke `Lambda` thủ công tạo ra single point of failure và tăng độ phức tạp không cần thiết.

**❌ Đáp án E:**
- Gửi alert đến `Amazon SNS` topic rồi gửi email cho owner là **xử lý thủ công/manual**, không phải **automatic processing**. Đề bài yêu cầu hệ thống tự động nén ảnh, không phải gửi thông báo cho con người để xử lý tiếp.

## 6


 ---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Một team phát triển đang thiết kế microservice để nén ảnh. Người dùng upload ảnh lớn qua giao diện web, ảnh gốc được lưu vào `Amazon S3` bucket, sau đó được xử lý và nén bởi `AWS Lambda`, rồi lưu ảnh đã nén vào một `S3` bucket khác.
- **Existing Resources:** `Amazon S3`, `AWS Lambda`
- **Current Issue/Goal:** Thiết kế giải pháp sử dụng các thành phần `durable` (bền vững, chống mất mát) và `stateless` (phi trạng thái) để tự động xử lý ảnh. Cần chọn **2 đáp án** đúng.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `durable` | Cần đảm bảo dữ liệu/job không bị mất nếu component fail → dùng `Amazon SQS` để lưu trữ message bền vững |
| `stateless` | Không được lưu trạng thái xử lý trên local disk, memory, hoặc `EC2` instance → tránh dùng text file để tracking |
| `automatically` | Quy trình tự động, không cần can thiệp thủ công như gửi email |
| `microservice` | Kiến trúc decoupled, thường kết hợp `S3` + `SQS` + `Lambda` |
| `Choose two` | Cần chọn 2 đáp án bổ sung nhau tạo thành một luồng xử lý hoàn chỉnh |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Architecture design (Most durable + stateless + automatic)
- **Constraints:** Sử dụng durable components, stateless components, xử lý tự động, không operational overhead không cần thiết

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A và B**

**Giải thích:**
- **Đáp án A:** Thiết lập `S3 Event Notification` gửi message đến `Amazon SQS` khi có object mới được upload. `SQS` đóng vai trò `durable message queue`, giữ lại thông tin về ảnh cần xử lý ngay cả khi `Lambda` đang bận hoặc fail. Điều này decouple quá trình upload và xử lý, đảm bảo không mất job.
- **Đáp án B:** Cấu hình `Lambda` sử dụng `Amazon SQS` queue làm `invocation source` (event source mapping). `Lambda` sẽ tự động poll message từ queue, xử lý ảnh (compression), và xóa message khỏi queue sau khi xử lý thành công. Điều này đảm bảo tính `stateless` và `automatic processing`.
- Kết hợp A + B tạo thành luồng hoàn chỉnh: `S3` (upload) → `SQS` (durable queue
