# Amazon Athena

- Data processing

- Interactive analytics

- serverless

- Purpose: USE SQL to query data in S3.

- Optimized for performing real-time data analysis and exploration, which allows users to interactively query and visualize data.

# Athena for Apache Spark -> Jupyter Notebook

# Keywords

- **SQL queries on S3** (Standard SQL queries directly on Amazon S3 data)
- **Serverless** (No infrastructure to manage or set up)
- **Pay-per-query** (Pricing based on the amount of data scanned in TB)
- **Columnar Storage (Parquet / ORC)** (Highly recommended to reduce scanned data size and cost)
- **Glue Data Catalog** (Integrates with Glue to fetch schemas for tables)
- **Partitioning** (Organizing S3 data by folders/keys to limit data scanned per query)
- **Workgroups** (Used for query control, cost limits, and user isolation)
- **Athena for Apache Spark** (Interactive Spark application running with Jupyter Notebooks)