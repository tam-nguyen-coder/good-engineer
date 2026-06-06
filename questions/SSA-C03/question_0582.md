# Question #582 - Topic 1

An ecommerce company uses Amazon Route 53 as its DNS provider. The company hosts its website on premises and in the AWS Cloud. The company's on-premises data center is near the us-west-1 Region. The company uses the eu-central-1 Region to host the website. The company wants to minimize load time for the website as much as possible. Which solution will meet these requirements?

## Options

**A.** Set up a geolocation routing policy. Send the traffic that is near us-west-1 to the on-premises data center. Send the traffic that is near eu- central-1 to eu-central-1.

**B.** Set up a simple routing policy that routes all traffic that is near eu-central-1 to eu-central-1 and routes all traffic that is near the on-premises datacenter to the on-premises data center.

**C.** Set up a latency routing policy. Associate the policy with us-west-1.

**D.** Set up a weighted routing policy. Split the traffic evenly between eu-central-1 and the on-premises data center.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Ecommerce website hosted both on-prem (near us-west-1) and eu-central-1 (AWS), want minimize load time.
- **Existing Resources:** Route 53.
- **Current Issue/Goal:** Minimize load time using DNS routing.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `minimize load time` | Cần routing dựa trên vị trí địa lý (geolocation) hoặc latency. |
| `geolocation routing` | Route dựa trên location của user → gửi đến endpoint gần nhất. |
| `near us-west-1` | on-prem DC gần us-west-1. |
| `near eu-central-1` | AWS Region. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Minimize load time
- **Constraints:** Two endpoints (on-prem near us-west-1, eu-central-1)

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Geolocation routing: Route 53 xác định location của user và route đến endpoint gần nhất.
- Users near us-west-1 → on-prem. Users near eu-central-1 → eu-central-1.
- Giảm latency tối đa bằng cách gửi user đến endpoint địa lý gần nhất.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Simple routing: chỉ route đến một endpoint (không thể routing conditional). Không support "near" logic.

**❌ Đáp án C:**
- Latency routing: đo latency thực tế, nhưng option này "associate the policy with us-west-1" không đúng cách. Thường latency routing chọn Region có latency thấp nhất tự động.

**❌ Đáp án D:**
- Weighted routing: chia traffic theo weight, không dựa trên location. Users xa sẽ bị latency cao.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Minimize load time by location → Geolocation routing. Latency = measure actual latency. Weighted = % split."*
