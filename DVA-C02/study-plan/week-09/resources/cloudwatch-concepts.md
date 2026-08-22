# CloudWatch Metrics — Concepts (namespace, dimension, resolution, statistics, alarms)

> **Nguồn (AWS official):** https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/cloudwatch_concepts.html
> **Tuần:** 9 — Observability & Optimization · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- **Namespace** = container chứa metric; **không có default namespace** — phải chỉ định khi `PutMetricData`. AWS đặt tên theo mẫu `AWS/{service}` (vd `AWS/EC2`, `AWS/Lambda`). Tên ≤ **255 ký tự**.
- **Dimension** = cặp name/value; **tối đa 30 dimension** cho mỗi metric. Mỗi tổ hợp dimension duy nhất được coi là **một metric riêng** → chỉ truy vấn được đúng tổ hợp đã publish.
- **Resolution:** standard = hạt **1 phút**; high-resolution = hạt **1 giây** (custom metric). High-res đọc được ở period 1/5/10/30 giây hoặc bội số 60.
- **Metric retention (rollup tự động):** period < 60s giữ **3 giờ**; period 60s (1 phút) giữ **15 ngày**; period 300s (5 phút) giữ **63 ngày**; period 3600s (1 giờ) giữ **455 ngày (15 tháng)**. Metric tự hết hạn sau **15 tháng** nếu không có data mới.
- **Timestamp** của data point: được phép trong khoảng **2 tuần quá khứ đến 2 giờ tương lai**; nên dùng **UTC**. Timestamp lệch giờ hiện tại có thể gây alarm `INSUFFICIENT_DATA` hoặc trễ.
- **Period** hợp lệ: **1, 5, 10, 30, hoặc bội số của 60** giây; default **60s**. Chỉ metric high-res (storage resolution 1s) mới hỗ trợ period dưới 1 phút.
- **Percentiles** (vd p95): được hỗ trợ ở API Gateway, ALB, EC2, ELB, Kinesis, **Lambda**, RDS; KHÔNG dùng được nếu có giá trị âm.
- **Alarm** chỉ kích action khi **đổi trạng thái và duy trì đủ số period** (trừ Auto Scaling action lặp mỗi phút). Chọn period ≥ resolution của metric (EC2 basic = 5 phút → period ≥ 300s; detailed = 1 phút → period ≥ 60s).

---

## 📄 Nội dung (trích từ tài liệu gốc)

# Metrics concepts

The following terminology and concepts are central to your understanding and use of Amazon CloudWatch:
+ OpenTelemetry metrics
+ Namespaces
+ Metrics
+ Dimensions
+ Resolution
+ Statistics
+ Percentiles
+ Alarms

For information about the service quotas for CloudWatch metrics, alarms, API requests, and alarm email notifications, see CloudWatch service quotas.

## OpenTelemetry metrics

CloudWatch also supports metrics sent using the OpenTelemetry Protocol (OTLP). OpenTelemetry metrics use a different data model from traditional CloudWatch metrics. Instead of namespaces and dimensions, OpenTelemetry metrics use metric names with descriptive labels (key-value pairs) that follow OpenTelemetry semantic conventions. OpenTelemetry metrics support up to 150 labels per metric and support metric types including gauge, sum, histogram, and exponential histogram.

OpenTelemetry metrics are queried using the Prometheus Query Language (PromQL) in CloudWatch Query Studio or through the Prometheus-compatible query API. You can set PromQL-based CloudWatch Alarms on OpenTelemetry metrics.

The following table summarizes the key differences between OpenTelemetry metrics and traditional CloudWatch metrics.

| Concept | Traditional CloudWatch metrics | OpenTelemetry metrics |
| --- | --- | --- |
| Identity | Namespace, metric name, up to 30 dimensions | Metric name, up to 150 labels |
| Metric types | Single values, statistic sets | Gauge, sum, histogram, exponential histogram |
| Ingestion | PutMetricData API or AWS CLI | OpenTelemetry Protocol (OTLP) |
| Query language | GetMetricStatistics, Metrics Insights | Prometheus Query Language (PromQL) |
| Alarms | Standard CloudWatch Alarms | PromQL-based CloudWatch Alarms |
| Console experience | CloudWatch Metrics console | CloudWatch Query Studio |
| Retention | Up to 15 months with automatic rollup | Up to 15 months |

## Namespaces

A *namespace* is a container for CloudWatch metrics. Metrics in different namespaces are isolated from each other, so that metrics from different applications are not mistakenly aggregated into the same statistics.

