# Question #496 - Topic 1

A company uses on-premises servers to host its applications. The company is running out of storage capacity. The applications use both block storage and NFS storage. The company needs a high-performing solution that supports local caching without re-architecting its existing applications. Which combination of actions should a solutions architect take to meet these requirements? (Choose two.)

## Options

**A.** Mount Amazon S3 as a file system to the on-premises servers.

**B.** Deploy an AWS Storage Gateway file gateway to replace NFS storage.

**C.** Deploy AWS Snowball Edge to provision NFS mounts to on-premises servers.

**D.** Deploy an AWS Storage Gateway volume gateway to replace the block storage.

**E.** Deploy Amazon Elastic File System (Amazon EFS) volumes and mount them to on-premises servers.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** On-premises servers hết storage. Apps dùng cả block storage và NFS storage. Cần local caching, không re-architect.
- **Existing Resources:** On-premises servers, block storage, NFS storage.
- **Current Issue/Goal:** Thêm storage cho both block và NFS, có local caching, không thay đổi app.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `block storage and NFS storage` | Cần 2 loại storage. |
| `local caching` | Storage Gateway có local cache để giảm latency. |
| `without re-architecting` | Storage Gateway exposed as iSCSI (block) hoặc NFS (file) → app không cần thay đổi. |
| `choose two` | 2 đáp án đúng. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Hybrid storage (choose 2)
- **Constraints:** Both block + NFS, local caching, no re-architecture.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B và D**

**Giải thích:**
- **B. File Gateway:** Expose S3 storage as NFS mount → thay thế NFS storage. Có local caching để tăng performance.
- **D. Volume Gateway:** Expose S3/EBS storage as iSCSI volumes → thay thế block storage. Có local caching (stored volumes hoặc cached volumes).
- Cả hai đều **không cần thay đổi ứng dụng** - ứng dụng tiếp tục dùng NFS/iSCSI như cũ.
- Cả hai đều support **local caching** để đảm bảo high performance.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Mount S3 as file system (S3FS): không có local caching built-in. Cần third-party tools, không phải giải pháp AWS managed.

**❌ Đáp án C:**
- **Snowball Edge:** Thiết bị tạm thời, không phải giải pháp storage lâu dài cho on-premises.

**❌ Đáp án E:**
- **EFS:** Cần kết nối network (VPN/Direct Connect) để mount từ on-premises. Không có local caching tự động trên on-prem (EFS có data consistency qua network).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Storage Gateway: File Gateway = NFS, Volume Gateway = block iSCSI. Cả hai đều local cache, không re-architect."*
