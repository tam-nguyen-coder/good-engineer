# Configuration and credential file settings in the AWS CLI

> **Nguồn (AWS official):** https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html
> **Tuần:** 1 — SDK/CLI + `Lambda` cơ bản · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- `aws configure` ghi ra 2 file trong thư mục `~/.aws/`: **`credentials`** (nhạy cảm, chứa key) và **`config`** (region/output/settings). Đây là fact DVA hay hỏi.
- **Đặt tên profile khác nhau giữa 2 file:** trong `config` phải viết `[profile user1]`, còn trong `credentials` chỉ viết `[user1]` (KHÔNG có chữ `profile`). Riêng `[default]` giống nhau ở cả 2 file.
- **Trùng key ở cả 2 file cùng 1 profile → `credentials` thắng** (the keys in the credentials file take precedence).
- **Precedence chọn setting:** command-line option > environment variable > giá trị trong profile file. `--profile` ghi đè `AWS_PROFILE`.
- Đổi vị trí file mặc định qua env var `AWS_CONFIG_FILE` và `AWS_SHARED_CREDENTIALS_FILE`.
- Profile assume role dùng `role_arn` + (`source_profile` HOẶC `credential_source`) — **không được dùng cả hai** cùng lúc. Credentials tạm được cache ở `~/.aws/cli/cache`.
- `output`: `json` (mặc định hay dùng), `yaml`, `yaml-stream`, `text` (tab-separated, hợp cho `grep`/`awk`), `table` (dễ đọc), `off` (im lặng).
- `max_attempts` (số lần thử tối đa, **tính cả lần gọi đầu**) và `retry_mode` (`standard`/`legacy`/`adaptive`) đều cấu hình được trong `config`, ghi đè bằng `AWS_MAX_ATTEMPTS` / `AWS_RETRY_MODE`.
- `duration_seconds` cho role session: từ **900s (15 phút)** đến tối đa **43200s (12h)**, mặc định **3600s**.
- `credential_source` (dùng trong EC2/container): `Environment` | `Ec2InstanceMetadata` | `EcsContainer`.

---

## 📄 Nội dung (trích từ tài liệu gốc)

You can save your frequently used configuration settings and credentials in files that are maintained by the AWS CLI. The files are divided into `profiles`. By default, the AWS CLI uses the settings found in the profile named `default`. To use alternate settings, you can create and reference additional profiles.

You can override an individual setting by either setting one of the supported environment variables, or by using a command line parameter.

## Format of the configuration and credential files

The `config` and `credentials` files are organized into sections. Sections include *profiles*, *sso-sessions*, and *services*. A section is a named collection of settings, and continues until another section definition line is encountered. Multiple profiles and sections can be stored in the `config` and `credentials` files.

These files are plaintext files that use the following format:
- Section names are enclosed in brackets `[ ]` such as `[default]`, `[profile user1]`, and `[sso-session]`.
- All entries in a section take the general form of `setting_name=value`.
- Lines can be commented out by starting the line with a hash character (`#`).

The `config` and `credentials` files contain these section types: `profile`, `sso-session`, `services`.

### Section type: `profile`

Depending on the file, profile section names use the following format:
- **Config file:** `[default]` `[profile user1]`
- **Credentials file:** `[default]` `[user1]`
  - Do ***not*** use the word `profile` when creating an entry in the `credentials` file.

Each profile can specify different credentials and can also specify different AWS Regions and output formats. When naming the profile in a `config` file, include the prefix word "`profile`", but do not include it in the `credentials` file.

**Example — Short-term credentials**

Credentials file:
```
[default]
aws_access_key_id=ASIAIOSFODNN7EXAMPLE
aws_secret_access_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
aws_session_token = IQoJb3JpZ2luX2I...VERYLONGSTRINGEXAMPLE

[user1]
aws_access_key_id=ASIAI44QH8DHBEXAMPLE
aws_secret_access_key=je7MtGbClwBF/2Zp9Utk/h3yCo8nvbEXAMPLEKEY
aws_session_token = fcZib3JpZ2luX2I...VERYLONGSTRINGEXAMPLE
```

Config file:
```
[default]
region=us-west-2
output=json

[profile user1]
region=us-east-1
output=text
```

