# Question #231 - Topic 1

An application runs on an Amazon EC2 instance that has an Elastic IP address in VPC A. The application requires access to a database in VPC B. Both VPCs are in the same AWS account. Which solution will provide the required access MOST securely?

## Options

**A.** Create a DB instance security group that allows all traffic from the public IP address of the application server in VPC A.

**B.** Configure a VPC peering connection between VPC A and VPC B.

**C.** Make the DB instance publicly accessible. Assign a public IP address to the DB instance.

**D.** Launch an EC2 instance with an Elastic IP address into VPC B. Proxy all requests through the new EC2 instance.

