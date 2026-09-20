# 🧪 Hands-on Labs — Tuần 1: Nền tảng vận hành + `KRaft` in production

> Lab cầm tay chỉ việc, chạy **hoàn toàn local** bằng Docker — không tốn phí. LUÔN chạy phần Dọn dẹp cuối mỗi lab (trừ khi lab sau nói "giữ cluster").
> 🔥 **Hai lab đánh dấu 💥 là lab "gây hỏng rồi sửa"** — bạn cố tình phá cluster rồi chẩn đoán và khôi phục. Đây là phần quan trọng nhất của tuần: đề CCAAK hỏi *hành động của người vận hành*, và phản xạ đó chỉ hình thành khi tay bạn đã từng run.
> ⚙️ Yêu cầu chung: macOS/Linux/WSL2, **Docker Desktop** (hoặc Docker Engine + Compose v2), ~4 GB RAM trống cho 4 container.
> Về [plan tuần](README.md) · [Câu hỏi luyện tập](questions.md) · [Kế hoạch tổng](../../CCAAK-STUDY-PLAN.md)

---

## 🔧 Chuẩn bị chung

Tuần này **không dựng compose mới**. Dùng lại nguyên si hai file compose chuẩn bạn đã tạo ở [CCDAK Tuần 1](../../../CCDAK/study-plan/week-01/labs.md) trong thư mục `~/kafka-labs/`.

```bash
cd ~/kafka-labs
ls docker-compose.single.yml docker-compose.cluster.yml    # cả hai phải tồn tại
mkdir -p week-01-ccaak && cd week-01-ccaak
docker --version && docker compose version
```

> ❗ Nếu thiếu file compose: quay lại [CCDAK Tuần 1 Lab 1.1 và 1.2](../../../CCDAK/study-plan/week-01/labs.md) tạo chúng trước. **Đừng chép lại nội dung compose vào đây** — cả bộ CCAAK tham chiếu đúng hai file gốc đó, sửa một chỗ là mọi tuần được hưởng.

### Sơ đồ cluster dùng cho cả tuần (`docker-compose.cluster.yml`)

| Container | `node.id` | `process.roles` | Cổng host | Địa chỉ trong docker network |
|---|---|---|---|---|
| `controller` | **1** | **`controller`** (thuần, không nhận produce/fetch) | — | `controller:9093` (listener `CONTROLLER`) |
| `kafka-1` | **2** | `broker` | **9092** | `kafka-1:19092` |
| `kafka-2` | **3** | `broker` | **9094** | `kafka-2:19092` |
| `kafka-3` | **4** | `broker` | **9096** | `kafka-3:19092` |

- `CLUSTER_ID` dùng chung: **`MkU3OEVBNTcwNTJENDM2Qk`** — cả 4 node format bằng đúng chuỗi này. Lab 1.2 sẽ phá chính chỗ này.
- `KAFKA_LOG_DIRS=/tmp/kraft-combined-logs` trên mọi node. Trên `controller`, thư mục đó chứa `__cluster_metadata-0`.
- Cluster này chỉ có **1 controller** → chịu lỗi **0**. Đó là lựa chọn có chủ ý cho lab: nó khiến Lab 1.3 mô phỏng được **mất toàn bộ quorum** chỉ bằng một lệnh `stop`.

### Khởi động + alias

```bash
cd ~/kafka-labs
docker compose -f docker-compose.cluster.yml up -d
docker compose -f docker-compose.cluster.yml ps        # 4 container phải "running"

# Alias của CCDAK Tuần 1 — trỏ vào listener NỘI BỘ, không dùng localhost
export KAFKA_CTR=kafka-1
export KAFKA_BS=kafka-1:19092

alias kt='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-topics.sh --bootstrap-server $KAFKA_BS'
alias kcp='docker exec -i  $KAFKA_CTR /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server $KAFKA_BS'
alias kcc='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server $KAFKA_BS'
alias kcg='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server $KAFKA_BS'
alias kcfg='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-configs.sh --bootstrap-server $KAFKA_BS'
alias kq='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-metadata-quorum.sh --bootstrap-server $KAFKA_BS'
alias ksh='docker exec -it $KAFKA_CTR bash'
```

> 🧠 Vì sao `KAFKA_BS=kafka-1:19092` chứ không phải `localhost:9092`? Vì lệnh chạy **bên trong** container. Bootstrap `localhost:9092` sẽ nhận metadata trỏ tới `localhost:9094`/`localhost:9096` — hai địa chỉ **không tồn tại bên trong container** → mọi thao tác chạm broker khác đều timeout. Đây chính là bẫy `advertised.listeners`, và nó là Question 16 trong [questions.md](questions.md).

---

## Lab 1.1 ⭐ — Cluster controller tách riêng: đọc và giải nghĩa từng dòng quorum

**🎯 Mục tiêu:** Xác nhận bằng mắt rằng `controller` là node **`process.roles=controller` thuần**, ba broker là observer của metadata log — rồi **giải nghĩa được từng dòng** của `kafka-metadata-quorum.sh describe --status` và `--replication`. Đây là output mà đề CCAAK in ra và hỏi "dòng này nghĩa là gì".

**🧩 Luyện kỹ năng (liên quan đề):**

- Phân biệt **Leader / Follower / Observer** trong control plane, và biết cái nào là broker.
- Đọc `ClusterId`, `LeaderId`, `LeaderEpoch`, `HighWatermark`, `MaxFollowerLag`, `CurrentVoters`, `CurrentObservers`.
- Biết khi nào phải dùng **`--bootstrap-controller`** thay vì `--bootstrap-server`.
- Thấy được vì sao `kraft.version` trả lời câu hỏi "static hay dynamic quorum".

**⏱️ ~35 phút** · **Yêu cầu trước:** Chuẩn bị chung, cluster đang chạy.

### Các bước

