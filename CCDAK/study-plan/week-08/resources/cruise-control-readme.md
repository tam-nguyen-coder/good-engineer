# LinkedIn Cruise Control for Apache Kafka — README

> **Nguồn (official):** https://github.com/linkedin/cruise-control (README.md, branch `main`)
> **Tuần:** 8 — Observability & Operations · **Loại:** GitHub README (dự án mã nguồn mở của LinkedIn, không phải Apache Kafka Docs)
> ⚠️ Nội dung dưới đây được crawl tự động (raw README qua HTTP, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Cruise Control** = công cụ của LinkedIn **tự động cân bằng workload + self-healing** cho cluster Kafka lớn (LinkedIn 10K+ broker). Giải quyết đúng điểm yếu của `kafka-reassign-partitions.sh`: tool chuẩn **không** biết phân tích tải để tự sinh plan; Cruise Control **có**.
- Kiến trúc 4 khối: **Load Monitor** (mẫu metric từ `CruiseControlMetricsReporter` gửi vào topic `__CruiseControlMetrics`, topic này phải `cleanup.policy=delete`) → **Analyzer** (goal optimizer, sinh proposal theo danh sách goal ưu tiên) → **Anomaly Detector** (goal violation, broker failure, metric anomaly, disk failure, slow broker, topic RF/partition-size anomaly, maintenance event) → **Executor** (thực thi reassignment/leader election, có throttle).
- Goal mặc định theo **độ ưu tiên giảm dần**: `RackAwareGoal` → `RackAwareDistributionGoal` → `MinTopicLeadersPerBrokerGoal` → `ReplicaCapacityGoal` → `DiskCapacityGoal` → `NetworkInbound/OutboundCapacityGoal` → `CpuCapacityGoal` → `ReplicaDistributionGoal` → `PotentialNwOutGoal` → `DiskUsage/NetworkInboundUsage/NetworkOutboundUsage/CpuUsageDistributionGoal` → `LeaderReplicaDistributionGoal` → `LeaderBytesInDistributionGoal` → `TopicReplicaDistributionGoal` → `PreferredLeaderElectionGoal`. **Hard goal** (capacity, rack) phải thoả; **soft goal** (distribution) cố gắng tối ưu.
- Self-healing hành động theo 3 kiểu: **fix** (rebalance ngay / fix offline replicas), **check** (đợi grace period rồi xem lại — ví dụ broker failure), **ignore** (tắt self-healing).
- Admin ops qua **REST API** (port mặc định **9090**, path `/kafkacruisecontrol/`): `state`, `load`, `proposals`, `rebalance`, `add_broker`, `remove_broker`, `demote_broker`, `fix_offline_replicas`, PLE, adjust replication factor. Xác minh setup: `http://localhost:9090/kafkacruisecontrol/state`.
- Yêu cầu: **Java 17**, branch `main` tương thích Kafka **2.5 → 4.3** (release `2.5.146+` cho Kafka 4.3); cần `capacity.config.file` (JSON dung lượng broker, mẫu `config/capacityJBOD.json`), `bootstrap.servers`; metrics reporter config prefix `cruise.control.metrics.reporter.` (kể cả SSL).
- Ghi nhớ vị trí trong hệ sinh thái: Confluent có **Self-Balancing Clusters / Auto Data Balancer**; Strimzi tích hợp Cruise Control qua `KafkaRebalance` CR; Amazon MSK có auto-rebalance riêng. CCDAK chỉ hỏi mức nhận diện "công cụ tự cân bằng partition + phát hiện bất thường".

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Introduction

Cruise Control is a product that helps run Apache Kafka clusters at large scale. Due to the popularity of Apache Kafka, many companies have increasingly large Kafka clusters with hundreds of brokers. At LinkedIn, we have 10K+ Kafka brokers, which means broker deaths are an almost daily occurrence and balancing the workload of Kafka also becomes a big overhead.

Kafka Cruise Control is designed to address this operational scalability issue.

### Features

Kafka Cruise Control provides the following features out of the box:

- Resource utilization tracking for brokers, topics, and partitions.
- Query the current Kafka cluster state to see the online and offline partitions, in-sync and out-of-sync replicas, replicas under `min.insync.replicas`, online and offline logDirs, and distribution of replicas in the cluster.
- Multi-goal rebalance proposal generation for:
  - Rack-awareness
  - Resource capacity violation checks (CPU, DISK, Network I/O)
  - Per-broker replica count violation check
  - Resource utilization balance (CPU, DISK, Network I/O)
  - Leader traffic distribution
  - Replica distribution for topics
  - Global replica distribution
  - Global leader replica distribution
  - Custom goals that you wrote and plugged in
- Anomaly detection, alerting, and self-healing for the Kafka cluster, including:
  - Goal violation
  - Broker failure detection
  - Metric anomaly detection
  - Disk failure detection
  - Slow broker detection
- Admin operations, including:
  - Add brokers
  - Remove brokers
  - Demote brokers
  - Rebalance the cluster
  - Fix offline replicas
  - Perform preferred leader election (PLE)
  - Adjust replication factor

### Environment Requirements

- The `main` branch of Cruise Control is compatible with Apache Kafka `2.5+`, `2.6`, `2.7`, `2.8`, `3.0`, `3.1`, `3.8`, `3.9`, `4.0`, and `4.3` (i.e. Releases with `2.5.146+`).
- This project requires Java 17.

### Quick Start

1. Get Cruise Control via `git clone https://github.com/linkedin/cruise-control.git && cd cruise-control/` or by browsing the available releases.
2. This step is required if `CruiseControlMetricsReporter` is used for metrics collection (i.e. the default for Cruise Control). The metrics reporter periodically samples the Kafka raw metrics on the broker and sends them to a Kafka topic.
   - `./gradlew jar` (Note: This project requires Java 17)
   - Copy `./cruise-control-metrics-reporter/build/libs/cruise-control-metrics-reporter-A.B.C.jar` to your Kafka server dependency jar folder (`libs/` for a Kafka release download).
   - Modify Kafka server configuration to set `metric.reporters` to `com.linkedin.kafka.cruisecontrol.metricsreporter.CruiseControlMetricsReporter`.
   - If `SSL` is enabled, ensure that the relevant client configurations are properly set for all brokers. `CruiseControlMetricsReporter` takes all configurations for vanilla `KafkaProducer` with a prefix of `cruise.control.metrics.reporter.` -- e.g. `cruise.control.metrics.reporter.ssl.truststore.password`.
   - If the default broker cleanup policy is `compact`, make sure that the topic to which Cruise Control metrics reporter should send messages is created with the `delete` cleanup policy -- the default metrics reporter topic is `__CruiseControlMetrics`.
3. Start Kafka server.
4. Modify `config/cruisecontrol.properties` of Cruise Control:
   - (Required) fill in `bootstrap.servers` to the Kafka cluster to be monitored.
   - (Required) update `capacity.config.file` to the path of your capacity file. Capacity file is a JSON file that provides the capacity of the brokers. You can start Cruise Control server with the default file (`config/capacityJBOD.json`), but it may not reflect the actual capacity of the brokers.
   - (Optional) set `metric.sampler.class` to your implementation (the default sampler class is `CruiseControlMetricsReporterSampler`)
   - (Optional) set `sample.store.class` to your implementation if you have one (the default `SampleStore` is `KafkaSampleStore`)
5. Run the following command:

   ```
   ./gradlew jar copyDependantLibs
   ./kafka-cruise-control-start.sh [-jars PATH_TO_YOUR_JAR_1,PATH_TO_YOUR_JAR_2] config/cruisecontrol.properties [port]
   ```

   `port` enables customizing the Cruise Control port number (default: `9090`). To emit Cruise Control JMX metrics on a particular port (e.g. `56666`), `export JMX_PORT=56666` before running `kafka-cruise-control-start.sh`.
6. (Verify your setup) Visit `http://localhost:9090/kafkacruisecontrol/state`.

**Note**: Cruise Control will need some time to read the raw Kafka metrics from the cluster. The metrics of a newly up broker may take a few minutes to get stable. Cruise Control will drop the inconsistent metrics (e.g when topic bytes-in is higher than broker bytes-in), so first few windows may not have enough valid partitions.

### REST API

Cruise Control provides a REST API for users to interact with (see the wiki page `REST-APIs` for `/state`, `/load`, `/proposals`, `/rebalance`, `/add_broker`, `/remove_broker`, `/demote_broker`, `/fix_offline_replicas`, `/topic_configuration`, `/admin`).

### How Does It Work

Cruise Control relies on the recent load information of replicas to optimize the cluster. Cruise Control periodically collects resource utilization samples at both broker- and partition-level to infer the traffic pattern of each partition. Based on the traffic characteristics and distribution of all the partitions, it derives the load impact of each partition over the brokers. Cruise Control then builds a workload model to simulate the workload of the Kafka cluster. The goal optimizer explores different ways to generate cluster workload optimization proposals based on the user-specified list of goals.

Cruise Control also monitors the liveness of all the brokers in the cluster. To avoid the loss of redundancy, Cruise Control automatically moves replicas from failed brokers to alive ones.

### Pluggable Components

#### Metric Sampler

The metric sampler enables users to deploy Cruise Control to various environments and work with the existing metric systems. Cruise Control provides a metrics reporter that can be configured in your Apache Kafka server. Metrics reporter generates performance metrics to a Kafka metrics topic that can be consumed by Cruise Control.

#### Sample Store

The Sample Store enables storage of collected metric samples and training samples in an external storage. The default Sample Store implementation produces metric samples back to Kafka.

#### Goals

The goals in Cruise Control are pluggable with different priorities. The default goals in order of decreasing priority are:

- **RackAwareGoal** - Ensures that all replicas of each partition are assigned in a rack aware manner -- i.e. no more than one replica of each partition resides in the same rack.
- **RackAwareDistributionGoal** - A relaxed version of `RackAwareGoal`. As long as replicas of each partition can achieve a perfectly even distribution across the racks, this goal lets placement of multiple replicas of a partition into a single rack.
- **MinTopicLeadersPerBrokerGoal** - Ensures that each alive broker has at least a certain number of leader replica of each topic in a configured set of topics.
- **ReplicaCapacityGoal** - Ensures that the maximum number of replicas per broker is under the specified maximum limit.
- **DiskCapacityGoal** - Ensures that Disk space usage of each broker is below a given threshold.
- **NetworkInboundCapacityGoal** - Ensures that inbound network utilization of each broker is below a given threshold.
- **NetworkOutboundCapacityGoal** - Ensures that outbound network utilization of each broker is below a given threshold.
- **CpuCapacityGoal** - Ensures that CPU utilization of each broker is below a given threshold.
- **ReplicaDistributionGoal** - Attempts to make all the brokers in a cluster have a similar number of replicas.
- **PotentialNwOutGoal** - Ensures that the potential network output (when all the replicas in the broker become leaders) on each of the broker do not exceed the broker's network outbound bandwidth capacity.
- **DiskUsageDistributionGoal** - Attempts to keep the Disk space usage variance among brokers within a certain range relative to the average Disk utilization.
- **NetworkInboundUsageDistributionGoal** / **NetworkOutboundUsageDistributionGoal** - Attempts to keep the inbound / outbound network utilization variance among brokers within a certain range relative to the average.
- **CpuUsageDistributionGoal** - Attempts to keep the CPU usage variance among brokers within a certain range relative to the average CPU utilization.
- **LeaderReplicaDistributionGoal** - Attempts to make all the brokers in a cluster have a similar number of leader replicas.
- **LeaderBytesInDistributionGoal** - Attempts to equalize the leader bytes in rate on each host.
- **TopicReplicaDistributionGoal** - Attempts to maintain an even distribution of any topic's partitions across the entire cluster.
- **PreferredLeaderElectionGoal** - Simply move the leaders to the first replica of each partition.
- **KafkaAssignerDiskUsageDistributionGoal** - (Kafka-assigner mode) Attempts to distribute disk usage evenly among brokers based on swap.
- **IntraBrokerDiskCapacityGoal** / **IntraBrokerDiskUsageDistributionGoal** - (Rebalance-disk mode) Ensures disk space usage of each disk is below a threshold / keeps disk usage variance among disks within range.

#### Anomaly Notifier

The anomaly notifier allows users to be notified when an anomaly is detected. Anomalies include: Broker failure; Goal violation; Metric anomaly; Disk failure; Slow brokers; Topic replication factor anomaly; Topic partition size anomaly; Maintenance Events.

In addition to anomaly notifications, users can enable actions to be taken in response to an anomaly by turning self-healing on for the relevant anomaly detectors. Multiple anomaly detectors work in harmony using distinct mitigation mechanisms. Their actions broadly fall into the following categories:

- **fix** - fix the problem right away (e.g. start a rebalance, fix offline replicas)
- **check** - check the situation again after a configurable delay (e.g. adopt a grace period before fixing broker failures)
- **ignore** - ignore the anomaly (e.g. self-healing is disabled)
