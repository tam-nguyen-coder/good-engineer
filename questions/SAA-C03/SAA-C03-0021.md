# Question #21 - Topic 1

An ecommerce company wants to launch a one-deal-a-day website on AWS. Each day will feature exactly one product on sale for a period of 24 hours. The company wants to be able to handle millions of requests each hour with millisecond latency during peak hours. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Use Amazon S3 to host the full website in different S3 buckets. Add Amazon CloudFront distributions. Set the S3 buckets as origins for the distributions. Store the order data in Amazon S3.

**B.** Deploy the full website on Amazon EC2 instances that run in Auto Scaling groups across multiple Availability Zones. Add an Application Load Balancer (ALB) to distribute the website traffic. Add another ALB for the backend APIs. Store the data in Amazon RDS for MySQL.

**C.** Migrate the full application to run in containers. Host the containers on Amazon Elastic Kubernetes Service (Amazon EKS). Use the Kubernetes Cluster Autoscaler to increase and decrease the number of pods to process bursts in traffic. Store the data in Amazon RDS for MySQL.

**D.** Use an Amazon S3 bucket to host the website's static content. Deploy an Amazon CloudFront distribution. Set the S3 bucket as the origin. Use Amazon API Gateway and AWS Lambda functions for the backend APIs. Store the data in Amazon DynamoDB.



## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty thương mại điện tử muốn triển khai website `one-deal-a-day` (mỗi ngày chỉ bán một sản phẩm trong 24 giờ) trên `AWS`.
- **Existing Resources:** Không có (triển khai từ đầu).
- **Current Issue/Goal:** Xử lý hàng triệu request mỗi giờ với độ trễ `millisecond` trong giờ cao điểm, đồng thời phải có `LEAST operational overhead` (chi phí vận hành thấp nhất).

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| `millions of requests each hour` | Cần kiến trúc có khả năng tự động scale ngang, ưu tiên serverless hoặc fully managed services |
| `millisecond latency` | Cần `CDN` (`CloudFront`) để cache và database có độ trễ thấp (`DynamoDB`) |
| `LEAST operational overhead` | Loại bỏ các giải pháp đòi hỏi quản lý server, container orchestration, hoặc patching OS |
| `one-deal-a-day` | Đặc thù read-heavy, có thể tận dụng cache tích cực; backend động chủ yếu là xử lý đơn hàng |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Best architecture / Least operational overhead
- **Constraints:** Hàng triệu request/giờ, độ trễ millisecond, giảm thiểu tối đa thao tác vận hành (không quản lý server, cluster, hoặc auto-scaling thủ công)

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**
**Giải thích:** 
- `Amazon S3` + `Amazon CloudFront`: Lưu trữ và phân phối nội dung tĩnh (static content) qua các edge locations toàn cầu, đảm bảo độ trễ thấp cho hàng triệu request. Đây là pattern chuẩn cho website tĩnh/có lưu lượng lớn.
- `Amazon API Gateway` + `AWS Lambda`: Backend dạng serverless, tự động scale từ zero lên hàng nghìn concurrent executions trong vài giây mà không cần cấu hình server, container, hay cluster. Operational overhead gần như bằng không.
- `Amazon DynamoDB`: Database NoSQL fully managed, cung cấp độ trễ single-digit millisecond ở mọi quy mô. Với chế độ `on-demand capacity`, nó tự động xử lý hàng triệu request/giờ mà không cần provision hay tune capacity thủ công.
- Tổng thể: Kiến trúc hoàn toàn serverless, loại bỏ hoàn toàn gánh nặng quản lý hạ tầng, phù hợp nhất với yêu cầu "least operational overhead".

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:** 
- `Amazon S3` chỉ phù hợp để host static website, không thể xử lý logic động của "full website" thương mại điện tử.
- Lưu trữ order data trong `Amazon S3` là không phù hợp vì `S3` là object storage, không hỗ trợ transactional consistency và độ trễ không đảm bảo millisecond cho các thao tác đọc/ghi nhanh.
- Dùng nhiều `S3 buckets` khác nhau tạo ra operational overhead không cần thiết và không giải quyết được yêu cầu backend động.

**❌ Đáp án B:** 
- `Amazon EC2` instances và `Amazon RDS for MySQL` đòi hỏi phải quản lý server: patching OS, bảo mật, cấu hình `Auto Scaling groups`, health checks, và tune database.
- `Application Load Balancer` (`ALB`) thêm một lớp quản lý nữa. Mặc dù có thể handle được traffic, operational overhead cao hơn rất nhiều so với serverless.
- Không đáp ứng yêu cầu "least operational overhead".

**❌ Đáp án C:** 
- `Amazon EKS` và `Kubernetes` dù là managed service nhưng vẫn có operational overhead rất lớn: quản lý pods, nodes, `Cluster Autoscaler`, networking, service mesh, và manifest files.
- So với `AWS Lambda` + `Amazon API Gateway`, `EKS` phức tạp hơn nhiều về vận hành và không phải là lựa chọn "least operational overhead".

