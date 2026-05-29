# Question #209 - Topic 1

A solutions architect is designing the architecture of a new application being deployed to the AWS Cloud. The application will run on Amazon EC2 On-Demand Instances and will automatically scale across multiple Availability Zones. The EC2 instances will scale up and down frequently throughout the day. An Application Load Balancer (ALB) will handle the load distribution. The architecture needs to support distributed session data management. The company is willing to make changes to code if needed. What should the solutions architect do to ensure that the architecture supports distributed session data management?

## Options

**A.** Use Amazon ElastiCache to manage and store session data.

**B.** Use session affinity (sticky sessions) of the ALB to manage session data.

**C.** Use Session Manager from AWS Systems Manager to manage the session.

**D.** Use the GetSessionToken API operation in AWS Security Token Service (AWS STS) to manage the session.

---

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Auto-scaling EC2 across AZs, ALB, frequent scale up/down. Need distributed session management.
- **Existing Resources:** EC2, ALB.
- **Current Issue/Goal:** External session store (since instances come and go).

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `distributed session data management` | **External session store** — **ElastiCache** |
| `scale up and down frequently` | Không thể dùng sticky sessions (mất session khi instance terminated) |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Session management
- **Constraints:** Distributed, auto-scaling, willing to change code

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: A**

**Giải thích:**
- **ElastiCache** — in-memory session store, accessible từ tất cả EC2 instances.
- Session data tồn tại độc lập với EC2 instances → không mất khi scale in/out.
- Willing to change code → có thể integrate ElastiCache.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án B:**
- Sticky sessions — khi instance được terminated, session mất.

**❌ Đáp án C:**
- Session Manager (SSM) — quản lý EC2 session (SSH), không phải web app session.

**❌ Đáp án D:**
- STS GetSessionToken — temporary credentials, không phải session data.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"ElastiCache = distributed session store. Sticky sessions = lost on instance termination. SSM = EC2 sessions"*
