# Question #631 - Topic 1

A social media company wants to store its database of user profiles, relationships, and interactions in the AWS Cloud. The company needs an application to monitor any changes in the database. The application needs to analyze the relationships between the data entities and to provide recommendations to users. Which solution will meet these requirements with the LEAST operational overhead?

## Options

**A.** Use Amazon Neptune to store the information. Use Amazon Kinesis Data Streams to process changes in the database.

**B.** Use Amazon Neptune to store the information. Use Neptune Streams to process changes in the database.

**C.** Use Amazon Quantum Ledger Database (Amazon QLDB) to store the information. Use Amazon Kinesis Data Streams to process changes in the database.

**D.** Use Amazon Quantum Ledger Database (Amazon QLDB) to store the information. Use Neptune Streams to process changes in the database.

## 1. CONTEXT & DE BAI
- **Scenario:** Social media company can store user profiles, relationships (graph data), interactions. Can monitor changes and analyze relationships for recommendations.
- **Existing Resources:** None.
- **Current Issue/Goal:** Graph database (relationships) + change data capture (CDC) for recommendations.

## 2. KEYWORDS QUAN TRONG
| Keyword | Y nghia / Goi y |
|---------|-----------------|
| `relationships between data entities` | Graph data => Amazon Neptune (graph database). |
| `monitor any changes in the database` | Change Data Capture => Neptune Streams. |
| `recommendations to users` | Graph queries (friends of friends, interactions). |
| `Neptune Streams` | Built-in CDC cho Neptune, tu dong capture changes. |
| `least operational overhead` | Neptune + Neptune Streams (built-in, khong can Kinesis). |

## 3. YEU CAU CUA DE
- **Question type:** Least operational overhead
- **Constraints:** Store relationships, monitor changes, provide recommendations

## 4. DAP AN DUNG
**Dap an: B**

**Giai thich:**
- Amazon Neptune: graph database chuyen cho use case co nhieu relationships (social media, recommendations).
- Neptune Streams: built-in feature de capture changes trong database, tu dong, khong can Kinesis.
- Ket hop Neptune + Neptune Streams la giai phap co operational overhead thap nhat cho graph + CDC.

## 5. CAC DAP AN SAI
**Dap an A:**
- Neptune + Kinesis Data Streams: duoc nhung operational overhead cao hon vi can cau hinh Kinesis rieng.

**Dap an C:**
- Amazon QLDB: ledger database (immutable, append-only), khong duoc optimize cho graph relationships va recommendations.

**Dap an D:**
- QLDB + Neptune Streams: Neptune Streams chi works voi Neptune, khong the dung voi QLDB.

## 6. MEO GHI NHO (Memory Hook)
*"Relationships (graph) => Neptune. CDC => Neptune Streams (built-in). QLDB = ledger, khong phai graph."*
