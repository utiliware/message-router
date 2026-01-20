import { RadialBarChart, RadialBar, Cell } from "recharts";
import { Card, CardContent, Typography, IconButton, Box } from "@mui/joy";

export default function SnsRadial({ value, title = "SNS Messages Published", onToggle }) {
  const maxValue = 50;
  const percentage = Math.min((value / maxValue) * 100, 100);
  
  const angle = (percentage / 100) * 180;
  
  const gaugeData = [
    { value: percentage, fill: "#1f77b4" },
    { value: 100 - percentage, fill: "#e0e0e0" }
  ];

  return (
    <Card
      sx={{
        width: "100%",
        border: "1px solid #e0e0e0",
        borderRadius: "4px",
        backgroundColor: "#ffffff",
        position: "relative",
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
          px: 1,
          pt: 1,
        }}
      >
        <Typography
          level="title-sm"
          sx={{
            fontSize: "14px",
            fontWeight: 500,
            color: "#1a1a1a",
          }}
        >
          {title}
        </Typography>
        <Box sx={{ display: "flex", gap: 0.5 }}>
          <IconButton size="sm" variant="plain" sx={{ "--IconButton-size": "24px", fontSize: "18px", color: "#666", fontWeight: "bold" }}>
            ×
          </IconButton>
        </Box>
      </Box>
      
      <CardContent sx={{ display: "flex", flexDirection: "column", alignItems: "center", pb: 2 }}>
        <Box sx={{ position: "relative", width: "100%", maxWidth: "400px" }}>
          <RadialBarChart
            width={400}
            height={200}
            innerRadius="60%"
            outerRadius="90%"
            data={gaugeData}
            startAngle={180}
            endAngle={0}
            barSize={20}
          >
            <RadialBar
              dataKey="value"
              cornerRadius={0}
              fill="#1f77b4"
            >
              {gaugeData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.fill} />
              ))}
            </RadialBar>
          </RadialBarChart>
          
          <Box
            sx={{
              position: "absolute",
              top: "50%",
              left: "50%",
              transform: "translate(-50%, -50%)",
              textAlign: "center",
            }}
          >
            <Typography
              level="h1"
              sx={{
                fontSize: "32px",
                fontWeight: 600,
                color: "#1a1a1a",
                lineHeight: 1,
              }}
            >
              {value}
            </Typography>
          </Box>
          
          <Box
            sx={{
              position: "absolute",
              bottom: "10px",
              left: "20px",
              fontSize: "12px",
              color: "#666",
            }}
          >
            0
          </Box>
          <Box
            sx={{
              position: "absolute",
              bottom: "10px",
              right: "20px",
              fontSize: "12px",
              color: "#666",
            }}
          >
            {maxValue}
          </Box>
        </Box>
        
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            gap: 1,
            mt: 2,
          }}
        >
          <Box
            sx={{
              width: "12px",
              height: "12px",
              backgroundColor: "#1f77b4",
              borderRadius: "2px",
            }}
          />
          <Typography
            level="body-xs"
            sx={{
              fontSize: "12px",
              color: "#666",
            }}
          >
            NumberOfMessagesPublished
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
}
