# ✅ Answers & Explanations — Week 6: Kafka Connect operations

> Open only after you have attempted every question in [questions.md](questions.md).
> Back to [week plan](README.md) · [labs](labs.md) · [master plan](../../CCAAK-STUDY-PLAN.md)

**Answer key:** 1-B · 2-C · 3-B · 4-AC · 5-C · 6-C · 7-B · 8-B · 9-A · 10-B · 11-B · 12-AC · 13-B · 14-ABC · 15-B · 16-B · 17-B · 18-AB · 19-B · 20-(1→C, 2→D, 3→B, 4→A) · 21-B · 22-AC · 23-A · 24-AB · 25-B · 26-B · 27-A · 28-B

---

### Question 1 — Answer: **B**

- **Why correct:** a Connect cluster is defined by **four** values that must match on every worker: `group.id` and the three internal topic names. Workers that differ in any one of them form a **separate** cluster that happens to use the same Kafka brokers. The symptom fits exactly: each worker has its own config topic, so each sees a different connector list, and neither will ever hand tasks to the other.
- **Why the others are wrong:** A — Connect has never used ZooKeeper for worker discovery, and Kafka 4.x has no ZooKeeper at all; distributed workers join a Kafka group and persist state in three Kafka topics. C — `tasks.max` controls parallelism inside one connector; it cannot cause a worker to be invisible, and the second worker sees no connectors at all, not just no tasks. D — a standalone worker does not expose `/connectors` as a cluster view and would not join anything, but the question states both REST endpoints answer as a distributed cluster would; besides, the first thing to compare is still the four identity values.
- 🧠 **Key point / trap:** "two workers, same brokers, different lists" is always an **identity mismatch**, not a networking problem. Check `group.id` first, then the three topic names.
- 📎 Source: `resources/connect-user-guide-standalone-distributed.md` (`group.id` must not conflict; all workers in a cluster use the same internal topics) and `resources/connect-cluster-rebalance-kip415-kip891.md`.

### Question 2 — Answer: **C**

- **Why correct:** the config topic must have **exactly one partition** — Kafka's own documentation says it "should be a single partition, highly replicated, compacted topic" and warns that "auto created topics may have multiple partitions". With more than one partition the ordering of configuration records is no longer total, so workers can converge on inconsistent state. The offsets (25) and status (5) partition counts in the output are the documented defaults and are fine.
- **Why the others are wrong:** A — the config topic is a serialized log of cluster state, not a throughput problem; spreading it across partitions destroys ordering. B — 25 and 5 are already correct: `offset.storage.partitions` defaults to 25 and `status.storage.partitions` to 5. D — all three topics must be **compacted**: they hold current state, and `delete` would silently discard connector configs and source offsets once retention expired.
- 🧠 **Key point / trap:** there is no `config.storage.partitions` setting, because one partition is a requirement rather than a default. If you see anything other than 1, the topic was auto-created.
- 📎 Source: `resources/connect-user-guide-standalone-distributed.md` (verbatim quote) and `resources/connect-worker-configs-4.3.md` (25 / 5 / RF 3).

### Question 3 — Answer: **B**

- **Why correct:** Confluent's documentation is explicit: "When a worker fails, tasks are rebalanced across the active workers. **When a task fails, no rebalance is triggered, as a task failure is considered an exceptional case.**" Nothing in Connect retries a failed task on its own. The operator reads the `trace`, fixes the cause, then restarts with `includeTasks=true` (and usually `onlyFailed=true` so healthy tasks are not disturbed).
- **Why the others are wrong:** A — `scheduled.rebalance.max.delay.ms` governs how long the leader defers reassigning the tasks of a **departed worker**; it has nothing to do with failed tasks, and both workers here are alive. C — this is normal and documented: the connector object and its tasks have independent states, which is precisely why you must read the `tasks[]` array. D — delete-and-recreate is destructive, unnecessary, and does not even clear offsets, so it fixes nothing.
- 🧠 **Key point / trap:** `connector.state = RUNNING` proves nothing. A dashboard that only watches the connector state will miss every task failure.
- 📎 Source: `resources/connect-cluster-rebalance-kip415-kip891.md` (task rebalancing rule) and `resources/connect-rest-api-reference.md` (`/status` shape).

### Question 4 — Answer: **A, C**

