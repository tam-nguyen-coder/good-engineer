# Question #605 - Topic 1

A company has several on-premises Internet Small Computer Systems Interface (ISCSI) network storage servers. The company wants to reduce the number of these servers by moving to the AWS Cloud. A solutions architect must provide low-latency access to frequently used data and reduce the dependency on on-premises servers with a minimal number of infrastructure changes. Which solution will meet these requirements?

## Options

**A.** Deploy an Amazon S3 File Gateway.

**B.** Deploy Amazon Elastic Block Store (Amazon EBS) storage with backups to Amazon S3.

**C.** Deploy an AWS Storage Gateway volume gateway that is configured with stored volumes.

**D.** Deploy an AWS Storage Gateway volume gateway that is configured with cached volumes.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** On-premises iSCSI storage servers → cần move lên AWS Cloud, giảm phụ thuộc on-prem, low-latency cho frequently used data, minimal infrastructure changes.
- **Existing Resources:** On-premises iSCSI network storage servers.
- **Current Issue/Goal:** Hybrid cloud storage, low-latency access to hot data, giảm on-prem footprint.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `iSCSI` | Block storage protocol → Volume Gateway (không phải File Gateway). |
| `low-latency access to frequently used data` | Cached volumes: frequently accessed data cached locally, primary data in AWS. |
| `reduce dependency on on-premises` | Muốn lưu primary data trên AWS, không giữ local. |
| `minimal infrastructure changes` | Volume Gateway hỗ trợ iSCSI, không cần thay đổi ứng dụng. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements
- **Constraints:** iSCSI protocol, low-latency for hot data, reduce on-prem dependency, minimal changes

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- Volume Gateway với cached volumes: primary data được lưu trên AWS (S3), frequently accessed data được cache locally → low-latency.
- Hỗ trợ iSCSI protocol → tương thích với existing infrastructure, minimal changes.
- Giảm dependency on on-premises vì primary data ở AWS, local chỉ chứa cache.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- S3 File Gateway hỗ trợ NFS/SMB, không hỗ trợ iSCSI.

**❌ Đáp án B:**
- EBS là block storage nhưng không thể truy cập từ on-premises dễ dàng qua iSCSI.

**❌ Đáp án C:**
- Stored volumes: primary data lưu on-prem, async backup to AWS → không giảm dependency on on-prem.
- Cần nhiều dung lượng local để chứa toàn bộ dữ liệu.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"iSCSI → Volume Gateway. Cached = primary ở AWS (giảm on-prem). Stored = primary ở on-prem (không giảm)."*
