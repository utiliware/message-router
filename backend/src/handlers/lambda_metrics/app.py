import boto3
import json
from datetime import datetime, timedelta

cloudwatch = boto3.client("cloudwatch")

# Lista de lambdas que quieres monitorear
FUNCTIONS = ["ReactApp-LambdaDispatcher-NeDu0cjfQ9T", "ReactApp-ApiFunction-e9uj0xbcfDWH", "ReactApp-DynamoLambda-kYB5fzKGqrZB", "ReactApp-DdbToS3Handler"]

def lambda_handler(event, context):
    now = datetime.utcnow()
    start_time = now - timedelta(minutes=15)

    durations = []
    invocations = []

    # --- Loop para todas las funciones ---
    for fn in FUNCTIONS:
        # Métrica: Duration promedio
        duration_metrics = cloudwatch.get_metric_data(
            MetricDataQueries=[
                {
                    "Id": f"duration_{fn.lower()}",
                    "MetricStat": {
                        "Metric": {
                            "Namespace": "AWS/Lambda",
                            "MetricName": "Duration",
                            "Dimensions": [
                                {"Name": "FunctionName", "Value": fn}
                            ]
                        },
                        "Period": 300,
                        "Stat": "Average",
                    },
                    "ReturnData": True,
                }
            ],
            StartTime=start_time,
            EndTime=now,
        )

        print(duration_metrics["MetricDataResults"])

        for ts, val in zip(duration_metrics["MetricDataResults"][0].get("Timestamps", []),
                           duration_metrics["MetricDataResults"][0].get("Values", [])):
            durations.append({
                "timestamp": int(ts.timestamp() * 1000),
                "functionName": fn,
                "avgMs": val
            })

        # Métrica: Invocations
        invocations_metrics = cloudwatch.get_metric_data(
            MetricDataQueries=[
                {
                    "Id": f"invocations_{fn.lower()}",
                    "MetricStat": {
                        "Metric": {
                            "Namespace": "AWS/Lambda",
                            "MetricName": "Invocations",
                            "Dimensions": [
                                {"Name": "FunctionName", "Value": fn}
                            ]
                        },
                        "Period": 60,
                        "Stat": "Sum",
                    },
                    "ReturnData": True,
                }
            ],
            StartTime=start_time,
            EndTime=now,
        )

        for ts, val in zip(invocations_metrics["MetricDataResults"][0].get("Timestamps", []),
                           invocations_metrics["MetricDataResults"][0].get("Values", [])):
            invocations.append({
                "timestamp": int(ts.timestamp() * 1000),
                "functionName": fn,
                "count": val
            })

    # EventBridge latencias (simulación fija, ya que no existe métrica directa en CW)
    latencies = [{
        "timestamp": int(now.timestamp() * 1000),
        "ruleName": "SendToSNSRule",
        "p50Ms": 10,
        "p95Ms": 20
    }]

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
            "Access-Control-Allow-Methods": "OPTIONS,GET"
        },
        "body": json.dumps({
            "lambdaDurations": durations,
            "eventBridgeLatencies": latencies,
            "invocations": invocations
        })
    }