- **Why correct:** A and C are the two halves of the same documented rule. A dead **worker** is a membership change, so the group rebalances and the leader redistributes its tasks. A dead **task** is an application-level error; Connect records it in the status topic and waits for a human.
- **Why the others are wrong:** B — inverted; this is exactly the behaviour the documentation rules out. D — a worker failure does not fail any connector; the surviving workers pick up the work (after the scheduled delay). E — connector and task states are independent; a connector commonly stays `RUNNING` while one of its tasks is `FAILED`, as in Question 3.
- 🧠 **Key point / trap:** "worker dies → automatic; task dies → manual" is the single most reusable sentence of this domain. Expect it phrased as a scenario rather than as a definition.
- 📎 Source: `resources/connect-cluster-rebalance-kip415-kip891.md`.

### Question 5 — Answer: **C**

- **Why correct:** `scheduled.rebalance.max.delay.ms` defaults to **300000 ms** and is described as the "maximum delay to wait for departed workers before rebalancing". Connect deliberately leaves the departed worker's tasks `UNASSIGNED` for up to five minutes so that a rolling restart or a brief crash-loop does not shuffle the whole cluster twice. Three minutes of no movement is the feature working, not a fault.
- **Why the others are wrong:** A — Connect has no quorum; it uses Kafka's group protocol, and the REST API answering proves the group is healthy. B — the worker default for `session.timeout.ms` is **10000 ms**, not 45000; 45000 is the *consumer* default, and mixing the two is the trap this option is built from. Worker liveness was already detected here — that is why the tasks show `UNASSIGNED`. D — `offset.flush.timeout.ms` (5000) bounds a source task's offset commit and plays no part in reassignment.
- 🧠 **Key point / trap:** three timers, three jobs — `session.timeout.ms` **10000** detects the dead worker, `scheduled.rebalance.max.delay.ms` **300000** defers the handover, `rebalance.timeout.ms` **60000** bounds one rebalance round. Lowering the delay buys faster failover at the cost of extra rebalances during maintenance.
- 📎 Source: `resources/connect-worker-configs-4.3.md` and `resources/connect-cluster-rebalance-kip415-kip891.md`.

### Question 6 — Answer: **C**

- **Why correct:** `tasks.max` is documented as the "**Maximum** number of tasks to use for this connector", and the runtime asks the connector for its task configurations via `taskConfigs(maxTasks)`. Most sink connectors simply return `maxTasks` configurations, so 8 tasks are created and all start successfully. Each task is a consumer in the group `connect-<connector-name>`, and a consumer group can give a partition to only one member, so with 3 partitions exactly 3 tasks get work and 5 sit idle with `partition-count = 0`.
- **Why the others are wrong:** A — `min(tasks.max, partitions)` is the formula that circulates in third-party material and it is **wrong**: it describes how many tasks have work, not how many exist. B — `tasks.max` applies to both connector types; it is source connectors like `FileStreamSource` that ignore it by returning a single task. D — idle consumers are perfectly legal; they stay `RUNNING`, they just own nothing.
- 🧠 **Key point / trap:** to raise sink throughput, add **partitions first**, then tasks. Adding tasks alone adds idle consumers, extra connections and extra rebalance participants for zero benefit.
- 📎 Source: `resources/connect-sink-source-connector-configs.md` (`tasks.max` default 1, "Maximum number of tasks") and `resources/connect-cluster-rebalance-kip415-kip891.md`.

### Question 7 — Answer: **B**

- **Why correct:** the output is the proof that six tasks exist and only three own a partition — three members report `#PARTITIONS 0`. The bottleneck is the partition count of the source topic, so the fix is to increase partitions; the six tasks then each pick up work at the next rebalance without any further change.
- **Why the others are wrong:** A — the three members did receive an assignment; the assignment is simply empty, which is the correct outcome when members outnumber partitions. Restarting them changes nothing. C — the assignor decides *which* member gets a partition, never *how many* partitions exist; no assignor can give one partition to two members of the same group. D — more workers spread the same six tasks over more machines; the three idle tasks stay idle, and lowering `tasks.max` would leave you exactly where you started.
- 🧠 **Key point / trap:** `#PARTITIONS 0` in `--members` output is the signature of over-provisioned sink tasks. It is the same idle-consumer rule you already know from consumer groups, arriving through a Connect-shaped question.
- 📎 Source: `resources/connect-cluster-rebalance-kip415-kip891.md` (sink tasks are consumers in `connect-<name>`) and `resources/connect-monitoring-jmx-metrics.md` (`partition-count`).

### Question 8 — Answer: **B**

