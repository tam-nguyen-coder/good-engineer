# Question #50 - Topic 1

A company has a production workload that runs on 1,000 Amazon EC2 Linux instances. The workload is powered by third-party software. The company needs to patch the third-party software on all EC2 instances as quickly as possible to remediate a critical security vulnerability. What should a solutions architect do to meet these requirements?

## Options

**A.** Create an AWS Lambda function to apply the patch to all EC2 instances.

**B.** Configure AWS Systems Manager Patch Manager to apply the patch to all EC2 instances.

**C.** Schedule an AWS Systems Manager maintenance window to apply the patch to all EC2 instances.

**D.** Use AWS Systems Manager Run Command to run a custom command that applies the patch to all EC2 instances.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** 1,000 EC2 Linux instances chạy third-party software, cần patch critical security vulnerability.
- **Existing Resources:** 1,000 EC2 Linux instances.
- **Current Issue/Goal:** Patch càng nhanh càng tốt cho tất cả instances.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `third-party software` | Không phải OS patch — cần custom command |
| `as quickly as possible` | Hành động ngay lập tức, không schedule |
| `critical security vulnerability` | Khẩn cấp, cần execute ngay |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most operational efficient / Fastest execution
- **Constraints:** 1,000 instances, third-party software (không phải OS patch mặc định)

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **AWS Systems Manager Run Command** cho phép chạy custom command trên nhiều EC2 instances **ngay lập tức** (ad-hoc), không cần schedule.
- Run Command phù hợp cho third-party software vì có thể chạy bất kỳ script/command nào.
- **"As quickly as possible"** → Run Command là lựa chọn nhanh nhất vì execute tức thời trên 1,000 instances (dùng target selection).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Lambda không có native EC2 agent để chạy command trên instances.
- Phải setup thêm (SSM Agent + batching) — phức tạp và chậm hơn Run Command.

**❌ Đáp án B:**
- **Patch Manager** chỉ hỗ trợ OS patching (Amazon Linux, Ubuntu, Windows Update...), **không hỗ trợ third-party software**.
- Patch Manager dùng predefined patch baselines, không dùng cho custom software.

**❌ Đáp án C:**
- **Maintenance Window** là scheduled, không phải "as quickly as possible".
- Maintenance Window phải đợi đến cửa sổ định sẵn — không phù hợp cho critical vulnerability cần patch ngay.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Patch Manager = OS patching, Run Command = custom software patching (ad-hoc, immediate)"*
