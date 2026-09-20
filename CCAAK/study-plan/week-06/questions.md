# 📝 Practice Questions — Week 6: Kafka Connect operations

> **28 questions** · real CCAAK exam style (scenario-first: a symptom, a CLI output or a metric, then "what does the administrator do?") · anchored on **Apache Kafka 4.3** · covers the full Week 6 material + 2 review questions from Week 5 (Security).
> 🔒 **Answers & explanations are in a separate file:** [answers.md](answers.md). Attempt everything first.
> Tag: `[DOMAIN · Topic · type]`. Multi = multiple-response (the number to choose is stated). Domains: `CONNECT` (Kafka Connect), `SEC` (Security).
> Back to [week plan](README.md) · [labs](labs.md) · [master plan](../../CCAAK-STUDY-PLAN.md)

---

### Question 1 — `[CONNECT · Cluster topology · Single]`

An administrator starts a second Kafka Connect worker to scale out an existing distributed cluster. Both workers start cleanly and both REST endpoints answer. However, `GET /connectors` on the first worker returns `["orders-sink"]` while the same call on the second worker returns `[]`, and the second worker never receives any tasks. Both workers point at the same `bootstrap.servers`. What should the administrator check FIRST?

- A. Whether the second worker registered its ephemeral node under `/connect/workers` in ZooKeeper
- B. Whether both workers share the same `group.id` **and** the same `config.storage.topic`, `offset.storage.topic` and `status.storage.topic` names — any difference makes them two independent Connect clusters
- C. Whether `tasks.max` on `orders-sink` is high enough to produce tasks for a second worker
- D. Whether the second worker was started with `connect-standalone.sh` instead of `connect-distributed.sh`

### Question 2 — `[CONNECT · Internal topics · Single]`

Before handing a new Connect cluster to a team, an administrator inspects its internal topics:

```
Topic: connect-configs   PartitionCount: 3   ReplicationFactor: 3   Configs: cleanup.policy=compact
Topic: connect-offsets   PartitionCount: 25  ReplicationFactor: 3   Configs: cleanup.policy=compact
Topic: connect-status    PartitionCount: 5   ReplicationFactor: 3   Configs: cleanup.policy=compact
```

Which statement identifies the problem and the correct remedy?

- A. Nothing is wrong; three partitions on the config topic simply spreads the write load
- B. `connect-offsets` should have 5 partitions and `connect-status` 25; swap the two `*.storage.partitions` settings
- C. `connect-configs` must have exactly **one** partition — it was auto-created using the broker's `num.partitions=3`. Stop the workers, delete and recreate the topic with 1 partition and `cleanup.policy=compact`, then restart
- D. All three topics should use `cleanup.policy=delete` so that stale connector configurations expire after the retention period

### Question 3 — `[CONNECT · Task failure · Single]`

A monitoring dashboard shows a connector as healthy. An administrator checks it directly:

```json
{
  "name": "payments-sink",
  "connector": { "state": "RUNNING", "worker_id": "connect-1:8083" },
  "tasks": [
    { "id": 0, "state": "RUNNING", "worker_id": "connect-1:8083" },
    { "id": 1, "state": "FAILED",  "worker_id": "connect-2:8083",
      "trace": "org.apache.kafka.connect.errors.ConnectException: Tolerance exceeded in error handler\n..." },
    { "id": 2, "state": "RUNNING", "worker_id": "connect-2:8083" }
  ],
  "type": "sink"
}
```

Which statement about this situation is correct?

- A. Because the connector is `RUNNING`, the failed task will be rebalanced onto another worker automatically within `scheduled.rebalance.max.delay.ms`
- B. A failed task triggers no rebalance and is never restarted automatically; the administrator must fix the underlying cause and then call `POST /connectors/payments-sink/restart?includeTasks=true&onlyFailed=true`
- C. The connector state should also read `FAILED`; the fact that it does not means the status topic is corrupted
- D. Deleting and recreating the connector is the only supported way to recover a `FAILED` task

### Question 4 — `[CONNECT · Failure handling · Multi — Choose 2]`

Which two statements correctly describe how a distributed Connect cluster reacts to failures? (Choose two.)

