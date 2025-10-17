import React, { useState, useEffect, useRef, useCallback } from "react";
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
  List,
  ListItem,
  Sheet,
} from "@mui/joy";

function SendMessage() {
  const [message, setMessage] = useState("");
  const [count, setCount] = useState(1);
  const [status, setStatus] = useState(null);
  const [prompts, setPrompts] = useState([]);
  const [wsStatus, setWsStatus] = useState("disconnected");
  const wsRef = useRef(null);

  // --- Manejar mensajes entrantes del WebSocket ---
  const handleIncomingMessage = useCallback((data) => {
    if (!data.prompt || !data.response) return;
    setPrompts((prev) => [
      { ...data, timestamp: new Date().toISOString() },
      ...prev,
    ]);
  }, []);

  // --- Conectar WebSocket con reconexión automática ---
  useEffect(() => {
    const wsUrl = import.meta.env.VITE_WS_BASE;
    if (!wsUrl) return console.error("❌ Falta configurar VITE_WS_BASE");

    let ws;

    const connect = () => {
      console.log("🔗 Conectando a WebSocket:", wsUrl);
      ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log("✅ WebSocket conectado");
        setWsStatus("connected");
        setStatus({ type: "info", text: "Conectado al WebSocket de Bedrock" });
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleIncomingMessage(data);
        } catch (err) {
          console.error("Error parseando mensaje WS:", err);
        }
      };

      ws.onclose = () => {
        console.warn("🔌 WebSocket desconectado. Reintentando en 5s...");
        setWsStatus("disconnected");
        setStatus({ type: "warning", text: "WebSocket desconectado. Reintentando..." });
        setTimeout(connect, 5000);
      };

      ws.onerror = (err) => {
        console.error("⚠️ Error WebSocket:", err);
        ws.close();
      };
    };

    connect();

    return () => ws.close();
  }, [handleIncomingMessage]);

  // --- Enviar mensaje a Lambda (API) ---
  const handleSend = async () => {
    if (!message.trim()) return;

    if (wsStatus !== "connected") {
      setStatus({ type: "warning", text: "Aún no hay conexión WebSocket. Espera unos segundos." });
      return;
    }

    try {
      const payload =
        count > 1
          ? { messages: Array.from({ length: count }, (_, i) => `${message} #${i + 1}`) }
          : { message };

      await axios.post(import.meta.env.VITE_API_BASE, payload, {
        headers: { "Content-Type": "application/json" },
      });

      setStatus({
        type: "success",
        text: count > 1
          ? `Se enviaron ${count} mensajes exitosamente`
          : "Mensaje enviado exitosamente",
      });
    } catch (err) {
      console.error(err);
      setStatus({ type: "error", text: "Error al enviar el mensaje. Intenta de nuevo." });
    }
  };

  return (
    <>
      <CssBaseline />
      <Container sx={{ mt: 5 }}>
        <Card variant="outlined" sx={{ p: 3 }}>
          <CardContent>
            <Typography level="h3" gutterBottom>
              🚀 Enviar mensaje a Bedrock
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

            <Stack direction="row" spacing={1} sx={{ mb: 2, flexWrap: "wrap" }}>
              {[50, 100, 150, 200].map((val) => (
                <Button
                  key={val}
                  onClick={() => setCount(val)}
                  variant={count === val ? "solid" : "outlined"}
                  color="primary"
                >
                  {val}
                </Button>
              ))}
            </Stack>

            <Button onClick={handleSend} disabled={!message.trim()} sx={{ mb: 2 }}>
              Enviar a API
            </Button>

            {status && (
              <Alert
                variant="soft"
                color={
                  status.type === "success"
                    ? "success"
                    : status.type === "error"
                    ? "danger"
                    : status.type === "warning"
                    ? "warning"
                    : "neutral"
                }
                sx={{ mt: 2 }}
              >
                {status.text}
              </Alert>
            )}

            {prompts.length > 0 && (
              <Sheet
                variant="outlined"
                sx={{
                  mt: 3,
                  maxHeight: 400,
                  overflowY: "auto",
                  borderRadius: "md",
                  p: 1,
                }}
              >
                <List>
                  {prompts.map((item, idx) => (
                    <ListItem
                      key={idx}
                      sx={{
                        flexDirection: "column",
                        alignItems: "flex-start",
                        mb: 1,
                        p: 2,
                        border: "1px solid #e0e0e0",
                        borderRadius: "md",
                        backgroundColor: "#fafafa",
                      }}
                    >
                      <Typography level="body-sm" color="neutral" sx={{ mb: 1 }}>
                        🧠 <strong>Prompt:</strong> {item.prompt}
                      </Typography>
                      <Typography level="body-sm" sx={{ mb: 0.5 }}>
                        💬 <strong>Respuesta:</strong> {item.response}
                      </Typography>
                      <Typography level="body-xs" color="neutral">
                        📡 Fuente: {item.source || "Bedrock"} | 🕒{" "}
                        {new Date(item.timestamp).toLocaleTimeString()}
                      </Typography>
                    </ListItem>
                  ))}
                </List>
              </Sheet>
            )}
          </CardContent>
        </Card>
      </Container>
    </>
  );
}

export default SendMessage;
