import { useState, useEffect } from "react";
import Section from "../../../components/section";
import Chart from "./chart1";
import { useMetrics } from "../../../hooks/useMetrics";

export default function Metrics() {
  const data = useMetrics()
  const [activeChartId, setActiveChartId] = useState(null);
  const [metricsData, setMetricsData] = useState({
    sns: { value: 0 },
    sqs: [],
    lambdaErrors: [],
  });
  const [loading, setLoading] = useState(true);


  //CAMBIAR URL
  useEffect(() => {
    fetch("https://xddm904054.execute-api.us-east-1.amazonaws.com/Prod/metrics", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      }
    })
      .then(res => {
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.json();
      })
      .then(data => {
        const transformedSqs = data.sqs.map(item => ({
          time: item.time,
          visible: item.sqsVisible ?? 0,
          inFlight: item.sqsInFlight ?? 0,
          sent: item.sqsSent ?? 0,
          received: item.sqsReceived ?? 0
        }));

        const totalErrors = data.lambdaErrors.reduce((sum, item) => sum + (item.errors ?? 0), 0);
        const transformedErrors = totalErrors > 0 ? [{
          function: "message-router-ApiFunction",
          errors: totalErrors
        }] : [
          { function: "message-router-ApiFunction", errors: 0 },
          { function: "message-router-LambdaDispatcher", errors: 0 },
          { function: "message-router-DynamoLambda", errors: 0 },
          { function: "message-router-DdbToS3Handler", errors: 0 },
        ];

        setMetricsData({
          sns: data.sns,
          sqs: transformedSqs,
          lambdaErrors: transformedErrors,
        });
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load metrics:", err);
        setLoading(false);
      });
  }, []);

  const charts = [
    {
      id: 1,
      title: "SNS Messages Published",
      indicator: String(metricsData.sns.value || 0),
      componentType: "sns",
      componentData: metricsData.sns,
    },
    {
      id: 2,
      title: "SQS Queue: visible / in-flight / sent",
      indicator: String(metricsData.sqs.reduce((sum, item) => sum + (item.received || 0), 0)),
      componentType: "sqs",
      componentData: metricsData.sqs,
    },
    {
      id: 3,
      title: "Lambda Errors",
      indicator: String(metricsData.lambdaErrors.reduce((sum, r) => sum + (r.errors || 0), 0)),
      componentType: "lambda-errors",
      componentData: metricsData.lambdaErrors,
    },
  ];

  if (loading) {
    return (
      <Section
        title={"Metrics"}
        content={<p>Loading CloudWatch metrics…</p>}
      />
    );
  }

  return (
    <Section
      title={"Metrics"}
      content={
        <>
          {charts.filter((c) => activeChartId === null || c.id === activeChartId).map(({ id, title, indicator, componentType, componentData }) => (
              <Chart
                key={id}
                id={id}
                title={title}
                indicator={indicator}
                componentType={componentType}
                componentData={componentData}
                onToggle={(isOpen) =>
                  setActiveChartId(isOpen ? id : null)
                }
              />
            ))}
        </>
      }
    />
  );
}