- A. When a worker process dies, its tasks are reassigned to the surviving workers by the cluster leader
- B. When a task fails, Connect triggers a cluster-wide rebalance so that the task can be retried on a different worker
- C. When a task fails, no rebalance is triggered — a task failure is treated as an exceptional case that requires operator action
- D. When a worker process dies, every connector in the cluster transitions to `FAILED` until an administrator restarts them
- E. When a task fails, the connector object it belongs to always transitions to `FAILED` as well

### Question 5 — `[CONNECT · Rebalance timing · Single]`

An administrator kills one of three Connect workers to test failover. Three minutes later, `GET /connectors/orders-sink/status` still shows the dead worker's tasks in state `UNASSIGNED` and no task has moved. The surviving workers are healthy and the REST API responds normally. What is happening?

- A. The Connect cluster has lost quorum and cannot elect a new leader; restart the remaining workers
- B. `session.timeout.ms` on the workers is set to the consumer default of 45000 ms, which is too long; lower it to 10000 ms
- C. This is the intended behaviour of `scheduled.rebalance.max.delay.ms` (default **300000 ms**): the leader defers reassigning a departed worker's tasks for up to five minutes so that a quick restart does not churn the whole cluster
- D. The tasks are waiting for `offset.flush.timeout.ms` to expire before they can be reassigned

### Question 6 — `[CONNECT · Task parallelism · Single]`

A sink connector is configured with `tasks.max=8` and consumes a topic with **3** partitions. After deployment, how many tasks will typically exist and what will they be doing?

- A. 3 tasks, because Connect computes the task count as `min(tasks.max, number of partitions)`
- B. 1 task, because `tasks.max` only applies to source connectors
- C. 8 tasks, all of them `RUNNING`, but only 3 of them own a topic partition — the other 5 are idle consumers in the group `connect-<connector-name>`
- D. 8 tasks, of which 5 will transition to `FAILED` because there are not enough partitions to assign

### Question 7 — `[CONNECT · Scaling diagnostics · Single]`

After raising `tasks.max` from 3 to 6 on a sink connector, throughput is unchanged. The administrator runs:

```
$ kafka-consumer-groups.sh --bootstrap-server kafka-1:19092 \
    --describe --group connect-billing-sink --members

GROUP                  CONSUMER-ID                        HOST         CLIENT-ID                     #PARTITIONS
connect-billing-sink   connector-consumer-...-0-9a1f      /10.0.1.21   connector-consumer-...-0      1
connect-billing-sink   connector-consumer-...-1-3c77      /10.0.1.21   connector-consumer-...-1      1
connect-billing-sink   connector-consumer-...-2-b04e      /10.0.1.22   connector-consumer-...-2      1
connect-billing-sink   connector-consumer-...-3-7f2a      /10.0.1.22   connector-consumer-...-3      0
connect-billing-sink   connector-consumer-...-4-115d      /10.0.1.21   connector-consumer-...-4      0
connect-billing-sink   connector-consumer-...-5-e8c9      /10.0.1.22   connector-consumer-...-5      0
```

What is the correct next action?

- A. Restart the three members showing `#PARTITIONS 0`, since they failed to receive an assignment
- B. Increase the number of partitions on the source topic first, then keep `tasks.max=6`; task count is bounded by partitions only in terms of *useful work*, not in terms of tasks created
- C. Switch the connector's consumer to `partition.assignment.strategy=RoundRobinAssignor` so partitions are spread over all six members
- D. Lower `tasks.max` back to 3 and add three more Connect workers instead

### Question 8 — `[CONNECT · REST restart semantics · Single]`

A task is in state `FAILED`. An administrator runs:

```
$ curl -s -X POST -w "\nHTTP %{http_code}\n" http://connect-1:8083/connectors/orders-sink/restart
HTTP 204
```

Thirty seconds later the task is still `FAILED`. Why, and what is the correct call?

- A. HTTP 204 means the request was rejected; retry until it returns 200
- B. Without `includeTasks=true` the call restarts only the connector object, not its tasks. Use `POST /connectors/orders-sink/restart?includeTasks=true&onlyFailed=true`, which returns **202** when task instances are actually restarted
- C. The connector must be paused before it can be restarted; call `PUT /connectors/orders-sink/pause` first
- D. Task restarts can only be requested on the worker that owns the task; send the request to that worker's REST port

### Question 9 — `[CONNECT · REST API · Single]`

An automation script updates connector configurations. It sends the following and receives an error:

