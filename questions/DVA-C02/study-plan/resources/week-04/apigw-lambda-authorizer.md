# Use API Gateway Lambda authorizers

> **Nguồn (AWS official):** https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-use-lambda-authorizer.html
> **Tuần:** 4 — `API Gateway` + `S3` (góc Developer) · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- `Lambda authorizer` (tên cũ: *custom authorizer*): nhận **identity của caller** làm input và trả về một **IAM policy** làm output. Dùng cho scheme tuỳ biến (OAuth, SAML, kiểm token…).
- Hai loại: **`TOKEN` authorizer** (nhận **1 bearer token** ở header, vd `Authorization` chứa JWT/OAuth token) và **`REQUEST` authorizer** (nhận **tổ hợp** headers, query string, `stageVariables`, `$context`).
- ⚠️ AWS **khuyến nghị dùng `REQUEST`** vì kiểm soát được **nhiều identity source** (fine-grained policy) so với `TOKEN` chỉ 1 nguồn; và tách cache key theo nhiều nguồn.
- Hàm authorizer **bắt buộc** trả về **IAM policy + principal identifier**; nếu không trả sẽ **fail**. Có thể trả thêm object **`context`** (String/Number/Boolean) để đẩy dữ liệu xuống backend.
- **Authorization caching**: bật để cache policy → không gọi lại hàm authorizer. `TOKEN`: **cache key = tên header** ở token source. `REQUEST`: cache key ghép từ **tất cả identity source** (theo thứ tự); nếu thiếu/null/empty một nguồn → trả **`401 Unauthorized`** mà KHÔNG gọi hàm.
- Kết quả: Allow → gọi method; Deny → trả HTTP phù hợp (**`403 ACCESS_DENIED`**); token `unauthorized`/rỗng → **`401 UNAUTHORIZED`**. Có thể tuỳ biến gateway responses 401/403.
- `TOKEN` hỗ trợ **`IdentityValidationExpression`** (RegEx) để validate token trước khi gọi hàm → giảm số lần gọi. Thuộc tính này **chỉ có ở `TOKEN`**.
- Ngoài môi trường test, khi Deny thì API Gateway trả **`403 Forbidden`**.

---

## 📄 Nội dung (trích từ tài liệu gốc)

# Use API Gateway Lambda authorizers

Use a *Lambda authorizer* (formerly known as a *custom authorizer*) to control access to your API. When a client makes a request to your API's method, API Gateway calls your Lambda authorizer. The Lambda authorizer takes the caller's identity as the input and returns an IAM policy as the output.

Use a Lambda authorizer to implement a custom authorization scheme. Your scheme can use request parameters to determine the caller's identity or use a bearer token authentication strategy such as OAuth or SAML. Create a Lambda authorizer in the API Gateway REST API console, using the AWS CLI, or an AWS SDK.

## Lambda authorizer authorization workflow

1. The client calls a method on an API Gateway API, passing a bearer token or request parameters.
2. API Gateway checks if the method request is configured with a Lambda authorizer. If it is, API Gateway calls the Lambda function.
3. The Lambda function authenticates the caller. The function can authenticate in the following ways:
   - By calling out to an OAuth provider to get an OAuth access token.
   - By calling out to a SAML provider to get a SAML assertion.
   - By generating an IAM policy based on the request parameter values.
   - By retrieving credentials from a database.
4. The Lambda function returns an IAM policy and a principal identifier. If the Lambda function does not return that information, the call fails.
5. API Gateway evaluates the IAM policy.
   - If access is denied, API Gateway returns a suitable HTTP status code, such as `403 ACCESS_DENIED`.
   - If access is allowed, API Gateway invokes the method. If you enable authorization caching, API Gateway caches the policy so that the Lambda authorizer function isn't invoked again. Ensure that your policy is applicable to all resources and methods across your API.

You can customize the `403 ACCESS_DENIED` or the `401 UNAUTHORIZED` gateway responses.

## Choosing a type of Lambda authorizer

**Request parameter-based Lambda authorizer (`REQUEST` authorizer)**
A `REQUEST` authorizer receives the caller's identity in a combination of headers, query string parameters, `stageVariables`, and `$context` variables. You can use a `REQUEST` authorizer to create fine-grained policies based on the information from multiple identity sources, such as the `$context.path` and `$context.httpMethod` context variables.
If you turn on authorization caching for a `REQUEST` authorizer, API Gateway verifies that all specified identity sources are present in the request. If a specified identity source is missing, null, or empty, API Gateway returns a `401 Unauthorized` HTTP response without calling the Lambda authorizer function. When multiple identity sources are defined, they are all used to derive the authorizer's cache key, with the order preserved. You can define a fine-grained cache key by using multiple identity sources.
If you change any of the cache key parts, and redeploy your API, the authorizer discards the cached policy document and generates a new one.
If you turn off authorization caching for a `REQUEST` authorizer, API Gateway directly passes the request to the Lambda function.

**Token-based Lambda authorizer (`TOKEN` authorizer)**
A `TOKEN` authorizer receives the caller's identity in a bearer token, such as a JSON Web Token (JWT) or an OAuth token.
If you turn on authorization caching for a `TOKEN` authorizer, the header name specified in the token source becomes the cache key.
Additionally, you can use token validation to enter a RegEx statement. API Gateway performs initial validation of the input token against this expression and invokes the Lambda authorizer function upon successful validation. This helps reduce calls to your API.
The `IdentityValidationExpression` property is supported for `TOKEN` authorizers only.

