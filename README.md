``` mermaid
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

    style Message fill:#e6b8af,stroke:#a61c00,stroke-width:2px,color:#000
    style APIGateway fill:#6237be
    style SQS1 fill:#bc1356
    style LambdaSamuel fill:#cf5b17
    style EventBridge1 fill:#bc1356
    style LambdaHugoHiram fill:#cf5b17
    style SQS2 fill:#bc1356
    style StepFunctions fill:#bc1356
    style EventBridge2 fill:#bc1356
    style SNSTopic fill:#bc1356
    style LambdaRaul fill:#cf5b17
    style DynamoDB fill:#3b42c2
    style LambdaS3 fill:#cf5b17
    style S3 fill:#337b1c
```
