# Question #362 - Topic 1

A company uses a payment processing system that requires messages for a particular payment ID to be received in the same order that they were sent. Otherwise, the payments might be processed incorrectly. Which actions should a solutions architect take to meet this requirement? (Choose two.)

## Options

**A.** Write the messages to an Amazon DynamoDB table with the payment ID as the partition key.

**B.** Write the messages to an Amazon Kinesis data stream with the payment ID as the partition key.

**C.** Write the messages to an Amazon ElastiCache for Memcached cluster with the payment ID as the key.

**D.** Write the messages to an Amazon Simple Queue Service (Amazon SQS) queue. Set the message attribute to use the payment ID.

**E.** Write the messages to an Amazon Simple Queue Service (Amazon SQS) FIFO queue. Set the message group to use the payment ID.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Payment processing, cần ordering guarantee cho messages cùng payment ID. If order wrong, payments incorrect.
- **Existing Resources:** (none specified)
- **Current Issue/Goal:** Guaranteed message ordering by payment ID.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `received in the same order` | FIFO ordering required. |
| `payment ID` | message group ID / partition key để group messages cùng payment. |
| `SQS FIFO queue` | Guarantees ordering within message group. First-in-first-out. |
| `Kinesis Data Streams` | Guarantees ordering within shard (by partition key). |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Choose two, message ordering
- **Constraints:** Ordering by payment ID

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B (Kinesis) và E (SQS FIFO)**

**Giải thích:**
- **B (Kinesis):** Partition key = payment ID → messages cùng payment ID vào cùng shard → ordering preserved.
- **E (SQS FIFO):** Message group ID = payment ID → FIFO queue guarantees ordering trong cùng group.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- DynamoDB không phải message queue. Ghi vào DDB không đảm bảo ordering khi read.

**❌ Đáp án C:**
- Memcached là cache, không durable, không phải message queue.

**❌ Đáp án D:**
- SQS standard queue: không guarantee ordering (best-effort).

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Message ordering → SQS FIFO (message group) hoặc Kinesis (partition key). SQS Standard = best-effort, không guarantee."*
