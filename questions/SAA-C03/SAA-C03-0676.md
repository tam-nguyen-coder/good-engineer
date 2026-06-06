# Question #676 - Topic 1

A company's application uses Network Load Balancers, Auto Scaling groups, Amazon EC2 instances, and databases that are deployed in an Amazon VPC. The company wants to capture information about traffic to and from the network interfaces in near real time in its Amazon VPC. The company wants to send the information to Amazon OpenSearch Service for analysis. Which solution will meet these requirements?

## Options

**A.** Create a log group in Amazon CloudWatch Logs. Configure VPC Flow Logs to send the log data to the log group. Use Amazon Kinesis Data Streams to stream the logs from the log group to OpenSearch Service.

**B.** Create a log group in Amazon CloudWatch Logs. Configure VPC Flow Logs to send the log data to the log group. Use Amazon Kinesis Data Firehose to stream the logs from the log group to OpenSearch Service.

**C.** Create a trail in AWS CloudTrail. Configure VPC Flow Logs to send the log data to the trail. Use Amazon Kinesis Data Streams to stream the logs from the trail to OpenSearch Service.

**D.** Create a trail in AWS CloudTrail. Configure VPC Flow Logs to send the log data to the trail. Use Amazon Kinesis Data Firehose to stream the logs from the trail to OpenSearch Service.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Capture VPC traffic info (Flow Logs) near real-time, send to OpenSearch Service for analysis.
- **Existing Resources:** VPC, NLB, ASG, EC2, databases.
- **Current Issue/Goal:** VPC Flow Logs to OpenSearch Service.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Y nghia / Goi y |
|---------|-----------------|
| `VPC Flow Logs` | Capture network interface traffic info. |
| `near real time` | Streaming pipeline. |
| `CloudWatch Logs` | Destination for VPC Flow Logs. |
| `Kinesis Data Firehose` | Streaming data to OpenSearch Service (built-in destination). |
| `Kinesis Data Streams` | Can consumer custom de dua vao OpenSearch. |

## 3. YEU CAU CUA DE
- **Question type:** Meet requirements
- **Constraints:** Near real-time, send to OpenSearch

## 4. DAP AN DUNG
**Dap an: B**

**Giai thich:**
- VPC Flow Logs to CloudWatch Logs (log group).
- CloudWatch Logs subscription filter to Kinesis Data Firehose.
- Firehose co built-in destination cho OpenSearch Service, direct delivery.
- Near real-time, khong can consumer code.

## 5. CAC DAP AN SAI
**Dap an A:**
- Kinesis Data Streams can consumer (Lambda, EC2, etc.) de doc va gui toi OpenSearch, operational overhead cao hon.

**Dap an C:**
- CloudTrail trail khong phai destination cho VPC Flow Logs. Flow Logs chi gui ve CloudWatch Logs hoac S3.

**Dap an D:**
- CloudTrail khong phai destination cho Flow Logs.

## 6. MEO GHI NHO (Memory Hook)
*"VPC Flow Logs to CloudWatch Logs, Firehose to OpenSearch = managed pipeline."*