1. Xác nhận vai trò từng node **từ chính cấu hình container**, không tin trí nhớ.

   ```bash
   for c in controller kafka-1 kafka-2 kafka-3; do
     echo "=== $c ==="
     docker inspect "$c" --format '{{range .Config.Env}}{{println .}}{{end}}' \
       | grep -E '^KAFKA_(NODE_ID|PROCESS_ROLES|CONTROLLER_QUORUM_VOTERS|LISTENERS)='
   done
   ```

   Chú ý ba điều: `controller` có `KAFKA_PROCESS_ROLES=controller` (**không** có chữ `broker`); ba broker có `KAFKA_PROCESS_ROLES=broker`; và **cả bốn** node đều khai `KAFKA_CONTROLLER_QUORUM_VOTERS=1@controller:9093` — broker-only **vẫn phải biết đường tới quorum**.

2. Đọc trạng thái quorum.

   ```bash
   kq describe --status
   ```

   Output có dạng:

   ```
   ClusterId:              MkU3OEVBNTcwNTJENDM2Qk
   LeaderId:               1
   LeaderEpoch:            2
   HighWatermark:          1183
   MaxFollowerLag:         0
   MaxFollowerLagTimeMs:   0
   CurrentVoters:          [{"id": 1, "directoryId": "...", "endpoints": ["CONTROLLER://controller:9093"]}]
   CurrentObservers:       [{"id": 2, "directoryId": "..."}, {"id": 3, "directoryId": "..."}, {"id": 4, "directoryId": "..."}]
   ```

   Giải nghĩa **từng dòng** — chép vào sổ:

   | Dòng | Nghĩa vận hành |
   |---|---|
   | `ClusterId` | Danh tính cluster. **Phải trùng** `cluster.id` trong `meta.properties` của mọi node. Lab 1.2 phá đúng chỗ này |
   | `LeaderId` | Node đang là **active controller**. `-1` = chưa bầu được leader → control plane đang chết |
   | `LeaderEpoch` | Số nhiệm kỳ. Tăng **mỗi lần bầu lại**. Epoch nhảy liên tục = quorum đang flap |
   | `HighWatermark` | Offset metadata record cuối đã được **đa số** xác nhận. Đứng yên khi cluster rảnh là bình thường |
   | `MaxFollowerLag` | Voter tụt xa nhất còn cách leader bao nhiêu offset. **> 0 kéo dài = một controller đang ốm** |
   | `MaxFollowerLagTimeMs` | Điều trên, tính bằng mili giây |
   | `CurrentVoters` | **Chỉ node có `process.roles` chứa `controller`.** Đây là tập tính đa số |
   | `CurrentObservers` | **Broker.** Replicate metadata log nhưng **không bỏ phiếu** |

3. Đọc tiến độ replicate metadata của từng node.

   ```bash
   kq describe --replication
   ```

   Cột `Status` chỉ nhận ba giá trị: **`Leader`** (active controller), **`Follower`** (standby controller), **`Observer`** (broker). Ở cluster lab chỉ có 1 controller nên bạn thấy **1 Leader + 3 Observer, không có Follower nào** — và đó chính là hình ảnh trực quan của "chịu lỗi = 0".

4. Nói chuyện **trực tiếp** với controller. Controller không nghe ở listener của client, nên phải đổi cờ.

   ```bash
   docker exec -it kafka-1 /opt/kafka/bin/kafka-metadata-quorum.sh \
     --bootstrap-controller controller:9093 describe --status

   docker exec -it kafka-1 /opt/kafka/bin/kafka-features.sh \
     --bootstrap-controller controller:9093 describe
   ```

   Trong output `kafka-features.sh`, tìm dòng `kraft.version`: `FinalizedVersionLevel: 0` → **static quorum**; `1` → **dynamic quorum** (KIP-853). Cluster lab này dùng `controller.quorum.voters` nên bạn sẽ thấy **0**.

5. Chứng minh controller **không** phục vụ client.

   ```bash
   docker exec -it kafka-1 /opt/kafka/bin/kafka-topics.sh \
     --bootstrap-server controller:9093 --list
   ```

   Lệnh này **treo rồi lỗi** (hoặc báo không kết nối được). Đó là kết quả **đúng**: cổng 9093 là listener `CONTROLLER`, không dành cho client. Ctrl+C nếu nó treo lâu.

6. Xem metadata log trên đĩa của controller.

   ```bash
   docker exec controller ls -la /tmp/kraft-combined-logs/__cluster_metadata-0/
   docker exec controller cat /tmp/kraft-combined-logs/meta.properties
   ```

### ✅ Kiểm chứng

- Bước 1: `controller` có `KAFKA_PROCESS_ROLES=controller`, **không** chứa `broker`. Ba broker có `node.id` **2, 3, 4**.
- Bước 2: `CurrentVoters` chỉ có **node 1**; `CurrentObservers` có đúng **node 2, 3, 4**. `LeaderId: 1`.
- Bước 3: đếm được **1 `Leader` + 3 `Observer`**, không có `Follower`.
- Bước 4: `kraft.version` hiển thị `FinalizedVersionLevel: 0` → static quorum.
- Bước 5: lệnh với `--bootstrap-server controller:9093` **thất bại** — đúng như mong đợi.
- Bước 6: thư mục `__cluster_metadata-0` có ít nhất một file `.log`; `meta.properties` chứa `cluster.id=MkU3OEVBNTcwNTJENDM2Qk`.

### 🧹 Dọn dẹp

```bash
# GIỮ cluster cho Lab 1.2 → 1.6.
```

### 🧠 Ý nghĩa với đề thi

- Đề in nguyên văn output `describe --status` rồi hỏi "node 2/3/4 là gì?" — đáp án là **broker, observer, không bỏ phiếu** (Question 2).
- `LeaderId: -1` là dấu hiệu duy nhất và rõ ràng nhất của "quorum chưa bầu được active controller".
- Nhớ cặp cờ: quorum/feature/controller-logger → **`--bootstrap-controller`** (cổng **9093**); mọi thứ còn lại → `--bootstrap-server` (cổng 9092).
- Production **không bao giờ** chạy 1 controller. Cluster lab này chịu lỗi 0 — và bạn sắp khai thác đúng điểm yếu đó ở Lab 1.3.

