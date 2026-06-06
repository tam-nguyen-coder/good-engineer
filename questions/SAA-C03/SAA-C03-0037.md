# Question #37 - Topic 1

A company recently launched a variety of new workloads on Amazon EC2 instances in its AWS account. The company needs to create a strategy to access and administer the instances remotely and securely. The company needs to implement a repeatable process that works with native AWS services and follows the AWS Well-Architected Framework. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Use the EC2 serial console to directly access the terminal interface of each instance for administration.

**B.** Attach the appropriate IAM role to each existing instance and new instance. Use AWS Systems Manager Session Manager to establish a remote SSH session.

**C.** Create an administrative SSH key pair. Load the public key into each EC2 instance. Deploy a bastion host in a public subnet to provide a tunnel for administration of each instance.

**D.** Establish an AWS Site-to-Site VPN connection. Instruct administrators to use their local on-premises machines to connect directly to the instances by using SSH keys across the VPN tunnel.



 ---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Một công ty vừa triển khai nhiều workload mới trên `Amazon EC2 instances` trong tài khoản AWS. Công ty cần một chiến lược để truy cập và quản trị các instance từ xa một cách bảo mật.
- **Existing Resources:** Các `EC2 instances` hiện có và các instance mới sẽ triển khai trong tương lai.
- **Current Issue/Goal:** Cần xây dựng quy trình có thể lặp lại (`repeatable process`), sử dụng dịch vụ `native AWS services`, tuân thủ `AWS Well-Architected Framework`, và đặc biệt phải có `LEAST operational overhead`.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| `LEAST operational overhead` | Ưu tiên giải pháp không yêu cầu quản lý hạ tầng, cấu hình thủ công, hoặc bảo trì liên tục |
| `AWS Well-Architected Framework` | Tuân thủ các trụ cột, đặc biệt là Security (giảm attack surface) và Operational Excellence (tự động hóa, giảm thao tác tay) |
| `native AWS services` | Sử dụng dịch vụ do AWS vận hành và quản lý, không tự xây dựng giải pháp thay thế |
| `AWS Systems Manager Session Manager` | Dịch vụ cho phép truy cập shell vào `EC2 instances` qua AWS Console/CLI mà không cần SSH key hay mở port 22 |
| `IAM role` | Cấp quyền bảo mật cho EC2 để giao tiếp với `Systems Manager` mà không cần hardcoded credentials |
| `Bastion host` | Jump server truyền thống, yêu cầu tự quản lý, vá lỗi, và bảo mật |
| `EC2 serial console` | Giao diện console nối tiếp để khắc phục sự cố khi mất kết nối network, không dùng cho quản trị thường xuyên |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Best practice / Least operational overhead
- **Constraints:** Truy cập từ xa (remote), bảo mật (secure), quy trình lặp lại được, sử dụng dịch vụ AWS native, tuân thủ Well-Architected, overhead thấp nhất

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**
**Giải thích:** `AWS Systems Manager Session Manager` là dịch vụ AWS native cho phép thiết lập phiên truy cập bảo mật vào `EC2 instances` mà không cần mở inbound port (như port 22), không cần quản lý SSH key pairs, và không cần duy trì `bastion host`. Bằng cách gắn `IAM role` (với policy `AmazonSSMManagedInstanceCore`) vào từng instance, administrator có thể khởi tạo phiên shell/SSH thông qua AWS Management Console hoặc AWS CLI. Giải pháp này hoàn toàn lặp lại được (có thể tích hợp vào `Launch Templates` hoặc `Auto Scaling`), giảm thiểu attack surface (đáp ứng Security Pillar của `AWS Well-Architected Framework`), và có operational overhead thấp nhất vì AWS quản lý toàn bộ hạ tầng truy cập.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:** `EC2 serial console` được thiết kế chủ yếu cho mục đích khắc phục sự cố (troubleshooting) trong các tình huống khẩn cấp khi instance không thể truy cập qua network (ví dụ: lỗi cấu hình network, SSH daemon không hoạt động). Nó không phù hợp để quản trị hàng ngày (day-to-day administration) và không hiệu quả khi cần quản lý nhiều instance đồng thời.

**❌ Đáp án C:** Việc triển khai `bastion host` trong public subnet đòi hỏi phải tự quản lý hạ tầng (cài đặt, vá lỗi, bảo mật, scale), quản lý SSH key pairs (tạo, phân phối, xoay vòng keys), và mở rộng attack surface. Điều này vi phạm yêu cầu `LEAST operational overhead` và không tận dụng được lợi thế của dịch vụ AWS native.

**❌ Đáp án D:** `AWS Site-to-Site VPN` tạo ra kết nối mạng giữa on-premises và AWS, nhưng vẫn yêu cầu quản lý SSH keys thủ công và dựa vào kết nối VPN liên tục. Operational overhead cao hơn đáng kể so với `Session Manager` do phải duy trì VPN tunnel, thiết bị customer gateway, và quản lý key trên từng instance.

## 6. MẸO GHI NHỚ
🧠 *Khi đề bài yêu cầu quản trị `EC2` an toàn, từ xa, với `LEAST operational overhead` và `native AWS service` → Nghĩ ngay đến `AWS Systems Manager Session Manager`. Nó loại bỏ hoàn toàn nhu cầu về `bastion host`, `SSH keys`, và mở inbound ports.*


