# Question #347 - Topic 1

A company has an application that is running on Amazon EC2 instances. A solutions architect has standardized the company on a particular instance family and various instance sizes based on the current needs of the company. The company wants to maximize cost savings for the application over the next 3 years. The company needs to be able to change the instance family and sizes in the next 6 months based on application popularity and usage. Which solution will meet these requirements MOST cost-effectively?

## Options

**A.** Compute Savings Plan

**B.** EC2 Instance Savings Plan

**C.** Zonal Reserved Instances

**D.** Standard Reserved Instances

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** EC2 instances, need max cost savings over 3 years, but need flexibility to change instance family/size in 6 months.
- **Existing Resources:** EC2 instances (various sizes, one family).
- **Current Issue/Goal:** Max cost savings + flexibility to change instance family.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `maximize cost savings` | 3-year term gives highest discount. |
| `change the instance family` | Compute Savings Plan: flexible across instance family, Region, OS, size. |
| `EC2 Instance Savings Plan` | Locked to instance family trong 1 Region. |
| `Reserved Instances` | Locked to instance family + size (Standard) hoặc size flexibility trong family. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective
- **Constraints:** 3-year term, ability to change instance family in 6 months

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- Compute Savings Plan: commitment to compute spend ($/hour), flexible across instance family, size, Region, OS, tenancy.
- 3-year term với Compute Savings Plan gives highest discount (~66%).
- Có thể thay đổi instance family sau 6 months mà không mất discount.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- EC2 Instance Savings Plan: locked to specific instance family → không thể đổi family sau 6 months.

**❌ Đáp án C:**
- Zonal Reserved Instances: locked to instance family + AZ → least flexible.

**❌ Đáp án D:**
- Standard Reserved Instances: locked to instance family (+ size flexibility trong family) → không thể đổi instance family.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Need to change instance family → Compute Savings Plan (flexible). Instance Savings Plan / RI = locked to family."*
