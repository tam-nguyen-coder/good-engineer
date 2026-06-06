# Question #62 - Topic 1

A company is deploying a new public web application to AWS. The application will run behind an Application Load Balancer (ALB). The application needs to be encrypted at the edge with an SSL/TLS certificate that is issued by an external certificate authority (CA). The certificate must be rotated each year before the certificate expires. What should a solutions architect do to meet these requirements?

## Options

**A.** Use AWS Certificate Manager (ACM) to issue an SSL/TLS certificate. Apply the certificate to the ALB. Use the managed renewal feature to automatically rotate the certificate.

**B.** Use AWS Certificate Manager (ACM) to issue an SSL/TLS certificate. Import the key material from the certificate. Apply the certificate to the ALUse the managed renewal feature to automatically rotate the certificate.

**C.** Use AWS Certificate Manager (ACM) Private Certificate Authority to issue an SSL/TLS certificate from the root CA. Apply the certificate to the ALB. Use the managed renewal feature to automatically rotate the certificate.

**D.** Use AWS Certificate Manager (ACM) to import an SSL/TLS certificate. Apply the certificate to the ALB. Use Amazon EventBridge (Amazon CloudWatch Events) to send a notification when the certificate is nearing expiration. Rotate the certificate manually.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** ALB với SSL/TLS certificate từ external CA, cần rotate hàng năm.
- **Existing Resources:** ALB, external CA-issued certificate.
- **Current Issue/Goal:** Encrypt at edge, cert từ external CA, auto-rotate (hoặc notify).

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `issued by an external certificate authority (CA)` | Cert không phải từ ACM — phải import |
| `rotated each year` | Cần renewal process |
| `encrypted at the edge` | SSL termination trên ALB |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security + Certificate management
- **Constraints:** External CA cert, rotate yearly

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- Vì cert được **external CA** cấp, phải **import** vào ACM (ACM không thể issue cert thay external CA).
- **Imported certificates cannot be automatically renewed** by ACM — phải manual renewal.
- EventBridge notification để biết khi cert sắp hết hạn → rotate thủ công.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- ACM-issued cert là từ Amazon's public CA, không phải "external CA".

**❌ Đáp án B:**
- "Import the key material" — ACM-issued cert không có key material để import.
- ACM tự động renew cert của nó, không liên quan đến external CA.

**❌ Đáp án C:**
- **ACM Private CA** dùng cho internal PKI, không phải external/public CA.

**❌ Lưu ý quan trọng:**
- ACM **chỉ auto-renew** certificates do ACM **issued** (public hoặc private CA).
- **Imported certificates** (từ external CA) **không auto-renew** — phải manual.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"ACM issued = auto-renew. Imported cert (external CA) = manual renew + EventBridge alert"*
