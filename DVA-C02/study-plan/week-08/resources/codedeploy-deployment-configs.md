# Working with deployment configurations in CodeDeploy

> **Nguồn (AWS official):** https://docs.aws.amazon.com/codedeploy/latest/userguide/deployment-configurations.html
> **Tuần:** 8 — Deployment / CI-CD / IaC · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- Deployment config = tập rule + điều kiện success/failure, KHÁC nhau theo compute platform (EC2/On-Premises vs Lambda vs ECS).
- **EC2/On-Premises** có 3 config dựng sẵn: `CodeDeployDefault.AllAtOnce`, `HalfAtATime`, `OneAtATime`. Mặc định nếu không chỉ định = **OneAtATime**. Chúng dựa trên **minimum healthy hosts** (số/% instance phải còn khỏe).
- **Lambda & ECS** shift traffic theo 3 kiểu: **canary**, **linear**, **all-at-once**.
- Config Lambda dựng sẵn (nhớ tên): `LambdaCanary10Percent{5,10,15,30}Minutes`, `LambdaLinear10PercentEvery{1,2,3,10}Minutes`, `LambdaAllAtOnce`.
- Config ECS dựng sẵn: `ECSLinear10PercentEvery{1,3}Minutes`, `ECSCanary10Percent{5,15}Minutes`, `ECSAllAtOnce`. Nếu dùng **Network Load Balancer** → CHỈ hỗ trợ `ECSAllAtOnce`.
- **Canary** = shift 10% trước, phần còn lại (90%) shift 1 lần sau X phút. **Linear** = shift đều 10% mỗi X phút cho tới hết. Bẫy thi hay nhầm canary vs linear.
- Có thể tạo **custom** canary/linear config cho Lambda & ECS. Nhưng CloudFormation blue/green (ECS) thì KHÔNG cho tạo custom config.
- `HalfAtATime` với nhiều Auto Scaling group: deploy tới tối đa nửa số instance BẤT KỂ ASG nào — có thể dồn hết vào 1 ASG.

---

## 📄 Nội dung (trích từ tài liệu gốc)

A deployment configuration is a set of rules and success and failure conditions used by CodeDeploy during a deployment. These rules and conditions are different, depending on whether you deploy to an EC2/On-Premises compute platform, AWS Lambda compute platform, or Amazon ECS compute platform.

## Deployment configurations on an EC2/on-premises compute platform

When you deploy to an EC2/On-Premises compute platform, the deployment configuration specifies, through the use of a 'minimum healthy hosts' value and an optional 'minimum healthy hosts per zone' value, the number or percentage of instances that must remain available at any time during a deployment.

You can use one of the three predefined deployment configurations provided by AWS or create a custom deployment configuration. If you don't specify a deployment configuration, CodeDeploy uses the **CodeDeployDefault.OneAtATime** deployment configuration.

**Note:** There are no predefined deployment configurations that support the zonal configuration feature (specifying the number of healthy hosts per Availability Zone). To use this feature, you must create your own deployment configuration.

### Predefined deployment configurations for an EC2/on-premises compute platform

| Deployment configuration | Description |
| --- | --- |
| CodeDeployDefault.AllAtOnce | **In-place:** Attempts to deploy to as many instances as possible at once. Overall status = Succeeded if deployed to one or more instances; Failed if deployed to none. Example with nine instances: deploys to all nine at once; succeeds if even one succeeds, fails only if all nine fail. |
| CodeDeployDefault.HalfAtATime | **In-place:** Deploys to up to half the instances at a time (fractions rounded down). Succeeds if deployed to at least half (fractions rounded up). Example with nine instances: up to four at a time; succeeds if five or more succeed. With multiple Auto Scaling groups, deploys to up to half of instances *regardless of the ASG they're in* (may deploy all to one ASG). |
| CodeDeployDefault.OneAtATime | **In-place:** Deploys to only one instance at a time. For groups with more than one instance: overall deployment succeeds if deployed to all but the last instance (see docs). For single-instance groups, success requires that one instance to succeed. |

