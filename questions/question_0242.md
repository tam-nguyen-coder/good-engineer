# Question #242 - Topic 1

A company hosts its web application on AWS using seven Amazon EC2 instances. The company requires that the IP addresses of all healthy EC2 instances be returned in response to DNS queries. Which policy should be used to meet this requirement?

## Options

**A.** Simple routing policy

**B.** Latency routing policy

**C.** Multivalue routing policy

**D.** Geolocation routing policy

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** 7 EC2 instances. Need IP addresses of all healthy instances returned via DNS.
- **Existing Resources:** EC2 instances.
- **Current Issue/Goal:** DNS routing with health checks.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `all healthy EC2 instances` | **Multivalue answer** (returns up to 8 healthy records) |
| `returned in response to DNS queries` | Route 53 routing policy |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** DNS / Routing
- **Constraints:** Return multiple healthy IPs

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **Multivalue answer routing** — trả về up to 8 records, chỉ bao gồm healthy records (có health checks).
- Client sẽ chọn ngẫu nhiên 1 IP từ danh sách.
- Phù hợp cho 7 instances (dưới 8).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Simple routing — returns all values nhưng không hỗ trợ health checks.

**❌ Đáp án B:**
- Latency routing — dựa trên latency, không trả về tất cả.

**❌ Đáp án D:**
- Geolocation routing — dựa trên vị trí địa lý.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Multivalue = return up to 8 healthy IPs. Simple = no health check. Latency/Geo = single best"*
