import React, { useEffect, useMemo, useState } from "react";
import axios from "axios";
import {
  CssBaseline,
  Container,
  Typography,
  Input,
  Button,
  Card,
  CardContent,
  Tabs,
  TabList,
  Tab,
  TabPanel,
  Sheet,
  Chip,
  Divider,
  Grid,
  Stack,
  Alert,
} from "@mui/joy";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
  AreaChart,
  Area,
} from "recharts";

const API_BASE = import.meta.env.VITE_API_BASE;
const METRICS_BASE =
  import.meta.env.VITE_API_BASE_METRICS || import.meta.env.VITE_API_BASE;

export default function App() {
  return (
    <>
      <CssBaseline />
      <Container sx={{ py: 4 }}>
        <Header />
        <Tabs defaultValue={0} sx={{ mt: 2 }}>
          <TabList>
            <Tab value={0}>Enviar</Tab>
            <Tab value={1}>Métricas</Tab>
          </TabList>
          <TabPanel value={0}>
            <SendMessageCard />
          </TabPanel>
          <TabPanel value={1}>
            <MetricsDashboard />
          </TabPanel>
        </Tabs>
      </Container>
    </>
  );
}

function Header() {
  return (
    <Stack spacing={1} sx={{ mb: 1 }}>
      <Typography level="h2">Demo: Envío de Mensajes + Métricas</Typography>
      <Typography level="body-sm" sx={{ opacity: 0.8 }}>
        Joy UI + Recharts • SPA de React
      </Typography>
      <Alert variant="soft" color="neutral">
        <Typography level="body-sm">
          Configura variables de entorno: <code>VITE_API_BASE</code> y{" "}
          <code>VITE_API_BASE_METRICS</code>
        </Typography>
      </Alert>
    </Stack>
  );
}

function SendMessageCard() {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);

  const handleSend = async () => {
    setLoading(true);
    setError(null);
    setResponse(null);
    try {
      const res = await axios.post(
        API_BASE,
        { message },
        {
          headers: { "Content-Type": "application/json" },
        }
      );
      setResponse(res.data);
    } catch (err) {
      setError(
        err?.response?.data?.message ||
          err?.message ||
          "Error al enviar el mensaje"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card variant="outlined">
      <CardContent>
        <Typography level="h4" gutterBottom>
          Enviar Mensaje
        </Typography>
        <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
          <Input
            placeholder="Escribe tu mensaje..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            sx={{ flex: 1 }}
          />
          <Button
            loading={loading}
            onClick={handleSend}
            disabled={!message.trim()}
          >
            Enviar
          </Button>
        </Stack>
        <Divider sx={{ my: 2 }} />
        {error && (
          <Alert color="danger" variant="soft">
            {String(error)}
          </Alert>
        )}
        {response && (
          <Sheet variant="soft" sx={{ p: 2, borderRadius: "lg" }}>
            <Typography level="title-md" sx={{ mb: 1 }}>
              Respuesta
            </Typography>
            <pre
              style={{
                margin: 0,
                whiteSpace: "pre-wrap",
                wordBreak: "break-word",
              }}
            >
              {JSON.stringify(response, null, 2)}
            </pre>
          </Sheet>
        )}
        <Stack direction="row" spacing={1} sx={{ mt: 2 }}>
          <Chip variant="soft">API_BASE: {API_BASE}</Chip>
        </Stack>
      </CardContent>
    </Card>
  );
}

function MetricsDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchMetrics = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(METRICS_BASE, { timeout: 20000 });
      setData(res.data);
    } catch (err) {
      setError(
        err?.response?.data?.message || err?.message || "Error al leer métricas"
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);
  useEffect(() => {
    if (!autoRefresh) return;
    const id = setInterval(fetchMetrics, 10000);
    return () => clearInterval(id);
  }, [autoRefresh]);

  const { lambdaDurationSeries, eventRuleLatencySeries, invocationSeries } =
    useMemo(() => normalizeMetrics(data), [data]);

  return (
    <Stack spacing={2}>
      <Card variant="outlined">
        <CardContent>
          <Stack
            direction={{ xs: "column", md: "row" }}
            justifyContent="space-between"
            alignItems={{ xs: "stretch", md: "center" }}
            spacing={2}
          >
            <Typography level="h4">Métricas en tiempo casi real</Typography>
            <Stack direction="row" spacing={1}>
              <Button
                variant="soft"
                onClick={fetchMetrics}
                loading={loading}
              >
                Refrescar ahora
              </Button>
              <Button
                variant={autoRefresh ? "solid" : "soft"}
                onClick={() => setAutoRefresh((v) => !v)}
              >
                Auto: {autoRefresh ? "ON" : "OFF"}
              </Button>
              <Chip variant="soft">METRICS_BASE: {METRICS_BASE}</Chip>
            </Stack>
          </Stack>
          {error && (
            <Alert color="danger" variant="soft" sx={{ mt: 2 }}>
              {String(error)}
            </Alert>
          )}
          {!error && !data && (
            <Typography level="body-sm" sx={{ mt: 2 }}>
              Cargando o esperando datos de métrica...
            </Typography>
          )}
          {data && (
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid xs={12} lg={6}>
                <MetricCard
                  title="Duración promedio por Lambda (ms)"
                  subtitle="Promedio por timestamp y función"
                >
                  <ResponsiveContainer width="100%" height={320}>
                    <LineChart data={lambdaDurationSeries}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="timeLabel"
                        interval="preserveStartEnd"
                        minTickGap={24}
                      />
                      <YAxis allowDecimals domain={["auto", "auto"]} />
                      <Tooltip />
                      <Legend />
                      {uniqueKeys(
                        data.lambdaDurations,
                        (d) => d.functionName
                      ).map((fn) => (
                        <Line
                          key={fn}
                          type="monotone"
                          dataKey={fn} // ✅ string
                          name={fn}
                          dot={false}
                          isAnimationActive={false}
                        />
                      ))}
                    </LineChart>
                  </ResponsiveContainer>
                </MetricCard>
              </Grid>
              <Grid xs={12} lg={6}>
                <MetricCard
                  title="Latencia EventBridge (p50 / p95 ms)"
                  subtitle="Por regla/timestamp"
                >
                  <ResponsiveContainer width="100%" height={320}>
                    <AreaChart data={eventRuleLatencySeries}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="timeLabel"
                        interval="preserveStartEnd"
                        minTickGap={24}
                      />
                      <YAxis allowDecimals domain={["auto", "auto"]} />
                      <Tooltip />
                      <Legend />
                      <Area
                        type="monotone"
                        dataKey="p50Ms"
                        name="p50"
                        dot={false}
                        isAnimationActive={false}
                      />
                      <Area
                        type="monotone"
                        dataKey="p95Ms"
                        name="p95"
                        dot={false}
                        isAnimationActive={false}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </MetricCard>
              </Grid>
              <Grid xs={12}>
                <MetricCard
                  title="Invocaciones por Lambda"
                  subtitle="Conteo por ventana/timestamp"
                >
                  <ResponsiveContainer width="100%" height={320}>
                    <BarChart data={invocationSeries}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="timeLabel"
                        interval="preserveStartEnd"
                        minTickGap={24}
                      />
                      <YAxis allowDecimals />
                      <Tooltip />
                      <Legend />
                      {uniqueKeys(
                        data.invocations,
                        (d) => d.functionName
                      ).map((fn) => (
                        <Bar
                          key={fn}
                          dataKey={fn} // ✅ string
                          name={fn}
                          isAnimationActive={false}
                        />
                      ))}
                    </BarChart>
                  </ResponsiveContainer>
                </MetricCard>
              </Grid>
            </Grid>
          )}
        </CardContent>
      </Card>
    </Stack>
  );
}