**Note**
We recommend that you use a `REQUEST` authorizer to control access to your API. You can control access to your API based on multiple identity sources when using a `REQUEST` authorizer, compared to a single identity source when using a `TOKEN` authorizer. In addition, you can separate cache keys using multiple identity sources for a `REQUEST` authorizer.

## Example `REQUEST` authorizer Lambda function (Node.js)

The following example allows a request if the client-supplied `HeaderAuth1` header, `QueryString1` query parameter, and stage variable `StageVar1` all match `headerValue1`, `queryValue1`, and `stageValue1` respectively.

```javascript
export const handler = function(event, context, callback) {
    console.log('Received event:', JSON.stringify(event, null, 2));

    var headers = event.headers;
    var queryStringParameters = event.queryStringParameters;
    var pathParameters = event.pathParameters;
    var stageVariables = event.stageVariables;

    var tmp = event.methodArn.split(':');
    var apiGatewayArnTmp = tmp[5].split('/');
    var awsAccountId = tmp[4];
    var region = tmp[3];
    var restApiId = apiGatewayArnTmp[0];
    var stage = apiGatewayArnTmp[1];
    var method = apiGatewayArnTmp[2];
    var resource = '/'; // root resource
    if (apiGatewayArnTmp[3]) {
        resource += apiGatewayArnTmp[3];
    }

    if (headers.HeaderAuth1 === "headerValue1"
        && queryStringParameters.QueryString1 === "queryValue1"
        && stageVariables.StageVar1 === "stageValue1") {
        callback(null, generateAllow('me', event.methodArn));
    }  else {
        callback(null, generateDeny('me', event.methodArn));
    }
}

var generatePolicy = function(principalId, effect, resource) {
    var authResponse = {};
    authResponse.principalId = principalId;
    if (effect && resource) {
        var policyDocument = {};
        policyDocument.Version = '2012-10-17'; // default version
        policyDocument.Statement = [];
        var statementOne = {};
        statementOne.Action = 'execute-api:Invoke'; // default action
        statementOne.Effect = effect;
        statementOne.Resource = resource;
        policyDocument.Statement[0] = statementOne;
        authResponse.policyDocument = policyDocument;
    }
    authResponse.context = {
        "stringKey": "stringval",
        "numberKey": 123,
        "booleanKey": true
    };
    return authResponse;
}

var generateAllow = function(principalId, resource) {
    return generatePolicy(principalId, 'Allow', resource);
}

var generateDeny = function(principalId, resource) {
    return generatePolicy(principalId, 'Deny', resource);
}
```

- If all required parameter values match, the authorizer returns a `200 OK` HTTP response and an `Allow` IAM policy; the method request succeeds:

```json
{
  "Version":"2012-10-17",
  "Statement": [
    {
      "Action": "execute-api:Invoke",
      "Effect": "Allow",
      "Resource": "arn:aws:execute-api:us-east-1:123456789012:ivdtdhp7b5/ESTestInvoke-stage/GET/"
    }
  ]
}
```

- Otherwise, the authorizer function returns a `401 Unauthorized` HTTP response, and the method request fails.

In addition to returning an IAM policy, the Lambda authorizer function must also return the caller's principal identifier. Optionally, it can return a `context` object containing additional information that can be passed into the integration backend.

## Example `TOKEN` authorizer Lambda function (Node.js)

Allows a caller if the client-supplied token value is `allow`; denies if `deny`; returns `401 UNAUTHORIZED` if `unauthorized` or empty; returns `500` for any other value. Token values are **case-sensitive**.

```javascript
export const handler =  function(event, context, callback) {
    var token = event.authorizationToken;
    switch (token) {
        case 'allow':
            callback(null, generatePolicy('user', 'Allow', event.methodArn));
            break;
        case 'deny':
            callback(null, generatePolicy('user', 'Deny', event.methodArn));
            break;
        case 'unauthorized':
            callback("Unauthorized");   // Return a 401 Unauthorized response
            break;
        default:
            callback("Error: Invalid token"); // Return a 500 Invalid token response
    }
};

var generatePolicy = function(principalId, effect, resource) {
    var authResponse = {};
    authResponse.principalId = principalId;
    if (effect && resource) {
        var policyDocument = {};
        policyDocument.Version = '2012-10-17';
        policyDocument.Statement = [];
        var statementOne = {};
        statementOne.Action = 'execute-api:Invoke';
        statementOne.Effect = effect;
        statementOne.Resource = resource;
        policyDocument.Statement[0] = statementOne;
        authResponse.policyDocument = policyDocument;
    }
    authResponse.context = {
        "stringKey": "stringval",
        "numberKey": 123,
        "booleanKey": true
    };
    return authResponse;
}
```

API Gateway passes the source token in `event.authorizationToken`. Behavior:
- Token `allow` → `200 OK` + `Allow` policy → method succeeds.
- Token `deny` → `200 OK` + `Deny` policy → method fails.
  - **Note:** Outside of the test environment, API Gateway returns a `403 Forbidden` HTTP response and the method request fails.
- Token `unauthorized` or empty string → `401 Unauthorized` HTTP response, method call fails.
- Any other token → client receives `500 Invalid token`, method call fails.

## Additional examples

- Built-in `AWSLambdaBasicExecutionRole` works for authorizers that don't call other AWS services; if the function calls other services, assign an IAM execution role.
- Example blueprints: `aws-apigateway-lambda-authorizer-blueprints` (GitHub); Lambda console blueprint `api-gateway-authorizer-python`.
- You can build a Lambda authorizer that authenticates users via Amazon Cognito user pools and authorizes based on a policy store using Verified Permissions.
