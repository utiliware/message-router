import { useEffect, useState } from "react";
import SnsRadial from "./SnsRadial";
import SqsLineChart from "./SqsLineChart";
import LambdaErrorsTable from "./LambdaErrorsTable";

export default function InvocationsDashboard() {
  const [sns, setSns] = useState(0);
  const [sqs, setSqs] = useState([]);
  const [lambdaErrors, setLambdaErrors] = useState([]);
  const [loading, setLoading] = useState(true);

  // CHANGE URL
  useEffect(() => {
  fetch("https://k8h3j63qrd.execute-api.us-east-1.amazonaws.com/Prod/metrics", {
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
      setSns(data.sns.value);
      
      // Transform SQS data to match SqsLineChart expected format
      const transformedSqs = data.sqs.map(item => ({
        time: item.time,
        visible: item.sqsVisible ?? 0,
        inFlight: item.sqsInFlight ?? 0,
        sent: item.sqsSent ?? 0,
        received: item.sqsReceived ?? 0
      }));
      setSqs(transformedSqs);
      
      // Transform Lambda errors to match LambdaErrorsTable expected format
      // Sum all errors for the function (since table shows one row per function)
      const totalErrors = data.lambdaErrors.reduce((sum, item) => sum + (item.errors ?? 0), 0);
      const transformedErrors = totalErrors > 0 ? [{
        function: "api_router", // You may want to make this dynamic
        errors: totalErrors
      }] : [];
      setLambdaErrors(transformedErrors);
      
      setLoading(false);
    })
    .catch(err => {
      console.error("Failed to load metrics:", err);
      setLoading(false);
    });
}, []);

  if (loading) return <p>Loading CloudWatch metrics…</p>;

  return (
    <>
      <SnsRadial value={sns} />
      <SqsLineChart data={sqs} />
      <LambdaErrorsTable rows={lambdaErrors} />
    </>
  );
}
