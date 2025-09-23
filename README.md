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
    style APIGateway fill:#e69138,stroke:#783f04,stroke-width:2px,color:#000
    style SQS1 fill:#f1c232,stroke:#7f6000,stroke-width:2px,color:#000
    style LambdaSamuel fill:#6aa84f,stroke:#274e13,stroke-width:2px,color:#000
    style EventBridge1 fill:#6d9eeb,stroke:#073763,stroke-width:2px,color:#000
    style LambdaHugoHiram fill:#6aa84f,stroke:#274e13,stroke-width:2px,color:#000
    style SQS2 fill:#f1c232,stroke:#7f6000,stroke-width:2px,color:#000
    style StepFunctions fill:#8e7cc3,stroke:#351c75,stroke-width:2px,color:#000
    style EventBridge2 fill:#6d9eeb,stroke:#073763,stroke-width:2px,color:#000
    style SNSTopic fill:#e69138,stroke:#783f04,stroke-width:2px,color:#000
    style LambdaRaul fill:#6aa84f,stroke:#274e13,stroke-width:2px,color:#000
    style DynamoDB fill:#3d85c6,stroke:#0b5394,stroke-width:2px,color:#fff
    style LambdaS3 fill:#6aa84f,stroke:#274e13,stroke-width:2px,color:#000
    style S3 fill:#3c78d8,stroke:#073763,stroke-width:2px,color:#fff
```
