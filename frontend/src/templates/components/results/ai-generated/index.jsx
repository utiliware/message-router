import { Box, Typography } from "@mui/joy";
import { useState, useEffect } from "react";
import { useResults } from "../../../../hooks/useResults";
import { useIdx } from "../../../../context";

export default function ResultsImage() {
  const { iaResult } = useResults();
  const { wsImageUrl } = useIdx();
  const [loadError, setLoadError] = useState(false);
  const imageUrl = wsImageUrl || (typeof iaResult === "string" ? iaResult : iaResult?.url) || null;
  const showImage = imageUrl && !loadError;

  useEffect(() => setLoadError(false), [imageUrl]);

  return (
    <Box
      sx={{
        width: "100%",
        minHeight: showImage ? 0 : 300,
        borderRadius: 1,
        bgcolor: showImage ? "transparent" : "primary.700",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        cursor: showImage ? "pointer" : "default",
        overflow: "hidden",
      }}
    >
      {showImage ? (
        <img
          src={imageUrl}
          alt="Resultado"
          crossOrigin="anonymous"
          onLoad={() => setLoadError(false)}
          onError={() => setLoadError(true)}
          style={{
            maxWidth: "100%",
            width: "auto",
            height: "auto",
            display: "block",
            objectFit: "contain",
          }}
        />
      ) : (
        <Typography level="h6" textColor="common.white">
          {imageUrl && loadError ? "Error al cargar la imagen" : "No imagen"}
        </Typography>
      )}
    </Box>
  );
}
