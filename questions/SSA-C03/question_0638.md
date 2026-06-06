# Question #638 - Topic 1

A company collects and shares research data with the company's employees all over the world. The company wants to collect and store the data in an Amazon S3 bucket and process the data in the AWS Cloud. The company will share the data with the company's employees. The company needs a secure solution in the AWS Cloud that minimizes operational overhead. Which solution will meet these requirements?

## Options

**A.** Use an AWS Lambda function to create an S3 presigned URL. Instruct employees to use the URL.

**B.** Create an IAM user for each employee. Create an IAM policy for each employee to allow S3 access. Instruct employees to use the AWS Management Console.

**C.** Create an S3 File Gateway. Create a share for uploading and a share for downloading. Allow employees to mount shares on their local computers to use S3 File Gateway.

**D.** Configure AWS Transfer Family SFTP endpoints. Select the custom identity provider options. Use AWS Secrets Manager to manage the user credentials. Instruct employees to use Transfer Family.

## 1. CONTEXT & DE BAI
- **Scenario:** Collect and share research data voi employees globally. Data trong S3, can secure access, minimize operational overhead.
- **Existing Resources:** Amazon S3 bucket, AWS Cloud processing.
- **Current Issue/Goal:** Secure sharing S3 data voi employees worldwide, minimal overhead.

## 2. KEYWORDS QUAN TRONG
| Keyword | Y nghia / Goi y |
|---------|-----------------|
| `employees all over the world` | Global access, can lightweight solution. |
| `secure solution` | Can temporary, limited access. |
| `minimizes operational overhead` | Presigned URL: khong can IAM users, khong can infrastructure. |
| `presigned URL` | Temporary URL voi expiration time, secure, zero infrastructure. |

## 3. YEU CAU CUA DE
- **Question type:** Minimize operational overhead
- **Constraints:** Secure, global employees, S3 data

## 4. DAP AN DUNG
**Dap an: A**

**Giai thich:**
- S3 Presigned URL: Lambda generate URL voi expiration time, employee co the download truc tiep tu S3.
- Secure: URL chi co hieu luc trong thoi gian nhat dinh, chi cho phep specific operations (GET).
- Operational overhead thap nhat: khong can IAM users, khong can maintain infrastructure.

## 5. CAC DAP AN SAI
**Dap an B:**
- IAM user cho moi employee: can tao/maintain users, credentials, permissions => operational overhead cao.
- AWS Console access: khong can thiet cho simple download use case.

**Dap an C:**
- S3 File Gateway: can deploy on-premises gateway, chi phu hop cho hybrid cloud, khong phai global sharing solution.
- Can mount shares => yeu cau network connectivity.

**Dap an D:**
- AWS Transfer Family SFTP: operational overhead cao (can manage endpoints, identity providers, Secrets Manager).
- Overkill cho simple use case share file.

## 6. MEO GHI NHO (Memory Hook)
*"Share S3 globally => Presigned URL (temporary, secure, zero infra). IAM users = overhead."*
