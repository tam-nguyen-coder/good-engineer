# Question #346 - Topic 1

A company has an aging network-attached storage (NAS) array in its data center. The NAS array presents SMB shares and NFS shares to client workstations. The company does not want to purchase a new NAS array. The company also does not want to incur the cost of renewing the NAS array's support contract. Some of the data is accessed frequently, but much of the data is inactive. A solutions architect needs to implement a solution that migrates the data to Amazon S3, uses S3 Lifecycle policies, and maintains the same look and feel for the client workstations. The solutions architect has identified AWS Storage Gateway as part of the solution. Which type of storage gateway should the solutions architect provision to meet these requirements?

## Options

**A.** Volume Gateway

**B.** Tape Gateway

**C.** Amazon FSx File Gateway

**D.** Amazon S3 File Gateway

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Aging NAS (SMB + NFS), muốn migrate lên S3 + S3 Lifecycle policies. Keep same look and feel for clients.
- **Existing Resources:** NAS array (SMB + NFS shares).
- **Current Issue/Goal:** Migrate to S3, lifecycle policies, same client experience.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `SMB shares and NFS shares` | File-level protocol (SMB + NFS). |
| `S3 Lifecycle policies` | Cần dùng S3, không phải FSx. |
| `maintains the same look and feel` | S3 File Gateway presents S3 as file share (SMB/NFS). |
| `Amazon S3 File Gateway` | File gateway cho phép on-premises clients access S3 via SMB/NFS. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which type of storage gateway
- **Constraints:** SMB + NFS, S3 storage with lifecycle policies, same client experience

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- S3 File Gateway: serves S3 buckets as NFS/SMB file shares → client workstations không thấy thay đổi (cùng SMB/NFS).
- Dữ liệu được lưu trong S3 → có thể dùng S3 Lifecycle policies (move to IA, Glacier, etc.).
- Local cache cho frequently accessed data để giảm latency.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Volume Gateway: iSCSI block storage, không phải file-level (SMB/NFS).

**❌ Đáp án B:**
- Tape Gateway: virtual tape library (VTL), dùng cho backup, không phải file shares.

**❌ Đáp án C:**
- FSx File Gateway: dùng cho Amazon FSx for Windows File Server, không phải S3. Không thể dùng S3 Lifecycle policies.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"NAS (SMB/NFS) → S3 + Lifecycle → S3 File Gateway. Volume Gateway = block. FSx File Gateway = FSx, không phải S3."*
