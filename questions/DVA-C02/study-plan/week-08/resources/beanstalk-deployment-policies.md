# Elastic Beanstalk — Deployment policies and settings

> **Nguồn (AWS official):** https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/using-features.rolling-version-deploy.html
> **Tuần:** 8 — Deployment / CI-CD / IaC · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- 5 deployment policy phải thuộc lòng: **All at once**, **Rolling**, **Rolling with additional batch**, **Immutable**, **Traffic splitting**. (Blue/Green làm thủ công bằng swap URL/CNAME — không phải 1 policy trong danh sách này.)
- **All at once** (mặc định) → có downtime ngắn, deploy tất cả cùng lúc. Rẻ & nhanh nhất, nhưng không giữ capacity.
- **Rolling** → deploy theo batch, GIẢM capacity trong lúc deploy (batch bị lấy ra khỏi service). Không tốn thêm instance.
- **Rolling with additional batch** → phóng thêm 1 batch instance mới TRƯỚC để giữ **full capacity**. Tốn thêm instance tạm thời.
- **Immutable** → phóng full bộ instance mới trong Auto Scaling group riêng; nếu fail health check thì hủy, KHÔNG đụng instance cũ. An toàn nhất nhưng tốn gấp đôi tài nguyên tạm thời.
- **Traffic splitting** → canary testing: chia % traffic sang bộ instance mới trong evaluation time; healthy thì chuyển hết, không thì rollback. YÊU CẦU **Application Load Balancer**.
- Bẫy thi capacity: Rolling (giảm capacity), Rolling+additional batch / Immutable / Traffic splitting (giữ full capacity). Immutable & Traffic splitting & managed update (instance replacement) làm MẤT EC2 burst balance.
- Namespace: `aws:elasticbeanstalk:command` với option `DeploymentPolicy` (`AllAtOnce | Rolling | RollingWithAdditionalBatch | Immutable | TrafficSplitting`), `BatchSize`, `BatchSizeType` (`Percentage | Fixed`).

---

## 📄 Nội dung (trích từ tài liệu gốc)

AWS Elastic Beanstalk provides several options for how deployments are processed, including deployment policies (*All at once*, *Rolling*, *Rolling with additional batch*, *Immutable*, and *Traffic splitting*) and options that let you configure batch size and health check behavior. By default, your environment uses **all-at-once** deployments. If you created the environment with the EB CLI and it's a scalable environment (no `--single` option), it uses **rolling** deployments.

With *rolling deployments*, Elastic Beanstalk splits the environment's EC2 instances into batches and deploys the new version to one batch at a time, leaving the rest running the old version.

To maintain full capacity during deployments, configure your environment to launch a new batch of instances before taking any out of service — a *rolling deployment with an additional batch*. When done, Elastic Beanstalk terminates the additional batch.

*Immutable deployments* perform an immutable update to launch a full set of new instances running the new version in a **separate Auto Scaling group**, alongside the instances running the old version. If the new instances don't pass health checks, Elastic Beanstalk terminates them, leaving the original instances untouched.

*Traffic-splitting deployments* let you perform **canary testing**. Elastic Beanstalk launches a full set of new instances (like an immutable deployment), then forwards a specified percentage of incoming client traffic to the new version for a specified evaluation period. If healthy, it forwards all traffic and terminates the old ones; if not (or you abort), it moves traffic back and terminates the new ones. There's never any service interruption.

**Warning:** Some policies replace all instances during the deployment/update, causing all accumulated Amazon EC2 burst balances to be lost:
- Managed platform updates with instance replacement enabled
- Immutable updates
- Deployments with immutable updates or traffic splitting enabled

If your application operates correctly at a lower health status, you can allow instances to pass health checks with a lower status (e.g. `Warning`) via the **Healthy threshold** option. To force an update regardless of health status, use the **Ignore health check** option.

When you specify a batch size for rolling updates, Elastic Beanstalk also uses that value for rolling application restarts.

## Configuring application deployments

In the environment management console, enable/configure batched deployments by editing **Updates and Deployments** on the environment's **Configuration** page.

The **Application deployments** section options:
- **Deployment policy** — choose from:
  - **All at once** – Deploy the new version to all instances simultaneously. All instances are out of service for a short time.
  - **Rolling** – Deploy in batches. Each batch is taken out of service during the deployment phase, reducing capacity by the number of instances in a batch.
  - **Rolling with additional batch** – Deploy in batches, but first launch a new batch to ensure full capacity.
  - **Immutable** – Deploy to a fresh group of instances by performing an immutable update.
  - **Traffic splitting** – Deploy to a fresh group of instances and temporarily split incoming client traffic between the existing and new versions.

