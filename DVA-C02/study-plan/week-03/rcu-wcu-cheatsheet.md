# 🧮 RCU / WCU — Cheat sheet tính capacity `DynamoDB`

> **Tuần:** 3 — DynamoDB · **Loại:** Cheat sheet tự luyện
>
> **Điều hướng:** [🏠 Tuần 3](README.md) · [📝 Câu hỏi](questions.md) · [🧪 Labs](labs.md) · [📂 Resources](resources/INDEX.md)

---

## 1. 🧠 Hiểu bản chất trước khi tính

**Capacity unit KHÔNG phải là "dung lượng"** — nó là **quota thao tác mỗi giây**.

- `1 WCU` = quyền ghi **1 lần/giây**, mỗi lần **tối đa 1 KB**.
- `1 RCU` = quyền đọc **1 lần/giây** (strongly consistent), mỗi lần **tối đa 4 KB**.

Hãy tưởng tượng như **vé xe bus mỗi giây**:

- Mỗi giây bạn được cấp N vé. Không dùng thì **mất** (chỉ giữ lại được tối đa `300 giây` burst capacity).
- Một item to hơn "1 ghế" thì phải mua **nhiều vé cho 1 lần đi** — và **không có vé lẻ**, luôn **làm tròn LÊN**.

> 🧠 **Memory hook:** *"Capacity là vé mỗi giây, không phải ổ cứng."*
> Đây là lý do đề thi luôn cho bạn 2 dữ kiện: **kích thước item** + **số request/giây**.

---

## 2. 🔢 Bốn con số phải thuộc lòng (và chỉ bốn)

| Con số   | Ý nghĩa                                              |
| ---------- | ------------------------------------------------------- |
| **1 KB** | Đơn vị **GHI** (write) — 1 WCU = 1 KB              |
| **4 KB** | Đơn vị **ĐỌC** (read) — 1 RCU = 4 KB               |
| **÷ 2**  | **Eventually consistent read** → rẻ một nửa       |
| **× 2**  | **Transactional** (đọc HOẶC ghi) → đắt gấp đôi |

> 🧠 **Memory hook — "1 4 2 2":**
> **1** KB ghi · **4** KB đọc · chia **2** nếu eventual · nhân **2** nếu transaction.
>
> Nhớ kèm câu: *"**Ghi một, đọc bốn; lơ mơ chia hai, chắc cú nhân hai**."*

---

## 3. ⚙️ Công thức 3 bước — dùng cho MỌI câu hỏi

```
                 ┌─ 1. CỠ ─────────────────────────────────┐
                 │  Ghi:  units = ceil(size / 1 KB)        │
                 │  Đọc:  units = ceil(size / 4 KB)        │
                 └─────────────────────────────────────────┘
                                    ↓
                 ┌─ 2. TẦN SỐ ─────────────────────────────┐
                 │  × số request mỗi GIÂY                  │
                 └─────────────────────────────────────────┘
                                    ↓
                 ┌─ 3. HỆ SỐ ──────────────────────────────┐
                 │  eventually consistent  → ÷ 2           │
                 │  transactional          → × 2           │
                 │  strongly consistent    → × 1 (mặc định)│
                 └─────────────────────────────────────────┘
                                    ↓
                        ceil(kết quả)  ← làm tròn LÊN lần cuối
```

**Đọc thành lời (thần chú khi đi thi):**

> **"Chia — Tròn — Nhân giây — Nhân hệ số — Tròn lần nữa."**

⚠️ **Làm tròn xảy ra 2 LẦN**: lần 1 ở bước cỡ (mỗi request), lần 2 ở tổng cuối (vì capacity provisioned phải là số nguyên).

---

## 4. 📊 Bảng tra 6 kiểu thao tác (suy ra được từ mục 3 — không cần học vẹo)

Giả sử **1 item = 4 KB, 1 request/giây**:

| Thao tác                       | Công thức                | Chi phí       | Ghi chú                       |
| -------------------------------- | -------------------------- | ---------------- | ------------------------------- |
| Read **eventually consistent** | `ceil(4/4) ÷ 2 = 0.5`    | **0.5 RCU** | Rẻ nhất, có thể stale     |
| Read **strongly consistent**   | `ceil(4/4) × 1 = 1`      | **1 RCU**   | Baseline                        |
| Read **transactional**         | `ceil(4/4) × 2 = 2`      | **2 RCU**   | `TransactGetItems`, ACID      |
| Write **standard**             | `ceil(4/1) × 1 = 4`      | **4 WCU**   | `PutItem` / `UpdateItem`      |
| Write **transactional**        | `ceil(4/1) × 2 = 8`      | **8 WCU**   | `TransactWriteItems`          |
| Write qua **GSI**              | tính RIÊNG trên index   | **+ WCU GSI** | Cộng thêm, không thay thế |

> 🧠 **Cái thang giá đọc — "½ · 1 · 2":** eventual → strong → transactional, **mỗi bậc nhân đôi**.
> ⇒ **Transactional read đắt gấp 4 lần eventually consistent read.** Đây là câu trả lời cho mọi câu hỏi "làm sao giảm chi phí đọc": hạ một bậc trên cái thang.

---

## 5. 🔍 Consistency — hiểu bằng hình ảnh 3 bản sao

Mỗi partition của `DynamoDB` có **3 bản sao trên 3 AZ khác nhau**, trong đó **1 là leader**. Write luôn đi vào leader, rồi replicate sang 2 bản còn lại.

```
        ┌──────────┐   ┌──────────┐   ┌──────────┐
Write → │ LEADER   │──▶│ replica  │   │ replica  │
        │  AZ-a    │   │  AZ-b    │   │  AZ-c    │
        └──────────┘   └──────────┘   └──────────┘
             ▲              ▲               ▲
             │              └───────┬───────┘
    strongly consistent      eventually consistent
    (luôn đọc leader)     (đọc bản sao BẤT KỲ → có thể chậm nhịp)
```