function MetricCard({ title, subtitle, children }) {
  return (
    <Card variant="outlined">
      <CardContent>
        <Typography level="title-lg">{title}</Typography>
        {subtitle && (
          <Typography level="body-sm" sx={{ opacity: 0.8, mb: 1 }}>
            {subtitle}
          </Typography>
        )}
        {children}
      </CardContent>
    </Card>
  );
}

function normalizeMetrics(raw) {
  if (!raw)
    return { lambdaDurationSeries: [], eventRuleLatencySeries: [], invocationSeries: [] };

  const formatTime = (ts) =>
    new Date(ts).toLocaleString(undefined, {
      hour12: false,
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });

  // pivotear lambdaDurations
  const lambdaDurationSeries = Object.values(
    (raw.lambdaDurations || []).reduce((acc, d) => {
      const timeLabel = formatTime(d.timestamp);
      acc[timeLabel] = acc[timeLabel] || { timeLabel };
      acc[timeLabel][d.functionName] = d.avgMs;
      return acc;
    }, {})
  );

  const eventRuleLatencySeries = (raw.eventBridgeLatencies || []).map((d) => ({
    ...d,
    timeLabel: formatTime(d.timestamp),
  }));

  // pivotear invocations
  const invocationSeries = Object.values(
    (raw.invocations || []).reduce((acc, d) => {
      const timeLabel = formatTime(d.timestamp);
      acc[timeLabel] = acc[timeLabel] || { timeLabel };
      acc[timeLabel][d.functionName] = d.count;
      return acc;
    }, {})
  );

  return { lambdaDurationSeries, eventRuleLatencySeries, invocationSeries };
}

function uniqueKeys(arr, keySelector) {
  const set = new Set();
  for (const item of arr || []) set.add(keySelector(item));
  return [...set];
}
