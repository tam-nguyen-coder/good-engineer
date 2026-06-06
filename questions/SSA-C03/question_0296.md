# Question #296 - Topic 1

A development team has launched a new application that is hosted on Amazon EC2 instances inside a development VPC. A solutions architect needs to create a new VPC in the same account. The new VPC will be peered with the development VPC. The VPC CIDR block for the development VPC is 192.168.0.0/24. The solutions architect needs to create a CIDR block for the new VPC. The CIDR block must be valid for a VPC peering connection to the development VPC. What is the SMALLEST CIDR block that meets these requirements?

## Options

**A.** 10.0.1.0/32

**B.** 192.168.0.0/24

**C.** 192.168.1.0/32

**D.** 10.0.1.0/24

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Cần tạo VPC mới peered với VPC hiện tại (CIDR 192.168.0.0/24). Chọn CIDR nhỏ nhất không overlap.
- **Existing Resources:** Development VPC with CIDR 192.168.0.0/24.
- **Current Issue/Goal:** Chọn CIDR block valid cho VPC peering, không overlap, nhỏ nhất.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `SMALLEST CIDR block` | CIDR mask càng lớn (số càng cao) càng nhỏ. |
| `valid for VPC` | VPC CIDR phải từ /16 đến /28 (theo AWS). |
| `VPC peering` | CIDRs không được overlap (trùng IP range). |
| `192.168.0.0/24` | Range từ 192.168.0.0 – 192.168.0.255. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Smallest valid CIDR
- **Constraints:** Non-overlapping with 192.168.0.0/24, valid VPC size (/28 - /16)

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D (10.0.1.0/24)**

**Giải thích:**
- /24 là valid (nằm trong dải /16 - /28).
- 10.0.1.0/24 không overlap với 192.168.0.0/24 (khác dải IP).
- /28 là smallest valid VPC CIDR về mặt lý thuyết, nhưng trong 4 options, 10.0.1.0/24 là smallest valid.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- /32 không valid cho VPC (AWS yêu cầu minimum /28).

**❌ Đáp án B:**
- 192.168.0.0/24 overlaps với development VPC → không thể peer.

**❌ Đáp án C:**
- /32 không valid cho VPC.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"VPC CIDR range: /16 – /28. Peering yêu cầu CIDRs không overlap. /32 không phải VPC CIDR."*