---

## Lab 1.2 💥 — Gây hỏng rồi sửa: `InconsistentClusterId`

**🎯 Mục tiêu:** Tái hiện **chính xác** lỗi mà mọi script tự động hoá dựng cluster đều mắc ít nhất một lần — mỗi máy gọi `kafka-storage.sh random-uuid` riêng thay vì dùng chung một `cluster.id` — rồi chẩn đoán theo đúng trình tự và khôi phục.

**🧩 Luyện kỹ năng (liên quan đề):**

- Biết `meta.properties` nằm ở đâu và chứa gì (`cluster.id`, `node.id`, `directory.id`).
- Trình tự chẩn đoán: **đọc log → đọc `meta.properties` → so với `describe --status` → format/sửa lại**.
- Hiểu vì sao KRaft bắt buộc format trước khi start, còn ZooKeeper thì không.

**⏱️ ~30 phút** · **Yêu cầu trước:** Lab 1.1, cluster đang chạy.

### Các bước

1. Ghi lại `cluster.id` **thật** của cluster và sao lưu `meta.properties` của `kafka-3`.

   ```bash
   mkdir -p ~/kafka-labs/week-01-ccaak && cd ~/kafka-labs/week-01-ccaak

   kq describe --status | grep ClusterId          # nguồn sự thật của cluster
   docker compose -f ~/kafka-labs/docker-compose.cluster.yml stop kafka-3
   docker cp kafka-3:/tmp/kraft-combined-logs/meta.properties ./meta-kafka3.backup
   cat ./meta-kafka3.backup
   ```

   > 📌 `docker cp` chạy được **cả khi container đã stop** — đó là lý do lab dùng nó thay vì `docker exec`. Khi broker chết vì lỗi cấu hình, `docker exec` không vào được nữa; `docker cp` thì vẫn.

2. Sinh một `cluster.id` **khác** — đúng như một script chạy `random-uuid` trên từng máy.

   ```bash
   WRONG_ID=$(docker exec controller /opt/kafka/bin/kafka-storage.sh random-uuid)
   echo "cluster.id sai sẽ dùng: $WRONG_ID"

   grep -v '^cluster.id=' ./meta-kafka3.backup > ./meta-kafka3.broken
   echo "cluster.id=$WRONG_ID" >> ./meta-kafka3.broken
   cat ./meta-kafka3.broken
   ```

3. Đẩy file hỏng vào container và bật lại.

   ```bash
   docker cp ./meta-kafka3.broken kafka-3:/tmp/kraft-combined-logs/meta.properties
   docker compose -f ~/kafka-labs/docker-compose.cluster.yml start kafka-3
   sleep 15
   docker compose -f ~/kafka-labs/docker-compose.cluster.yml ps kafka-3
   ```

4. **Chẩn đoán như người trực ca.** Đọc log trước, đừng đoán.

   ```bash
   docker logs kafka-3 2>&1 | grep -iE 'inconsistent|cluster ?id|Exiting Kafka' | tail -20
   ```

   Bạn sẽ thấy một dòng thuộc họ:

   ```
   org.apache.kafka.common.errors.InconsistentClusterIdException: Expected cluster ID MkU3OEVBNTcwNTJENDM2Qk
           but got <WRONG_ID>
   ```

   > ⚠️ **Câu chữ có thể khác** tuỳ đường đi: storage tool chặn ngay lúc format, hay Raft client bị controller từ chối khi fetch metadata. Thứ cần nhận ra là **tên ngoại lệ** và ý nghĩa "danh tính node không khớp cluster", không phải câu văn.

5. Xác nhận bằng hai nguồn — đây là bước mà đề hỏi.

   ```bash
   docker cp kafka-3:/tmp/kraft-combined-logs/meta.properties ./meta-kafka3.current
   grep cluster.id ./meta-kafka3.current      # danh tính NODE nghĩ nó thuộc về
   kq describe --status | grep ClusterId      # danh tính THẬT của cluster
   ```

6. Xác nhận cluster đang **thiếu một broker**: partition có RF 3 nay chỉ còn 2 replica trong ISR.

   ```bash
   kt --create --topic broken-lab --partitions 3 --replication-factor 3 2>/dev/null || true
   kt --describe --under-replicated-partitions
   ```

7. **Khôi phục.** Trả lại `cluster.id` đúng rồi bật lại.

   ```bash
   docker compose -f ~/kafka-labs/docker-compose.cluster.yml stop kafka-3
   docker cp ./meta-kafka3.backup kafka-3:/tmp/kraft-combined-logs/meta.properties
   docker compose -f ~/kafka-labs/docker-compose.cluster.yml start kafka-3
   sleep 20
   docker logs kafka-3 2>&1 | grep -E 'Kafka Server started|KafkaRaftServer' | tail -3
   ```

   > 🛟 **Phương án dự phòng** nếu container không lên lại được (ví dụ bạn lỡ xoá mất backup): xoá hẳn container để nó format lại từ đầu bằng `CLUSTER_ID` trong compose —
   > `docker compose -f ~/kafka-labs/docker-compose.cluster.yml rm -sf kafka-3 && docker compose -f ~/kafka-labs/docker-compose.cluster.yml up -d kafka-3`.
   > Trên production, tương đương với: **xoá log dir rồi `kafka-storage.sh format --cluster-id <id thật> --no-initial-controllers`** — chấp nhận broker phải replicate lại toàn bộ dữ liệu từ đầu.

8. Xác nhận đã lành.

   ```bash
   kq describe --status | grep CurrentObservers
   kt --describe --under-replicated-partitions      # phải KHÔNG in gì
   ```

### ✅ Kiểm chứng

- Bước 4: log của `kafka-3` chứa một dòng nhắc tới **cluster ID không khớp**; container không đạt trạng thái phục vụ.
- Bước 5: hai giá trị `cluster.id` **khác nhau** — đây là bằng chứng chẩn đoán, không phải phỏng đoán.
- Bước 6: `--under-replicated-partitions` **in ra** các partition có `Isr` chỉ còn 2 phần tử.
- Bước 8: `CurrentObservers` có lại đủ **3** node (2, 3, 4) và `--under-replicated-partitions` **không in gì**.

