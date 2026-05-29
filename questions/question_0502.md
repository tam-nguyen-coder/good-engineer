# Question #502 - Topic 1

A company runs a website that uses a content management system (CMS) on Amazon EC2. The CMS runs on a single EC2 instance and uses an Amazon Aurora MySQL Multi-AZ DB instance for the data tier. Website images are stored on an Amazon Elastic Block Store (Amazon EBS) volume that is mounted inside the EC2 instance. Which combination of actions should a solutions architect take to improve the performance and resilience of the website? (Choose two.)

## Options

**A.** Move the website images into an Amazon S3 bucket that is mounted on every EC2 instance

**B.** Share the website images by using an NFS share from the primary EC2 instance. Mount this share on the other EC2 instances.

**C.** Move the website images onto an Amazon Elastic File System (Amazon EFS) file system that is mounted on every EC2 instance.

**D.** Create an Amazon Machine Image (AMI) from the existing EC2 instance. Use the AMI to provision new instances behind an Application Load Balancer as part of an Auto Scaling group. Configure the Auto Scaling group to maintain a minimum of two instances. Configure an accelerator in AWS Global Accelerator for the website

**E.** Create an Amazon Machine Image (AMI) from the existing EC2 instance. Use the AMI to provision new instances behind an Application Load Balancer as part of an Auto Scaling group. Configure the Auto Scaling group to maintain a minimum of two instances. Configure an Amazon CloudFront distribution for the website.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Website CMS trên 1 EC2 instance, database Aurora MySQL Multi-AZ, images lưu trên EBS volume gắn vào instance đó.
- **Existing Resources:** 1 EC2 instance, Aurora MySQL Multi-AZ, EBS volume chứa images.
- **Current Issue/Goal:** Improve performance (tốc độ) và resilience (khả năng chịu lỗi). Single point of failure ở EC2 và EBS.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `single EC2 instance` | Single point of failure → cần multi-instance + ALB. |
| `images stored on EBS volume` | EBS chỉ gắn được vào 1 EC2 instance trong 1 AZ → không shared được. |
| `improve performance and resilience` | Cần giải pháp cho cả shared storage và HA compute. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Improve performance and resilience (choose 2)
- **Constraints:** Shared image storage, multi-instance HA

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: C và E**

**Giải thích:**
- **C - EFS:** EFS là managed NFS file system, có thể gắn đồng thời vào nhiều EC2 instance (cross-AZ). Thay thế EBS để images được shared giữa các instances → giải quyết single point of failure ở storage.
- **E - AMI + ALB + ASG + CloudFront:** Tạo AMI từ instance hiện tại → dùng trong ASG với tối thiểu 2 instances, đứng sau ALB → HA cho compute tier. CloudFront cache images và static content → improve performance (giảm tải cho EC2, giảm latency).
- Cả 2 kết hợp: shared EFS + multi-instance ASG + CloudFront → performance và resilience đều được cải thiện.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- S3 bucket không thể "mount" như file system kiểu POSIX. S3 dùng object storage, không hỗ trợ mounting qua FUSE mà không có third-party tool.

**❌ Đáp án B:**
- NFS share từ primary EC2 tạo single point of failure mới (primary instance die → mất images). Không resilient.

**❌ Đáp án D:**
- Global Accelerator giúp tối ưu global traffic (anycast IP), không cache content. Với images, CloudFront (E) có cache → performance tốt hơn. Dùng GA cho use case global latency, không phải để improve performance của image serving.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"EBS = single instance. EFS = multi-instance shared. ALB + ASG = HA compute. CloudFront = cache + performance."*
