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

    style Message fill:#fce5cd,stroke:#e69138,stroke-width:2px
    style APIGateway fill:#f6b26b,stroke:#e69138,stroke-width:2px
    style SQS1 fill:#ffe599,stroke:#bf9000,stroke-width:2px
    style LambdaSamuel fill:#93c47d,stroke:#38761d,stroke-width:2px
    style EventBridge1 fill:#a4c2f4,stroke:#1155cc,stroke-width:2px
    style LambdaHugoHiram fill:#93c47d,stroke:#38761d,stroke-width:2px
    style SQS2 fill:#ffe599,stroke:#bf9000,stroke-width:2px
    style StepFunctions fill:#b4a7d6,stroke:#674ea7,stroke-width:2px
    style EventBridge2 fill:#a4c2f4,stroke:#1155cc,stroke-width:2px
    style SNSTopic fill:#f9cb9c,stroke:#e69138,stroke-width:2px
    style LambdaRaul fill:#93c47d,stroke:#38761d,stroke-width:2px
    style DynamoDB fill:#6fa8dc,stroke:#0b5394,stroke-width:2px
    style LambdaS3 fill:#93c47d,stroke:#38761d,stroke-width:2px
    style S3 fill:#cfe2f3,stroke:#0b5394,stroke-width:2px
```
