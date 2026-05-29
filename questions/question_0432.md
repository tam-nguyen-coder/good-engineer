# Question #432 - Topic 1

An ecommerce company wants to use machine learning (ML) algorithms to build and train models. The company will use the models to visualize complex scenarios and to detect trends in customer data. The architecture team wants to integrate its ML models with a reporting platform to analyze the augmented data and use the data directly in its business intelligence dashboards. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Use AWS Glue to create an ML transform to build and train models. Use Amazon OpenSearch Service to visualize the data.

**B.** Use Amazon SageMaker to build and train models. Use Amazon QuickSight to visualize the data.

**C.** Use a pre-built ML Amazon Machine Image (AMI) from the AWS Marketplace to build and train models. Use Amazon OpenSearch Service to visualize the data.

**D.** Use Amazon QuickSight to build and train models by using calculated fields. Use Amazon QuickSight to visualize the data.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Ecommerce, ML models to detect trends, visualize complex scenarios. Integrate with reporting platform + BI dashboards.
- **Existing Resources:** Customer data.
- **Current Issue/Goal:** ML + BI integration. Least ops overhead.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `ML algorithms to build and train models` | SageMaker: managed ML platform. |
| `visualize complex scenarios` | QuickSight: BI dashboards. |
| `least operational overhead` | Fully managed services. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Least operational overhead / ML
- **Constraints:** Build/train ML models, BI dashboards

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- Amazon SageMaker: managed ML service (build, train, deploy). Notebooks, built-in algorithms, auto-tuning.
- Amazon QuickSight: serverless BI service, dashboards, ML insights.
- Both fully managed → least operational overhead.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- AWS Glue ML: focused on ETL + data prep, không phải ML model training. OpenSearch: search/analytics, không phải BI dashboard.

**❌ Đáp án C:**
- Pre-built ML AMI: tự quản training infrastructure → overhead cao.

**❌ Đáp án D:**
- QuickSight: BI tool, không phải ML training platform. Calculated fields không dùng để train models.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"ML → SageMaker. BI dashboards → QuickSight. Least overhead = fully managed."*