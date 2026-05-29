# Question #306 - Topic 1

A company wants to run an in-memory database for a latency-sensitive application that runs on Amazon EC2 instances. The application processes more than 100,000 transactions each minute and requires high network throughput. A solutions architect needs to provide a cost- effective network design that minimizes data transfer charges. Which solution meets these requirements?

## Options

**A.** Launch all EC2 instances in the same Availability Zone within the same AWS Region. Specify a placement group with cluster strategy when launching EC2 instances.

**B.** Launch all EC2 instances in different Availability Zones within the same AWS Region. Specify a placement group with partition strategy when launching EC2 instances.

**C.** Deploy an Auto Scaling group to launch EC2 instances in different Availability Zones based on a network utilization target.

**D.** Deploy an Auto Scaling group with a step scaling policy to launch EC2 instances in different Availability Zones.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** In-memory database, latency-sensitive, high throughput (100k+ txn/min), cần cost-effective với minimize data transfer charges.
- **Existing Resources:** EC2 instances.
- **Current Issue/Goal:** Low latency, high throughput, minimize data transfer costs.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `latency-sensitive` | Cần network latency thấp nhất → cùng AZ + cluster placement group. |
| `high network throughput` | Cluster placement group cung cấp bandwidth cao hơn (up to 25 Gbps). |
| `minimizes data transfer charges` | Cùng AZ → data transfer free. |
| `placement group with cluster strategy` | Instances cùng trong cluster placement group → low latency, high throughput. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost-effective network design
- **Constraints:** Low latency, high throughput, minimize data transfer charges

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Cluster placement group đặt tất cả instances trong cùng AZ với network được tối ưu cho low latency và high throughput.
- Data transfer giữa các instances trong cùng AZ là free → minimize data transfer charges.
- Cần tất cả instances trong 1 cluster placement group và cùng AZ để đạt network performance tối đa.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Partition placement group dùng cho fault tolerance (Hadoop, HDFS), không optimize network throughput hay latency. Cross-AZ → có data transfer charges.

**❌ Đáp án C:**
- Auto Scaling across AZs → cross-AZ data transfer charges và không optimize latency (khác AZ = latency cao hơn).

**❌ Đáp án D:**
- Tương tự C: cross-AZ không optimize cho latency-sensitive workload.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Low latency + high throughput → cluster placement group + cùng AZ. Cross-AZ = latency + cost."*