| Loại                                | Đọc từ đâu                          | Đảm bảo                                                                 | Giá        | Khi nào dùng                                                       |
| ------------------------------------- | --------------------------------------- | -------------------------------------------------------------------------- | ------------- | -------------------------------------------------------------------- |
| **Eventually consistent** (default) | 1 bản sao bất kỳ                  | Có thể **chưa thấy** write vừa xong (thường kịp trong ~1 giây) | **0.5×** | Feed, catalog, đếm view, dashboard — sai lệch 1 giây vô hại |
| **Strongly consistent**             | **Leader**                            | Luôn thấy write mới nhất đã commit                                | **1×**   | Read-after-write: check số dư, kiểm tồn kho trước khi trừ    |
| **Transactional**                   | Leader + **serializable isolation** | **ACID** — đọc/ghi nhiều item "cùng một lúc", all-or-nothing       | **2×**   | Chuyển tiền, đặt vé, ràng buộc nhiều bảng                    |

**Cách bật strongly consistent:** tham số `ConsistentRead=true` trong `GetItem` / `Query` / `Scan` / `BatchGetItem`.

> 🧠 **Memory hook:**
> - **Eventual** = *"hỏi bất kỳ ai trong 3 người"* → nhanh, rẻ, có thể nghe tin cũ.
> - **Strong** = *"hỏi đúng người trưởng nhóm"* → luôn đúng, đắt gấp đôi.
> - **Transactional** = *"triệu tập họp và chốt biên bản"* → all-or-nothing, đắt gấp đôi nữa.

---

### 5.1 ⚠️ Consistency là chuyện của ĐỌC — write không có "eventually consistent"

| Thao tác     | Các "kiểu" có thể chọn                                                                                              | Số kiểu   |
| -------------- | ------------------------------------------------------------------------------------------------------------------------ | ------------ |
| **READ**  | `eventually consistent` (default) → `strongly consistent` (`ConsistentRead=true`) → `transactional` (`TransactGetItems`) | **3**  |
| **WRITE** | `standard` (`PutItem`/`UpdateItem`/`DeleteItem`/`BatchWriteItem`) → `transactional` (`TransactWriteItems`)                | **2**  |

**Vì sao không có "eventually consistent write":** mọi write đều đi vào **leader replica** và chỉ được ack sau khi đã ghi bền vững ở **đa số bản sao (2/3 AZ)**. Khi API trả về thành công ⇒ dữ liệu **đã commit**. Không có lựa chọn "ghi lỏng cho rẻ".

**`Transactional` thì có ở CẢ HAI chiều**, vì nó nói về **phạm vi nguyên tử** (nhiều item, all-or-nothing), không phải về **độ mới của dữ liệu**.

**Nhưng chữ "eventual" VẪN xuất hiện trên đường ghi — ở tầng khác, đừng nhầm với `ConsistentRead`:**

| Nơi xuất hiện                | Cơ chế                                                                                 | Hệ quả cho đề thi                                                                        |
| ------------------------------- | ---------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| **Read từ non-leader**   | Bạn **chủ động chọn** (default)                                                  | Rẻ một nửa, có thể stale ~1 giây                                                       |
| **`GSI` propagation** 🪤 | Write vào table → GSI cập nhật **ASYNC**                                          | GSI **CHỈ** eventually consistent · truyền `ConsistentRead=true` lên GSI → **`ValidationException`** |
| **`LSI`**                | Nằm **CÙNG partition** với item → cập nhật **ĐỒNG BỘ** trong cùng thao tác ghi | Vì vậy LSI **hỗ trợ** strongly consistent read                                          |
| **`Global Tables`** 🪤   | Replicate **cross-Region** là eventually consistent                                | Xung đột giải quyết bằng **last-writer-wins** · không có strongly consistent xuyên Region |

> 🧠 **Memory hook:** *"**Không có ghi lỏng — chỉ có đọc lỏng.** Nhưng thứ bạn ghi **sang GSI** và **sang Region khác** thì luôn tới muộn."*
>
> 🧠 **Tại sao LSI strong được mà GSI không:** *"LSI ở cùng nhà (cùng partition) nên cập nhật kịp; GSI ở nhà khác nên phải gửi thư."*

---

### 5.2 🔬 Phân biệt KỸ 3 loại read — hai trục, không phải một cái thang

**Sai lầm phổ biến:** coi 3 loại read là thang "yếu → mạnh". Thực tế chúng trả lời **hai câu hỏi khác nhau**:

- **`strongly consistent`** → về **ĐỘ MỚI của MỘT item**: *"cái tôi đọc có phải bản mới nhất?"*
- **`transactional`** → về **SỰ CÔ LẬP GIỮA NHIỀU item**: *"tập item tôi đọc có cùng một khoảnh khắc?"*

⇒ **Hai lần `strongly consistent read` riêng lẻ vẫn có thể cho ra bức tranh SAI**, dù mỗi lần đọc đều mới nhất. `transactional` **không phải** "strong hơn strong".

#### Bảng so sánh đầy đủ

