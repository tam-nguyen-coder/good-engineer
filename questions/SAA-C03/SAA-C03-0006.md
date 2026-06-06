# Question #6 - Topic 1

A company uses NFS to store large video files in on-premises network attached storage. Each video file ranges in size from 1 MB to 500 GB. The total storage is 70 TB and is no longer growing. The company decides to migrate the video files to Amazon S3. The company must migrate the video files as soon as possible while using the least possible network bandwidth. Which solution will meet these requirements?

## Options

**A.** Create an S3 bucket. Create an IAM role that has permissions to write to the S3 bucket. Use the AWS CLI to copy all files locally to the S3 bucket.

**B.** Create an AWS Snowball Edge job. Receive a Snowball Edge device on premises. Use the Snowball Edge client to transfer data to the device. Return the device so that AWS can import the data into Amazon S3.

**C.** Deploy an S3 File Gateway on premises. Create a public service endpoint to connect to the S3 File Gateway. Create an S3 bucket. Create a new NFS file share on the S3 File Gateway. Point the new file share to the S3 bucket. Transfer the data from the existing NFS file share to the S3 File Gateway.

**D.** Set up an AWS Direct Connect connection between the on-premises network and AWS. Deploy an S3 File Gateway on premises. Create a public virtual interface (VIF) to connect to the S3 File Gateway. Create an S3 bucket. Create a new NFS file share on the S3 File Gateway. Point the new file share to the S3 bucket. Transfer the data from the existing NFS file share to the S3 File Gateway.



 ---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty đang lưu trữ file video lớn (kích thước từ 1 MB đến 500 GB) trên hệ thống `NFS` on-premises với tổng dung lượng 70 TB. Dữ liệu đã ngừng tăng trưởng. Công ty cần di chuyển toàn bộ dữ liệu này lên `Amazon S3`.
- **Existing Resources:** Hệ thống lưu trữ `NFS` on-premises, 70 TB file video
- **Current Issue/Goal:** Phải di chuyển dữ liệu càng nhanh càng tốt, đồng thời sử dụng ít băng thông mạng nhất có thể.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| 70 TB | Dung lượng rất lớn, thuộc phạm vi `offline data transfer` thay vì truyền qua mạng |
| As soon as possible | Ưu tiên giải pháp vận chuyển vật lý thay vì truyền qua mạng băng thông hạn chế |
| Least possible network bandwidth | Cần loại bỏ hoàn toàn hoặc cực kỳ giảm thiểu việc sử dụng băng thông cho dữ liệu thực tế |
| NFS | Giao thức lưu trữ file hiện tại, cần tương thích trong quá trình di chuyển |
| No longer growing | Dữ liệu tĩnh, phù hợp cho one-time migration thay vì hybrid access liên tục |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Best performance + Least network bandwidth (kết hợp tốc độ và tối ưu băng thông)
- **Constraints:** 70 TB dữ liệu, file lớn nhất 500 GB, nguồn `NFS` on-premises, đích đến là `Amazon S3`

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- `AWS Snowball Edge` là dịch vụ được thiết kế riêng cho việc di chuyển dữ liệu khối lượng lớn (từ hàng chục TB đến PB) từ on-premises lên `AWS` mà không cần sử dụng băng thông mạng cho việc truyền dữ liệu thực tế.
- Với 70 TB dữ liệu, thiết bị `Snowball Edge Storage Optimized` (có dung lượng khả dụng ~80 TB) có thể chứa toàn bộ dữ liệu trong một thiết bị duy nhất.
- Công ty chỉ cần sao chép dữ liệu từ `NFS` sang thiết bị `Snowball Edge` tại chỗ (qua mạng LAN nội bộ), sau đó gửi trả thiết bị về `AWS`. `AWS` sẽ nhập dữ liệu vào `Amazon S3`.
- Phương pháp này đáp ứng đồng thời cả hai yêu cầu: nhanh nhất (vận chuyển vật lý nhanh hơn hàng tuần so với upload qua internet) và tiết kiệm băng thông mạng nhất (chỉ sử dụng băng thông tối thiểu cho việc quản lý job).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Sử dụng `AWS CLI` để copy trực tiếp từ local lên `S3 bucket` qua mạng internet.
- Với 70 TB, việc này sẽ tiêu tốn rất nhiều băng thông mạng và mất thời gian rất lâu (có thể hàng tuần hoặc hàng tháng), vi phạm cả hai yêu cầu "nhanh nhất" và "ít băng thông nhất".
- *Khi nào đúng:* Chỉ phù hợp với lượng dữ liệu nhỏ (vài GB) hoặc khi có kết nối mạng rất mạnh và không giới hạn băng thông.

