import boto3
import os

ddb = boto3.resource("dynamodb")
table = ddb.Table(os.environ["CONNECTIONS_TABLE"])

def lambda_handler(event, context):
    connection_id = event["requestContext"]["connectionId"]
    table.put_item(Item={"connectionId": connection_id})
    print(f"Added connection: {connection_id}")
    return {"statusCode": 200}