### 🧹 Dọn dẹp

```bash
kt --delete --topic broken-lab
rm -f ~/kafka-labs/week-01-ccaak/meta-kafka3.broken ~/kafka-labs/week-01-ccaak/meta-kafka3.current
# GIỮ cluster và GIỮ meta-kafka3.backup cho các lab sau.
```

### 🧠 Ý nghĩa với đề thi

- `InconsistentClusterIdException` nằm trong cheat-sheet exception của domain Troubleshooting. Phản xạ: **so `meta.properties` với `describe --status`**, rồi format lại đúng id — không phải chỉnh timeout, không phải đụng ZooKeeper (Question 3).
- Đây là lỗi **chỉ tồn tại trong thế giới KRaft**: thời ZooKeeper, broker tự đăng ký lúc start nên không có bước format nào để làm sai.
- Nguyên nhân gốc trong thực tế luôn giống nhau: **`random-uuid` bị gọi nhiều lần**. Sinh một lần, đưa vào biến môi trường / secret store, mọi node dùng chung.
- Ghi nhớ: xoá `log.dirs` = xoá `meta.properties` = node **mất danh tính**. Trên controller, đó là mất một voter của quorum.

---

## Lab 1.3 ⭐💥 — Gây hỏng rồi sửa: mất toàn bộ quorum controller

**🎯 Mục tiêu:** Tự tay chứng minh mệnh đề quan trọng nhất tuần này — khi quorum controller chết, **control plane đóng băng nhưng data plane vẫn phục vụ** những partition không đổi leader — và chứng minh luôn vì sao đó là trạng thái **nguy hiểm chứ không phải an toàn**.

**🧩 Luyện kỹ năng (liên quan đề):**

- Nhận ra chữ ký của mất quorum: **produce/consume chạy bình thường nhưng lệnh admin timeout**.
- Biết `kafka-topics.sh --create` thất bại còn `--list` vẫn chạy, và giải thích được vì sao.
- Biết hành động đầu tiên là **khôi phục controller**, không phải đi sửa từng topic.
- Thấy tận mắt rủi ro kế tiếp: một broker chết trong lúc mất quorum = partition **offline vĩnh viễn**.

**⏱️ ~40 phút** · **Yêu cầu trước:** Lab 1.2 đã khôi phục xong, cả 4 container `running`.

### Các bước

1. Chuẩn bị **trước khi** phá: tạo topic và ghi vài message. Sau khi controller chết bạn sẽ không tạo được topic nữa.

   ```bash
   kt --create --topic quorum-test --partitions 3 --replication-factor 3
   kt --describe --topic quorum-test

   printf 'before-outage-1\nbefore-outage-2\n' | \
     docker exec -i kafka-1 /opt/kafka/bin/kafka-console-producer.sh \
       --bootstrap-server kafka-1:19092 --topic quorum-test
   ```

2. Ghi lại leader hiện tại của từng partition — lát nữa phải so lại.

   ```bash
   # dùng docker exec "trần" (không -it) khi ghi ra file: -t sẽ chèn ký tự CR làm diff nhiễu
   docker exec kafka-1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka-1:19092 \
     --describe --topic quorum-test | tee ~/kafka-labs/week-01-ccaak/leaders-before.txt
   ```

3. 💥 **Phá.** Tắt controller duy nhất → mất ngay đa số (1/1).

   ```bash
   docker compose -f ~/kafka-labs/docker-compose.cluster.yml stop controller
   docker compose -f ~/kafka-labs/docker-compose.cluster.yml ps
   ```

4. **Data plane — vẫn sống.** Ghi và đọc trên topic đã tồn tại.

   ```bash
   printf 'during-outage-1\nduring-outage-2\n' | \
     docker exec -i kafka-1 /opt/kafka/bin/kafka-console-producer.sh \
       --bootstrap-server kafka-1:19092 --topic quorum-test

   docker exec kafka-1 /opt/kafka/bin/kafka-console-consumer.sh \
     --bootstrap-server kafka-1:19092 --topic quorum-test \
     --from-beginning --timeout-ms 8000
   ```

   Bạn thấy **cả 4 message**. (Console consumer kết thúc bằng một `TimeoutException` sau 8 giây rảnh — đó là cách nó thoát, không phải lỗi.)

5. **Commit offset — cũng vẫn sống**, vì `__consumer_offsets` là data plane.

   ```bash
   docker exec kafka-1 /opt/kafka/bin/kafka-console-consumer.sh \
     --bootstrap-server kafka-1:19092 --topic quorum-test \
     --group outage-group --from-beginning --timeout-ms 8000

   kcg --describe --group outage-group
   ```

6. **Control plane — đóng băng.** Thử tạo topic mới.

   ```bash
   kt --create --topic after-outage --partitions 3 --replication-factor 3
   ```

   Kết quả mong đợi (mất khoảng 30–60 giây rồi mới báo):

   ```
   Error while executing topic command : The request timed out.
   [...] ERROR org.apache.kafka.common.errors.TimeoutException: The request timed out.
    (org.apache.kafka.tools.TopicCommand)
   ```

   Thử thêm hai lệnh nữa để thấy ranh giới **đọc / ghi metadata**:

   ```bash
   kt --list                                   # ✅ CHẠY — đọc từ metadata cache của broker
   kt --describe --topic quorum-test           # ✅ CHẠY — vẫn là đọc cache
   kcfg --alter --entity-type topics --entity-name quorum-test \
        --add-config retention.ms=3600000      # ❌ TIMEOUT — ghi metadata
   ```

7. Xem quorum tự nói về mình.

   ```bash
   kq describe --status
   ```

   Lệnh này **timeout hoặc báo lỗi** vì không còn ai trả lời thay mặt quorum. Trên cluster thật (3 controller, mất 2), nó vẫn chạy nhưng in `LeaderId: -1`. **Cả hai đều là chữ ký của mất quorum.**

