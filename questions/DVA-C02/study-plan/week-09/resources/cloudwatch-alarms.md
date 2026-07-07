# Using Amazon CloudWatch Alarms (metric / composite / log alarms, states, actions)

> **Nguồn (AWS official):** https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html
> **Tuần:** 9 — Observability & Optimization · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- **3 trạng thái alarm:** `OK` / `ALARM` / `INSUFFICIENT_DATA`. Trên dashboard: xám = `INSUFFICIENT_DATA`, đỏ = `ALARM`, không màu = `OK`.
- **Metric alarm:** theo dõi **1 metric** hoặc kết quả **math expression**. Action: gửi **`SNS`**, **EC2 action**, **EC2 Auto Scaling action**, mở investigation, hoặc tạo OpsItem/incident trong Systems Manager.
- **Composite alarm:** gộp trạng thái nhiều alarm bằng **rule expression (AND/OR)** → giảm nhiễu (alarm noise). Chỉ vào `ALARM` khi thoả rule. **Composite gửi được `SNS` nhưng KHÔNG làm được EC2 action / Auto Scaling action.**
- **Alarm chỉ kích action khi ĐỔI trạng thái** (state change). Ngoại lệ: **Auto Scaling action** lặp lại **mỗi phút** khi alarm vẫn ở trạng thái mới.
- **Không giới hạn số alarm** trong 1 account. Tạo/sửa bằng `PutMetricAlarm` / `put-metric-alarm`.
- **Alarm history giữ 30 ngày.** Test alarm bằng `SetAlarmState` / `set-alarm-state` (chỉ tạm thời tới lần so sánh kế tiếp).
- **Evaluation period quota:** tối đa **7 ngày** với alarm period ≥ 1 giờ (3600s); tối đa **1 ngày** với alarm period ngắn hơn (và với alarm dùng custom Lambda data source).
- **`INSUFFICIENT_DATA`** hay xuất hiện khi resource không gửi metric (vd EBS volume chưa attach) — không nhất thiết là lỗi; cấu hình cách xử lý missing data.
- Có thể tạo alarm cho **custom metric TRƯỚC khi metric đó tồn tại** (phải khai đủ namespace + metric name + tất cả dimension).

---

## 📄 Nội dung (trích từ tài liệu gốc)

# Using Amazon CloudWatch alarms

You can create alarms that watch metrics and send notifications or automatically make changes to the resources you are monitoring when a threshold is breached. For example, you can monitor the CPU usage and disk reads and writes of your Amazon EC2 instances and then use that data to determine whether you should launch additional instances to handle increased load. You can also use this data to stop under-used instances to save money.

You can create both *metric* and *composite* alarms in Amazon CloudWatch.

You can create alarms on Metrics Insights queries that use AWS resource tags to filter and group metrics.

+ A **metric alarm** watches a single CloudWatch metric or the result of a math expression based on CloudWatch metrics. The alarm performs one or more actions based on the value of the metric or expression relative to a threshold over a number of time periods. The action can be sending a notification to an Amazon SNS topic, performing an Amazon EC2 action or an Amazon EC2 Auto Scaling action, starting an investigation in CloudWatch investigations, or creating an OpsItem or incident in Systems Manager.
+ A **PromQL alarm** monitors metrics using a Prometheus Query Language (PromQL) instant query on metrics ingested through the CloudWatch OTLP endpoint. The alarm tracks individual breaching time series as contributors and uses duration-based pending and recovery periods to control state transitions.
+ A **log alarm** monitors the results of a CloudWatch Logs Insights query that runs on a schedule. The alarm evaluates aggregated query results against a threshold using M-out-of-N evaluation on recent query executions. Use log alarms to detect patterns, errors, or threshold breaches directly in your log data without creating metric filters.
+ A **composite alarm** includes a rule expression that takes into account the alarm states of other alarms that you have created. The composite alarm goes into ALARM state only if all conditions of the rule are met. The alarms specified in a composite alarm's rule expression can include metric alarms and other composite alarms.

  Using composite alarms can reduce alarm noise. You can create multiple metric alarms, and also create a composite alarm and set up alerts only for the composite alarm. For example, a composite might go into ALARM state only when all of the underlying metric alarms are in ALARM state.

  Composite alarms can send Amazon SNS notifications when they change state, and can create investigations, Systems Manager OpsItems, or incidents when they go into ALARM state, but **can't perform EC2 actions or Auto Scaling actions**.