- **Why correct:** `includeTasks` defaults to **false**, so a bare `restart` restarts only the connector instance and leaves the task instances untouched — which is why the task is still `FAILED`. The documented response codes make this visible: **200/204** when only the connector was restarted, **202 ACCEPTED** when task instances were actually restarted (`includeTasks=true` or `onlyFailed=true`). Adding `onlyFailed=true` restarts the broken tasks without bouncing the healthy ones.
- **Why the others are wrong:** A — 204 means the request succeeded with no content; it is not a rejection, and retrying an identical call produces the same result. C — pausing is not a precondition for restarting; it is an unrelated lifecycle operation. D — any worker accepts the call and forwards it to the leader; that is what `rest.advertised.*` exists for.
- 🧠 **Key point / trap:** learn the restart query parameters as a pair. "Restart my failed tasks and nothing else" is `?includeTasks=true&onlyFailed=true`, and the fact that it returns **202** rather than 200 is itself a testable detail.
- 📎 Source: `resources/connect-rest-api-reference.md` (restart parameters and response codes).

### Question 9 — Answer: **A**

- **Why correct:** the two creation endpoints take different shapes. `POST /connectors` takes the envelope `{"name": …, "config": {…}}`; `PUT /connectors/{name}/config` takes the **flat** configuration map, because the name is already in the URL. Sending the envelope to `PUT` makes Connect treat `name` and `config` as configuration keys, so it finds no `connector.class` and rejects the request.
- **Why the others are wrong:** B — `PUT /connectors/{name}/config` is an **upsert**: 201 when it creates, 200 when it updates. It is the recommended way to change a running connector and deleting first is both unnecessary and destructive. C — the API uses plain `application/json`. D — followers forward writes to the leader; a leader-only restriction would return 409 during rebalance, not a 400 about a missing connector type.
- 🧠 **Key point / trap:** wrapped body → `POST /connectors`. Flat body → `PUT /connectors/{name}/config`. Getting this backwards is one of the most common real-world Connect automation bugs.
- 📎 Source: `resources/connect-rest-api-reference.md` (both request shapes shown verbatim).

### Question 10 — Answer: **B**

- **Why correct:** deleting a connector removes its configuration and stops its tasks; it does **not** remove offsets. A sink connector's offsets are ordinary consumer group offsets stored under `connect-<connector-name>`, and that group survives the delete. Recreating the connector with the same name means the same group, so the new tasks resume exactly where the old ones stopped — hence `LAG 0` and no output.
- **Why the others are wrong:** A — `auto.offset.reset` only applies when there is **no** committed offset; here there is one, so it is never consulted. And it is a consumer property, set through `consumer.override.*` on the connector, not a worker-level fix for this. C — `connect-offsets` holds **source** connector offsets; this is a sink connector, and compaction preserves the latest value rather than replaying anything. D — the delete clearly took effect (204, and the connector was recreatable); stopping first is required for *offset* operations, not for deletion.
- 🧠 **Key point / trap:** "delete and recreate to start over" is a reflex that does not work in Connect. Offsets outlive the connector for **both** types, which is the whole reason KIP-875 added explicit offset endpoints.
- 📎 Source: `resources/connect-offset-management-kip875.md`.

### Question 11 — Answer: **B**

- **Why correct:** the offset endpoints require the `STOPPED` state, documented as "the connector must exist and be in the stopped state". `PAUSED` keeps the tasks alive, so the consumer group still has members and the broker cannot delete it — which is exactly what `DELETE /offsets` does for a sink connector. `PUT /stop` shuts the tasks down completely (`tasks` becomes an empty list), after which the offset operation succeeds and `PUT /resume` brings the connector back.
- **Why the others are wrong:** A — this is the sequence that just failed; the 400 is a state error, not a transient rebalance (that would be 409), so retrying will fail identically. C — deleting the connector removes the thing you are trying to operate on, and as Question 10 showed it does not clear offsets anyway. D — hand-writing tombstones into `connect-offsets` is the pre-KIP-875 hack, it is error-prone because the keys are connector-defined, and for a **sink** connector the offsets are not even in that topic.
- 🧠 **Key point / trap:** `pause` ≠ `stop`. Only `stop` destroys the tasks, and only `stop` unlocks offset modification. Expect at least one question that offers `pause` as the plausible-looking wrong answer.
- 📎 Source: `resources/connect-offset-management-kip875.md` and `resources/connect-rest-api-reference.md` (`pause` vs `stop` semantics).

### Question 12 — Answer: **A, C**

