import { LambdaClient, InvokeCommand } from "@aws-sdk/client-lambda";

// retryMode + maxAttempts: SDK tự backoff+jitter khi bị throttle
const client = new LambdaClient({
  region: "us-east-1",
  retryMode: "adaptive",
  maxAttempts: 5,
});

const res = await client.send(new InvokeCommand({
  FunctionName: "dva-lab-fn",
  Payload: Buffer.from(JSON.stringify({ name: "sdk" })),
}));
console.log(new TextDecoder().decode(res.Payload));