| Tiêu chí                            | `eventually consistent`             | `strongly consistent`                  | `transactional`                          |
| -------------------------------------- | ------------------------------------- | ---------------------------------------- | ------------------------------------------ |
| **Cách gọi**                    | default (bỏ trống)               | **`ConsistentRead=true`**          | **`TransactGetItems`**               |
| **Đọc từ đâu**                | 1 trong 3 bản sao **bất kỳ**  | **leader replica**                 | leader + **snapshot cô lập**         |
| **Đảm bảo ĐỘ MỚI**          | có thể chậm nhịp (~<1s)        | thấy **mọi write đã ack** trước | như strong                               |
| **Đảm bảo CÔ LẬP**            | ❌ không                          | ❌ **không** (chỉ đúng từng item) | ✅ **SERIALIZABLE** trên cả tập     |
| **Giá / 4 KB**                    | **0.5 RCU**                     | **1 RCU**                          | **2 RCU**                            |
| **Latency**                         | thấp nhất                        | cao hơn                                | cao nhất (2-phase)                      |
| **Khả năng scale**              | tốt nhất — **3 replica** phục vụ | leader là **bottleneck**           | thấp nhất                             |
| **Nhiều item / nhiều bảng**   | không đảm bảo                   | không đảm bảo                       | ✅ ≤ **100 item / 4 MB**, cùng Region+account |
| **Trên `GSI`**                   | ✅ (**CHỈ** mode này)          | ❌ **`ValidationException`**       | ❌ (chỉ base table)                    |
| **Trên `LSI`**                   | ✅                                  | ✅                                     | ❌                                       |
| **`DAX` cache**                   | ✅ **được cache**              | ❌ **pass-through**                | ❌ pass-through                          |
| **Global Tables cross-Region**      | ✅                                  | ❌ chỉ trong Region local            | ❌ không xuyên Region                  |
| **Lỗi đặc trưng** 🪤          | —                                   | **HTTP 500** nếu network delay/outage | **`TransactionCanceledException`**   |

#### Ví dụ then chốt: vì sao 2 strong read ≠ 1 transactional read

`TransactWriteItems` chuyển **100đ** từ A → B. Bạn đọc số dư bằng **hai lần `GetItem` strongly consistent**:

```
        t1              t2                t3
        │               │                 │
  A: 500 ──────────▶ A: 400 ──────────▶ A: 400
  B: 200 ──────────▶ B: 200 ──────────▶ B: 300
                    ↑ đã trừ A, CHƯA cộng B
        đọc A ở t2 → 400  (strong: ĐÚNG, mới nhất)
        đọc B ở t2 → 200  (strong: ĐÚNG, mới nhất)
        Tổng = 600  ✗  (đáng lẽ luôn phải là 700)
```

Cả hai lần đọc đều **chính xác** tại thời điểm của nó, nhưng **ghép lại thì sai** — 100đ "bốc hơi". `TransactGetItems` chỉ thấy **hoặc 500/200, hoặc 400/300**, không bao giờ thấy trạng thái nửa vời.

> 🧠 **Memory hook:** *"**Strong = ảnh chụp rõ nét từng người. Transactional = ảnh chụp nhóm cùng một cú bấm máy.**"*
> Nhiều ảnh nét chưa chắc ghép thành một ảnh nhóm đúng.

#### Isolation level của từng API đọc (so với `TransactWriteItems`)

| Thao tác đọc         | Isolation              | Nghĩa là                                                            |
| ------------------------ | ---------------------- | --------------------------------------------------------------------- |
| `GetItem`              | **SERIALIZABLE**  | 1 item ⇒ không thể thấy trạng thái nửa vời                  |
| `TransactGetItems`     | **SERIALIZABLE**  | cả tập item là 1 snapshot                                        |
| `BatchGetItem` 🪤      | **READ-COMMITTED** | mỗi item đều đã commit, **nhưng tập hợp có thể lệch nhịp** |
| `Query` / `Scan` 🪤    | **READ-COMMITTED** | như trên — đây chính là bẫy ở ví dụ trên                    |

`READ-COMMITTED` = **không bao giờ đọc dữ liệu chưa commit** (không dirty read), nhưng **không** đảm bảo nhiều item thuộc cùng một khoảnh khắc.

#### Cây quyết định khi đi thi

```
Đề nói gì?
│
├─ "multiple items / multiple tables must succeed or fail together"
│  "all-or-nothing" · "consistent snapshot across items" · chuyển tiền, đặt vé
│                                          └──▶ TRANSACTIONAL  (×2)
│
├─ "must read the latest value" · "read-after-write" · "immediately after writing"
│  kiểm tồn kho trước khi trừ · check số dư 1 tài khoản
│                                          └──▶ STRONGLY CONSISTENT  (×1)
│
└─ "cost-effective" · "minimize cost" · "maximize read throughput"
   "slight delay is acceptable" · feed, catalog, đếm view, dashboard
                                              └──▶ EVENTUALLY CONSISTENT  (×0.5)
```

#### 3 bẫy dễ mất điểm nhất

1. **`Strongly consistent` có thể trả về HTTP 500** — vì buộc phải đọc leader replica; mạng/AZ sự cố thì không có bản sao thay thế. `Eventually consistent` vẫn chạy được. ⇒ Strong **đánh đổi cả availability**, không chỉ tiền.
2. **`Eventually consistent` scale tốt gấp ~3 lần** ở cùng số RCU: rẻ một nửa **và** tải rải trên cả 3 replica thay vì dồn vào leader. Đề nhắc *"maximize read throughput"* ⇒ đáp án là **eventual**, không phải tăng RCU.
3. **`GSI` không nhận `ConsistentRead=true`** ⇒ đề yêu cầu strongly consistent read theo attribute không phải partition key thì **bắt buộc `LSI`** ⇒ kéo theo **LSI phải khai lúc create table**. Chuỗi suy luận 3 bước này đề rất thích.

---

## 6. 🔐 Transactional — ACID trên DynamoDB

`TransactWriteItems` / `TransactGetItems` cho phép nhóm nhiều thao tác thành **1 đơn vị all-or-nothing**.

**Tại sao ×2?** Vì DynamoDB chạy **2-phase commit**: *prepare* → *commit*. Hai lần chạm dữ liệu ⇒ hai lần trả tiền.

> 🧠 **Memory hook:** *"Hai pha thì hai vé."*

**Giới hạn phải thuộc (đề rất hay hỏi số):**

