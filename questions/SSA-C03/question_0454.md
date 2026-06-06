# Question #454 - Topic 1

A company has resources across multiple AWS Regions and accounts. A newly hired solutions architect discovers a previous employee did not provide details about the resources inventory. The solutions architect needs to build and map the relationship details of the various workloads across all accounts. Which solution will meet these requirements in the MOST operationally efficient way?

## Options

**A.** Use AWS Systems Manager Inventory to generate a map view from the detailed view report.

**B.** Use AWS Step Functions to collect workload details. Build architecture diagrams of the workloads manually.

**C.** Use Workload Discovery on AWS to generate architecture diagrams of the workloads.

**D.** Use AWS X-Ray to view the workload details. Build architecture diagrams with relationships.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Resources across multi-Region, multi-account. No documentation. Need to discover and map workloads.
- **Existing Resources:** Multiple AWS accounts/regions.
- **Current Issue/Goal:** Automatically discover resources and generate architecture diagrams.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `build and map the relationship` | Architecture diagrams showing resource relationships. |
| `most operationally efficient` | Automated tool, không manual. |
| `Workload Discovery on AWS` | AWS Solution: tự động discover resources, generate diagrams. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Operations / Discovery
- **Constraints:** Multi-account, multi-Region, automated mapping

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C**

**Giải thích:**
- Workload Discovery on AWS: AWS Solution tự động quét resources across accounts/regions.
- Generates interactive architecture diagrams với relationships.
- Most operationally efficient: chỉ cần deploy solution, không manual work.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- Systems Manager Inventory: collects OS/software inventory, không architecture mapping.

**❌ Đáp án B:**
- Step Functions: orchestration, không tự động phát hiện resources. Cần manual diagram.

**❌ Đáp án D:**
- X-Ray: application tracing, không resource discovery.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Discover resources + diagrams = Workload Discovery on AWS. NOT Systems Manager/X-Ray."*