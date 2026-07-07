# CodePipeline concepts

> **Nguồn (AWS official):** https://docs.aws.amazon.com/codepipeline/latest/userguide/concepts.html
> **Tuần:** 8 — Deployment / CI-CD / IaC · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- Cấu trúc phân cấp: **Pipeline → Stages → Actions**; giữa các stage là **transitions** (có thể disable/enable). Mỗi stage chứa action nối tiếp (serial) hoặc song song (parallel) qua thuộc tính `runOrder`.
- 6 loại action (category): `source`, `build`, `test`, `deploy`, `approval`, `invoke`. Nhớ để chọn đúng provider.
- **1 stage chỉ xử lý 1 execution tại 1 thời điểm** (stage bị "khóa" khi đang xử lý). Đây là bẫy thi kinh điển.
- Execution mode: **SUPERSEDED** (mặc định — execution mới đè execution cũ đang chờ), **PARALLEL**, **QUEUED**.
- Trạng thái pipeline: `InProgress`, `Stopping`, `Stopped`, `Succeeded`, `Superseded`, `Failed`. Stop có 2 kiểu: **Stop and wait** và **Stop and abandon**.
- **Artifacts** truyền giữa action qua **artifact store (S3 bucket)** — input/output artifacts. CodePipeline copy artifact vào store rồi action sau lấy ra.
- **Triggers**: khởi chạy pipeline. Khuyến nghị dùng **Amazon CloudWatch Events (EventBridge)** cho CodeCommit/S3 (thay vì polling). Webhook (WebhookV2) cho third-party (GitHub, GitLab, Bitbucket). Pipeline không hoạt động >30 ngày sẽ bị **tắt polling**.
- **Variables** giải quyết tại runtime (declare ở pipeline-level hoặc do action phát ra). **Conditions** (gates) + **Rules**: Entry / On Success / On Failure — kiểm tra alarm, deployment window trước khi vào/ra stage; có thể rollback stage.

---

## 📄 Nội dung (trích từ tài liệu gốc)

**Topics:** Pipelines · Pipeline executions · Stage operations · Action executions · Execution types · Action types · Artifacts · Source revisions · Triggers · Variables · Conditions · Rules

## Pipelines

A *pipeline* is a workflow construct that describes how software changes go through a release process. Each pipeline is made up of a series of *stages*.

### Stages
A stage is a logical unit you can use to isolate an environment and to limit the number of concurrent changes in that environment. Each stage contains actions that are performed on the application artifacts. A stage might be a build stage (source is built, tests run) or a deployment stage (code deployed to runtime environments). Each stage is made up of a series of serial or parallel *actions*.

### Transitions
A *transition* is the point where a pipeline execution moves to the next stage. You can disable a stage's inbound transition to prevent executions from entering that stage, and enable it later. When more than one execution arrives at a disabled transition, only the latest execution continues when the transition is enabled (newer executions supersede waiting ones).

### Actions
An *action* is a set of operations performed on application code, configured to run at a specified point. Valid CodePipeline action types are `source`, `build`, `test`, `deploy`, `approval`, and `invoke`. Actions can run in series or in parallel (see `runOrder` in action structure requirements).

## Pipeline executions

An *execution* is a set of changes released by a pipeline. Each pipeline execution is unique and has its own ID. While a pipeline can process multiple executions at the same time, **a pipeline stage processes only one execution at a time** — a stage is locked while it processes an execution. The execution waiting to enter an occupied stage is an *inbound execution* (which can still fail, be superseded, or be manually stopped).

Pipeline executions traverse pipeline stages in order. Valid statuses for pipelines are `InProgress`, `Stopping`, `Stopped`, `Succeeded`, `Superseded`, and `Failed`.

### Stopped executions
A pipeline execution can be stopped manually. When stopped manually, it shows `Stopping`, then `Stopped`. A `Stopped` execution can be retried. Two ways to stop:
- **Stop and wait**
- **Stop and abandon**

