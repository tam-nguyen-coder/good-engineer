# Question #445 - Topic 1

A company is storing 700 terabytes of data on a large network-attached storage (NAS) system in its corporate data center. The company has a hybrid environment with a 10 Gbps AWS Direct Connect connection. After an audit from a regulator, the company has 90 days to move the data to the cloud. The company needs to move the data efficiently and without disruption. The company still needs to be able to access and update the data during the transfer window. Which solution will meet these requirements?

## Options

**A.** Create an AWS DataSync agent in the corporate data center. Create a data transfer task Start the transfer to an Amazon S3 bucket.

**B.** Back up the data to AWS Snowball Edge Storage Optimized devices. Ship the devices to an AWS data center. Mount a target Amazon S3 bucket on the on-premises file system.

**C.** Use rsync to copy the data directly from local storage to a designated Amazon S3 bucket over the Direct Connect connection.

**D.** Back up the data on tapes. Ship the tapes to an AWS data center. Mount a target Amazon S3 bucket on the on-premises file system.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** 700TB on NAS to AWS via 10Gbps Direct Connect. 90 days. No disruption, need access/update during transfer.
- **Existing Resources:** NAS, 10Gbps Direct Connect.
- **Current Issue/Goal:** Efficient migration without downtime.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `without disruption` | Online transfer, không gián đoạn truy cập. |
| `access and update the data during transfer` | DataSync: incremental sync, chỉ transfer changes. |
| `10 Gbps Direct Connect` | Đủ bandwidth: 700TB / 90 days ~ 0.9 Gbps. |
| `DataSync` | Managed data transfer, scheduling, incremental. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Migration
- **Constraints:** 700TB, 90 days, no disruption, live access during transfer

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- DataSync agent on-prem: reads NAS share, transfers to S3 efficiently.
- Incremental sync: initial full sync + subsequent changes.
- 10Gbps Direct Connect: đủ bandwidth (700TB/90d = ~740 MB/s, dễ dàng).
- No disruption: data trên NAS vẫn accessible.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Snowball Edge: 80TB/device → cần ~9 devices. Phải backup, ship, wait → mất thời gian, không real-time access.

**❌ Đáp án C:**
- rsync: không managed, không có scheduling, reporting, error handling như DataSync.

**❌ Đáp án D:**
- Tapes: offline, không thể access/update data trong lúc transfer. Rất chậm.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Large data + DC + timeline → DataSync (online, incremental). Snowball nếu không đủ bandwidth."*