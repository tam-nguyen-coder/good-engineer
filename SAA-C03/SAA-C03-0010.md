# Question #10 - Topic 1

A company is building an ecommerce web application on AWS. The application sends information about new orders to an Amazon API Gateway REST API to process. The company wants to ensure that orders are processed in the order that they are received. Which solution will meet these requirements?

## Options

**A.** Use an API Gateway integration to publish a message to an Amazon Simple Notification Service (Amazon SNS) topic when the application receives an order. Subscribe an AWS Lambda function to the topic to perform processing.

**B.** Use an API Gateway integration to send a message to an Amazon Simple Queue Service (Amazon SQS) FIFO queue when the application receives an order. Configure the SQS FIFO queue to invoke an AWS Lambda function for processing.

**C.** Use an API Gateway authorizer to block any requests while the application processes an order.

**D.** Use an API Gateway integration to send a message to an Amazon Simple Queue Service (Amazon SQS) standard queue when the application receives an order. Configure the SQS standard queue to invoke an AWS Lambda function for processing.



---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Một công ty đang xây dựng ứng dụng web thương mại điện tử trên AWS. Ứng dụng gửi thông tin đơn hàng mới đến `Amazon API Gateway` REST API để xử lý.
- **Existing Resources:** `Amazon API Gateway` REST API.
- **Current Issue/Goal:** Đảm bảo các đơn hàng được xử lý đúng theo thứ tự chúng được nhận vào hệ thống (first-in-first-out).

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| `processed in the order that they are received` | Yêu cầu bắt buộc về thứ tự xử lý FIFO |
| `Amazon API Gateway` | Cổng vào cho các request từ ứng dụng ecommerce |
| `Amazon SQS FIFO queue` | Hàng đợi đảm bảo thứ tự tin nhắn và xử lý exactly-once |
| `Amazon SQS standard queue` | Hàng đợi không đảm bảo thứ tự, chỉ đảm bảo at-least-once delivery |
| `Amazon SNS` | Dịch vụ pub/sub; topic chuẩn không đảm bảo thứ tự |
| `AWS Lambda` | Dịch vụ xử lý compute serverless |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Chọn giải pháp kiến trúc (solution selection) đảm bảo tính tuần tự.
- **Constraints:** Các đơn hàng phải được xử lý theo đúng thứ tự nhận được; sử dụng `API Gateway` làm điểm vào.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**
**Giải thích:** Để đảm bảo các đơn hàng được xử lý đúng thứ tự nhận vào, cần sử dụng `Amazon SQS FIFO queue`. `SQS FIFO` được thiết kế đặc biệt để duy trì thứ tự tin nhắn (first-in-first-out) và cung cấp khả năng xử lý exactly-once. Khi `API Gateway` gửi message vào `SQS FIFO queue` thông qua AWS Service integration, các message sẽ được giữ nguyên thứ tự. Sau đó, `SQS FIFO queue` có thể được cấu hình làm event source để trigger `AWS Lambda` function xử lý tuần tự, đáp ứng yêu cầu đề bài.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:** `Amazon SNS` topic chuẩn (standard) là dịch vụ pub/sub không đảm bảo thứ tự phân phối message đến subscriber. Mặc dù AWS có `SNS FIFO`, nhưng đề bài chỉ đề cập đến SNS topic thông thường. Do đó, giải pháp này không đáp ứng yêu cầu xử lý theo thứ tự.

**❌ Đáp án C:** `API Gateway authorizer` chỉ được sử dụng cho mục đích xác thực (`authentication`) và ủy quyền (`authorization`), không phải để kiểm soát luồng xử lý hay chặn request trong khi hệ thống đang bận. Giải pháp này không đảm bảo thứ tự, đồng thời tạo ra điểm nghẽn nghiêm trọng và không khả thi trong kiến trúc thực tế.

**❌ Đáp án D:** `Amazon SQS standard queue` không đảm bảo thứ tự message (chỉ cung cấp best-effort ordering). Message có thể bị xử lý không theo thứ tự hoặc bị duplicate. Do đó, không đáp ứng được yêu cầu bắt buộc về ordering của đề bài.

