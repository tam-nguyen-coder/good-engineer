# Tài nguyên Tuần 8 — Deployment / CI-CD / IaC

> Crawl từ tài liệu AWS chính thức. Về [file học Tuần 8](../README.md) · [Kế hoạch tổng](../../../DVA-C02-STUDY-PLAN.md)

| # | Tài nguyên (file local) | Chủ đề | Nguồn AWS |
|---|---|---|---|
| 1 | [codebuild-buildspec.md](codebuild-buildspec.md) | `CodeBuild` buildspec.yml: 4 phase, env/parameter-store/secrets-manager, artifacts, reports, cache | https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html |
| 2 | [codedeploy-appspec.md](codedeploy-appspec.md) | `CodeDeploy` AppSpec file: EC2/Lambda/ECS platform, lifecycle hooks, spacing | https://docs.aws.amazon.com/codedeploy/latest/userguide/reference-appspec-file.html |
| 3 | [codedeploy-deployment-configs.md](codedeploy-deployment-configs.md) | `CodeDeploy` deployment configs: AllAtOnce/HalfAtATime/OneAtATime, canary vs linear (Lambda & ECS) | https://docs.aws.amazon.com/codedeploy/latest/userguide/deployment-configurations.html |
| 4 | [codepipeline-concepts.md](codepipeline-concepts.md) | `CodePipeline`: pipeline/stage/action, transitions, artifacts, triggers, execution modes, conditions | https://docs.aws.amazon.com/codepipeline/latest/userguide/concepts.html |
| 5 | [cloudformation-intrinsic-functions.md](cloudformation-intrinsic-functions.md) | `CloudFormation` intrinsic functions: Ref, GetAtt, Sub, Join, ImportValue, condition functions | https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference.html |
| 6 | [sam-overview.md](sam-overview.md) | `AWS SAM`: mở rộng CloudFormation cho serverless, SAM CLI (init/build/deploy/local/sync), connectors | https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html |
| 7 | [beanstalk-deployment-policies.md](beanstalk-deployment-policies.md) | `Elastic Beanstalk`: All at once / Rolling / Rolling+batch / Immutable / Traffic splitting, capacity & burst balance | https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/using-features.rolling-version-deploy.html |
| 8 | [ecs-task-definitions.md](ecs-task-definitions.md) | `Amazon ECS` task definitions: blueprint JSON, task vs service, network mode, task role vs execution role | https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definitions.html |

## Gợi ý thứ tự đọc
1. **`ecs-task-definitions.md`** — hiểu đơn vị deploy container (task vs service, 2 IAM role) trước khi vào CI/CD.
2. **`cloudformation-intrinsic-functions.md`** — nền tảng IaC; nắm `Ref` vs `Fn::GetAtt`, `Fn::Sub`, `Fn::ImportValue`.
3. **`sam-overview.md`** — SAM là lớp mở rộng của CloudFormation cho serverless.
4. **`codebuild-buildspec.md`** — giai đoạn Build của pipeline (buildspec 4 phase).
5. **`codedeploy-appspec.md`** rồi **`codedeploy-deployment-configs.md`** — giai đoạn Deploy: AppSpec + chiến lược shift traffic (canary/linear/blue-green).
6. **`codepipeline-concepts.md`** — ghép tất cả lại thành pipeline CI/CD end-to-end.
7. **`beanstalk-deployment-policies.md`** — so sánh 5 deployment policy (câu hỏi "giữ full capacity? / zero downtime? / rẻ nhất?").

## Bẫy thi hay gặp (cross-service)
- **Canary vs Linear** (CodeDeploy Lambda/ECS): canary = 10% trước rồi 90% một lần; linear = 10% đều mỗi X phút.
- **Beanstalk capacity**: Rolling giảm capacity; Rolling+additional batch / Immutable / Traffic splitting giữ full capacity.
- **CloudFormation `Ref` vs `Fn::GetAtt`**: Ref → physical ID/param value; GetAtt → attribute cụ thể (ARN, DNSName...).
- **ECS task role vs execution role**: task role = quyền app gọi AWS API; execution role = kéo image ECR + ghi log CloudWatch.
- **CodePipeline**: 1 stage chỉ xử lý 1 execution tại 1 thời điểm (locked); SUPERSEDED là execution mode mặc định.
