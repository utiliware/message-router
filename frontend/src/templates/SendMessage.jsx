import React, { useState } from "react";
import axios from "axios";
import {
  CssBaseline,
  Container,
  Typography,
  Input,
  Button,
  Card,
  CardContent,
  Alert,
  Stack,
} from "@mui/joy";

function SendMessage() {
  const [message, setMessage] = useState("");
  const [count, setCount] = useState(""); // empieza vacío
  const [status, setStatus] = useState(null);

  const handleSend = async () => {
    const finalCount = Number(count) || 1; // si está vacío, manda solo 1

    try {
      const payload =
        finalCount > 1
          ? {
              messages: Array.from(
                { length: finalCount },
                (_, i) => `${message} #${i + 1}`
              ),
            }
          : { message };

      await axios.post(import.meta.env.VITE_API_BASE, payload, {
        headers: { "Content-Type": "application/json" },
      });

      setStatus({
        type: "success",
        text:
          finalCount > 1
            ? `Se enviaron ${finalCount} mensajes exitosamente`
            : "Mensaje enviado exitosamente",
      });
    } catch (err) {
      setStatus({
        type: "error",
        text: "Error al enviar el mensaje. Intenta de nuevo.",
      });
    }
  };

  return (
    <>
      <CssBaseline />
      <Container sx={{ mt: 5 }}>
        <Card variant="outlined" sx={{ p: 3 }}>
          <CardContent>
            <Typography level="h4" gutterBottom>
              Enviar Mensaje
            </Typography>

            {/* Input del mensaje */}
            <Input
              placeholder="Escribe tu mensaje..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              sx={{ mb: 2 }}
            />

            {/* Input de cantidad personalizada */}
            <Input
              type="number"
              placeholder="Cantidad de mensajes"
              value={count}
              onChange={(e) => setCount(e.target.value)}
              sx={{ mb: 2 }}
              slotProps={{ input: { min: 1 } }}
            />

            <Stack direction="row" spacing={1} sx={{ mb: 2, flexWrap: "wrap" }}>
              {[50, 100, 150, 200].map((val) => (
                <Button
                  key={val}
                  onClick={() => setCount(val)} 
                  variant={Number(count) === val ? "solid" : "outlined"}
                  color="primary"
                >
                  {val}
                </Button>
              ))}
            </Stack>

            {/* Botón de envío */}
            <Button onClick={handleSend} disabled={!message.trim()}>
              Enviar
            </Button>

            {status && (
              <Alert
                variant="soft"
                color={status.type === "success" ? "success" : "danger"}
                sx={{ mt: 2 }}
              >
                {status.text}
              </Alert>
            )}
          </CardContent>
        </Card>
      </Container>
    </>
  );
}

export default SendMessage;
