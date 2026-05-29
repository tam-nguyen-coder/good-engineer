# Question #640 - Topic 1

A company has an application workflow that uses an AWS Lambda function to download and decrypt files from Amazon S3. These files are encrypted using AWS Key Management Service (AWS KMS) keys. A solutions architect needs to design a solution that will ensure the required permissions are set correctly. Which combination of actions accomplish this? (Choose two.)

## Options

**A.** Attach the kms:decrypt permission to the Lambda function's resource policy.

**B.** Grant the decrypt permission for the Lambda IAM role in the KMS key's policy.

**C.** Grant the decrypt permission for the Lambda resource policy in the KMS key's policy.

**D.** Create a new IAM policy with the kms:decrypt permission and attach the policy to the Lambda function.

**E.** Create a new IAM role with the kms:decrypt permission and attach the execution role to the Lambda function.

## 1. CONTEXT & DE BAI
- **Scenario:** Lambda function download va decrypt files tu S3, duoc encrypt bang KMS keys. Can configure permissions correctly.
- **Existing Resources:** Lambda function, S3 bucket, KMS key.
- **Current Issue/Goal:** Lambda can decrypt => can KMS decrypt permission.

## 2. KEYWORDS QUAN TRONG
| Keyword | Y nghia / Goi y |
|---------|-----------------|
| `Lambda IAM role` | Lambda execution role la IAM role duoc attach vao Lambda function. |
| `KMS key's policy` | KMS key policy co the grant permission den IAM roles. |
| `kms:decrypt` | Permission can thiet de decrypt bang KMS. |
| `execution role` | Lambda execution role chua permissions ma Lambda can. |
| `KMS key policy` | Can grant access cho principal (IAM role) trong key policy. |

## 3. YEU CAU CUA DE
- **Question type:** Permissions configuration (Choose 2)
- **Constraints:** Lambda decrypt S3 files encrypted with KMS

## 4. DAP AN DUNG
**Dap an: B va E**

**Giai thich:**
- **E:** Tao IAM role voi kms:decrypt permission, gan role do lam Lambda execution role => Lambda co the goi KMS decrypt.
- **B:** Grant decrypt permission cho Lambda IAM role trong KMS key's policy => KMS key cho phep role do decrypt.
- Ca hai buoc can thiet: role co permission (E) + key policy allow role (B).

## 5. CAC DAP AN SAI
**Dap an A:**
- Lambda resource policy dung de control ai co the invoke Lambda function, khong phai permission cho Lambda de goi service khac.

**Dap an C:**
- Lambda resource policy khong phai IAM principal, khong the grant permission trong KMS key policy. KMS key policy chi grant cho IAM users, roles, AWS services.

**Dap an D:**
- Lambda function khong the attach IAM policy truc tiep. Lambda dung execution role (IAM role) de获得 permissions. Statement nay sai ve mat ky thuat.

## 6. MEO GHI NHO (Memory Hook)
*"Lambda can KMS decrypt => IAM role (execution role) + KMS key policy grant cho role do."*
