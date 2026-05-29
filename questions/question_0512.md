# Question #512 - Topic 1

A company uses AWS Organizations with resources tagged by account. The company also uses AWS Backup to back up its AWS infrastructure resources. The company needs to back up all AWS resources. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Use AWS Config to identify all untagged resources. Tag the identified resources programmatically. Use tags in the backup plan.

**B.** Use AWS Config to identify all resources that are not running. Add those resources to the backup vault.

**C.** Require all AWS account owners to review their resources to identify the resources that need to be backed up.

**D.** Use Amazon Inspector to identify all noncompliant resources.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty dùng AWS Organizations, resources tagged by account. Dùng AWS Backup. Cần backup tất cả resources.
- **Existing Resources:** AWS Backup, AWS Organizations, tagged resources.
- **Current Issue/Goal:** Đảm bảo tất cả resources được backup, operational overhead thấp nhất.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `resources tagged by account` | Dùng tags để quản lý backup. |
| `back up all AWS resources` | Cần phát hiện resources chưa được tag/backup. |
| `AWS Config` | Dùng rules để phát hiện resources không compliant (không có tag backup). |
| `least operational overhead` | Tự động hóa tối đa. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Backup all resources, Organizations, tag-based backup

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- AWS Backup dùng tags để xác định resources cần backup. Nếu resources chưa có tag backup → sẽ không được backup.
- AWS Config rules (ví dụ: `required-tags`) phát hiện resources không có tag backup → dùng AWS Systems Manager Automation hoặc Lambda để auto-tag.
- Khi resources được tag, AWS Backup tự động nhặt và backup → hoàn toàn tự động.
- Đây là giải pháp tự động hóa phát hiện + khắc phục để đảm bảo coverage.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- AWS Config xác định resources "not running" không liên quan đến backup coverage. Mục đích của Config là compliance, không phải runtime status.
- "Add those resources to backup vault" không phải cách AWS Backup hoạt động.

**❌ Đáp án C:**
- Manual review bởi account owners → operational overhead cao nhất. Không tự động.

**❌ Đáp án D:**
- Amazon Inspector là vulnerability management service, dùng để scan security vulnerabilities. Không liên quan đến backup compliance.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Backup all resources → AWS Config phát hiện untagged resources + auto-tag → AWS Backup dùng tags. Inspector = security scan, không phải backup."*
