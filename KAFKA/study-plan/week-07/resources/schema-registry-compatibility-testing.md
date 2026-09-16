# Confluent Schema Registry — Compatibility testing: REST `/compatibility` & Maven plugin `test-compatibility`

> **Nguồn (official):** https://docs.confluent.io/platform/current/schema-registry/develop/api.html#compatibility · https://docs.confluent.io/platform/current/schema-registry/develop/maven-plugin.html
> **Tuần:** 7 — Security & Testing · **Loại:** Confluent Docs (Schema Registry API Reference + Schema Registry Maven Plugin, Confluent Platform 8.3.x)
> ⚠️ Nội dung dưới đây được crawl tự động (qua curl + WebFetch, có rút gọn) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)

- **Contract test schema trong CI = kiểm tra tương thích mà KHÔNG đăng ký version mới.** REST: **`POST /compatibility/subjects/<subject>/versions/latest`** (hoặc `/versions/<n>`, `-1` = latest) → `{"is_compatible": true|false}`; thêm **`?verbose=true`** để nhận `messages[]` giải thích lý do fail (mặc định `false`, không có lý do). Ngược lại `POST /subjects/<s>/versions` **mutates** (register).
- **`POST /compatibility/subjects/<subject>/versions`** (không version) = check theo đúng logic **register** sẽ dùng: với `BACKWARD`/`FORWARD`/`FULL` chỉ so **latest**; với `*_TRANSITIVE` so **mọi version** trước.
- Mức compatibility áp dụng = config của **subject** (`GET /config/<subject>`), chưa set thì dùng **global** (`GET /config`). 7 mức: `BACKWARD` (**mặc định**), `BACKWARD_TRANSITIVE`, `FORWARD`, `FORWARD_TRANSITIVE`, `FULL`, `FULL_TRANSITIVE`, `NONE`. Confluent khuyến nghị giữ BACKWARD vì cho phép **rewind consumer** về đầu topic.
- Request body: `schema` (string JSON-escaped), `schemaType` (`AVRO` mặc định / `PROTOBUF` / `JSON`), `references[]`, `metadata`, `ruleSet` (tuỳ chọn). Header `Content-Type: application/vnd.schemaregistry.v1+json` (chấp nhận cả `application/json`).
- Mã lỗi phải nhớ: **404** → `40401` subject not found, `40402` version not found; **422** → `42201` invalid schema, `42202` invalid version, `42203` invalid compatibility level (PUT /config); **500** → `50001` backend datastore. Body lỗi luôn có `error_code` + `message`.
- Đổi mức: `PUT /config/<subject>` với `{"compatibility": "FULL"}`; `PUT /config` cho global; `DELETE /config/<subject>` quay về global. Đọc `GET /config/<subject>?defaultToGlobal=true` để thấy mức hiệu lực thật.
- **Maven plugin** `io.confluent:kafka-schema-registry-maven-plugin` (version **8.3.1**, repo `https://packages.confluent.io/maven/`), 7 goal: `download`, **`test-compatibility`** (so với SR thật, dùng trong CI), **`test-local-compatibility`** (so với schema cũ trong repo, **không cần SR**, không "tốn" free schema), `register`, `validate` (chỉ syntax), `set-compatibility` (`__GLOBAL` cho global), `derive-schema` (sinh schema từ JSON mẫu).
- `test-compatibility` config: `schemaRegistryUrls` (bắt buộc), `subjects` map subject → file (bắt buộc), `schemaTypes`, `references`, `userInfoConfig` (user:pass cho Confluent Cloud), **`verbose` mặc định `true`**. `test-local-compatibility` cần `schemas`, `previousSchemaPaths` (file hoặc thư mục), `compatibilityLevels` (BACKWARD/FORWARD/FULL cần **đúng 1** previous schema).
- Quy trình CI khuyến nghị: PR → `validate` → `test-compatibility` (fail build nếu không tương thích) → merge → `register` (bước deploy). Tương ứng bash: `curl` → `jq .is_compatible` → `exit 1` khi `false`.
- Với Avro BACKWARD: **thêm field bắt buộc không default → không tương thích**; thêm field có `default` hoặc xoá field → OK. Đây là case demo Lab 7.7.

