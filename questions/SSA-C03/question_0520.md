# Question #520 - Topic 1

A company is designing a new web application that will run on Amazon EC2 Instances. The application will use Amazon DynamoDB for backend data storage. The application traffic will be unpredictable. The company expects that the application read and write throughput to the database will be moderate to high. The company needs to scale in response to application traffic. Which DynamoDB table configuration will meet these requirements MOST cost-effectively?

## Options

**A.** Configure DynamoDB with provisioned read and write by using the DynamoDB Standard table class. Set DynamoDB auto scaling to a maximum defined capacity.

**B.** Configure DynamoDB in on-demand mode by using the DynamoDB Standard table class.

**C.** Configure DynamoDB with provisioned read and write by using the DynamoDB Standard Infrequent Access (DynamoDB Standard-IA) table class. Set DynamoDB auto scaling to a maximum defined capacity.

**D.** Configure DynamoDB in on-demand mode by using the DynamoDB Standard Infrequent Access (DynamoDB Standard-IA) table class.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Web app trên EC2 + DynamoDB backend. Traffic unpredictable, throughput moderate to high. Need cost-effective scaling.
- **Existing Resources:** EC2 instances, DynamoDB.
- **Current Issue/Goal:** Chọn DynamoDB capacity mode + table class cost-effective nhất.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `unpredictable traffic` | On-demand mode phù hợp vì không cần dự đoán capacity. |
| `moderate to high` | Throughput cao → Standard table class (không phải Standard-IA có chi phí request cao). |
| `scale in response to traffic` | Tự động scale theo traffic. |
| `Most cost-effectively` | Cân bằng giữa cost và scaling. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective
- **Constraints:** Unpredictable traffic, moderate to high throughput

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- On-demand mode: DynamoDB tự động scale up/down theo traffic, không cần capacity planning. Phù hợp với unpredictable traffic.
- Standard table class: tối ưu cho workload có throughput cao (cả read và write). Standard-IA có chi phí request cao hơn, chỉ phù hợp cho dữ liệu ít truy cập.
- Với "moderate to high" throughput unpredictable, on-demand sẽ cost-effective hơn provisioned + auto scaling vì provisioned phải trả tiền cho capacity đã provision (dù không dùng hết), trong khi on-demand chỉ trả cho request thực tế.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Provisioned + auto scaling: phù hợp cho workload predictable. Với unpredictable traffic, phải over-provision để tránh throttle → tốn kém. Nếu set max capacity thấp → bị throttle khi peak.

**❌ Đáp án C:**
- Standard-IA: chi phí lưu trữ thấp hơn, nhưng chi phí request (RCU/WCU) cao hơn. Với "moderate to high throughput", Standard-IA sẽ đắt hơn Standard.
- Dùng sai use case: Standard-IA cho dữ liệu ít truy cập, không phải workload throughput cao.

**❌ Đáp án D:**
- Standard-IA + on-demand: sai vì Standard-IA không phù hợp với throughput cao. Chi phí request cao sẽ đội tổng chi phí lên rất nhiều.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Unpredictable throughput → DynamoDB On-demand. Moderate to high → Standard class (không dùng Standard-IA). Provisioned = predictable traffic."*