| Giới hạn                      | Giá trị                                                                            |
| ------------------------------- | ------------------------------------------------------------------------------------- |
| Số action mỗi transaction    | **≤ 100**                                                                       |
| Tổng dung lượng               | **≤ 4 MB**                                                                      |
| Item trùng trong 1 transaction | **KHÔNG được** (không thao tác 2 lần lên cùng 1 item)                       |
| Cùng Region / cùng account   | **Bắt buộc** (transaction không xuyên Region)                                 |
| Idempotency                     | Có, qua **`ClientRequestToken`** (hiệu lực **10 phút**)                     |
| Lỗi khi xung đột              | **`TransactionCanceledException`** (kèm `CancellationReasons` giải thích lý do) |

**Các action dùng được trong `TransactWriteItems`:** `Put`, `Update`, `Delete`, **`ConditionCheck`** (chỉ kiểm tra điều kiện, không ghi).

**Phân biệt với `BatchWriteItem`:**

| | `TransactWriteItems`            | `BatchWriteItem`                                    |
| ---------------- | --------------------------------- | ----------------------------------------------------- |
| Tính nguyên tử | **ALL-or-nothing**          | **Độc lập** — 1 item fail, các item khác vẫn OK |
| Giới hạn       | 100 action / 4 MB                 | **25 item / 16 MB**                             |
| Capacity         | **×2**                      | **×1** (không giảm giá!)                        |
| Hỗ trợ Update  | Có                              | **KHÔNG** (chỉ `PutItem` / `DeleteItem`)        |

> 🧠 **Memory hook:** *"**Trans**action = **trans**fer tiền → phải toàn-hoặc-không. **Batch** = giặt cả mẻ → áo nào bẩn thì trả lại áo đó (`UnprocessedItems`)."*

---

### 6.1 🏦 Ví dụ chuyển tiền — soi cả phía ĐỌC và phía GHI

`TransactWriteItems` chạy **2 pha**: **PREPARE** (khoá item + kiểm mọi `ConditionExpression`) rồi mới **COMMIT** (áp thay đổi). Trạng thái "nửa vời" ở mục 5.2 chính là **khoảng giữa 2 pha** — và cũng là lý do capacity **×2**.

#### Phía ĐỌC — `TransactGetItems` không bao giờ thấy nửa vời

```
              TransactWriteItems (chuyển 100đ A→B)
     ┌────────── PREPARE ──────────┬────────── COMMIT ─────────┐
     │ khoá A, khoá B              │ A: 500 → 400              │
     │ kiểm ConditionExpression    │ B: 200 → 300              │
     └─────────────────────────────┴───────────────────────────┘
   t1                       t2                          t3
   │                        │                           │
   A:500  B:200             A:500  B:200 (đã KHOÁ)      A:400  B:300
   │                        │                           │
   ▼                        ▼                           ▼
TransactGetItems         TransactGetItems            TransactGetItems
 → A:500 B:200 ✓          → XUNG ĐỘT: bị cancel       → A:400 B:300 ✓
   Tổng = 700 ✓             TransactionCanceledException
                            (reason: TransactionConflict)
                            SDK tự retry → chạy lại ở t3
                            → A:400 B:300 ✓  Tổng = 700 ✓
```

**Tổng LUÔN là 700.** Không tồn tại đường nào cho ra 600.

| Cách đọc                              | Có thể ra 600?   | Vì sao                                                                     |
| ----------------------------------------- | ------------------- | ---------------------------------------------------------------------------- |
| 2 × `GetItem` **strongly consistent** | ✅ **CÓ**      | Mỗi lần đọc mới nhất, nhưng **hai lần rơi vào hai thời điểm khác nhau** |
| 1 × `TransactGetItems`                | ❌ **KHÔNG**   | Cả 2 item đọc trong **cùng một snapshot serializable**                |

#### Phía GHI — `all-or-nothing` (chỗ transaction thật sự cứu bạn)

Bây giờ **A chỉ có 50đ** mà vẫn cố chuyển 100đ.

```
❌ KHÔNG transaction — và bạn vô tình cộng B TRƯỚC:

  t1: UpdateItem B: Balance += 100      → B: 200 → 300   ✓ THÀNH CÔNG
  t2: UpdateItem A: Balance -= 100
        ConditionExpression "Balance >= 100"
        A chỉ có 50                     → ✗ ConditionalCheckFailedException

  Kết quả cuối:  A: 50   B: 300     Tổng = 350  (trước đó là 250)
                 ⚠️  100đ VỪA ĐƯỢC TẠO RA TỪ KHÔNG KHÍ
                 ⚠️  Và bạn phải tự viết code rollback cho B — rollback đó
                     cũng có thể fail → hỏng vĩnh viễn
```

```
✅ CÓ transaction — TransactWriteItems:

  PREPARE:  khoá A, khoá B
            kiểm ConditionExpression trên A: "Balance >= 100"
            A chỉ có 50  → ✗ ĐIỀU KIỆN SAI

  COMMIT:   KHÔNG BAO GIỜ CHẠY — huỷ toàn bộ

  Kết quả cuối:  A: 50   B: 200     Tổng = 250  (không đổi) ✓
                 → TransactionCanceledException
                   CancellationReasons: [
                     { Code: "ConditionalCheckFailed" },   ← A
                     { Code: "None" }                       ← B, không bị áp
                   ]
```

**B không hề bị chạm tới**, dù lệnh của B hoàn toàn hợp lệ. Không cần viết rollback.

> 🧠 **Memory hook:** *"**Không transaction = bạn phải tự viết rollback, và rollback cũng có thể fail. Có transaction = không có gì để rollback.**"*

#### Code

