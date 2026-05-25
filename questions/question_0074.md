# Question #74 - Topic 1

A solutions architect is designing a two-tier web application. The application consists of a public-facing web tier hosted on Amazon EC2 in public subnets. The database tier consists of Microsoft SQL Server running on Amazon EC2 in a private subnet. Security is a high priority for the company. How should security groups be configured in this situation? (Choose two.)

## Options

**A.** Configure the security group for the web tier to allow inbound traffic on port 443 from 0.0.0.0/0.

**B.** Configure the security group for the web tier to allow outbound traffic on port 443 from 0.0.0.0/0.

**C.** Configure the security group for the database tier to allow inbound traffic on port 1433 from the security group for the web tier.

**D.** Configure the security group for the database tier to allow outbound traffic on ports 443 and 1433 to the security group for the web tier.

**E.** Configure the security group for the database tier to allow inbound traffic on ports 443 and 1433 from the security group for the web tier.