8. ⚠️ **Chứng minh vì sao đây là trạng thái nguy hiểm** (bước quan trọng nhất của lab). Tắt thêm một broker trong lúc quorum đang chết.

   ```bash
   docker compose -f ~/kafka-labs/docker-compose.cluster.yml stop kafka-3
   sleep 20
   docker exec kafka-1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka-1:19092 \
     --describe --topic quorum-test | tee ~/kafka-labs/week-01-ccaak/leaders-during.txt
   diff ~/kafka-labs/week-01-ccaak/leaders-before.txt ~/kafka-labs/week-01-ccaak/leaders-during.txt || true
   ```

   Những partition mà **`kafka-3` (node 4) đang làm leader** giờ **không có ai bầu leader thay** — không có controller thì không có leader election. Thử produce vào topic đó:

   ```bash
   printf 'after-second-failure\n' | \
     docker exec -i kafka-1 /opt/kafka/bin/kafka-console-producer.sh \
       --bootstrap-server kafka-1:19092 --topic quorum-test
   ```

   Nếu partition được chọn theo round-robin rơi vào partition mất leader, bạn sẽ thấy `LEADER_NOT_AVAILABLE` / timeout. **Đây chính là chi phí thật của việc chần chừ khi mất quorum.**

9. **Khôi phục — đúng thứ tự.** Controller **trước**, broker sau.

   ```bash
   docker compose -f ~/kafka-labs/docker-compose.cluster.yml start controller
   sleep 20
   kq describe --status                      # LeaderId phải trở lại là 1

   docker compose -f ~/kafka-labs/docker-compose.cluster.yml start kafka-3
   sleep 25
   kt --describe --under-replicated-partitions     # chờ tới khi KHÔNG in gì
   kt --create --topic after-outage --partitions 3 --replication-factor 3    # giờ mới chạy được
   ```

### ✅ Kiểm chứng

- Bước 4 và 5: produce, consume và commit offset đều **thành công** khi controller đã tắt.
- Bước 6: `--create` và `kafka-configs.sh --alter` **timeout**, trong khi `--list` và `--describe` **vẫn chạy**. Ranh giới nằm ở **ghi metadata** so với **đọc metadata cache**.
- Bước 7: `kq describe --status` không trả lời được (hoặc `LeaderId: -1`).
- Bước 8: `diff` cho thấy leader **không** di chuyển khỏi node 4 — vì không ai bầu được; produce vào partition đó thất bại.
- Bước 9: sau khi controller lên, `LeaderId: 1` trở lại và `--create` chạy được ngay.

### 🧹 Dọn dẹp

```bash
kt --delete --topic quorum-test
kt --delete --topic after-outage
kcg --delete --group outage-group
rm -f ~/kafka-labs/week-01-ccaak/leaders-*.txt
# GIỮ cluster cho Lab 1.4.
```

### 🧠 Ý nghĩa với đề thi

- **Chữ ký của mất quorum**: client vẫn produce/consume bình thường, nhưng mọi lệnh admin timeout. Gặp mô tả này trong đề → nghĩ ngay tới **controller majority** (Question 5, Question 8).
- Ranh giới cần nói được thành lời: **đọc** metadata dùng cache của broker → vẫn chạy; **ghi** metadata phải qua active controller → chết.
- Offset commit là **data plane** (ghi vào `__consumer_offsets`), không phải metadata → vẫn chạy. Đây là phương án nhiễu hay gặp.
- Bước 8 là lý do câu trả lời đúng luôn là "**khôi phục quorum trước**". Mọi phút trôi qua trong trạng thái mất quorum là một phút cluster không có khả năng tự chữa lành.
- Và đây cũng là lý do production dùng **3 hoặc 5 controller**: để một node chết không bao giờ tạo ra tình huống này.

---

## Lab 1.4 — Tour bộ đồ nghề CLI của admin

**🎯 Mục tiêu:** Chạy đúng **một lần** mỗi công cụ chẩn đoán, để khi đề hỏi "bạn gõ lệnh nào tiếp theo" thì bạn nhớ được **hình dạng output** chứ không chỉ nhớ tên lệnh.

**🧩 Luyện kỹ năng (liên quan đề):**

- `kafka-broker-api-versions.sh` — kiểm tra broker nào đang sống và nói được API version nào.
- `kafka-log-dirs.sh --describe` — partition nằm ổ nào, chiếm bao nhiêu byte.
- `kafka-features.sh describe` — `metadata.version` và `kraft.version`.
- `kafka-dump-log.sh` — soi segment dữ liệu **và** segment metadata.

**⏱️ ~35 phút** · **Yêu cầu trước:** Lab 1.3 đã khôi phục, cả 4 container `running`.

### Các bước

1. Tạo ít dữ liệu để có cái mà soi.

   ```bash
   kt --create --topic cli-tour --partitions 3 --replication-factor 3
   for i in $(seq 1 200); do echo "key-$((i % 5)):payload-$i"; done | \
     docker exec -i kafka-1 /opt/kafka/bin/kafka-console-producer.sh \
       --bootstrap-server kafka-1:19092 --topic cli-tour \
       --property parse.key=true --property key.separator=:
   ```

2. **`kafka-broker-api-versions.sh`** — ai đang sống, và nói được gì.

   ```bash
   docker exec kafka-1 /opt/kafka/bin/kafka-broker-api-versions.sh \
     --bootstrap-server kafka-1:19092 | grep -E '^kafka-[0-9]'
   ```

   Mỗi broker một dòng `kafka-N:19092 (id: X rack: null ...)`. Dùng khi nghi ngờ **client quá cũ**: baseline giao thức của Kafka 4.x là **2.1**.

