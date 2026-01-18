import { useState } from "react";
import Section from "../../../components/Section";
import Chart from "./chart1";
import { useMetrics } from "../../../hooks/useMetrics";

export default function Metrics() {
  const data = useMetrics()
  const [activeChartId, setActiveChartId] = useState(null);
 

//   const [chart] = useState(data)
  const [chart] = useState([
    {
      id: 1,
      title: "Duración promedio por Lambda (ms)",
      indicator: "10",
      type: "line",
      data: { hola: "como estas" },
    },
    {
      id: 2,
      title: "Latencia EventBridge (p50 / p95 ms)",
      indicator: "20",
      type: "area",
      data: { hola: "como estas" },
    },
    {
      id: 3,
      title: "Invocaciones por Lambda",
      indicator: "30",
      type: "bar",
      data: { hola: "como estas" },
    },
  ]);

  return (
    <Section
      title={"Metrics"}
      content={
        <>
          {chart.filter((c) => activeChartId === null || c.id === activeChartId).map(({ id, title, indicator, type, data }) => (
              <Chart
                key={id}
                id={id}
                title={title}
                indicator={indicator}
                type={type}
                data={data}
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
