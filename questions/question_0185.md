# Question #185 - Topic 1

A company runs an application using Amazon ECS. The application creates resized versions of an original image and then makes Amazon S3 API calls to store the resized images in Amazon S3. How can a solutions architect ensure that the application has permission to access Amazon S3?

## Options

**A.** Update the S3 role in AWS IAM to allow read/write access from Amazon ECS, and then relaunch the container.

**B.** Create an IAM role with S3 permissions, and then specify that role as the taskRoleArn in the task definition.

**C.** Create a security group that allows access from Amazon ECS to Amazon S3, and update the launch configuration used by the ECS cluster.

**D.** Create an IAM user with S3 permissions, and then relaunch the Amazon EC2 instances for the ECS cluster while logged in as this account.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** ECS app resizes images and stores in S3 via S3 API calls.
- **Existing Resources:** ECS cluster.
- **Current Issue/Goal:** Grant S3 permissions to ECS task.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Amazon ECS` | Cần IAM role cho task |
| `taskRoleArn` | IAM role cho ECS task |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / IAM
- **Constraints:** ECS task → S3 API

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **taskRoleArn** — IAM role được gán cho ECS task, cấp permission cho containers trong task.
- Role cần s3:PutObject permission.
- Đây là best practice cho ECS tasks.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- "S3 role" không phải concept trong IAM.

**❌ Đáp án C:**
- Security group — network-level, không thể cấp API permissions.

**❌ Đáp án D:**
- IAM user + EC2 instance login — không best practice, không scalable.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"ECS taskRoleArn = IAM role for containers. Security group = network only. IAM user = not best practice"*