**Note:** You can create as many alarms as you want in your AWS account.

You can add alarms to dashboards, so you can monitor and receive alerts about your AWS resources and applications across multiple regions. After you add an alarm to a dashboard, the alarm turns gray when it's in the `INSUFFICIENT_DATA` state and red when it's in the `ALARM` state. The alarm is shown with no color when it's in the `OK` state.

An alarm invokes actions only when the alarm changes state. The exception is for alarms with Auto Scaling actions. For Auto Scaling actions, the alarm continues to invoke the action once per minute that the alarm remains in the new state.

An alarm can watch a metric in the same account. If you have enabled cross-account functionality, you can also create alarms that watch metrics in other AWS accounts. Creating cross-account composite alarms is not supported. Creating cross-account alarms that use math expressions is supported, except that the `ANOMALY_DETECTION_BAND`, `INSIGHT_RULE`, and `SERVICE_QUOTA` functions are not supported for cross-account alarms.

**Note:** CloudWatch doesn't test or validate the actions that you specify, nor does it detect any Amazon EC2 Auto Scaling or Amazon SNS errors resulting from an attempt to invoke nonexistent actions. Make sure that your alarm actions exist.

## Common features of CloudWatch alarms

The following features apply to all CloudWatch alarms:
+ There is no limit to the number of alarms that you can create. To create or update an alarm, you use the CloudWatch console, the `PutMetricAlarm` or `PutLogAlarm` API actions, or the corresponding commands in the AWS CLI.
+ Alarm names must contain only UTF-8 characters, and can't contain ASCII control characters.
+ You can list any or all of the currently configured alarms, and list any alarms in a particular state by using the console, the `DescribeAlarms` API action, or the `describe-alarms` command in the AWS CLI.
+ You can disable and enable alarm actions by using the `DisableAlarmActions` and `EnableAlarmActions` API actions, or the `disable-alarm-actions` and `enable-alarm-actions` commands in the AWS CLI.
+ You can test an alarm by setting it to any state using the `SetAlarmState` API action or the `set-alarm-state` command in the AWS CLI. This temporary state change lasts only until the next alarm comparison occurs.
+ You can create an alarm for a custom metric before you've created that custom metric. For the alarm to be valid, you must include all of the dimensions for the custom metric in addition to the metric namespace and metric name in the alarm definition.
+ You can view an alarm's history using the console, the `DescribeAlarmHistory` API action, or the `describe-alarm-history` command in the AWS CLI. **CloudWatch preserves alarm history for 30 days.** Each state transition is marked with a unique timestamp.
+ Alarms have an evaluation period quota. The evaluation period is calculated by multiplying the alarm period by the number of evaluation periods used.
  + The maximum evaluation period is seven days for alarms with a period of at least one hour (3600 seconds).
  + The maximum evaluation period is one day for alarms with a shorter period.
  + The maximum evaluation period is one day for alarms that use the custom Lambda data source.

**Note:** Some AWS resources don't send metric data to CloudWatch under certain conditions. For example, Amazon EBS might not send metric data for an available volume that is not attached to an Amazon EC2 instance, because there is no metric activity to be monitored for that volume. If you have an alarm set for such a metric, you might notice its state change to `INSUFFICIENT_DATA`. This might indicate that your resource is inactive, and might not necessarily mean that there is a problem. You can specify how each alarm treats missing data.
