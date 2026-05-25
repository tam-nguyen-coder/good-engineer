# Question #431 - Topic 1

A company has developed a new video game as a web application. The application is in a three-tier architecture in a VPC with Amazon RDS for MySQL in the database layer. Several players will compete concurrently online. The game’s developers want to display a top-10 scoreboard in near- real time and offer the ability to stop and restore the game while preserving the current scores. What should a solutions architect do to meet these requirements?

## Options

**A.** Set up an Amazon ElastiCache for Memcached cluster to cache the scores for the web application to display.

**B.** Set up an Amazon ElastiCache for Redis cluster to compute and cache the scores for the web application to display.

**C.** Place an Amazon CloudFront distribution in front of the web application to cache the scoreboard in a section of the application.

**D.** Create a read replica on Amazon RDS for MySQL to run queries to compute the scoreboard and serve the read traffic to the web application.

