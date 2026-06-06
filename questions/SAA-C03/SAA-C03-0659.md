# Question #659 - Topic 1

A company is relocating its data center and wants to securely transfer 50 TB of data to AWS within 2 weeks. The existing data center has a Site-to- Site VPN connection to AWS that is 90% utilized. Which AWS service should a solutions architect use to meet these requirements?

## Options

**A.** AWS DataSync with a VPC endpoint

**B.** AWS Direct Connect

**C.** AWS Snowball Edge Storage Optimized

**D.** AWS Storage Gateway

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Relocate data center, transfer 50TB to AWS within 2 weeks. Existing VPN at 90% utilization.
- **Existing Resources:** Site-to-Site VPN (90% utilized).
- **Current Issue/Goal:** Transfer large data quickly when network is almost saturated.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `90% utilized` | VPN almost saturated → không thể dùng thêm bandwidth cho 50TB. |
| `50 TB within 2 weeks` | 50TB over VPN at 10% remaining ≈ ~3.7 Mbps → quá chậm (mất ~3+ năm). |
| `AWS Snowball Edge` | Physical device, ship 50TB data. Storage Optimized có ~80TB usable. |
| `AWS Direct Connect` | Cần thời gian provision (weeks), không kịp 2 weeks. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements
- **Constraints:** 50TB/2 weeks, VPN saturated

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Snowball Edge Storage Optimized: thiết bị vật lý, dung lượng ~80TB, đủ chứa 50TB.
- Chuyển dữ liệu offline: copy vào Snowball, ship đến AWS → không phụ thuộc bandwidth network.
- Hoàn thành trong 2 weeks (shipping time ~vài ngày).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- DataSync dùng network (VPN hoặc Direct Connect). VPN đã 90% → không đủ bandwidth.

**❌ Đáp án B:**
- Direct Connect cần ~2-4 weeks để provision, không kịp 2 weeks.

**❌ Đáp án D:**
- Storage Gateway đồng bộ qua network (VPN), cũng bị giới hạn bandwidth.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Large data + slow network + time constraint → Snowball (physical transfer)."*