```
$ curl -s -X PUT -H "Content-Type: application/json" \
    http://connect-1:8083/connectors/orders-sink/config \
    --data '{"name":"orders-sink","config":{"connector.class":"...","tasks.max":"4"}}'
{"error_code":400,"message":"Connector config {name=orders-sink, config={...}} contains no connector type"}
```

What is wrong?

- A. `PUT /connectors/{name}/config` expects the **flat** configuration map as its body; the wrapped `{"name":…, "config":{…}}` envelope belongs to `POST /connectors`
- B. `PUT` cannot be used to update a connector; only `POST /connectors` works, and the connector must be deleted first
- C. The `Content-Type` header must be `application/vnd.connect.v1+json`
- D. The request must be sent to the cluster leader; followers reject `PUT` with 400

### Question 10 — `[CONNECT · Offsets · Single]`

A team wants a sink connector to reprocess a topic from the beginning. They run `DELETE /connectors/orders-sink`, wait for 204, then recreate the connector with exactly the same name and configuration. The connector starts successfully but writes nothing to the target system, and `kafka-consumer-groups.sh --describe --group connect-orders-sink` reports `LAG 0`. What happened?

- A. The recreated connector needs `auto.offset.reset=earliest` in its worker configuration
- B. Deleting a connector does not delete its offsets. A sink connector's offsets live in the consumer group `connect-orders-sink`, which survived the delete, so the new connector resumed from the committed position
- C. The `connect-offsets` topic is compacted, so the old offsets were replayed into the new connector
- D. The delete did not take effect because the connector was not stopped first

### Question 11 — `[CONNECT · Offsets · Single]`

Continuing from the previous incident, the administrator tries to reset the offsets through the REST API:

```
$ curl -s -X PUT http://connect-1:8083/connectors/orders-sink/pause
$ curl -s -X DELETE http://connect-1:8083/connectors/orders-sink/offsets
{"error_code":400,"message":"Connectors must be in a stopped state before their offsets can be modified. ..."}
```

What is the correct sequence?

- A. `PUT /connectors/orders-sink/pause` → `DELETE /connectors/orders-sink/offsets` → `PUT /connectors/orders-sink/resume`; the error indicates a transient rebalance, so simply retry
- B. `PUT /connectors/orders-sink/stop` → `DELETE /connectors/orders-sink/offsets` → `PUT /connectors/orders-sink/resume`; `PAUSED` keeps the tasks alive, while `STOPPED` shuts them down completely, which is what offset modification requires
- C. `DELETE /connectors/orders-sink` → `DELETE /connectors/orders-sink/offsets` → recreate the connector
- D. Produce a tombstone for the connector's key into the `connect-offsets` topic, then resume the connector

### Question 12 — `[CONNECT · Offsets · Multi — Choose 2]`

Which two statements about where Kafka Connect keeps connector offsets are correct? (Choose two.)

- A. Source connector offsets are stored in the worker's `offset.storage.topic` (default `connect-offsets`, 25 partitions, compacted) as connector-defined partition/offset pairs
- B. Sink connector offsets are stored in the same `connect-offsets` topic, keyed by connector name
- C. Sink connector offsets are ordinary consumer group offsets in `__consumer_offsets`, under the group `connect-<connector-name>`, and can be reset with `kafka-consumer-groups.sh`
- D. In standalone mode, source connector offsets are written to the ZooKeeper path configured by `offset.storage.znode`
- E. `GET /connectors/{name}/offsets` works only for sink connectors, because source offsets have no standard schema

### Question 13 — `[CONNECT · Error handling · Single]`

A sink connector kept failing whenever a malformed record appeared, so an engineer added `errors.tolerance=all` and nothing else. The connector has been `RUNNING` for two weeks with no alerts. The downstream team now reports that roughly 0.3% of records are missing, with no trace in any log. What is the explanation and the fix?

- A. `errors.tolerance=all` only tolerates retriable errors; raise `errors.retry.timeout` to `-1` so the records are eventually delivered
- B. With `errors.tolerance=all` and no dead letter queue configured, bad records are skipped **silently**. Add `errors.deadletterqueue.topic.name`, set `errors.deadletterqueue.context.headers.enable=true`, and enable `errors.log.enable=true`
- C. The records were filtered out by the default single message transformation chain; remove the `transforms` property
- D. The sink task committed offsets before writing; set `errors.tolerance=none` and increase `offset.flush.interval.ms`

