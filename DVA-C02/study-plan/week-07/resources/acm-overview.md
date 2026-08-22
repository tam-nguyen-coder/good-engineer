# What is AWS Certificate Manager (ACM)?

> **Nguồn (AWS official):** https://docs.aws.amazon.com/acm/latest/userguide/acm-overview.html
> **Tuần:** 7 — KMS + Secrets + Encryption · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- **`ACM` cấp, lưu, và TỰ ĐỘNG GIA HẠN (auto-renew)** chứng chỉ SSL/TLS X.509 (public & private) — bẫy đề "cert TLS hết hạn / phải tự renew" → dùng ACM, không tự mua/tự gia hạn.
- **MIỄN PHÍ cho public SSL/TLS cert** do ACM cấp và quản lý — chỉ trả tiền cho AWS resource chạy app. (Private CA qua AWS Private CA thì tính phí riêng.)
- **Cert là resource theo REGION** (regional): dùng cùng 1 FQDN ở nhiều region → phải **request/import cert riêng cho từng region**, không copy cert giữa region được.
- **BẪY CloudFront (cực hay hỏi):** cert dùng với **CloudFront BẮT BUỘC nằm ở region `us-east-1` (N. Virginia)**. Cert ở us-east-1 gắn CloudFront distribution sẽ được phân phối tới mọi edge location.
- Cert ACM tích hợp với các service AWS: **ELB/ALB, CloudFront, API Gateway** (đây là các dịch vụ integrated, được auto-renew).
- Có thể **import cert bên thứ 3** vào ACM (nhưng cert import **không** được ACM tự gia hạn — phải tự re-import trước khi hết hạn).
- Bảo vệ được: single domain, nhiều domain cụ thể, **wildcard domain** (bảo vệ vô số subdomain), hoặc kết hợp.
- Muốn dùng cert trên **EC2/web server tự quản** (standalone): dùng **ACME protocol** để tự động issue/renew trực tiếp trên host (không phải cơ chế integrated service).

---

## 📄 Nội dung (trích từ tài liệu gốc)

# What is AWS Certificate Manager?

AWS Certificate Manager (ACM) handles the complexity of creating, storing, and renewing public and private SSL/TLS X.509 certificates and keys that protect your AWS websites and applications. You can provide certificates for your integrated AWS services either by issuing them directly with ACM or by importing third-party certificates into the ACM management system. ACM certificates can secure singular domain names, multiple specific domain names, wildcard domains, or combinations of these. ACM wildcard certificates can protect an unlimited number of subdomains. You can also export ACM certificates signed by AWS Private CA for use anywhere in your internal PKI.

**Note:** You can use ACM certificates with stand-alone web servers and other customer-managed infrastructure, including Amazon EC2 instances. For publicly trusted web certificates on these servers, use the ACME protocol to automate issuance and renewal directly on your hosts. For private PKI scenarios, see the tutorial for setting up a secure server on an Amazon EC2 instance (Configure SSL/TLS on Amazon Linux 2023).

**Topics**
- Supported Regions
- Pricing for AWS Certificate Manager
- AWS Certificate Manager concepts
- Choosing how to issue certificates with AWS

## Supported Regions

ACM supports IPv4 and IPv6 on public endpoints. Visit AWS Regions and Endpoints in the AWS General Reference or the AWS Region Table to see the regional availability for ACM.

Certificates in ACM are **regional resources**. To use a certificate with Elastic Load Balancing for the same fully qualified domain name (FQDN) or set of FQDNs in more than one AWS region, you must request or import a certificate for each region. For certificates provided by ACM, this means you must revalidate each domain name in the certificate for each region. **You cannot copy a certificate between regions.**

To use an ACM certificate with Amazon CloudFront, **you must request or import the certificate in the US East (N. Virginia) region**. ACM certificates in this region that are associated with a CloudFront distribution are distributed to all the geographic locations configured for that distribution.

## Pricing for AWS Certificate Manager

You are not subject to an additional charge for SSL/TLS certificates that you manage with AWS Certificate Manager. You pay only for the AWS resources that you create to run your website or application.
