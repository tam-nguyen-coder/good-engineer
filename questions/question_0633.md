# Question #633 - Topic 1

A company manages an application that stores data on an Amazon RDS for PostgreSQL Multi-AZ DB instance. Increases in traffic are causing performance problems. The company determines that database queries are the primary reason for the slow performance. What should a solutions architect do to improve the application's performance?

## Options

**A.** Serve read traffic from the Multi-AZ standby replica.

**B.** Configure the DB instance to use Transfer Acceleration.

**C.** Create a read replica from the source DB instance. Serve read traffic from the read replica.

**D.** Use Amazon Kinesis Data Firehose between the application and Amazon RDS to increase the concurrency of database requests.

## 1. CONTEXT & DE BAI
- **Scenario:** RDS PostgreSQL Multi-AZ, traffic tang gay performance problems. Database queries la root cause.
- **Existing Resources:** RDS for PostgreSQL Multi-AZ.
- **Current Issue/Goal:** Giam tai cho database bang cach offload read queries.

## 2. KEYWORDS QUAN TRONG
| Keyword | Y nghia / Goi y |
|---------|-----------------|
| `database queries are the primary reason` | Can offload read traffic. |
| `Multi-AZ DB instance` | Multi-AZ standby chi dung cho failover, KHONG the serve read traffic. |
| `read replica` | Read replica co the serve read traffic, giam tai cho primary. |
| `improve performance` | Read replica giup scale read capacity. |

## 3. YEU CAU CUA DE
- **Question type:** Improve performance
- **Constraints:** RDS PostgreSQL, query performance, Multi-AZ

## 4. DAP AN DUNG
**Dap an: C**

**Giai thich:**
- RDS Read Replica: co the tao read replica tu source DB instance, serve read traffic tu read replica.
- Giam tai cho primary instance => improve performance cho write operations va cac read queries con lai.
- Read replica co the duoc dat cung region hoac cross-region.

## 5. CAC DAP AN SAI
**Dap an A:**
- Multi-AZ standby replica: chi dung cho failover va high availability, KHONG the serve read traffic. Day la misconception pho bien.

**Dap an B:**
- Transfer Acceleration: la tinh nang cua S3 (S3 Transfer Acceleration), khong lien quan den RDS.

**Dap an D:**
- Kinesis Data Firehose: streaming data delivery service, khong phu hop de increase database query concurrency.

## 6. MEO GHI NHO (Memory Hook)
*"Multi-AZ standby = HA failover (khong doc). Read replica = scale doc. Transfer Acceleration = S3."*
