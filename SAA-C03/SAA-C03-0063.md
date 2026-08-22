# Question #63 - Topic 1

A company runs its infrastructure on AWS and has a registered base of 700,000 users for its document management application. The company intends to create a product that converts large .pdf files to .jpg image files. The .pdf files average 5 MB in size. The company needs to store the original files and the converted files. A solutions architect must design a scalable solution to accommodate demand that will grow rapidly over time. Which solution meets these requirements MOST cost-effectively?

## Options

**A.** Save the .pdf files to Amazon S3. Configure an S3 PUT event to invoke an AWS Lambda function to convert the files to .jpg format and store them back in Amazon S3.

**B.** Save the .pdf files to Amazon DynamoDUse the DynamoDB Streams feature to invoke an AWS Lambda function to convert the files to .jpg format and store them back in DynamoDB.

**C.** Upload the .pdf files to an AWS Elastic Beanstalk application that includes Amazon EC2 instances, Amazon Elastic Block Store (Amazon EBS) storage, and an Auto Scaling group. Use a program in the EC2 instances to convert the files to .jpg format. Save the .pdf files and the .jpg files in the EBS store.

**D.** Upload the .pdf files to an AWS Elastic Beanstalk application that includes Amazon EC2 instances, Amazon Elastic File System (Amazon EFS) storage, and an Auto Scaling group. Use a program in the EC2 instances to convert the file to .jpg format. Save the .pdf files and the .jpg files in the EBS store.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Document management, convert PDF (5MB) → JPG. Cần store cả original và converted.
- **Existing Resources:** 700,000 users.
- **Current Issue/Goal:** Scalable, cost-effective solution, demand tăng nhanh.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `demand that will grow rapidly` | Cần serverless để scale tự động |
| `most cost-effectively` | Pay-per-use, không provision trước |
| `5 MB in size` | Phù hợp Lambda (max payload 6MB cho synchronous, nhưng S3 event là async) |
| `.pdf to .jpg` | CPU-bound conversion — Lambda có giới hạn |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective + Scalable
- **Constraints:** Document conversion, file storage

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **S3 event notification** trigger Lambda khi PDF được upload.
- **Lambda** xử lý conversion PDF → JPG, lưu lại vào S3.
- Serverless, pay-per-use, scale tự động theo số lượng files.
- S3 lưu trữ cost-effective cho cả original và converted files.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- DynamoDB có giới hạn item size **400 KB** — 5MB PDF không thể lưu.
- DynamoDB không phải file storage.

**❌ Đáp án C:**
- Elastic Beanstalk + EC2 + EBS — phải provision capacity, không cost-effective cho demand không predictable.
- EBS không share được giữa instances và không tự động scale.

**❌ Đáp án D:**
- Tương tự C — thêm EFS nhưng vẫn phải quản lý EC2 instances.
- "Save files in the EBS store" — sai, EBS được mention nhưng không phải shared storage.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"S3 + Lambda = serverless file processing. DynamoDB max 400KB — không chứa file"*
