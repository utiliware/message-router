import { Box, Typography } from "@mui/joy";
import { useState } from "react";
import { useResults } from "../../../../hooks/useResults";

export default function ResultsImage() {
  const { iaResult } = useResults()
  //   const [imageUrl, setImageUrl] = useState(data[1])
    // const [imageUrl, setImageUrl] = useState("")
  const [imageUrl, setImageUrl] = useState("https://ethic.es/wp-content/uploads/2023/03/imagen-640x384.jpg")
  
  return (
    <Box
      sx={{
        width: "100%",
        height: 300,
        borderRadius: 1,
        bgcolor: imageUrl ? "transparent" : "primary.700",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        cursor: imageUrl ? "pointer" : "default",
        overflow: "hidden"
      }}
    >
      {imageUrl ? (
        <img
          src={imageUrl}
          alt="Resultado"
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
          }}
        />
      ) : (
        <Typography level="h6" textColor="common.white">
          No imagen
        </Typography>
      )}
    </Box>
  );
}