## Deployment configurations on an Amazon ECS compute platform

When you deploy to an Amazon ECS compute platform, the deployment configuration specifies how traffic is shifted to the updated Amazon ECS task set. You can shift traffic using a **canary**, **linear**, or **all-at-once** deployment configuration. You can also create your own custom canary or linear deployment configuration.

**Note:** If you're using a Network Load Balancer, only the `CodeDeployDefault.ECSAllAtOnce` predefined deployment configuration is supported.

### Predefined deployment configurations for an Amazon ECS compute platform

| Deployment configuration | Description |
| --- | --- |
| CodeDeployDefault.ECSLinear10PercentEvery1Minutes | Shifts 10 percent of traffic every minute until all traffic is shifted. |
| CodeDeployDefault.ECSLinear10PercentEvery3Minutes | Shifts 10 percent of traffic every three minutes until all traffic is shifted. |
| CodeDeployDefault.ECSCanary10Percent5Minutes | Shifts 10 percent of traffic in the first increment. The remaining 90 percent is deployed five minutes later. |
| CodeDeployDefault.ECSCanary10Percent15Minutes | Shifts 10 percent of traffic in the first increment. The remaining 90 percent is deployed 15 minutes later. |
| CodeDeployDefault.ECSAllAtOnce | Shifts all traffic to the updated Amazon ECS container at once. |

## Deployment configurations for CloudFormation blue/green deployments (Amazon ECS)

When you deploy to an Amazon ECS compute platform through CloudFormation blue/green deployments, the deployment configuration specifies how traffic is shifted (canary, linear, or all-at-once). With CloudFormation blue/green deployments, you cannot create your own custom canary or linear deployment configuration.

**Note:** Managing Amazon ECS blue/green deployments with CloudFormation is not available in the Europe (Milan), Africa (Cape Town), and Asia Pacific (Osaka) regions.

## Deployment configurations on an AWS Lambda compute platform

When you deploy to an AWS Lambda compute platform, the deployment configuration specifies the way traffic is shifted to the new Lambda function versions (canary, linear, or all-at-once). You can also create your own custom canary or linear deployment configuration.

### Predefined deployment configurations for an AWS Lambda compute platform

| Deployment configuration | Description |
| --- | --- |
| CodeDeployDefault.LambdaCanary10Percent5Minutes | Shifts 10 percent of traffic in the first increment. The remaining 90 percent is deployed five minutes later. |
| CodeDeployDefault.LambdaCanary10Percent10Minutes | Shifts 10 percent of traffic in the first increment. The remaining 90 percent is deployed 10 minutes later. |
| CodeDeployDefault.LambdaCanary10Percent15Minutes | Shifts 10 percent of traffic in the first increment. The remaining 90 percent is deployed 15 minutes later. |
| CodeDeployDefault.LambdaCanary10Percent30Minutes | Shifts 10 percent of traffic in the first increment. The remaining 90 percent is deployed 30 minutes later. |
| CodeDeployDefault.LambdaLinear10PercentEvery1Minute | Shifts 10 percent of traffic every minute until all traffic is shifted. |
| CodeDeployDefault.LambdaLinear10PercentEvery2Minutes | Shifts 10 percent of traffic every two minutes until all traffic is shifted. |
| CodeDeployDefault.LambdaLinear10PercentEvery3Minutes | Shifts 10 percent of traffic every three minutes until all traffic is shifted. |
| CodeDeployDefault.LambdaLinear10PercentEvery10Minutes | Shifts 10 percent of traffic every 10 minutes until all traffic is shifted. |
| CodeDeployDefault.LambdaAllAtOnce | Shifts all traffic to the updated Lambda functions at once. |

## Topics
- Create a Deployment Configuration
- View Deployment Configuration Details
- Delete a Deployment Configuration
