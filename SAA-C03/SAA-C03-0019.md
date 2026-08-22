# Question #19 - Topic 1

A company has a three-tier web application that is deployed on AWS. The web servers are deployed in a public subnet in a VPC. The application servers and database servers are deployed in private subnets in the same VPC. The company has deployed a third-party virtual firewall appliance from AWS Marketplace in an inspection VPC. The appliance is configured with an IP interface that can accept IP packets. A solutions architect needs to integrate the web application with the appliance to inspect all traffic to the application before the traffic reaches the web server. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Create a Network Load Balancer in the public subnet of the application's VPC to route the traffic to the appliance for packet inspection.

**B.** Create an Application Load Balancer in the public subnet of the application's VPC to route the traffic to the appliance for packet inspection.

**C.** Deploy a transit gateway in the inspection VPConfigure route tables to route the incoming packets through the transit gateway.

**D.** Deploy a Gateway Load Balancer in the inspection VPC. Create a Gateway Load Balancer endpoint to receive the incoming packets and forward the packets to the appliance.



 ---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty có


## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Một ứng dụng web 3-tier trên AWS với web server ở `public subnet`, application và database server ở `private subnet` (cùng một `VPC`). Có một thiết bị `virtual firewall` bên thứ ba (từ AWS Marketplace) được triển khai trong một `inspection VPC` riêng. Thiết bị này có interface có thể nhận các `IP packets`.
- **Current Issue/Goal:** Tích hợp ứng dụng web với thiết bị firewall để kiểm tra **tất cả traffic** đến ứng dụng **trước khi** traffic đến web server, với **ít operational overhead nhất**.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa |
|---------|---------|
| `virtual firewall appliance` | Thiết bị ảo bên thứ ba (IDS/IPS/Firewall) cần inspect traffic. |
| `inspection VPC` | VPC riêng chứa appliance, tách biệt với VPC ứng dụng. |
| `IP packets` | Traffic ở Layer 3, cần được forward dạng gói tin gốc để inspect. |
| `LEAST operational overhead` | Giải pháp phải là managed, native AWS, dễ triển khai nhất. |
| `AWS Marketplace` | Appliance thường tương thích với `Gateway Load Balancer` (dùng `GENEVE`). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Chọn kiến trúc tối ưu nhất với ràng buộc operational overhead thấp.
- **Constraints:** Traffic phải được inspect inline trước khi chạm web server; appliance nằm ở VPC khác; hoạt động ở L3/IP packet level.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:** 
- `Gateway Load Balancer` (`GWLB`) là dịch vụ được AWS thiết kế **riêng** cho use case này: tích hợp các third-party virtual appliances (firewall, IPS/IDS) từ AWS Marketplace để inspect traffic một cách **inline** và **transparent**.
- `GWLB` hoạt động ở Layer 3, sử dụng `GENEVE protocol` để encapsulate và forward `IP packets` gốc đến appliance.
- Cách hoạt động: Triển khai `GWLB` trong `inspection VPC` (nơi đặt appliance), sau đó tạo `Gateway Load Balancer endpoint` (`GWLBe`) trong `public subnet` của application VPC. Traffic đi vào sẽ được route qua `GWLBe` → `GWLB` → Appliance (inspect) → quay lại → đến web server.
- Đây là giải pháp managed, scalable, và có **ít operational overhead nhất** vì không cần tự quản lý routing phức tạp, NAT, hay tunnel thủ công.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:** Dùng `Network Load Balancer` trong public subnet để route traffic đến appliance.
- `NLB` có thể forward đến `IP targets`, nhưng để đưa traffic đi từ application VPC sang `inspection VPC` rồi quay lại web server đòi hỏi cấu hình routing, NAT, hoặc tunnel rất phức tạp. Không phải là cách native để inline inspect với appliance bên thứ ba trong VPC khác. Operational overhead cao.

**❌ Đáp án B:** Dùng `Application Load Balancer` trong public subnet để route traffic đến appliance.
- `ALB` hoạt động ở Layer 7 (HTTP/HTTPS), terminate connection, không forward raw `IP packets`. Một firewall appliance cần inspect `IP packets` ở L3/L4 sẽ không hoạt động đúng cách khi đứng sau `ALB`. Không phù hợp về mặt kiến trúc.

**❌ Đáp án C:** Triển khai `Transit Gateway` trong inspection VPC và route packet qua đó.
- `Transit Gateway` dùng để kết nối nhiều VPC/on-prem. Dù có thể dùng `appliance mode` để đẩy traffic qua inspection VPC, nhưng cách này đòi hỏi cấu hình `route tables`, `attachments`, đảm bảo symmetric routing, và thường phức tạp hơn nhiều so với `GWLB`. Không phải là giải pháp ít operational overhead nhất cho use case inline L3 inspection này.

## 6. MẸO GHI NHỚ
🧠 *Thấy "third-party virtual appliance/firewall/IDS từ AWS Marketplace" + "inspect IP packets" + "least operational overhead" → Nghĩ ngay đến `Gateway Load Balancer` (`GWLB`). `GWLB` dùng `GENEVE` để đẩy IP packets gốc vào appliance. `GWLBe` (endpoint) nằm ở VPC cần bảo vệ, còn `GWLB` nằm ở `inspection VPC`.*
