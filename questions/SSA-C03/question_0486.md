# Question #486 - Topic 1

A company is building a three-tier application on AWS. The presentation tier will serve a static website The logic tier is a containerized application. This application will store data in a relational database. The company wants to simplify deployment and to reduce operational costs. Which solution will meet these requirements?

## Options

**A.** Use Amazon S3 to host static content. Use Amazon Elastic Container Service (Amazon ECS) with AWS Fargate for compute power. Use a managed Amazon RDS cluster for the database.

**B.** Use Amazon CloudFront to host static content. Use Amazon Elastic Container Service (Amazon ECS) with Amazon EC2 for compute power. Use a managed Amazon RDS cluster for the database.

**C.** Use Amazon S3 to host static content. Use Amazon Elastic Kubernetes Service (Amazon EKS) with AWS Fargate for compute power. Use a managed Amazon RDS cluster for the database.

**D.** Use Amazon EC2 Reserved Instances to host static content. Use Amazon Elastic Kubernetes Service (Amazon EKS) with Amazon EC2 for compute power. Use a managed Amazon RDS cluster for the database.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Three-tier app: static website (presentation), containerized app (logic), relational DB. Mục tiêu: simplify deployment, reduce operational costs.
- **Existing Resources:** N/A (greenfield).
- **Current Issue/Goal:** Chọn kiến trúc đơn giản nhất, rẻ nhất cho three-tier app.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `static website` | S3 static website hosting (rẻ, đơn giản). |
| `containerized application` | ECS đơn giản hơn EKS cho container orchestration. |
| `simplify deployment and reduce operational costs` | Fargate (serverless container) không cần quản lý EC2. RDS managed. |
| `relational database` | Amazon RDS (managed). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Simplify deployment + reduce operational costs
- **Constraints:** Three-tier, static web, container, relational DB.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **S3 static website hosting:** Rẻ nhất, không cần quản lý server, scale tự động.
- **ECS on Fargate:** Serverless container, không cần quản lý EC2 cluster, pay-per-task.
- **RDS managed:** Không cần quản lý DB server, tự động backup, patch.
- Kết hợp: đơn giản nhất, operational cost thấp nhất.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- **CloudFront** để host static content: tốn thêm chi phí CDN, không cần thiết nếu chỉ là static site đơn giản.
- **ECS with EC2:** Cần quản lý EC2 instances → operational cost cao hơn Fargate.

**❌ Đáp án C:**
- **EKS with Fargate:** EKS (Kubernetes) phức tạp hơn ECS cho use case này. Kubernetes learning curve và operational overhead cao hơn ECS.

**❌ Đáp án D:**
- **EC2 Reserved Instances** cho static content: đắt và phức tạp nhất. S3 là lựa chọn tối ưu cho static website.
- **EKS with EC2:** Phức tạp nhất.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Static → S3. Container → ECS Fargate. DB → RDS. Đơn giản + rẻ nhất. Tránh EKS trừ khi cần Kubernetes."*
