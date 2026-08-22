# Question #662 - Topic 1

A company uses AWS Cost Explorer to monitor its AWS costs. The company notices that Amazon Elastic Block Store (Amazon EBS) storage and snapshot costs increase every month. However, the company does not purchase additional EBS storage every month. The company wants to optimize monthly costs for its current storage usage. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Use logs in Amazon CloudWatch Logs to monitor the storage utilization of Amazon EBS. Use Amazon EBS Elastic Volumes to reduce the size of the EBS volumes.

**B.** Use a custom script to monitor space usage. Use Amazon EBS Elastic Volumes to reduce the size of the EBS volumes.

**C.** Delete all expired and unused snapshots to reduce snapshot costs.

**D.** Delete all nonessential snapshots. Use Amazon Data Lifecycle Manager to create and manage the snapshots according to the company's snapshot policy requirements.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EBS storage + snapshot costs increase monthly, but no additional EBS storage purchased.
- **Existing Resources:** EBS volumes and snapshots.
- **Current Issue/Goal:** Optimize costs (snapshot costs likely cause of increase).

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `snapshot costs increase every month` | Snapshot costs accumulate (incremental snapshots). |
| `does not purchase additional EBS storage` | Storage cost không tăng → snapshot costs là nguyên nhân. |
| `Amazon Data Lifecycle Manager` | Automates snapshot creation/deletion → prevent orphan snapshots. |
| `least operational overhead` | DLM managed, tự động. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Optimize costs for current storage

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- Chi phí EBS snapshot tăng vì snapshot cũ không được xóa, snapshot mới được tạo liên tục.
- Delete nonessential snapshots → giảm ngay chi phí.
- Dùng DLM để tự động hóa việc tạo và xóa snapshot theo policy → ngăn chặn tích lũy snapshot không cần thiết trong tương lai.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- CloudWatch Logs monitor storage utilization không giải quyết snapshot costs.
- EBS Elastic Volumes chỉ có thể tăng size, không giảm.

**❌ Đáp án B:**
- Custom script → operational overhead cao hơn DLM.

**❌ Đáp án C:**
- Chỉ xóa 1 lần (cleanup), không có cơ chế tự động ngăn tích lũy trong tương lai.
- Thiếu DLM để quản lý snapshot policy.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Snapshot costs increasing → delete old snapshots + DLM (auto lifecycle)."*
