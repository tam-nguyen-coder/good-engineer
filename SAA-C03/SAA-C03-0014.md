# Question #14 - Topic 1

A company runs an ecommerce application on Amazon EC2 instances behind an Application Load Balancer. The instances run in an Amazon EC2 Auto Scaling group across multiple Availability Zones. The Auto Scaling group scales based on CPU utilization metrics. The ecommerce application stores the transaction data in a MySQL 8.0 database that is hosted on a large EC2 instance. The database's performance degrades quickly as application load increases. The application handles more read requests than write transactions. The company wants a solution that will automatically scale the database to meet the demand of unpredictable read workloads while maintaining high availability. Which solution will meet these requirements?

## Options

**A.** Use Amazon Redshift with a single node for leader and compute functionality.

**B.** Use Amazon RDS with a Single-AZ deployment Configure Amazon RDS to add reader instances in a different Availability Zone.

**C.** Use Amazon Aurora with a Multi-AZ deployment. Configure Aurora Auto Scaling with Aurora Replicas.

**D.** Use Amazon ElastiCache for Memcached with EC2 Spot Instances.



---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty vận hành ứng dụng `ecommerce` trên `Amazon EC2` instances phía sau `Application Load Balancer`. Các instances chạy trong `Amazon EC2 Auto Scaling group` trải rộng nhiều `Availability Zones`, scale dựa trên `CPU utilization`. Ứng dụng lưu `transaction data` trong `MySQL 8.0` database được host trên một large `EC2` instance duy nhất.
- **Existing Resources:** `EC2` instances, `ALB`, `EC2 Auto Scaling group`, `MySQL 8.0` trên single `EC2` instance (self-managed).
- **Current Issue/Goal:** Database performance suy giảm nhanh khi tải tăng. Ứng dụng có nhiều `read requests` hơn `write transactions`. Cần giải pháp tự động scale database để đáp ứng `unpredictable read workloads` đồng thời duy trì `high availability`.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| `MySQL 8.0` | Engine database hiện tại, yêu cầu giải pháp tương thích hoặc dễ migrate |
| Unpredictable read workloads | Cần khả năng scale out/in read capacity một cách tự động, linh hoạt |
| High availability | Yêu cầu HA, loại trừ các kiến trúc `Single-AZ` hoặc single point of failure |
| More read than write | Pattern đọc nhiều hơn ghi -> lý tưởng cho kiến trúc `read replica` |
| Transaction data | Dữ liệu giao dịch OLTP, cần persistent storage, không thể chỉ dùng cache |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Solution architecture - Chọn dịch vụ database phù hợp
- **Constraints:** 
  - Tự động scale cho read workload
  - `High availability`
  - Tương thích với `MySQL`
  - OLTP (transaction processing), không phải analytics
  - Không self-managed

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**
**Giải thích:** `Amazon Aurora` là engine database tương thích `MySQL`, được thiết kế riêng cho cloud và OLTP. `Multi-AZ deployment` đảm bảo `high availability` bằng cách phân phối dữ liệu và compute across nhiều `Availability Zones` (Aurora tự động replicate 6 bản sao dữ liệu across 3 AZ). `Aurora Replicas` có thể phục vụ read traffic (hỗ trợ tới 15 replicas), và `Aurora Auto Scaling` cho phép tự động thêm hoặc loại bỏ `Aurora Replicas` dựa trên metric của read load. Điều này đáp ứng chính xác yêu cầu xử lý `unpredictable read workloads` mà vẫn đảm bảo HA, đồng thời giải quyết vấn đề performance degrade của database cũ.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:** `Amazon Redshift` là data warehouse dùng cho analytics và OLAP, không phù hợp cho ứng dụng `ecommerce` xử lý giao dịch trực tuyến (OLTP). Single node cũng không đáp ứng được yêu cầu `high availability`.
**❌ Đáp án B:** `Single-AZ deployment` vi phạm trực tiếp yêu cầu `high availability`. Nếu `Availability Zone` chứa primary instance gặp sự cố, toàn bộ database sẽ unavailable. Mặc dù có thể thêm reader instances, nhưng việc thiếu HA ở primary và khả năng auto scale không tối ưu bằng `Aurora Auto Scaling` khiến option này không đáp ứng đủ requirement.
**❌ Đáp án D:** `Amazon ElastiCache` for `Memcached` chỉ là caching layer, không thể thay thế persistent database để lưu `transaction data`. `EC2 Spot Instances` có thể bị gián đoạn bất cứ lúc nào, không phù hợp cho yêu cầu ổn định và `high availability` của database layer.

## 6. MẸO GHI NHỚ
🧠 *Công thức: `MySQL` + `auto scale read` + `high availability` + `unpredictable workload` = `Amazon Aurora` + `Aurora Auto Scaling` + `Aurora Replicas`.*
🧠 *`Single-AZ` = Không HA. `Redshift` = Analytics/Data Warehouse (OLAP). `ElastiCache` = Cache layer, không phải Database thay thế.*
🧠 *`Aurora` hỗ trợ tới 15 `read replicas` và tự động scale storage, trong khi `RDS MySQL` thông thường chỉ hỗ trợ tối đa 5 `read replicas` và scale storage thủ công (trừ `Storage Auto Scaling` nhưng vẫn khác biệt với Aurora architecture).*