### Failed executions
If an execution fails, it stops and does not completely traverse the pipeline. Its status is `FAILED` and the stage is unlocked. A more recent execution can catch up and enter the unlocked stage. You can retry a failed execution unless it has been superseded or is not retryable. You can roll back a failed stage to a previous successful execution.

### Execution modes
Newer executions pass and replace less recent executions already running through the pipeline. When this occurs, the older execution is superseded by the newer one (between stages). **SUPERSEDED is the default execution mode.** In SUPERSEDED mode, if an execution is waiting to enter a locked stage, a more recent execution might catch up and supersede it (superseded execution stops with `SUPERSEDED` status and can no longer be retried). Other available execution modes are **PARALLEL** or **QUEUED** mode.

## Stage operations

When a pipeline execution runs through a stage, the stage completes all its actions. Valid statuses for stages are `InProgress`, `Stopping`, `Stopped`, `Succeeded`, and `Failed`. You can retry a failed stage unless it's not retryable, and roll back a stage to a specified previous successful execution. A stage can be configured to roll back automatically on failure.

## Action executions

An *action execution* is the process of completing a configured action that operates on designated artifacts (input, output, or both). Valid statuses for actions are `InProgress`, `Abandoned`, `Succeeded`, or `Failed`.

## Execution types

A pipeline or stage execution can be either a **standard** or a **rolled-back** execution. Standard = full pipeline run with a unique ID. A pipeline rollback has a stage to be rolled back and a successful execution for the stage as the target execution; the target execution is used to retrieve source revisions and variables for the stage to rerun.

## Action types

*Action types* are preconfigured actions available for selection in CodePipeline. An action type is defined by its owner, provider, version, and category, and provides customized parameters used to complete the action tasks.

## Artifacts

*Artifacts* refers to the collection of data (application source code, built applications, dependencies, definitions files, templates, etc.) worked on by pipeline actions. Artifacts can be *input artifacts* or *output artifacts*. Actions pass output to another action using the **pipeline artifact bucket** — CodePipeline copies artifacts to the artifact store, where the action picks them up.

## Source revisions

When you make a source code change, a new version is created. A *source revision* is the version of a source change that triggers a pipeline execution. For GitHub and CodeCommit repositories this is the commit; for S3 buckets/actions this is the object version. You can start an execution with a specified source revision, overriding the default revision.

## Triggers

*Triggers* are events that start your pipeline. Some (like starting manually) are available for all source providers. **Amazon CloudWatch Events is the recommended trigger for automatic change detection for pipelines with a CodeCommit or S3 source action.** Webhooks are a type of trigger for third-party repository events (e.g. WebhookV2 for Git tags with GitHub.com, GitHub Enterprise Server, GitLab.com, GitLab self-managed, or Bitbucket Cloud). You can filter triggers (push or pull request), on Git tags, branches, or file paths; pull request events on event (opened, updated, closed), branches, or file paths.

**Important:** Pipelines that are inactive for longer than **30 days** will have polling disabled for the pipeline (see `pollingDisabledAt`). Migrate from polling to event-based change detection.

## Variables

A *variable* is a value used to dynamically configure actions. Variables can be declared at the pipeline level or emitted by actions. Values are resolved at the time of pipeline execution and can be viewed in execution history. Pipeline-level variables can have default values or be overridden for a given execution. Action-emitted variable values are available after the action successfully completes.

## Conditions

A *condition* contains a set of rules that are evaluated. If all rules succeed, the condition is met. Conditions are also referred to as **gates** — they specify when an execution enters and runs through a stage or exits after running. Results include failing the stage or rolling back the stage. Three types:
- **Entry conditions** — "If the rules are met, then enter the stage." The stage is locked when the execution enters, then rules run.
- **On Failure conditions** — engage when a stage has failed, with a result of rolling back a failed stage.
- **On Success conditions** — engage when a stage is successful (e.g. checking for CloudWatch alarms before proceeding; roll back a successful stage if alarms found).

You can override conditions at runtime.

## Rules

Conditions use one or more preconfigured *rules* that run and perform checks (e.g. alarm status, deployment window times) that then engage the configured result when the condition is not met.
