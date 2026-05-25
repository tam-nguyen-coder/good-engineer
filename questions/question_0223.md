# Question #223 - Topic 1

A company has deployed a Java Spring Boot application as a pod that runs on Amazon Elastic Kubernetes Service (Amazon EKS) in private subnets. The application needs to write data to an Amazon DynamoDB table. A solutions architect must ensure that the application can interact with the DynamoDB table without exposing traffic to the internet. Which combination of steps should the solutions architect take to accomplish this goal? (Choose two.)

## Options

**A.** Attach an IAM role that has sufficient privileges to the EKS pod.

**B.** Attach an IAM user that has sufficient privileges to the EKS pod.

**C.** Allow outbound connectivity to the DynamoDB table through the private subnets’ network ACLs.

**D.** Create a VPC endpoint for DynamoDB.

**E.** Embed the access keys in the Java Spring Boot code.