## 6. MẸO GHI NHỚ
🧠 *Khi đề bài xuất hiện yêu cầu về thứ tự xử lý (order / sequence / FIFO), hãy ưu tiên tìm `SQS FIFO` hoặc `SNS FIFO`. Trong các lựa chọn có cả Standard và FIFO, luôn chọn FIFO nếu ordering là yêu cầu bắt buộc. `API Gateway` hoàn toàn có thể tích hợp trực tiếp với `SQS` thông qua AWS Service integration mà không cần thành phần trung gian.*


 ---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Một công ty đang xây dựng ứng dụng web thương mại điện tử trên `AWS`. Ứng dụng gửi thông tin về đơn hàng mới đến `Amazon API Gateway` `REST API` để xử lý.
- **Existing Resources:** `Amazon API Gateway` `REST API`
- **Current Issue/Goal:** Đảm bảo các đơn hàng được xử lý đúng theo thứ tự mà chúng được nhận (ordering guarantee).

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `processed in the order` | Yêu cầu cốt lõi: đảm bảo thứ tự nghiêm ngặt (first-in-first-out) |
| `Amazon API Gateway` | Cần sử dụng `integration` để gửi `message` đến dịch vụ hàng đợi |
| `Amazon SQS` `FIFO queue` | Hàng đợi đảm bảo thứ tự và `exactly-once processing` |
| `Amazon SQS` `standard queue` | Chỉ có `best-effort ordering`, không đảm bảo thứ tự tuyệt đối |
| `Amazon SNS` | `Pub/sub`, `standard topic` không đảm bảo thứ tự đến `subscriber` |
| `AWS Lambda` | Dịch vụ compute để xử lý đơn hàng, có thể được `invoke` bởi `SQS` |
| `message group` | Trong `SQS FIFO`, thứ tự được đảm bảo trong cùng một `message group` |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements (đảm bảo thứ tự xử lý)
- **Constraints:** Các đơn hàng phải được xử lý đúng thứ tự nhận; không đề cập đến chi phí nhưng cần giải pháp đúng cho ordering

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- `Amazon SQS` `FIFO queue` là dịch vụ được thiết kế riêng để đảm bảo thứ tự `message` (`ordering guarantee`) và ngăn chặn trùng lặp (`exactly-once processing`).
- `API Gateway` có thể cấu hình `AWS service integration` để gửi trực tiếp `message` đến `SQS` `FIFO queue` khi nhận được đơn hàng mới.
- Khi cấu hình `SQS` `FIFO queue` làm `event source` cho `AWS Lambda`, các `message` sẽ được `invoke` và xử lý theo đúng thứ tự trong cùng một `message group`, hoàn toàn đáp ứng yêu cầu đề bài.
- Đây là kiến trúc chuẩn: `API Gateway` → `SQS FIFO` → `Lambda` cho các use case thương mại điện tử cần ordering.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- `Amazon SNS` `standard topic` không đảm bảo thứ tự phân phối `message` đến các `subscriber`. Khi có nhiều `Lambda` `subscriber` hoặc xử lý song song, thứ tự có thể bị xáo trộn.
- Ngay cả `SNS` `FIFO topic` cũng không phải là lựa chọn tối ưu khi cần một luồng xử lý tuần tự đơn giản vì `SNS` được thiết kế cho `fan-out` (phát tán).
- **When correct:** Khi cần gửi cùng một thông báo đến nhiều `subscriber` mà không yêu cầu thứ tự nghiêm ngặt.

**❌ Đáp án C:**
- `API Gateway authorizer` chỉ được dùng cho `authentication` và `authorization` (xác thực, ủy quyền), không có chức năng kiểm soát luồng xử lý hay `block request` để đảm bảo thứ tự.
- Việc `block` các `request` trong khi xử lý sẽ làm giảm `throughput`, tăng `latency` và không giải quyết được vấn đề ordering.
- **When correct:** Khi cần bảo mật `API`, kiểm tra `token`/`JWT` trước khi cho phép truy cập.

**❌ Đáp án D:**
- `Amazon SQS` `standard queue` chỉ cung cấp `best-effort ordering`, nghĩa là `message` hoàn toàn có thể bị xử lý không đúng thứ tự (`out-of-order`) khi hệ thống có sự cố hoặc xử lý song song.
- `Standard queue` cũng có thể tạo ra `duplicate messages`.
- **When correct:** Khi cần `throughput` cao nhất, không yêu cầu thứ tự nghiêm ngặt, và application có khả năng xử lý trùng lặp.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Cần đúng thứ tự → nhớ ngay `SQS FIFO`; `standard` là 'hên xui' ordering, `SNS` là phát tán không giữ thứ tự."*

---
