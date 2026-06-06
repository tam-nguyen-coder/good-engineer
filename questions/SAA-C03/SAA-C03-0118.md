# Question #118 - Topic 1

A company is building a web-based application running on Amazon EC2 instances in multiple Availability Zones. The web application will provide access to a repository of text documents totaling about 900 TB in size. The company anticipates that the web application will experience periods of high demand. A solutions architect must ensure that the storage component for the text documents can scale to meet the demand of the application at all times. The company is concerned about the overall cost of the solution. Which storage solution meets these requirements MOST cost-effectively?

## Options

**A.** Amazon Elastic Block Store (Amazon EBS)

**B.** Amazon Elastic File System (Amazon EFS)

**C.** Amazon OpenSearch Service (Amazon Elasticsearch Service)

**D.** Amazon S3

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Web app EC2 multi-AZ, 900TB text documents, needs to scale, cost-effective.
- **Existing Resources:** EC2 instances.
- **Current Issue/Goal:** Storage cho 900TB documents, scalable, cost-effective.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `900 TB` | Rất lớn — cần storage vô hạn |
| `scale to meet the demand` | Auto-scaling storage |
| `cost-effectively` | Chi phí thấp nhất cho dung lượng lớn |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Storage + Cost optimization
- **Constraints:** 900TB, scalable, cost-effective

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- **S3** — object storage, scale virtually unlimited, pay per GB.
- 900TB trên S3 rẻ hơn nhiều so với EBS/EFS.
- EC2 multi-AZ có thể access S3 qua endpoint.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- **EBS** — max 16TB/volume, phải provision trước, không auto-scale, đắt cho 900TB.

**❌ Đáp án B:**
- **EFS** — scalable nhưng đắt hơn S3 cho dung lượng lớn (EFS có phí throughput).

**❌ Đáp án C:**
- **OpenSearch** — không phải storage solution, là search/analytics engine.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"S3 = cheapest for large datasets. EBS = max 16TB/volume. EFS = expensive for 900TB"*