3. **`kafka-log-dirs.sh`** — partition ở ổ nào, nặng bao nhiêu.

   ```bash
   docker exec kafka-1 /opt/kafka/bin/kafka-log-dirs.sh \
     --bootstrap-server kafka-1:19092 --describe --broker-list 2,3,4 \
     --topic-list cli-tour
   ```

   Output là **một dòng JSON**: `{"version":1,"brokers":[{"broker":2,"logDirs":[{"logDir":"/tmp/kraft-combined-logs","error":null,"partitions":[{"partition":"cli-tour-0","size":...,"offsetLag":0,"isFuture":false}, ...]}]}]}`.

   Ba trường phải đọc được: **`logDir`** (ổ nào), **`size`** (byte), **`offsetLag`** (replica còn tụt bao nhiêu). Đây là công cụ đầu tiên khi một broker sắp đầy đĩa.

4. **`kafka-features.sh`** — cluster đang ở feature level nào.

   ```bash
   docker exec kafka-1 /opt/kafka/bin/kafka-features.sh \
     --bootstrap-controller controller:9093 describe
   ```

   Hai dòng đáng nhớ: **`metadata.version`** (quyết định feature nào khả dụng, nâng bằng `kafka-features.sh upgrade --release-version X.Y`) và **`kraft.version`** (0 = static quorum, 1 = dynamic).

5. **`kafka-dump-log.sh`** trên segment **dữ liệu**.

   ```bash
   docker exec kafka-1 sh -c 'ls /tmp/kraft-combined-logs/cli-tour-0/'
   docker exec kafka-1 /opt/kafka/bin/kafka-dump-log.sh \
     --files /tmp/kraft-combined-logs/cli-tour-0/00000000000000000000.log \
     --print-data-log | head -12
   ```

   Chú ý: tên file segment = **base offset**; mỗi `baseOffset ... lastOffset ... count ...` là một **RecordBatch**, không phải một record.

6. **`kafka-dump-log.sh --cluster-metadata-decoder`** trên segment **metadata** (chạy trong container `controller`).

   ```bash
   docker exec controller /opt/kafka/bin/kafka-dump-log.sh \
     --cluster-metadata-decoder \
     --files /tmp/kraft-combined-logs/__cluster_metadata-0/00000000000000000000.log \
     | head -40
   ```

   Bạn sẽ thấy các loại record như `REGISTER_BROKER_RECORD`, `TOPIC_RECORD`, `PARTITION_RECORD`, `PARTITION_CHANGE_RECORD`, `FEATURE_LEVEL_RECORD`. **Đây là "znode của thời KRaft"** — mỗi thay đổi metadata là một record có offset.

7. Tìm record ứng với topic bạn vừa tạo.

   ```bash
   docker exec controller /opt/kafka/bin/kafka-dump-log.sh \
     --cluster-metadata-decoder \
     --files /tmp/kraft-combined-logs/__cluster_metadata-0/00000000000000000000.log \
     | grep -i 'cli-tour' | head -5
   ```

### ✅ Kiểm chứng

- Bước 2: đúng **3** dòng broker, id **2, 3, 4**.
- Bước 3: JSON chứa `cli-tour-0/1/2` với `size` > 0 và `offsetLag: 0`.
- Bước 4: thấy cả `metadata.version` và `kraft.version` kèm `FinalizedVersionLevel`.
- Bước 5: đọc được ít nhất một dòng `baseOffset: ... count: ...`; tên file là `00000000000000000000.log`.
- Bước 6: thấy ít nhất một `REGISTER_BROKER_RECORD` và một `TOPIC_RECORD`.
- Bước 7: tên `cli-tour` xuất hiện trong metadata log.

### 🧹 Dọn dẹp

```bash
kt --delete --topic cli-tour
# GIỮ cluster cho Lab 1.5.
```

### 🧠 Ý nghĩa với đề thi

- Đề CCAAK hỏi **"bạn chạy lệnh nào tiếp theo"** nhiều hơn hỏi "cờ này nghĩa là gì". Ghép cặp: đĩa → `log-dirs`, quorum → `metadata-quorum`, feature → `features`, "trong file thực sự có gì" → `dump-log`.
- `--cluster-metadata-decoder` là câu trả lời cho "làm sao đọc `__cluster_metadata`" — **không** dùng console consumer được (Question 11).
- Nhớ cặp còn lại: `kafka-dump-log.sh` đọc **record**, `kafka-metadata-shell.sh --snapshot` duyệt **state** đã materialize.
- `kafka-broker-api-versions.sh` là cách nhanh nhất để biết broker nào **thật sự** đang phục vụ, khác với `docker ps` chỉ nói container còn sống.

---

## Lab 1.5 — `kafka-configs.sh`: giá trị hiệu lực và `synonyms` ở 3 mức

**🎯 Mục tiêu:** Trả lời được câu hỏi vận hành kinh điển — *"giá trị đang thực sự có hiệu lực là bao nhiêu, và nó đến từ đâu?"* — bằng cột `synonyms`, thay vì đoán.

**🧩 Luyện kỹ năng (liên quan đề):**

- Thứ tự ưu tiên: `DYNAMIC_TOPIC_CONFIG` > `DYNAMIC_BROKER_CONFIG` > `DYNAMIC_DEFAULT_BROKER_CONFIG` > `STATIC_BROKER_CONFIG` > `DEFAULT_CONFIG`.
- Biết `--all` là cờ bật cột `synonyms`.
- Hiểu vì sao "đổi config ở broker mà topic không đổi hành vi".

**⏱️ ~25 phút** · **Yêu cầu trước:** cluster đang chạy.

### Các bước

1. Đọc giá trị hiệu lực ở **mức broker**. Compose đặt `KAFKA_MIN_INSYNC_REPLICAS: 2`, tức là một `STATIC_BROKER_CONFIG`.

   ```bash
   kcfg --describe --entity-type brokers --entity-name 2 --all | grep -E '^\s+min\.insync\.replicas='
   ```

   Bạn thấy đại loại:

   ```
     min.insync.replicas=2 sensitive=false synonyms={STATIC_BROKER_CONFIG:min.insync.replicas=2, DEFAULT_CONFIG:min.insync.replicas=1}
   ```

   Đọc: **giá trị hiệu lực 2**, đến từ file config tĩnh; mặc định gốc của Kafka là **1**.

