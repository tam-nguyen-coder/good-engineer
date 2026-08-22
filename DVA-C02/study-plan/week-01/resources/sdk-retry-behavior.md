# Retry behavior (AWS SDKs and Tools)

> **Nguồn (AWS official):** https://docs.aws.amazon.com/sdkref/latest/guide/feature-retry-behavior.html
> **Tuần:** 1 — SDK/CLI + `Lambda` cơ bản · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- **3 retry mode:** `standard` (mặc định, khuyến nghị) · `adaptive` (`standard` + client-side rate limiter, có thể trì hoãn cả request đầu tiên) · `legacy` (chỉ để tương thích ngược).
- **`adaptive`** hợp cho client nhắm **1 resource duy nhất** và bị throttle nhiều; KHÔNG nên dùng khi client gọi nhiều resource/nhiều tenant (rate limiter làm chậm cả request không liên quan). Không phải default.
- **Max attempts mặc định = 3** (1 request đầu + 2 retry). Đặt = 1 để tắt retry hoàn toàn. **`DynamoDB`/DynamoDB Streams default = 4** (base backoff 25 ms thay vì 50 ms).
- **Precedence cấu hình:** code > env var (`AWS_RETRY_MODE`, `AWS_MAX_ATTEMPTS`) > shared config file (`retry_mode`, `max_attempts`) > SDK default.
- **Phân loại lỗi:** *transient* (retry, base delay **50 ms**) · *throttling* (retry, base delay **1000 ms**) · *non-retryable* (`ValidationException`, `AccessDeniedException`, `ResourceNotFoundException` → trả về ngay). Khớp theo **error code trước**, rồi mới đến HTTP status.
- **Backoff formula:** `delay = random(0,1) × min(20000 ms, base_delay × 2^retry)` — **exponential backoff with full jitter**, cap tối đa **20 giây**.
- **Full jitter** = nhân ngẫu nhiên để tránh **thundering herd** (nhiều client cùng retry đúng 1 thời điểm) → rải đều request.
- **Retry quota (token bucket):** capacity **500 tokens**; mỗi transient retry tốn **14 tokens**, mỗi throttling retry tốn **5 tokens**; hết token → fail-fast (không retry nữa). Success không cần retry hoàn lại 1 token.
- Header **`x-amz-retry-after`** (server-directed): SDK dùng delay của server, clamp trong [computed backoff, computed backoff + 5000 ms]; hiệu lực tối đa ~25 giây; không áp jitter thêm.
- ⚠️ Hành vi 2026 mới cần opt-in bằng `AWS_NEW_RETRIES_2026=true`; chưa set thì SDK dùng behavior pre-2026 (khác về backoff timing, quota cost, service defaults).

---

## 📄 Nội dung (trích từ tài liệu gốc)

> **Important:** The behavior described on this page requires opting in until it becomes the default behavior. Set `AWS_NEW_RETRIES_2026=true` in your environment. Without this setting, your SDK uses pre-2026 retry behavior, which differs in backoff timing, retry quota costs, and service-specific defaults.

When a request to an AWS service fails due to a transient error or throttling, the SDK can automatically retry the request.

## Configuring retries

### Choosing a retry mode

Three modes are available: **standard**, **adaptive**, and **legacy**.

|  | Standard | Adaptive | Legacy |
| --- | --- | --- | --- |
| Retry quota | Yes | Yes | Varies by SDK |
| Can delay initial request | No | Yes | No |
| Error-type-specific backoff | Yes | Yes | Varies by SDK |
| Standardized across SDKs | Yes | Yes | No |
| Recommendation | Default for all workloads | Single-resource, throttling-heavy, latency-tolerant | Backward compatibility only |

**Standard mode (default):** retries failed requests using exponential backoff with jitter. Shorter delays for transient errors, longer delays for throttling errors. Includes a **retry quota** (token bucket): deducts tokens per retry, replenishes on success; when tokens are exhausted, the SDK returns the error without retrying (fail fast). The retry quota never delays or blocks the initial request. Use standard mode unless you have a specific reason to choose another mode.

**Adaptive mode:** everything in standard mode plus a **client-side rate limiter** that tracks throttling responses and adjusts the send rate. Unlike standard mode, adaptive mode **can delay or block the initial request**, not just retries. The rate limiter operates per SDK client instance (all requests from a client share the same rate limit).
- *When to use:* client targets a single resource (e.g., one DynamoDB table) and you expect frequent throttling; you want the SDK to auto slow down.
- *When NOT to use:* client sends requests to multiple resources or serves multiple tenants (throttling on one resource slows ALL requests from that client); you need predictable initial-request latency.
- Adaptive mode is **not recommended as a general default**.

**Legacy mode:** the retry behavior each SDK used before standard mode. Does not include a standardized retry quota; behavior varies across SDKs (retry count, backoff timing, retryable error sets, throttling behavior). **Available in:** Java, Python, Ruby, PHP, C++, CLI. **Not available in:** .NET, Go, Kotlin, Rust, Swift, JavaScript. Exists only for backward compatibility — switch to standard mode.

### Retry settings

| Setting | What it controls | Environment variable | Config file key | Default |
| --- | --- | --- | --- | --- |
| Retry mode | Which retry strategy to use | `AWS_RETRY_MODE` | `retry_mode` | standard |
| Max attempts | Total attempts including the initial request | `AWS_MAX_ATTEMPTS` | `max_attempts` | 3 (see notes) |

A max attempts value of `3` means one initial request and up to two retries. Set max attempts to `1` to disable retries entirely.

> **Note:** The DynamoDB and DynamoDB Streams clients default to `4` max attempts. These services use a shorter base backoff delay (**25 ms** instead of 50 ms).

