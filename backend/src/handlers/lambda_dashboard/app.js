import { CloudWatchClient, GetMetricDataCommand } from "@aws-sdk/client-cloudwatch";

const client = new CloudWatchClient({ region: "us-east-1" });

/* ----------------------------- HELPERS ----------------------------- */
const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "Content-Type",
  "Access-Control-Allow-Methods": "GET,OPTIONS"
};

const metric = ({ id, namespace, name, stat = "Sum", period = 300, dimensions = [] }) => ({
  Id: id,
  MetricStat: {
    Metric: {
      Namespace: namespace,
      MetricName: name,
      Dimensions: dimensions
    },
    Period: period,
    Stat: stat
  },
  ReturnData: true
});

/* -------------------------- FORMATTERS ----------------------------- */
const formatForFrontend = (results) => {
  console.log("Raw MetricDataResults:", JSON.stringify(results, null, 2));
  
  const byId = Object.fromEntries(
    results.map(r => [r.Id, r])
  );
  
  const formatted = {
    sns: formatSNS(byId.snsPublished),
    sqs: formatSQS([
      byId.sqsVisible,
      byId.sqsInFlight,
      byId.sqsSent,
      byId.sqsReceived
    ]),
    lambdaErrors: formatLambdaErrors(byId.lambdaErrors)
  };
  
  console.log("Formatted payload:", JSON.stringify(formatted, null, 2));
  return formatted;
};

const formatSNS = (metric) => {
  console.log("SNS metric:", metric);
  return {
    value: metric?.Values?.[0] ?? 0
  };
};

const formatSQS = (metrics) => {
  console.log("SQS metrics:", metrics);
  const map = {};
  
  metrics.forEach(metric => {
    if (!metric || !metric.Timestamps || metric.Timestamps.length === 0) return;
    
    metric.Timestamps.forEach((ts, i) => {
      const time = new Date(ts).toISOString();
      map[time] ??= { time };
      map[time][metric.Id] = metric.Values[i];
    });
  });
  
  return Object.values(map).sort(
    (a, b) => new Date(a.time) - new Date(b.time)
  );
};

const formatLambdaErrors = (metric) => {
  console.log("Lambda Errors metric:", metric);
  if (!metric || !metric.Timestamps || metric.Timestamps.length === 0) return [];
  
  return metric.Timestamps.map((ts, i) => ({
    time: new Date(ts).toISOString(),
    errors: metric.Values[i]
  })).sort(
    (a, b) => new Date(a.time) - new Date(b.time)
  );
};

/* ------------------------------ HANDLER ---------------------------- */
export const handler = async (event) => {
  console.log("Incoming event:", JSON.stringify(event, null, 2));
  
  if (event.httpMethod === "OPTIONS") {
    return {
      statusCode: 200,
      headers: corsHeaders,
      body: ""
    };
  }

  const endTime = new Date();
  const startTime = new Date(endTime.getTime() - 12 * 60 * 60 * 1000);
  
  console.log("Time range:", {
    startTime: startTime.toISOString(),
    endTime: endTime.toISOString()
  });

  const SNS_TOPIC_NAME = process.env.SNS_TOPIC_NAME || "MyTargetTopic";
  const SQS_QUEUE_NAME = process.env.SQS_QUEUE_NAME || "MyMessageQueue";
  const LAMBDA_FUNCTION_NAME = process.env.LAMBDA_FUNCTION_NAME || "api_router";

  const queries = [
    // SNS
    metric({
      id: "snsPublished",
      namespace: "AWS/SNS",
      name: "NumberOfMessagesPublished",
      stat: "Sum",
      dimensions: [{ Name: "TopicName", Value: SNS_TOPIC_NAME }]
    }),
    
    // Lambda
    metric({
      id: "lambdaErrors",
      namespace: "AWS/Lambda",
      name: "Errors",
      stat: "Sum",
      dimensions: [{ Name: "FunctionName", Value: LAMBDA_FUNCTION_NAME }]
    }),
    
    // SQS
    metric({
      id: "sqsVisible",
      namespace: "AWS/SQS",
      name: "ApproximateNumberOfMessagesVisible",
      stat: "Average",
      dimensions: [{ Name: "QueueName", Value: SQS_QUEUE_NAME }]
    }),
    metric({
      id: "sqsInFlight",
      namespace: "AWS/SQS",
      name: "ApproximateNumberOfMessagesNotVisible",
      stat: "Average",
      dimensions: [{ Name: "QueueName", Value: SQS_QUEUE_NAME }]
    }),
    metric({
      id: "sqsSent",
      namespace: "AWS/SQS",
      name: "NumberOfMessagesSent",
      stat: "Sum",
      dimensions: [{ Name: "QueueName", Value: SQS_QUEUE_NAME }]
    }),
    metric({
      id: "sqsReceived",
      namespace: "AWS/SQS",
      name: "NumberOfMessagesReceived",
      stat: "Sum",
      dimensions: [{ Name: "QueueName", Value: SQS_QUEUE_NAME }]
    })
  ];

  console.log("Metric queries:", JSON.stringify(queries, null, 2));

  const response = await client.send(
    new GetMetricDataCommand({
      StartTime: startTime,
      EndTime: endTime,
      MetricDataQueries: queries
    })
  );

  console.log("CloudWatch response:", JSON.stringify(response, null, 2));

  const payload = formatForFrontend(response.MetricDataResults);

  return {
    statusCode: 200,
    headers: corsHeaders,
    body: JSON.stringify(payload)
  };
};
