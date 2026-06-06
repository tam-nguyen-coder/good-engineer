# Question #630 - Topic 1

A solutions architect is creating a data processing job that runs once daily and can take up to 2 hours to complete. If the job is interrupted, it has to restart from the beginning. How should the solutions architect address this issue in the MOST cost-effective manner?

## Options

**A.** Create a script that runs locally on an Amazon EC2 Reserved Instance that is triggered by a cron job.

**B.** Create an AWS Lambda function triggered by an Amazon EventBridge scheduled event.

**C.** Use an Amazon Elastic Container Service (Amazon ECS) Fargate task triggered by an Amazon EventBridge scheduled event.

**D.** Use an Amazon Elastic Container Service (Amazon ECS) task running on Amazon EC2 triggered by an Amazon EventBridge scheduled event.

## 1. CONTEXT & DE BAI
- **Scenario:** Data processing job chay 1 lan/ngay, toi da 2 gio. Neu bi interrupt, phai restart tu dau.
- **Existing Resources:** None.
- **Current Issue/Goal:** Chon serverless/cost-effective compute cho scheduled job 2 gio.

## 2. KEYWORDS QUAN TRONG
| Keyword | Y nghia / Goi y |
|---------|-----------------|
| `once daily, up to 2 hours` | Batch job, chay ngan, schedule co dinh. |
| `restart from the beginning` | Job khong co checkpoint, can execution lien tuc. |
| `most cost-effective` | Chi chay 2h/ngay, khong muon tra tien cho idle resources. |
| `Fargate` | Serverless compute cho containers, pay per second. |
| `EC2 Reserved Instance` | Phai tra tien 24/7 du chi chay 2h/ngay, khong cost-effective. |

## 3. YEU CAU CUA DE
- **Question type:** Most cost-effective
- **Constraints:** Daily job, up to 2 hours, no checkpoint

## 4. DAP AN DUNG
**Dap an: C**

**Giai thich:**
- ECS Fargate: serverless, chi tra tien cho thoi gian task chay (per second).
- EventBridge scheduled event trigger task hang ngay, tu dong hoa.
- Pay-per-use: 2 gio/ngay x 30 ngay, cost rat thap so voi EC2 instance chay 24/7.
- Thich hop cho batch job 2 gio voi chi phi toi uu nhat.

## 5. CAC DAP AN SAI
**Dap an A:**
- EC2 Reserved Instance: phai tra tien cho 1-3 nam, instance chay 24/7. Cho job 2h/ngay, rat lang phi.

**Dap an B:**
- AWS Lambda: max execution time 15 phut, khong the chay job 2 gio.

**Dap an D:**
- ECS on EC2: can EC2 instances chay 24/7, khong cost-effective bang Fargate cho job ngan.

## 6. MEO GHI NHO (Memory Hook)
*"Daily 2h job => ECS Fargate (pay per second). Lambda = 15 min max. EC2 RI = 24/7 cost."*
