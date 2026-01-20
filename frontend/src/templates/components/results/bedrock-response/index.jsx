import { Box, Typography } from "@mui/joy";
import { useResults } from "../../../../hooks/useResults";

export default function ResultsBedrock() {
  const { bedrockResult, loading } = useResults();

  if (loading) {
    return (
      <Box
        sx={{
          width: "100%",
          minHeight: 300,
          borderRadius: 1,
          bgcolor: "primary.700",
          p: 2,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          color: "white",
        }}
      >
        Loading...
      </Box>
    );
  }

  if (!bedrockResult) {
    return (
      <Box
        sx={{
          width: "100%",
          minHeight: 300,
          borderRadius: 1,
          bgcolor: "primary.700",
          p: 2,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          color: "white",
        }}
      >
        No Bedrock response...
      </Box>
    );
  }

  // Handle both string and object responses
  let responseData = bedrockResult;
  if (typeof bedrockResult === 'string') {
    try {
      responseData = JSON.parse(bedrockResult);
    } catch (e) {
      // If parsing fails, treat the string as the response itself
      responseData = { response: bedrockResult };
    }
  }

  const prompt = responseData?.prompt || responseData?.Prompt || "";
  const response = responseData?.response || responseData?.Response || "";
  const source = responseData?.source || responseData?.Source || "";

  return (
    <Box
      sx={{
        width: "100%",
        minHeight: 300,
        borderRadius: 1,
        bgcolor: "primary.700",
        p: 2,
        overflowY: "auto",
        display: "flex",
        flexDirection: "column",
        gap: 2,
      }}
    >
      {prompt && (
        <Box
          sx={{
            p: 2,
            borderRadius: 1,
            bgcolor: "background.surface",
          }}
        >
          <Typography
            level="title-sm"
            sx={{
              fontWeight: "bold",
              mb: 1,
              color: "text.primary",
            }}
          >
            Prompt:
          </Typography>
          <Typography
            level="body-sm"
            sx={{
              color: "text.secondary",
              whiteSpace: "pre-wrap",
              wordBreak: "break-word",
            }}
          >
            {prompt}
          </Typography>
        </Box>
      )}

      {response && (
        <Box
          sx={{
            p: 2,
            borderRadius: 1,
            bgcolor: "background.surface",
          }}
        >
          <Typography
            level="title-sm"
            sx={{
              fontWeight: "bold",
              mb: 1,
              color: "text.primary",
            }}
          >
            Bedrock response:
          </Typography>
          <Typography
            level="body-sm"
            sx={{
              color: "text.secondary",
              whiteSpace: "pre-wrap",
              wordBreak: "break-word",
            }}
          >
            {response}
          </Typography>
          {source && (
            <Typography
              level="body-xs"
              sx={{
                mt: 1,
                color: "text.tertiary",
                fontStyle: "italic",
              }}
            >
              Source: {source}
            </Typography>
          )}
        </Box>
      )}
    </Box>
  );
}