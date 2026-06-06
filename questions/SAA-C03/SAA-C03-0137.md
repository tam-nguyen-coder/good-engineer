# Question #137 - Topic 1

A company uses AWS Organizations to create dedicated AWS accounts for each business unit to manage each business unit's account independently upon request. The root email recipient missed a notification that was sent to the root user email address of one account. The company wants to ensure that all future notifications are not missed. Future notifications must be limited to account administrators. Which solution will meet these requirements?

## Options

**A.** Configure the company’s email server to forward notification email messages that are sent to the AWS account root user email address to all users in the organization.

**B.** Configure all AWS account root user email addresses as distribution lists that go to a few administrators who can respond to alerts. Configure AWS account alternate contacts in the AWS Organizations console or programmatically.

**C.** Configure all AWS account root user email messages to be sent to one administrator who is responsible for monitoring alerts and forwarding those alerts to the appropriate groups.

**D.** Configure all existing AWS accounts and all newly created accounts to use the same root user email address. Configure AWS account alternate contacts in the AWS Organizations console or programmatically.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** AWS Organizations, missed root email notification. Cần ensure no future missed notifications.
- **Existing Resources:** Multiple AWS accounts.
- **Current Issue/Goal:** Notifications đến đúng administrators, không bị miss.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `root user email address` | Email gốc của account — dễ bị miss |
| `alternate contacts` | AWS feature để thêm contacts cho billing, operations, security |
| `limited to account administrators` | Chỉ admin mới nhận |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Account management
- **Constraints:** Không miss notifications, limited to admins

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **Distribution list** cho root email — nhiều admin nhận, không miss.
- **Alternate contacts** (billing, operations, security) — gửi notification đến đúng người quản lý.
- Có thể cấu hình qua AWS Organizations console hoặc API.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Forward đến tất cả users — quá rộng, không "limited to account administrators".

**❌ Đáp án C:**
- Single administrator — single point of failure, có thể miss như cũ.

**❌ Đáp án D:**
- Cùng root email cho tất cả accounts — security risk, nếu 1 account bị compromise thì tất cả đều ảnh hưởng.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Alternate contacts + distribution list = no missed notifications. Same root email = security risk"*