- **Why correct:** A and C describe the two distinct storage mechanisms. Source connectors define their own partition/offset pairs (for example `{"filename": …} → {"position": …}`) and the framework persists them in `offset.storage.topic`, which defaults to 25 partitions and is compacted. Sink connectors are consumers, so their progress is an ordinary committed offset in `__consumer_offsets` under the group `connect-<connector-name>`, resettable with `kafka-consumer-groups.sh` once the group is inactive.
- **Why the others are wrong:** B — `connect-offsets` holds source offsets only; nothing about a sink connector is written there. D — there is no `offset.storage.znode`, and standalone offsets go to the **local file** named by `offset.storage.file.filename`; Kafka 4.x has no ZooKeeper. E — `GET /connectors/{name}/offsets` works for both types; the response shape simply differs, opaque for source and `kafka_topic`/`kafka_partition`/`kafka_offset` for sink.
- 🧠 **Key point / trap:** source and sink offsets live in different systems, with different shapes and different reset tools. Every "how do I replay?" question resolves once you identify the connector type.
- 📎 Source: `resources/connect-offset-management-kip875.md` and `resources/connect-worker-configs-4.3.md`.

### Question 13 — Answer: **B**

- **Why correct:** `errors.tolerance=all` means "skip problematic records". With no dead letter queue and `errors.log.enable` at its default of **false**, a skipped record leaves no artefact anywhere — no exception, no log line, no topic. A steady trickle of unparseable records therefore disappears silently, which matches "0.3% missing, no trace". The fix is to keep the tolerance but capture what is skipped: a DLQ topic, context headers so the reason is attached, and application logging.
- **Why the others are wrong:** A — `errors.tolerance` is not limited to retriable errors, and retrying forever cannot fix a record that will never parse; it would only stall the task. C — Connect applies no transformations unless `transforms` is configured, and the configuration described adds only one property. D — the ordering of commits is not the issue, and `errors.tolerance=none` would restore the original failure mode the engineer was trying to escape.
- 🧠 **Key point / trap:** Confluent puts it bluntly — the three strategies are "fail fast, silently ignore, and dead letter queues". `errors.tolerance=all` **on its own** is the "silently ignore" strategy, and it is the classic wrong-looking-right exam option.
- 📎 Source: `resources/connect-error-handling-dlq-kip298.md`.

### Question 14 — Answer: **A, B, C**

- **Why correct:** these three are exactly the documented recipe. `errors.tolerance=all` stops the task from dying, `errors.deadletterqueue.topic.name` names the topic (empty by default, which means DLQ off), and `errors.deadletterqueue.context.headers.enable=true` attaches the `__connect.errors.*` headers that carry the original topic/partition/offset, the failing stage and the exception — without them the DLQ holds bytes with no explanation. On a 3-broker cluster the default `errors.deadletterqueue.topic.replication.factor=3` is already valid, so it does not need to be changed.
- **Why the others are wrong:** D — there is no `errors.deadletterqueue.enable` property; the DLQ is switched on by naming a topic. E — `errors.tolerance=none` fails the task on the first bad record, which is the opposite of "without stopping the pipeline", and infinite retries would block rather than divert.
- 🧠 **Key point / trap:** remember that the RF default is **3**. On a 1- or 2-broker cluster you must lower `errors.deadletterqueue.topic.replication.factor`, otherwise the task dies while trying to create the very topic meant to save it.
- 📎 Source: `resources/connect-sink-source-connector-configs.md` (defaults) and `resources/connect-error-handling-dlq-kip298.md`.

### Question 15 — Answer: **B**

- **Why correct:** the generated configuration reference for source connectors contains `errors.tolerance`, `errors.log.enable`, `errors.log.include.messages`, `errors.retry.timeout` and `errors.retry.delay.max.ms` — and **no** `errors.deadletterqueue.*` keys at all. Confluent states it directly: "Dead Letter Queues apply only to sink connectors." A DLQ is a Kafka topic that a sink writes rejected *Kafka* records to; a source failure happens before the record exists in Kafka, so there is nothing of that shape to divert.
- **Why the others are wrong:** A — the property simply does not exist for source connectors and would be rejected as an unknown configuration. C — `errors.tolerance` is a **connector** property, not a worker property, and there is no cluster-wide DLQ. D — exactly-once source support concerns producer transactions and zombie fencing; it does not capture bad input rows anywhere.
- 🧠 **Key point / trap:** "DLQ is sink-only" is one of the highest-frequency facts in this domain. When a question asks for a DLQ on a source connector, the correct answer is always that it does not exist.
- 📎 Source: `resources/connect-sink-source-connector-configs.md` (side-by-side tables, with the explicit note that the source table has no DLQ keys).

### Question 16 — Answer: **B**

