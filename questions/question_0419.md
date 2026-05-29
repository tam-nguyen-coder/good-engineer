# Question #419 - Topic 1

A company uses AWS Organizations with all features enabled and runs multiple Amazon EC2 workloads in the ap-southeast-2 Region. The company has a service control policy (SCP) that prevents any resources from being created in any other Region. A security policy requires the company to encrypt all data at rest. An audit discovers that employees have created Amazon Elastic Block Store (Amazon EBS) volumes for EC2 instances without encrypting the volumes. The company wants any new EC2 instances that any IAM user or root user launches in ap-southeast-2 to use encrypted EBS volumes. The company wants a solution that will have minimal effect on employees who create EBS volumes. Which combination of steps will meet these requirements? (Choose two.)

## Options

**A.** In the Amazon EC2 console, select the EBS encryption account attribute and define a default encryption key.

**B.** Create an IAM permission boundary. Attach the permission boundary to the root organizational unit (OU). Define the boundary to deny the ec2:CreateVolume action when the ec2:Encrypted condition equals false.

**C.** Create an SCP. Attach the SCP to the root organizational unit (OU). Define the SCP to deny the ec2:CreateVolume action whenthe ec2:Encrypted condition equals false.

**D.** Update the IAM policies for each account to deny the ec2:CreateVolume action when the ec2:Encrypted condition equals false.

**E.** In the Organizations management account, specify the Default EBS volume encryption setting.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Organizations multi-account. SCP cấm tạo resources ngoài ap-southeast-2. Audit phát hiện EBS volumes không được encrypt. Cần encrypt mọi volume mới.
- **Existing Resources:** AWS Organizations, SCP (region restriction), EC2, EBS.
- **Current Issue/Goal:** Enforce EBS encryption for new volumes. Minimal effect on employees.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `minimal effect on employees` | Default encryption: tự động, không cần employee nhớ encrypt. |
| `EBS encryption account attribute` | Default encryption key ở account level. |
| `SCP` | Deny CreateVolume nếu không encrypted. |
| `Choose two` | 2 answers required. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Security / Governance
- **Constraints:** All new EBS volumes encrypted, minimal employee impact

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A, C**

**Giải thích:**
- **A:** EBS encryption by default (account attribute): tự động encrypt volumes mới → không cần employee can thiệp.
- **C:** SCP deny ec2:CreateVolume khi ec2:Encrypted = false → enforce kể cả khi ai đó cố tình tắt default encryption.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Permission boundary: gán vào IAM user/role, không thể attach vào OU.

**❌ Đáp án D:**
- Update IAM policies per account: nhiều công sức, không "minimal effect".

**❌ Đáp án E:**
- Không có tính năng "Default EBS volume encryption" ở cấp Organizations management account.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"EBS encrypt enforcement: default encryption (account attribute) + SCP deny non-encrypted."*