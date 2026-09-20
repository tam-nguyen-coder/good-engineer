# KIP-1066 — Mechanism to cordon brokers and log directories

> **Nguồn (official):** https://cwiki.apache.org/confluence/spaces/KAFKA/pages/311627566/KIP-1066+Mechanism+to+cordon+brokers+and+log+directories · lệnh đã được xác nhận trong https://kafka.apache.org/43/operations/basic-kafka-operations/ (mục *Decommissioning*) · config đã được xác nhận trong https://docs.confluent.io/platform/current/installation/configuration/broker-configs.html
> **Tuần:** 2 — Cluster Config I · **Loại:** KIP (Apache cwiki)
> ⚠️ Trang cwiki **không crawl trực tiếp được** (WebFetch trả về rỗng ở cả hai dạng URL). Phần tóm tắt dưới đây tổng hợp từ **kết quả tìm kiếm trên chính cwiki** cộng với **lệnh và config đã xác minh trên docs Apache Kafka 4.3 + Confluent config reference**. Mọi tên config và lệnh đều đã đối chiếu ít nhất một nguồn chính thức.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **"Cordon" mượn thẳng thuật ngữ từ Kubernetes.** Một log directory bị cordon **vẫn hoạt động đầy đủ** cho các partition đang nằm trên đó — chỉ là **không nhận partition mới** nữa. Đây là điểm khác biệt quan trọng với "log dir offline" (ổ hỏng, partition trên đó chết).
- Config mới: **`cordoned.log.dirs`** — kiểu `list`, mặc định `""` (rỗng), update mode **`per-broker`**. Đặt được trong file properties lúc khởi động **và** sửa nóng qua Admin client / `kafka-configs.sh`.
- **Cordon cả broker** = đặt `cordoned.log.dirs="*"`. Nếu mọi log dir của broker đều bị cordon thì broker đó coi như bị cordon: không partition mới nào được giao cho nó.
- Khi reassignment cố đặt replica lên broker **không còn log dir nào chưa cordon**, request bị trả lỗi **`INELIGIBLE_REPLICA`**.
- **Dùng khi nào:** thu nhỏ cluster (decommission broker), rút một ổ đĩa ra để thay, hoặc "đóng băng" một ổ sắp đầy trong lúc bạn đang reassign bớt partition đi nơi khác. Thứ tự chuẩn: **cordon → chuyển replica đi → `kafka-cluster.sh unregister`**.
- Cordon **không tự di chuyển** partition đang có. Nó chỉ chặn *thêm* — muốn rỗng ổ đĩa vẫn phải `kafka-reassign-partitions.sh`.
- Kafka **4.3** là bản có sẵn cả config lẫn ví dụ trong mục *Decommissioning* của trang Basic Kafka Operations.

---

## 📄 Nội dung (trích từ tài liệu gốc — phần tổng hợp, không crawl được nguyên văn KIP)

### Motivation

Trước KIP-1066, khi muốn rút một broker hoặc một ổ đĩa ra khỏi cluster, người vận hành không có cách nào nói với controller "đừng đặt thêm partition lên đây nữa". Kết quả: trong lúc đang `kafka-reassign-partitions.sh` chuyển replica đi, topic mới tạo hoặc partition mới thêm lại tiếp tục rơi vào đúng chỗ đang muốn dọn — một cuộc đua không bao giờ kết thúc.

### Proposal (theo tóm tắt của cwiki)

> KIP-1066 proposes introducing the concept of "cordoned" log directories, reusing the "cordon" terminology from Kubernetes.
>
> When a log directory is cordoned, it still fully functions but no new partitions can be allocated on it. If all the log directories of a broker are cordoned, the broker is effectively cordoned and no new partitions can be assigned to that broker.
>
> Cluster operators will be able to set the `cordoned.log.dirs` configuration on each broker, which can be set in the broker properties files when it is started and updated at runtime via the Admin client or using the `kafka-configs.sh` tool. This can also be set to `*` to cordon all log directories.
>
> When reassigning partitions between brokers, if the request places partitions on brokers with no uncordoned log directories, the `INELIGIBLE_REPLICA` error will be returned.

### Config (đã xác minh ở Confluent Broker Config Reference)

| Config | Type | Default | Update Mode |
|---|---|---|---|
| `cordoned.log.dirs` | list | `""` | per-broker |

### Lệnh (nguyên văn từ `/43/operations/basic-kafka-operations/`)

Cordon **một log directory** trên broker 1:

```
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --alter \
  --add-config cordoned.log.dirs=/data/dir1 --entity-type brokers --entity-name 1
```

Cordon **cả broker** 1:

```
$ bin/kafka-configs.sh --bootstrap-server localhost:9092 --alter \
  --add-config cordoned.log.dirs="*" --entity-type brokers --entity-name 1
```

Gỡ cordon khi broker **đang offline** (nói thẳng với controller):

```
$ bin/kafka-configs.sh --bootstrap-controller localhost:9093 --alter \
  --delete-config cordoned.log.dirs --entity-type brokers --entity-name 1
```

Sau khi đã chuyển hết replica ra khỏi broker, gỡ đăng ký nó:

```
$ bin/kafka-cluster.sh unregister --bootstrap-server localhost:9092 --id 1
```

### KIP liên quan (cùng họ JBOD/log dir)

| KIP | Nội dung |
|---|---|
| **KIP-112** | Handle disk failure for JBOD — nền tảng của "một ổ hỏng chỉ làm offline partition trên ổ đó" |
| **KIP-113** | Support replicas movement between log directories — cho phép `kafka-reassign-partitions.sh` chỉ định `(broker, log_dir)` |
| **KIP-849** | Expose logdirs **total and usable space** via `kafka-log-dirs.sh` — lý do output của tool có thêm dung lượng ổ đĩa |
| **KIP-928** | Making Kafka resilient to log directories becoming full |
| **KIP-1066** | Cordon brokers and log directories (`cordoned.log.dirs`) |
