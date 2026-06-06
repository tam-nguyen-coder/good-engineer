# Question #583 - Topic 1

A company has 5 PB of archived data on physical tapes. The company needs to preserve the data on the tapes for another 10 years for compliance purposes. The company wants to migrate to AWS in the next 6 months. The data center that stores the tapes has a 1 Gbps uplink internet connectivity. Which solution will meet these requirements MOST cost-effectively?

## Options

**A.** Read the data from the tapes on premises. Stage the data in a local NFS storage. Use AWS DataSync to migrate the data to Amazon S3 Glacier Flexible Retrieval.

**B.** Use an on-premises backup application to read the data from the tapes and to write directly to Amazon S3 Glacier Deep Archive.

**C.** Order multiple AWS Snowball devices that have Tape Gateway. Copy the physical tapes to virtual tapes in Snowball. Ship the Snowball devices to AWS. Create a lifecycle policy to move the tapes to Amazon S3 Glacier Deep Archive.

**D.** Configure an on-premises Tape Gateway. Create virtual tapes in the AWS Cloud. Use backup software to copy the physical tape to the virtual tape.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** 5 PB archived data on physical tapes, cần migrate to AWS trong 6 tháng, data center có 1 Gbps uplink.
- **Existing Resources:** Physical tapes, 1 Gbps internet.
- **Current Issue/Goal:** Migrate 5 PB tapes to AWS cost-effectively.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `5 PB` | Rất lớn. 1 Gbps uplink = ~10.8 TB/ngày → 5 PB sẽ mất ~463 ngày > 6 tháng. |
| `physical tapes` | Cần Tape Gateway approach. |
| `Snowball` | Offline transfer: ship physical device. |
| `Tape Gateway` | Virtual tape library trên AWS. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effectively
- **Constraints:** 5 PB, 6 months, 1 Gbps uplink, compliance 10 years

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- 5 PB qua 1 Gbps internet sẽ mất > 6 tháng → cần offline transfer (Snowball).
- Snowball with Tape Gateway: copy tapes to virtual tapes on Snowball, ship to AWS.
- Lifecycle policy → Glacier Deep Archive (cheapest storage cho archive 10 năm).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- DataSync qua 1 Gbps: không đủ băng thông, 5 PB sẽ mất > 6 tháng.

**❌ Đáp án B:**
- Direct upload to Glacier Deep Archive qua 1 Gbps: quá chậm, không kịp 6 tháng.

**❌ Đáp án D:**
- Tape Gateway on-prem + backup software: vẫn upload qua internet → chậm.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"5 PB + 1 Gbps = too slow for 6 months → Snowball (offline). Tape Gateway + Snowball → Glacier Deep Archive."*
