# Amazon ECS task definitions

> **Nguồn (AWS official):** https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_definitions.html
> **Tuần:** 8 — Deployment / CI-CD / IaC · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- **Task definition** = "bản thiết kế" (blueprint) ứng dụng, file **JSON** mô tả 1 hoặc nhiều container. Nó KHÔNG chạy — chạy nó ra 1 **task** (instance của task definition trong cluster) hoặc 1 **service** (duy trì số task mong muốn).
- Task definition khai báo: launch type/capacity, Docker image mỗi container, **CPU & memory** (ở task-level và/hoặc container-level), OS, **network mode**, logging config, `essential` (task còn chạy hay dừng khi container thoát), command, data volumes, và **IAM role** (task role).
- Bẫy thi phân biệt 2 IAM role: **task execution role** (kéo image từ ECR, gửi log tới CloudWatch — cấp cho ECS agent) vs **task role** (quyền app trong container gọi AWS API).
- Network mode (hay hỏi): `awsvpc` (bắt buộc cho **Fargate**; mỗi task có ENI + private IP riêng), `bridge`, `host`, `none`. Fargate CHỈ dùng `awsvpc`.
- **Service** dùng service scheduler: nếu task fail/stop, tự launch task mới để duy trì desired count. Task chỉ là 1 lần chạy.
- Task definition có nhiều **revision** (version); deregister/delete theo revision. Có param riêng cho Fargate, EC2, và Managed Instances.

---

## 📄 Nội dung (trích từ tài liệu gốc)

A *task definition* is a blueprint for your application. It is a text file in JSON format that describes the parameters and one or more containers that form your application.

The following are some of the parameters that you can specify in a task definition:
- The capacity to use, which determines the infrastructure that your tasks are hosted on
- The Docker image to use with each container in your task
- How much CPU and memory to use with each task or each container within a task
- The memory and CPU requirements
- The operating system of the container that the task runs on
- The Docker networking mode to use for the containers in your task
- The logging configuration to use for your tasks
- Whether the task continues to run if the container finishes or fails
- The command that the container runs when it's started
- Any data volumes that are used with the containers in the task
- The IAM role that your tasks use

For a complete list of task definition parameters, see "Amazon ECS task definition parameters for Fargate".

After you create a task definition, you can run it as a task or a service:
- A *task* is the instantiation of a task definition within a cluster. After you create a task definition, you can specify the number of tasks to run on your cluster.
- An Amazon ECS *service* runs and maintains your desired number of tasks simultaneously in an Amazon ECS cluster. If any of your tasks fail or stop for any reason, the Amazon ECS service scheduler launches another instance based on your task definition to replace it, thereby maintaining your desired number of tasks in the service.

**Topics**
- Amazon ECS task definition states
- Architect your application for Amazon ECS
- Creating an Amazon ECS task definition using the console
- Using Amazon Q Developer to provide task definition recommendations in the Amazon ECS console
- Updating an Amazon ECS task definition using the console
- Deregistering an Amazon ECS task definition revision using the console
- Deleting an Amazon ECS task definition revision using the console
- Amazon ECS task definition use cases
- Amazon ECS task definition parameters for Amazon ECS Managed Instances
- Amazon ECS task definition parameters for Fargate
- Amazon ECS task definition parameters for Amazon EC2
- Amazon ECS task definition template
- Example Amazon ECS task definitions