- **Why correct:** the trace reads bottom-up. `JsonParseException: Unrecognized token 'PING'` is the root cause; `DataException: Converting byte[] to Kafka Connect data failed due to serialization error` thrown from `JsonConverter.toConnectData` names the **value converter** as the failing stage; `Tolerance exceeded in error handler` means `errors.tolerance` is still `none`, so the first bad record killed the task. The remedy is to fix the mismatch between the data and the converter (or the producer that wrote `PING`), and then decide deliberately whether to run with a DLQ.
- **Why the others are wrong:** A — the sink system was never reached; the failure is in deserialization, and retries cannot make invalid JSON parse. C — the status topic stores the trace faithfully; compaction settings do not fabricate stack traces. D — `offset.flush.timeout.ms` produces a "Failed to flush, timed out" message, which is nowhere in this trace.
- 🧠 **Key point / trap:** always read a Connect trace from the **last** `Caused by` upward, and use the class name in the middle frame (`JsonConverter`, an SMT class, or the sink task class) to identify the pipeline stage. That stage is also what the `__connect.errors.stage` header would record.
- 📎 Source: `resources/connect-error-handling-dlq-kip298.md` (converter errors, `Unknown magic byte!` / `DataException` patterns) and `resources/connect-rest-api-reference.md` (`trace` field).

### Question 17 — Answer: **B**

- **Why correct:** distributed mode with one worker already gives everything the requirements ask for: connectors are created and modified over the REST API, configuration, offsets and status live in Kafka topics so they survive a restart, and scaling out later is just starting a second process with the same `group.id` and the same three topic names. Nothing has to be rewritten.
- **Why the others are wrong:** A — converting standalone to distributed is not a matter of adding one property: the connector definitions move from command-line files into the config topic and the offsets move from a local file into a Kafka topic, so it is a migration. C — `offset.storage.topic` is a distributed-mode property; standalone uses `offset.storage.file.filename`. D — Connect has no quorum requirement; it relies on Kafka's group coordinator, and a one-worker distributed cluster is entirely valid.
- 🧠 **Key point / trap:** the only genuine reason to choose standalone is that the job is intrinsically tied to one machine — an agent tailing files on the host that produces them. Everything else, including single-worker deployments, is distributed.
- 📎 Source: `resources/connect-user-guide-standalone-distributed.md`.

### Question 18 — Answer: **A, B**

- **Why correct:** standalone is started as `connect-standalone.sh worker.properties conn1.properties [conn2.properties …]`, so connectors come from files on the command line, and its distinguishing property is `offset.storage.file.filename`, the local file that holds source connector offsets.
- **Why the others are wrong:** C — Connect never used ZooKeeper for discovery, standalone workers do not form clusters at all, and Kafka 4.x has removed ZooKeeper entirely. D — `config.storage.topic` is a distributed-mode property; a standalone worker holds connector configuration only in the files it was given and in memory. E — a process supervisor restarts a dead process but cannot move work elsewhere; the documentation is explicit that standalone has "no fault tolerance".
- 🧠 **Key point / trap:** the file-based offset store is the one-line giveaway for standalone mode. If an option mentions `offset.storage.file.filename`, the question is about standalone; if it mentions the three topics, it is about distributed.
- 📎 Source: `resources/connect-user-guide-standalone-distributed.md`.

### Question 19 — Answer: **B**

- **Why correct:** per-connector credentials are exactly what `producer.override.*` / `consumer.override.*` / `admin.override.*` are for, and they only take effect if the worker's `connector.client.config.override.policy` permits them. `Principal` is the policy purpose-built for this case: it allows precisely `security.protocol`, `sasl.mechanism` and `sasl.jaas.config` and nothing else. `Allowlist` (Kafka 4.2+) achieves the same with an explicit list and is the direction the documentation recommends.
- **Why the others are wrong:** A — per-connector credentials are supported; a second cluster is the pre-override workaround and is far more operational overhead. C — the default in Apache Kafka 4.3 is **`All`**, not `None` (it changed in Kafka 3.0 via KIP-722), and `None` would block every override including security ones — the option is wrong twice over. D — Connect does not derive a principal from the connector name; the worker-level `consumer.sasl.jaas.config` is a single shared credential for every sink connector.
- 🧠 **Key point / trap:** two version facts travel together here. The default **was** `None` and **is** `All` since 3.0; and from 4.2 the documentation recommends `Allowlist`, which becomes the default in 5.0. Older study material still teaches the pre-3.0 default.
- 📎 Source: `resources/connect-security-rest-and-clients.md` and `resources/connect-worker-configs-4.3.md`.

### Question 20 — Answer: **1 → C, 2 → D, 3 → B, 4 → A**

