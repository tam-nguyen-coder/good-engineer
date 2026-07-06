# Amazon Kinesis Data Streams

- Data Streaming

- Real-time processing.

Optimized for rapid and continuous data intake and aggregation, including IT infrastructure log data, application logs, social media, market data feeds, and web clickstream data.

# Keywords

- **Shards** (Throughput unit: 1MB/s write, 2MB/s read per shard)
- **Partition Key** (Determines which shard receives the data; preserves order per key)
- **Sub-second Latency / Real-time** (Immediate processing of streaming data)
- **Data Retention** (24 hours default, extendable up to 365 days)
- **Enhanced Fan-Out** (Dedicated throughput of 2MB/s per consumer using HTTP/2)
- **KPL / KCL** (Kinesis Producer/Client Library for custom ingestion/processing)
- **Provisioned vs On-Demand** (Capacity modes for scaling shards)
