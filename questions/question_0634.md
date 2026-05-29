# Question #634 - Topic 1

A company collects 10 GB of telemetry data daily from various machines. The company stores the data in an Amazon S3 bucket in a source data account. The company has hired several consulting agencies to use this data for analysis. Each agency needs read access to the data for its analysts. The company must share the data from the source data account by choosing a solution that maximizes security and operational efficiency. Which solution will meet these requirements?

## Options

**A.** Configure S3 global tables to replicate data for each agency.

**B.** Make the S3 bucket public for a limited time. Inform only the agencies.

**C.** Configure cross-account access for the S3 bucket to the accounts that the agencies own.

**D.** Set up an IAM user for each analyst in the source data account. Grant each user access to the S3 bucket.

## 1. CONTEXT & DE BAI
- **Scenario:** 10 GB telemetry data daily in S3 (source account). Can share data voi consulting agencies. Each agency needs read access for its analysts.
- **Existing Resources:** S3 bucket in source account.
- **Current Issue/Goal:** Share S3 data voi agencies securely and efficiently.

## 2. KEYWORDS QUAN TRONG
| Keyword | Y nghia / Goi y |
|---------|-----------------|
| `cross-account access` | Cho phep agencies dung account rieng de access S3 bucket. |
| `maximizes security` | Khong make bucket public, khong tao IAM users cho ben ngoai. |
| `several consulting agencies` | Moi agency co account rieng. |
| `S3 bucket policy` | Co the grant cross-account access via bucket policy. |

## 3. YEU CAU CUA DE
- **Question type:** Maximize security and operational efficiency
- **Constraints:** Source account, agencies need read access

## 4. DAP AN DUNG
**Dap an: C**

**Giai thich:**
- Cross-account access: source account S3 bucket policy grant read access den IAM roles/users trong agency accounts.
- Agencies quan ly users cua ho trong account rieng => security tot hon (khong share credentials).
- Operational efficiency: khong can tao/maintain IAM users cho ben ngoai.

## 5. CAC DAP AN SAI
**Dap an A:**
- S3 khong co "global tables" nhu DynamoDB. Khong phai tinh nang co san.

**Dap an B:**
- Public bucket: vi pham security, bat ky ai cung co the truy cap neu biet URL.

**Dap an D:**
- IAM users trong source account: can quan ly users cho ben ngoai, operational overhead cao, security risk (shared account).

## 6. MEO GHI NHO (Memory Hook)
*"Share S3 voi ben ngoai => cross-account access. Khong public, khong IAM users cho nguoi ngoai."*
