# Question #285 - Topic 1

A company hosts its static website by using Amazon S3. The company wants to add a contact form to its webpage. The contact form will have dynamic server-side components for users to input their name, email address, phone number, and user message. The company anticipates that there will be fewer than 100 site visits each month. Which solution will meet these requirements MOST cost-effectively?

## Options

**A.** Host a dynamic contact form page in Amazon Elastic Container Service (Amazon ECS). Set up Amazon Simple Email Service (Amazon SES) to connect to any third-party email provider.

**B.** Create an Amazon API Gateway endpoint with an AWS Lambda backend that makes a call to Amazon Simple Email Service (Amazon SES).

**C.** Convert the static webpage to dynamic by deploying Amazon Lightsail. Use client-side scripting to build the contact form. Integrate the form with Amazon WorkMail.

**D.** Create a t2.micro Amazon EC2 instance. Deploy a LAMP (Linux, Apache, MySQL, PHP/Perl/Python) stack to host the webpage. Use client- side scripting to build the contact form. Integrate the form with Amazon WorkMail.

## 1. CONTEXT & ĐỀ BÀI
- **Scenario:** Static S3 website cần thêm contact form có dynamic server-side components. Rất ít traffic (<100 visits/month).
- **Existing Resources:** S3 static website.
- **Current Issue/Goal:** Thêm dynamic contact form, cost-effective nhất.

## 2. KEYWORDS QUAN TRỌNG
| Keyword | Ý nghĩa / Gợi ý |
|---------|-----------------|
| `fewer than 100 site visits each month` | Cực kỳ ít traffic → cần serverless/pay-per-use để tối ưu chi phí. |
| `most cost-effectively` | Chi phí thấp nhất. Serverless Lambda + API Gateway là lý tưởng cho low traffic. |
| `dynamic server-side components` | Cần xử lý request từ form (không thể chỉ client-side). |
| `Amazon SES` | Email service, có thể gửi email không cần SMTP server riêng. |

## 3. YÊU CẦU CỦA ĐỀ
- **Question type:** Most cost-effective
- **Constraints:** <100 visits/month, dynamic contact form, send email

## 4. ĐÁP ÁN ĐÚNG
**✅ Đáp án: B**

**Giải thích:**
- API Gateway + Lambda là serverless → pay-per-use, chi phí rất thấp cho <100 requests/tháng (trong free tier).
- Lambda gọi SES để gửi email từ form, không cần maintain server.
- S3 vẫn giữ static content, chỉ contact form xử lý qua API.

## 5. CÁC ĐÁP ÁN SAI
**❌ Đáp án A:**
- ECS dù serverless (Fargate) nhưng vẫn cần cluster, task definitions → over-engineered và đắt hơn Lambda.

**❌ Đáp án C:**
- Lightsail là VPS (trả phí cố định hàng tháng) → đắt hơn so với serverless cho <100 visits.

**❌ Đáp án D:**
- EC2 t2.micro vẫn trả phí dù ít traffic, phải tự quản LAMP stack → operational overhead cao hơn và cost không tối ưu.

## 6. MẸO GHI NHỚ (Memory Hook)
🧠 *"Low traffic + dynamic form → API Gateway + Lambda + SES = cheapest. EC2/ECS/Lightsail đều đắt hơn cho <100 visits."*