### Configuration precedence (highest → lowest)

1. **Explicit client configuration in code.**
2. **Environment variable** (e.g., `AWS_RETRY_MODE`, `AWS_MAX_ATTEMPTS`).
3. **Shared config file** (`retry_mode` / `max_attempts` in `~/.aws/config`).
4. **SDK default.**

Example: `AWS_RETRY_MODE=adaptive` (env) overrides `retry_mode=standard` (config file) → SDK uses adaptive.

## How retries work

### What happens when a request fails
1. **(Adaptive mode only)** SDK checks the client-side rate limiter; may delay/block the request.
2. SDK sends the request.
3. On success, returns the result.
4. On failure, SDK classifies the error as *transient*, *throttling*, or *non-retryable*.
5. Non-retryable → returns error immediately.
6. Retryable → checks whether max attempts reached; if so, returns error.
7. SDK checks the **retry quota (token bucket)**; if depleted, does not retry (Exception: long-polling operations still apply a backoff delay before returning).
8. SDK computes a backoff delay based on error type and attempt number.
9. SDK waits, then re-sends from step 2.

### Which errors are retried

Classification is based on the **error code** and **HTTP status code**. The SDK matches on error code first, then falls back to HTTP status code.

**Transient errors** (base delay 50 ms): `RequestTimeout`, `RequestTimeoutException`, `InternalError`, `IDPCommunicationError`, I/O Failure (Connection reset, DNS resolution failure, socket timeout), and any HTTP 500/502/503/504 without a recognized error code.

**Throttling errors** (base delay 1,000 ms): `Throttling`, `ThrottlingException`, `ThrottledException`, `RequestThrottledException`, `TooManyRequestsException`, `ProvisionedThroughputExceededException`, `TransactionInProgressException`, `LimitExceededException`, `PriorRequestNotComplete`, `RequestThrottled`, `EC2ThrottledException`, `RequestLimitExceeded`, `SlowDown`, `BandwidthLimitExceeded`.

**Non-retryable errors** (returned immediately): e.g., `AccessDeniedException`, `ValidationException`, `ResourceNotFoundException`.

> **Note:** An HTTP 5XX with a throttling error code is classified as a throttling error, not transient.

### How long does the SDK wait

Uses **exponential backoff with full jitter**.

**Base delays:** transient (non-throttling) = **50 ms** (resolves within ms → fast recovery); throttling = **1,000 ms** (service rate-limited → give time to recover).

**Backoff formula:**
```
delay = random(0, 1) × min(20,000 ms, base_delay × 2^retry)
```
- `random(0, 1)` = uniformly distributed value between 0 and 1
- `base_delay` = 50 ms (transient) or 1,000 ms (throttling)
- `retry` starts at 0 for the first retry (the second overall request attempt)
- Maximum backoff cap = **20 seconds**.

**Worked example — throttling, 3 max attempts:** Attempt 1 fails (429). Attempt 2 waits random(0, 1,000 ms) (avg ~500 ms). Attempt 3 waits random(0, 2,000 ms) (avg ~1,000 ms). Total added latency ~1,500 ms.

**Backoff cap:** With a 50 ms base, the cap takes effect at the 10th retry (11th attempt). For throttling (1,000 ms base), the cap takes effect at the 6th retry. With the default of 3 max attempts, the cap is never reached.

**Why jitter matters:** The random multiplier is *full jitter*. Without it, all clients that hit an error at the same time would retry at the same time, creating a burst (the "thundering herd" problem). Full jitter spreads retries uniformly across the backoff window.

**Server-directed retry timing:** Some services include an `x-amz-retry-after` header (delay in ms). The SDK uses the server-specified delay, clamped to [computed backoff delay, computed backoff delay + 5,000 ms]. Since the computed backoff is capped at 20 s, the effective max server-directed delay is 25 s. No jitter is applied to this value.

### Retry quota (token bucket)

The token budget starts full. Each retry deducts tokens; a successful retry restores the tokens it consumed; a first-try success restores 1 token. When the budget reaches zero, the SDK stops retrying and returns errors directly.

| Parameter | Value |
| --- | --- |
| Budget capacity | 500 tokens |
| Cost per transient (non-throttling) retry | 14 tokens |
| Cost per throttling retry | 5 tokens |
| Tokens restored on success after retry | Amount consumed by the last retry (14 or 5) |
| Tokens restored on success without retry | 1 token |

With the default of 3 max attempts, the quota begins to drain when more than ~**22%** of requests result in sustained transient failures, or more than ~**32%** for throttling errors. The 500-token starting balance absorbs short bursts. Scope: typically per single SDK client instance; not shared across processes or hosts.

## Service-specific behavior

**DynamoDB** (applies to DynamoDB and DynamoDB Streams):

| Setting | General default | DynamoDB default |
| --- | --- | --- |
| Transient (non-throttling) base delay | 50 ms | 25 ms |
| Throttling base delay | 1,000 ms | 1,000 ms |
| Max attempts | 3 | 4 |

**Long-polling operations** (`SQS.ReceiveMessage`, `SFN.GetActivityTask`, `SWF.PollForActivityTask`, `SWF.PollForDecisionTask`): when the retry quota is depleted and retries are blocked, the SDK still applies a backoff delay before returning the error (prevents a tight polling loop from spiking CPU/traffic during failures).

## Support by AWS SDKs and tools

Updated retry behavior availability (opt-in via `AWS_NEW_RETRIES_2026=true`): **Yes** — SDK for Java 2.x, Python (Boto3), .NET 4.x, Tools for PowerShell V5, JavaScript 3.x, PHP 3.x, Kotlin, Rust. **See tracking issue** — Swift, Ruby 3.x, Go V2, C++, AWS CLI v2.
