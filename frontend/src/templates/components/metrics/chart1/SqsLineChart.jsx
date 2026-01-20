import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { Card, CardContent, Typography, IconButton, Box } from "@mui/joy";

const COLORS = {
  visible: "#1f77b4",
  inFlight: "#ff7f0e",
  sent: "#2ca02c",
  received: "#d62728",
};

const METRIC_LABELS = {
  visible: "ApproximateNumberOfMessagesVisible",
  inFlight: "ApproximateNumberOfMessagesNotVisible",
  sent: "NumberOfMessagesSent",
  received: "NumberOfMessagesReceived",
};

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <Box
        sx={{
          backgroundColor: "#fff",
          border: "1px solid #e0e0e0",
          borderRadius: "4px",
          padding: "8px 12px",
          boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
        }}
      >
        <Typography
          sx={{
            fontSize: "12px",
            fontWeight: 600,
            color: "#1a1a1a",
            marginBottom: "4px",
          }}
        >
          {label}
        </Typography>
        {payload.map((entry, index) => (
          <Box
            key={index}
            sx={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              marginTop: "4px",
            }}
          >
            <Box
              sx={{
                width: "12px",
                height: "2px",
                backgroundColor: entry.color,
              }}
            />
            <Typography
              sx={{
                fontSize: "12px",
                color: "#666",
              }}
            >
              {METRIC_LABELS[entry.dataKey] || entry.dataKey}:{" "}
              <span style={{ fontWeight: 600, color: "#1a1a1a" }}>
                {entry.value ?? 0}
              </span>
            </Typography>
          </Box>
        ))}
      </Box>
    );
  }
  return null;
};

export default function SqsLineChart({ data, title = "SQS Queue: visible / in-flight / sent", onToggle }) {
  const chartData = data.map(item => ({
    ...item,
    timeLabel: new Date(item.time).toLocaleTimeString("en-US", { 
      hour: "2-digit", 
      minute: "2-digit",
      hour12: false 
    }),
    timestamp: new Date(item.time).getTime(),
  })).sort((a, b) => a.timestamp - b.timestamp);

  return (
    <Card
      sx={{
        width: "100%",
        border: "1px solid #e0e0e0",
        borderRadius: "4px",
        backgroundColor: "#ffffff",
        cursor: onToggle ? "pointer" : "default",
      }}
      onClick={onToggle}
    >
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 1,
          px: 2,
          pt: 2,
        }}
      >
        <Typography
          level="title-sm"
          sx={{
            fontSize: "14px",
            fontWeight: 500,
            color: "#1a1a1a",
            display: "flex",
            alignItems: "center",
            gap: 1,
          }}
        >
          {title}
          <IconButton size="sm" variant="plain" sx={{ "--IconButton-size": "20px", fontSize: "18px", color: "#666", fontWeight: "bold" }}>
            ×
          </IconButton>
        </Typography>
      </Box>
      
      <CardContent sx={{ px: 2, pb: 2 }}>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis
              dataKey="timeLabel"
              stroke="#666"
              tick={{ fontSize: 12, fill: "#666" }}
              minTickGap={30}
            />
            <YAxis
              label={{ value: "Count", angle: -90, position: "insideLeft", style: { textAnchor: "middle", fill: "#666", fontSize: 12 } }}
              stroke="#666"
              tick={{ fontSize: 12, fill: "#666" }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ fontSize: "12px", paddingTop: "10px" }}
              iconType="line"
            />
            <Line
              type="monotone"
              dataKey="visible"
              stroke={COLORS.visible}
              strokeWidth={2}
              dot={false}
              name={METRIC_LABELS.visible}
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey="inFlight"
              stroke={COLORS.inFlight}
              strokeWidth={2}
              dot={false}
              name={METRIC_LABELS.inFlight}
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey="sent"
              stroke={COLORS.sent}
              strokeWidth={2}
              dot={false}
              name={METRIC_LABELS.sent}
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey="received"
              stroke={COLORS.received}
              strokeWidth={2}
              dot={false}
              name={METRIC_LABELS.received}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
