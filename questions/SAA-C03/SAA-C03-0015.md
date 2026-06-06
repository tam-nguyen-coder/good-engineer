# Question #15 - Topic 1

A company recently migrated to AWS and wants to implement a solution to protect the traffic that flows in and out of the production VPC. The company had an inspection server in its on-premises data center. The inspection server performed specific operations such as traffic flow inspection and traffic filtering. The company wants to have the same functionalities in the AWS Cloud. Which solution will meet these requirements?

## Options

**A.** Use Amazon GuardDuty for traffic inspection and traffic filtering in the production VPC.

**B.** Use Traffic Mirroring to mirror traffic from the production VPC for traffic inspection and filtering.

**C.** Use AWS Network Firewall to create the required rules for traffic inspection and traffic filtering for the production VPC.

**D.** Use AWS Firewall Manager to create the required rules for traffic inspection and traffic filtering for the production VPC.



 ## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Một công ty mới migrate lên AWS và muốn triển khai giải pháp bảo vệ traffic đi vào/ra khỏi `production VPC`. Trước đây tại data center on-premises, họ sử dụng một `inspection server` để thực hiện `traffic flow inspection` và `traffic filtering`.
- **Existing Resources:** `Production VPC` trên AWS.
- **Current Issue/Goal:** Tìm kiếm dịch vụ AWS tương đương để thay thế inspection server on-premises, đảm bảo khả năng inspect và filter traffic cho VPC.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| `production VPC` | VPC chứa workload production, cần được bảo vệ biên giới (north-south traffic) |
| `inspection server` | Thiết bị/firewall appliance thực hiện kiểm tra và lọc traffic |
| `traffic flow inspection` | Kiểm tra sâu nội dung/luồng traffic (stateful/stateless inspection) |
| `traffic filtering` | Hành động cho phép (allow) hoặc chặn (drop) traffic dựa trên quy tắc |
| `in and out` | Traffic vào/ra VPC (north-south), có thể kèm east-west giữa các subnet |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Single choice – chọn dịch vụ AWS thay thế chức năng của on-premises inspection server.
- **Constraints:** Giải pháp phải thực hiện được **cả hai** chức năng: inspect traffic VÀ filter traffic một cách chủ động (inline) cho VPC.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**
**Giải thích:** `AWS Network Firewall` là managed firewall service được thiết kế riêng cho VPC, cung cấp khả năng `stateful inspection`, `stateless rules`, `intrusion prevention system (IPS)` và traffic filtering (allow/drop) hoạt động **inline**. Khi traffic đi vào/ra hoặc giữa các subnet trong `production VPC`, nó phải đi qua `Network Firewall`, cho phép công ty áp dụng các quy tắc phức tạp để inspect và filter traffic giống hệt một inspection server on-premises truyền thống.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:** `Amazon GuardDuty` là dịch vụ phát hiện mối đe dọa (threat detection) dựa trên phân tích `VPC Flow Logs`, `CloudTrail`, `DNS logs` bằng machine learning. GuardDuty **không phải** là inline firewall và **không thể** thực hiện `traffic filtering` (block traffic real-time). Nó chỉ cảnh báo sau khi phát hiện dấu hiệu bất thường.

**❌ Đáp án B:** `Traffic Mirroring` chỉ sao chép (mirror) traffic từ `EC2 instances` ra một out-of-band appliance bên ngoài để giám sát/phân tích. Đây là cơ chế **passive** (chỉ quan sát bản sao), do đó nó **không thể** thực hiện `traffic filtering` hoặc chặn traffic gốc. Không đáp ứng được yêu cầu filter.

**❌ Đáp án D:** `AWS Firewall Manager` là dịch vụ quản lý tập trung (security management service) dùng để triển khai và quản lý các quy tắc từ `AWS WAF`, `AWS Shield Advanced`, `AWS Network Firewall`, và Security Groups **xuyên suốt nhiều accounts/regions**. Nó **không trực tiếp** inspect hay filter traffic; nó chỉ giúp quản lý policy. Công ty cần engine firewall chứ không phải công cụ quản lý policy.

## 6. MẸO GHI NHỚ
🧠 *"Inspect + Filter traffic inline trong VPC"* → `AWS Network Firewall`
🧠 *"Quản lý firewall rules trên nhiều accounts"* → `AWS Firewall Manager`
🧠 *"Mirror traffic để giám sát out-of-band"* → `Traffic Mirroring` (không filter được)
🧠 *"Threat detection từ logs, không block được"* → `Amazon GuardDuty`


---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Một công ty mới migrate lên AWS và muốn triển khai giải pháp bảo vệ traffic đi vào/ra khỏi `production VPC`. Trước đây tại data center on-premises, họ sử dụng một `inspection server` để thực hiện `traffic flow inspection` và `traffic filtering`.
- **Existing Resources:** `Production VPC` trên AWS.
- **Current Issue/Goal:** Tìm kiếm dịch vụ AWS tương đương để thay thế `inspection server` on-premises, đảm bảo khả năng inspect và filter traffic cho VPC.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `production VPC` | VPC chứa workload production, cần được bảo vệ biên giới (`north-south traffic`) |
| `inspection server` | Thiết bị/firewall appliance thực hiện kiểm tra và lọc traffic |
| `traffic flow inspection` | Kiểm tra sâu nội dung/luồng traffic (`stateful`/`stateless inspection`) |
| `traffic filtering` | Hành động cho phép (`allow`) hoặc chặn (`drop`) traffic dựa trên quy tắc |
| `in and out` | Traffic vào/ra VPC (`north-south`), có thể kèm `east-west` giữa các `subnet` |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Single choice – chọn dịch vụ AWS thay thế chức năng của on-premises `inspection server`.
- **Constraints:** Giải pháp phải thực hiện được **cả hai** chức năng: inspect traffic VÀ filter traffic một cách chủ động (`inline`) cho `VPC`.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- `AWS Network Firewall` là `managed firewall service` được thiết kế riêng cho `VPC`, cung cấp khả năng `stateful inspection`, `stateless rules`, `intrusion prevention system (IPS)` và `traffic filtering` (`allow`/`drop`) hoạt động **`inline`**. Khi traffic đi vào/ra hoặc giữa các `subnet` trong `production VPC`, nó phải đi qua `Network Firewall`, cho phép công ty áp dụng các quy tắc phức tạp để inspect và filter traffic giống hệt một `inspection server` on-premises truyền thống.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- `Amazon GuardDuty` là dịch vụ phát hiện mối đe dọa (`threat detection`) dựa trên phân tích `VPC Flow Logs`, `CloudTrail`, `DNS logs` bằng `machine learning`. `GuardDuty` **không phải** là `inline firewall` và **không thể** thực hiện `traffic filtering` (block traffic real-time). Nó chỉ cảnh báo sau khi phát hiện dấu hiệu bất thường.

**❌ Đáp án B:**
- `Traffic Mirroring` chỉ sao chép (`mirror`) traffic từ `EC2 instances` ra một `out-of-band` appliance bên ngoài để giám sát/phân tích. Đây là cơ chế **`passive`** (chỉ quan sát bản sao), do đó nó **không thể** thực hiện `traffic filtering` hoặc chặn traffic gốc. Không đáp ứng được yêu cầu filter.

**❌ Đáp án D:**
- `AWS Firewall Manager` là dịch vụ quản lý tập trung (`security management service`) dùng để triển khai và quản lý các quy tắc từ `AWS WAF`, `AWS Shield Advanced`,
