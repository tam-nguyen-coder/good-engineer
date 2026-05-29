# Question #625 - Topic 1

A company is hosting a website behind multiple Application Load Balancers. The company has different distribution rights for its content around the world. A solutions architect needs to ensure that users are served the correct content without violating distribution rights. Which configuration should the solutions architect choose to meet these requirements?

## Options

**A.** Configure Amazon CloudFront with AWS WAF.

**B.** Configure Application Load Balancers with AWS WAF.

**C.** Configure Amazon Route 53 with a geolocation policy.

**D.** Configure Amazon Route 53 with a geoproximity routing policy.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Website behind multiple ALBs, different distribution rights per geographic region. Cần serve correct content dựa trên user location.
- **Existing Resources:** Multiple Application Load Balancers.
- **Current Issue/Goal:** Route users đến đúng ALB (content) dựa trên vị trí địa lý.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `different distribution rights` | Quyền phân phối nội dung khác nhau theo khu vực địa lý. |
| `around the world` | Global user base. |
| `geolocation policy` | Route 53 định tuyến dựa trên vị trí địa lý của user (quốc gia, châu lục). |
| `geoproximity routing` | Định tuyến dựa trên khoảng cách địa lý và bias, không phân biệt quốc gia cụ thể. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements
- **Constraints:** Content distribution rights, user location-based routing

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Route 53 Geolocation Routing: định tuyến DNS dựa trên vị trí địa lý của user (quốc gia, continent).
- Cho phép map specific regions đến specific ALBs → users chỉ thấy content mà họ có quyền xem.
- Ví dụ: users ở US → ALB US (US content), users ở EU → ALB EU (EU content).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- CloudFront + WAF: CloudFront có geo-restriction nhưng chặn/từ chối truy cập, không phải routing đến different content. WAF không phải geo-routing solution.

**❌ Đáp án B:**
- ALB + WAF: ALB không có geo-routing capability. WAF filter traffic nhưng không route đến different backends dựa trên location.

**❌ Đáp án D:**
- Geoproximity routing: dựa trên khoảng cách địa lý và bias, không phân biệt quốc gia. Không chính xác cho distribution rights (cần biên giới quốc gia).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Distribution rights → Route 53 Geolocation (map country → specific ALB). Geoproximity = distance, không chính xác."*
