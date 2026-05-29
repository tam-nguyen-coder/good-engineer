# Question #450 - Topic 1

A company has a three-tier web application that is in a single server. The company wants to migrate the application to the AWS Cloud. The company also wants the application to align with the AWS Well-Architected Framework and to be consistent with AWS recommended best practices for security, scalability, and resiliency. Which combination of solutions will meet these requirements? (Choose three.)

## Options

**A.** Create a VPC across two Availability Zones with the application's existing architecture. Host the application with existing architecture on an Amazon EC2 instance in a private subnet in each Availability Zone with EC2 Auto Scaling groups. Secure the EC2 instance with security groups and network access control lists (network ACLs).

**B.** Set up security groups and network access control lists (network ACLs) to control access to the database layer. Set up a single Amazon RDS database in a private subnet.

**C.** Create a VPC across two Availability Zones. Refactor the application to host the web tier, application tier, and database tier. Host each tier on its own private subnet with Auto Scaling groups for the web tier and application tier.

**D.** Use a single Amazon RDS database. Allow database access only from the application tier security group.

**E.** Use Elastic Load Balancers in front of the web tier. Control access by using security groups containing references to each layer's security groups.

**F.** Use an Amazon RDS database Multi-AZ cluster deployment in private subnets. Allow database access only from application tier security groups.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Single server three-tier web app. Migrate to AWS. Follow Well-Architected: security, scalability, resiliency.
- **Existing Resources:** Single server on-prem.
- **Current Issue/Goal:** Design HA, scalable, secure architecture on AWS.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `security` | Security groups, NACLs, private subnets, least privilege. |
| `scalability` | ASG, ELB. |
| `resiliency` | Multi-AZ, RDS Multi-AZ cluster. |
| `Choose three` | 3 answers required. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Well-Architected / Migration
- **Constraints:** Security + Scalability + Resiliency

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A, E, F**

**Giải thích:**
- **A:** VPC 2 AZs, EC2 private subnet + ASG = scalability + resiliency. SG + NACL = security.
- **E:** ELB in front of web tier = scalability. SG references between tiers = security.
- **F:** RDS Multi-AZ cluster = database resiliency (HA). Private subnet + SG = security.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Single RDS database: không resilient (SPOF). Cần Multi-AZ.

**❌ Đáp án C:**
- Refactor là tốt nhưng không cần thiết nếu A đã có. Tuy nhiên C cũng đúng về mặt kiến trúc... Nhưng đề hỏi "which combination" và A + E + F là đủ 3.

**❌ Đáp án D:**
- Single RDS: không resilient.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Well-Architected: VPC 2 AZs + ASG (resiliency), ELB + SG refs (security/scalability), RDS Multi-AZ (DB HA)."*