```json
// TransactWriteItems — chuyển tiền an toàn
{
  "TransactItems": [
    { "Update": {
        "TableName": "Accounts",
        "Key": { "AccountId": { "S": "A" } },
        "UpdateExpression": "SET Balance = Balance - :amt",
        "ConditionExpression": "Balance >= :amt",
        "ExpressionAttributeValues": { ":amt": { "N": "100" } } } },
    { "Update": {
        "TableName": "Accounts",
        "Key": { "AccountId": { "S": "B" } },
        "UpdateExpression": "SET Balance = Balance + :amt",
        "ExpressionAttributeValues": { ":amt": { "N": "100" } } } }
  ],
  "ClientRequestToken": "transfer-20260822-0001"
}
```

```json
// TransactGetItems — đọc số dư cả 2 tài khoản trong 1 snapshot
{
  "TransactItems": [
    { "Get": { "TableName": "Accounts", "Key": { "AccountId": { "S": "A" } } } },
    { "Get": { "TableName": "Accounts", "Key": { "AccountId": { "S": "B" } } } }
  ]
}
```

#### Giá của sự an toàn (item 1 KB, 1 lần/giây)

| Thao tác                                | Tính                     | Chi phí     |
| ----------------------------------------- | -------------------------- | -------------- |
| 2 × `GetItem` strongly consistent     | `ceil(1/4)=1` × 2 item   | **2 RCU** |
| 1 × `TransactGetItems` (2 item)       | `1 × 2` × 2 item         | **4 RCU** |
| 2 × `UpdateItem` riêng lẻ           | `ceil(1/1)=1` × 2 item   | **2 WCU** |
| 1 × `TransactWriteItems` (2 item)     | `1 × 2` × 2 item         | **4 WCU** |

**Trả gấp đôi để mua tính nguyên tử.** Đây là câu trả lời cho dạng đề *"giảm chi phí cho app đang dùng transaction"*: chỉ transaction cho **đúng thao tác cần nguyên tử**, còn phần đọc hiển thị/báo cáo hạ xuống eventually consistent — chênh nhau **4 lần**.

#### 🪤 Bẫy `ClientRequestToken`

Timeline phía đọc hé lộ vì sao token này bắt buộc trong thực tế: transaction bị `TransactionConflict` sẽ được **SDK retry**. Nếu request đầu **đã commit thành công** mà response mất trên đường về, retry sẽ **chuyển tiền lần thứ hai**.

- `ClientRequestToken` làm request **idempotent trong 10 phút** — DynamoDB nhận ra token trùng và trả kết quả cũ thay vì thực thi lại.
- Cùng token nhưng **khác nội dung** ⇒ **`IdempotentParameterMismatchException`**.
- ⇒ Token phải sinh từ **business ID** (mã giao dịch), **KHÔNG** phải timestamp hay UUID random mỗi lần retry.

---

### 6.2 🔓 Transaction có khoá cả bảng không? — KHÔNG, chỉ khoá từng item

**Sai lầm phổ biến:** *"đang có transaction chạy thì không tạo transaction khác được."* → **SAI**. DynamoDB **không có lock toàn cục**; xung đột chỉ ở **mức từng item**.

**Cơ chế:** DynamoDB **không** dùng *lock-and-wait* (khoá rồi bắt người sau xếp hàng) như RDBMS. Nó dùng ***abort-and-retry***: transaction sau **không chờ**, mà **bị huỷ ngay** với `TransactionConflict`, rồi SDK tự retry.
⇒ Xung đột **không làm chậm**, nó làm **fail nhanh**. Nhưng quá nhiều transaction tranh cùng 1 item ⇒ **retry storm** ⇒ throughput sụp **dù capacity còn dư**.

#### 4 tình huống — chỉ 2 trong 4 là xung đột

Giả sử `TransactWriteItems` #1 đang chuyển tiền **A → B** (đã khoá A, B):

```
┌─ 1. Transaction khác, ITEM KHÁC HẲN ──────────────────────────────┐
│  TransactWriteItems #2:  C → D                                    │
│  ✅ CHẠY SONG SONG BÌNH THƯỜNG — không liên quan gì tới A, B     │
│  (DynamoDB xử lý hàng nghìn transaction/giây đồng thời như vậy)   │
└───────────────────────────────────────────────────────────────────┘

┌─ 2. Transaction khác, CHẠM CÙNG item A ───────────────────────────┐
│  TransactWriteItems #2:  A → C                                    │
│  ❌ XUNG ĐỘT → 1 trong 2 bị cancel                               │
│     TransactionCanceledException                                  │
│     CancellationReasons: [{ Code: "TransactionConflict" }]        │
│  → SDK tự retry → thành công sau khi #1 xong                      │
└───────────────────────────────────────────────────────────────────┘

┌─ 3. Ghi ĐƠN LẺ (không transaction) vào A ─────────────────────────┐
│  UpdateItem A: Balance += 50                                      │
│  ❌ CŨNG BỊ XUNG ĐỘT → TransactionConflictException              │
│  (write đơn lẻ cũng serializable với transaction — không lách được)│
└───────────────────────────────────────────────────────────────────┘

┌─ 4. ĐỌC (không transaction) item A ───────────────────────────────┐
│  GetItem / Query / Scan trên A                                    │
│  ✅ KHÔNG BỊ CHẶN — vẫn đọc được ngay                           │
│  Chỉ là: thấy giá trị TRƯỚC hoặc SAU, không thấy nửa vời         │
│  → Reader KHÔNG BAO GIỜ block writer, writer không block reader   │
└───────────────────────────────────────────────────────────────────┘
```

| Thao tác đồng thời                          | Item                | Kết quả                                          |
| ------------------------------------------------ | ------------------- | --------------------------------------------------- |
| Transaction khác                              | **khác** item | ✅ Chạy song song, không ảnh hưởng            |
| Transaction khác                              | **cùng** item | ❌ `TransactionConflict` → cancel → SDK retry  |
| `PutItem` / `UpdateItem` / `DeleteItem`        | **cùng** item | ❌ `TransactionConflictException`                 |
| `GetItem` / `Query` / `Scan` (mọi consistency) | cùng item         | ✅ **KHÔNG bị chặn**                        |

