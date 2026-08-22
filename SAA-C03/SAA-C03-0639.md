# Question #639 - Topic 1

A company is building a new furniture inventory application. The company has deployed the application on a fleet of Amazon EC2 instances across multiple Availability Zones. The EC2 instances run behind an Application Load Balancer (ALB) in their VPC. A solutions architect has observed that incoming traffic seems to favor one EC2 instance, resulting in latency for some requests. What should the solutions architect do to resolve this issue?

## Options

**A.** Disable session affinity (sticky sessions) on the ALB.

**B.** Replace the ALB with a Network Load Balancer.

**C.** Increase the number of EC2 instances in each Availability Zone.

**D.** Adjust the frequency of the health checks on the ALB's target group.

## 1. CONTEXT & DE BAI
- **Scenario:** EC2 instances across multiple AZs behind ALB. Traffic favor one instance, gay latency.
- **Existing Resources:** ALB, EC2 instances, ASG.
- **Current Issue/Goal:** Traffic phan phoi khong deu giua cac instances, can fix load balancing.

## 2. KEYWORDS QUAN TRONG
| Keyword | Y nghia / Goi y |
|---------|-----------------|
| `traffic seems to favor one EC2 instance` | Phan phoi traffic khong deu. |
| `session affinity (sticky sessions)` | Khi bat sticky sessions, ALB gui requests tu cung client den cung target => mat can bang tai. |
| `ALB` | Application Load Balancer. |
| `latency for some requests` | Instances khac nhan it traffic hon, instance duoc favor bi overload. |

## 3. YEU CAU CUA DE
- **Question type:** Fix traffic distribution / Improve performance
- **Constraints:** EC2 + ALB, uneven traffic

## 4. DAP AN DUNG
**Dap an: A**

**Giai thich:**
- Session affinity (sticky sessions) lam ALB gui requests tu cung client den cung instance.
- Neu instance duoc favor khong con du capacity, requests bi delay.
- Disable sticky sessions => ALB phan phoi traffic deu hon (round-robin), can bang tai tot hon.

## 5. CAC DAP AN SAI
**Dap an B:**
- NLB cung co flow stickiness (5-tuple hash), khong giai quyet triet de van de.

**Dap an C:**
- Tang so instances co the giam overload, nhung khong giai quyet root cause (sticky sessions).

**Dap an D:**
- Health check frequency: khong lien quan den traffic distribution.

## 6. MEO GHI NHO (Memory Hook)
*"ALB traffic favor 1 instance => disable sticky sessions. Sticky = client luon ve 1 server."*
