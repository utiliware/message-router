import boto3
import os

ddb = boto3.resource("dynamodb")
table = ddb.Table(os.environ["CONNECTIONS_TABLE"])

def lambda_handler(event, context):
    connection_id = event["requestContext"]["connectionId"]
    table.delete_item(Key={"connectionId": connection_id})
    print(f"Removed connection: {connection_id}")
    return {"statusCode": 200}