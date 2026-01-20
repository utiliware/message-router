import { Box } from "@mui/joy";
import { useResults } from "../../../../hooks/useResults";
import { useEffect } from "react";

export default function ResultsMessage() {
  const { messResult, loading } = useResults();

  useEffect(() => {
    console.log(messResult);
  }, [messResult]);

  if (loading) {
    return (
      <Box
        sx={{
          width: "100%",
          height: 300,
          borderRadius: 1,
          bgcolor: "primary.700",
          p: 2,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          color: "white",
        }}
      >
        Cargando...
      </Box>
    );
  }

  if (!messResult) {
    return (
      <Box
        sx={{
          width: "100%",
          height: 300,
          borderRadius: 1,
          bgcolor: "primary.700",
          p: 2,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          color: "white",
        }}
      >
        No hay resultados
      </Box>
    );
  }

  return (
    <Box
      sx={{
        width: "100%",
        height: 300,
        borderRadius: 1,
        bgcolor: "primary.700",
        p: 2,
        overflowY: "auto",
      }}
    >
      <Box
        sx={{
          mb: 2,
          p: 2,
          borderRadius: 1,
          bgcolor: "background.surface",
        }}
      >
        <Box sx={{ fontWeight: "bold", mb: 1 }}>{messResult.message}</Box>

        {(messResult.contact || []).map((c, index) => (
          <Box
            key={c.id || index}
            sx={{
              mb: 1,
              p: 1,
              borderRadius: 0.5,
              bgcolor: "neutral.softBg",
            }}
          >
            <Box sx={{ fontSize: "0.8rem", fontWeight: "bold", mb: 0.5 }}>
              {c.type}
            </Box>
            {c.type === "phone" ? (
              <Box>
                {c.lada} {c.number}
              </Box>
            ) : (
              <Box>
                {c.email}
                {c.domains}
              </Box>
            )}
          </Box>
        ))}
      </Box>
    </Box>
  );
}