**❌ Đáp án C:**
- Triển khai `S3 File Gateway` với `public service endpoint` vẫn yêu cầu truyền toàn bộ 70 TB dữ liệu qua internet/public network để đồng


## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty sử dụng `NFS` để lưu trữ các file video lớn trong hệ thống `on-premises network attached storage`. Kích thước mỗi file video từ 1 MB đến 500 GB. Tổng dung lượng lưu trữ là 70 TB và không còn tăng trưởng.
- **Existing Resources:** `on-premises NFS` storage chứa 70 TB dữ liệu tĩnh.
- **Current Issue/Goal:** Di chuyển toàn bộ video sang `Amazon S3` với hai ràng buộc chính: (1) thực hiện càng nhanh càng tốt (`as soon as possible`), và (2) sử dụng ít băng thông mạng nhất có thể (`least possible network bandwidth`).

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| `70 TB` | Dung lượng rất lớn, nằm trong phạm vi lý tưởng cho `AWS Snowball Edge` |
| `No longer growing` | Dữ liệu tĩnh, phù hợp cho one-time migration thay vì hybrid access liên tục |
| `As soon as possible` | Ưu tiên tốc độ hoàn thành; upload qua mạng thông thường sẽ quá chậm |
| `Least possible network bandwidth` | Yêu cầu tối thiểu hóa việc truyền dữ liệu qua mạng → ưu tiên offline data transfer |
| `500 GB` / `Video files` | File lớn, cần giải pháp hỗ trợ object size lớn khi import vào `S3` |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Data Migration / Storage
- **Constraints:** 
  - Dung lượng: 70 TB
  - Thời gian: Tối đa hóa tốc độ
  - Băng thông: Tối thiểu hóa (lý tưởng là không dùng network cho data plane)

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**
**Giải thích:** 
- `AWS Snowball Edge` là dịch vụ được thiết kế riêng cho việc di chuyển dữ liệu quy mô lớn (TB đến PB) vào `AWS` khi không có đủ băng thông mạng hoặc cần hoàn thành nhanh chóng.
- `Snowball Edge Storage Optimized` có dung lượng khả dụng ~80 TB, đủ để chứa toàn bộ 70 TB dữ liệu trong một thiết bị (hoặc có thể dùng nhiều thiết bị nếu cần).
- Dữ liệu được sao chép trực tiếp vào thiết bị `Snowball Edge` tại chỗ (`on-premises`) qua mạng nội bộ (tốc độ cao, không tiêu tốn băng thông internet/WAN), sau đó thiết bị được vận chuyển vật lý trả lại `AWS` để import vào `Amazon S3`.
- Phương pháp này sử dụng băng thông mạng gần như bằng không cho việc truyền dữ liệu thực tế (chỉ dùng rất ít cho việc quản lý job và mã hóa), hoàn toàn đáp ứng yêu cầu `least possible network bandwidth`.
- Thời gian tổng thể (đặt hàng thiết bị, copy nội bộ, vận chuyển, import) thường nhanh hơn rất nhiều so với upload 70 TB qua internet hoặc ngay cả qua `Direct Connect` đối với đa số doanh nghiệp.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:** Sử dụng `AWS CLI` để copy trực tiếp lên `S3`.
- Việc upload 70 TB qua mạng (dù là internet hay `Direct Connect`) sẽ tiêu tốn cực kỳ nhiều băng thông và thời gian (có thể kéo dài hàng tuần đến hàng tháng tùy băng thông hiện có).
- Hoàn toàn vi phạm yêu cầu `least possible network bandwidth` và `as soon as possible`.

**❌ Đáp án C:** Triển khai `S3 File Gateway` với `public service endpoint`.
- `S3 File Gateway` được thiết kế chủ yếu cho kịch bản hybrid cloud (truy cập liên tục, cache dữ liệu `on-premises` với backend trên `S3`), không phải là công cụ di chuyển dữ liệu một lần (one-time migration) tối ưu.
- Dữ liệu vẫn phải tr