- **Why correct:**
  - **1 → C.** A `FAILED` task never recovers on its own and triggers no rebalance. Read `trace`, fix the cause, then `restart?includeTasks=true&onlyFailed=true`.
  - **2 → D.** `STOPPED` with zero tasks is precisely the state the offset endpoints require; `PATCH`/`DELETE /connectors/{n}/offsets` are documented as needing the stopped state.
  - **3 → B.** Every task `UNASSIGNED` plus a stuck `rebalancing = true` is a **cluster** symptom, not a connector symptom — typically a worker crash-looping or repeatedly missing `session.timeout.ms`. Changing connector configuration during an unfinished rebalance only adds 409s.
  - **4 → A.** `PAUSED` is a user-requested state; the tasks still exist, so `resume` is all that is needed.
- **Why the others are wrong:** each action maps to exactly one state. Using C on state 2 would restart a connector you deliberately stopped; using A on state 1 does nothing because the task is failed rather than paused; using D on state 4 fails because `PAUSED` is not `STOPPED`; using B on state 1 sends you hunting a cluster problem that does not exist.
- 🧠 **Key point / trap:** the distinction that carries the whole table is **who caused the state**. `PAUSED`/`STOPPED` are yours, `FAILED` is the data's or the target system's, `UNASSIGNED` is the cluster's.
- 📎 Source: `resources/connect-rest-api-reference.md` (state list and lifecycle) and `resources/connect-monitoring-jmx-metrics.md` (status attribute values).

### Question 21 — Answer: **B**

- **Why correct:** a sink connector's tasks join a consumer group named `connect-<connector-name>`, and Kafka authorizes group membership separately from topic access. The exception names the resource explicitly: `Not authorized to access group: connect-invoices-sink`. The missing ACL is `Read` on the **Group** resource with that exact name.
- **Why the others are wrong:** A — `connect-offsets` holds source offsets and is accessed by the worker's own principal, not by a sink connector's consumer; a missing ACL there would surface as a topic error on a different resource. C — `Create` on Cluster is needed by the **worker** to create its internal topics, not by each connector, and the error would be a cluster authorization error. D — putting service principals in `super.users` defeats authorization entirely, and Connect consumers are ordinary clients with ordinary ACLs.
- 🧠 **Key point / trap:** read the exception type before the message. `TopicAuthorizationException` → topic ACL; `GroupAuthorizationException` → group ACL. For sink connectors the group name is derivable from the connector name, which is what makes this fixable in one command.
- 📎 Source: `resources/connect-security-rest-and-clients.md` (connector ACL requirements, `connect-{name}` group naming).

### Question 22 — Answer: **A, C**

