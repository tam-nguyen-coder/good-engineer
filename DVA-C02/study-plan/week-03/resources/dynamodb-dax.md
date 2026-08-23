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

## 🧩 Đào sâu: "DAX is only available for the EC2-VPC platform" nghĩa là gì?

### 1. Nghĩa lịch sử — vế đối chiếu đã không còn tồn tại

Ngày xưa AWS có **2 nền tảng mạng** cho EC2:

| Nền tảng            | Là gì                                                                                                    | Trạng thái                      |
| --------------------- | ---------------------------------------------------------------------------------------------------------- | --------------------------------- |
| **EC2-Classic** | Mạng "phẳng" nguyên thuỷ (trước 2013) — instance nằm chung pool mạng AWS,**KHÔNG có VPC** | ⚰️**Khai tử 15/08/2022** |
| **EC2-VPC**     | Instance nằm**trong VPC của bạn** — subnet, route table, security group, private IP              | ✅ Nền tảng duy nhất hiện nay |

⇒ Ngày nay câu đó chỉ đơn giản có nghĩa: **`DAX` buộc phải nằm BÊN TRONG một VPC.**

### 2. Vì sao câu này vẫn cực kỳ quan trọng

Nó nói lên một khác biệt kiến trúc căn bản mà đề DVA-C02 hay khai thác:

- **`DynamoDB` có PUBLIC endpoint** — `dynamodb.<region>.amazonaws.com`. Gọi được từ laptop, từ Lambda không-VPC, từ bất cứ đâu có Internet, chỉ cần **IAM credentials**. Không cần biết gì về mạng.
- **`DAX` KHÔNG có public endpoint** — chỉ có **private IP trong subnet của bạn**.

⇒ Chuyển từ DynamoDB SDK sang DAX client **không chỉ là đổi thư viện** — nó **thêm một phụ thuộc về MẠNG** mà trước đó bạn chưa từng có. Đây là chỗ vỡ trận phổ biến nhất khi triển khai DAX lần đầu.

```
              ┌──────────────── AWS Region ─────────────────┐
              │                                             │
Laptop ──────▶│  DynamoDB  ← PUBLIC endpoint                │
Lambda        │  dynamodb.ap-southeast-1.amazonaws.com      │
(no VPC) ────▶│  chỉ cần IAM credentials                    │
              │        ▲                                    │
              │        │ DAX tự gọi xuống (AWS lo, ko cần NAT)
              │  ┌─────┴──────────── VPC của bạn ─────────┐ │
              │  │                                        │ │
              │  │   DAX cluster                          │ │
              │  │   my-dax.abc123.dax-clusters...:8111   │ │
              │  │   ← CHỈ private IP trong subnet        │ │
              │  │        ▲                               │ │
              │  │        │ Security Group phải mở 8111   │ │
              │  │   EC2 / ECS / Lambda-in-VPC            │ │
              │  └────────────────────────────────────────┘ │
              └─────────────────────────────────────────────┘

  ✗ KHÔNG có đường nào từ Internet đi tới DAX
```

### 2.1 ⚠️ Hiểu sai phổ biến nhất: app nói chuyện với AI?

```
❌ Nhiều người hình dung (SAI):

   App ──▶ DynamoDB ──▶ DAX
                        (DynamoDB tự biết dùng cache)

✅ Thực tế:

   App ──▶ DAX cluster ──▶ DynamoDB
       (endpoint DAX)      (DAX gọi hộ bạn)
```

**DAX nằm PHÍA TRƯỚC DynamoDB, không phải phía sau.** DynamoDB **hoàn toàn không biết** DAX tồn tại — nó **không bao giờ** tự route request sang DAX. Nếu app vẫn gọi `dynamodb.<region>.amazonaws.com` thì DAX **ngồi không**, không có tác dụng gì, mà bạn vẫn trả tiền node-hour.

**Nguồn gốc ngộ nhận:** cụm **"API-compatible"** trong docs. Nó **chỉ** nghĩa là *DAX phơi ra đúng các API giống DynamoDB* (`GetItem`, `Query`, `PutItem`...) nên **code gọi hàm không phải sửa**. Nó **KHÔNG** nghĩa "trong suốt / tự động". Thứ **bắt buộc phải đổi** là **client + endpoint**.

> 🧠 **Memory hook:** *"Cache nào cũng phải được **TRỎ VÀO** mới có tác dụng."* — giống `ElastiCache` (app trỏ vào Redis, không phải RDS) và `CloudFront` (client gọi domain CloudFront, không phải origin).

#### Thứ duy nhất phải đổi trong code

```python
# ❌ TRƯỚC — nói chuyện trực tiếp với DynamoDB
import boto3
ddb = boto3.resource('dynamodb')
table = ddb.Table('Orders')
table.get_item(Key={'OrderId': '123'})

# ✅ SAU — nói chuyện với DAX
from amazondax import AmazonDaxClient
dax = AmazonDaxClient.resource(
    endpoint_url='dax://my-dax.abc123.dax-clusters.ap-southeast-1.amazonaws.com'
)
table = dax.Table('Orders')          # ← từ dòng này trở đi CODE Y HỆT
table.get_item(Key={'OrderId': '123'})
```

Chỉ **2 dòng khởi tạo client** thay đổi. Toàn bộ logic nghiệp vụ giữ nguyên — đó chính xác là ý nghĩa của "API-compatible".

#### DAX làm gì với từng loại request?