> 🧠 **Memory hook:** *"**Transaction không khoá cả bảng — chỉ khoá đúng những item nó chạm.** Và người đọc thì không bao giờ bị khoá."*

#### 🪤 Đừng nhầm 2 loại lỗi này

Trong **CÙNG MỘT** transaction thì **không được** chạm 1 item hai lần:

```
❌ TransactItems: [ Update A -= 100, Update A += 50 ]
   → ValidationException: "Transaction request cannot include
      multiple operations on one item"
   (Lỗi VALIDATION lúc gửi request — KHÔNG phải xung đột runtime)
```

|                    | Cùng item trong **1** transaction   | Cùng item ở **2** transaction khác nhau        |
| ------------------ | ------------------------------------------ | ------------------------------------------------------ |
| Lỗi              | **`ValidationException`**            | **`TransactionCanceledException`** (`TransactionConflict`) |
| Khi nào          | **Ngay lúc gửi** — sai từ đầu     | **Runtime** — tuỳ timing                          |
| Sửa thế nào    | Gộp thành **1 `UpdateExpression`**   | **Retry** (SDK làm sẵn)                          |

#### 💡 Nguyên tắc thiết kế suy ra được (đề hay hỏi ẩn)

- **"Hot item" phiên bản transaction:** nếu mọi giao dịch đều update **một item tổng** (`TotalBalance` toàn hệ thống) thì mọi transaction tranh nhau item đó → `TransactionConflict` tăng vọt → throughput sụp **dù capacity còn dư**.
  - **Theo dõi:** CloudWatch metric **`TransactionConflict`**.
  - **Chữa:** **sharding** item tổng thành N item con (`TotalBalance#0..#9`) rồi cộng lại khi đọc — cùng tư duy với **write sharding** chữa hot partition (mục 10).
- **Chỉ cần đảm bảo 1 item duy nhất?** ⇒ **ĐỪNG** dùng transaction. Dùng **conditional write + optimistic locking (version number)**: chi phí **×1** thay vì **×2**.

---

## 7. ✍️ 12 ví dụ có lời giải (tăng dần độ khó)

| # | Đề bài                                                        | Lời giải                                | Đáp án        |
| - | ---------------------------------------------------------------- | ----------------------------------------- | ---------------- |
| 1 | Đọc item **8 KB**, strong, **10 req/s**                | `ceil(8/4)=2` → `2×10`                 | **20 RCU**  |
| 2 | Cùng trên, **eventual**                                    | `20 ÷ 2`                                | **10 RCU**  |
| 3 | Cùng trên, **transactional**                               | `2 × 2 × 10`                            | **40 RCU**  |
| 4 | Ghi item **3 KB**, **6 req/s**                           | `ceil(3/1)=3` → `3×6`                  | **18 WCU**  |
| 5 | Cùng trên, **transactional**                               | `18 × 2`                                | **36 WCU**  |
| 6 | Ghi item **0.5 KB**, **100 req/s** 🪤                    | `ceil(0.5/1)=1` (KHÔNG có 0.5 WCU)     | **100 WCU** |
| 7 | Đọc item **1 KB**, strong, **100 req/s** 🪤            | `ceil(1/4)=1` — lãng phí 3 KB          | **100 RCU** |
| 8 | Cùng trên, **eventual**                                    | `100 ÷ 2`                               | **50 RCU**  |
| 9 | Đọc item **6 KB**, eventual, **30 req/s**              | `ceil(6/4)=2` → `60 ÷ 2`               | **30 RCU**  |
| 10 | Đọc item **9 KB**, eventual, **1 req/s** 🪤           | `ceil(9/4)=3` → `3÷2=1.5` → **ceil** | **2 RCU**   |
| 11 | `Query` trả **100 item × 2 KB**, strong 🪤            | Tròn trên **TỔNG 200 KB**: `ceil(200/4)` | **50 RCU**  |
| 12 | So sánh: **100 lần `GetItem`** item 2 KB, strong 🪤 | `ceil(2/4)=1` mỗi lần → `1×100`      | **100 RCU** |

**Ví dụ 11 vs 12 là điểm ăn tiền của đề thi:** cùng đọc 200 KB nhưng `Query` chỉ tốn **một nửa** so với 100 `GetItem` riêng lẻ, vì `Query` **làm tròn 4 KB trên tổng**, còn `GetItem` làm tròn **từng item**.

> 🧠 **Memory hook:** *"`Query` gộp rồi mới tròn — `GetItem` tròn từng cái. Item nhỏ hơn 4 KB thì càng gộp càng lời."*

---

## 8. 📄 `Query` / `Scan` — làm tròn trên TỔNG

| Điều cần nhớ                            | Chi tiết                                                                                        |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| Làm tròn                                  | Trên **tổng kích thước item đã ĐỌC**, bội số 4 KB                                    |
| Trang tối đa                             | **1 MB** mỗi lần gọi                                                                      |
| RCU của 1 trang đầy                     | `1 MB / 4 KB` = **256 RCU** (strong) · **128 RCU** (eventual)                          |
| **`FilterExpression`** 🪤                 | Áp dụng **SAU** khi đọc ⇒ **vẫn trả tiền cho dữ liệu bị loại bỏ**              |
| Pagination                                  | Còn dữ liệu → trả **`LastEvaluatedKey`** → truyền vào **`ExclusiveStartKey`** |
| `Scan` 🪤                                 | Đọc **toàn bảng** → tốn RCU khủng; `Query` luôn được ưu tiên                   |
| `ProjectionExpression` / `Select` 🪤       | **KHÔNG** giảm RCU (chỉ giảm băng thông trả về)                                    |
| Cách thật để giảm RCU                  | Dùng **`Query` + đúng key**, hoặc **GSI/LSI projection hẹp** (item index nhỏ hơn)  |