There is no default namespace. You must specify a namespace for each data point you publish to CloudWatch. You can specify a namespace name when you create a metric. These names must contain valid ASCII characters, and be 255 or fewer characters. Possible characters are: alphanumeric characters (0-9A-Za-z), period (.), hyphen (-), underscore (_), forward slash (/), hash (#), colon (:), and the space character. A namespace must contain at least one non-whitespace character.

The AWS namespaces typically use the following naming convention: `AWS/{{service}}`. For example, Amazon EC2 uses the `AWS/EC2` namespace.

## Metrics

*Metrics* are the fundamental concept in CloudWatch. A metric represents a time-ordered set of data points that are published to CloudWatch. Think of a metric as a variable to monitor, and the data points as representing the values of that variable over time. For example, the CPU usage of a particular EC2 instance is one metric provided by Amazon EC2.

By default, many AWS services provide metrics at no charge for resources (such as Amazon EC2 instances, Amazon EBS volumes, and Amazon RDS DB instances). For a charge, you can also enable detailed monitoring for some resources, such as your Amazon EC2 instances, or publish your own application metrics. For custom metrics, you can add the data points in any order, and at any rate you choose.

Metrics exist only in the Region in which they are created. Metrics cannot be deleted, but they automatically expire after 15 months if no new data is published to them. Data points older than 15 months expire on a rolling basis; as new data points come in, data older than 15 months is dropped.

Metrics are uniquely defined by a name, a namespace, and zero or more dimensions. Each data point in a metric has a time stamp, and (optionally) a unit of measure.

### Time stamps

Each metric data point must be associated with a time stamp. The time stamp can be up to two weeks in the past and up to two hours into the future. If you do not provide a time stamp, CloudWatch creates a time stamp for you based on the time the data point was received.

Time stamps are `dateTime` objects, with the complete date plus hours, minutes, and seconds (for example, 2016-10-31T23:59:59Z). Although it is not required, we recommend that you use Coordinated Universal Time (UTC). When you retrieve statistics from CloudWatch, all times are in UTC.

CloudWatch alarms check metrics based on the current time in UTC. Custom metrics sent to CloudWatch with time stamps other than the current UTC time can cause alarms to display the **Insufficient Data** state or result in delayed alarms.

### Metrics retention

CloudWatch retains metric data as follows:
+ Data points with a period of less than 60 seconds are available for 3 hours. These data points are high-resolution custom metrics.
+ Data points with a period of 60 seconds (1 minute) are available for 15 days
+ Data points with a period of 300 seconds (5 minutes) are available for 63 days
+ Data points with a period of 3600 seconds (1 hour) are available for 455 days (15 months)

Data points that are initially published with a shorter period are aggregated together for long-term storage. For example, if you collect data using a period of 1 minute, the data remains available for 15 days with 1-minute resolution. After 15 days this data is still available, but is aggregated and is retrievable only with a resolution of 5 minutes. After 63 days, the data is further aggregated and is available with a resolution of 1 hour.

**Note:** Metrics that have not had any new data points in the past two weeks do not appear in the console. The best way to retrieve these metrics is with the `get-metric-data` or `get-metric-statistics` commands in the AWS CLI.

## Dimensions

A *dimension* is a name/value pair that is part of the identity of a metric. You can assign up to 30 dimensions to a metric.

Every metric has specific characteristics that describe it, and you can think of dimensions as categories for those characteristics. Because dimensions are part of the unique identifier for a metric, whenever you add a unique name/value pair to one of your metrics, you are creating a new variation of that metric.

AWS services that send data to CloudWatch attach dimensions to each metric. You can use dimensions to filter the results that CloudWatch returns. For example, you can get statistics for a specific EC2 instance by specifying the `InstanceId` dimension.

For metrics produced by certain AWS services, such as Amazon EC2, CloudWatch can aggregate data across dimensions. CloudWatch does not aggregate across dimensions for your custom metrics.

### Dimension combinations

CloudWatch treats each unique combination of dimensions as a separate metric, even if the metrics have the same metric name. You can only retrieve statistics using combinations of dimensions that you specifically published.

For example, suppose that you publish four distinct metrics named ServerStats in the DataCenterMetric namespace with the following properties:

```
Dimensions: Server=Prod, Domain=Frankfurt, Unit: Count, Timestamp: 2016-10-31T12:30:00Z, Value: 105
Dimensions: Server=Beta, Domain=Frankfurt, Unit: Count, Timestamp: 2016-10-31T12:31:00Z, Value: 115
Dimensions: Server=Prod, Domain=Rio,       Unit: Count, Timestamp: 2016-10-31T12:32:00Z, Value: 95
Dimensions: Server=Beta, Domain=Rio,       Unit: Count, Timestamp: 2016-10-31T12:33:00Z, Value: 97
```

If you publish only those four metrics, you can retrieve statistics for these combinations of dimensions:
+ `Server=Prod,Domain=Frankfurt`
+ `Server=Prod,Domain=Rio`
+ `Server=Beta,Domain=Frankfurt`
+ `Server=Beta,Domain=Rio`

You can't retrieve statistics for the following dimensions or if you specify no dimensions (exception: metric math **SEARCH** function):
+ `Server=Prod`
+ `Server=Beta`
+ `Domain=Frankfurt`
+ `Domain=Rio`

## Resolution

Each metric is one of the following:
+ Standard resolution, with data having a one-minute granularity
+ High resolution, with data at a granularity of one second

Metrics produced by AWS services are standard resolution by default. When you publish a custom metric, you can define it as either standard resolution or high resolution. When you publish a high-resolution metric, CloudWatch stores it with a resolution of 1 second, and you can read and retrieve it with a period of 1 second, 5 seconds, 10 seconds, 30 seconds, or any multiple of 60 seconds.

Keep in mind that every `PutMetricData` call for a custom metric is charged, so calling `PutMetricData` more often on a high-resolution metric can lead to higher charges.

If you set an alarm on a high-resolution metric, you can specify a high-resolution alarm with a period of 10 seconds or 30 seconds, or you can set a regular alarm with a period of any multiple of 60 seconds. There is a higher charge for high-resolution alarms with a period of 10 or 30 seconds.

## Statistics

*Statistics* are metric data aggregations over specified periods of time. Aggregations are made using the namespace, metric name, dimensions, and the data point unit of measure, within the time period you specify.

## Units

Each statistic has a unit of measure. Example units include `Bytes`, `Seconds`, `Count`, and `Percent`. If you do not specify a unit, CloudWatch uses `None` as the unit. Metric data points that specify a unit of measure are aggregated separately.

## Periods

A *period* is the length of time associated with a specific Amazon CloudWatch statistic. Periods are defined in numbers of seconds, and valid values for period are 1, 5, 10, 30, or any multiple of 60. For example, to specify a period of six minutes, use 360 as the period value. The default value of a period is 60 seconds. A period can be as short as one second, and must be a multiple of 60 if it is greater than the default value of 60 seconds.

Only custom metrics that you define with a storage resolution of 1 second support sub-minute periods.

When you retrieve statistics, you can specify a period, start time, and end time. The default values for the start time and end time get you the last hour's worth of statistics.

When statistics are aggregated over a period of time, they are stamped with the time corresponding to the beginning of the period.

Periods are also important for CloudWatch alarms. For example, if you specify three evaluation periods, CloudWatch compares a window of three data points. CloudWatch only notifies you if the oldest data point is breaching and the others are breaching or missing.

## Aggregation

Amazon CloudWatch aggregates statistics according to the period length that you specify when retrieving statistics. CloudWatch does not automatically aggregate data across Regions, but you can use metric math to aggregate metrics from different Regions.

For large datasets, you can insert a pre-aggregated dataset called a *statistic set*. With statistic sets, you give CloudWatch the Min, Max, Sum, and SampleCount for a number of data points. This is commonly used when you need to collect data many times in a minute.

Amazon CloudWatch doesn't differentiate the source of a metric. If you publish a metric with the same namespace and dimensions from different sources, CloudWatch treats this as a single metric.

## Percentiles

A *percentile* indicates the relative standing of a value in a dataset. For example, the 95th percentile means that 95 percent of the data is lower than this value and 5 percent of the data is higher than this value.

Some CloudWatch metrics support percentiles as a statistic. You can specify the percentile with up to ten decimal places (for example, p95.0123456789).

Percentile statistics are available for custom metrics as long as you publish the raw, unsummarized data points for your custom metric. Percentile statistics are not available for metrics when any of the metric values are negative numbers.

The following AWS services include metrics that support percentile statistics:
+ API Gateway
+ Application Load Balancer
+ Amazon EC2
+ Elastic Load Balancing
+ Kinesis
+ Lambda
+ Amazon RDS

## Alarms

You can use an *alarm* to automatically initiate actions on your behalf. An alarm watches a single metric over a specified time period, and performs one or more specified actions, based on the value of the metric relative to a threshold over time. The action is a notification sent to an Amazon SNS topic or an Auto Scaling policy. You can also add alarms to dashboards.

Alarms invoke actions for sustained state changes only. CloudWatch alarms do not invoke actions simply because they are in a particular state. The state must have changed and been maintained for a specified number of periods.

When creating an alarm, select an alarm monitoring period that is greater than or equal to the metrics resolution. For example, basic monitoring for Amazon EC2 provides metrics for your instances every 5 minutes. When setting an alarm on a basic monitoring metric, select a period of at least 300 seconds (5 minutes). Detailed monitoring for Amazon EC2 provides metrics for your instances with a resolution of 1 minute. When setting an alarm on a detailed monitoring metric, select a period of at least 60 seconds (1 minute).
