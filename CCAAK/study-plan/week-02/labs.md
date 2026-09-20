# 🧪 Hands-on Labs — Tuần 2: broker config, `log.dirs` & JBOD, retention, compaction

> Lab cầm tay chỉ việc, chạy **hoàn toàn local** bằng Docker — không tốn phí. LUÔN chạy phần Dọn dẹp cuối mỗi lab.
> ⚙️ Yêu cầu chung: cluster 3 broker + 1 controller từ [CCDAK Tuần 1 — Lab 1.2](../../../CCDAK/study-plan/week-01/labs.md) (`~/kafka-labs/docker-compose.cluster.yml`) và `kafkajs` trong `~/kafka-labs/`.
> Về [plan tuần](README.md) · [Câu hỏi luyện tập](questions.md) · [Kế hoạch tổng](../../CCAAK-STUDY-PLAN.md)

---

## 🔧 Chuẩn bị chung

```bash
cd ~/kafka-labs
mkdir -p week-02
docker compose -f docker-compose.cluster.yml up -d
docker compose -f docker-compose.cluster.yml ps
```

Cluster này gồm 4 container: `controller` (`node.id` **1**, `process.roles=controller`), `kafka-1` (**2**), `kafka-2` (**3**), `kafka-3` (**4**). Host port `9092` / `9094` / `9096`; bên trong docker network dùng listener nội bộ `kafka-1:19092`.

```bash
export KAFKA_CTR=kafka-1 KAFKA_BS=kafka-1:19092
```

Alias của Tuần 1 vẫn dùng nguyên (`kt` `kcp` `kcc` `kcg` `kcfg`). Tuần này thêm 2 alias:

```bash
alias kld='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-log-dirs.sh --bootstrap-server $KAFKA_BS'
alias kcl='docker exec -it $KAFKA_CTR /opt/kafka/bin/kafka-cluster.sh --bootstrap-server $KAFKA_BS'
```

> 📌 **`kafka-dump-log.sh` không có alias** vì nó đọc **file trên đĩa của một broker cụ thể**, không đi qua bootstrap server. Luôn gọi thẳng: `docker exec kafka-2 /opt/kafka/bin/kafka-dump-log.sh --files ...`.

> ⚠️ **Cluster này là đồ dùng một lần.** `KAFKA_LOG_DIRS` trỏ vào `/tmp/kraft-combined-logs` **bên trong container**, không có volume — `docker compose down` là mất sạch dữ liệu. Ba lab 2.2 / 2.6 / 2.7 sẽ **tạo lại container** `kafka-3` bằng file override. Nếu bất kỳ lúc nào cluster rơi vào trạng thái kỳ quặc không giải thích được, cứ `docker compose -f docker-compose.cluster.yml down && docker compose -f docker-compose.cluster.yml up -d` rồi làm lại từ đầu lab đó.

> 📌 **Không định nghĩa lại `docker-compose.cluster.yml`.** Mọi thay đổi trong tuần này đi qua **file override** riêng (`docker-compose.jbod.yml`, `docker-compose.smalldisk.yml`) và luôn được gọi kèm file gốc: `docker compose -f docker-compose.cluster.yml -f docker-compose.<override>.yml up -d`.

---

## Lab 2.1 — Ba mức config, và đọc `synonyms` để biết giá trị đến từ đâu ⭐

**🎯 Mục tiêu:** Đặt **cùng một config** (`retention.ms`) ở 3 nơi khác nhau, rồi dùng `kafka-configs.sh --describe --all` để chứng minh đúng thứ tự ưu tiên 5 mức — và gỡ dần từng mức để thấy giá trị "rơi" xuống đâu.
**🧩 Luyện kỹ năng (liên quan đề):**

- Đọc cột **`synonyms={...}`**: phần tử đầu tiên là nguồn đang thắng. Đây là câu trả lời cho dạng đề "giá trị hiệu lực đến từ đâu".
- Phân biệt `--entity-name <id>` (một broker) với `--entity-default` (cluster-wide).
- Thấy tận mắt vì sao **đặt cluster default không đè được topic override**.
- Nhận ra config `read-only` bị từ chối ngay khi `--alter`.

**⏱️ ~35 phút** · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước

1. Tạo topic sạch, chưa có override nào.

   ```bash
   kt --create --topic cfg-demo --partitions 3 --replication-factor 3
   kcfg --describe --entity-type topics --entity-name cfg-demo
   ```

   Dòng đầu phải in `Dynamic configs for topic cfg-demo are:` và **không có gì bên dưới** — topic chưa có override.
2. Xem giá trị **đang hiệu lực** và nguồn của nó khi chưa ai đụng vào.

   ```bash
   kcfg --describe --all --entity-type topics --entity-name cfg-demo | grep -E "^\s+(retention\.ms|segment\.bytes)="
   ```

   Kết quả dạng:

   ```
     retention.ms=604800000 sensitive=false synonyms={DEFAULT_CONFIG:log.retention.hours=168}
   ```

   ➜ Giá trị đến từ **`DEFAULT_CONFIG`**, và tên của nó ở tầng broker là `log.retention.hours`.
3. **Mức 3 — cluster-wide default.** Đặt `log.retention.ms` cho toàn cluster.

   ```bash
   kcfg --alter --entity-type brokers --entity-default \
     --add-config log.retention.ms=259200000      # 3 ngày
   kcfg --describe --all --entity-type topics --entity-name cfg-demo | grep "^\s*retention\.ms="
   ```

   Bây giờ synonyms có thêm `DYNAMIC_DEFAULT_BROKER_CONFIG:log.retention.ms=259200000` **ở đầu**, và giá trị hiệu lực là 259200000.
4. **Mức 2 — dynamic cho một broker.** Đặt riêng cho broker 2 (`kafka-1`).

   ```bash
   kcfg --alter --entity-type brokers --entity-name 2 \
     --add-config log.retention.ms=172800000      # 2 ngày
   kcfg --describe --all --entity-type brokers --entity-name 2 | grep "^\s*log\.retention\.ms="
   ```

   Thứ tự synonyms giờ là `DYNAMIC_BROKER_CONFIG` → `DYNAMIC_DEFAULT_BROKER_CONFIG` → `DEFAULT_CONFIG`.

   > 📌 So sánh ngay với broker 3 để thấy nó **chỉ áp cho broker 2**:
   > `kcfg --describe --all --entity-type brokers --entity-name 3 | grep "^\s*log\.retention\.ms="`
5. **Mức 1 — topic override.** Mức mạnh nhất.

   ```bash
   kcfg --alter --entity-type topics --entity-name cfg-demo \
     --add-config retention.ms=60000               # 1 phút
   kcfg --describe --all --entity-type topics --entity-name cfg-demo | grep "^\s*retention\.ms="
   ```

   Giá trị hiệu lực = **60000**, và phần tử đầu tiên của synonyms là `DYNAMIC_TOPIC_CONFIG:retention.ms=60000`.
6. **Chứng minh bẫy vận hành:** đổi cluster default lần nữa và xác nhận topic **không đổi theo**.

   ```bash
   kcfg --alter --entity-type brokers --entity-default \
     --add-config log.retention.ms=86400000        # 1 ngày
   kcfg --describe --all --entity-type topics --entity-name cfg-demo | grep "^\s*retention\.ms="
   ```

   Vẫn là **60000**. Cluster default chỉ dịch chuyển phần tử thứ ba trong danh sách synonyms.
