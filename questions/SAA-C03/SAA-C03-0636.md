# Question #636 - Topic 1

A development team is creating an event-based application that uses AWS Lambda functions. Events will be generated when files are added to an Amazon S3 bucket. The development team currently has Amazon Simple Notification Service (Amazon SNS) configured as the event target from Amazon S3. What should a solutions architect do to process the events from Amazon S3 in a scalable way?

## Options

**A.** Create an SNS subscription that processes the event in Amazon Elastic Container Service (Amazon ECS) before the event runs in Lambda.

**B.** Create an SNS subscription that processes the event in Amazon Elastic Kubernetes Service (Amazon EKS) before the event runs in Lambda.

**C.** Create an SNS subscription that sends the event to Amazon Simple Queue Service (Amazon SQS). Configure the SQS queue to trigger a Lambda function.

**D.** Create an SNS subscription that sends the event to AWS Server Migration Service (AWS SMS). Configure the Lambda function to poll from the SMS event.

## 1. CONTEXT & DE BAI
- **Scenario:** Event-based app voi Lambda, S3 events => SNS (current). Can process events in a scalable way.
- **Existing Resources:** S3 bucket, SNS topic.
- **Current Issue/Goal:** Scalable event processing: them SQS giua SNS va Lambda de buffer va scale.

## 2. KEYWORDS QUAN TRONG
| Keyword | Y nghia / Goi y |
|---------|-----------------|
| `events will be generated when files are added to S3` | S3 event notification. |
| `SNS configured as the event target` | S3 => SNS hien tai. |
| `scalable way` | SQS giup buffer events, tranh throtte Lambda. |
| `SNS => SQS => Lambda` | Pattern: fan-out (SNS) + buffer (SQS) + process (Lambda). |

## 3. YEU CAU CUA DE
- **Question type:** Scalable processing
- **Constraints:** S3 events, SNS, Lambda

## 4. DAP AN DUNG
**Dap an: C**

**Giai thich:**
- SNS => SQS: tao SQS subscription tu SNS topic. SQS buffer events khi co spike.
- SQS trigger Lambda: Lambda poll tu SQS, xu ly theo toc do cua no, tu dong scale.
- Giai phap nay dam bao scalability: SQS hap thu spikes, Lambda xu ly theo kha nang.

## 5. CAC DAP AN SAI
**Dap an A va B:**
- ECS/EKS truoc Lambda: them container services khong can thiet, tang operational overhead.
- Khong giai quyet scalability issue cua Lambda.

**Dap an D:**
- AWS SMS (Server Migration Service): la service de migrate servers, khong lien quan den event processing.
- "SMS" co the nham lan voi SQS, nhung SMS la dich vu khac.

## 6. MEO GHI NHO (Memory Hook)
*"S3 => SNS => SQS => Lambda: buffer + scale. ECS/EKS truoc Lambda = unnecessary complexity."*
