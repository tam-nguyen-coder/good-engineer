# Question #43 - Topic 1

A company has an on-premises application that generates a large amount of time-sensitive data that is backed up to Amazon S3. The application has grown and there are user complaints about internet bandwidth limitations. A solutions architect needs to design a long-term solution that allows for both timely backups to Amazon S3 and with minimal impact on internet connectivity for internal users. Which solution meets these requirements?

## Options

**A.** Establish AWS VPN connections and proxy all traffic through a VPC gateway endpoint.

**B.** Establish a new AWS Direct Connect connection and direct backup traffic through this new connection.

**C.** Order daily AWS Snowball devices. Load the data onto the Snowball devices and return the devices to AWS each day.

**D.** Submit a support ticket through the AWS Management Console. Request the removal of S3 service limits from the account.



 ## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Một công ty sở hữu ứng dụng `on-premises` tạo ra lượng lớn dữ liệu nhạy cảp về thời gian (`time-sensitive data`) và cần được sao lưu lên `Amazon S3`.
- **Existing Resources:** Hệ thống hiện tại đang dùng kết nối internet công cộng để backup dữ liệu lên `Amazon S3`.
- **Current Issue/Goal:** Ứng dụng đã phát triển, dẫn đến người dùng nội bộ phàn nàn về băng thông internet bị hạn chế. Cần một giải pháp **lâu dài** cho phép:
  - Backup kịp thời lên `Amazon S3`.
  - Tác động tối thiểu đến kết nối internet của người dùng nội bộ.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| `time-sensitive data` | Dữ liệu cần được xử lý/chuyển giao nhanh, không thể chờ đợi lâu. |
| `internet bandwidth limitations` | Băng thông internet hiện có không đủ cho cả backup và hoạt động nội bộ. |
| `long-term solution` | Giải pháp cần bền vững, không phải giải pháp tạm thời hoặc một lần. |
| `minimal impact on internet connectivity` | Cần tách biệt hoàn toàn hoặc giảm thiểu traffic backup khỏi đường truyền internet hiện tại. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Thiết kế kiến trúc mạng/kết nối (Network Connectivity Architecture).
- **Constraints:** 
  - Giải pháp phải lâu dài.
  - Không được ảnh hưởng đến băng thông internet của người dùng nội bộ.
  - Phải đảm bảo tính kịp thời (`timely`) cho dữ liệu nhạy cảm về thời gian.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**
**Giải thích:** Thiết lập một kết nối `AWS Direct Connect` mới và định tuyến toàn bộ traffic backup qua kết nối này là giải pháp lý tưởng. `Direct Connect` cung cấp một đường kết nối chuyên dụng (dedicated network connection) từ trung tâm dữ liệu `on-premises` đến AWS, hoàn toàn không đi qua internet công cộng. Điều này giúp:
- Giải phóng hoàn toàn băng thông internet hiện tại cho người dùng nội bộ.
- Đảm bảo băng thông ổn định, độ trễ thấp và nhất quán cho việc backup dữ liệu lớn, thường xuyên lên `Amazon S3`.
- Là giải pháp **lâu dài**, phù hợp cho workload backup định kỳ và liên tục.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:** `AWS VPN` vẫn sử dụng internet công cộng làm underlay (đi qua encrypted tunnel trên internet), do đó không giải quyết được vấn đề băng thông internet bị chiếm dụng. Hơn nữa, `VPC gateway endpoint` chỉ cho phép các instance trong `VPC` kết nối đến `S3` mà không qua internet; nó **không thể** được sử dụng từ môi trường `on-premises`.

**❌ Đáp án C:** `AWS Snowball` phù hợp cho việc di chuyển dữ liệu khối lượng lớn một lần (one-time migration) hoặc không thường xuyên, nhưng không phải là giải pháp lâu dài cho backup hàng ngày. Việc đặt hàng thiết bị, vận chuyển và xử lý hàng ngày sẽ gây ra độ trễ lớn, không đáp ứng được yêu cầu `time-sensitive`.

**❌ Đáp án D:** `Amazon S3` không có "service limits" về băng thông cần phải xóa. Việc gửi support ticket để yêu cầu xóa giới hạn là không hợp lý và hoàn toàn không giải quyết được nút thắt cổ chai ở đường truyền internet của công ty.

## 6. MẸO GHI NHỚ
🧠 *Khi đề bài nhắc đến việc backup dữ liệu lớn, thường xuyên (`long-term`, `timely`) từ `on-premises` lên AWS và muốn tránh ảnh hưởng đến internet — hãy nghĩ ngay đến `AWS Direct Connect`. `Snowball` chỉ dùng cho bulk transfer không thường xuyên, còn `VPN` vẫn ăn băng thông internet.*
