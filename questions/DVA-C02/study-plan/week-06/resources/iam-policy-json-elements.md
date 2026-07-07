# IAM — JSON policy element reference

> **Nguồn (AWS official):** https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements.html
> **Tuần:** 6 — Security I: `IAM` + `STS` + `Cognito` · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- Một policy JSON gồm các phần tử: `Version`, `Id`, `Statement`, `Sid`, `Effect`, `Principal`, `NotPrincipal`, `Action`, `NotAction`, `Resource`, `NotResource`, `Condition`.
- **`Effect`** chỉ nhận `Allow` hoặc `Deny`. **`Principal`** CHỈ dùng trong resource-based policy (và trust policy) — thấy `Principal` là resource-based.
- **Các cặp loại trừ lẫn nhau (mutually exclusive)** — không dùng chung trong một statement: `Action`/`NotAction`, `Principal`/`NotPrincipal`, `Resource`/`NotResource`. Đây là bẫy cú pháp hay hỏi.
- **Thứ tự các phần tử KHÔNG quan trọng** — `Resource` có thể đứng trước `Action`. `Condition` là tùy chọn (không bắt buộc).
- `Version` nên dùng giá trị `"2012-10-17"` (bản mới nhất hỗ trợ policy variables) — KHÔNG phải là ngày tạo policy.
- IAM có **policy validation** (bắt lỗi cú pháp JSON) và **IAM Access Analyzer** (đưa ra khuyến nghị tinh chỉnh policy).

---

## 📄 Nội dung (trích từ tài liệu gốc)

# IAM JSON policy element reference

JSON policy documents are made up of elements. The elements are listed here in the general order you use them in a policy. **The order of the elements doesn't matter** — for example, the `Resource` element can come before the `Action` element. You're not required to specify any `Condition` elements in the policy.

**Some JSON policy elements are mutually exclusive.** This means that you cannot create a policy that uses both. For example, you cannot use both `Action` and `NotAction` in the same policy statement. Other pairs that are mutually exclusive include `Principal`/`NotPrincipal` and `Resource`/`NotResource`.

The details of what goes into a policy vary for each service, depending on what actions the service makes available, what types of resources it contains, and so on. When you're writing policies for a specific service, it's helpful to see examples of policies for that service.

When you create or edit a JSON policy, IAM can perform **policy validation** to help you create an effective policy. IAM identifies JSON syntax errors, while **IAM Access Analyzer** provides additional policy checks with recommendations to help you further refine your policies.

**Topics (các phần tử — mỗi phần tử có trang chi tiết riêng):**
+ **Version** — bản ngôn ngữ policy; khuyến nghị `"2012-10-17"`.
+ **Id** — mã định danh tùy chọn cho policy.
+ **Statement** — chứa một hoặc nhiều statement (mảng).
+ **Sid** — statement ID tùy chọn (nhãn phân biệt các statement).
+ **Effect** — bắt buộc: `Allow` hoặc `Deny`.
+ **Principal** — ai được áp dụng (dùng trong resource-based policy / trust policy).
+ **NotPrincipal** — loại trừ principal (loại trừ với `Principal`).
+ **Action** — danh sách action (vd `s3:GetObject`); hỗ trợ wildcard `*`.
+ **NotAction** — mọi action TRỪ những cái liệt kê (loại trừ với `Action`).
+ **Resource** — ARN tài nguyên áp dụng.
+ **NotResource** — mọi tài nguyên TRỪ những cái liệt kê (loại trừ với `Resource`).
+ **Condition** — điều kiện (tùy chọn) để statement có hiệu lực.
+ **Variables and tags** — policy variables và tag.
+ **Supported data types** — các kiểu dữ liệu hỗ trợ trong `Condition`.
