# Invoking a Lambda function asynchronously

> **Nguồn (AWS official):** https://docs.aws.amazon.com/lambda/latest/dg/invocation-async.html
> **Tuần:** 2 — `Lambda` nâng cao · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- Async invoke: đặt `InvocationType = Event`; Lambda **xếp event vào internal queue** rồi trả **`202`** ngay, KHÔNG chờ kết quả code.
- Nhiều dịch vụ gọi Lambda async sẵn: `S3`, `SNS`, `EventBridge`, ...
- Một tiến trình riêng đọc event từ queue và gửi tới function.
- Có thể cấu hình **xử lý lỗi** và gửi **invocation records** tới downstream như `SQS` hoặc `EventBridge` (destinations) để nối chuỗi thành phần ứng dụng.
- File output (vd `response.json`) được tạo nhưng **rỗng**; nếu Lambda không thêm được event vào queue thì lỗi hiện trong output CLI.
- ⚠️ Payload async: theo trang *Lambda quotas* hiện hành ghi **1 MB** (async). (Đề cũ thường ghi 256 KB — đối chiếu bảng quotas mới nhất, xem `lambda-quotas-limits.md`.)
- ⚠️ CLI v2 cần `--cli-binary-format raw-in-base64-out`.

---

## 📄 Nội dung (trích từ tài liệu gốc)

Several AWS services, such as Amazon Simple Storage Service (Amazon S3) and Amazon Simple Notification Service (Amazon SNS), invoke functions asynchronously to process events. You can also invoke a Lambda function asynchronously using the AWS Command Line Interface (AWS CLI) or one of the AWS SDKs. When you invoke a function asynchronously, you don't wait for a response from the function code. You hand off the event to Lambda and Lambda handles the rest. You can configure how Lambda handles errors, and can send invocation records to a downstream resource such as Amazon Simple Queue Service (Amazon SQS) or Amazon EventBridge (EventBridge) to chain together components of your application.

For asynchronous invocation, Lambda places the event in a queue and returns a success response without additional information. A separate process reads events from the queue and sends them to your function.

To invoke a Lambda function asynchronously using the AWS CLI or one of the AWS SDKs, set the `InvocationType` parameter to `Event`. The following example shows an AWS CLI command to invoke a function.

```
aws lambda invoke \
  --function-name my-function  \
  --invocation-type Event \
  --cli-binary-format raw-in-base64-out \
  --payload '{ "key": "value" }' response.json
```

Output:

```
{
    "StatusCode": 202
}
```

The **cli-binary-format** option is required if you're using AWS CLI version 2. To make this the default setting, run `aws configure set cli-binary-format raw-in-base64-out`.

The output file (`response.json`) doesn't contain any information, but is still created when you run this command. If Lambda isn't able to add the event to the queue, the error message appears in the command output.