- **Why correct:** A secures the transport. The REST interface is configured through `listeners`, and its TLS material uses the dedicated **`listeners.https.*`** prefix rather than the generic `ssl.*` block (which configures the worker's connection to the brokers); `rest.advertised.listener=https` ensures workers forward requests to each other over the same scheme. C adds authentication, which Connect implements as a REST extension — `rest.extension.classes` is empty by default, which is why the API is open.
- **Why the others are wrong:** B — `security.protocol` governs the worker's client connections to Kafka and has no effect on the REST server. D — an unauthenticated API on an unusual port is still an unauthenticated API; port scanning is trivial. E — the override policy limits which **client** configurations a connector may override; it neither authenticates nor authorizes REST callers.
- 🧠 **Key point / trap:** Connect has **two** independent security surfaces — worker-to-broker (`security.protocol`, `sasl.*`, `ssl.*`) and client-to-REST (`listeners`, `listeners.https.*`, `rest.extension.classes`). Securing one says nothing about the other, and an open REST API is effectively admin access to every topic the worker can reach.
- 📎 Source: `resources/connect-security-rest-and-clients.md` and `resources/connect-worker-configs-4.3.md` (`listeners` default `http://:8083`, `rest.extension.classes` default `""`).

### Question 23 — Answer: **A** (5 → 4 → 3 → 2 → 1)

- **Why correct:** record the current offsets first (step 5) so the change is reversible — this is the cheap, read-only action and it costs nothing. Then stop the connector (4), because `DELETE /offsets` requires the `STOPPED` state. Confirm the state actually reached `STOPPED` with zero tasks (3), since `stop` is asynchronous and returns 202 immediately. Only then reset the offsets (2), and finally resume (1).
- **Why the others are wrong:** B — stopping before reading the offsets still works but loses the ability to verify the state before mutating, and it places the confirmation *after* the mutation, which is the wrong order for an irreversible step. C — calls `DELETE /offsets` while the connector is still running, which returns 400. D — checking for `STOPPED` before issuing `stop` is meaningless, and the connector is never actually stopped before the reset.
- 🧠 **Key point / trap:** the pattern CCAAK rewards is *read → stop → verify → mutate → resume*. Every ordering question in this domain is really asking whether you verify the asynchronous state transition before the destructive step.
- 📎 Source: `resources/connect-offset-management-kip875.md` and `resources/connect-rest-api-reference.md` (202 Accepted on `stop`).

### Question 24 — Answer: **A, B**

- **Why correct:** A — `connector-count` and `task-count` in `connect-worker-metrics` count what runs "in this worker", so when one of two workers dies the survivor's `task-count` rises to the cluster total. That is the most direct numeric proof that the tasks were reassigned. B — a healthy recovery ends with `rebalancing` back to `false` and `completed-rebalances-total` incremented; a value stuck at `true` is the signature of a cluster that has not converged.
- **Why the others are wrong:** C — the statement inverts the metric's meaning: `connector-count` is per worker, not cluster-wide, so it also changes. D — `stopped` is not a valid value for `connector-task-metrics → status` (only `unassigned`, `running`, `paused`, `failed`, `restarting`); `stopped` exists only at the connector level. E — `total-retries` belongs to `task-error-metrics` and counts retried **record operations** after errors; moving a task does not increment it.
- 🧠 **Key point / trap:** Connect metrics are **per worker**. A cluster-level view requires scraping every worker and summing — a single worker's `task-count` is never the cluster's task count.
- 📎 Source: `resources/connect-monitoring-jmx-metrics.md`.

### Question 25 — Answer: **B**

- **Why correct:** the two rates are defined around the transformation chain. `sink-record-read-rate` is measured "**before** transformations are applied"; `sink-record-send-rate` is measured "**after** transformations are applied and excludes any records filtered out by the transformations". Reading 412/s while sending 0/s therefore means every record is being removed between the two points — a `Filter` transformation, or a predicate that matches everything. `put-batch-avg-time-ms = 0.0` confirms the sink task's `put()` is never called with data, and `LAG 0` confirms Kafka-side consumption is healthy.
- **Why the others are wrong:** A — `sink-record-send-rate` counts records handed to the sink task, not rows acknowledged by the external system; a dead target usually shows rising `sink-record-active-count` and failing tasks instead. C — records dropped by `errors.tolerance` would appear in `total-records-skipped` and would normally arrive with errors logged or a DLQ; nothing here points at conversion failures. D — tasks owning no partitions would show `partition-count = 0` and a `sink-record-read-rate` of 0, not 412.
- 🧠 **Key point / trap:** learn the read/send and poll/write pairs as **before/after the transformation chain**. The gap between the two is the single fastest way to spot an over-eager SMT.
- 📎 Source: `resources/connect-monitoring-jmx-metrics.md` (verbatim metric descriptions).

### Question 26 — Answer: **B**

- **Why correct:** KIP-891 shipped in **Kafka 4.1** and lets a worker load several versions of the same plugin at once. Installing the new JAR still requires one worker restart so the plugin is discovered, but after that each connector selects its version through `connector.plugin.version` (and the matching `*.converter.plugin.version` / `transforms.<alias>.plugin.version` keys). That is precisely the two-phase upgrade with per-connector rollback the team wants.
- **Why the others are wrong:** A — this was the correct answer **before** 4.1 and is exactly the limitation KIP-891 removed; the cluster here runs 4.3. C — replacing a JAR in place removes the old version, so there is no rollback path and a restart migrates all 40 connectors at once. D — `plugin.discovery` controls *how* plugins are found (`only_scan`, `hybrid_warn`, `hybrid_fail`, `service_load`), not which version a connector uses, and it never picks a version automatically.
- 🧠 **Key point / trap:** "one plugin version per Connect cluster" is a genuine fact that became obsolete in 4.1. Any question that anchors on a 4.1+ cluster and offers "run a second cluster" is testing whether you know KIP-891.
- 📎 Source: `resources/connect-cluster-rebalance-kip415-kip891.md` and `resources/connect-sink-source-connector-configs.md` (`connector.plugin.version`).

### Question 27 — Answer: **A**

- **Why correct:** SCRAM credentials are stored in cluster metadata and managed dynamically with `kafka-configs.sh --alter --add-config 'SCRAM-SHA-512=[password=…]' --entity-type users --entity-name <user>`. Adding the configuration for an existing user replaces the stored salted hash, so the rotation takes effect without touching any broker process. Existing connections keep working until they re-authenticate, which is what makes SCRAM rotation a zero-downtime operation.
- **Why the others are wrong:** B — `kafka-storage.sh format --add-scram` seeds a credential at **format time**, before the cluster exists; running it against a formatted cluster is not how you rotate a password. C — `kafka-acls.sh` manages authorization rules, not credentials, and it has no `--add-config` for passwords. D — editing a static JAAS file and rolling the brokers is the SASL/PLAIN pattern; the entire point of SCRAM is that it avoids exactly this.
- 🧠 **Key point / trap:** the dividing line is SASL/PLAIN (static file, restart to change) versus SASL/SCRAM (dynamic, stored in the cluster, changeable at runtime). That difference is why SCRAM is the recommended mechanism for credentials that must rotate.
- 📎 Source: `../../../CCDAK/study-plan/week-07/resources/kafka-security-sasl.md` and this week's `resources/connect-security-rest-and-clients.md` (per-connector SCRAM credentials).

### Question 28 — Answer: **B**

- **Why correct:** with mTLS and the default `ssl.principal.mapping.rules` (`DEFAULT`), the authenticated principal is the certificate's **entire distinguished name**, for example `User:CN=etl,OU=data,O=Acme,C=VN`. An ACL written for `User:etl` simply does not match that principal, so every request is denied even though the TLS handshake succeeded. The second client works because its DN happens to match the ACL that was written for it. The fix is either to write ACLs against the full DN or to add a mapping rule such as `RULE:^CN=(.*?),.*$/$1/,DEFAULT`.
- **Why the others are wrong:** A — an expired certificate fails the handshake with an SSL error; the client would never reach authorization. C — `ssl.endpoint.identification.algorithm` governs hostname verification during the handshake and produces `SSLHandshakeException`, not an authorization error; clearing it is also the classic unsafe "fix". D — `allow.everyone.if.no.acl.found=true` would mask the problem by allowing everything with no ACL, and it is not a prerequisite for certificate principals; here ACLs **do** exist, they just name a different principal.
- 🧠 **Key point / trap:** authentication succeeding and authorization failing is the signature of a principal-name mismatch. With mTLS, always check what the broker actually sees as the principal before blaming the ACL.
- 📎 Source: `../../../CCDAK/study-plan/week-07/resources/kafka-security-ssl.md` (principal mapping rules) and `../../../CCDAK/study-plan/week-07/resources/kafka-security-authorization-acls.md`.

---

## 🧭 Kế hoạch theo kết quả

| Điểm tổng | Đánh giá | Việc cần làm ngay |
| --- | --- | --- |
| **≥ 80%** (23+/28) | Đạt ngưỡng cá nhân cho domain CONNECT. | Review 100% câu sai và viết file phân tích trong `CCAAK/questions/`. Sang Tuần 7 (Observability + Troubleshooting) — nhớ rằng nhiều triệu chứng Connect ở tuần này sẽ quay lại trong **FULL MOCK #1** cuối Tuần 7. |
| **70–79%** (20–22/28) | Gần đạt, còn lỗ hổng cục bộ. | Xác định nhóm sai nhiều nhất (kiến trúc worker / REST & state / tasks & scaling / offset / error & DLQ / bảo mật & metric), đọc lại đúng mục đó trong [README](README.md) và **làm lại Lab 6.2 + 6.4 không nhìn hướng dẫn**. Rồi làm lại bộ câu hỏi sau 2 ngày. |
| **< 70%** (≤ 19/28) | Chưa sẵn sàng sang Tuần 7. | Đọc lại toàn bộ Buổi A, làm lại **cả 7 lab**, và học thuộc hai bảng: 3 internal topic và trạng thái → hành động. CONNECT chỉ chiếm 12% nhưng là domain **dễ ăn điểm nhất** vì câu hỏi rất cụ thể — bỏ lỡ nó là bỏ lỡ ~7 câu chắc ăn. |

> 📌 Dù điểm bao nhiêu: **mọi câu sai đều phải vào sổ câu sai** kèm *lý do sai* (thiếu kiến thức / đọc sót qualifier / dính bẫy version / hết giờ), và ôn lại theo mốc **1 ngày → 3 ngày → 7 ngày**. Câu đúng nhờ đoán may cũng tính là câu sai.
>
> 🎯 Bốn câu đáng soi kỹ nhất dù bạn làm đúng: **Q6/Q7** (`tasks.max` là trần — công thức `min()` lan truyền khắp nơi là sai), **Q10/Q11** (xoá connector không xoá offset; `STOPPED` chứ không phải `PAUSED`), **Q13/Q15** (DLQ chỉ sink, và `errors.tolerance=all` một mình là mất dữ liệu im lặng), **Q19/Q26** (hai mặc định đã đổi: override policy `None`→`All` ở 3.0, và "một version plugin mỗi cluster" hết đúng từ 4.1).
