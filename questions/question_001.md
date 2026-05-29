# Question #1 - Topic 1

A company collects data for temperature, humidity, and atmospheric pressure in cities across multiple continents. The average volume of data that the company collects from each site daily is 500 GB. Each site has a high-speed Internet connection. The company wants to aggregate the data from all these global sites as quickly as possible in a single Amazon S3 bucket. The solution must minimize operational complexity. Which solution meets these requirements?

## Options

**A.** Turn on S3 Transfer Acceleration on the destination S3 bucket. Use multipart uploads to directly upload site data to the destination S3 bucket.

**B.** Upload the data from each site to an S3 bucket in the closest Region. Use S3 Cross-Region Replication to copy objects to the destination S3 bucket. Then remove the data from the origin S3 bucket.

**C.** Schedule AWS Snowball Edge Storage Optimized device jobs daily to transfer data from each site to the closest Region. Use S3 Cross- Region Replication to copy objects to the destination S3 bucket.

**D.** Upload the data from each site to an Amazon EC2 instance in the closest Region. Store the data in an Amazon Elastic Block Store (Amazon EBS) volume. At regular intervals, take an EBS snapshot and copy it to the Region that contains the destination S3 bucket. Restore the EBS volume in that Region.



---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Một công ty thu thập dữ liệu cảm biến (nhiệt độ, độ ẩm, áp suất khí quyển) từ nhiều thành phố trên nhiều lục địa. Mỗi site gửi khoảng 500 GB dữ liệu mỗi ngày.
- **Existing Resources:** Các site đều có `high-speed Internet connection`. Cần tập hợp dữ liệu vào một `Amazon S3 bucket` duy nhất.
- **Current Issue/Goal:** Tổng hợp dữ liệu toàn cầu một cách nhanh nhất có thể, đồng thời giảm thiểu độ phức tạp vận hành xuống mức tối thiểu.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `500 GB daily per site` + `high-speed Internet` | Dung lượng lớn nhưng đường truyền tốt, không cần thiết bị vật lý |
| `single Amazon S3 bucket` | Mục tiêu là tập trung dữ liệu, tránh nhiều thành phần trung gian |
| `minimize operational complexity` | Ưu tiên giải pháp đơn giản, ít thành phần cần quản lý nhất |
| `S3 Transfer Acceleration` | Tăng tốc upload từ xa bằng cách đi qua `AWS edge network` thay vì internet công cộng |
| `multipart uploads` | Chia object lớn thành nhiều phần upload song song, bắt buộc với object cỡ lớn |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most operationally efficient / Fastest aggregation / Minimize operational overhead
- **Constraints:** Dữ liệu 500 GB/site/ngày, nhiều lục địa, đường truyền internet tốc độ cao, bucket đích duy nhất

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Đáp án này kích hoạt `S3 Transfer Acceleration` trên bucket đích, cho phép dữ liệu từ các site trên toàn cầu được đẩy lên nhanh hơn thông qua các điểm `edge location` của AWS, tối ưu đường truyền xuyên lục địa về `S3 bucket` tập trung.
- Dung lượng 500 GB mỗi site yêu cầu sử dụng `multipart uploads` để chia nhỏ object, tăng tốc độ truyền và độ tin cậy khi upload object lớn.
- Vì các site đã có `high-speed Internet connection`, việc upload trực tiếp hoàn toàn khả thi mà không cần thiết bị vật lý hay máy chủ trung gian.
- Phương án này chỉ cần duy nhất một `S3 bucket` đích, loại bỏ hoàn toàn việc quản lý bucket nguồn, `cross-region replication`, `lifecycle policy` hay các thành phần compute, từ đó đạt được yêu cầu giảm thiểu vận hành xuống thấp nhất.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Phương án này tạo thêm `S3 bucket` ở mỗi `Region` gần site nhất, sau đó dùng `S3 Cross-Region Replication` để sao chép sang bucket đích. Việc này làm tăng độ phức tạp vận hành do phải quản lý nhiều bucket, cấu hình `replication rule`, chờ đồng bộ không đồng thời, và phải xóa dữ liệu ở bucket nguồn sau khi replicate.
- Đáp án này chỉ đúng khi đề yêu cầu tuân thủ `data residency` tạm thời ở region cục bộ trước khi tập hợp, hoặc khi đường truyền trực tiếp đến bucket đích quá chậm.

**❌ Đáp án C:**
- `AWS Snowball Edge Storage Optimized` được thiết kế cho trường hợp không có đường truyền internet đủ nhanh hoặc dữ liệu ở quy mô petabyte. Với 500 GB mỗi ngày và `high-speed Internet`, việc đặt lịch thiết bị Snowball hàng ngày tạo ra gánh nặng vận hành cực lớn (đặt hàng, vận chuyển, sao chép dữ liệu vật lý, trả lại thiết bị).
- Đáp án này đúng khi site nằm ở vùng không có internet băng thông cao hoặc dữ liệu cần chuyển lên đến hàng chục TB/PB.

**❌ Đáp án D:**
- Phương án này đưa dữ liệu vào `Amazon EC2` và `Amazon EBS`, sau đó dùng `EBS snapshot` và copy snapshot qua region khác. Đây là cách tiếp cận gián tiếp, không tối ưu cho việc tập hợp dữ liệu vào `S3`.
- Tạo ra nhiều thành phần cần quản lý (máy chủ `EC2`, ổ đĩa `EBS`, snapshot), chi phí cao, và dữ liệu cuối cùng không được đưa vào `S3` một cách trực tiếp hay hiệu quả.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *Internet nhanh + file lớn + xa xôi = `S3TA` + `Multipart`. Tránh `CRR`, `Snowball`, hay `EC2` khi đề yêu cầu giảm thiểu vận hành.*
