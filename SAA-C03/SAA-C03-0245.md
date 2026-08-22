# Question #245 - Topic 1

A company is launching an application on AWS. The application uses an Application Load Balancer (ALB) to direct traffic to at least two Amazon EC2 instances in a single target group. The instances are in an Auto Scaling group for each environment. The company requires a development environment and a production environment. The production environment will have periods of high traffic. Which solution will configure the development environment MOST cost-effectively?

## Options

**A.** Reconfigure the target group in the development environment to have only one EC2 instance as a target.

**B.** Change the ALB balancing algorithm to least outstanding requests.

**C.** Reduce the size of the EC2 instances in both environments.

**D.** Reduce the maximum number of EC2 instances in the development environment's Auto Scaling group.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** ALB + ASG per environment (dev + prod). Production has high traffic. Configure dev cost-effectively.
- **Existing Resources:** ALB, ASG per environment.
- **Current Issue/Goal:** Reduce dev cost without affecting prod.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `MOST cost-effectively` | **Reduce max instances** in dev ASG |
| `development environment` | Không cần scale nhiều như prod |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Cost optimization
- **Constraints:** Dev cost reduction, separate from prod

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: D**

**Giải thích:**
- Reduce **max capacity** của dev ASG → hạn chế số instances tối đa.
- Dev không cần scale nhiều như prod.
- Không ảnh hưởng đến production environment.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- ALB target group cần ≥ 2 instances (theo requirement).

**❌ Đáp án B:**
- Change ALB algorithm — không giảm cost.

**❌ Đáp án C:**
- Reduce instance size in **both** — ảnh hưởng production.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Reduce max ASG size in dev = cost-effective. Reduce instance type in both = affects prod"*