---

## 📄 Nội dung (trích từ tài liệu gốc)

### Compatibility concepts (API Reference)

The Schema Registry server can enforce certain compatibility rules when new schemas are registered in a subject. These are the compatibility types:

- **BACKWARD**: (default) consumers using the new schema can read data written by producers using the latest registered schema
- **BACKWARD_TRANSITIVE**: consumers using the new schema can read data written by producers using all previously registered schemas
- **FORWARD**: consumers using the latest registered schema can read data written by producers using the new schema
- **FORWARD_TRANSITIVE**: consumers using all previously registered schemas can read data written by producers using the new schema
- **FULL**: the new schema is forward and backward compatible with the latest registered schema
- **FULL_TRANSITIVE**: the new schema is forward and backward compatible with all previously registered schemas
- **NONE**: schema compatibility checks are disabled

We recommend keeping the default backward compatibility since it allows you to rewind consumers to the beginning of the topic.

**Content types.** The preferred format for content types is `application/vnd.schemaregistry.v1+json`, where v1 is the API version and json is the serialization format. However, other less specific content types are permitted, including `application/vnd.schemaregistry+json`, `application/json`, and `application/octet-stream`. Your requests should specify the most specific format and version information possible via the HTTP Accept header.

**Errors.** All API endpoints use a standard error message format for any requests that return an HTTP status indicating an error (any 400 or 500 statuses):

```
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/vnd.schemaregistry.v1+json
{
    "error_code": 422,
    "message": "schema may not be empty"
}
```

### Compatibility (API Reference)

The compatibility resource allows you to test schemas for compatibility against a specific version or all versions of a subject's schema.

#### Test compatibility against a particular schema subject-version

```
POST /compatibility/subjects/(string: subject)/versions/(versionId: version)
```

Test input schema against a particular version of a subject's schema for compatibility. Note that the compatibility level applied for the check is the configured compatibility level for the subject (`GET /config/(string: subject)`). If this subject's compatibility level was never changed, then the global compatibility level applies (`GET /config`).

**Path Parameters:**

- `subject` (string) – Subject of the schema version against which compatibility is to be tested
- `version` (int) – Version of the subject's schema against which compatibility is to be tested. Valid values for versionId are between [1,2^31-1] or the string `latest`, which checks compatibility of the input schema with the last registered schema under the specified subject. The value `-1` is equivalent to `latest`. Note that there may be a new latest schema that gets registered right after this request is served.

**Query Parameters:**

- `normalize` (boolean) – Add `?normalize=true` at the end of this request to normalize the schema. The default is false.
- `verbose` (boolean) – Add `?verbose=true` at the end of this request to output the reason a schema fails the compatibility test, in cases where it fails. The default is false (the reason a schema fails compatibility test is not given).

**Request JSON Object:**

- `schemaType` – Defines the schema format: AVRO (default), PROTOBUF, JSON (Optional)
- `references` – Specifies the names of referenced schemas (Optional).
- `schema` – The schema string
- `metadata` – Specifies the user-defined metadata for the schema (Optional).
- `ruleSet` – Specifies the ruleSet for the schema (Optional).

**Response JSON Object:**

- `is_compatible` (boolean) – True, if compatible, False if not compatible
- `messages` (array) – An array of error messages (strings) explaining why the schema is incompatible (only returned if verbose=true)

**Status Codes:**

- 404 Not Found – Error code 40401 – Subject not found · Error code 40402 – Version not found
- 422 Unprocessable Entity – Error code 42201 – Invalid schema · Error code 42202 – Invalid version
- 500 Internal Server Error – Error code 50001 – Error in the backend datastore

Example request:

```
POST /compatibility/subjects/test/versions/latest HTTP/1.1
Host: schemaregistry.example.com
Accept: application/vnd.schemaregistry.v1+json, application/vnd.schemaregistry+json, application/json

{
  "schema":
    "{
       \"type\": \"record\",
       \"name\": \"test\",
       \"fields\":
         [
           { \"type\": \"string\", \"name\": \"field1\" },
           { \"type\": \"int\",    \"name\": \"field2\" }
         ]
     }"
}
```

