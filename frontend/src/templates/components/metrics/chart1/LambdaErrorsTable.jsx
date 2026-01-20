import { Card, CardContent, Typography, Box, Table, Sheet, IconButton } from "@mui/joy";
import { useState } from "react";

export default function LambdaErrorsTable({ rows, title = "Lambda Errors", onToggle }) {
  const [timeRange, setTimeRange] = useState("12h");
  
  const tableRows = rows.length > 0 ? rows : [
    { function: "message-router-ApiFunction", errors: 0 },
    { function: "message-router-LambdaDispatcher", errors: 0 },
    { function: "message-router-DynamoLambda", errors: 0 },
    { function: "message-router-DdbToS3Handler", errors: 0 },
  ];

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
          mb: 2,
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
          }}
        >
          {title}
        </Typography>
        <Box sx={{ display: "flex", gap: 1, alignItems: "center" }}>
          {/* <Box
            sx={{
              display: "flex",
              gap: 0.5,
              border: "1px solid #d0d0d0",
              borderRadius: "4px",
              p: 0.5,
            }}
          >
            {["1h", "3h", "12h", "1d", "3d", "1w"].map((range) => (
              <Box
                key={range}
                onClick={(e) => {
                  e.stopPropagation();
                  setTimeRange(range);
                }}
                sx={{
                  px: 1,
                  py: 0.5,
                  borderRadius: "3px",
                  fontSize: "12px",
                  cursor: "pointer",
                  backgroundColor: timeRange === range ? "#1f77b4" : "transparent",
                  color: timeRange === range ? "#fff" : "#666",
                  "&:hover": {
                    backgroundColor: timeRange === range ? "#1f77b4" : "#f0f0f0",
                  },
                }}
              >
                {range}
              </Box>
            ))}
          </Box> */}
          <IconButton size="sm" variant="plain" sx={{ "--IconButton-size": "24px", fontSize: "18px", color: "#666", fontWeight: "bold" }}>
            ×
          </IconButton>
        </Box>
      </Box>
      
      <CardContent sx={{ px: 2, pb: 2 }}>
        <Sheet
          variant="outlined"
          sx={{
            borderRadius: "4px",
            overflow: "auto",
            maxHeight: "400px",
          }}
        >
          <Table
            sx={{
              "& thead th": {
                backgroundColor: "#f5f5f5",
                fontWeight: 600,
                fontSize: "12px",
                color: "#1a1a1a",
                borderBottom: "1px solid #e0e0e0",
                position: "sticky",
                top: 0,
                zIndex: 1,
              },
              "& tbody td": {
                fontSize: "12px",
                color: "#1a1a1a",
                borderBottom: "1px solid #f0f0f0",
              },
              "& tbody tr:hover": {
                backgroundColor: "#f9f9f9",
              },
            }}
          >
            <thead>
              <tr>
                <th style={{ width: "40px" }}></th>
                <th style={{ textAlign: "left", minWidth: "250px" }}>Label</th>
                <th style={{ textAlign: "right", width: "80px" }}>Min</th>
                <th style={{ textAlign: "right", width: "80px" }}>Max</th>
                <th style={{ textAlign: "right", width: "80px" }}>Sum</th>
                <th style={{ textAlign: "right", width: "80px" }}>Average</th>
              </tr>
            </thead>
            <tbody>
              {tableRows.map((row, index) => (
                <tr key={row.function || index}>
                  <td>
                    <Box
                      sx={{
                        width: "16px",
                        height: "16px",
                        borderRadius: "2px",
                        backgroundColor: "#1f77b4",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                      }}
                    >
                      <Box
                        sx={{
                          width: "8px",
                          height: "8px",
                          borderRadius: "50%",
                          backgroundColor: "#fff",
                        }}
                      />
                    </Box>
                  </td>
                  <td style={{ textAlign: "left" }}>
                    <Typography level="body-sm" sx={{ fontSize: "12px" }}>
                      {row.function}
                    </Typography>
                  </td>
                  <td style={{ textAlign: "right" }}>{row.errors || 0}</td>
                  <td style={{ textAlign: "right" }}>{row.errors || 0}</td>
                  <td style={{ textAlign: "right" }}>{row.errors || 0}</td>
                  <td style={{ textAlign: "right" }}>{row.errors || 0}</td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Sheet>
      </CardContent>
    </Card>
  );
}
