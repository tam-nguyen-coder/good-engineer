# Apache Kafka 4.3 — KRaft Operations: quorum status, membership change, debugging metadata

> **Nguồn (official):** https://kafka.apache.org/43/operations/kraft/
> **Tuần:** 7 — Observability + Troubleshooting playbook · **Loại:** Apache Kafka Docs (§6.10 KRaft)
> ⚠️ Nội dung dưới đây được crawl tự động (HTTP → Markdown, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Lệnh đầu tiên khi nghi ngờ controller:** `kafka-metadata-quorum.sh describe --status`. Output cho `ClusterId`, `LeaderId`, `LeaderEpoch`, `HighWatermark`, **`MaxFollowerLag`**, `CurrentVoters`, `CurrentObservers`. `LeaderId` = **-1** hoặc epoch nhảy liên tục = quorum đang không bầu được leader.
- Phân biệt **voter** và **observer**: controller trong `controller.quorum.voters` (hoặc quorum động) là voter; **broker luôn là observer** của `__cluster_metadata` — broker xuất hiện ở `CurrentObservers` là bình thường, không phải lỗi.
- **Quy tắc đa số:** *"A majority of the controllers must be alive in order to maintain availability. With 3 controllers, the cluster can tolerate 1 controller failure; with 5 controllers, the cluster can tolerate 2 controller failures."* Muốn chịu N lỗi đồng thời → cần **2N + 1** controller. Vì vậy quorum luôn là số **lẻ**: 3 hoặc 5.
- Mất đa số quorum → **control plane đóng băng** (không tạo topic, không bầu leader mới, không đăng ký broker), nhưng **data plane vẫn phục vụ** produce/fetch cho partition không cần đổi leader, vì broker dùng metadata đã cache.
- Quorum **động** (KIP-853): thêm/bớt controller lúc chạy bằng `kafka-metadata-quorum.sh add-controller` / `remove-controller --controller-id <id> --controller-directory-id <dir-id>`. Theo dõi replica mới bắt kịp bằng `describe --replication`.
- **2 công cụ debug metadata**: `kafka-dump-log.sh --cluster-metadata-decoder --files .../__cluster_metadata-0/*.log` (đọc bản ghi metadata dạng text) và `kafka-metadata-shell.sh --snapshot <snapshot-file>` (duyệt metadata như filesystem). Dùng khi cần trả lời "controller **nghĩ** partition này đang ở đâu".
- `--bootstrap-controller` cho phép nói chuyện **thẳng** với controller khi broker đang hỏng — rất hữu ích khi broker không join được cluster.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Describing the quorum

The `kafka-metadata-quorum` tool can be used to describe the runtime state of the cluster metadata partition:

```bash
$ bin/kafka-metadata-quorum.sh --bootstrap-server localhost:9092 describe --status
ClusterId:              fMCL8kv1SWm87L_Md-I2hg
LeaderId:               3002
LeaderEpoch:            2
HighWatermark:          10
MaxFollowerLag:         0
MaxFollowerLagTimeMs:   -1
CurrentVoters:          [{"id": 3000, "directoryId": "ILZ5MPTeRWakmJu99uBJCA", "endpoints": ["CONTROLLER://localhost:9093"]},
                         {"id": 3001, "directoryId": "b-DwmhtOheTqZzPoh52kfA", "endpoints": ["CONTROLLER://localhost:9094"]},
                         {"id": 3002, "directoryId": "g42deArWBTRM5A1yuVpMCg", "endpoints": ["CONTROLLER://localhost:9095"]}]
CurrentObservers:       [{"id": 0, "directoryId": "3Db5QLSqSZieL3rJBUUegA"},
                         {"id": 1, "directoryId": "UegA3Db5QLSqSZieL3rJBU"},
                         {"id": 2, "directoryId": "L3rJBUUegA3Db5QLSqSZie"}]
```

The replication status of each voter and observer can be inspected with:

```bash
$ bin/kafka-metadata-quorum.sh --bootstrap-server localhost:9092 describe --replication
```

### Controller membership changes

Controllers can be added to the cluster metadata partition dynamically:

```bash
$ bin/kafka-metadata-quorum.sh --bootstrap-server localhost:9092 add-controller
```

or, when the brokers are not reachable, by talking directly to a controller:

```bash
$ bin/kafka-metadata-quorum.sh --bootstrap-controller localhost:9093 add-controller
```

Controllers can be removed from the cluster metadata partition by running:

```bash
$ bin/kafka-metadata-quorum.sh --bootstrap-server localhost:9092 remove-controller --controller-id <id> --controller-directory-id <directory-id>
```

You can monitor the replication to the new controller with `describe --replication`.

### Fault tolerance of the quorum

A majority of the controllers must be alive in order to maintain availability. With 3 controllers, the cluster can tolerate 1 controller failure; with 5 controllers, the cluster can tolerate 2 controller failures.

If a majority of the controllers is unavailable for an extended period of time, controller operations — such as creating topics or electing new partition leaders — will not be possible.

For a Kafka cluster to be able to tolerate N concurrent controller failures, at least 2N + 1 controllers must be provisioned.

### Debugging

#### Metadata log decoding

Dump the cluster metadata log with the dedicated decoder:

```bash
$ bin/kafka-dump-log.sh --cluster-metadata-decoder --files metadata_log_dir/__cluster_metadata-0/00000000000000000000.log
```

#### Metadata shell

Inspect a metadata snapshot interactively:

```bash
$ bin/kafka-metadata-shell.sh --snapshot metadata_log_dir/__cluster_metadata-0/00000000000000000000-0000000001.checkpoint
>> ls /
brokers  local  metadataQuorum  topicIds  topics
>> cat /brokers/0/registration
...
```

### Notes on storage and cluster identity

Each node's storage directory must be formatted with `kafka-storage.sh format` using the **same cluster id**. A node whose `meta.properties` contains a different cluster id than the rest of the cluster will refuse to start.
