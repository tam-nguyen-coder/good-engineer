# Question #637 - Topic 1

A solutions architect is designing a new service behind Amazon API Gateway. The request patterns for the service will be unpredictable and can change suddenly from 0 requests to over 500 per second. The total size of the data that needs to be persisted in a backend database is currently less than 1 GB with unpredictable future growth. Data can be queried using simple key-value requests. Which combination of AWS services would meet these requirements? (Choose two.)

## Options

**A.** AWS Fargate

**B.** AWS Lambda

**C.** Amazon DynamoDB

**D.** Amazon EC2 Auto Scaling

**E.** MySQL-compatible Amazon Aurora

## 1. CONTEXT & DE BAI
- **Scenario:** API Gateway backend, unpredictable traffic (0 to 500+ req/s), < 1 GB data, key-value queries, unpredictable future growth.
- **Existing Resources:** Amazon API Gateway.
- **Current Issue/Goal:** Serverless backend cho API Gateway, key-value database.

## 2. KEYWORDS QUAN TRONG
| Keyword | Y nghia / Goi y |
|---------|-----------------|
| `unpredictable... 0 to over 500 per second` | Traffic spike lon => can serverless compute (Lambda) + serverless DB (DynamoDB). |
| `less than 1 GB`, `unpredictable future growth` | DynamoDB pay-per-use, scale vo han. |
| `simple key-value requests` | DynamoDB (NoSQL key-value) la lua chon toi uu. |
| `Lambda` | Serverless compute, scale tu 0 den hang ngan requests. |

## 3. YEU CAU CUA DE
- **Question type:** Meet requirements (Choose 2)
- **Constraints:** API Gateway, unpredictable traffic, key-value, < 1 GB

## 4. DAP AN DUNG
**Dap an: B va C**

**Giai thich:**
- **B - AWS Lambda:** Serverless, tu dong scale tu 0 len 500+ req/s khong can provision truoc, chi tra tien khi chay.
- **C - Amazon DynamoDB:** Serverless key-value database, on-demand capacity, scale vo han, phu hop cho < 1 GB du lieu voi growth khong xac dinh.

## 5. CAC DAP AN SAI
**Dap an A:**
- AWS Fargate: serverless container, nhung can provision task definition, co startup latency (cold start dai hon Lambda). Khong scale nhanh bang Lambda tu 0.

**Dap an D:**
- EC2 Auto Scaling: can provision instance truoc, co startup time, operational overhead cao hon Lambda.

**Dap an E:**
- Aurora MySQL: relational database, khong phai key-value. Can provision capacity, co schema co dinh.

## 6. MEO GHI NHO (Memory Hook)
*"API Gateway + unpredictable + key-value => Lambda (compute) + DynamoDB (DB). Serverless combo."*
