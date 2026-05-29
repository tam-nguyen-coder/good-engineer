# Question #620 - Topic 1

A company is planning to deploy a business-critical application in the AWS Cloud. The application requires durable storage with consistent, low- latency performance. Which type of storage should a solutions architect recommend to meet these requirements?

## Options

**A.** Instance store volume

**B.** Amazon ElastiCache for Memcached cluster

**C.** Provisioned IOPS SSD Amazon Elastic Block Store (Amazon EBS) volume

**D.** Throughput Optimized HDD Amazon Elastic Block Store (Amazon EBS) volume

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Business-critical application cần durable storage với consistent low-latency performance.
- **Existing Resources:** None.
- **Current Issue/Goal:** Chọn storage type phù hợp: durable + consistent low-latency.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `durable` | Dữ liệu không bị mất khi instance stop/terminate. |
| `consistent, low-latency performance` | Cần IOPS ổn định, độ trễ thấp. |
| `business-critical` | Cần độ tin cậy cao. |
| `Provisioned IOPS SSD` | io1/io2: cung cấp consistent IOPS, low latency, durable. |
| `Instance store` | Ephemeral (không durable). |
| `Throughput Optimized HDD` | st1: throughput-optimized, không low-latency (HDD). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Meet requirements
- **Constraints:** Durable, consistent low-latency, business-critical

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Provisioned IOPS SSD (io1/io2): cung cấp consistent IOPS với latency thấp, phù hợp cho business-critical applications.
- Durable: EBS volume tồn tại độc lập với EC2 instance, dữ liệu không mất khi instance terminate.
- io2 có durability 99.999% (so với gp3 99.8–99.9%).

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Instance store: ephemeral storage, dữ liệu mất khi instance stop/terminate → không durable.

**❌ Đáp án B:**
- ElastiCache: in-memory cache, không durable (dữ liệu trong memory mất khi restart).

**❌ Đáp án D:**
- Throughput Optimized HDD (st1): HDD-based, latency cao hơn SSD, không phù hợp cho low-latency requirements.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Durable + consistent low-latency → Provisioned IOPS SSD (io1/io2). Instance store = ephemeral, HDD = high latency."*