2. Tạo topic rồi đọc ở **mức topic** (chưa có override nào).

   ```bash
   kt --create --topic cfg-lab --partitions 3 --replication-factor 3
   kcfg --describe --entity-type topics --entity-name cfg-lab --all | grep -E '^\s+min\.insync\.replicas='
   ```

3. Thêm **override cấp topic** — mức ưu tiên cao nhất.

   ```bash
   kcfg --alter --entity-type topics --entity-name cfg-lab --add-config min.insync.replicas=3
   kcfg --describe --entity-type topics --entity-name cfg-lab --all | grep -E '^\s+min\.insync\.replicas='
   ```

   Giờ `synonyms` liệt kê `DYNAMIC_TOPIC_CONFIG:min.insync.replicas=3` **đứng đầu** — đó là giá trị thắng.

4. Thêm **dynamic config cho một broker** và **cluster-default**, rồi xem chúng xếp ở đâu.

   ```bash
   kcfg --alter --entity-type brokers --entity-name 2 --add-config min.insync.replicas=2
   kcfg --alter --entity-type brokers --entity-default --add-config min.insync.replicas=1

   kcfg --describe --entity-type brokers --entity-name 2 --all | grep -E '^\s+min\.insync\.replicas='
   kcfg --describe --entity-type topics  --entity-name cfg-lab --all | grep -E '^\s+min\.insync\.replicas='
   ```

   Topic **vẫn là 3** — vì override cấp topic thắng tất cả. Đây chính là hiện tượng "tôi đổi ở broker mà không có tác dụng".

5. Liệt kê **chỉ những config được đặt tường minh** (bỏ `--all`) để thấy khác biệt.

   ```bash
   kcfg --describe --entity-type topics --entity-name cfg-lab
   kcfg --describe --entity-type brokers --entity-name 2
   ```

   Không có `--all` thì **không có cột `synonyms`** và không thấy giá trị mặc định — đây là lý do nhiều người kết luận sai.

6. Gỡ override và xác nhận giá trị "rơi xuống" mức kế tiếp.

   ```bash
   kcfg --alter --entity-type topics --entity-name cfg-lab --delete-config min.insync.replicas
   kcfg --describe --entity-type topics --entity-name cfg-lab --all | grep -E '^\s+min\.insync\.replicas='
   ```

7. Thử một config **read-only** để thấy ranh giới động/tĩnh.

   ```bash
   kcfg --alter --entity-type brokers --entity-name 2 \
        --add-config advertised.listeners=PLAINTEXT://kafka-1:19092,PLAINTEXT_HOST://localhost:9092
   ```

   Lệnh này **bị từ chối**: KRaft đã bỏ khả năng cập nhật động `advertised.listeners`. Muốn đổi → sửa file config và **restart broker**.

### ✅ Kiểm chứng

- Bước 1: thấy `STATIC_BROKER_CONFIG:min.insync.replicas=2` và `DEFAULT_CONFIG:min.insync.replicas=1` trong `synonyms`.
- Bước 3: `DYNAMIC_TOPIC_CONFIG` đứng **đầu** danh sách và giá trị hiệu lực đổi thành **3**.
- Bước 4: đổi ở broker **không** làm đổi giá trị hiệu lực của topic.
- Bước 5: bỏ `--all` → mất cột `synonyms`.
- Bước 6: sau khi xoá override, giá trị hiệu lực quay về giá trị của mức broker.
- Bước 7: nhận thông báo lỗi nói rằng config này **không cập nhật động được**.

### 🧹 Dọn dẹp

```bash
kcfg --alter --entity-type brokers --entity-name 2 --delete-config min.insync.replicas
kcfg --alter --entity-type brokers --entity-default --delete-config min.insync.replicas
kt --delete --topic cfg-lab
# GIỮ cluster cho Lab 1.6.
```

### 🧠 Ý nghĩa với đề thi

- Đề in nguyên văn một dòng `synonyms={...}` rồi hỏi "giá trị hiệu lực là bao nhiêu và đến từ đâu" (Question 19). Đọc **từ trái sang phải** — phần tử đầu tiên thắng.
- Phản xạ trước mọi thay đổi config: **`--describe --all` trước, `--alter` sau**. Phần lớn sự cố "đổi rồi mà không ăn" là do một override ở mức cao hơn.
- Ranh giới động/tĩnh là một câu hỏi riêng của domain Cluster Configuration (22%). `advertised.listeners` là ví dụ được hỏi nhiều nhất.
- Tuần 2 sẽ khai thác sâu bảng này với `log.retention.*`, `cleanup.policy`, `segment.ms`.

---

## Lab 1.6 — Leader election: tắt 1 broker, rồi trả leader về preferred

**🎯 Mục tiêu:** Quan sát trọn vẹn một vòng đời leader: ISR co lại khi broker chết → leader chuyển sang replica **trong ISR** → broker quay lại nhưng leader **không tự về ngay** → trả về bằng preferred election.

**🧩 Luyện kỹ năng (liên quan đề):**

- Đọc `Leader / Replicas / Isr` và xác định **preferred leader** (phần tử **đầu tiên** của `Replicas`).
- Phân biệt `--under-replicated-partitions` và `--unavailable-partitions`.
- Biết `auto.leader.rebalance.enable=true` + `leader.imbalance.check.interval.seconds=300` làm gì, và khi nào cần can thiệp tay.

**⏱️ ~30 phút** · **Yêu cầu trước:** cluster đang chạy đủ 4 container.

### Các bước

1. Tạo topic 6 partition RF 3 và ghi lại phân bố leader.

   ```bash
   kt --create --topic leader-lab --partitions 6 --replication-factor 3
   docker exec kafka-1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka-1:19092 \
     --describe --topic leader-lab | tee ~/kafka-labs/week-01-ccaak/ll-before.txt
   ```

   Đếm xem mỗi broker (2, 3, 4) làm leader bao nhiêu partition — cân bằng thì mỗi node **2** partition. Với mỗi dòng, phần tử **đầu tiên** của `Replicas` là **preferred leader**, và ngay sau khi tạo topic thì `Leader` **trùng** với nó.

