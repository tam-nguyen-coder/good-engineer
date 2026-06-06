# Question #64 - Topic 1

A company has more than 5 TB of file data on Windows file servers that run on premises. Users and applications interact with the data each day. The company is moving its Windows workloads to AWS. As the company continues this process, the company requires access to AWS and on- premises file storage with minimum latency. The company needs a solution that minimizes operational overhead and requires no significant changes to the existing file access patterns. The company uses an AWS Site-to-Site VPN connection for connectivity to AWS. What should a solutions architect do to meet these requirements?

## Options

**A.** Deploy and configure Amazon FSx for Windows File Server on AWS. Move the on-premises file data to FSx for Windows File Server. Reconfigure the workloads to use FSx for Windows File Server on AWS.

**B.** Deploy and configure an Amazon S3 File Gateway on premises. Move the on-premises file data to the S3 File Gateway. Reconfigure the on- premises workloads and the cloud workloads to use the S3 File Gateway.

**C.** Deploy and configure an Amazon S3 File Gateway on premises. Move the on-premises file data to Amazon S3. Reconfigure the workloads to use either Amazon S3 directly or the S3 File Gateway. depending on each workload's location.

**D.** Deploy and configure Amazon FSx for Windows File Server on AWS. Deploy and configure an Amazon FSx File Gateway on premises. Move the on-premises file data to the FSx File Gateway. Configure the cloud workloads to use FSx for Windows File Server on AWS. Configure the on- premises workloads to use the FSx File Gateway.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** 5TB+ Windows file servers on-prem, hybrid migration to AWS.
- **Existing Resources:** Windows file servers on-prem, Site-to-Site VPN.
- **Current Issue/Goal:** Min latency, min operational overhead, no changes to access patterns, hybrid access.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `Windows file servers` | SMB protocol, cần Windows-native solution |
| `no significant changes to existing file access patterns` | Giữ nguyên SMB file share |
| `minimum latency` | Cache local trên on-prem |
| `Site-to-Site VPN` | Kết nối hybrid sẵn có |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Hybrid storage + Minimal changes
- **Constraints:** Windows, SMB, hybrid access, low latency

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **FSx for Windows File Server** trên AWS — managed Windows file server cho cloud workloads.
- **FSx File Gateway** on-prem — cache local cho on-prem workloads, đồng bộ với FSx qua VPN.
- Cả on-prem và cloud workloads đều dùng SMB — **không thay đổi access pattern**.
- FSx File Gateway caches data locally → **minimum latency** cho on-prem users.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Chỉ có FSx trên AWS — on-prem workloads không có local cache, latency cao qua VPN.

**❌ Đáp án B:**
- S3 File Gateway dùng S3 backend, không native Windows file server (thiếu Windows ACLs, AD integration).

**❌ Đáp án C:**
- Tương tự B — phải reconfigure workloads, S3 khác access pattern so với Windows file shares.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"FSx for Windows = SMB + AD. FSx File Gateway = local cache cho on-prem. Hybrid solution cho Windows"*