### Question 14 — `[CONNECT · Dead letter queue · Multi — Choose 3]`

A sink connector runs against a **3-broker** cluster and must route unprocessable records to a dead letter queue with enough context to debug them, without stopping the pipeline. Which three configuration entries belong in the connector configuration? (Choose three.)

- A. `errors.tolerance=all`
- B. `errors.deadletterqueue.topic.name=payments-dlq`
- C. `errors.deadletterqueue.context.headers.enable=true`
- D. `errors.deadletterqueue.enable=true`
- E. `errors.tolerance=none` together with `errors.retry.timeout=-1`

### Question 15 — `[CONNECT · Dead letter queue · Single]`

A JDBC **source** connector occasionally hits rows it cannot convert. The team asks the administrator to route those rows to a dead letter queue so the ingest job keeps running. What is the correct response?

- A. Add `errors.deadletterqueue.topic.name` to the source connector configuration — it works identically for source and sink connectors
- B. Dead letter queues exist only for **sink** connectors; the source connector configuration has no `errors.deadletterqueue.*` properties. For a source, the available options are `errors.tolerance`, `errors.log.enable`/`errors.log.include.messages` and `errors.retry.*`, plus fixing the data at the source
- C. Set `errors.tolerance=all` on the worker configuration, which enables a cluster-wide dead letter queue for all connectors
- D. Enable `exactly.once.source.support=enabled` on the worker; failed records are then written to the transaction log for later inspection

### Question 16 — `[CONNECT · Diagnosing a failed task · Single]`

A sink task fails with the following trace, taken from `GET /connectors/events-sink/status`:

```
org.apache.kafka.connect.errors.ConnectException: Tolerance exceeded in error handler
  at org.apache.kafka.connect.runtime.errors.RetryWithToleranceOperator.execAndHandleError(...)
Caused by: org.apache.kafka.connect.errors.DataException: Converting byte[] to Kafka Connect data failed due to serialization error:
  at org.apache.kafka.connect.json.JsonConverter.toConnectData(JsonConverter.java:333)
Caused by: com.fasterxml.jackson.core.JsonParseException: Unrecognized token 'PING': was expecting (JSON String, Number, Array, Object or token 'null', 'true' or 'false')
 at [Source: (byte[])"PING"; line: 1, column: 5]
```

What does this trace tell the administrator?

- A. The sink system rejected the record; increase `errors.retry.timeout` so the write is retried
- B. The failure happened in the **value converter** stage: a non-JSON record reached a connector configured with `JsonConverter`, and `errors.tolerance` is still at its default `none`. Fix the converter or the producer, and decide on a tolerance/DLQ policy before restarting the tasks
- C. The `connect-status` topic is not compacted, so an old stack trace is being replayed
- D. The task exceeded `offset.flush.timeout.ms` while committing, and the parse error is a side effect

### Question 17 — `[CONNECT · Deployment mode · Single]`

A company runs a single Connect worker in production today and wants to be able to add a second worker later without rewriting anything. Operations also want to change connector configurations without editing files on the host. Which deployment mode should the administrator choose, and why?

- A. Standalone mode, because with one worker there is nothing to coordinate and it can be converted to distributed later by adding `group.id`
- B. Distributed mode even with a single worker: connectors are managed through the REST API, configuration/offsets/status live in Kafka topics, and adding a second worker later requires only starting another process with the same `group.id`
- C. Standalone mode with `offset.storage.topic` configured, which gives file-free offsets while keeping the simpler startup command
- D. Distributed mode, but only after at least three workers are available, since the Connect cluster needs a majority quorum

### Question 18 — `[CONNECT · Standalone mode · Multi — Choose 2]`

Which two statements about Kafka Connect **standalone** mode are correct? (Choose two.)

- A. Connector configurations are passed as `.properties` files on the `connect-standalone.sh` command line, not through the REST API
- B. Source connector offsets are written to the local file named by `offset.storage.file.filename`
- C. Standalone workers register themselves in ZooKeeper so that other standalone workers can discover them and share tasks
- D. Standalone mode stores connector configurations in the `config.storage.topic` so they survive a restart
- E. Standalone mode provides the same fault tolerance as distributed mode as long as the process is managed by systemd

