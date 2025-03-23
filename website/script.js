document.addEventListener("DOMContentLoaded", function () {
  const months = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
  ];
  const trendData = [30, 40, 55, 60, 75, 80, 95, 90, 85, 70, 50, 40];

  function calculateStats(data) {
    let sum = data.reduce((a, b) => a + b, 0);
    let mean = sum / data.length;
    let variance =
      data.reduce((total, value) => total + Math.pow(value - mean, 2), 0) /
      data.length;
    return {
      mean: mean.toFixed(2),
      stdDev: Math.sqrt(variance).toFixed(2),
      min: Math.min(...data),
      max: Math.max(...data),
    };
  }

  let stats = calculateStats(trendData);
  document.getElementById("stats").innerHTML = `
      <div class="stats-box">
          <p><strong>Mean:</strong> ${stats.mean}</p>
          <p><strong>Standard Deviation:</strong> ${stats.stdDev}</p>
          <p><strong>Min Cases:</strong> ${stats.min}</p>
          <p><strong>Max Cases:</strong> ${stats.max}</p>
      </div>
  `;

  new Chart(document.getElementById("trendChart"), {
    type: "line",
    data: {
      labels: months,
      datasets: [
        {
          label: "Disease Trend",
          data: trendData,
          borderColor: "#4CAF50",
          backgroundColor: "rgba(76, 175, 80, 0.2)",
          borderWidth: 2,
          pointBackgroundColor: "#4CAF50",
          pointBorderColor: "#4CAF50",
          pointRadius: 5,
          fill: true,
          tension: 0.4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { labels: { color: "#333", font: { size: 14 } } } },
      scales: {
        x: { ticks: { color: "#333" } },
        y: { ticks: { color: "#333" } },
      },
    },
  });

  function updateClock() {
    const now = new Date();
    document.getElementById("clock").textContent = new Intl.DateTimeFormat(
      "en-IN",
      {
        timeZone: "Asia/Kolkata",
        hour12: true,
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      }
    ).format(now);
  }
  setInterval(updateClock, 1000);
  updateClock();
});