| Thao tác                                                                     | DAX xử lý thế nào                                                                                        | Có cache?                          |
| ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | ----------------------------------- |
| `GetItem` / `BatchGetItem` **eventual**                             | **Read-through**: hit → trả từ **item cache**; miss → gọi DynamoDB, cache lại, trả về    | ✅ TTL mặc định**5 phút** |
| `Query` / `Scan` **eventual**                                       | Read-through vào**query cache** (key = tham số request)                                              | ✅ TTL mặc định**5 phút** |
| Read**strongly consistent**                                             | **Pass-through** — đi thẳng xuống DynamoDB                                                         | ❌                                  |
| `PutItem` / `UpdateItem` / `DeleteItem`                                 | **Write-through**: ghi xuống **DynamoDB TRƯỚC** (đồng bộ), rồi mới cập nhật item cache | ghi cả 2 nơi                      |
| `TransactGetItems` / `TransactWriteItems`                                 | **Pass-through**                                                                                       | ❌                                  |
| **Control plane** (`CreateTable`, `DescribeTable`, `UpdateTable`) | ❌**DAX KHÔNG hỗ trợ** — phải gọi DynamoDB trực tiếp                                           | —                                  |

⚠️ Dòng cuối rất quan trọng khi code thật: **app thường phải giữ CẢ HAI client** — DAX client cho data plane, SDK thường cho control plane và các thao tác DAX không hỗ trợ.

#### 🪤 Hai bẫy sinh ra từ việc DAX có HAI cache riêng biệt

1. **Write-through cập nhật item cache nhưng KHÔNG invalidate query cache.** `PutItem` qua DAX xong, `GetItem` thấy dữ liệu mới ngay, nhưng `Query` có thể vẫn trả kết quả cũ **cho tới khi TTL 5 phút hết hạn**. ⇒ DAX **không** phù hợp khi app cần đọc lại ngay danh sách vừa thay đổi.
2. **Ghi TRỰC TIẾP vào DynamoDB (không qua DAX) thì DAX không hề hay biết** — cache stale tới hết TTL. ⇒ Đã dùng DAX thì **mọi** đường ghi (job batch, Lambda khác, console) nên đi qua DAX, hoặc chấp nhận độ trễ bằng TTL.

### 3. Hệ quả thực tế — những gì bạn phải làm

| Yêu cầu                           | Chi tiết                                                                                                       |
| ----------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| **DAX subnet group**          | Khai trước khi tạo cluster — liệt kê subnet trong VPC. Nên chọn**≥ 3 AZ** cho HA                 |
| **Security group**            | Mở inbound TCP**`8111`** (không mã hoá) hoặc **`9111`** (TLS) từ SG của client           |
| **Client phải ở TRONG VPC** | EC2 / ECS / EKS cùng VPC, hoặc**Lambda có cấu hình VPC**                                             |
| **Từ ngoài VPC**            | Cần**VPC peering / Transit Gateway / VPN / Direct Connect**. **Không** có PrivateLink cho DAX    |
| **Từ on-premises / laptop**  | ❌ Không gọi trực tiếp được — phải qua VPN/DX                                                          |
| **Cùng Region**              | DAX và bảng DynamoDB**bắt buộc cùng Region**                                                         |
| **Đường DAX → DynamoDB**  | AWS tự lo —**không cần** NAT Gateway cho riêng đường này                                         |
| **Client library**            | Phải dùng**DAX client** (Go, Java, Node.js, Python, .NET), **không** phải SDK DynamoDB thường |
| **Kích thước cluster**     | 1 primary + tối đa**10 read replica** (**11 node**); production nên **3 node / 3 AZ**      |

### 4. 🪤 Bẫy số 1 của DVA-C02: Lambda + DAX

```
Đề: "Lambda function gọi DAX bị timeout / không kết nối được. Vì sao?"

❌ Lambda mặc định chạy NGOÀI VPC của bạn
   → Không thấy private IP của DAX → timeout

✅ Phải bật VPC config cho Lambda: chọn subnet + security group
   → Lambda được gắn ENI trong VPC → mới thấy DAX
```

**Chuỗi hệ quả đề rất thích hỏi tiếp:** Lambda vào VPC rồi thì **mất đường ra Internet mặc định**. Nếu function còn cần gọi `S3`, `SNS`, `Secrets Manager`... phải thêm:

- **VPC Gateway Endpoint** cho S3 / DynamoDB (**miễn phí**), hoặc
- **VPC Interface Endpoint** (PrivateLink) cho service khác, hoặc
- **NAT Gateway** trong public subnet (tốn tiền, nhưng chữa được tất cả).

> 🧠 **Memory hook:** *"**DynamoDB gọi từ đâu cũng được — DAX chỉ gọi được từ trong nhà (VPC).** Muốn Lambda vào nhà thì phải cấp cho nó ENI; vào nhà rồi thì mất cửa ra Internet."*

### 5. 📌 Chốt

| Câu hỏi                           | Trả lời                                                             |
| ----------------------------------- | --------------------------------------------------------------------- |
| "EC2-VPC platform" nghĩa gì?      | **DAX phải nằm trong VPC** — vế "EC2-Classic" đã khai tử |
| DAX có public endpoint?            | **KHÔNG** — chỉ private IP                                   |
| Gọi DAX từ laptop được không? | **Không** (trừ khi qua VPN/DX)                                |
| Lambda gọi DAX cần gì?           | **Bật VPC config** (subnet + SG)                               |
| Port                                | **8111** (plain) · **9111** (TLS)                        |
| DAX và table khác Region được? | **Không** — bắt buộc cùng Region                           |

---

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
