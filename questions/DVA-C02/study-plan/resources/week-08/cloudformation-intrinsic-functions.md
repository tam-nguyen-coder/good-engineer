# CloudFormation intrinsic function reference

> **Nguồn (AWS official):** https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference.html
> **Tuần:** 8 — Deployment / CI-CD / IaC · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- Intrinsic function chỉ dùng được ở **một số phần nhất định** của template: resource properties, outputs, metadata attributes, update policy attributes, và để tạo resource có điều kiện. KHÔNG dùng được trong `Parameters` mặc định.
- **`Ref`** vs **`Fn::GetAtt`** (bẫy thi kinh điển): `Ref` trả về giá trị mặc định (thường là physical ID, hoặc value của parameter); `Fn::GetAtt` trả về một **attribute cụ thể** của resource (vd ARN, DNSName).
- YAML short form vs full form: `!Ref`, `!GetAtt`, `!Sub`, `!Join`, `!FindInMap`, `!Select`, `!Split`, `!Base64`, `!ImportValue`, `!GetAZs`, `!Cidr`, `!If`, `!Equals`, `!And`, `!Or`, `!Not`. KHÔNG được lồng 2 short-form functions trực tiếp.
- **`Fn::Sub`** = chèn biến vào chuỗi (`${VarName}`), thay cho `Fn::Join` phức tạp. **`Fn::Join`** ghép list thành chuỗi với delimiter.
- **`Fn::ImportValue`** = import output đã `Export` từ stack khác (cross-stack reference). Nhớ cặp `Export`/`Fn::ImportValue`.
- **`Fn::GetAZs`** trả list AZ của Region; thường kết hợp `Fn::Select` để chọn 1 AZ. `Fn::FindInMap` tra cứu giá trị trong `Mappings` (vd AMI theo Region).
- **`Fn::Base64`** thường dùng cho EC2 `UserData`. **Condition functions** (`Fn::If`, `Fn::Equals`, `Fn::And`, `Fn::Or`, `Fn::Not`) dùng trong section `Conditions` để tạo resource có điều kiện.

---

## 📄 Nội dung (trích từ tài liệu gốc)

CloudFormation provides several built-in functions that help you manage your stacks. Use intrinsic functions in your templates to assign values to properties that are not available until runtime.

**Note:** You can use intrinsic functions only in specific parts of a template. Currently, you can use intrinsic functions in **resource properties, outputs, metadata attributes, and update policy attributes**. You can also use intrinsic functions to conditionally create stack resources.

### Danh sách intrinsic functions (Topics)

- **`Fn::Base64`** — Returns the Base64 representation of an input string (commonly used to pass encoded data such as EC2 `UserData`).
- **`Fn::Cidr`** — Returns an array of CIDR address blocks (given an IP block, count, and CIDR bits).
- **Condition functions** — `Fn::If`, `Fn::Equals`, `Fn::And`, `Fn::Or`, `Fn::Not` (used in the `Conditions` section to conditionally create resources or set property values).
- **`Fn::FindInMap`** — Returns the value corresponding to keys in a two-level map declared in the `Mappings` section (e.g. AMI ID per Region).
- **`Fn::ForEach`** — Iterates over a collection to replicate template configuration (language extensions transform).
- **`Fn::GetAtt`** — Returns the value of an attribute from a resource in the template (e.g. an ARN, DNS name, endpoint address).
- **`Fn::GetAZs`** — Returns an array that lists Availability Zones for a specified Region (in alphabetical order).
- **`Fn::GetStackOutput`** — Returns the value of an output exported by another stack (retrieves a stack output).
- **`Fn::ImportValue`** — Returns the value of an output exported by another stack (cross-stack reference; pairs with `Export`).
- **`Fn::Join`** — Appends a set of values into a single value, separated by the specified delimiter.
- **`Fn::Length`** — Returns the number of elements within an array or an intrinsic function that returns an array.
- **`Fn::Select`** — Returns a single object from a list of objects by index.
- **`Fn::Split`** — Splits a string into a list of string values by a specified delimiter (the reverse of `Fn::Join`).
- **`Fn::Sub`** — Substitutes variables in an input string with values that you specify (e.g. `${VariableName}`).
- **`Fn::ToJsonString`** — Converts an object or array into its corresponding JSON string.
- **`Fn::Transform`** — Specifies a macro to perform custom processing on part of a template.
- **`Ref`** — Returns the value of the specified parameter or resource (for a resource, typically its physical ID; for a parameter, its value).
- **Rule functions** — Functions used within the `Rules` section (e.g. for template rules / service catalog).

### Ghi chú cú pháp (JSON vs YAML)

Mỗi function có 2 dạng viết trong YAML: full function name và short form.

| Function | Full form (YAML) | Short form (YAML) |
| --- | --- | --- |
| Ref | `Ref: logicalName` | `!Ref logicalName` |
| Fn::GetAtt | `Fn::GetAtt: [logicalName, attr]` | `!GetAtt logicalName.attr` |
| Fn::Sub | `Fn::Sub: string` | `!Sub string` |
| Fn::Join | `Fn::Join: [delimiter, [values]]` | `!Join [delimiter, [values]]` |
| Fn::FindInMap | `Fn::FindInMap: [MapName, TopKey, SecondKey]` | `!FindInMap [MapName, TopKey, SecondKey]` |
| Fn::Select | `Fn::Select: [index, list]` | `!Select [index, list]` |
| Fn::Split | `Fn::Split: [delimiter, string]` | `!Split [delimiter, string]` |
| Fn::Base64 | `Fn::Base64: value` | `!Base64 value` |
| Fn::GetAZs | `Fn::GetAZs: region` | `!GetAZs region` |
| Fn::ImportValue | `Fn::ImportValue: sharedValueToImport` | `!ImportValue sharedValueToImport` |
| Fn::Cidr | `Fn::Cidr: [ipBlock, count, cidrBits]` | `!Cidr [ipBlock, count, cidrBits]` |
| Fn::If | `Fn::If: [condition, valueIfTrue, valueIfFalse]` | `!If [condition, valueIfTrue, valueIfFalse]` |
| Fn::Equals | `Fn::Equals: [value1, value2]` | `!Equals [value1, value2]` |
| Fn::And / Or / Not | `Fn::And: [...]` | `!And [...]` |

**Lưu ý:** Trong YAML, bạn KHÔNG thể lồng hai short-form intrinsic functions trực tiếp trong nhau (vd `!Sub ! GetAtt ...`) — phải dùng full form cho function bên trong.
