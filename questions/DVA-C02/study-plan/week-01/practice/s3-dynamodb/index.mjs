import { randomUUID } from "crypto";
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, PutCommand } from "@aws-sdk/lib-dynamodb";
import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";

const TABLE  = process.env.TABLE_NAME;
const BUCKET = process.env.BUCKET_NAME;

// client tạo ở init → tái sử dụng giữa các invoke
const ddb = DynamoDBDocumentClient.from(new DynamoDBClient({}));
const s3  = new S3Client({});

export const handler = async (event, context) => {
  const itemId = randomUUID();
  // (1) Ghi item vào DynamoDB — cần dynamodb:PutItem trong execution role
  await ddb.send(new PutCommand({
    TableName: TABLE,
    Item: { id: itemId, ts: Math.floor(Date.now() / 1000), msg: event.msg ?? "hi" },
  }));
  // (2) Put object lên S3 — cần s3:PutObject
  await s3.send(new PutObjectCommand({
    Bucket: BUCKET,
    Key: `events/${itemId}.json`,
    Body: JSON.stringify(event),
  }));
  return { ok: true, id: itemId };
};
