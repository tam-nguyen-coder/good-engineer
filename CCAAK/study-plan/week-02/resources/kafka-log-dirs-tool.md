# `kafka-log-dirs.sh` — đọc phân bố partition trên nhiều `log.dirs`

> **Nguồn (official):** https://docs.confluent.io/kafka/operations-tools/kafka-tools.html (mục `kafka-log-dirs`) · https://cwiki.apache.org/confluence/display/KAFKA/KIP-113:+Support+replicas+movement+between+log+directories · https://cwiki.apache.org/confluence/display/KAFKA/KIP-849:+Expose+logdirs+total+and+usable+space+via+kafka-log-dirs.sh
> **Tuần:** 2 — Cluster Config I · **Loại:** Confluent CLI reference + KIP
> ⚠️ Danh sách option crawl được từ Confluent CLI reference. **Hai trang cwiki của KIP-113 / KIP-849 không crawl trực tiếp được** — phần JSON output và ngữ nghĩa các trường tổng hợp từ kết quả tìm kiếm trên chính cwiki; kiểm lại bằng cách chạy `kafka-log-dirs.sh --describe` trên cluster lab.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- `kafka-log-dirs.sh --describe` là **công cụ duy nhất** trả lời được câu "partition nào đang nằm ở ổ nào và chiếm bao nhiêu byte". Khi đề mô tả "một broker sắp đầy đĩa", đây là bước chẩn đoán đầu tiên — **trước** khi nghĩ tới reassign.
- Output là **JSON**: `brokers[] → logDirs[] → partitions[]`. Mỗi log dir có `logDir`, `error`, và (từ **KIP-849**) `totalBytes` / `usableBytes`. Mỗi partition có `partition`, `size`, `offsetLag`, `isFuture`.
- Trường **`error`** của một log dir khác `null` chính là dấu hiệu **ổ đó đang offline** — ghép với metric `OfflineLogDirectoryCount` > 0.
- Trường **`isFuture: true`** nghĩa là replica đang **được copy sang log dir khác** (KIP-113). Thấy nó tức là một lệnh di chuyển giữa các ổ đang chạy dở.
- **Di chuyển replica giữa các ổ trên cùng broker** dùng `kafka-reassign-partitions.sh` với JSON có trường **`log_dirs`** song song với `replicas` (số phần tử phải bằng nhau; `"any"` = để Kafka tự chọn).
- Nhớ khác biệt: `kafka-log-dirs.sh` **chỉ đọc**, không di chuyển gì. Việc di chuyển là của `kafka-reassign-partitions.sh`; việc chặn partition mới là của `cordoned.log.dirs` (KIP-1066).

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Options (Confluent CLI reference, nguyên văn)

| Option | Mô tả |
|---|---|
| `--bootstrap-server` (REQUIRED) | "the servers to use for bootstrapping" |
| `--broker-list` | "The list of brokers to be queried in the form '0,1,2'" |
| `--topic-list` | "The list of topics to be queried in the form 'topic1,topic2,topic3'" |
| `--describe` | "Describe the specified log directories on the specified brokers" |
| `--command-config` | Property file for Admin Client configurations |
| `--help` / `--version` | Print usage / display Kafka version |

**Example command:**

```bash
bin/kafka-log-dirs.sh --bootstrap-server host1:9092 --describe --broker-list 0,1,2
```

### JSON output — version 1

```json
{
  "version": 1,
  "brokers": [
    {
      "broker": 1,
      "logDirs": [
        {
          "logDir": "/tmp/kraft-combined-logs",
          "error": null,
          "partitions": [
            {
              "partition": "foo-0",
              "size": 0,
              "offsetLag": 0,
              "isFuture": false
            }
          ]
        }
      ]
    }
  ]
}
```

### JSON output — version 2 (KIP-849)

Từ KIP-849, mỗi phần tử `logDirs` có thêm **`totalBytes`** và **`usableBytes`** — dung lượng tổng và dung lượng còn dùng được của ổ chứa thư mục đó. Đây là cách duy nhất biết ổ nào sắp đầy mà không cần SSH vào máy.

### Di chuyển replica giữa các log dir (KIP-113)

File JSON đưa cho `kafka-reassign-partitions.sh --execute` có thêm trường `log_dirs`:

```json
{
  "version": 1,
  "partitions": [
    {
      "topic": "orders",
      "partition": 0,
      "replicas": [2, 3, 4],
      "log_dirs": ["/var/lib/kafka/data-2", "any", "any"]
    }
  ]
}
```

- Số phần tử của `log_dirs` **phải bằng** số phần tử của `replicas`, xếp theo đúng thứ tự.
- `"any"` = giữ nguyên / để broker tự chọn thư mục.
- Trong lúc copy, `kafka-log-dirs.sh --describe` sẽ hiện replica đích với `isFuture: true`; xong thì nó thay thế bản cũ.

### Cách broker chọn log dir cho partition mới

Theo `/43/operations/hardware-and-os/`: *"partitions will be assigned round-robin to data directories. Each partition will be entirely in one of the data directories."* Cụ thể, partition mới rơi vào thư mục **đang có ít partition nhất**.

> ⚠️ **Đây là bẫy trung tâm của Tuần 2:** tiêu chí là **số partition**, không phải **dung lượng trống**. Một ổ 200 GB đã đầy 190 GB nhưng chỉ giữ 3 partition vẫn có thể nhận partition mới trước một ổ trống trơn đang giữ 10 partition. Cách xử lý: `kafka-log-dirs.sh` để nhìn, `cordoned.log.dirs` để chặn, `kafka-reassign-partitions.sh` + `log_dirs` để dọn.
