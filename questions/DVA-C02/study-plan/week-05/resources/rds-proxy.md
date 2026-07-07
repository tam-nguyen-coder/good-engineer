# Amazon RDS Proxy

> **Nguồn (AWS official):** https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/rds-proxy.html
> **Tuần:** 5 — Messaging + Step Functions + Caching · **Loại:** AWS Docs
> ⚠️ Nội dung dưới đây được crawl tự động (qua WebFetch, có thể rút gọn nhẹ) — luôn đối chiếu link gốc để đầy đủ & cập nhật nhất.

## 🎯 Điểm thi quan trọng (tóm tắt tiếng Việt)
- **`RDS Proxy` = connection pooling**: gom và chia sẻ (tái dùng) connection tới DB → xử lý được các đợt tăng đột biến traffic (đặc biệt do **`Lambda` scale = "connection storm"**), tránh oversubscribe DB.
- Tăng **độ bền khi failover**: tự kết nối sang **standby DB instance** trong khi **giữ nguyên** connection của ứng dụng → giảm downtime.
- **Bảo mật:** client kết nối proxy **bắt buộc IAM authentication** (nếu bật); proxy kết nối DB bằng **IAM database auth** hoặc credential trong **`AWS Secrets Manager`**.
- **Không đổi code:** bật được cho hầu hết ứng dụng mà **không cần sửa code**; tương thích đầy đủ với các engine version được hỗ trợ.
- Số PHẢI NHỚ (quota): **20 proxy / account**; mỗi proxy tối đa **200 Secrets Manager secrets** (→ tối đa 200 user account); default endpoint trải trên **2 AZ**; thêm được tới **20 proxy endpoint** phụ.
- Proxy khi quá tải sẽ **queue/throttle** rồi mới **reject** (shed load) — latency có thể tăng nhưng DB không bị sập.
- **Vị trí mạng:** proxy phải **cùng VPC** với DB, **không public**; chỉ gắn với **writer DB instance** (không gắn read replica); không dùng với VPC tenancy `dedicated`.
- **Session pinning:** câu lệnh có text > **16 KB** khiến proxy **pin** session vào 1 connection (mất lợi ích pooling).

---

## 📄 Nội dung (trích từ tài liệu gốc)

By using Amazon RDS Proxy, you can allow your applications to **pool and share database connections** to improve their ability to scale. RDS Proxy makes applications more **resilient to database failures** by automatically connecting to a **standby DB instance while preserving application connections**. By using RDS Proxy, you can enforce **AWS IAM authentication** for clients connecting to the proxy, and the proxy can connect to databases using either **IAM database authentication** or **credentials stored in AWS Secrets Manager**.

Using RDS Proxy, you can handle **unpredictable surges** in database traffic. Otherwise, these surges might cause issues due to oversubscribing connections or new connections being created at a fast rate. RDS Proxy establishes a **database connection pool** and reuses connections in this pool. This avoids the memory and CPU overhead of opening a new database connection each time. To protect a database against oversubscription, you can control the number of database connections that are created.

RDS Proxy **queues or throttles** application connections that can't be served immediately from the connection pool. Although latencies might increase, your application can continue to scale without abruptly failing or overwhelming the database. If connection requests exceed the limits you specify, RDS Proxy **rejects application connections (sheds load)**, while maintaining predictable performance for the load that RDS can serve.

You can reduce the overhead to process credentials and establish a secure connection for each new connection. RDS Proxy is **fully compatible** with the engine versions it supports. You can enable RDS Proxy for most applications with **no code changes**.

### Region and version availability

Feature availability and support varies across specific versions of each database engine, and across AWS Regions. See *Supported Regions and DB engines for Amazon RDS Proxy*.

### Quotas and limitations for RDS Proxy

- Each **AWS account ID is limited to 20 proxies**. Request an increase via the Service Quotas page (Amazon RDS → **Proxies**) if you need more.
- Each proxy can have up to **200 associated Secrets Manager secrets**, thus limiting connections to up to **200 different user accounts** when using secrets.
- Each proxy has a **default endpoint** provisioned across only **two Availability Zones** selected from the proxy's configured subnets.
- You can add up to **20 additional proxy endpoints** per proxy, provisioned across all the AZs specified during their creation.
- For RDS DB instances in replication configurations, you can associate a proxy only with the **writer DB instance, not a read replica**.
- Your RDS Proxy must be in the **same VPC** as the database. The proxy **can't be publicly accessible**, although the database can be.
- You **can't use RDS Proxy with a VPC that has its tenancy set to `dedicated`**.
- You can't use RDS Proxy in a VPC that has encryption controls with `Enforce Mode` enabled.
- For IPv6 endpoint network types, configure your VPC and subnets to support only IPv6. For both IPv4 and IPv6 target connection network types, configure dual-stack mode.
- If you use RDS Proxy with a DB instance that has IAM authentication enabled, the proxy can connect to the database using either IAM authentication or Secrets Manager credentials. **Clients connecting to the proxy must authenticate using IAM credentials.**
- You can't use RDS Proxy with custom DNS when using SSL hostname validation.
- Each proxy can be associated with a **single target DB instance**. However, you can associate **multiple proxies with the same DB instance**.
- **Any statement with a text size greater than 16 KB causes the proxy to pin the session** to the current connection.
- Certain Regions have AZ restrictions: US East (N. Virginia) does not support RDS Proxy in `use1-az3`; US West (N. California) does not support it in `usw1-az2`.
- RDS Proxy doesn't support any global condition context keys.
- You can't use RDS Proxy with RDS Custom for SQL Server.
- To reflect a database parameter group modification, an **instance reboot is required** (cluster-wide reboot for cluster-level parameters).
- Your proxy automatically creates the protected **`rdsproxyadmin` DB user** when you register a proxy target. Deleting or modifying it can make the proxy completely unavailable.

#### Engine-specific highlights
- **MySQL / MariaDB:** proxies listen on port **3306**; can't use with self-managed DBs on EC2; can't use if `read_only` parameter = `1`; no compressed mode; don't set `sql_auto_is_null` to true.
- **PostgreSQL:** proxies listen on port **5432**; the default `postgres` database must exist; no session pinning filters; no streaming replication mode; supports only version 3.0 of the PostgreSQL messaging protocol.
- **SQL Server:** number of Secrets Manager secrets depends on collation; no Active Directory connections; does not support SQL Server 2022 or 2014 major versions; no end-to-end IAM authentication.

(For additional per-engine limitations, see the source page.)