Example response:

```
HTTP/1.1 200 OK
Content-Type: application/vnd.schemaregistry.v1+json

{
  "is_compatible": true
}
```

#### Test schema compatibility against all schemas under a subject

```
POST /compatibility/subjects/(string: subject)/versions
```

Test input schema against a subject's schemas for compatibility, based on the configured compatibility level of the subject. In other words, this call will perform the same compatibility check as register for that subject. Perform a compatibility check on the schema against one or more versions in the subject, depending on how the compatibility is set. For example, if compatibility on the subject is set to BACKWARD, FORWARD, or FULL, the compatibility check is against the latest version. If compatibility is set to one of the TRANSITIVE types, the check is against all previous versions.

Status codes: 404 (40401 Subject not found), 422 (42201 Invalid schema), 500 (50001). Request/response body identical to the single-version endpoint.

```
POST /compatibility/subjects/test/versions
{
  "schema": "{\"type\": \"record\",\"name\": \"test\",\"fields\":[{\"type\": \"string\",\"name\": \"field1\"},{\"type\": \"int\",\"name\": \"field2\"}]}"
}
→ HTTP/1.1 200 OK  {"is_compatible": true}
```

### Config (API Reference — tóm lược)

- `GET /config` — global compatibility settings: `compatibilityLevel` (BACKWARD, BACKWARD_TRANSITIVE, FORWARD, FORWARD_TRANSITIVE, FULL, FULL_TRANSITIVE, NONE), `normalize`, `defaultMetadata`, `overrideMetadata`, `defaultRuleSet`, `overrideRuleSet`.
- `GET /config/(string: subject)` — subject-level config; `?defaultToGlobal=true` returns the global config when the subject has none. 404 if subject not found.
- `PUT /config/(string: subject)` / `PUT /config` — request JSON `{"compatibility": "FULL"}` (one of the 7 levels; optional `normalize`, `alias`, `compatibilityGroup`, metadata/ruleSet overrides). 422 error code **42203** – Invalid compatibility level.
- `DELETE /config/(string: subject)` / `DELETE /config` — remove the override, reverting to the global / default level.

### Schema Registry Maven Plugin

Plugin coordinates: groupId `io.confluent`, artifactId `kafka-schema-registry-maven-plugin`, version `8.3.1`.

```xml
<pluginRepositories>
    <pluginRepository>
        <id>confluent</id>
        <url>https://packages.confluent.io/maven/</url>
    </pluginRepository>
</pluginRepositories>
```

The `configs` option is available for all goals to add any valid configuration to the `CachedSchemaRegistryClient` (e.g. `schema.registry.ssl.keystore.location`, `schema.registry.basic.auth.credentials.source`). Note that the `schema.registry.` prefix is needed.

#### schema-registry:test-compatibility

This goal is used to read schemas from the local file system and test them for compatibility against the Schema Registry servers. This goal can be used in a continuous integration pipeline to ensure that schemas in the project are compatible with the schemas in another environment.

- `schemaRegistryUrls` — Schema Registry URLs to connect to. Type: String[]. Required: true
- `userInfoConfig` — User credentials for connecting to Schema Registry, of the form `user:password`. This is required if connecting to Confluent Cloud Schema Registry. Required: false. Default: null
- `subjects` — Map containing subject to schema path of the subjects to be registered. Type: Map<String, File>. Required: true
- `schemaTypes` — String that specifies the schema type. One of AVRO (default), JSON, PROTOBUF. Required: false
- `references` — Map containing a reference name and a subject. Type: Map<String, Reference[]>. Required: false
- `metadata` / `ruleSet` — Map containing a subject and a Metadata / RuleSet object. Required: false
- `verbose` — Include in the output the reason the schema fails the compatibility test, in cases where it fails. Type: Boolean. Required: false. **Default: true**