### Question 19 — `[CONNECT · Client overrides · Single]`

A regulated workload requires that one specific sink connector authenticate to the brokers as `User:payments-svc` rather than with the shared worker principal, while all other connectors keep using the worker's credentials. Which approach is correct on Apache Kafka 4.3?

- A. Start a second Connect cluster with a different `group.id` and the payments credentials; per-connector credentials are not supported
- B. Set `connector.client.config.override.policy` on the **worker** to `Principal` (or `Allowlist`), then add `consumer.override.security.protocol`, `consumer.override.sasl.mechanism` and `consumer.override.sasl.jaas.config` to that connector's configuration
- C. Nothing needs to be enabled: the policy defaults to `None`, which already permits security-related overrides on a per-connector basis
- D. Put the credentials in the worker's `consumer.sasl.jaas.config`; Connect resolves them per connector using the connector name as the principal

### Question 20 — `[CONNECT · Connector & task states · Matching]`

Match each observed state with the action a competent administrator takes. Each action is used exactly once.

| # | Observed state |
|---|---|
| 1 | A task has been in `FAILED` state for ten minutes |
| 2 | The connector shows `STOPPED` and `GET /connectors/{n}/tasks` returns an empty list |
| 3 | All tasks show `UNASSIGNED` and `rebalancing` has been `true` for several minutes |
| 4 | The connector and all its tasks show `PAUSED` after a planned maintenance window |

| Letter | Action |
|---|---|
| A | Call `PUT /connectors/{n}/resume` to bring the tasks back to `RUNNING` |
| B | Investigate the workers — one is probably restart-looping — before changing any connector configuration |
| C | Read the `trace` field, fix the root cause, then call `POST /connectors/{n}/restart?includeTasks=true&onlyFailed=true` |
| D | This is the expected precondition for `PATCH`/`DELETE` on `/connectors/{n}/offsets`; proceed with the offset operation |

### Question 21 — `[CONNECT · Security · Single]`

A newly deployed sink connector fails immediately after the cluster enabled authorization. The task trace reads:

```
org.apache.kafka.common.errors.GroupAuthorizationException: Not authorized to access group: connect-invoices-sink
```

The connector's principal already has `Read` and `Describe` on the topic it consumes. What is missing?

- A. `Write` permission on the `connect-offsets` topic for the connector's principal
- B. A `Read` ACL on the **Group** resource `connect-invoices-sink` — a sink connector's tasks form a consumer group named after the connector, and topic ACLs alone are not enough
- C. `Create` permission on the Cluster resource, which every connector needs in order to register
- D. `super.users` must include the connector's principal, because Connect always runs its consumers as a superuser

### Question 22 — `[CONNECT · Security · Multi — Choose 2]`

The Connect REST API of a production cluster is currently reachable over plain HTTP with no authentication. Which two changes address this? (Choose two.)

- A. Configure `listeners=https://0.0.0.0:8443` and the corresponding `listeners.https.ssl.keystore.location` / `listeners.https.ssl.keystore.password` properties, and set `rest.advertised.listener=https`
- B. Set `security.protocol=SSL` in the worker configuration, which secures both the broker connections and the REST interface
- C. Add `rest.extension.classes=org.apache.kafka.connect.rest.basic.auth.extension.BasicAuthSecurityRestExtension` and provide a JAAS login module for REST users
- D. Set `rest.port=0` so the REST interface binds to a random port that attackers cannot guess
- E. Set `connector.client.config.override.policy=None`, which disables the REST API for non-administrators

### Question 23 — `[CONNECT · Offset reset procedure · Ordering]`

An administrator must make a sink connector reprocess its input topic from the beginning, using only the Connect REST API, with no data loss for other connectors. Put the five steps in the correct order.

1. `PUT /connectors/{name}/resume`
2. `DELETE /connectors/{name}/offsets`
3. `GET /connectors/{name}/status` and confirm the state is `STOPPED` with zero tasks
4. `PUT /connectors/{name}/stop`
5. `GET /connectors/{name}/offsets` and record the current values before changing anything

- A. 5 → 4 → 3 → 2 → 1
- B. 4 → 5 → 2 → 3 → 1
- C. 5 → 2 → 4 → 3 → 1
- D. 3 → 5 → 4 → 2 → 1

