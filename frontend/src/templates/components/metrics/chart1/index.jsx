import {
  Button,
  Container,
  Card,
  CardContent,
  CardActions,
  Typography,
} from "@mui/joy";
import { useState } from "react";
import {
  ResponsiveContainer,
  LineChart,
  AreaChart,
  BarChart,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  Line,
  Area,
  Bar,
} from "recharts";
import SnsRadial from "./SnsRadial";
import SqsLineChart from "./SqsLineChart";
import LambdaErrorsTable from "./LambdaErrorsTable";

export default function Chart({
  id,
  title,
  indicator,
  type,
  data,
  raw,
  onToggle,
  componentType,
  componentData,
}) {
  const [changed, setChanged] = useState("Indicator");
  const safeData = Array.isArray(data) ? data : [];

  const titleFontSize = title.length > 32
  ? "clamp(0.7rem, 1.8vw, 0.9rem)"
  : "clamp(0.85rem, 2vw, 1.1rem)";

  if (componentType === "sns") {
    return (
      <Container>
        {changed === "Indicator" ? (
          <Card sx={{ 
            width: "100%", 
            height: 170 
          }}>
            <CardContent>
              <Typography
                level="body-sm"
                sx={{
                  fontSize: titleFontSize,
                  lineHeight: 1.25,
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  display: "-webkit-box",
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: "vertical",
                }}
              >
                {title}
              </Typography>
              <Typography level="h2">{indicator || componentData?.value || 0}</Typography>
            </CardContent>
            <CardActions>
              <Button onClick={() => {
                setChanged("Chart");
                onToggle?.(true);
              }}>
                See details...
              </Button>
            </CardActions>
          </Card>
        ) : (
          <div
            onClick={() => {
              setChanged("Indicator");
              onToggle?.(false);
            }}
            style={{ cursor: "pointer", width: "100%" }}
          >
            <SnsRadial 
              value={componentData?.value || 0} 
              title={title}
              onToggle={() => {
                setChanged("Indicator");
                onToggle?.(false);
              }}
            />
          </div>
        )}
      </Container>
    );
  }

  if (componentType === "sqs") {
    return (
      <Container>
        {changed === "Indicator" ? (
          <Card sx={{ 
            width: "100%", 
            height: 170 
          }}>
            <CardContent>
              <Typography
                level="body-sm"
                sx={{
                  fontSize: titleFontSize,
                  lineHeight: 1.25,
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  display: "-webkit-box",
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: "vertical",
                }}
              >
                {title}
              </Typography>
              <Typography level="h2">{indicator || "0"}</Typography>
            </CardContent>
            <CardActions>
              <Button onClick={() => {
                setChanged("Chart");
                onToggle?.(true);
              }}>
                See details...
              </Button>
            </CardActions>
          </Card>
        ) : (
          <div
            onClick={() => {
              setChanged("Indicator");
              onToggle?.(false);
            }}
            style={{ cursor: "pointer", width: "100%" }}
          >
            <SqsLineChart 
              data={componentData || []} 
              title={title}
              onToggle={() => {
                setChanged("Indicator");
                onToggle?.(false);
              }}
            />
          </div>
        )}
      </Container>
    );
  }

  if (componentType === "lambda-errors") {
    return (
      <Container>
        {changed === "Indicator" ? (
          <Card sx={{ 
            width: "100%", 
            height: 170 
          }}>
            <CardContent>
              <Typography
                level="body-sm"
                sx={{
                  fontSize: titleFontSize,
                  lineHeight: 1.25,
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  display: "-webkit-box",
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: "vertical",
                }}
              >
                {title}
              </Typography>
              <Typography level="h2">{indicator || "0"}</Typography>
            </CardContent>
            <CardActions>
              <Button onClick={() => {
                setChanged("Chart");
                onToggle?.(true);
              }}>
                See details...
              </Button>
            </CardActions>
          </Card>
        ) : (
          <div
            onClick={() => {
              setChanged("Indicator");
              onToggle?.(false);
            }}
            style={{ cursor: "pointer", width: "100%" }}
          >
            <LambdaErrorsTable 
              rows={componentData || []} 
              title={title}
              onToggle={() => {
                setChanged("Indicator");
                onToggle?.(false);
              }}
            />
          </div>
        )}
      </Container>
    );
  }

  // Original chart types
  const series = (() => {
    if (!raw || raw.length === 0) {
      return type === "area" ? ["p50Ms", "p95Ms"] : [];
    }

    if (type === "area") return ["p50Ms", "p95Ms"];

    const set = new Set();
    for (const item of raw) {
      if (item?.functionName) set.add(item.functionName);
    }
    return [...set];
  })();

  const ChartComponent =
    type === "line"
      ? LineChart
      : type === "area"
      ? AreaChart
      : BarChart;

  const changeToChart = () => {
    setChanged((prev) => {
      const next = prev === "Indicator" ? "Chart" : "Indicator";
      onToggle?.(next === "Chart");
      return next;
    });
  };

  return (
    <Container>
      {changed === "Indicator" ? (
        <Card sx={{ 
          width: "100%", 
          height: 170 
        }}
        >
          <CardContent>
            <Typography
              level="body-sm"
              sx={{
                fontSize: titleFontSize,
                lineHeight: 1.25,
                overflow: "hidden",
                textOverflow: "ellipsis",
                display: "-webkit-box",
                WebkitLineClamp: 2,
                WebkitBoxOrient: "vertical",
              }}
            >
              {title}
            </Typography>
            <Typography level="h2">{indicator}</Typography>
          </CardContent>
          <CardActions>
            <Button onClick={changeToChart}>
              See details...
            </Button>
          </CardActions>
        </Card>
      ) : (
        <div
          onClick={changeToChart}
          style={{ cursor: "pointer", width: "100%" }}
        >
          <ResponsiveContainer width="100%" height={320}>
            <ChartComponent data={safeData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timeLabel" minTickGap={24} />
              <YAxis />
              <Tooltip />
              <Legend />

              {type === "line" &&
                series.map((key) => (
                  <Line
                    key={key}
                    type="monotone"
                    dataKey={key}
                    dot={false}
                    isAnimationActive={false}
                  />
                ))}

              {type === "area" &&
                series.map((key) => (
                  <Area
                    key={key}
                    type="monotone"
                    dataKey={key}
                    dot={false}
                    isAnimationActive={false}
                  />
                ))}

              {type === "bar" &&
                series.map((key) => (
                  <Bar
                    key={key}
                    dataKey={key}
                    isAnimationActive={false}
                  />
                ))}
            </ChartComponent>
          </ResponsiveContainer>
        </div>
      )}
    </Container>
  );
}
