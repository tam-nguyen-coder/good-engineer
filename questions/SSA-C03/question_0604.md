# Question #604 - Topic 1

A company will migrate 10 PB of data to Amazon S3 in 6 weeks. The current data center has a 500 Mbps uplink to the internet. Other on-premises applications share the uplink. The company can use 80% of the internet bandwidth for this one-time migration task. Which solution will meet these requirements?

## Options

**A.** Configure AWS DataSync to migrate the data to Amazon S3 and to automatically verify the data.

**B.** Use rsync to transfer the data directly to Amazon S3.

**C.** Use the AWS CLI and multiple copy processes to send the data directly to Amazon S3.

**D.** Order multiple AWS Snowball devices. Copy the data to the devices. Send the devices to AWS to copy the data to Amazon S3.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** 10 PB data, 6 weeks deadline, 500 Mbps uplink, 80% usable = 400 Mbps.
- **Existing Resources:** On-premises data center with limited bandwidth.
- **Current Issue/Goal:** One-time migration của 10 PB trong 6 tuần.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `10 PB` | Quá lớn để truyền qua internet trong 6 tuần với 400 Mbps (~181 TB tối đa). |
| `500 Mbps uplink` | Băng thông rất hạn chế. Tính: 400 Mbps × 6 tuần ≈ 181 TB << 10 PB. |
| `Snowball` | Offline transfer, mỗi device 80 TB, dùng nhiều devices để đạt 10 PB. |
| `6 weeks` | Thời gian gấp, Snowball là giải pháp khả thi duy nhất. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements (feasibility)
- **Constraints:** 10 PB in 6 weeks, 500 Mbps shared uplink (80% usable)

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- Tính toán băng thông: 500 Mbps × 80% = 400 Mbps. 400 Mbps = 50 MB/s.
- 50 MB/s × 86,400 s/ngày × 42 ngày = ~181 TB → Không đủ cho 10 PB.
- AWS Snowball Edge device có thể chứa ~80 TB mỗi device. Cần ~125 devices.
- Snowball là giải pháp offline physical transfer, không phụ thuộc bandwidth internet.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- DataSync dùng internet, bị giới hạn bởi 400 Mbps → không đủ băng thông cho 10 PB trong 6 tuần.

**❌ Đáp án B:**
- rsync qua internet cũng bị giới hạn băng thông như DataSync.

**❌ Đáp án C:**
- AWS CLI multiple copy processes vẫn bị giới hạn bởi 400 Mbps uplink.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Data lớn (10 PB) + bandwidth nhỏ (500 Mbps) → Snowball. Tính: 400 Mbps × 6 tuần ≈ 180 TB << 10 PB."*
