# Question #576 - Topic 1

A company is building a RESTful serverless web application on AWS by using Amazon API Gateway and AWS Lambda. The users of this web application will be geographically distributed, and the company wants to reduce the latency of API requests to these users. Which type of endpoint should a solutions architect use to meet these requirements?

## Options

**A.** Private endpoint

**B.** Regional endpoint

**C.** Interface VPC endpoint

**D.** Edge-optimized endpoint

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** API Gateway + Lambda, users geographically distributed, reduce latency.
- **Existing Resources:** API Gateway, Lambda.
- **Current Issue/Goal:** Giảm latency cho global users.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `geographically distributed` | Cần CDN/edge locations để giảm latency. |
| `reduce the latency` | Edge-optimized endpoint uses CloudFront. |
| `API Gateway endpoint type` | Edge-optimized, Regional, Private. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which type of endpoint
- **Constraints:** Serverless, global users, reduce latency

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- Edge-optimized endpoint: API Gateway + CloudFront distribution globally → requests đi qua edge locations gần user nhất.
- Giảm latency nhờ CloudFront caching và edge termination.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Private endpoint: chỉ truy cập trong VPC, không public internet.

**❌ Đáp án B:**
- Regional endpoint: chỉ deploy trong một Region → users xa sẽ bị latency cao.

**❌ Đáp án C:**
- Interface VPC endpoint: dùng cho AWS services trong VPC (AWS PrivateLink), không liên quan API Gateway endpoint type.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Global users → Edge-optimized (CloudFront). Regional = single region latency. Private = VPC only."*
