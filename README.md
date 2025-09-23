flowchart TD
    Message([Message]) --> Angel
    
    subgraph Angel
        APIGateway -. "Sends message to the queue" .-> SQS1["SQS"]
    end

    SQS1 -. "Gets message from the Queue" .-> Samuel

    subgraph Samuel
        LambdaSamuel["Lambda"] -. "Sends message to EventBridge" .-> EventBridge1["EventBridge (Rule 1)"]
    end

    EventBridge1 -.-> Hugo_Hiram

    subgraph Hugo_Hiram["Hugo & Hiram"]
        LambdaHugoHiram["Lambda"] --> SQS2["SQS 2"]
    end

    SQS2 -. "Sends message to StepFunctions" .-> Hiram

    subgraph Hiram
        StepFunctions 
    end

    StepFunctions -. "Get message from StepFunctions" .-> Ricardo

    subgraph Ricardo
        EventBridge2["EventBridge (Rule 2)"]
    end

    EventBridge2 -. "Send message to topic" .-> Raul

    subgraph Raul
        SNSTopic -. "Subscribe to topic" .-> LambdaRaul["Lambda"]
    end

    LambdaRaul -. "Store in DynamoDB" .-> Pepe

    subgraph Pepe
        DynamoDB
    end

    DynamoDB -. "DynamoDB Streams" .-> Llineth_Stellios

    subgraph Llineth_Stellios["Llineth & Stellios"]
        LambdaS3["Lambda"] --> S3["S3 Bucket"]
    end
