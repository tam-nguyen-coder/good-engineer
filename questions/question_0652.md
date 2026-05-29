# Question #652 - Topic 1

A company has a large data workload that runs for 6 hours each day. The company cannot lose any data while the process is running. A solutions architect is designing an Amazon EMR cluster configuration to support this critical data workload. Which solution will meet these requirements MOST cost-effectively?

## Options

**A.** Configure a long-running cluster that runs the primary node and core nodes on On-Demand Instances and the task nodes on Spot Instances.

**B.** Configure a transient cluster that runs the primary node and core nodes on On-Demand Instances and the task nodes on Spot Instances.

**C.** Configure a transient cluster that runs the primary node on an On-Demand Instance and the core nodes and task nodes on Spot Instances.

**D.** Configure a long-running cluster that runs the primary node on an On-Demand Instance, the core nodes on Spot Instances, and the task nodes on Spot Instances.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Large data workload runs 6 hours daily, cannot lose data. EMR cluster.
- **Existing Resources:** EMR workload.
- **Current Issue/Goal:** Cost-effective cluster with data durability.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `cannot lose any data` | Core nodes (lưu HDFS) không thể dùng Spot (có thể bị reclaim). |
| `runs 6 hours each day` | Transient cluster (chạy xong tự terminate) tiết kiệm hơn long-running. |
| `primary node` | Master node cần On-Demand để đảm bảo ổn định. |
| `core nodes` | Lưu dữ liệu HDFS → On-Demand (không mất data). |
| `task nodes` | Chỉ compute, không lưu data → Spot để tiết kiệm. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective
- **Constraints:** Cannot lose data, 6 hours daily

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- **Transient cluster:** tự động terminate sau khi job hoàn thành → không trả tiền khi không dùng (6h/ngày).
- **Primary + Core nodes On-Demand:** đảm bảo không mất data (HDFS trên core nodes).
- **Task nodes Spot:** tiết kiệm chi phí, task nodes chỉ compute không lưu data → Spot phù hợp.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Long-running cluster: chạy 24/7 dù chỉ dùng 6h/ngày → tốn kém.

**❌ Đáp án C:**
- Core nodes trên Spot: risk mất data nếu Spot bị reclaim (violate "cannot lose any data").

**❌ Đáp án D:**
- Long-running: tốn kém.
- Core nodes Spot: risk mất data.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Transient cluster = cost saving. Primary + Core = On-Demand (no data loss). Task = Spot (cheap compute)."*
