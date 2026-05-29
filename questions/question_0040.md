# Question #40 - Topic 1

A company has thousands of edge devices that collectively generate 1 TB of status alerts each day. Each alert is approximately 2 KB in size. A solutions architect needs to implement a solution to ingest and store the alerts for future analysis. The company wants a highly available solution. However, the company needs to minimize costs and does not want to manage additional infrastructure. Additionally, the company wants to keep 14 days of data available for immediate analysis and archive any data older than 14 days. What is the MOST operationally efficient solution that meets these requirements?

## Options

**A.** Create an Amazon Kinesis Data Firehose delivery stream to ingest the alerts. Configure the Kinesis Data Firehose stream to deliver the alerts to an Amazon S3 bucket. Set up an S3 Lifecycle configuration to transition data to Amazon S3 Glacier after 14 days.

**B.** Launch Amazon EC2 instances across two Availability Zones and place them behind an Elastic Load Balancer to ingest the alerts. Create a script on the EC2 instances that will store the alerts in an Amazon S3 bucket. Set up an S3 Lifecycle configuration to transition data to Amazon S3 Glacier after 14 days.

**C.** Create an Amazon Kinesis Data Firehose delivery stream to ingest the alerts. Configure the Kinesis Data Firehose stream to deliver the alerts to an Amazon OpenSearch Service (Amazon Elasticsearch Service) cluster. Set up the Amazon OpenSearch Service (Amazon Elasticsearch Service) cluster to take manual snapshots every day and delete data from the cluster that is older than 14 days.

**D.** Create an Amazon Simple Queue Service (Amazon SQS) standard queue to ingest the alerts, and set the message retention period to 14 days. Configure consumers to poll the SQS queue, check the age of the message, and analyze the message data as needed. If the message is 14 days old, the consumer should copy the message to an Amazon S3 bucket and delete the message from the SQS queue.



 ## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty có hàng nghìn thiết bị edge, mỗi ngày tạo ra 1 TB cảnh báo trạng thái, mỗi cảnh báo khoảng 2 KB.
