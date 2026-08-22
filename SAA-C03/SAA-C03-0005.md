# Question #5 - Topic 1

A company is hosting a web application on AWS using a single Amazon EC2 instance that stores user-uploaded documents in an Amazon EBS volume. For better scalability and availability, the company duplicated the architecture and created a second EC2 instance and EBS volume in another Availability Zone, placing both behind an Application Load Balancer. After completing this change, users reported that, each time they refreshed the website, they could see one subset of their documents or the other, but never all of the documents at the same time. What should a solutions architect propose to ensure users see all of their documents at once?

## Options

**A.** Copy the data so both EBS volumes contain all the documents

**B.** Configure the Application Load Balancer to direct a user to the server with the documents

**C.** Copy the data from both EBS volumes to Amazon EFS. Modify the application to save new documents to Amazon EFS

**D.** Configure the Application Load Balancer to send the request to both servers. Return each document from the correct server



---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Một công ty đang chạy web application trên AWS. Ban đầu, hệ thống chỉ có một `Amazon EC2` instance duy nhất và lưu trữ các tài liệu do người dùng tải lên trên một `Amazon EBS` volume.
- **Existing Resources:** Để cải thiện khả năng mở rộng (`scalability`) và tính sẵn sàng (`availability`), công ty đã nhân đôi kiến trúc: tạo thêm một `EC2` instance thứ hai và một `EBS` volume thứ hai tại một `Availability Zone` khác, sau đó đặt cả hai instance này phía sau một `Application Load Balancer`.
- **Current Issue/Goal:** Người dùng báo cáo rằng mỗi khi refresh website, họ chỉ thấy một tập hợp con (subset) tài liệu này hoặc tập hợp con tài liệu khác, nhưng không bao giờ thấy toàn bộ tài liệu cùng lúc. Yêu cầu đề xuất giải pháp để người dùng luôn nhìn thấy tất cả tài liệu của họ.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| `Amazon EBS` | Block storage gắn chặt với một `EC2` instance trong một `AZ`, không thể mount đồng thời trên nhiều instance ở các `AZ` khác nhau để chia sẻ dữ liệu. |
| `Amazon EFS` | Managed NFS service hoạt động ở mức regional, cho phép hàng trăm `EC2` instances ở nhiều `AZ` khác nhau mount cùng một file system. |
| `Application Load Balancer` | Phân phối incoming requests đến các target trong target group, mỗi request chỉ được gửi đến **một** target duy nhất. |
| `Availability Zone` | Vùng khả dụng độc lập trong một Region; `EBS` bị giới hạn ở một `AZ` cụ thể. |
| Session stickiness | Cơ chế gắn user vào một instance cụ thể, nhưng không giải quyết vấn đề dữ liệu bị phân tán giữa nhiều server. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Troubleshooting / Architecture Optimization
- **Constraints:** 
  - Phải đảm bảo dữ liệu tài liệu (documents) nhất quán, đầy đủ trên cả hai server.
  - Giải pháp phải bền vững cho cả dữ liệu hiện tại và dữ liệu mới được upload sau này.
  - Hoạt động cross-`AZ` với `ALB`.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**
**Giải thích:** Vấn đề cốt lõi là `Amazon EBS` là block storage "gắn liền" với từng `EC2` instance và không chia sẻ được giữa nhiều instance ở các `Availability Zone` khác nhau. Khi người dùng upload tài liệu, `ALB` điều hướng request đến một trong hai instance, nên tài liệu chỉ được lưu vào `EBS` volume của instance đó → dữ liệu bị phân mảnh giữa hai ổ đĩa. 

Đáp án **C** giải quyết triệt để bằng cách:
1. **Migrate dữ liệu hiện có** từ cả hai `EBS` volumes lên `Amazon EFS` (tạo một bộ dữ liệu thống nhất, hợp nhất).
2. **Thay đổi application** để lưu tài liệu mới trực tiếp lên `Amazon EFS`.

`Amazon EFS` là shared file system, cho phép cả hai `EC2` instances (ở các `AZ` khác nhau) mount và đọc/ghi cùng một nguồn dữ liệu. Từ đó, bất kể `ALB` điều hướng người dùng đến instance nào, họ đều thấy toàn bộ tài liệu.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:** *Copy the data so both EBS volumes contain all the documents.*
Chỉ là giải pháp một lần (one-time fix). Khi người dùng upload tài liệu mới, `ALB` sẽ gửi đến một trong hai instance, nên lại chỉ có một `EBS` được cập nhật, dẫn đến data divergence. `EBS` không hỗ trợ chia sẻ đồng thời giữa nhiều instance cross-`AZ`, do đó cần một cơ chế đồng bộ phức tạp và không quản lý được. Không phải là kiến trúc bền vững.

**❌ Đáp án B:** *Configure the Application Load Balancer to direct a user to the server with the documents.*
`ALB` không có khả năng routing dựa trên "server nào đang chứa file nào". Ngay cả khi bật `sticky sessions` (session affinity), user chỉ bị gắn vào một instance cụ thể; nếu họ upload tài liệu trên instance A thì chỉ thấy tài liệu trên A, và hoàn toàn không thấy tài liệu của những người dùng khác đã upload lên instance B. Điều này vi phạm yêu cầu "thấy tất cả tài liệu".

**❌ Đáp án D:** *Configure the Application Load Balancer to send the request to both servers. Return each document from the correct server.*
`Application Load Balancer` (và load balancer layer 7 nói chung) không hoạt động theo cơ chế fan-out hay multicast. Theo thiết kế, mỗi incoming request chỉ được gửi đến **một** healthy target duy nhất trong target group và chờ response từ target đó. `ALB` không thể gửi request đến cả hai server đồng thời rồ
