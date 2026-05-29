# Question #41 - Topic 1

A company's application integrates with multiple software-as-a-service (SaaS) sources for data collection. The company runs Amazon EC2 instances to receive the data and to upload the data to an Amazon S3 bucket for analysis. The same EC2 instance that receives and uploads the data also sends a notification to the user when an upload is complete. The company has noticed slow application performance and wants to improve the performance as much as possible. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Create an Auto Scaling group so that EC2 instances can scale out. Configure an S3 event notification to send events to an Amazon Simple Notification Service (Amazon SNS) topic when the upload to the S3 bucket is complete.

**B.** Create an Amazon AppFlow flow to transfer data between each SaaS source and the S3 bucket. Configure an S3 event notification to send events to an Amazon Simple Notification Service (Amazon SNS) topic when the upload to the S3 bucket is complete.

**C.** Create an Amazon EventBridge (Amazon CloudWatch Events) rule for each SaaS source to send output data. Configure the S3 bucket as the rule's target. Create a second EventBridge (Cloud Watch Events) rule to send events when the upload to the S3 bucket is complete. Configure an Amazon Simple Notification Service (Amazon SNS) topic as the second rule's target.

**D.** Create a Docker container to use instead of an EC2 instance. Host the containerized application on Amazon Elastic Container Service (Amazon ECS). Configure Amazon CloudWatch Container Insights to send events to an Amazon Simple Notification Service (Amazon SNS) topic when the upload to the S3 bucket is complete.



 ## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty có ứng dụng tích hợp với nhiều nguồn `SaaS` để thu thập dữ liệu.
- **Existing Resources:** `Amazon EC2 instances` đang đảm nhận đồng thời 3 nhiệm vụ: (1) nhận dữ liệu từ các nguồn `SaaS`, (2) upload dữ liệu lên `Amazon S3`, và (3) gửi thông báo đến người dùng khi upload hoàn tất.
- **Current Issue/Goal:** Ứng dụng đang chậm, cần cải thiện hiệu năng nhiều nhất có thể (`improve the performance as much as possible`) với `LEAST operational overhead`.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| `SaaS` sources | Các ứng dụng phần mềm dịch vụ bên thứ ba (Salesforce, Slack, Google Analytics, v.v.) |
| `EC2` instances | Compute đang làm quá nhiều việc, trở thành điểm nghẽn hiệu năng |
| `Amazon AppFlow` | Dịch vụ fully managed chuyên dụng để truyền dữ liệu giữa `SaaS` và AWS |
| `S3` event notification | Cơ chế native của S3 để phát sự kiện khi object được tạo/xóa |
| `LEAST operational overhead` | Ưu tiên giải pháp managed/serverless, không cần tự quản lý compute |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Tối ưu hóa kiến trúc (Architecture Optimization)
- **Constraints:** Phải cải thiện hiệu năng tối đa và overhead vận hành thấp nhất

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**
**Giải thích:** `Amazon AppFlow` là dịch vụ được thiết kế riêng để tích hợp và chuyển dữ liệu từ hàng chục ứng dụng `SaaS` phổ biến trực tiếp vào `Amazon S3` mà không cần viết code hay duy trì `EC2`. Việc này loại bỏ hoàn toàn điểm nghẽn hiệu năng do EC2 phải nhận và upload data. Kết hợp với `S3 event notification` gửi đến `Amazon SNS`, hệ thống có thể tự động thông báo cho người dùng khi upload hoàn tất mà không cần bất kỳ compute instance nào xử lý. Đây là giải pháp fully managed, giúp cải thiện hiệu năng tối đa và overhead thấp nhất.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:** Dùng `Auto Scaling group` giúp scale out `EC2`, nhưng các instance vẫn phải tự quản lý kết nối đến từng nguồn `SaaS`, viết/maintain code integration, và quản lý fleet EC2. Điều này không loại bỏ được gánh nặng chính gây chậm (xử lý SaaS integration trên EC2) và vẫn có operational overhead cao hơn đáp án B.

**❌ Đáp án C:** `Amazon EventBridge` (CloudWatch Events) là event bus, không phải công cụ transfer dữ liệu (data transfer pipeline). Không thể dùng EventBridge rule để chuyển khối lượng dữ liệu lớn từ SaaS vào `S3` như một target trực tiếp. Kiến trúc này không phù hợp với bài toán chuyển data, lại còn phức tạp hơn cần thiết.

**❌ Đáp án D:** Chuyển từ `EC2` sang `Amazon ECS` container vẫn đòi hỏi quản lý compute (cluster, task definition, service) và vẫn phải tự viết logic tích hợp `SaaS` bên trong container. Đặc biệt, `CloudWatch Container Insights` là công cụ giám sát/giám sát hiệu năng container, hoàn toàn không có khả năng phát hiện việc upload lên `S3` để gửi event đến `SNS`. Đây là việc sử dụng sai dịch vụ.

## 6. MẸO GHI NHỚ
🧠 *Khi đề bài nhắc đến tích hợp dữ liệu từ `SaaS` và yêu cầu giảm operational overhead — hãy ưu tiên nghĩ đến `Amazon AppFlow`. Khi cần thông báo sự kiện từ `S3`, pattern đơn giản nhất là `S3 Event Notification` → `SNS`.*
