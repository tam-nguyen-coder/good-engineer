# Question #22 - Topic 1

A solutions architect is using Amazon S3 to design the storage architecture of a new digital media application. The media files must be resilient to the loss of an Availability Zone. Some files are accessed frequently while other files are rarely accessed in an unpredictable pattern. The solutions architect must minimize the costs of storing and retrieving the media files. Which storage option meets these requirements?

## Options

**A.** S3 Standard

**B.** S3 Intelligent-Tiering

**C.** S3 Standard-Infrequent Access (S3 Standard-IA)

**D.** S3 One Zone-Infrequent Access (S3 One Zone-IA)



 ## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Thiết kế kiến trúc lưu trữ cho ứng dụng digital media mới sử dụng `Amazon S3`.
- **Existing Resources:** Chưa có (thiết kế mới).
- **Current Issue/Goal:** 
  - File media phải chịu được mất một `Availability Zone` (độ bền cao).
  - Một số file truy cập thường xuyên, một số file khác truy cập hiếm với **pattern không thể đoán trước** (unpredictable).
  - Phải **tối thiểu hóa chi phí** lưu trữ và truy xuất.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| Resilient to the loss of an Availability Zone | Yêu cầu dữ liệu được lưu trữ xuyên suốt nhiều AZ (multi-AZ). Loại trừ các lớp lưu trữ single-AZ như `S3 One Zone-IA`. |
| Unpredictable pattern | Pattern truy cập không xác định trước → cần giải pháp tự động phân loại/chuyển tier thay vì chọn 1 tier cố định. |
| Minimize costs of storing and retrieving | Cần tối ưu cả chi phí lưu trữ lẫn chi phí truy xuất, không chỉ chọn tier rẻ nhất. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Best storage option / Cost optimization
- **Constraints:** 
  1. High availability/durability across multiple AZs.
  2. Mixed access patterns (frequent + infrequent, unpredictable).
  3. Lowest total cost (storage + retrieval).

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B. `S3 Intelligent-Tiering`**

**Giải thích:** 
- `S3 Intelligent-Tiering` lưu trữ dữ liệu trên nhiều `Availability Zone`, đáp ứng yêu cầu chịu được mất một AZ.
- Đây là lớp lưu trữ **duy nhất** tự động di chuyển object giữa `Frequent Access tier` và `Infrequent Access tier` dựa trên pattern truy cập **thực tế**, không cần dự đoán trước.
- Chi phí lưu trữ ban đầu tương đương `S3 Standard`, nhưng khi object không được truy cập trong 30 ngày, nó tự động chuyển xuống tier rẻ hơn. Khi được truy cập lại, tự động chuyển lên tier phù hợp.
- **Không mất phí truy xuất (retrieval fee)** khi object chuyển tier, giúp tối thiểu hóa tổng chi phí trong khi vẫn đảm bảo hiệu năng.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A. `S3 Standard`:** 
- Đáp ứng được yêu cầu multi-AZ, nhưng chi phí lưu trữ cao cho những file hiếm khi được truy cập. Không có khả năng tự động tối ưu chi phí theo pattern.

**❌ Đáp án C. `S3 Standard-IA`:** 
- Có độ bền multi-AZ, nhưng được thiết kế cho dữ liệu **ít được truy cập**. Nếu đặt file thường xuyên được truy cập vào đây, sẽ phát sinh **phí truy xuất (retrieval fee)** cao. Không phù hợp với pattern không thể đoán trước vì bạn không biết file nào sẽ hot hay cold.

**❌ Đáp án D. `S3 One Zone-IA`:** 
- Vi phạm yêu cầu đầu tiên: lưu trữ trong **một AZ duy nhất**. Nếu AZ đó bị mất, dữ liệu sẽ bị mất. Loại ngay lập tức.

## 6. MẸO GHI NHỚ
🧠 *"Unpredictable access pattern" trong đề thi AWS SAA gần như luôn trỏ đến `S3 Intelligent-Tiering`. Nếu đề nhắc "loss of an AZ" → loại ngay `One Zone-IA`. `Intelligent-Tiering` = set-and-forget để tối ưu chi phí khi bạn không biết pattern.*
