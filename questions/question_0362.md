# Question #362 - Topic 1

A company uses a payment processing system that requires messages for a particular payment ID to be received in the same order that they were sent. Otherwise, the payments might be processed incorrectly. Which actions should a solutions architect take to meet this requirement? (Choose two.)

## Options

**A.** Write the messages to an Amazon DynamoDB table with the payment ID as the partition key.

**B.** Write the messages to an Amazon Kinesis data stream with the payment ID as the partition key.

**C.** Write the messages to an Amazon ElastiCache for Memcached cluster with the payment ID as the key.

**D.** Write the messages to an Amazon Simple Queue Service (Amazon SQS) queue. Set the message attribute to use the payment ID.

**E.** Write the messages to an Amazon Simple Queue Service (Amazon SQS) FIFO queue. Set the message group to use the payment ID.

