# Create an alias for a Lambda function

> **Nguồn (AWS official):** https://docs.aws.amazon.com/lambda/latest/dg/configuration-aliases.html
> **Tuần:** 2 — `Lambda` nâng cao · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- `alias` = **con trỏ tới 1 function version** mà bạn có thể cập nhật (đổi trỏ sang version khác).
- Client gọi qua **alias ARN**; khi deploy version mới chỉ cần **update-alias** → client KHÔNG cần đổi ARN.
- **Weighted alias (routing config)**: chia traffic giữa **đúng 2 version** → dùng làm **canary deployment**. (Chi tiết ở trang *Implement Lambda canary deployments using a weighted alias*.)
- ⚠️ Alias **chỉ trỏ tới version**, KHÔNG trỏ tới alias khác.
- Không thể tạo alias từ **unqualified ARN** (phải có version).
- API/CLI chính: `create-alias`, `update-alias` (đổi version hoặc weighted), `delete-alias`.

---

## 📄 Nội dung (trích từ tài liệu gốc)

You can create aliases for your Lambda function. A Lambda alias is a pointer to a function version that you can update. The function's users can access the function version using the alias Amazon Resource Name (ARN). When you deploy a new version, you can update the alias to use the new version, or split traffic between two versions.

### Console

**To create an alias using the console**

1. Open the Functions page of the Lambda console.
2. Choose a function.
3. Choose **Aliases** and then choose **Create alias**.
4. On the **Create alias** page, do the following:
   1. Enter a **Name** for the alias.
   2. (Optional) Enter a **Description** for the alias.
   3. For **Version**, choose a function version that you want the alias to point to.
   4. (Optional) To configure routing on the alias, expand **Weighted alias**. For more information, see *Implement Lambda canary deployments using a weighted alias*.
   5. Choose **Save**.

### AWS CLI

To create an alias, use the `create-alias` command.

```
aws lambda create-alias \
  --function-name my-function \
  --name alias-name \
  --function-version version-number \
  --description " "
```

To change an alias to point a new version of the function, use the `update-alias` command.

```
aws lambda update-alias \
  --function-name my-function \
  --name alias-name \
  --function-version version-number
```

To delete an alias, use the `delete-alias` command.

```
aws lambda delete-alias \
  --function-name my-function \
  --name alias-name
```

The AWS CLI commands correspond to the following Lambda API operations:
- `CreateAlias`
- `UpdateAlias`
- `DeleteAlias`
