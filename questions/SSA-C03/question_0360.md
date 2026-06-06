# Question #360 - Topic 1

A company uses Amazon API Gateway to run a private gateway with two REST APIs in the same VPC. The BuyStock RESTful web service calls the CheckFunds RESTful web service to ensure that enough funds are available before a stock can be purchased. The company has noticed in the VPC flow logs that the BuyStock RESTful web service calls the CheckFunds RESTful web service over the internet instead of through the VPC. A solutions architect must implement a solution so that the APIs communicate through the VPC. Which solution will meet these requirements with the FEWEST changes to the code?

## Options

**A.** Add an X-API-Key header in the HTTP header for authorization.

**B.** Use an interface endpoint.

**C.** Use a gateway endpoint.

**D.** Add an Amazon Simple Queue Service (Amazon SQS) queue between the two REST APIs.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Two Private REST APIs in API Gateway trong cùng VPC. Một API gọi API kia qua internet thay vì qua VPC.
- **Existing Resources:** API Gateway Private REST APIs trong VPC.
- **Current Issue/Goal:** Route traffic giữa APIs qua VPC (không qua internet), fewest code changes.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `private gateway` | API Gateway Private: chỉ truy cập trong VPC qua interface endpoint. |
| `interface endpoint` | AWS PrivateLink VPC endpoint for API Gateway (execute-api). |
| `gateway endpoint` | For S3/DynamoDB only, không support API Gateway. |
| `fewest changes to the code` | Interface endpoint: chỉ cần change API endpoint URL từ public → VPC private DNS. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Fewest changes to the code
- **Constraints:** API Gateway Private, VPC communication, same VPC

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Interface endpoint (AWS PrivateLink) cho API Gateway: tạo VPC endpoint cho execute-api trong VPC.
- API Gateway Private chỉ accessible qua interface endpoint.
- Code changes: chỉ cần đổi endpoint URL từ public API Gateway URL → private DNS name (VPC endpoint).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- X-API-Key header xác thực API, không ảnh hưởng đến network routing. Traffic vẫn qua internet.

**❌ Đáp án C:**
- Gateway endpoint chỉ hỗ trợ S3 và DynamoDB, không support API Gateway.

**❌ Đáp án D:**
- SQS giữa 2 APIs: thay đổi architecture hoàn toàn (sync → async) → nhiều code changes.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"API Gateway Private VPC communication → Interface Endpoint (PrivateLink). Gateway endpoint = S3/DynamoDB only."*
