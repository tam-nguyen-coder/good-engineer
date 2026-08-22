# Question #72 - Topic 1

A company runs a photo processing application that needs to frequently upload and download pictures from Amazon S3 buckets that are located in the same AWS Region. A solutions architect has noticed an increased cost in data transfer fees and needs to implement a solution to reduce these costs. How can the solutions architect meet this requirement?

## Options

**A.** Deploy Amazon API Gateway into a public subnet and adjust the route table to route S3 calls through it.

**B.** Deploy a NAT gateway into a public subnet and attach an endpoint policy that allows access to the S3 buckets.

**C.** Deploy the application into a public subnet and allow it to route through an internet gateway to access the S3 buckets.

**D.** Deploy an S3 VPC gateway endpoint into the VPC and attach an endpoint policy that allows access to the S3 buckets.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Photo processing app frequent S3 upload/download trong cùng Region.
- **Existing Resources:** EC2 instances, S3 buckets.
- **Current Issue/Goal:** Giảm data transfer costs.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `increased cost in data transfer fees` | Traffic qua internet gateway hoặc NAT gateway tốn phí |
| `same AWS Region` | Có thể dùng VPC Gateway Endpoint (free) |
| `reduce these costs` | Tránh traffic qua internet |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost optimization
- **Constraints:** S3 same Region, reduce data transfer

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **S3 VPC Gateway Endpoint** — cho phép EC2 trong VPC access S3 qua AWS private network, **không tính phí data transfer**.
- Traffic không đi qua internet gateway → giảm đáng kể chi phí.
- Endpoint policy kiểm soát access đến S3 buckets.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- API Gateway không phải để route S3 traffic. Sai kiến trúc.

**❌ Đáp án B:**
- **NAT gateway** tính phí per hour + data processing — làm tăng chi phí, không giảm.

**❌ Đáp án C:**
- **Internet gateway** — data transfer qua internet tốn phí (đặc biệt là data transfer từ EC2 → S3 khi ở cùng Region vẫn tính phí nếu qua NAT/IGW).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"S3 Gateway Endpoint = free, private access. NAT Gateway = extra cost. IGW = public, costs"*
