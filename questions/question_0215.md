# Question #215 - Topic 1

A company has 700 TB of backup data stored in network attached storage (NAS) in its data center. This backup data need to be accessible for infrequent regulatory requests and must be retained 7 years. The company has decided to migrate this backup data from its data center to AWS. The migration must be complete within 1 month. The company has 500 Mbps of dedicated bandwidth on its public internet connection available for data transfer. What should a solutions architect do to migrate and store the data at the LOWEST cost?

## Options

**A.** Order AWS Snowball devices to transfer the data. Use a lifecycle policy to transition the files to Amazon S3 Glacier Deep Archive.

**B.** Deploy a VPN connection between the data center and Amazon VPC. Use the AWS CLI to copy the data from on premises to Amazon S3 Glacier.

**C.** Provision a 500 Mbps AWS Direct Connect connection and transfer the data to Amazon S3. Use a lifecycle policy to transition the files to Amazon S3 Glacier Deep Archive.

**D.** Use AWS DataSync to transfer the data and deploy a DataSync agent on premises. Use the DataSync task to copy files from the on-premises NAS storage to Amazon S3 Glacier.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** 700TB backup NAS, infrequent access, retain 7 years. Must migrate in 1 month. 500Mbps bandwidth.
- **Existing Resources:** NAS storage, 500Mbps internet.
- **Current Issue/Goal:** Fast migration + lowest cost storage.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `700 TB` | Large data — **Snowball** needed |
| `within 1 month` | 500Mbps quá chậm cho 700TB (cần ~133 ngày) |
| `infrequent regulatory requests` | **Glacier Deep Archive** (cheapest) |
| `lowest cost` | Snowball + Glacier Deep Archive |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Migration / Storage
- **Constraints:** 1 month, lowest cost

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **Snowball devices** — physical transfer, vận chuyển 700TB trong vài ngày.
- **S3 Glacier Deep Archive** — cheapest storage class ($1/TB/month), phù hợp cho 7-year retention.
- Lifecycle policy tự động transition từ S3 Standard → Glacier Deep Archive.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- VPN + CLI — 500Mbps không đủ băng thông cho 700TB trong 1 tháng (cần ~133 ngày).

**❌ Đáp án C:**
- Direct Connect 500Mbps — vẫn không đủ băng thông.

**❌ Đáp án D:**
- DataSync — vẫn bị giới hạn bởi băng thông, không đạt 1 month deadline.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Snowball = large data transfer (TB→PB). 500Mbps for 700TB = too slow. Glacier Deep Archive = cheapest"*
