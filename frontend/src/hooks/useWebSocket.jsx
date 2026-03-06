import { useState, useEffect, useRef, useCallback } from "react";
import { API_BASE_URL } from "../endpoint/api-base";

// WebSocket API is separate from the REST API (MessageWebSocketApi in template.yaml 68-73). URL format: wss://API_ID.execute-api.REGION.amazonaws.com/Prod
const BUILD_WEBSOCKET_URL = import.meta.env.VITE_WEBSOCKET_URL || "";
const FALLBACK_WEBSOCKET_URL = "wss://6gmt988n08.execute-api.us-east-1.amazonaws.com/Prod";

function normalizeWsUrl(url) {
  return (url || "").trim().replace(/\/$/, "");
}

export const useWebSocket = (onMessage) => {
  const [resolvedWsUrl, setResolvedWsUrl] = useState(() => normalizeWsUrl(BUILD_WEBSOCKET_URL));
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;
  const reconnectDelay = 3000; // 3 seconds

  // Resolve WebSocket URL: use build-time env, else GET /config, else fallback
  useEffect(() => {
    if (normalizeWsUrl(BUILD_WEBSOCKET_URL)) return;
    const configUrl = `${API_BASE_URL}/config`;
    fetch(configUrl)
      .then((r) => r.json())
      .then((data) => {
        const url = normalizeWsUrl(data?.webSocketUrl || "");
        if (url) setResolvedWsUrl(url);
        else if (FALLBACK_WEBSOCKET_URL) setResolvedWsUrl(normalizeWsUrl(FALLBACK_WEBSOCKET_URL));
        else setError("Config missing webSocketUrl");
      })
      .catch(() => {
        if (FALLBACK_WEBSOCKET_URL) setResolvedWsUrl(normalizeWsUrl(FALLBACK_WEBSOCKET_URL));
        else setError("Could not load config (is API_BASE_URL correct?)");
      });
  }, []);

  const connect = useCallback(
    (url) => {
      const normalized = normalizeWsUrl(url);
      if (!normalized) {
        setError("WebSocket URL not configured");
        return;
      }
      try {
        const ws = new WebSocket(normalized);
        wsRef.current = ws;

        ws.onopen = () => {
          setIsConnected(true);
          setError(null);
          reconnectAttemptsRef.current = 0;
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (onMessage) onMessage(data);
          } catch (err) {
            console.error("Error parsing WebSocket message:", err);
          }
        };

        ws.onerror = () => {
          setError("WebSocket connection error");
          setIsConnected(false);
        };

        ws.onclose = (event) => {
          setIsConnected(false);
          if (event.code !== 1000 && reconnectAttemptsRef.current < maxReconnectAttempts) {
            reconnectAttemptsRef.current += 1;
            reconnectTimeoutRef.current = setTimeout(() => connect(normalized), reconnectDelay);
          } else if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
            setError("Failed to reconnect after multiple attempts");
          }
        };
      } catch {
        setError("Failed to create WebSocket connection");
        setIsConnected(false);
      }
    },
    [onMessage]
  );

  useEffect(() => {
    if (!resolvedWsUrl) return;
    connect(resolvedWsUrl);
    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (wsRef.current) wsRef.current.close(1000, "Component unmounting");
    };
  }, [resolvedWsUrl, connect]);

  return {
    isConnected,
    error,
    send: (data) => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify(data));
      } else {
        console.warn("WebSocket is not connected. Cannot send message.");
      }
    }
  };
};

