# Question #197 - Topic 1

A company has a Microsoft .NET application that runs on an on-premises Windows Server. The application stores data by using an Oracle Database Standard Edition server. The company is planning a migration to AWS and wants to minimize development changes while moving the application. The AWS application environment should be highly available. Which combination of actions should the company take to meet these requirements? (Choose two.)

## Options

**A.** Refactor the application as serverless with AWS Lambda functions running .NET Core.

**B.** Rehost the application in AWS Elastic Beanstalk with the .NET platform in a Multi-AZ deployment.

**C.** Replatform the application to run on Amazon EC2 with the Amazon Linux Amazon Machine Image (AMI).

**D.** Use AWS Database Migration Service (AWS DMS) to migrate from the Oracle database to Amazon DynamoDB in a Multi-AZ deployment.

**E.** Use AWS Database Migration Service (AWS DMS) to migrate from the Oracle database to Oracle on Amazon RDS in a Multi-AZ deployment.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** .NET app on Windows Server, Oracle DB Standard. Migrate to AWS, min dev changes, HA.
- **Existing Resources:** .NET app, Oracle DB.
- **Current Issue/Goal:** Minimal change migration, HA.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `minimize development changes` | **Rehost** (lift & shift) |
| `.NET application on Windows Server` | Elastic Beanstalk .NET platform |
| `Oracle Database` | **Oracle on RDS Multi-AZ** |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Migration
- **Constraints:** Chọn 2, min dev changes, HA

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B và E**

**Giải thích:**
- **B: Elastic Beanstalk .NET Multi-AZ** — rehost .NET app, HA, min dev changes.
- **E: DMS → Oracle on RDS Multi-AZ** — migrate Oracle DB lên RDS Oracle Multi-AZ, compatible, HA.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Refactor to Lambda .NET Core — cần code changes.

**❌ Đáp án C:**
- Amazon Linux — .NET không chạy trên Linux (cần Windows).

**❌ Đáp án D:**
- Oracle → DynamoDB — schema changes, code changes.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Elastic Beanstalk .NET + Oracle RDS Multi-AZ = rehost. Lambda/DynamoDB = refactor (more changes)"*