> 🧠 **Memory hook:** *"**Filter là cái rổ đặt SAU máy đếm tiền** — lọc bao nhiêu cũng đã trả tiền rồi."*

---

## 9. 🧭 Capacity đi đâu: Index, DAX, Streams, Batch

| Thành phần            | Capacity                                                                                                                                     |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- |
| **LSI**            | **DÙNG CHUNG** WCU/RCU với bảng gốc · hỗ trợ **strongly consistent** · phải tạo **lúc create table** · tối đa **5** |
| **GSI**            | **RIÊNG** WCU/RCU · **CHỈ eventually consistent** 🪤 · tạo/xoá **bất kỳ lúc nào** · mặc định **20**             |
| **Ghi vào GSI** 🪤 | 1 write vào bảng → **cộng thêm** WCU trên **từng GSI** có attribute liên quan (tính theo **size của item trong index**)         |
| **GSI hết WCU** 🪤 | **Throttle lan sang cả bảng gốc** — write vào table bị chặn! (không xảy ra với on-demand)                                       |
| **`DAX`**          | Cache hit → **0 RCU** · chỉ tăng tốc **eventually consistent** read · strongly consistent read **đi thẳng** xuống table 🪤    |
| **Streams**        | Đọc stream **KHÔNG** tiêu RCU của bảng (có read request unit riêng của stream)                                                  |
| **`BatchGetItem`** | Tổng RCU từng item, **KHÔNG giảm giá** · ≤ **100 item / 16 MB** · hỗ trợ `ConsistentRead` theo từng bảng               |
| **`BatchWriteItem`** | Tổng WCU từng item, **KHÔNG giảm giá** · ≤ **25 item / 16 MB** · trả `UnprocessedItems`                                  |
| **`UpdateItem`** 🪤 | Tính theo **kích thước LỚN HƠN** giữa trước và sau khi update                                                              |
| **`UpdateItem` đổi attribute đang được GSI index** 🪤 | GSI phải **XOÁ entry cũ + GHI entry mới** ⇒ tốn WCU cho **CẢ HAI**                                       |
| **Conditional write fail** 🪤 | **VẪN tiêu WCU** (và tính vào `ConsumedCapacity`)                                                                                |

---

## 10. ⚠️ Bẫy hay gặp trong đề DVA-C02