**Example — IAM role** (profile assumes a role using another profile's credentials)

Config file:
```
[default]
region=us-west-2
output=json

[profile user1]
role_arn=arn:aws:iam::777788889999:role/user1role
source_profile=default
role_session_name=session_user1
region=us-east-1
output=text
```

**Example — EC2 instance metadata credentials**

Config file:
```
[default]
role_arn=arn:aws:iam::123456789012:role/defaultrole
credential_source=Ec2InstanceMetadata
region=us-west-2
output=json
```

**Example — Long-term credentials** (Warning: AWS khuyến nghị dùng IAM Identity Center thay cho IAM user)

Credentials file:
```
[default]
aws_access_key_id=AKIAIOSFODNN7EXAMPLE
aws_secret_access_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

[user1]
aws_access_key_id=AKIAI44QH8DHBEXAMPLE
aws_secret_access_key=je7MtGbClwBF/2Zp9Utk/h3yCo8nvbEXAMPLEKEY
```

### Section type: `sso-session`

The `sso-session` section of the `config` file groups configuration variables for acquiring SSO access tokens, which can then be used to acquire AWS credentials. Settings used:
- **(Required)** `sso_start_url`
- **(Required)** `sso_region`
- `sso_account_id`
- `sso_role_name`
- `sso_registration_scopes`

`sso_region` and `sso_start_url` must be set within the `sso-session` section; `sso_account_id` and `sso_role_name` are typically set in the `profile` section. An `sso-session` can be reused across multiple profiles. The authentication token is cached to disk under the `~/.aws/sso/cache` directory with a filename based on the session name.

```
[profile dev]
sso_session = my-sso
sso_account_id = 111122223333
sso_role_name = SampleRole

[sso-session my-sso]
sso_region = us-east-1
sso_start_url = https://my-sso-portal.awsapps.com/start
sso_registration_scopes = sso:account:access
```

### Section type: `services`

The `services` section is a group of settings that configures custom endpoints for AWS service requests. A profile is linked to a `services` section. The section is separated into subsections by `<SERVICE> = ` lines (service identifier key = API model's `serviceId` with spaces replaced by underscores and lowercased), followed by nested settings indented by two spaces.

```
[profile dev]
services = my-services

[services my-services]
dynamodb =
  endpoint_url = http://localhost:8000
```

If a profile uses role-based credentials via `source_profile`, the SDK only uses service configurations for that specified profile — it does not use profiles that are role chained to it.

## Where are configuration settings stored?

The AWS CLI stores sensitive credential information (from `aws configure`) in `~/.aws/credentials`. Less sensitive configuration options go to `~/.aws/config`. Both live in the `.aws` folder in your home directory.

**Storing credentials in the config file:** You can keep all profile settings in a single file since the AWS CLI can read credentials from the `config` file. **If there are credentials in both files for a profile sharing the same name, the keys in the credentials file take precedence.** AWS suggests keeping credentials in the `credentials` file (also used by the language SDKs).

Home directory: `%UserProfile%` on Windows; `$HOME` or `~` on Unix. You can specify a non-default location by setting `AWS_CONFIG_FILE` and `AWS_SHARED_CREDENTIALS_FILE`.

When you use a shared profile that specifies an IAM role, the AWS CLI calls AWS STS `AssumeRole` to retrieve temporary credentials. These are stored in `~/.aws/cli/cache`. Subsequent commands use the cached temporary credentials until they expire, then the AWS CLI automatically refreshes them.

## Using named profiles

If no profile is explicitly defined, the `default` profile is used. To use a named profile, add `--profile profile-name`:

```
$ aws ec2 describe-instances --profile user1
```

To avoid specifying the profile in every command, set the `AWS_PROFILE` environment variable. You can override it with `--profile`.

```
# Linux or macOS
$ export AWS_PROFILE=user1

# Windows
C:\> setx AWS_PROFILE user1
```

## Set and view configuration settings using commands

- **`aws configure`** — quickly set and view credentials, Region, and output format.
  ```
  $ aws configure
  AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
  AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
  Default region name [None]: us-west-2
  Default output format [None]: json
  ```
- **`aws configure set`** — set any setting. `$ aws configure set region us-west-2 --profile integ`. To remove a setting, delete it manually in the file.
- **`aws configure get`** — retrieve a setting. `$ aws configure get region --profile integ`. Empty output = not explicitly set (uses default).
- **`aws configure import --csv file://credentials.csv`** — import CSV credentials generated from the IAM web console (not for IAM Identity Center). Required headers: `User Name`, `Access key ID`, `Secret access key`.
- **`aws configure list`** — lists profile, access key, secret key, and region, plus the value, its source location, and the config variable name.
  ```
  NAME       : VALUE                : TYPE                    : LOCATION
  profile    : <not set>            : None                    : None
  access_key : ****************ABCD : shared-credentials-file :
  secret_key : ****************ABCD : shared-credentials-file :
  region     : us-west-2            : env                     : AWS_DEFAULT_REGION
  ```
- **`aws configure list-profiles`** — list all profile names.
- **`aws configure mfa-login`** — configure a profile to use MFA with IAM user credentials. Supports only hardware/software OTP authenticators (no passkeys/U2F).
- **`aws configure sso`** / **`aws configure sso-session`** — set IAM Identity Center credentials.
- **`aws configure export-credentials`** — export currently set credentials. Default format is `process` (JSON). Formats: `process`, `env`, `env-no-export`, `powershell`, `windows-cmd`.

## Supported `config` file settings (chọn lọc, thi hay dùng)

- **`account_id_endpoint_mode`** — `preferred` (default) | `disabled` | `required`. Env: `AWS_ACCOUNT_ID_ENDPOINT_MODE`.
- **`aws_access_key_id`** / **`aws_secret_access_key`** — recommended stored in `credentials`, not `config`. Cannot be set as command line option. Env: `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`.
- **`aws_session_token`** — required only for temporary security credentials. Env: `AWS_SESSION_TOKEN`.
- **`ca_bundle`** — CA cert bundle (`.pem`). Env: `AWS_CA_BUNDLE`, option `--ca-bundle`.
- **`cli_binary_format`** — `base64` (default) or `raw-in-base64-out` (default in CLI v1). Option `--cli-binary-format`. Controls how binary/BLOB input is interpreted (`file://` vs `fileb://`).
- **`cli_timestamp_format`** — `iso8601` (default v2) or `wire` (default v1).
- **`credential_process`** — external command to generate/retrieve credentials.
- **`credential_source`** — used in EC2/containers to specify where to find credentials to assume `role_arn`. Values: `Environment` | `Ec2InstanceMetadata` | `EcsContainer`. **Cannot** be used together with `source_profile`.
- **`duration_seconds`** — max role session duration. Range **900s (15 min)** to max session setting of the role (max **43200**). Default **3600s**.
- **`endpoint_url`** — endpoint used for all service requests (or per-service in a `services` section).
- **`max_attempts`** — max retry attempts; **the initial call counts toward this value**. Env: `AWS_MAX_ATTEMPTS`.
- **`output`** — `json` | `yaml` | `yaml-stream` | `text` (tab-separated, good for `grep`/`sed`/`awk`) | `table` | `off`. Env: `AWS_DEFAULT_OUTPUT`, option `--output`.
- **`parameter_validation`** — `true` (default) or `false`.
- **`region`** — AWS Region for requests. `aws_global` = global endpoint for services like STS and S3. Override: `AWS_REGION`, `AWS_DEFAULT_REGION`, or `--region`.
- **`retry_mode`** — `standard` (default) | `legacy` | `adaptive`. Env: `AWS_RETRY_MODE`.
- **`role_arn`** — ARN of the IAM role to assume; must also specify `source_profile` OR `credential_source`. Env: `AWS_ROLE_ARN`.
- **`role_session_name`** — name attached to the role session (appears in CloudTrail). Env: `AWS_ROLE_SESSION_NAME`.
- **`source_profile`** — named profile with long-term credentials used to assume `role_arn`. **Cannot** be used together with `credential_source`.
- **`sso_account_id` / `sso_region` / `sso_registration_scopes` / `sso_role_name` / `sso_start_url`** — IAM Identity Center settings.
- **`use_dualstack_endpoint`** — enable dual-stack (IPv4+IPv6) endpoints. Default false. Mutually exclusive with `use_accelerate_endpoint`.
- **`use_fips_endpoint`** — use FIPS 140-2 endpoints where available.
- **`web_identity_token_file`** — path to OAuth 2.0 / OIDC token file; passed as `WebIdentityToken` to `AssumeRoleWithWebIdentity`. Env: `AWS_WEB_IDENTITY_TOKEN_FILE`.

### S3 Custom command settings (`s3` nested key)

```
[profile development]
s3 =
  max_concurrent_requests = 20
  max_queue_size = 10000
  multipart_threshold = 64MB
  multipart_chunksize = 16MB
  max_bandwidth = 50MB/s
  use_accelerate_endpoint = true
  addressing_style = path
```

- **`addressing_style`** — `path` | `virtual` | `auto` (default). `virtual` = bucket in hostname (`https://bucketname.s3.amazonaws.com`); `path` = bucket in URI path (`https://s3.amazonaws.com/bucketname`).
- **`use_accelerate_endpoint`** — use S3 Accelerate endpoint (`s3-accelerate.amazonaws.com`). Default false. Mutually exclusive with `use_dualstack_endpoint`. Bucket must have S3 Accelerate enabled.
- **`max_bandwidth`** — max transfer bandwidth (uploads/downloads only). Default: no limit. Suffixes: `KB/s`, `MB/s`, `GB/s`.
- **`max_concurrent_requests`** — max concurrent requests. **Default 10.**
- **`max_queue_size`** — max tasks in the task queue. **Default 1000.**
- **`multipart_chunksize`** — chunk size for multipart transfers. **Default 8 MB, minimum 5 MB.**
- **`multipart_threshold`** — size threshold above which the CLI switches to multipart operations. **Default 8 MB.** Suffixes: `KB`, `MB`, `GB`, `TB`.