### Question 24 — `[CONNECT · Observability · Multi — Choose 2]`

An administrator kills one of two Connect workers and watches JMX. Which two observations confirm that the cluster recovered correctly? (Choose two.)

- A. `kafka.connect:type=connect-worker-metrics` → `task-count` on the surviving worker increases to the total number of tasks in the cluster
- B. `kafka.connect:type=connect-worker-rebalance-metrics` → `rebalancing` returns to `false` and `completed-rebalances-total` has increased by at least one
- C. `kafka.connect:type=connect-worker-metrics` → `connector-count` reports the cluster-wide number of connectors and therefore does not change
- D. `kafka.connect:type=connector-task-metrics` → `status` becomes `stopped` for the tasks that moved
- E. `kafka.connect:type=task-error-metrics` → `total-retries` increases by exactly the number of tasks that moved

### Question 25 — `[CONNECT · Observability · Single]`

A sink connector's tasks are all `RUNNING` and the consumer group shows `LAG 0`, yet the target system receives no rows. JMX shows, for every task:

```
sink-record-read-rate = 412.6
sink-record-send-rate = 0.0
put-batch-avg-time-ms = 0.0
```

What is the most likely cause?

- A. The target system is down; `sink-record-send-rate` measures successful writes to the external system
- B. Records are being read from Kafka but eliminated before reaching the sink task — `sink-record-send-rate` counts records **after** transformations, so a `Filter` transformation (or a predicate) is dropping everything
- C. `errors.tolerance=all` is discarding every record; check the dead letter queue
- D. The tasks own no partitions, so nothing is being processed

### Question 26 — `[CONNECT · Plugin upgrades · Single]`

A team must upgrade a JDBC connector from 10.6 to 10.8 across 40 connector instances, but wants to migrate them a few at a time and be able to roll individual connectors back. The cluster runs Apache Kafka **4.3**. What is the correct approach?

- A. Stand up a second Connect cluster with the new plugin version and move connectors across one by one, since a worker can only load one version of a plugin
- B. Install both plugin versions under `plugin.path`, restart the workers once so the new JAR is discovered, then set `connector.plugin.version` per connector to migrate or roll back individual instances (KIP-891, available since Kafka 4.1)
- C. Replace the JAR in place and perform a rolling restart; running connectors keep the old classes in memory until they are restarted individually
- D. Set `plugin.discovery=service_load`, which allows Connect to load several plugin versions and pick the newest one per connector automatically

### Question 27 — `[SEC · Week 5 review · Single]`

An administrator must rotate the password of the SASL/SCRAM user `etl-service` on a running Kafka 4.3 cluster without restarting any broker. Which command does this?

- A. `kafka-configs.sh --bootstrap-server kafka-1:9092 --alter --add-config 'SCRAM-SHA-512=[password=new-secret]' --entity-type users --entity-name etl-service`
- B. `kafka-storage.sh format --add-scram 'SCRAM-SHA-512=[name=etl-service,password=new-secret]' --cluster-id <id>`
- C. `kafka-acls.sh --bootstrap-server kafka-1:9092 --alter --principal User:etl-service --add-config password=new-secret`
- D. Edit `jaas.conf` on every broker and perform a rolling restart

### Question 28 — `[SEC · Week 5 review · Single]`

A client can establish a TLS connection to a broker but every request is rejected with `TopicAuthorizationException`, while a second client using the same certificate chain works normally. The listener uses `SSL` with `ssl.client.auth=required` and the brokers set `ssl.principal.mapping.rules` to the default. What is the most likely cause?

- A. The failing client's certificate has expired, which Kafka reports as an authorization error
- B. With the default mapping rules the principal is the **full distinguished name** of the certificate (for example `User:CN=etl,OU=data,O=Acme,C=VN`), so an ACL written as `User:etl` does not match that client's DN
- C. `ssl.endpoint.identification.algorithm` must be cleared on the failing client
- D. The broker needs `allow.everyone.if.no.acl.found=true` before certificate-based principals can be authorized

---

> ✅ Done? Check your answers in [answers.md](answers.md), log every wrong answer with the reason you got it wrong (missing knowledge / skipped a qualifier / fell for a version trap / ran out of time), then re-read the matching section of the [week plan](README.md) before moving on to Week 7.
