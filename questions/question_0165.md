# Question #165 - Topic 1

A solutions architect must design a solution that uses Amazon CloudFront with an Amazon S3 origin to store a static website. The company’s security policy requires that all website traffic be inspected by AWS WAF. How should the solutions architect comply with these requirements?

## Options

**A.** Configure an S3 bucket policy to accept requests coming from the AWS WAF Amazon Resource Name (ARN) only.

**B.** Configure Amazon CloudFront to forward all incoming requests to AWS WAF before requesting content from the S3 origin.

**C.** Configure a security group that allows Amazon CloudFront IP addresses to access Amazon S3 only. Associate AWS WAF to CloudFront.

**D.** Configure Amazon CloudFront and Amazon S3 to use an origin access identity (OAI) to restrict access to the S3 bucket. Enable AWS WAF on the distribution.