2. 💥 Tắt `kafka-3` (node **4**).

   ```bash
   docker compose -f ~/kafka-labs/docker-compose.cluster.yml stop kafka-3
   sleep 20
   ```

3. Quan sát hậu quả.

   ```bash
   docker exec kafka-1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka-1:19092 \
     --describe --topic leader-lab | tee ~/kafka-labs/week-01-ccaak/ll-during.txt
   diff ~/kafka-labs/week-01-ccaak/ll-before.txt ~/kafka-labs/week-01-ccaak/ll-during.txt || true

   kt --describe --under-replicated-partitions     # 6 partition đều URP: Isr còn 2/3
   kt --describe --unavailable-partitions          # KHÔNG in gì: mọi partition vẫn có leader
   ```

   Hai điều phải nói được thành lời:
   - `Isr` của mọi partition **mất số 4**, nên `UnderReplicatedPartitions` > 0.
   - Những partition mà node 4 đang làm leader đã có **leader mới**, và leader mới **luôn là một replica đang ở trong ISR** — vì `unclean.leader.election.enable=false`.

4. Chứng minh ghi vẫn an toàn: RF 3, ISR còn 2, `min.insync.replicas=2` → `acks=all` vẫn qua.

   ```bash
   printf 'isr2-write\n' | \
     docker exec -i kafka-1 /opt/kafka/bin/kafka-console-producer.sh \
       --bootstrap-server kafka-1:19092 --topic leader-lab \
       --request-required-acks all
   ```

5. Bật lại `kafka-3` và chờ ISR đầy lại.

   ```bash
   docker compose -f ~/kafka-labs/docker-compose.cluster.yml start kafka-3
   sleep 25
   kt --describe --under-replicated-partitions     # chờ tới khi KHÔNG in gì nữa
   docker exec kafka-1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka-1:19092 \
     --describe --topic leader-lab | tee ~/kafka-labs/week-01-ccaak/ll-after.txt
   ```

   Quan sát điểm mấu chốt: **`Isr` đã đủ 3 nhưng `Leader` vẫn chưa quay về preferred.** Node 4 đang không làm leader của partition nào, còn node 2 và 3 gánh hết.

6. Trả leader về preferred — **bằng tay**.

   ```bash
   docker exec kafka-1 /opt/kafka/bin/kafka-leader-election.sh \
     --bootstrap-server kafka-1:19092 \
     --election-type preferred --all-topic-partitions

   docker exec kafka-1 /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka-1:19092 \
     --describe --topic leader-lab | tee ~/kafka-labs/week-01-ccaak/ll-elected.txt
   diff ~/kafka-labs/week-01-ccaak/ll-before.txt ~/kafka-labs/week-01-ccaak/ll-elected.txt || true
   ```

7. Hoặc **không làm gì cả** và để cluster tự xử lý. `auto.leader.rebalance.enable` mặc định `true`, `leader.imbalance.check.interval.seconds` mặc định **300**.

   ```bash
   kcfg --describe --entity-type brokers --entity-name 2 --all \
     | grep -E 'auto\.leader\.rebalance\.enable|leader\.imbalance'
   ```

   Nếu ở bước 5 bạn chờ đủ **5 phút** trước khi chạy bước 6, leader sẽ tự về preferred mà không cần lệnh nào.

### ✅ Kiểm chứng

- Bước 1: `Leader` trùng phần tử đầu của `Replicas` ở cả 6 partition.
- Bước 3: `--under-replicated-partitions` in **6** dòng; `--unavailable-partitions` **không in gì**; không partition nào có leader là node 4.
- Bước 4: produce với `acks=all` **thành công** khi ISR = 2 và `min.insync.replicas` = 2.
- Bước 5: `--under-replicated-partitions` về rỗng, nhưng `Leader` **vẫn lệch**.
- Bước 6: sau preferred election, `diff` giữa `ll-before.txt` và `ll-elected.txt` **không còn khác biệt về cột `Leader`** (`TopicId` và thứ tự `Isr` có thể khác, không sao).
- Bước 7: xác nhận `auto.leader.rebalance.enable=true` và `leader.imbalance.check.interval.seconds=300`.

### 🧹 Dọn dẹp

```bash
kt --delete --topic leader-lab
rm -f ~/kafka-labs/week-01-ccaak/ll-*.txt

# Kết thúc tuần — hạ cluster:
docker compose -f ~/kafka-labs/docker-compose.cluster.yml down
```

### 🧠 Ý nghĩa với đề thi

- **Preferred leader = phần tử đầu tiên của `Replicas`.** Đề in nguyên văn output `--describe` rồi hỏi tại sao một broker gánh hết leader (Question 18).
- Phân biệt hai cờ: `--under-replicated-partitions` = ISR < RF (**degraded**); `--unavailable-partitions` = **không có leader** (chết thật). Hai mức nghiêm trọng khác nhau.
- Leader chuyển sang replica **trong ISR** là hành vi an toàn mặc định. Phương án "bật `unclean.leader.election.enable` để cân bằng lại leader" luôn sai — nó dùng để đánh đổi **mất dữ liệu** lấy availability, không phải để cân bằng tải.
- Sau mọi rolling restart, hãy kiểm tra phân bố leader. Nếu vội thì `kafka-leader-election.sh --election-type preferred`; nếu không vội thì cluster tự làm trong **5 phút**.

---

> ✅ Xong 6 lab? Quay lại **[Lab checklist trong README](README.md#-lab-checklist)** tick đủ 6 dòng, rồi làm **[questions.md](questions.md)** (28 câu, ~42 phút, không tra tài liệu).
> 💥 Trước khi sang Tuần 2, làm lại **Lab 1.2 và Lab 1.3 mà không nhìn hướng dẫn**. Đó là hai lab dạy đúng thứ CCAAK chấm: *người vận hành làm gì tiếp theo*.
