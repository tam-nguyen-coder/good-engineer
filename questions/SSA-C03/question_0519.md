# Question #519 - Topic 1

A consulting company provides professional services to customers worldwide. The company provides solutions and tools for customers to expedite gathering and analyzing data on AWS. The company needs to centrally manage and deploy a common set of solutions and tools for customers to use for self-service purposes. Which solution will meet these requirements?

## Options

**A.** Create AWS CloudFormation templates for the customers.

**B.** Create AWS Service Catalog products for the customers.

**C.** Create AWS Systems Manager templates for the customers.

**D.** Create AWS Config items for the customers.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Consulting company cung cấp solutions và tools cho customers worldwide. Cần centrally manage và deploy common solutions để customers tự dùng (self-service).
- **Existing Resources:** AWS solutions/tools.
- **Current Issue/Goal:** Centralized management + self-service deployment cho customers.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `centrally manage and deploy` | Quản lý tập trung, kiểm soát versions, permissions. |
| `common set of solutions and tools` | Standardized products, có thể tái sử dụng. |
| `self-service purposes` | Customer tự deploy mà không cần can thiệp của consulting team. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Centrally manage + self-service
- **Constraints:** Customers worldwide, self-service deployment

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- AWS Service Catalog cho phép tạo "products" (có thể là CloudFormation templates) và publish thành "portfolio".
- Customers được cấp quyền truy cập vào portfolio → tự deploy products mà không cần chia sẻ template files.
- Centralized management: consulting company quản lý versions, updates, permissions tập trung.
- Hỗ trợ governance (ai được deploy gì, version nào) và self-service.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- CloudFormation templates là infrastructure-as-code, nhưng chia sẻ templates cho customers (gửi file) không có centralized management.
- Không có access control, version control, hay self-service portal built-in.

**❌ Đáp án C:**
- Systems Manager dùng để quản lý và vận hành EC2 instances (patch, run command, state manager). Không phải để deploy solutions cho customers.

**❌ Đáp án D:**
- AWS Config dùng để đánh giá compliance của resources (rules). Không phải để deploy solutions.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Self-service deploy + centrally manage → AWS Service Catalog (products + portfolios). CloudFormation chỉ là template, Service Catalog thêm governance + self-service."*
