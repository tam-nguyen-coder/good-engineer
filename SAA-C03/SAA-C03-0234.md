# Question #234 - Topic 1

A company is building a new web-based customer relationship management application. The application will use several Amazon EC2 instances that are backed by Amazon Elastic Block Store (Amazon EBS) volumes behind an Application Load Balancer (ALB). The application will also use an Amazon Aurora database. All data for the application must be encrypted at rest and in transit. Which solution will meet these requirements?

## Options

**A.** Use AWS Key Management Service (AWS KMS) certificates on the ALB to encrypt data in transit. Use AWS Certificate Manager (ACM) to encrypt the EBS volumes and Aurora database storage at rest.

**B.** Use the AWS root account to log in to the AWS Management Console. Upload the company's encryption certificates. While in the root account, select the option to turn on encryption for all data at rest and in transit for the account.

**C.** Use AWS Key Management Service (AWS KMS) to encrypt the EBS volumes and Aurora database storage at rest. Attach an AWS Certificate Manager (ACM) certificate to the ALB to encrypt data in transit.

**D.** Use BitLocker to encrypt all data at rest. Import the company's TLS certificate keys to AWS Key Management Service (AWS KMS). Attach the KMS keys to the ALB to encrypt data in transit.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** CRM app on EC2 + EBS + ALB + Aurora. Encrypt at rest + in transit.
- **Existing Resources:** EC2, EBS, ALB, Aurora.
- **Current Issue/Goal:** KMS for at-rest, ACM for in-transit.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `encrypted at rest` | **AWS KMS** (EBS, Aurora) |
| `encrypted in transit` | **ACM** certificate on ALB (TLS) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / Encryption
- **Constraints:** At-rest + in-transit

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- **KMS** — encrypt EBS volumes và Aurora storage at rest.
- **ACM** — quản lý TLS certificate cho ALB → encrypt traffic in transit.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- KMS cho in-transit, ACM cho at-rest — sai: KMS là key management, ACM là certificate.

**❌ Đáp án B:**
- Root account — không nên dùng. Không có option "encrypt all data" một lần.

**❌ Đáp án D:**
- BitLocker — không phải AWS managed. KMS keys không thể attach trực tiếp vào ALB.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"KMS = encrypt at rest (EBS, Aurora). ACM = TLS certs for in transit (ALB)"*
