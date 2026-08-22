# Question #580 - Topic 1

A company uses locally attached storage to run a latency-sensitive application on premises. The company is using a lift and shift method to move the application to the AWS Cloud. The company does not want to change the application architecture. Which solution will meet these requirements MOST cost-effectively?

## Options

**A.** Configure an Auto Scaling group with an Amazon EC2 instance. Use an Amazon FSx for Lustre file system to run the application.

**B.** Host the application on an Amazon EC2 instance. Use an Amazon Elastic Block Store (Amazon EBS) GP2 volume to run the application.

**C.** Configure an Auto Scaling group with an Amazon EC2 instance. Use an Amazon FSx for OpenZFS file system to run the application.

**D.** Host the application on an Amazon EC2 instance. Use an Amazon Elastic Block Store (Amazon EBS) GP3 volume to run the application.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** On-prem latency-sensitive app dùng locally attached storage, lift-and-shift to AWS.
- **Existing Resources:** On-prem app with local storage.
- **Current Issue/Goal:** Migrate without changing architecture, cost-effective, low latency.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `locally attached storage` | Cần block storage (EBS) tương tự local disk. |
| `lift and shift` | Không change architecture → dùng EC2 + EBS (block storage). |
| `latency-sensitive` | EBS GP3: low latency, high performance. |
| `MOST cost-effectively` | GP3 rẻ hơn GP2 (cùng dung lượng, throughput baseline cao hơn). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effectively
- **Constraints:** Lift-and-shift, latency-sensitive, no architecture change

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- EC2 + EBS GP3 tương tự locally attached storage (block storage), phù hợp lift-and-shift.
- GP3: baseline performance cao hơn GP2 với giá thấp hơn (cost-effective).
- Không cần thay đổi application architecture.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- FSx for Lustre là parallel file system (HPC use case), không phải locally attached storage, overkill và đắt hơn.

**❌ Đáp án B:**
- EBS GP2: đắt hơn GP3 với cùng performance. GP3 là thế hệ mới hơn, rẻ hơn.

**❌ Đáp án C:**
- FSx for OpenZFS là file system, không phải block storage. Không phù hợp lift-and-shift từ local disk.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Lift-and-shift local disk → EBS GP3 (block storage, cheaper than GP2). FSx = file system, not block."*
