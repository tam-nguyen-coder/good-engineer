# Question #383 - Topic 1

A company is planning to migrate a commercial off-the-shelf application from its on-premises data center to AWS. The software has a software licensing model using sockets and cores with predictable capacity and uptime requirements. The company wants to use its existing licenses, which were purchased earlier this year. Which Amazon EC2 pricing option is the MOST cost-effective?

## Options

**A.** Dedicated Reserved Hosts

**B.** Dedicated On-Demand Hosts

**C.** Dedicated Reserved Instances

**D.** Dedicated On-Demand Instances

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** COTS app with socket/core licensing, wants to use existing licenses (BYOL). Predictable capacity/uptime.
- **Existing Resources:** Existing licenses (sockets/cores based).
- **Current Issue/Goal:** Most cost-effective EC2 pricing for BYOL.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `licensing model using sockets and cores` | Cần Dedicated Host để BYOL (licenses bound to physical server). |
| `existing licenses` | BYOL (Bring Your Own License) → Dedicated Hosts required. |
| `predictable capacity` | Reserved (1-3 year) > On-Demand (cost). |
| `Dedicated Hosts` | Physical server, visibility into sockets/cores for BYOL. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective pricing option
- **Constraints:** Socket/core licensing, BYOL, predictable workload

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Dedicated Hosts: cung cấp physical server visibility (sockets, cores) → cần cho BYOL software dựa trên socket/core.
- Reserved: commit 1-3 year → giảm cost cho predictable workload.
- Dedicated Reserved Hosts = cheapest option for BYOL with predictable capacity.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Dedicated On-Demand Hosts: đắt hơn Reserved (không commitment discount).

**❌ Đáp án C:**
- Dedicated Instances: không cung cấp visibility vào physical server (sockets/cores) → không support BYOL.

**❌ Đáp án D:**
- Dedicated On-Demand Instances: đắt hơn Reserved, không support BYOL.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"BYOL socket/core license → Dedicated Host (physical server visibility). Reserved = cheaper for predictable. Dedicated Instances ≠ Dedicated Hosts."*
