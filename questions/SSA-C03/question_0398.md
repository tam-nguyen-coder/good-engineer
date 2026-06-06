# Question #398 - Topic 1

A company needs to transfer 600 TB of data from its on-premises network-attached storage (NAS) system to the AWS Cloud. The data transfer must be complete within 2 weeks. The data is sensitive and must be encrypted in transit. The company's internet connection can support an upload speed of 100 Mbps. Which solution meets these requirements MOST cost-effectively?

## Options

**A.** Use Amazon S3 multi-part upload functionality to transfer the files over HTTPS.

**B.** Create a VPN connection between the on-premises NAS system and the nearest AWS Region. Transfer the data over the VPN connection.

**C.** Use the AWS Snow Family console to order several AWS Snowball Edge Storage Optimized devices. Use the devices to transfer the data to Amazon S3.

**D.** Set up a 10 Gbps AWS Direct Connect connection between the company location and the nearest AWS Region. Transfer the data over a VPN connection into the Region to store the data in Amazon S3.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** 600 TB transfer to AWS within 2 weeks, 100 Mbps internet, sensitive data, encrypted in transit. Most cost-effective.
- **Existing Resources:** On-premises NAS, 100 Mbps internet.
- **Current Issue/Goal:** 600 TB in 14 days > bandwidth.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `600 TB` | Very large data volume. |
| `100 Mbps` | Max ~14.5 TB in 2 weeks → không đủ cho 600 TB. |
| `2 weeks` | Need faster transfer → offline physical device. |
| `Snowball Edge Storage Optimized` | 80 TB usable per device → ~8 devices for 600 TB. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective
- **Constraints:** 600 TB, 2 weeks, 100 Mbps, encrypted

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- 100 Mbps × 86400 × 14 = ~14.5 TB tối đa → không thể transfer 600 TB online.
- Snowball Edge Storage Optimized: 80 TB usable per device → ~8 devices, ship to AWS.
- Encrypted at rest (hardware), encrypted in transit (HTTPS when importing to S3).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Multipart upload over 100 Mbps: chỉ được ~14.5 TB trong 2 tuần → không đủ.

**❌ Đáp án B:**
- VPN qua 100 Mbps: tương tự, không đủ bandwidth.

**❌ Đáp án D:**
- Direct Connect 10 Gbps: có thể đủ, nhưng chi phí setup và monthly fee cao hơn Snowball cho one-time transfer. Snowball cost-effective hơn.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"600 TB in 2 weeks with 100 Mbps → Snowball Edge (offline, physical). Online transfer không đủ bandwidth."*