For **Rolling** and **Rolling with additional batch** you can configure:
- **Batch size** – Choose **Percentage** (up to 100%) or **Fixed** (up to max instance count).

For **Traffic splitting** you can configure:
- **Traffic split** – Initial percentage of incoming client traffic shifted to the new version.
- **Traffic splitting evaluation time** – Time (minutes) Elastic Beanstalk waits after an initial healthy deployment before shifting all traffic.

The **Deployment preferences** section (health checks):
- **Ignore health check** – Prevents a deployment from rolling back when a batch fails to become healthy within the **Command timeout**.
- **Healthy threshold** – Lowers the threshold at which an instance is considered healthy.
- **Command timeout** – Seconds to wait for an instance to become healthy before canceling (or, if Ignore health check is set, continuing to the next batch).

## How rolling deployments work

When processing a batch, Elastic Beanstalk detaches all instances in the batch from the load balancer, deploys the new version, and reattaches them. With connection draining enabled, existing connections are drained first.

After reattaching, Elastic Load Balancing waits until instances pass the **Healthy check count threshold** before routing traffic. If a health check URL is configured, the load balancer waits for a `200 OK` from an `HTTP GET` to the health check URL.

Elastic Beanstalk waits until all instances in a batch are healthy before moving to the next batch. With **enhanced health reporting**, all instances must pass **12 consecutive health checks within two minutes** for web server environments, and **18 health checks within three minutes** for worker environments.

If a batch does not become healthy within the command timeout, the deployment fails. To roll back, perform another deployment with a known good version. If a deployment fails after some batches completed, completed batches run the new version while pending batches run the old.

## How traffic-splitting deployments work

Traffic-splitting deployments allow canary testing. Elastic Beanstalk creates a new set of instances in a **separate temporary Auto Scaling group**, directs a certain percentage of traffic to them, and tracks their health for a configured time. If healthy, it shifts remaining traffic and attaches them to the original Auto Scaling group, replacing the old instances, then terminates the old ones and removes the temporary group.

**Note:** The environment's capacity doesn't change during a traffic-splitting deployment. Elastic Beanstalk launches the same number of instances in the temporary group as in the original.

Rolling back is quick and doesn't impact service. **Traffic-splitting deployments require an Application Load Balancer** (Elastic Beanstalk uses this type by default when creating environments via console or EB CLI). You can abort a deployment via the console or the `AbortEnvironmentUpdate` API.

## Deployment option namespaces

Use configuration options in the `aws:elasticbeanstalk:command` namespace. For traffic splitting, additional options are in the `aws:elasticbeanstalk:trafficsplitting` namespace.

`DeploymentPolicy` supported values:
- `AllAtOnce` – Always deploys to all instances simultaneously.
- `Rolling` – Standard rolling deployments.
- `RollingWithAdditionalBatch` – Launches an extra batch before starting, to maintain full capacity.
- `Immutable` – Performs an immutable update for every deployment.
- `TrafficSplitting` – Performs traffic-splitting (canary) deployments.

**Example .ebextensions/rolling-updates.config**
```yaml
option_settings:
  aws:elasticbeanstalk:command:
    DeploymentPolicy: Rolling
    BatchSizeType: Percentage
    BatchSize: 25
```

**Example .ebextensions/rolling-additionalbatch.config**
```yaml
option_settings:
  aws:elasticbeanstalk:command:
    DeploymentPolicy: RollingWithAdditionalBatch
    BatchSizeType: Fixed
    BatchSize: 5
```

**Example .ebextensions/immutable-ignorehealth.config**
```yaml
option_settings:
  aws:elasticbeanstalk:command:
    DeploymentPolicy: Immutable
    HealthCheckSuccessThreshold: Warning
    IgnoreHealthCheck: true
    Timeout: "900"
```

**Example .ebextensions/traffic-splitting.config**
```yaml
option_settings:
  aws:elasticbeanstalk:command:
    DeploymentPolicy: TrafficSplitting
  aws:elasticbeanstalk:trafficsplitting:
    NewVersionPercent: "15"
    EvaluationTime: "10"
```
