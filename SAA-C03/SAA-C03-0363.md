# Question #363 - Topic 1

A company is building a game system that needs to send unique events to separate leaderboard, matchmaking, and authentication services concurrently. The company needs an AWS event-driven system that guarantees the order of the events. Which solution will meet these requirements?

## Options

**A.** Amazon EventBridge event bus

**B.** Amazon Simple Notification Service (Amazon SNS) FIFO topics

**C.** Amazon Simple Notification Service (Amazon SNS) standard topics

**D.** Amazon Simple Queue Service (Amazon SQS) FIFO queues

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Game system: 3 services nhận events concurrently (fan-out). Cần guarantee ordering.
- **Existing Resources:** (none specified)
- **Current Issue/Goal:** Event fan-out with ordering.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `concurrently` | Fan-out (1 event → nhiều consumers). |
| `guarantees the order of the events` | FIFO ordering. |
| `SNS FIFO topics` | Support ordering + fan-out to multiple SQS FIFO queues. |
| `SQS FIFO queues` | Ordering but no fan-out (single consumer). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Which solution meets requirements
- **Constraints:** Fan-out + ordering

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- SNS FIFO topics: vừa fan-out (publish 1 event → nhiều subscribers) vừa guarantee ordering (FIFO).
- Subscribers là SQS FIFO queues → mỗi service nhận events đúng thứ tự.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- EventBridge event bus: fan-out nhưng không guarantee ordering.

**❌ Đáp án C:**
- SNS Standard topics: fan-out nhưng không guarantee ordering.

**❌ Đáp án D:**
- SQS FIFO queues: ordering nhưng single consumer (không fan-out).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Fan-out + ordering → SNS FIFO topics (subscribe SQS FIFO). SQS FIFO = ordering only. EventBridge = fan-out, no ordering."*
