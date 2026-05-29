# Question #479 - Topic 1

A company is making a prototype of the infrastructure for its new website by manually provisioning the necessary infrastructure. This infrastructure includes an Auto Scaling group, an Application Load Balancer and an Amazon RDS database. After the configuration has been thoroughly validated, the company wants the capability to immediately deploy the infrastructure for development and production use in two Availability Zones in an automated fashion. What should a solutions architect recommend to meet these requirements?

## Options

**A.** Use AWS Systems Manager to replicate and provision the prototype infrastructure in two Availability Zones

**B.** Define the infrastructure as a template by using the prototype infrastructure as a guide. Deploy the infrastructure with AWS CloudFormation.

**C.** Use AWS Config to record the inventory of resources that are used in the prototype infrastructure. Use AWS Config to deploy the prototype infrastructure into two Availability Zones.

**D.** Use AWS Elastic Beanstalk and configure it to use an automated reference to the prototype infrastructure to automatically deploy new environments in two Availability Zones.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Đã manually prototype infra (ASG, ALB, RDS). Cần automated deploy cho dev và production ở 2 AZs.
- **Existing Resources:** Manual prototype infra.
- **Current Issue/Goal:** Infrastructure as Code, automated deployment.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `manually provisioning` | Hiện tại manual, muốn automated. |
| `automated fashion` | Infrastructure as Code (IaC). |
| `immediately deploy` | CloudFormation: deploy nhanh, repeatable, consistent. |
| `development and production` | Multi-environment: dev + prod, cùng template. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Automated infrastructure deployment
- **Constraints:** Based on validated prototype, dev + prod, 2 AZs

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- CloudFormation: Infrastructure as Code, define template từ prototype infrastructure.
- Deploy nhanh, consistent, repeatable → dev và prod dùng chung/cùng template.
- Hỗ trợ parameters để customize giữa môi trường.
- 2 AZs dễ dàng cấu hình trong template.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Systems Manager: quản lý và patching instances, không phải Infrastructure as Code deployment tool.
- Không thể "provision infrastructure" từ prototype.

**❌ Đáp án C:**
- AWS Config: ghi nhận resource inventory và compliance, không phải deployment tool.
- Không thể deploy infrastructure.

**❌ Đáp án D:**
- Elastic Beanstalk: PaaS, tự động quản lý infra. Tuy nhiên, không thể "reference prototype infrastructure" - Elastic Beanstalk có platform riêng.
- Dùng Elastic Beanstalk có thể giới hạn customizability so với CloudFormation.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Auto deploy infra từ prototype → CloudFormation (IaC). Systems Manager = quản lý, Config = inventory, BeanStalk = PaaS."*
