# Question #227 - Topic 1

A company needs to retain its AWS CloudTrail logs for 3 years. The company is enforcing CloudTrail across a set of AWS accounts by using AWS Organizations from the parent account. The CloudTrail target S3 bucket is configured with S3 Versioning enabled. An S3 Lifecycle policy is in place to delete current objects after 3 years. After the fourth year of use of the S3 bucket, the S3 bucket metrics show that the number of objects has continued to rise. However, the number of new CloudTrail logs that are delivered to the S3 bucket has remained consistent. Which solution will delete objects that are older than 3 years in the MOST cost-effective manner?

## Options

**A.** Configure the organization’s centralized CloudTrail trail to expire objects after 3 years.

**B.** Configure the S3 Lifecycle policy to delete previous versions as well as current versions.

**C.** Create an AWS Lambda function to enumerate and delete objects from Amazon S3 that are older than 3 years.

**D.** Configure the parent account as the owner of all objects that are delivered to the S3 bucket.