7. **Gỡ dần từ trên xuống** và quan sát giá trị rơi xuống mức kế tiếp.

   ```bash
   kcfg --alter --entity-type topics --entity-name cfg-demo --delete-config retention.ms
   kcfg --describe --all --entity-type topics --entity-name cfg-demo | grep "^\s*retention\.ms="   # → 86400000

   kcfg --alter --entity-type brokers --entity-default --delete-config log.retention.ms
   kcfg --describe --all --entity-type topics --entity-name cfg-demo | grep "^\s*retention\.ms="   # → 604800000
   ```

   ➜ `--delete-config` **không** đưa về mặc định in trong docs; nó đưa về **mức ưu tiên kế tiếp còn tồn tại**.
8. **Thử một config `read-only`** để thấy Kafka từ chối.

   ```bash
   kcfg --alter --entity-type brokers --entity-default --add-config queued.max.requests=1000
   ```

   Lỗi mong đợi (nội dung có thể hơi khác theo bản vá, nhưng phải nhắc tới "cannot be updated dynamically"):

   ```
   org.apache.kafka.common.errors.InvalidRequestException: Cannot update these configs dynamically: Set(queued.max.requests)
   ```
9. **Đối chứng:** cùng một lệnh nhưng với config `cluster-wide` thì thành công ngay, không restart.

   ```bash
   kcfg --alter --entity-type brokers --entity-default --add-config num.io.threads=12
   kcfg --describe --all --entity-type brokers --entity-name 2 | grep "^\s*num\.io\.threads="
   ```

### ✅ Kiểm chứng

- Bước 2: synonyms chỉ có **một** phần tử `DEFAULT_CONFIG` — chứng tỏ topic hoàn toàn "sạch".
- Bước 3 → 5: mỗi lần đặt thêm một mức, danh sách synonyms **dài thêm một phần tử ở đầu**, và giá trị hiệu lực bằng đúng phần tử đầu. Nếu bạn thấy ngược lại thì đang đọc nhầm topic hoặc nhầm broker id.
- Bước 6: giá trị **không đổi** sau khi sửa cluster default — đây là bằng chứng cho câu "đặt broker default không đè được topic override".
- Bước 8 báo lỗi, bước 9 thành công. Cặp đối chứng này là toàn bộ ý nghĩa của cột *Update Mode*.

### 🧹 Dọn dẹp

```bash
kcfg --alter --entity-type brokers --entity-name 2 --delete-config log.retention.ms
kcfg --alter --entity-type brokers --entity-default --delete-config num.io.threads
kt --delete --topic cfg-demo
```

### 🧠 Ý nghĩa với đề thi

