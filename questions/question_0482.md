# Question #482 - Topic 1

A company wants to migrate 100 GB of historical data from an on-premises location to an Amazon S3 bucket. The company has a 100 megabits per second (Mbps) internet connection on premises. The company needs to encrypt the data in transit to the S3 bucket. The company will store new data directly in Amazon S3. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Use the s3 sync command in the AWS CLI to move the data directly to an S3 bucket

**B.** Use AWS DataSync to migrate the data from the on-premises location to an S3 bucket

**C.** Use AWS Snowball to move the data to an S3 bucket

**D.** Set up an IPsec VPN from the on-premises location to AWS. Use the s3 cp command in the AWS CLI to move the data directly to an S3 bucket

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Migrate 100 GB historical data on-prem → S3. Internet 100 Mbps. Cần encrypt in transit. New data sẽ được store trực tiếp vào S3 sau này.
- **Existing Resources:** On-premises data, 100 Mbps internet.
- **Current Issue/Goal:** Migration 100 GB với least operational overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `100 GB` | Dung lượng nhỏ, không cần Snowball (Snowball phù hợp >10TB). |
| `100 Mbps` | ~12.5 MB/s. 100 GB = ~8000s ≈ 2.2 giờ. Online transfer khả thi. |
| `encrypt the data in transit` | AWS CLI s3 sync dùng HTTPS → encryption in transit tự động. |
| `least operational overhead` | Càng ít component càng tốt. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead
- **Constraints:** Encrypt in transit, dung lượng 100 GB, băng thông 100 Mbps.

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- `aws s3 sync` dùng HTTPS → encryption in transit tự động, không cần cấu hình thêm.
- 100 GB qua 100 Mbps là feasible (~2-3 giờ).
- Không cần cài đặt agent, không cần VPN, không cần hardware.
- Operational overhead thấp nhất: chỉ cần cài AWS CLI và chạy 1 command.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- **AWS DataSync:** Cần deploy DataSync agent on-premises → operational overhead cao hơn CLI.

**❌ Đáp án C:**
- **AWS Snowball:** Overkill cho 100 GB. Snowball phù hợp cho >10 TB data. Thời gian ship hardware lâu hơn nhiều so với online transfer.

**❌ Đáp án D:**
- **IPsec VPN + s3 cp:** Cần setup và maintain VPN connection → operational overhead cao hơn, không cần thiết vì CLI đã dùng HTTPS.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"100 GB = small → CLI sync (HTTPS) đủ. Snowball chỉ khi >10TB hoặc bandwidth thấp. DataSync = agent = overhead."*
