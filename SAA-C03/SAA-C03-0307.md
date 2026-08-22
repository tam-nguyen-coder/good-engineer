# Question #307 - Topic 1

A company that primarily runs its application servers on premises has decided to migrate to AWS. The company wants to minimize its need to scale its Internet Small Computer Systems Interface (iSCSI) storage on premises. The company wants only its recently accessed data to remain stored locally. Which AWS solution should the company use to meet these requirements?

## Options

**A.** Amazon S3 File Gateway

**B.** AWS Storage Gateway Tape Gateway

**C.** AWS Storage Gateway Volume Gateway stored volumes

**D.** AWS Storage Gateway Volume Gateway cached volumes

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** On-premises app servers, muốn minimize iSCSI storage scaling. Chỉ keep recently accessed data locally.
- **Existing Resources:** On-premises iSCSI storage.
- **Current Issue/Goal:** Local cache chỉ cho recently accessed data, phần còn lại trên AWS.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `iSCSI storage` | Volume gateway dùng iSCSI protocol (block storage). |
| `only its recently accessed data to remain stored locally` | Chỉ cache dữ liệu thường dùng → cached volumes (primary data ở AWS). |
| `cached volumes` | Lưu primary data trong S3, cache frequently accessed data on-premises. |
| `stored volumes` | Lưu toàn bộ data on-premises, async backup lên S3. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which solution meets requirements
- **Constraints:** iSCSI, minimize local storage, recently accessed data only locally

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- Volume Gateway cached volumes: primary data được lưu trong S3, chỉ cache dữ liệu thường xuyên truy cập (recently accessed) on-premises.
- Sử dụng iSCSI protocol → compatible với on-premises app servers.
- Minimize nhu cầu mở rộng iSCSI storage on-premises (vì dữ liệu chính ở AWS).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- S3 File Gateway dùng SMB/NFS, không phải iSCSI.

**❌ Đáp án B:**
- Tape Gateway dùng cho virtual tape library (VTL) backup, không phải iSCSI volumes.

**❌ Đáp án C:**
- Stored volumes lưu toàn bộ data on-premises → vẫn cần mở rộng local storage, không đáp ứng yêu cầu minimize.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"iSCSI + recently accessed data locally → Volume Gateway cached volumes (primary in S3, cache on-prem). Stored = all local."*