1. **Không có capacity lẻ ở mức mỗi request** — item 100 bytes vẫn tốn **1 WCU**.
2. **Eventual không phải "một nửa của mọi thứ"** — chia 2 **sau** khi đã làm tròn cỡ, rồi **làm tròn lên** lần nữa (ví dụ #10).
3. **Transactional read = 2× strong = 4× eventual**, không phải "×2 so với eventual".
4. **`FilterExpression` không tiết kiệm capacity.**
5. **GSI chỉ eventually consistent** — đề hỏi "strongly consistent read trên attribute phụ" ⇒ **LSI**, không phải GSI.
6. **LSI không thêm được sau khi tạo bảng** ⇒ đề nói "bảng đã production, cần query theo field mới" ⇒ **GSI**.
7. **GSI bị throttle sẽ throttle luôn table** (chế độ provisioned).
8. **`DAX` không giúp strongly consistent read**, cũng không giúp write.
9. **Item tối đa `400 KB`** — lớn hơn thì lưu `S3` + giữ pointer trong item.
10. **Giới hạn mỗi partition: `3000 RCU` / `1000 WCU` / `10 GB`** — vượt là **hot partition** dù table còn dư capacity ⇒ sửa bằng **thiết kế partition key** (high-cardinality, write sharding / thêm suffix ngẫu nhiên).
11. **On-demand dùng tên khác nhưng cùng công thức**: `RRU` (Read Request Unit) / `WRU` (Write Request Unit) — cũng 4 KB / 1 KB, cũng ÷2 và ×2.
12. **Throttle không phải lúc nào cũng do thiếu capacity** — `ProvisionedThroughputExceededException` ⇒ xử lý bằng **exponential backoff + jitter** (SDK đã có sẵn retry), rồi mới nghĩ đến tăng capacity / Auto Scaling / DAX.

---

## 11. 🔄 Tính NGƯỢC (đề cũng hay hỏi kiểu này)

**Cho trước capacity → hỏi được bao nhiêu request/giây?**

```
Số read/giây (strong)   = RCU / ceil(size / 4KB)
Số read/giây (eventual) = 2 × RCU / ceil(size / 4KB)
Số write/giây           = WCU / ceil(size / 1KB)
```

| Ví dụ                                                      | Lời giải                       | Đáp án           |
| ------------------------------------------------------------- | -------------------------------- | ------------------- |
| Bảng có **100 RCU**, item **4 KB**, eventual → ? read/s | `2 × 100 / 1`                  | **200 read/s** |
| Bảng có **100 RCU**, item **10 KB**, strong → ? read/s  | `100 / ceil(10/4)=100/3`       | **33 read/s**  |
| Bảng có **50 WCU**, item **2.5 KB** → ? write/s         | `50 / ceil(2.5/1)=50/3`        | **16 write/s** |
| Bảng có **60 WCU**, transactional write item 1 KB → ?    | `60 / (1×2)`                   | **30 write/s** |

---

## 12. 🎯 Flashcard 30 giây (đọc trước khi vào phòng thi)

```
GHI 1 KB · ĐỌC 4 KB
eventual ÷2 · strong ×1 · transactional ×2
LÀM TRÒN LÊN — hai lần (mỗi request, và tổng)

Query/Scan: tròn trên TỔNG · 1 trang = 1 MB = 256 RCU strong / 128 eventual
Filter & Projection: KHÔNG giảm RCU
UpdateItem: tính theo size LỚN HƠN · Conditional fail: VẪN tốn WCU

Transaction: 100 action / 4 MB / ×2 capacity / ClientRequestToken 10 phút
Batch: get 100 item–16 MB · write 25 item–16 MB · KHÔNG giảm giá · KHÔNG atomic

GSI: capacity RIÊNG · CHỈ eventual · tạo bất kỳ lúc nào · 20/bảng
LSI: capacity CHUNG · strong OK · CHỈ lúc create table · 5/bảng

Item ≤ 400 KB · Partition ≤ 3000 RCU / 1000 WCU / 10 GB
Burst: giữ 300 giây capacity chưa dùng
Throttle → exponential backoff + jitter → rồi mới scale/DAX
```

---

## 13. 📝 Bài tập tự luyện — ĐÃ GIẢI (lần 1: 2026-08-22 · **4/5**)

| # | Đề bài                                                        | Cách tính                                                          | Đáp án            | ✔ |
| - | ---------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------- | - |
| 1 | read **12 KB**, eventual, **25 req/s**                 | `ceil(12/4)=3` → `3×25=75` → `75÷2=37.5` → **ceil**          | **38 RCU**     | ✅ |
| 2 | write **1.2 KB**, transactional, **40 req/s**           | `ceil(1.2/1)=2` → `2×40=80` → `×2`                             | **160 WCU**    | ✅ |
| 3 | `Query` **500 item × 1 KB**, strong, **2 lần/s**  | tròn trên **TỔNG 500 KB**: `ceil(500/4)=125` → `×2`          | **250 RCU**    | ✅ |
| 4 | **200 RCU**, item **7 KB**, strong → ? read/s     | `ceil(7/4)=2` → `200÷2`                                          | **100 read/s** | ✅ |
| 5 | write **3 KB**, **2 GSI** (ALL), **10 req/s**     | table `3×10=30` · GSI1 `30` · GSI2 `30`                        | **90 WCU**     | ❌ |

**Đã làm đúng (đây là 2 chỗ hay sai nhất):**
- Bài 1: làm tròn `37.5 → 38` **ở CUỐI**, không phải trước khi chia 2.
- Bài 3: tròn trên **TỔNG 500 KB**, không phải từng item (nếu tròn từng item sẽ ra 500 RCU — gấp đôi). Lưu ý thêm: 500 KB < 1 MB nên vừa **1 trang**, không cần pagination.

#### ❌ Bài 5 — sai ở đâu: bỏ quên chính BẢNG GỐC

```
Ghi 1 item 3 KB, 10 req/s, bảng có 2 GSI (projection ALL):

  ┌─────────────────┐
  │  TABLE Orders   │  ceil(3/1)=3 × 10  =  30 WCU   ← BỊ BỎ QUÊN
  └────────┬────────┘
           │ (DynamoDB tự động ghi tiếp)
     ┌─────┴─────┐
     ▼           ▼
  ┌──────┐   ┌──────┐
  │ GSI1 │   │ GSI2 │  mỗi cái: ceil(3/1)=3 × 10 = 30 WCU
  └──────┘   └──────┘

  Tổng phải provision = 30 (table) + 30 (GSI1) + 30 (GSI2) = 90 WCU
```

Đây là **3 pool RIÊNG BIỆT**, không phải 1 con số 90 dùng chung: khai `30 WCU` cho table, `30 WCU` cho GSI1, `30 WCU` cho GSI2. Và **GSI hết WCU sẽ throttle luôn write vào table gốc** (mục 9).

#### 🧠 Bài học gốc rễ: **GSI là một BẢNG RIÊNG**

Về mặt vật lý, GSI là một bảng độc lập mà DynamoDB tự đồng bộ giúp bạn.
⇒ **"Ghi 1 item" thực chất là ghi N+1 item**, với N = số GSI có index attribute đó.

| Tình huống                             | WCU mỗi write             |
| ---------------------------------------- | --------------------------- |
| Bảng **0 GSI**                    | **1×**                |
| Bảng **2 GSI** (projection ALL)   | **3×**                |
| Bảng **5 GSI** (projection ALL)   | **6×**                |
| Bảng 2 GSI nhưng **`KEYS_ONLY`** | table 3 WCU + 1 + 1 = **5 WCU/req** thay vì 9 |

⇒ Đáp án cho dạng đề *"chi phí write tăng vọt sau khi thêm index"*: **giảm số GSI**, hoặc **thu hẹp projection** (`KEYS_ONLY` / `INCLUDE`) để **item trong index nhỏ đi**.

> 🧠 **Memory hook:** *"**Mỗi GSI là một bảng nữa phải ghi.** Projection càng rộng, bảng đó càng nặng."*

---

## 14. 📝 Bài tập vòng 2 (làm sau 3 ngày)

| # | Đề bài                                                                                                      | Cách tính | Đáp án |
| - | -------------------------------------------------------------------------------------------------------------- | ----------- | --------- |
| 1 | Đọc item **5 KB**, **transactional**, **12 req/s** → RCU?                                    |             |           |
| 2 | `Scan` đọc hết **1 MB**, **eventually consistent**, **1 lần/s** → RCU?                  |             |           |
| 3 | `UpdateItem` đổi item từ **2 KB → 6 KB**, **8 req/s** → WCU?                                |             |           |
| 4 | Bảng **300 WCU**, item **2 KB**, **transactional** write → được bao nhiêu write/s?      |             |           |
| 5 | Ghi item **4 KB**, 10 req/s, bảng có **1 GSI `KEYS_ONLY`** (index item ~0.2 KB) → WCU table & GSI? |             |           |
| 6 | `UpdateItem` **3 KB** làm **đổi giá trị attribute đang được GSI index** (index item 3 KB), 5 req/s → WCU trên GSI? |             |           |
