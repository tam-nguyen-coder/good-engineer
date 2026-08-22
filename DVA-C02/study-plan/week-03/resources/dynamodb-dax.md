# DynamoDB Accelerator (DAX) — In-Memory Cache

> **Nguồn (AWS official):** https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DAX.html
> **Tuần:** 3 — DynamoDB · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- `DAX` = caching service **API-compatible với DynamoDB**, in-memory, đưa latency đọc từ **single-digit milliseconds → microseconds**.
- **Chỉ tăng tốc EVENTUALLY CONSISTENT read.** KHÔNG dùng cho app cần **strongly consistent read** (DAX pass-through, không cache strong read).
- KHÔNG hợp cho **write-intensive** workload (write nhiều → replication tăng, tốn tài nguyên, rủi ro availability).
- DAX hoạt động tốt khi **cache hit rate > 90%**; hit rate thấp → nhiều cache miss, tốn tài nguyên.
- Use case điển hình: real-time bidding, social gaming, trading; **hot key / hot partition** (VD flash-sale 1 sản phẩm); giảm RCU cần provision → tiết kiệm chi phí đọc.
- **Chỉ chạy trên nền EC2-VPC.** Hỗ trợ Go, Java, Node.js, Python, .NET (dùng DAX client, không phải SDK DynamoDB thường).
- Hỗ trợ **encryption at rest** (KMS) và **encryption in transit** (TLS, xác thực bằng cluster x509 certificate).
- IAM: cluster service role phải cho phép `dynamodb:DescribeTable`.
- Bẫy: DAX cache tên attribute **vô thời hạn** → dùng vô số tên attribute top-level (timestamps/UUIDs/session IDs làm attribute name) có thể gây **memory exhaustion**. Không phải vấn đề nếu đó là *giá trị* chứ không phải *tên* attribute.

---

## 📄 Nội dung (trích từ tài liệu gốc)

# In-memory acceleration with DynamoDB Accelerator (DAX)

Amazon DynamoDB is designed for scale and performance. In most cases, the DynamoDB response times can be measured in **single-digit milliseconds**. However, there are certain use cases that require response times in **microseconds**. For these use cases, DynamoDB Accelerator (DAX) delivers fast response times for accessing **eventually consistent** data.

DAX is a DynamoDB-compatible caching service. DAX addresses three core scenarios:
1. As an in-memory cache, DAX reduces the response times of eventually consistent read workloads by an order of magnitude from single-digit milliseconds to microseconds.
2. DAX reduces operational and application complexity by providing a managed service that is **API-compatible with DynamoDB**, requiring only minimal functional changes to use with an existing application.
3. For read-heavy or bursty workloads, DAX provides increased throughput and potential operational cost savings by reducing the need to overprovision read capacity units. Especially beneficial for applications that require repeated reads for individual keys.

DAX supports **server-side encryption**. With encryption at rest, the data persisted by DAX on disk will be encrypted (DAX writes data to disk as part of propagating changes from the primary node to read replicas). DAX also supports **encryption in transit**, ensuring all requests/responses between your application and the cluster are encrypted by TLS, and connections can be authenticated by verification of a cluster x509 certificate.

## Use cases for DAX

DAX provides access to eventually consistent data from DynamoDB tables, with **microsecond latency**. A **Multi-AZ** DAX cluster can serve **millions of requests per second**.

DAX is **ideal** for:
- Applications that require the fastest possible response time for reads (real-time bidding, social gaming, trading).
- Applications that read a small number of items more frequently than others — to mitigate a **"hot" key** and non-uniform traffic distribution (e.g., a one-day sale on a popular product), offload read activity to a DAX cache.
- Applications that are read-intensive but cost-sensitive — offload activity from your application to a DAX cluster to reduce the number of RCUs you need to purchase.
- Applications that require repeated reads against a large set of data (e.g., long-running regional weather analysis), so those reads don't consume the table's read capacity.

DAX is **NOT ideal** for:
- Applications that require **strongly consistent reads** (or cannot tolerate eventually consistent reads).
- Applications that do not require microsecond response times, or do not need to offload repeated read activity.
- **Write-intensive** applications. High volume of writes leads to increased replication across DAX nodes, increasing resource consumption and risk of availability issues.
- Applications **without many repeated reads**. DAX performs best when **cache hit rates exceed 90%**. Lower cache hit rates increase cache misses, consuming more resources across the cluster.

## DAX usage notes
- For a list of AWS Regions where DAX is available, see Amazon DynamoDB pricing.
- DAX supports applications written in **Go, Java, Node.js, Python, and .NET**, using AWS-provided clients for those languages.
- DAX is **only available for the EC2-VPC platform**.
- The DAX cluster service role policy must allow the `dynamodb:DescribeTable` action to maintain metadata about the DynamoDB table.
- DAX clusters maintain metadata about the **attribute names** of items they store. That metadata is maintained **indefinitely** (even after the item has expired or been evicted). Applications that use an **unbounded number of attribute names** can, over time, cause **memory exhaustion** in the DAX cluster. This limitation applies only to **top-level attribute names**, not nested attribute names or attribute **values**. Examples of problematic top-level attribute names include timestamps, UUIDs, and session IDs.

  Not a problem (timestamp is a *value*):
  ```json
  {
      "Id": 123,
      "Title": "Bicycle 123",
      "CreationDate": "2017-10-24T01:02:03+00:00"
  }
  ```

  A problem if there are enough of them each with a different timestamp (timestamp is an *attribute name*):
  ```json
  {
      "Id": 123,
      "Title": "Bicycle 123",
      "2017-10-24T01:02:03+00:00": "created"
  }
  ```
