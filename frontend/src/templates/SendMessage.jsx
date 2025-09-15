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
} from "@mui/joy";

function SendMessage() {
  const [message, setMessage] = useState("");
  const [count, setCount] = useState(1); // Número de veces a enviar
  const [status, setStatus] = useState(null); // Mensaje de éxito o error

  const handleSend = async () => {
    try {
      // Construir payload dinámico
      const payload =
        count > 1
          ? { messages: Array.from({ length: count }, (_, i) => `${message} #${i + 1}`) }
          : { message };

      // Llamamos a la Lambda vía API Gateway
      await axios.post(
        "https://iq2br9ni35.execute-api.us-east-1.amazonaws.com/Prod/send", // Variable ENV
        payload,
        { headers: { "Content-Type": "application/json" } }
      );

      // Mostrar éxito
      setStatus({
        type: "success",
        text:
          count > 1
            ? `Se enviaron ${count} mensajes exitosamente`
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

            <Input
              placeholder="Escribe tu mensaje..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              sx={{ mb: 2 }}
            />

            <Input
              type="number"
              placeholder="Cantidad de mensajes"
              value={count}
              onChange={(e) => setCount(Number(e.target.value))}
              sx={{ mb: 2 }}
              slotProps={{ input: { min: 1 } }}
            />

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