- **Existing Resources:** Hệ thống edge device hiện có đang gửi dữ liệu.
- **Current Issue/Goal:** Cần một giải pháp ingest và lưu trữ dữ liệu để phân tích sau này. Yêu cầu: highly available, tối thiểu chi phí, không quản lý thêm hạ tầng, giữ 14 ngày dữ liệu gần nhất để phân tích ngay lập tức, và archive dữ liệu cũ hơn 14 ngày.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| `thousands of edge devices` | Nguồn sinh dữ liệu lớn, phân tán, cần dịch vụ ingest có khả năng scale tự động |
| `1 TB each day` | Lưu lượng lớn, cần giải pháp lưu trữ có chi phí thấp |
| `highly available` | Giải pháp phải có tính sẵn sàng cao, loại bỏ single point of failure |
| `minimize costs` | ưu tiên dịch vụ serverless/managed, tránh provisioning thừa |
| `does not want to manage additional infrastructure` | Loại bỏ các đáp án có `EC2`, cần dịch vụ fully managed |
| `14 days available for immediate analysis` | Dữ liệu mới phải nằm ở tier có thể truy cập ngay (như `S3`) |
| `archive any data older than 14 days` | Cần chuyển dữ liệu cũ sang storage class/tier giá rẻ (như `S3 Glacier`) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Chọn kiến trúc tối ưu nhất (Most operationally efficient).
- **Constraints:** 
  - Không quản lý hạ tầng (no EC2, no self-managed).
  - HA tự nhiên.
  - Cost-optimized.
  - 14 ngày "hot data", còn lại "cold archive".

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**
**Giải thích:** 
- `Amazon Kinesis Data Firehose` là dịch vụ fully managed để ingest dữ liệu streaming từ hàng nghìn thiết bị, tự động scale, highly available, không cần quản lý server.
- Firehose có thể delivery trực tiếp vào `Amazon S3` bucket. `S3` cung cấp độ bền và sẵn sàng cao (11 9's durability, 99.99% availability), đồng thời là nơi lưu trữ cost-effective để phân tích dữ liệu trong 14 ngày (có thể dùng `Amazon Athena`, `Amazon QuickSight`, hoặc các công cụ phân tích khác trực tiếp trên `S3`).
- `S3 Lifecycle configuration` cho phép tự động chuyển dữ liệu sang `Amazon S3 Glacier` sau 14 ngày để archive với chi phí cực thấp, đáp ứng yêu cầu lưu trữ dài hạn mà không cần thao tác thủ công.
- Tổng thể, đây là giải pháp serverless, operationally efficient nhất, đáp ứng đầy đủ các yêu cầu về ingestion, HA, cost, và archiving.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:** Sử dụng `Amazon EC2` instances đặt sau `Elastic Load Balancer` để ingest dữ liệu. Vi phạm trực tiếp yêu cầu "does not want to manage additional infrastructure" vì phải quản lý server (patching, scaling, HA cho EC2, script tự viết). Đây là anti-pattern cho ingestion quy mô lớn so với dịch vụ managed như `Kinesis`.

**❌ Đáp án C:** `Amazon OpenSearch Service` (hay Elasticsearch) rất đắt đỏ để lưu 1 TB dữ liệu mỗi ngày và giữ 14 TB cho phân tích ngay lập tức. Hơn nữa, đáp án đề cập "manual snapshots" và "delete data older than 14 days" — việc snapshot thủ công không operationally efficient, và xóa dữ liệu không phải là archive (không đáp ứng yêu cầu lưu trữ dài hạn chi phí thấp).

**❌ Đáp án D:** `Amazon SQS` là message queue, không phải dịch vụ lưu trữ hay analytics. Việc dùng consumer để poll, kiểm tra tuổi message, rồi copy sang `S3` là operational overhead rất lớn. `SQS` không được thiết kế để lưu 1 TB dữ liệu mỗi ngày trong 14 ngày để phân tích — đây là kiến trúc sai mục đích (abusing queue as database).

## 6. MẸO GHI NHỚ
🧠 *Khi đề bài yêu cầu: ingest từ nhiều nguồn + không quản lý hạ tầng + lưu trữ lâu dài + archive tự động → nghĩ ngay đến `Kinesis Data Firehose` → `S3` + `S3 Lifecycle` → `S3 Glacier`. Tránh `EC2` (manage infra), tránh `OpenSearch` (đắt tiền cho log/archive), tránh `SQS` (không phải storage).*


 ---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty có hàng nghìn thiết bị edge, mỗi ngày tạo ra 1 TB cảnh báo trạng thái, mỗi cảnh báo khoảng 2 KB.
- **Existing Resources:** Hệ thống edge device hiện có đang gửi dữ liệu.
- **Current Issue/Goal:** Cần một giải pháp ingest và lưu trữ dữ liệu để phân tích sau này. Yêu cầu: `highly available`, tối thiểu chi phí, không quản lý thêm hạ tầng, giữ 14 ngày dữ liệu gần nhất để `immediate analysis`, và `archive` dữ liệu cũ hơn 14 ngày.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `thousands of edge devices` | Nguồn sinh dữ liệu lớn, phân tán, cần dịch vụ ingest có khả năng scale tự động |
| `1 TB each day` | Lưu lượng lớn, cần giải pháp lưu trữ có chi phí thấp |
| `highly available` | Giải pháp phải có tính sẵn sàng cao, loại bỏ `single point of failure` |
| `minimize costs` | Ưu tiên dịch vụ `serverless`/`managed`, tránh provisioning thừa |
| `does not want to manage additional infrastructure` | Loại bỏ các đáp án có `EC2`, cần dịch vụ `fully managed` |
| `14 days available for immediate analysis` | Dữ liệu mới phải nằm ở tier có thể truy cập ngay (như `S3 Standard`) |
| `archive any data older than 14 days` | Cần chuyển dữ liệu cũ sang `storage class` giá rẻ (như `S3 Glacier`) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most operationally efficient
- **Constraints:** Không quản lý hạ tầng (`no EC2`, `self-managed`), `high availability`, `cost-optimized`, 14 ngày `hot data` + `cold archive`

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- `Amazon Kinesis Data Firehose` là dịch vụ `fully managed` để ingest dữ liệu streaming từ hàng nghìn thiết bị, tự động scale, `highly available`, không cần quản lý server.
- `Kinesis Data Firehose` có thể delivery trực tiếp vào `Amazon S3` bucket. `S3` cung cấp độ bền và sẵn sàng cao (`11 9's durability`, `99.99% availability`), đồng thời là nơi lưu trữ `cost-effective` để phân tích dữ liệu trong 14 ngày (có thể dùng `Amazon Athena`, `Amazon QuickSight`, hoặc các công cụ phân tích khác trực tiếp trên `S3`).
- `S3 Lifecycle configuration` cho phép tự động chuyển dữ liệu sang `Amazon S3 Glacier` sau 14 ngày để archive với chi phí cực thấp, đáp ứng yêu cầu lưu trữ dài hạn mà không cần thao tác thủ công.
- Tổng thể, đây là giải pháp `serverless`, `operationally efficient` nhất, đáp ứng đầy đủ các yêu cầu về ingestion, HA, cost, và archiving.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Sử dụng `Amazon EC2` instances đặt sau `Elastic Load Balancer` để ingest dữ liệu. Vi phạm trực tiếp yêu cầu "does not want to manage additional infrastructure" vì phải quản lý server (`patching`, `scaling`, HA cho `EC2`, script tự viết). Đây là `anti-pattern` cho ingestion quy mô lớn so với dịch vụ `managed` như `Kinesis`.
- *When this answer WOULD be correct:* Nếu đề bài yêu cầu xử lý logic phức tạp tùy chỉnh trong quá trình ingest và không có dịch vụ `managed` nào đáp ứng được.

**❌ Đáp án C:**
- `Amazon OpenSearch Service` (hay `Amazon Elasticsearch Service`) rất đắt đỏ để lưu 1 TB dữ liệu mỗi ngày và giữ 14 TB cho phân tích ngay lập tức
