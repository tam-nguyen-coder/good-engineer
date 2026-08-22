# 📂 Tài nguyên Tuần 1 — SDK/CLI + Lambda cơ bản

> Crawl từ tài liệu AWS chính thức. Về [file học Tuần 1](../README.md) · [Kế hoạch tổng](../../../DVA-C02-STUDY-PLAN.md)

| # | Tài nguyên (file local) | Chủ đề | Nguồn AWS |
|---|---|---|---|
| 1 | [cli-config-credentials-files.md](cli-config-credentials-files.md) | AWS CLI: file `config` vs `credentials`, named profiles, precedence, output/region, retry settings | https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html |
| 2 | [sdk-credential-provider-chain.md](sdk-credential-provider-chain.md) | Credential provider chain: thứ tự tìm creds, code > env > file, các provider chuẩn hoá (IMDS/Container/SSO/AssumeRole/Process) | https://docs.aws.amazon.com/sdkref/latest/guide/standardized-credentials.html |
| 3 | [sdk-retry-behavior.md](sdk-retry-behavior.md) | Retry modes (`standard`/`adaptive`/`legacy`), exponential backoff + full jitter, retry quota, max_attempts, phân loại lỗi | https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html |
| 4 | [lambda-programming-model.md](lambda-programming-model.md) | Programming model: handler/event/context, init code reuse, `/tmp`, logging → CloudWatch, stateless & scale | https://docs.aws.amazon.com/lambda/latest/dg/foundation-progmodel.html |
| 5 | [lambda-execution-role.md](lambda-execution-role.md) | Execution role, trust policy `lambda.amazonaws.com`, `AWSLambdaBasicExecutionRole`, tạo role bằng CLI, least privilege | https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html |
| 6 | [lambda-faqs.md](lambda-faqs.md) | FAQ: memory 128–10240 MB, timeout 15 phút, runtimes, concurrency/throttle, retry async, DLQ, SnapStart vs PC | https://aws.amazon.com/lambda/faqs/ |

## Gợi ý thứ tự đọc
1. **cli-config-credentials-files.md** — nắm chắc 2 file `~/.aws/config` + `~/.aws/credentials`, cách đặt named profile và precedence khi cùng lúc có nhiều nguồn setting.
2. **sdk-credential-provider-chain.md** — hiểu chuỗi tìm credentials (code > env > file > role); nối liền với phần precedence vừa học ở CLI.
3. **sdk-retry-behavior.md** — retry mode, backoff + jitter, retry quota; đây là chỗ DVA hay bẫy về throttling/idempotency.
4. **lambda-programming-model.md** — hiểu handler/event/context và vòng đời execution environment (init reuse, `/tmp`, logging).
5. **lambda-execution-role.md** — phân biệt execution role (function gọi service khác) với resource-based policy; tự tạo role bằng CLI.
6. **lambda-faqs.md** — chốt các con số phải nhớ (memory, timeout, concurrency, retry async, DLQ) và các khái niệm SnapStart / Provisioned Concurrency.
