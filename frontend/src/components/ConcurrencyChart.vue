<template>
  <div class="p-6">
    <h2 class="text-xl font-bold mb-4">Concurrencia Lambda</h2>
    <LineChart :chart-data="chartData" :chart-options="chartOptions" />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { Chart as ChartJS, Title, Tooltip, Legend, LineElement, LinearScale, PointElement, CategoryScale } from "chart.js";
import { Line } from "vue-chartjs";

// Registrar componentes de Chart.js
ChartJS.register(Title, Tooltip, Legend, LineElement, LinearScale, PointElement, CategoryScale);

const chartData = ref({
  labels: [],
  datasets: [
    {
      label: "ConcurrentExecutions",
      data: [],
      borderColor: "rgb(75, 192, 192)",
      tension: 0.3
    }
  ]
});

const chartOptions = {
  responsive: true,
  plugins: {
    legend: {
      display: true,
      position: "top"
    }
  }
};

onMounted(async () => {
  const res = await fetch("https://rcp9pkrke1.execute-api.us-east-1.amazonaws.com/Stage/metrics");
  const data = await res.json();

  // Suponiendo que tu Lambda devuelve Timestamps y Values
  chartData.value.labels = data.Timestamps.map(t => new Date(t).toLocaleTimeString());
  chartData.value.datasets[0].data = data.Values;
});

const LineChart = Line;
</script>
