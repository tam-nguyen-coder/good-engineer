# Apache Kafka 4.3 Docs — Incorporating Security Features in a Running Cluster

> **Nguồn (official):** https://kafka.apache.org/43/security/incorporating-security-features-in-a-running-cluster/
> **Tuần:** 5 — Security administration · **Loại:** Apache Kafka Docs (Security → Incorporating Security Features in a Running Cluster)
> ⚠️ Nội dung dưới đây được crawl tự động (WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- Đây là trang **quan trọng nhất của Tuần 5** cho dạng câu *list order*: "sắp xếp các bước bật bảo mật cho cluster đang chạy". Kafka làm việc này bằng **nhiều đợt rolling bounce**, không bao giờ tắt cả cluster.
- **4 pha chuẩn** (thuộc lòng đúng thứ tự):
  1. **Bounce đợt 1** — mở thêm cổng bảo mật, **giữ nguyên** cổng PLAINTEXT.
  2. **Đổi client** sang cổng bảo mật (client là thứ chuyển **giữa hai lần bounce**, không phải cuối cùng).
  3. **Bounce đợt 2** — bật bảo mật cho **inter-broker** (`security.inter.broker.protocol` / `inter.broker.listener.name`).
  4. **Bounce đợt 3 (cuối)** — **đóng cổng PLAINTEXT**.
- Lý do bắt buộc giữ PLAINTEXT xuyên suốt: trong lúc chuyển, broker cũ và broker mới vẫn phải nói chuyện được với nhau và với client chưa kịp đổi. Đóng sớm = **cluster tự chia đôi**.
- Mỗi lần bounce phải **dừng broker sạch bằng SIGTERM** (để `controlled.shutdown` chạy) và **chờ replica vừa restart quay lại ISR** rồi mới sang node kế tiếp. Đây chính là quy tắc "chờ `UnderReplicatedPartitions` về 0" của rolling restart.
- Ví dụ mở đồng thời nhiều cổng khi vừa muốn SSL cho inter-broker vừa muốn SASL_SSL cho client:
  `listeners=PLAINTEXT://broker1:9091,SSL://broker1:9092,SASL_SSL://broker1:9093`.
- Cùng một khung 4 pha áp dụng cho: bật TLS lần đầu, bật SASL lần đầu, **đổi mechanism SASL**, **đổi cổng hoặc protocol của controller listener** (nhờ `controller.listener.names` nhận nhiều giá trị).
- 📌 Ghép với kiến thức dynamic config: **xoay chứng chỉ** (đổi keystore/truststore của một listener **đã tồn tại**) **không cần** quy trình 4 pha này — làm được bằng `kafka-configs.sh` mà **không restart**. Quy trình 4 pha dành cho việc **thêm/bớt listener hoặc đổi protocol**, là những config **read-only** cần restart.

---

## 📄 Nội dung (trích từ tài liệu gốc)

You can secure a running cluster via one or more of the supported protocols discussed previously. This is done in phases:

- Incrementally bounce the cluster nodes to open additional secured port(s).
- Restart clients using the secured rather than PLAINTEXT port (assuming you are securing the client-broker connection).
- Incrementally bounce the cluster again to enable broker-to-broker security (if this is required).
- A final incremental bounce to close the PLAINTEXT port.

The specific steps for configuring SSL and SASL are described in the sections above. Follow these steps to enable security for your desired protocol(s).

The security implementation lets you configure different protocols for both broker-client and broker-broker communication. These must be enabled in separate bounces. A PLAINTEXT port must be left open throughout so brokers and/or clients can continue to communicate.

When performing an incremental bounce stop the brokers cleanly via a SIGTERM. It's also good practice to wait for restarted replicas to return to the ISR list before moving onto the next node.

### Example: add SSL encryption for both broker-client and broker-broker communication

**As an example**, say we wish to add SSL encryption for both broker-client and broker-broker communication. In the first incremental bounce, an SSL port is opened on each node:

```
listeners=PLAINTEXT://broker1:9091,SSL://broker1:9092
```

We then restart the clients, changing their config to point at the newly opened, secured port:

```
bootstrap.servers = [broker1:9092,...]
security.protocol = SSL
...etc
```

In the second incremental server bounce we instruct Kafka to use SSL as the broker-broker protocol (which will use the same SSL port):

```
listeners=PLAINTEXT://broker1:9091,SSL://broker1:9092
security.inter.broker.protocol=SSL
```

In the final bounce we secure the cluster by closing the PLAINTEXT port:

```
listeners=SSL://broker1:9092
security.inter.broker.protocol=SSL
```

### Example: use SSL for broker-broker and SASL_SSL for client-broker

**Alternatively** we might choose to open multiple ports so that different protocols can be used for broker-broker and broker-client communication. Say we wished to use SSL encryption throughout (i.e. for broker-broker and broker-client communication) but we'd like to add SASL authentication to the broker-client connection also. We would achieve this by opening two additional ports during the first bounce:

```
listeners=PLAINTEXT://broker1:9091,SSL://broker1:9092,SASL_SSL://broker1:9093
```

We would then restart the clients, changing their config to point at the newly opened, SASL & SSL secured port:

```
bootstrap.servers = [broker1:9093,...]
security.protocol = SASL_SSL
...etc
```

The second server bounce would switch the cluster to use encrypted broker-broker communication via the SSL port we previously opened on port 9092:

```
listeners=PLAINTEXT://broker1:9091,SSL://broker1:9092,SASL_SSL://broker1:9093
security.inter.broker.protocol=SSL
```

The final bounce secures the cluster by closing the PLAINTEXT port:

```
listeners=SSL://broker1:9092,SASL_SSL://broker1:9093
security.inter.broker.protocol=SSL
```
