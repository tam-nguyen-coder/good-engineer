# Question #42 - Topic 1

A company runs a highly available image-processing application on Amazon EC2 instances in a single VPC. The EC2 instances run inside several subnets across multiple Availability Zones. The EC2 instances do not communicate with each other. However, the EC2 instances download images from Amazon S3 and upload images to Amazon S3 through a single NAT gateway. The company is concerned about data transfer charges. What is the MOST cost-effective way for the company to avoid Regional data transfer charges?

## Options

**A.** Launch the NAT gateway in each Availability Zone.

**B.** Replace the NAT gateway with a NAT instance.

**C.** Deploy a gateway VPC endpoint for Amazon S3.

**D.** Provision an EC2 Dedicated Host to run the EC2 instances.



## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Công ty vận hành ứng dụng xử lý ảnh highly available trên các instance `Amazon EC2` trong một `VPC` duy nhất. Các instance được phân bổ trong nhiều `subnet` trải rộng qua nhiều `Availability Zones`. Các instance không giao tiếp với nhau, nhưng thường xuyên download và upload ảnh từ/tới `Amazon S3` thông qua một `NAT gateway` đơn lẻ.
- **Existing Resources:** `EC2` instances (đa AZ), `VPC`, `subnet`, single `NAT gateway`, `Amazon S3`.
- **Current Issue/Goal:** Giảm thiểu chi phí data transfer (`
