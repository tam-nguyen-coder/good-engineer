# Question #684 - Topic 1

A company wants to migrate its web applications from on premises to AWS. The company is located close to the eu-central-1 Region. Because of regulations, the company cannot launch some of its applications in eu-central-1. The company wants to achieve single-digit millisecond latency. Which solution will meet these requirements?

## Options

**A.** Deploy the applications in eu-central-1. Extend the company’s VPC from eu-central-1 to an edge location in Amazon CloudFront.

**B.** Deploy the applications in AWS Local Zones by extending the company's VPC from eu-central-1 to the chosen Local Zone.

**C.** Deploy the applications in eu-central-1. Extend the company’s VPC from eu-central-1 to the regional edge caches in Amazon CloudFront.

**D.** Deploy the applications in AWS Wavelength Zones by extending the company’s VPC from eu-central-1 to the chosen Wavelength Zone.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Company near eu-central-1, regulations prevent deploying some apps in eu-central-1. Need single-digit ms latency.
- **Existing Resources:** On-premises applications near eu-central-1.
- **Current Issue/Goal:** Deploy near users but not in eu-central-1, low latency.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `cannot launch some of its applications in eu-central-1` | Due to regulations, cannot use parent region. |
| `single-digit millisecond latency` | AWS Local Zones: single-digit ms latency, close to users. |
| `Local Zones` | Extension of AWS Region, placed near large population centers. |
| `Wavelength Zones` | For 5G edge computing (telco). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements
- **Constraints:** Cannot use eu-central-1, single-digit ms latency

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- AWS Local Zones: mở rộng VPC từ region (eu-central-1) đến các location gần users.
- Single-digit ms latency đến end users.
- Regulations cấm deploy trong eu-central-1 → Local Zones vẫn được quản lý bởi region nhưng compute/storage ở location riêng.
- Phù hợp cho latency-sensitive applications.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- CloudFront edge location chỉ cache content (CDN), không thể deploy applications.
- VPC không thể extend đến CloudFront edge.

**❌ Đáp án C:**
- Regional edge cache là caches trong CloudFront, không deploy được applications.

**❌ Đáp án D:**
- Wavelength Zones dành cho 5G mobile edge computing, yêu cầu telecom provider integration.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Cannot use region + need low latency → AWS Local Zones. Wavelength = 5G."*
