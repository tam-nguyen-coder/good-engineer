# Question #599 - Topic 1

A company wants to use Amazon Elastic Container Service (Amazon ECS) clusters and Amazon RDS DB instances to build and run a payment processing application. The company will run the application in its on-premises data center for compliance purposes. A solutions architect wants to use AWS Outposts as part of the solution. The solutions architect is working with the company's operational team to build the application. Which activities are the responsibility of the company's operational team? (Choose three.)

## Options

**A.** Providing resilient power and network connectivity to the Outposts racks

**B.** Managing the virtualization hypervisor, storage systems, and the AWS services that run on Outposts

**C.** Physical security and access controls of the data center environment

**D.** Availability of the Outposts infrastructure including the power supplies, servers, and networking equipment within the Outposts racks

**E.** Physical maintenance of Outposts components

**F.** Providing extra capacity for Amazon ECS clusters to mitigate server failures and maintenance events

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Payment processing app using ECS + RDS on AWS Outposts trong on-prem data center. Xác định responsibilities của operational team (customer).
- **Existing Resources:** AWS Outposts.
- **Current Issue/Goal:** Phân biệt AWS responsibility vs Customer responsibility trong Outposts.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `AWS Outposts` | AWS quản lý hardware, customer quản lý facility. |
| `Shared Responsibility Model` | AWS: hardware maintenance, hypervisor, patching. Customer: physical environment, power, network to rack, security. |
| `operational team` | Customer's responsibility. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Responsibility (Choose three)
- **Constraints:** Outposts on-prem, compliance

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A, C, F**

**Giải thích:**
- **A:** Customer chịu trách nhiệm cấp điện và network connectivity đến Outposts racks (facility responsibility).
- **C:** Customer chịu trách nhiệm physical security và access control của data center (AWS không kiểm soát facility của customer).
- **F:** Customer phải cung cấp extra capacity cho ECS clusters để mitigate server failures (trách nhiệm ứng dụng/capacity planning).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- AWS quản lý virtualization hypervisor, storage systems, và AWS services trên Outposts (AWS responsibility).

**❌ Đáp án D:**
- AWS chịu trách nhiệm availability của Outposts infrastructure (power supplies, servers, networking equipment trong rack).

**❌ Đáp án E:**
- AWS chịu trách nhiệm physical maintenance của Outposts components (AWS sẽ sửa chữa/thay thế hardware).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Customer responsibility = what's outside the rack (power, network, security). AWS responsibility = what's inside the rack (hardware, hypervisor, maintenance)."*