- Đề sẽ đưa output `--describe --all` và hỏi *"giá trị này đến từ đâu / gỡ override topic thì thành bao nhiêu"*. Cả hai câu đều trả lời bằng cách đọc `synonyms` từ trái sang phải.
- Dạng câu thứ hai: *"đã đặt cluster default rồi mà topic X vẫn không đổi"* → luôn là **topic override đang thắng**.
- Dạng câu thứ ba: *"config này đổi được lúc chạy không"* → thuộc bảng ở [README](README.md#-buổi-a--lý-thuyết-3h): nhóm thread và cleaner = cluster-wide; nhóm socket, `log.dirs`, `log.retention.hours` = read-only.

---

## Lab 2.2 — JBOD: nhiều `log.dirs`, xem phân bố, rồi làm hỏng một ổ ⭐ *(gây hỏng rồi sửa)*

**🎯 Mục tiêu:** Cho `kafka-3` hai log directory, tạo topic nhiều partition để thấy Kafka rải partition **theo số lượng**, rồi **cố tình làm hỏng một log dir** và khôi phục.
**🧩 Luyện kỹ năng (liên quan đề):**

- Đọc JSON của `kafka-log-dirs.sh --describe` (`logDirs` → `partitions`, trường `error`, `size`, `isFuture`).
- Thấy tận mắt: một ổ hỏng **không** làm broker chết, chỉ làm offline partition trên ổ đó.
- `log.dirs` là **read-only** → thêm ổ bắt buộc restart broker.
- Nhận diện `KafkaStorageException` trong log broker.

**⏱️ ~50 phút** · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước

1. Tạo file override cho `kafka-3` có **2 log directory**.

   ```yaml
   # ~/kafka-labs/docker-compose.jbod.yml
   # Chỉ đổi kafka-3 (node.id 4): thêm log dir thứ hai. Mọi thứ khác kế thừa docker-compose.cluster.yml.
   services:
     kafka-3:
       environment:
         KAFKA_LOG_DIRS: /tmp/kraft-combined-logs,/tmp/kraft-logs-2
   ```

   ```bash
   cd ~/kafka-labs
   docker compose -f docker-compose.cluster.yml -f docker-compose.jbod.yml up -d kafka-3
   docker logs kafka-3 2>&1 | grep -iE "Kafka Server started|log dirs|Formatting" | tail -5
   ```

   > 🩹 **Nếu broker không lên** và log báo không tìm thấy `meta.properties` trong thư mục mới, format bổ sung thủ công rồi khởi động lại:
   >
   > ```bash
   > docker exec -u 0 kafka-3 /opt/kafka/bin/kafka-storage.sh format \
   >   --cluster-id MkU3OEVBNTcwNTJENDM2Qk \
   >   --config /etc/kafka/docker/server.properties --ignore-formatted
   > docker compose -f docker-compose.cluster.yml -f docker-compose.jbod.yml restart kafka-3
   > ```
2. Xác nhận broker 4 giờ khai báo 2 log dir.

   ```bash
   kld --describe --broker-list 4 | python3 -m json.tool | head -30
   ```

   Phải thấy **hai** phần tử trong mảng `logDirs`, `logDir` lần lượt là `/tmp/kraft-combined-logs` và `/tmp/kraft-logs-2`, `error` của cả hai là `null`.
3. Tạo một topic **8 partition, RF=1, ghim hết vào broker 4** để quan sát cách rải.

   ```bash
   kt --create --topic jbod-demo --replica-assignment 4,4,4,4,4,4,4,4
   kld --describe --topic-list jbod-demo --broker-list 4 | python3 -m json.tool
   ```

   Đếm số phần tử trong `partitions` của từng `logDir`: phải là **4 và 4**. Kafka đặt mỗi partition mới vào thư mục **đang có ít partition nhất**.
4. Ghi dữ liệu vào topic để hai ổ có kích thước khác nhau.

   ```bash
   docker exec kafka-1 /opt/kafka/bin/kafka-producer-perf-test.sh \
     --topic jbod-demo --num-records 200000 --record-size 200 --throughput -1 \
     --producer-props bootstrap.servers=kafka-1:19092

   kld --describe --topic-list jbod-demo --broker-list 4 \
     | python3 -c "import sys,json; d=json.load(sys.stdin); [print(L['logDir'], sum(p['size'] for p in L['partitions']), 'bytes', len(L['partitions']), 'partitions') for L in d['brokers'][0]['logDirs']]"
   ```
5. 💥 **Làm hỏng log dir thứ hai.** Thu hồi quyền ghi của user chạy Kafka trên thư mục đó.

   ```bash
   docker exec -u 0 kafka-3 chmod 000 /tmp/kraft-logs-2
   docker exec -u 0 kafka-3 ls -ld /tmp/kraft-logs-2
   ```
6. Ép broker chạm vào ổ đó bằng cách ghi tiếp và ép roll segment.

   ```bash
   kcfg --alter --entity-type topics --entity-name jbod-demo --add-config segment.ms=5000
   docker exec kafka-1 /opt/kafka/bin/kafka-producer-perf-test.sh \
     --topic jbod-demo --num-records 200000 --record-size 500 --throughput -1 \
     --producer-props bootstrap.servers=kafka-1:19092
   ```
7. Quan sát hậu quả — **ba góc nhìn**.

   ```bash
   # (a) Log broker
   docker logs kafka-3 2>&1 | grep -iE "KafkaStorageException|offline|Stopping serving logs" | tail -20

   # (b) Tool log-dirs: error khác null
   kld --describe --broker-list 4 | python3 -m json.tool | grep -A2 '"logDir"'

   # (c) Metadata topic: partition mất leader
   kt --describe --topic jbod-demo | head -12
   ```

   Ở (a) phải thấy dòng dạng:

   ```
   ERROR Error while writing to checkpoint file /tmp/kraft-logs-2/... (kafka.server.LogDirFailureChannel)
   java.io.FileNotFoundException: /tmp/kraft-logs-2/... (Permission denied)
   ...
   ERROR Shutdown broker because all log dirs in /tmp/kraft-logs-2 have failed (kafka.log.LogManager)
   ```

   ⚠️ **Đọc kỹ dòng cuối:** nếu broker có **nhiều** log dir, chỉ ổ hỏng bị đưa offline và broker sống tiếp; broker chỉ tự tắt khi **tất cả** log dir đều hỏng. Ở (c), 4 partition nằm trên ổ hỏng sẽ có `Leader: none` (hoặc `-1`) và `Isr:` rỗng — vì RF=1 nên không có replica nào cứu.
8. Xác nhận **broker vẫn sống** và 4 partition ở ổ còn tốt vẫn ghi được.

   ```bash
   docker compose -f docker-compose.cluster.yml -f docker-compose.jbod.yml ps kafka-3
   kt --describe --topic jbod-demo | grep -c "Leader: 4"
   ```
9. 🛠️ **Khôi phục.** Trả quyền rồi restart broker — log dir offline **chỉ trở lại online khi broker khởi động lại**.

   ```bash
   docker exec -u 0 kafka-3 chmod 755 /tmp/kraft-logs-2
   docker compose -f docker-compose.cluster.yml -f docker-compose.jbod.yml restart kafka-3

   sleep 20
   kld --describe --broker-list 4 | python3 -m json.tool | grep '"error"'
   kt --describe --topic jbod-demo | head -12
   ```
10. (Mở rộng, 5 phút) **Cordon** ổ thứ hai để nó không nhận partition mới nữa, rồi tạo topic mới và xác nhận.

    ```bash
    kcfg --alter --entity-type brokers --entity-name 4 \
      --add-config cordoned.log.dirs=/tmp/kraft-logs-2
    kt --create --topic jbod-after-cordon --replica-assignment 4,4,4,4
    kld --describe --topic-list jbod-after-cordon --broker-list 4 | python3 -m json.tool
    ```

    Cả 4 partition mới phải nằm trong `/tmp/kraft-combined-logs`. Gỡ cordon:

    ```bash
    kcfg --alter --entity-type brokers --entity-name 4 --delete-config cordoned.log.dirs
    ```

### ✅ Kiểm chứng

- Bước 3: **4 partition mỗi thư mục** — đây là bằng chứng Kafka rải theo **số partition**. Nếu bạn tạo thêm 1 partition nữa, nó sẽ vào thư mục đang có ít hơn, **bất kể** thư mục đó còn bao nhiêu chỗ trống.
- Bước 7: cả ba góc nhìn phải khớp nhau — log có `KafkaStorageException` / `Permission denied`, `kafka-log-dirs.sh` có `error` khác `null`, và `kt --describe` có partition mất leader.
- Bước 8: container `kafka-3` vẫn `running`, và 4 partition trên ổ tốt vẫn có `Leader: 4`. **Đây là điểm quan trọng nhất của lab.**
- Bước 9: sau restart, `"error": null` cho cả hai log dir và mọi partition có leader trở lại.
- Bước 10: topic mới **không** có partition nào trên ổ bị cordon, nhưng các partition cũ trên đó **vẫn chạy bình thường**.

### 🧹 Dọn dẹp

```bash
kt --delete --topic jbod-demo
kt --delete --topic jbod-after-cordon 2>/dev/null
kcfg --alter --entity-type brokers --entity-name 4 --delete-config cordoned.log.dirs 2>/dev/null
cd ~/kafka-labs
docker compose -f docker-compose.cluster.yml -f docker-compose.jbod.yml up -d kafka-3   # trả kafka-3 về 1 log dir
```

### 🧠 Ý nghĩa với đề thi

- Câu kinh điển: *"broker có 4 ổ đĩa, một ổ hỏng — chuyện gì xảy ra?"* → **chỉ partition trên ổ đó offline**, broker vẫn phục vụ. Phương án "broker tắt hoàn toàn" chỉ đúng khi **mọi** log dir đều hỏng.
- Câu thứ hai: *"vì sao một ổ đầy còn ổ kia trống?"* → vì Kafka rải theo **số partition**, không theo dung lượng.
- Câu thứ ba: *"muốn rút một ổ ra để thay"* → `cordoned.log.dirs` (chặn partition mới) rồi `kafka-reassign-partitions.sh` với `log_dirs` (chuyển cái cũ đi). Cordon **không** tự chuyển gì.
- Nhớ: log dir đã offline **không tự online lại** — phải restart broker.

---

## Lab 2.3 — Retention: vì sao "đặt 1 phút mà data vẫn còn"

**🎯 Mục tiêu:** Chạy hai topic song song, cùng `retention.ms=60000`, khác nhau duy nhất ở `segment.ms` — để thấy bằng mắt rằng retention **chỉ xoá segment đã đóng**.
**🧩 Luyện kỹ năng (liên quan đề):**

- Bẫy số 1 của domain CFG: *"Data is deleted one log segment at a time."*
- Đọc `LogStartOffset` để biết retention đã thực sự xoá được gì.
- Nhớ nhịp quét `log.retention.check.interval.ms` = 300000 (5 phút) và độ trễ xoá thật `file.delete.delay.ms` = 60000.

**⏱️ ~40 phút** (có 2 quãng chờ) · **Yêu cầu trước:** Chuẩn bị chung.

### Các bước

1. Hạ nhịp quét retention xuống **10 giây** cho cả cluster, nếu không bạn phải chờ 5 phút mỗi vòng. Đây là config **read-only** nên phải sửa qua override + restart — nhưng có một đường tắt cho lab: đặt qua biến môi trường trong override.

   ```yaml
   # ~/kafka-labs/docker-compose.fastcheck.yml
   services:
     kafka-1:
       environment:
         KAFKA_LOG_RETENTION_CHECK_INTERVAL_MS: 10000
     kafka-2:
       environment:
         KAFKA_LOG_RETENTION_CHECK_INTERVAL_MS: 10000
     kafka-3:
       environment:
         KAFKA_LOG_RETENTION_CHECK_INTERVAL_MS: 10000
   ```

   ```bash
   cd ~/kafka-labs
   docker compose -f docker-compose.cluster.yml -f docker-compose.fastcheck.yml up -d
   ```

   > 📌 Việc phải dựng override chỉ để đổi một con số chính là bài học: `log.retention.check.interval.ms` là **read-only**. Trên production, đổi nó = rolling restart.
2. Tạo **hai** topic, chỉ khác nhau ở `segment.ms`.

   ```bash
   # A — để segment.bytes/segment.ms mặc định (1 GiB / 7 ngày)
   kt --create --topic ret-default --partitions 1 --replication-factor 3 \
      --config retention.ms=60000

   # B — ép roll segment mỗi 10 giây
   kt --create --topic ret-fast --partitions 1 --replication-factor 3 \
      --config retention.ms=60000 --config segment.ms=10000
   ```
3. Ghi 2000 record vào mỗi topic.

   ```bash
   for T in ret-default ret-fast; do
     docker exec kafka-1 /opt/kafka/bin/kafka-producer-perf-test.sh \
       --topic $T --num-records 2000 --record-size 500 --throughput 500 \
       --producer-props bootstrap.servers=kafka-1:19092
   done
   ```
4. Ghi lại `LogStartOffset` / `LogEndOffset` ban đầu của cả hai.

   ```bash
   docker exec kafka-1 /opt/kafka/bin/kafka-run-class.sh kafka.tools.GetOffsetShell \
     --bootstrap-server kafka-1:19092 --topic ret-default --time -2
   docker exec kafka-1 /opt/kafka/bin/kafka-run-class.sh kafka.tools.GetOffsetShell \
     --bootstrap-server kafka-1:19092 --topic ret-fast --time -2
   ```

   `--time -2` = earliest (chính là `LogStartOffset`), `--time -1` = latest. Lúc này cả hai đều là `:0:0`.
5. **Chờ 3 phút** (đủ để vượt `retention.ms` 60 s cộng vài vòng quét 10 s), rồi đo lại.

   ```bash
   sleep 180
   for T in ret-default ret-fast; do
     echo "--- $T"
     docker exec kafka-1 /opt/kafka/bin/kafka-run-class.sh kafka.tools.GetOffsetShell \
       --bootstrap-server kafka-1:19092 --topic $T --time -2
     docker exec kafka-1 /opt/kafka/bin/kafka-run-class.sh kafka.tools.GetOffsetShell \
       --bootstrap-server kafka-1:19092 --topic $T --time -1
   done
   ```

   Kết quả mong đợi:

   - `ret-fast`: **earliest đã nhảy lên** (gần bằng latest) → segment cũ đã bị xoá.
   - `ret-default`: **earliest vẫn là 0** → chưa xoá được gì, dù `retention.ms` đã quá hạn từ lâu.
6. Nhìn thẳng vào thư mục partition để hiểu vì sao.

   ```bash
   docker exec kafka-1 sh -c 'ls -la /tmp/kraft-combined-logs/ret-default-0/ /tmp/kraft-combined-logs/ret-fast-0/'
   ```

   `ret-default-0` chỉ có **đúng một bộ** `00000000000000000000.log/.index/.timeindex` — đó là **active segment**, và active segment không bao giờ bị xoá. `ret-fast-0` có nhiều segment, trong đó những segment cũ đã biến mất (hoặc đang mang đuôi `.deleted`).
7. 🛠️ **Sửa `ret-default`** theo đúng cách người vận hành làm.

   ```bash
   kcfg --alter --entity-type topics --entity-name ret-default --add-config segment.ms=10000
   sleep 120
   docker exec kafka-1 /opt/kafka/bin/kafka-run-class.sh kafka.tools.GetOffsetShell \
     --bootstrap-server kafka-1:19092 --topic ret-default --time -2
   ```

   Earliest bây giờ đã nhảy lên — cùng một `retention.ms`, chỉ thêm `segment.ms`.
8. (2 phút) Kiểm tra `retention.bytes` tính **per partition**, không phải cả topic.

   ```bash
   kt --create --topic ret-bytes --partitions 4 --replication-factor 3 \
      --config retention.bytes=1048576 --config segment.ms=10000
   kcfg --describe --all --entity-type topics --entity-name ret-bytes | grep "^\s*retention\.bytes="
   ```

   `retention.bytes=1048576` nghĩa là **mỗi partition** tối đa ~1 MiB → topic 4 partition RF=3 chiếm tối đa ~12 MiB trên toàn cluster.

### ✅ Kiểm chứng

- Bước 5 là trái tim của lab: hai topic có **cùng `retention.ms`** nhưng chỉ topic có `segment.ms` nhỏ mới thực sự xoá được dữ liệu.
- Bước 6: `ret-default-0` chỉ có một segment → không có gì để xoá. Nếu bạn thấy nhiều segment ở đây thì có lẽ đã ghi quá 1 GiB, hãy giảm `--num-records`.
- Bước 7: sau khi thêm `segment.ms`, earliest offset nhảy lên trong vòng ~2 phút.

### 🧹 Dọn dẹp

```bash
kt --delete --topic ret-default
kt --delete --topic ret-fast
kt --delete --topic ret-bytes
cd ~/kafka-labs
docker compose -f docker-compose.cluster.yml up -d      # bỏ override fastcheck
```

### 🧠 Ý nghĩa với đề thi

- Đề dựng đúng tình huống này: *"Retention đặt 1 giờ, nhưng consumer vẫn đọc được dữ liệu 3 ngày trước. Người vận hành làm gì?"* → **hạ `segment.ms`** (hoặc `segment.bytes`) trên topic đó. Các phương án "restart broker", "tăng `log.retention.check.interval.ms`", "chạy `kafka-delete-records.sh`" đều là nhiễu (cái cuối *có* xoá được nhưng là hành động một lần, không sửa nguyên nhân).
- Đề cũng hỏi ngược: *"topic 6 partition, `retention.bytes=10 GiB`, RF=3 — tốn bao nhiêu đĩa?"* → 6 × 10 × 3 = **180 GiB**, vì `retention.bytes` là **per partition per replica**.
- Nhớ nhịp: quét mỗi **300000 ms**, file bị đổi tên `.deleted` rồi xoá thật sau **60000 ms**.

---

## Lab 2.4 — Compaction thật: ép cleaner chạy, và nhìn tombstone biến mất ⭐

**🎯 Mục tiêu:** Dựng một compacted topic với tham số "cực đoan" để cleaner chạy trong vài chục giây thay vì vài ngày, ghi nhiều bản của cùng key + tombstone, rồi đọc kết quả bằng `kafka-dump-log.sh`.
**🧩 Luyện kỹ năng (liên quan đề):**

- `min.cleanable.dirty.ratio` · `segment.ms` · `delete.retention.ms` — ba tham số quyết định "bao giờ cleaner đụng vào".
- Tombstone: value `null`, sống `delete.retention.ms` rồi biến mất.
- 4 đảm bảo của compaction, đặc biệt **offset không đổi** và **head vẫn còn key trùng**.

**⏱️ ~50 phút** · **Yêu cầu trước:** Chuẩn bị chung, `npm i kafkajs` trong `~/kafka-labs`.

### Các bước

1. Tạo compacted topic với tham số ép cleaner làm việc ngay.

   ```bash
   kt --create --topic user-state --partitions 1 --replication-factor 3 \
     --config cleanup.policy=compact \
     --config min.cleanable.dirty.ratio=0.01 \
     --config segment.ms=5000 \
     --config delete.retention.ms=10000 \
     --config min.compaction.lag.ms=0 \
     --config max.compaction.lag.ms=20000

   kcfg --describe --entity-type topics --entity-name user-state
   ```

   Giải thích từng con số so với mặc định: dirty ratio **0.01** thay vì 0.5 · segment đóng sau **5 s** thay vì 7 ngày · tombstone sống **10 s** thay vì 24 h · deadline ép dọn **20 s** thay vì Long.MAX.
2. Ghi nhiều bản của cùng một key, bằng `kafkajs`.

   ```javascript
   // ~/kafka-labs/week-02/compact-write.mjs
   import { Kafka, logLevel } from "kafkajs";

   const kafka = new Kafka({
     clientId: "w2-compact",
     brokers: ["localhost:9092", "localhost:9094", "localhost:9096"],
     logLevel: logLevel.NOTHING,
   });

   const producer = kafka.producer();
   await producer.connect();

   // 5 key × 40 bản = 200 record. Bản cuối của mỗi key là version 40.
   for (let v = 1; v <= 40; v++) {
     await producer.send({
       topic: "user-state",
       messages: Array.from({ length: 5 }, (_, k) => ({
         key: `user-${k}`,
         value: JSON.stringify({ user: `user-${k}`, version: v, ts: Date.now() }),
       })),
     });
   }

   // Tombstone cho user-3: key có, value null → xoá key này khỏi snapshot
   await producer.send({
     topic: "user-state",
     messages: [{ key: "user-3", value: null }],
   });

   console.log("Đã ghi 200 record + 1 tombstone (tổng 201 offset: 0..200)");
   await producer.disconnect();
   ```

   ```bash
   cd ~/kafka-labs/week-02 && node compact-write.mjs
   ```
3. Ép segment cuối đóng lại — **cleaner không bao giờ đụng active segment**.

   ```bash
   # Ghi thêm vài record để có gì đó rơi vào segment mới sau khi segment cũ roll
   docker exec kafka-1 sh -c 'for i in 1 2 3; do echo "flush-$i:x"; done | \
     /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server kafka-1:19092 \
     --topic user-state --property parse.key=true --property key.separator=:'
   sleep 20
   ```
4. Tìm broker đang giữ leader của partition 0 và xem thư mục segment của nó.

   ```bash
   kt --describe --topic user-state
   # Giả sử Leader: 3 → đó là container kafka-2. Đổi biến dưới cho khớp.
   export LEADER_CTR=kafka-2

   docker exec $LEADER_CTR ls -la /tmp/kraft-combined-logs/user-state-0/
   ```

   Ngoài `.log/.index/.timeindex` bạn sẽ thấy các file mới của compaction: `leader-epoch-checkpoint`, và ở mức log dir là `cleaner-offset-checkpoint`.

   ```bash
   docker exec $LEADER_CTR cat /tmp/kraft-combined-logs/cleaner-offset-checkpoint
   ```

   File này ghi "đã dọn tới offset nào" cho từng partition — bằng chứng trực tiếp rằng cleaner đã chạy.
5. **Đọc nội dung log bằng `kafka-dump-log.sh`** — công cụ duy nhất nhìn thấy từng record trên đĩa.

   ```bash
   docker exec $LEADER_CTR sh -c '/opt/kafka/bin/kafka-dump-log.sh \
     --files $(ls /tmp/kraft-combined-logs/user-state-0/*.log | tr "\n" ",") \
     --print-data-log --deep-iteration' | grep -E "offset:|payload" | head -40
   ```

   Điều cần nhìn thấy:

   - **Offset có lỗ.** Ví dụ nhảy từ `offset: 3` sang `offset: 187` — đúng như đảm bảo *"offset không đổi"*: compaction xoá record chứ không đánh số lại.
   - Với mỗi key chỉ còn **bản cuối** ở phần tail.
   - Record của `user-3` có `payload: ` **rỗng / null** — đó là tombstone, nếu nó chưa quá `delete.retention.ms`.
6. **Chờ tombstone hết hạn** rồi dump lại.

   ```bash
   sleep 60
   docker exec kafka-1 sh -c 'echo "kick:1" | /opt/kafka/bin/kafka-console-producer.sh \
     --bootstrap-server kafka-1:19092 --topic user-state \
     --property parse.key=true --property key.separator=:'
   sleep 30

   docker exec $LEADER_CTR sh -c '/opt/kafka/bin/kafka-dump-log.sh \
     --files $(ls /tmp/kraft-combined-logs/user-state-0/*.log | tr "\n" ",") \
     --print-data-log --deep-iteration' | grep -c "user-3"
   ```

   Sau khi vượt `delete.retention.ms` = 10 s **và** cleaner chạy thêm một vòng, bản ghi `user-3` (kể cả tombstone) phải biến mất hoàn toàn.
7. Đọc lại từ đầu bằng consumer để xác nhận "đọc từ offset 0 thấy ít nhất trạng thái cuối của mọi key".

   ```bash
   kcc --topic user-state --from-beginning --timeout-ms 8000 \
     --property print.key=true --property print.offset=true | sort -u
   ```

   Bạn sẽ thấy `user-0`, `user-1`, `user-2`, `user-4` với `version: 40`, và **không** thấy `user-3`.
8. **Chứng minh head vẫn còn key trùng.** Ghi thêm 3 bản của `user-0` rồi đọc ngay, không chờ cleaner.

   ```bash
   docker exec kafka-1 sh -c 'for v in 41 42 43; do echo "user-0:{\"version\":$v}"; done | \
     /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server kafka-1:19092 \
     --topic user-state --property parse.key=true --property key.separator=:'

   kcc --topic user-state --from-beginning --timeout-ms 8000 \
     --property print.key=true | grep -c "^user-0"
   ```

   Kết quả **> 1**: compaction **không** đảm bảo "mỗi key đúng 1 record" — phần head chưa được dọn vẫn còn nhiều bản.
9. (2 phút) Thử đổi sang `compact,delete` để thấy hai cơ chế chạy cùng lúc.

   ```bash
   kcfg --alter --entity-type topics --entity-name user-state \
     --add-config cleanup.policy=compact,delete --add-config retention.ms=30000
   kcfg --describe --entity-type topics --entity-name user-state
   ```

### ✅ Kiểm chứng

- Bước 4: `cleaner-offset-checkpoint` có dòng cho `user-state 0` với offset > 0 → cleaner **đã** chạy. Nếu file trống hoặc offset = 0, cleaner chưa đụng tới — chờ thêm và kiểm `segment.ms` đã áp chưa.
- Bước 5: dump log có **lỗ offset**. Đây là bằng chứng mạnh nhất cho "offset là định danh vĩnh viễn".
- Bước 6: `grep -c "user-3"` trả **0**.
- Bước 8: `grep -c "^user-0"` trả **> 1** ngay sau khi ghi — head chưa compact.

### 🧹 Dọn dẹp

```bash
kt --delete --topic user-state
rm -f ~/kafka-labs/week-02/compact-write.mjs
```

### 🧠 Ý nghĩa với đề thi

- Câu hay gặp: *"Đã bật `cleanup.policy=compact` nhưng topic vẫn phình to"* → nguyên nhân gần như luôn là **segment active** (chưa roll) hoặc **dirty ratio chưa chạm 0.5**. Hành động: hạ `segment.ms`, hạ `min.cleanable.dirty.ratio`.
- Câu về tombstone: *"consumer dựng lại cache từ offset 0 nhưng một key đã xoá lại xuất hiện"* → bootstrap lâu hơn `delete.retention.ms` (mặc định **24 h**) nên bỏ lỡ tombstone.
- Câu "chọn phát biểu SAI về compaction": phương án sai gần như luôn là **"mỗi key chỉ còn đúng một record"**.
- Nhớ: compacted topic **bắt buộc có key**, và **không dùng được tiered storage**.

---

## Lab 2.5 — `RecordTooLargeException` ở hai tầng khác nhau

**🎯 Mục tiêu:** Gây cùng một tên ngoại lệ ở **client** và ở **broker**, phân biệt được hai trường hợp chỉ bằng cách đọc thông điệp lỗi, rồi sửa đúng tầng.
**🧩 Luyện kỹ năng (liên quan đề):**

- Ba con số: producer `max.request.size` **1048576** · broker/topic `message.max.bytes` / `max.message.bytes` **1048588** · follower `replica.fetch.max.bytes` **1048576**.
- Lỗi ở client xảy ra **trước khi** có byte nào ra mạng; lỗi ở broker xảy ra **sau một vòng mạng**.
- Sửa ở tầng nào cho tình huống nào.

**⏱️ ~35 phút** · **Yêu cầu trước:** Chuẩn bị chung, `kafkajs`.

### Các bước

1. Tạo topic mặc định.

   ```bash
   kt --create --topic big-msg --partitions 3 --replication-factor 3
   kcfg --describe --all --entity-type topics --entity-name big-msg | grep "^\s*max\.message\.bytes="
   ```

   Phải in `max.message.bytes=1048588` với synonym `DEFAULT_CONFIG:message.max.bytes=1048588`.
2. **Tầng 1 — lỗi ở client.** Gửi record 2 MiB với producer để mặc định.

   ```javascript
   // ~/kafka-labs/week-02/big-msg.mjs
   import { Kafka, logLevel } from "kafkajs";

   const sizeMiB = Number(process.argv[2] ?? 2);
   const maxRequestSize = process.argv[3] ? Number(process.argv[3]) : undefined;

   const kafka = new Kafka({
     clientId: "w2-bigmsg",
     brokers: ["localhost:9092", "localhost:9094", "localhost:9096"],
     logLevel: logLevel.NOTHING,
   });

   const producer = kafka.producer({
     ...(maxRequestSize ? { maxRequestSize } : {}),
   });
   await producer.connect();

   const payload = "x".repeat(sizeMiB * 1024 * 1024);
   try {
     await producer.send({
       topic: "big-msg",
       messages: [{ key: "k1", value: payload }],
     });
     console.log(`✅ Gửi thành công ${sizeMiB} MiB`);
   } catch (err) {
     console.log(`❌ ${err.name}: ${err.message}`);
   } finally {
     await producer.disconnect();
   }
   ```

   ```bash
   cd ~/kafka-labs/week-02 && node big-msg.mjs 2
   ```

   Lỗi mong đợi — **client tự từ chối**, chưa gửi đi byte nào:

   ```
   ❌ KafkaJSError: The message is 2097258 bytes when serialized which is larger than the maximum request size you have configured.
   ```

   > 📌 Trong Java producer, cùng tình huống này ném `org.apache.kafka.common.errors.RecordTooLargeException` với thông điệp *"The message is N bytes when serialized which is larger than `max.request.size`"*. Chữ **`max.request.size`** trong thông điệp là dấu hiệu nhận biết **lỗi ở client**.
3. **Tầng 2 — lỗi ở broker.** Nới trần phía client lên 5 MiB nhưng **giữ nguyên** trần phía broker.

   ```bash
   node big-msg.mjs 2 5242880
   ```

   Lần này request **thực sự bay tới broker** rồi bị từ chối:

   ```
   ❌ KafkaJSProtocolError: The request included a message larger than the max message size the server will accept
   ```

   Java client sẽ hiện `RecordTooLargeException` kèm mã lỗi `MESSAGE_TOO_LARGE`. Xác nhận từ phía broker:

   ```bash
   docker logs kafka-1 2>&1 | grep -i "MESSAGE_TOO_LARGE\|larger than the maximum" | tail -5
   ```
4. 🛠️ **Sửa đúng tầng.** Nới `max.message.bytes` của topic lên 5 MiB.

   ```bash
   kcfg --alter --entity-type topics --entity-name big-msg \
     --add-config max.message.bytes=5242880
   kcfg --describe --all --entity-type topics --entity-name big-msg | grep "^\s*max\.message\.bytes="
   node big-msg.mjs 2 5242880      # bây giờ thành công
   ```
5. **Tầng 3 — follower.** Kiểm tra `replica.fetch.max.bytes` và hiểu vì sao nó *không* làm replication kẹt.

   ```bash
   kcfg --describe --all --entity-type brokers --entity-name 2 \
     | grep -E "^\s*(replica\.fetch\.max\.bytes|message\.max\.bytes)="
   kt --describe --topic big-msg      # Isr phải vẫn đủ 3 replica
   ```

   `replica.fetch.max.bytes` = 1048576 < record 2 MiB, nhưng ISR vẫn đủ: batch **đầu tiên** luôn được trả về dù vượt trần, để replication không bao giờ kẹt. Tuy vậy, thực hành tốt là đặt `replica.fetch.max.bytes` ≥ `message.max.bytes` để follower không phải fetch từng batch một.
6. **Đối chứng ở mức broker default** (thay vì per-topic) để thấy đây là config `cluster-wide`.

   ```bash
   kcfg --alter --entity-type brokers --entity-default --add-config message.max.bytes=5242880
   kt --create --topic big-msg-2 --partitions 1 --replication-factor 3
   kcfg --describe --all --entity-type topics --entity-name big-msg-2 | grep "^\s*max\.message\.bytes="
   ```

   Topic mới **kế thừa** 5242880 từ `DYNAMIC_DEFAULT_BROKER_CONFIG` mà không cần khai gì.

### ✅ Kiểm chứng

- Bước 2 và bước 3 cho **hai thông điệp lỗi khác nhau** dù cùng gửi 2 MiB. Đây là điểm cần nhớ, không phải con số.
- Bước 4: sau khi nới topic config, gửi thành công **ngay lập tức**, không cần restart broker.
- Bước 5: ISR đủ 3 — bằng chứng cho "batch đầu vẫn được trả về".
- Bước 6: topic mới kế thừa, topic cũ (`big-msg`) vẫn dùng override riêng của nó.

### 🧹 Dọn dẹp

```bash
kcfg --alter --entity-type brokers --entity-default --delete-config message.max.bytes
kt --delete --topic big-msg
kt --delete --topic big-msg-2
rm -f ~/kafka-labs/week-02/big-msg.mjs
```

### 🧠 Ý nghĩa với đề thi

- Đề in nguyên văn một exception rồi hỏi *"sửa config nào"*. Nếu thông điệp nhắc `max.request.size` → sửa **producer**. Nếu nhắc *"larger than the max message size the server will accept"* / mã `MESSAGE_TOO_LARGE` → sửa **`max.message.bytes` của topic** (hoặc `message.max.bytes` của broker).
- Nhớ đúng hai con số **1048576** (producer) và **1048588** (broker/topic). Phương án nào ghi cả hai bằng 1048576 là sai.
- Phương án "tăng `replica.fetch.max.bytes` để sửa `RecordTooLargeException`" là nhiễu: nó không gây ra lỗi này.

---

## Lab 2.6 — Làm đầy đĩa: `KafkaStorageException` và đường về ⭐ *(gây hỏng rồi sửa)*

**🎯 Mục tiêu:** Cho `kafka-3` một log dir **chỉ 32 MiB** (tmpfs), ghi cho đầy, quan sát log dir chuyển offline, rồi khôi phục theo đúng playbook.
**🧩 Luyện kỹ năng (liên quan đề):**

- Nhận diện `KafkaStorageException` / `No space left on device` trong log broker.
- Biết rằng log dir đã offline **không tự online lại** — bắt buộc restart sau khi giải phóng chỗ.
- Dùng `kafka-log-dirs.sh` để tìm thủ phạm (partition nào chiếm chỗ) thay vì đoán.

**⏱️ ~45 phút** · **Yêu cầu trước:** Chuẩn bị chung. Lab này **an toàn cho máy host** vì ổ nhỏ là tmpfs trong container, không phải đĩa thật.

### Các bước

1. Tạo override cho `kafka-3`: log dir thứ hai nằm trên **tmpfs 32 MiB**.

   ```yaml
   # ~/kafka-labs/docker-compose.smalldisk.yml
   # kafka-3 (node.id 4) có 2 log dir; dir thứ hai là tmpfs 32 MiB → đầy rất nhanh, không đụng đĩa host.
   services:
     kafka-3:
       environment:
         KAFKA_LOG_DIRS: /tmp/kraft-combined-logs,/tmp/kraft-logs-small
       tmpfs:
         - /tmp/kraft-logs-small:size=32m,mode=1777
   ```

   ```bash
   cd ~/kafka-labs
   docker compose -f docker-compose.cluster.yml -f docker-compose.smalldisk.yml up -d kafka-3
   sleep 20
   kld --describe --broker-list 4 | python3 -m json.tool | grep -E '"logDir"|"totalBytes"|"usableBytes"'
   ```

   Nếu bản Kafka của bạn in `totalBytes`/`usableBytes` (KIP-849), bạn sẽ thấy ngay ổ nhỏ chỉ có ~33 MB.

   > 🩹 Gặp lỗi thiếu `meta.properties` như Lab 2.2 thì dùng đúng cách chữa ở đó (`kafka-storage.sh format --ignore-formatted`).
2. Tạo topic **8 partition RF=1 ghim vào broker 4**, để 4 partition rơi vào ổ nhỏ.

   ```bash
   kt --create --topic fill-me --replica-assignment 4,4,4,4,4,4,4,4 \
     --config segment.bytes=1048576
   kld --describe --topic-list fill-me --broker-list 4 | python3 -m json.tool | grep -E '"logDir"|"partition"'
   ```

   Ghi lại **partition nào nằm trên `/tmp/kraft-logs-small`** — bạn sẽ ghi thẳng vào chúng ở bước sau.
3. 💥 **Đổ dữ liệu cho đầy.** 32 MiB không cần nhiều.

   ```bash
   docker exec kafka-1 /opt/kafka/bin/kafka-producer-perf-test.sh \
     --topic fill-me --num-records 400000 --record-size 500 --throughput -1 \
     --producer-props bootstrap.servers=kafka-1:19092 acks=1
   ```

   Lệnh này sẽ báo lỗi ở một số partition — đó là điều mong muốn.
4. Quan sát hậu quả — vẫn **ba góc nhìn** như Lab 2.2.

   ```bash
   # (a) Log broker
   docker logs kafka-3 2>&1 | grep -iE "No space left|KafkaStorageException|failed|offline" | tail -20

   # (b) Trạng thái log dir
   kld --describe --broker-list 4 | python3 -m json.tool | grep -B1 -A1 '"error"'

   # (c) Partition mất leader
   kt --describe --topic fill-me
   ```

   Ở (a) phải thấy dạng:

   ```
   ERROR Error while appending records to fill-me-1 in dir /tmp/kraft-logs-small (kafka.server.LogDirFailureChannel)
   java.io.IOException: No space left on device
   ...
   WARN Stopping serving logs in dir /tmp/kraft-logs-small (kafka.log.LogManager)
   ```

   Ở (c), những partition nằm trên ổ nhỏ có `Leader: none` và `Isr:` rỗng; những partition trên ổ lớn **vẫn có `Leader: 4`**.
5. Kiểm tra phía client: producer nhận lỗi gì.

   ```bash
   docker exec kafka-1 sh -c 'echo "probe" | /opt/kafka/bin/kafka-console-producer.sh \
     --bootstrap-server kafka-1:19092 --topic fill-me --request-required-acks 1' 2>&1 | tail -5
   ```

   Bạn sẽ thấy `LEADER_NOT_AVAILABLE` hoặc `NOT_LEADER_OR_FOLLOWER` cho các partition hỏng, kèm `KafkaStorageException` nếu request rơi trúng partition đó.
6. 🛠️ **Khôi phục — đúng thứ tự playbook.**

   **Bước 1: tìm thủ phạm** (đừng đoán).

   ```bash
   kld --describe --broker-list 4 | python3 -c "
   import sys, json
   d = json.load(sys.stdin)
   for L in d['brokers'][0]['logDirs']:
       tot = sum(p['size'] for p in L['partitions'])
       print(L['logDir'], 'error=', L['error'], 'bytes=', tot)
       for p in sorted(L['partitions'], key=lambda x: -x['size'])[:5]:
           print('   ', p['partition'], p['size'])
   "
   ```

   **Bước 2: giải phóng chỗ.** Trên production đây là "xoá topic không cần, hạ `retention.ms`, hoặc reassign partition đi broker khác". Trong lab, ổ đang offline nên Kafka không tự dọn được — ta xoá tay:

   ```bash
   docker exec -u 0 kafka-3 sh -c 'du -sh /tmp/kraft-logs-small; rm -rf /tmp/kraft-logs-small/fill-me-*; df -h /tmp/kraft-logs-small'
   ```

   **Bước 3: restart broker** — log dir offline chỉ trở lại khi khởi động lại.

   ```bash
   docker compose -f docker-compose.cluster.yml -f docker-compose.smalldisk.yml restart kafka-3
   sleep 25
   kld --describe --broker-list 4 | python3 -m json.tool | grep '"error"'
   kt --describe --topic fill-me | head -10
   ```

   **Bước 4: phòng tái diễn.** Đặt trần dung lượng cho topic.

   ```bash
   kcfg --alter --entity-type topics --entity-name fill-me \
     --add-config retention.bytes=2097152 --add-config segment.ms=10000
   ```
7. **Rút ra bài học về RF=1.** Vì topic này RF=1, dữ liệu trên ổ hỏng **mất hẳn** — không có replica nào để phục hồi. Xác nhận:

   ```bash
   docker exec kafka-1 /opt/kafka/bin/kafka-run-class.sh kafka.tools.GetOffsetShell \
     --bootstrap-server kafka-1:19092 --topic fill-me --time -1
   ```

   Các partition trên ổ hỏng quay về offset 0. Với RF=3 thì sau restart, follower sẽ kéo lại từ leader và không mất gì.

### ✅ Kiểm chứng

- Bước 4 (c): **có partition sống và có partition chết trên cùng một broker**. Đó là bằng chứng "một ổ hỏng ≠ broker chết", giống Lab 2.2 nhưng với nguyên nhân khác (hết chỗ thay vì mất quyền).
- Bước 6 bước 3: sau restart, mọi `"error"` trở về `null` và mọi partition có leader.
- Bước 7: offset về 0 với RF=1 — nhớ con số này khi đề hỏi "cluster production nên đặt RF bao nhiêu".

### 🧹 Dọn dẹp

```bash
kt --delete --topic fill-me
cd ~/kafka-labs
docker compose -f docker-compose.cluster.yml up -d kafka-3     # trả kafka-3 về 1 log dir, bỏ tmpfs
```

### 🧠 Ý nghĩa với đề thi

- Playbook đĩa đầy theo đúng thứ tự: **`kafka-log-dirs.sh` (nhìn) → giải phóng chỗ hoặc reassign có `--throttle` (sửa) → restart broker (đưa log dir về online) → đặt `retention.bytes`/`segment.ms` (phòng)**. Đề hay hỏi "hành động ĐẦU TIÊN", và câu trả lời gần như luôn là bước *nhìn*, không phải bước *sửa*.
- `KafkaStorageException` là exception đặc trưng của tầng đĩa. Thấy nó → nghĩ ngay tới log dir, không phải tới mạng hay ISR.
- Phương án "log dir sẽ tự online lại khi có chỗ trống" là **sai** — phải restart broker.
- Ghép với Tuần 4 (sizing): đĩa cần ≈ `throughput ghi × retention × RF × 1.2`.

---

## Lab 2.7 — Tiered storage: hai công tắc và một điều kiện loại trừ

**🎯 Mục tiêu:** Thấy tận mắt rằng tiered storage cần **cả hai** công tắc, và rằng nó **từ chối compacted topic** — hai điểm mà đề hỏi thẳng.
**🧩 Luyện kỹ năng (liên quan đề):**

- Broker `remote.log.storage.system.enable` (**read-only**) + topic `remote.storage.enable`.
- `local.retention.ms` mặc định **-2** = kế thừa `retention.ms` → bật xong mà không hạ nó thì không tiết kiệm được gì.
- Điều kiện loại trừ: **compacted topic không dùng được tiered storage**.

**⏱️ ~35 phút** · **Yêu cầu trước:** Chuẩn bị chung.

> ⚠️ **Giới hạn thật của lab này.** Một tiered storage **chạy đủ vòng** cần một `RemoteStorageManager` (S3, GCS, hoặc `LocalTieredStorage` dùng trong test của Kafka). `LocalTieredStorage` nằm trong **test jar**, không có sẵn trong image `apache/kafka:4.3.1`. Vì vậy các bước 1–4 dưới đây tập trung vào **cổng kiểm tra cấu hình** — phần mà đề CCAAK thực sự hỏi — và bước 5 là đường mở rộng nếu bạn muốn chạy đủ.

### Các bước

1. Xác nhận cluster **chưa** bật tiered storage.

   ```bash
   kcfg --describe --all --entity-type brokers --entity-name 2 \
     | grep -E "^\s*(remote\.log\.storage\.system\.enable|log\.local\.retention\.(ms|bytes))="
   ```

   Mong đợi: `remote.log.storage.system.enable=false`, `log.local.retention.ms=-2`, `log.local.retention.bytes=-2`.
2. **Cổng 1 — bật ở topic khi cluster chưa bật.** Kafka phải từ chối.

   ```bash
   kt --create --topic tiered-demo --partitions 3 --replication-factor 3 \
     --config remote.storage.enable=true \
     --config local.retention.ms=10000 \
     --config retention.ms=3600000 \
     --config segment.bytes=1048576
   ```

   Lỗi mong đợi (câu chữ có thể khác đôi chút giữa các bản vá — đọc kỹ output thật của bạn):

   ```
   Error while executing topic command : Tiered Storage functionality is disabled in the broker.
   ```

   ➜ Đây là bằng chứng: **topic-level một mình không đủ**.
3. **Cổng 2 — `remote.log.storage.system.enable` là read-only.** Thử bật động:

   ```bash
   kcfg --alter --entity-type brokers --entity-default \
     --add-config remote.log.storage.system.enable=true
   ```

   Bị từ chối với `Cannot update these configs dynamically`. ➜ Bật tiered storage trên cluster đang chạy = **rolling restart**.
4. **Cổng 3 — compacted topic bị loại.** Tạo topic thường rồi thử ghép hai policy:

   ```bash
   kt --create --topic tiered-compact --partitions 1 --replication-factor 3 \
     --config cleanup.policy=compact --config remote.storage.enable=true
   ```

   Kafka từ chối vì tiered storage **không hỗ trợ compacted topic**. Thử chiều ngược lại cũng vậy: tạo topic tiered rồi `--alter` sang `cleanup.policy=compact`.
5. (Mở rộng — chỉ làm nếu muốn chạy đủ vòng) Dùng `LocalTieredStorage`. Cần tải test jar của Kafka rồi mount vào container, và thêm 5 config vào broker:

   ```yaml
   # ~/kafka-labs/docker-compose.tiered.yml — KHUNG THAM KHẢO, cần jar mới chạy được
   services:
     kafka-3:
       environment:
         KAFKA_REMOTE_LOG_STORAGE_SYSTEM_ENABLE: "true"
         KAFKA_REMOTE_LOG_STORAGE_MANAGER_CLASS_NAME: org.apache.kafka.server.log.remote.storage.LocalTieredStorage
         KAFKA_REMOTE_LOG_STORAGE_MANAGER_CLASS_PATH: /opt/kafka/tiered/*
         KAFKA_REMOTE_LOG_METADATA_MANAGER_LISTENER_NAME: PLAINTEXT
         KAFKA_RSM_CONFIG_DIR: /tmp/tiered-storage
       volumes:
         - ./week-02/tiered-jars:/opt/kafka/tiered:ro
   ```

   Nếu chạy được, lệnh tạo topic của docs Apache là:

   ```bash
   kt --create --topic tieredTopic --partitions 1 --replication-factor 1 \
     --config remote.storage.enable=true \
     --config local.retention.ms=1000 \
     --config retention.ms=3600000 \
     --config segment.bytes=1048576
   ```

   Chú ý `segment.bytes=1048576` trong ví dụ chính thức: **chỉ segment đã đóng mới được đẩy lên remote** — y hệt luật của retention và compaction.
6. Dù không chạy được bước 5, vẫn học được phần quan trọng nhất bằng cách đọc cấu hình mẫu và tự trả lời: *"topic giữ 1 năm, đĩa broker chỉ chứa 6 giờ — đặt gì?"*

   ```
   remote.storage.enable=true
   local.retention.ms=21600000        # 6 giờ trên đĩa broker
   retention.ms=31536000000           # 365 ngày tổng cộng
   ```

### ✅ Kiểm chứng

- Bước 2, 3, 4 đều **phải báo lỗi**. Ba lỗi đó chính là ba điểm thi. Nếu một trong ba lại thành công, đọc kỹ output — có thể cluster của bạn đã bật sẵn tiered storage từ lab trước.
- Bước 1: `log.local.retention.ms=-2` là con số cần nhớ (kế thừa `retention.ms`).

### 🧹 Dọn dẹp

```bash
kt --delete --topic tiered-demo 2>/dev/null
kt --delete --topic tiered-compact 2>/dev/null
kcfg --alter --entity-type brokers --entity-default \
  --delete-config remote.log.storage.system.enable 2>/dev/null
cd ~/kafka-labs
docker compose -f docker-compose.cluster.yml down       # kết thúc tuần
```

### 🧠 Ý nghĩa với đề thi

- Câu kinh điển: *"cần giữ 1 năm dữ liệu, chi phí đĩa broker quá cao"* → **tiered storage** + `local.retention.ms` nhỏ. Phương án "tăng `retention.ms` rồi mua thêm đĩa" là nhiễu đắt tiền; "dùng MirrorMaker 2 sang cluster lưu trữ" là nhiễu phức tạp.
- Câu bẫy: *"bật tiered storage cho `__consumer_offsets`"* → **không được**, nó là compacted topic.
- Câu bẫy thứ hai: *"đã đặt `remote.storage.enable=true` mà đĩa không giảm"* → quên hạ `local.retention.ms` (mặc định `-2` = kế thừa `retention.ms`).
- Nhớ `remote.log.storage.system.enable` là **read-only** → bật nó trên cluster đang chạy nghĩa là **rolling restart**, không phải `kafka-configs.sh`.

---

> ✅ **Xong 7 lab?** Quay lại [Lab checklist trong README](README.md#-lab-checklist) tick từng dòng — nhớ rằng **Lab 2.2 và Lab 2.6 là hai bài "gây hỏng rồi sửa" bắt buộc** của tuần, đừng bỏ qua. Sau đó làm [questions.md](questions.md) (30 câu) và ghi sổ câu sai theo 5 nhóm: ưu tiên config / update mode / `log.dirs` & JBOD / retention & segment / compaction.
