# Question #544 - Topic 1

A retail company uses a regional Amazon API Gateway API for its public REST APIs. The API Gateway endpoint is a custom domain name that points to an Amazon Route 53 alias record. A solutions architect needs to create a solution that has minimal effects on customers and minimal data loss to release the new version of APIs. Which solution will meet these requirements?

## Options

**A.** Create a canary release deployment stage for API Gateway. Deploy the latest API version. Point an appropriate percentage of traffic to the canary stage. After API verification, promote the canary stage to the production stage.

**B.** Create a new API Gateway endpoint with a new version of the API in OpenAPI YAML file format. Use the import-to-update operation in merge mode into the API in API Gateway. Deploy the new version of the API to the production stage.

**C.** Create a new API Gateway endpoint with a new version of the API in OpenAPI JSON file format. Use the import-to-update operation in overwrite mode into the API in API Gateway. Deploy the new version of the API to the production stage.

**D.** Create a new API Gateway endpoint with new versions of the API definitions. Create a custom domain name for the new API Gateway API. Point the Route 53 alias record to the new API Gateway API custom domain name.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty retail dùng API Gateway regional với custom domain name (Route 53 alias record). Cần release phiên bản mới của API với tối thiểu ảnh hưởng đến khách hàng và tối thiểu mất dữ liệu.
- **Existing Resources:** Regional API Gateway API, custom domain name, Route 53 alias record.
- **Current Issue/Goal:** Deploy API version mới an toàn, kiểm soát traffic dần dần.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `minimal effects on customers` | Cần triển khai dần dần, không ảnh hưởng đến production |
| `minimal data loss` | Có thể rollback dễ dàng, không mất requests |
| `canary release` | Chiến lược deploy từng phần traffic |
| `release the new version of APIs` | Update API hiện tại, không tạo mới hoàn toàn |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most appropriate solution
- **Constraints:** Minimal customer impact, minimal data loss

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Canary release deployment cho phép triển khai phiên bản API mới và chỉ cho một phần nhỏ traffic (ví dụ 5-10%) đến phiên bản mới.
- Sau khi xác minh phiên bản mới hoạt động tốt (monitoring, logging), có thể promote canary stage lên production (100% traffic).
- Nếu có vấn đề, chỉ cần thay đổi tỷ lệ canary về 0% là rollback ngay lập tức, không mất dữ liệu và ảnh hưởng tối thiểu đến khách hàng.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B (Import YAML merge mode vào API hiện tại):** Import-to-update trong merge mode sẽ update trực tiếp API hiện tại. Nếu có lỗi, toàn bộ API sẽ bị ảnh hưởng, không có cơ chế canary hoặc rollback an toàn.

**❌ Đáp án C (Import JSON overwrite mode):** Overwrite mode sẽ ghi đè toàn bộ API definition, gây nguy cơ mất dữ liệu cấu hình API hiện tại. Không có canary testing.

**❌ Đáp án D (Tạo API Gateway mới + custom domain mới + Route 53):** Tạo API hoàn toàn mới và thay đổi DNS record làm gián đoạn dịch vụ do DNS propagation delay. Custom domain mới cũng gây ảnh hưởng đến client vì URL thay đổi (trừ khi dùng cùng domain nhưng Route 53 switch time có độ trễ).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"API Gateway canary = deploy new version to X% traffic, verify, promote to 100%. Rollback = set canary to 0%. Safer than direct import-update."*
