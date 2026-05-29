# Question #331 - Topic 1

A company must migrate 20 TB of data from a data center to the AWS Cloud within 30 days. The company's network bandwidth is limited to 15 Mbps and cannot exceed 70% utilization. What should a solutions architect do to meet these requirements?

## Options

**A.** Use AWS Snowball.

**B.** Use AWS DataSync.

**C.** Use a secure VPN connection.

**D.** Use Amazon S3 Transfer Acceleration.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** 20 TB data migration, 30-day deadline, 15 Mbps bandwidth limited to 70% utilization.
- **Existing Resources:** On-premises data center, limited bandwidth.
- **Current Issue/Goal:** Migrate 20 TB trong 30 ngày với bandwidth constraint.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `15 Mbps, cannot exceed 70%` | Available bandwidth ~10.5 Mbps → max ~3.4 TB in 30 days qua network (20 TB > 3.4 TB → không đủ). |
| `Snowball` | Offline physical device để transfer large data when network is too slow. |
| `30 days` | Snowball có thể ship và hoàn thành trong vài ngày. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which solution meets requirements
- **Constraints:** 20 TB, 30 days, 15 Mbps @ 70% utilization

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- 10.5 Mbps * 86400 * 30 = ~3.4 TB có thể transfer qua network trong 30 ngày → không đủ cho 20 TB.
- AWS Snowball là physical device: copy 20 TB vào Snowball, ship về AWS. Hoàn thành trong vài ngày, không phụ thuộc bandwidth.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- DataSync transfer online → không đủ bandwidth (chỉ ~3.4 TB tối đa).

**❌ Đáp án C:**
- VPN transfer online → không đủ bandwidth.

**❌ Đáp án D:**
- S3 Transfer Acceleration cải thiện upload speed nhưng không đủ cho 20 TB trong 30 ngày với 10.5 Mbps.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"20 TB > 3.4 TB (max online) → Snowball offline. DataSync/VPN/TA online không đủ bandwidth."*