```xml
<plugin>
    <groupId>io.confluent</groupId>
    <artifactId>kafka-schema-registry-maven-plugin</artifactId>
    <version>8.3.1</version>
    <configuration>
        <schemaRegistryUrls>
            <param>http://192.168.99.100:8081</param>
        </schemaRegistryUrls>
        <subjects>
            <order>src/main/avro/order.avsc</order>
            <product>src/main/avro/product.avsc</product>
            <customer>src/main/avro/customer.avsc</customer>
        </subjects>
        <schemaTypes>
            <order>AVRO</order>
            <product>AVRO</product>
            <customer>AVRO</customer>
        </schemaTypes>
        <references>
            <order>
              <reference>
                  <name>com.acme.Product</name>
                  <subject>product</subject>
              </reference>
              <reference>
                  <name>com.acme.Customer</name>
                  <subject>customer</subject>
              </reference>
            </order>
        </references>
    </configuration>
    <goals>
        <goal>test-compatibility</goal>
    </goals>
</plugin>
```

Run with `mvn schema-registry:test-compatibility`; the build fails when any subject is incompatible.

#### schema-registry:test-local-compatibility

This goal tests compatibility of a local schema with other existing local schemas during development and testing phases. Before the addition of `schema-registry:test-local-compatibility`, if you wanted to check compatibility of a new schema you had to connect to the Schema Registry. This meant registering all the schemas for which you want to perform compatibility checks, resulting in a reduction in available free schemas. This new goal solves that problem and supports quick, efficient compatibility testing of local schemas as appropriate for development phases.

- `schemas` — Map of schema and location of schemas for which compatibility test is performed. Required: true
- `previousSchemaPaths` — Map of schema and location of previous schemas. The location can be a directory or file name. If it is a directory name, all files inside folder are added. Subdirectories are ignored. Required: true
- `compatibilityLevels` — Map of schema and the compatibility type for which check is performed (one of NONE, BACKWARD, BACKWARD_TRANSITIVE, FORWARD, FORWARD_TRANSITIVE, FULL, or FULL_TRANSITIVE). For compatibility level BACKWARD, FORWARD, or FULL, exactly one previousSchema is expected per schema. Required: true
- `schemaTypes` — Map<String, String> (one of AVRO (default), JSON, PROTOBUF). Required: false

```xml
<configuration>
    <schemas>
        <order>src/main/avro/order.avsc</order>
        <product>src/main/avro/product.avsc</product>
        <customer>src/main/avro/customer.avsc</customer>
    </schemas>
    <schemaTypes>
        <order>AVRO</order>
        <product>AVRO</product>
        <customer>AVRO</customer>
    </schemaTypes>
    <compatibilityLevels>
        <order>BACKWARD</order>
        <product>FORWARD</product>
        <customer>NONE</customer>
    </compatibilityLevels>
    <previousSchemaPaths>
        <order>src/main/avro/order.avsc</order>
        <product>src/main/avro/products/</product>
        <customer>src/main/avro/customer.avsc</customer>
    </previousSchemaPaths>
</configuration>
```

#### Other goals (tóm lược)

- `schema-registry:download` — retrieves schemas from a Schema Registry server and writes them locally (`schemaRegistryUrls`, `outputDirectory`, `subjectPatterns` regex).
- `schema-registry:register` — registers schemas to Schema Registry from local files (`subjects`, `references`, `metadata`, `ruleSet`).
- `schema-registry:validate` — validates local schema syntax before registration.
- `schema-registry:set-compatibility` — updates compatibility settings at subject or global level (`compatibilityLevels`; use `__GLOBAL` for global configuration changes).
- `schema-registry:derive-schema` — auto-generates a schema (Avro, JSON or ProtoBuf) from a file containing JSON messages (`messagePath`, `outputPath`, `schemaType`).

**Workflows and examples.** You can integrate Maven Plugin goals with GitHub Actions into a continuous integration/continuous deployment (CI/CD) pipeline to manage schemas on Schema Registry. A general example is provided in the `kafka-github-actions` demo repo, with detailed `validate` and `register` steps driven by properties `schemaRegistryUrl` and `schemaRegistryBasicAuthUserInfo`.