## 6. MẸO GHI NHỚ
🧠 *Khi đề bài yêu cầu "least operational overhead" kèm "millions of requests" và "millisecond latency" → Nghĩ ngay đến kiến trúc **SERVERLESS**: `Amazon S3` + `Amazon CloudFront` cho static content, `Amazon API Gateway` + `AWS Lambda` cho backend, và `Amazon DynamoDB` cho database. Tránh `EC2`, `EKS`, và `RDS` nếu đề nhấn mạnh giảm thiểu vận hành tối đa.*


---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty thương mại điện tử muốn xây dựng website "one-deal-a-day" trên AWS. Mỗi ngày chỉ có đúng một sản phẩm được bán trong 24 giờ.
- **Existing Resources:** Không có tài nguyên hiện có; công ty đang thiết kế kiến trúc mới hoàn toàn trên AWS.
- **Current Issue/Goal:** Cần xử lý hàng triệu request mỗi giờ với độ trễ millisecond trong giờ cao điểm, đồng thời phải có **LEAST operational overhead** (chi phí vận hành thấp nhất).

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| one-deal-a-day | Nội dung chủ yếu là tĩnh (1 sản phẩm), rất phù hợp để cache trên CDN |
| millions of requests each hour | Yêu cầu khả năng scale gần như vô hạn, cần kiến trúc auto-scaling |
| millisecond latency | Cần `CloudFront` cho static content và database hiệu năng cao (ví dụ `DynamoDB`) |
| least operational overhead | Gợi ý kiến trúc serverless, tránh `EC2`, `EKS`, hoặc self-managed servers |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective / Least operational overhead + High performance + Scalability
- **Constraints:** Website thương mại điện tử (cần xử lý đơn hàng động), peak traffic tập trung, yêu cầu độ trễ millisecond

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- Đây là kiến trúc **serverless** hoàn toàn, đáp ứng yêu cầu **least operational overhead**:
  - **Static content:** `Amazon S3` lưu trữ frontend tĩnh + `Amazon CloudFront` phân phối qua các edge locations toàn cầu, đảm bảo millisecond latency cho hàng triệu request.
  - **Dynamic backend:** `Amazon API Gateway` + `AWS Lambda` xử lý API đặt hàng mà không cần quản lý server, auto-scale tự động theo lưu lượng.
  - **Database:** `Amazon DynamoDB` là NoSQL database serverless, được thiết kế cho single-digit millisecond latency ở quy mô hàng triệu request/giờ, không cần provision hay quản lý server.
- Không có server nào cần patch, scale thủ công, hay quản lý hệ điều hành.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- **Why wrong:** Lưu trữ order data trong `Amazon S3` là không phù hợp cho dữ liệu giao dịch thương mại điện tử. `S3` là object storage, không phải database, không đảm bảo các tính chất ACID cần thiết cho đơn hàng. Ngoài ra, host "full website" trên `S3` nghĩa là chỉ có static website, không có backend động để xử lý API đặt hàng.
- **When correct:** Nếu chỉ cần lưu trữ và phân phối nội dung tĩnh (như hình ảnh, video) hoặc dữ liệu log/archive, không cần xử lý giao dịch.

**❌ Đáp án B:**
- **Why wrong:** Sử dụng `Amazon EC2` instances trong `Auto Scaling groups` và `Amazon RDS for MySQL` đòi hỏi operational overhead cao: phải quản lý OS patching, cấu hình `Auto Scaling`, maintain database instances, và quản lý hai `ALB`. Điều này vi phạm yêu cầu **least operational overhead**.
- **When correct:** Khi ứng dụng cần kiểm soát môi trường runtime chặt chẽ, sử dụng phần mềm không tương thích với serverless, hoặc yêu cầu relational database với complex joins và operational overhead không phải là ưu tiên hàng đầu.

**❌ Đáp án C:**
- **Why wrong:** `Amazon EKS` và `Kubernetes` có **operational overhead cao nhất** trong các đáp án. Việc quản lý `Kubernetes Cluster Autoscaler`, node groups, pod lifecycle, và control plane đòi hỏi chuyên môn sâu và công sức vận hành lớn. Đây là ngược hoàn toàn với yêu cầu "least operational overhead".
- **When correct:** Khi ứng dụng là microservices phức tạp, cần orchestration container linh hoạt, portable giữa các cloud, hoặc cần advanced service mesh, và câu hỏi không yêu cầu giảm thiểu operational overhead.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Cần least ops + millions of requests + millisecond latency → nghĩ ngay đến Serverless: `S3`+`CloudFront` cho static, `API Gateway`+`Lambda`+`DynamoDB` cho dynamic."*
