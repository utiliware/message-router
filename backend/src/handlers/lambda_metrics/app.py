import boto3
import json
from datetime import datetime, timedelta

cloudwatch = boto3.client("cloudwatch")

def lambda_handler(event, context):
    now = datetime.utcnow()
    start_time = now - timedelta(minutes=15)

    response = cloudwatch.get_metric_data(
        MetricDataQueries=[
            {
                "Id": "lambda_concurrency",
                "MetricStat": {
                    "Metric": {
                        "Namespace": "AWS/Lambda",
                        "MetricName": "ConcurrentExecutions",
                        "Dimensions": []  # Puedes agregar nombre de función si quieres filtrar
                    },
                    "Period": 60,
                    "Stat": "Average",
                },
                "ReturnData": True,
            }
        ],
        StartTime=start_time,
        EndTime=now,
    )

    # Extraer datos de CloudWatch
    metric_result = response["MetricDataResults"][0]

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",  # Permite CORS
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
            "Access-Control-Allow-Methods": "OPTIONS,GET"
        },
        "body": json.dumps({
            "Label": metric_result.get("Label"),
            "Timestamps": [t.isoformat() for t in metric_result.get("Timestamps", [])],
            "Values": metric_result.get("Values", [])
        })
    }
