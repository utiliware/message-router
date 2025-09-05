<template>
  <div class="container mx-auto p-6 max-w-3xl bg-white shadow-md rounded-lg">
    <h2 class="text-2xl font-bold mb-4 text-center">Graficas Lambda</h2>
    <canvas ref="chart"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import Chart from "chart.js/auto";

const chart = ref(null);

onMounted(async () => {
  try {
    const res = await fetch("https://rcp9pkrke1.execute-api.us-east-1.amazonaws.com/Stage/metrics");
    const data = await res.json();

    const labels = data.Timestamps.map(t => new Date(t).toLocaleTimeString());
    const values = data.Values;

    new Chart(chart.value, {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            label: "ConcurrentExecutions",
            data: values,
            fill: false,
            borderColor: "blue",
            tension: 0.3
          }
        ]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            display: true,
            position: "top"
          }
        },
        scales: {
          x: {
            title: {
              display: true,
              text: "Hour"
            }
          },
          y: {
            title: {
              display: true,
              text: "Concurrency"
            },
            beginAtZero: true
          }
        }
      }
    });
  } catch (err) {
    console.error("Error fetching metrics:", err);
  }
});
</script>

<style scoped>
.container {
  margin-top: 40px;
  padding: 20px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}
</style>
