import React from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

function ChartView({ result }) {
  if (!Array.isArray(result) || result.length === 0) return null;
  const keys = Object.keys(result[0]);
  if (keys.length < 2) return null;
  const labelKey = keys[0];
  const dataKey = keys[1];
  const labels = result.map((r) => String(r[labelKey]));
  const data = result.map((r) => Number(r[dataKey]));
  if (data.some((n) => Number.isNaN(n))) return null;
  const chartData = {
    labels,
    datasets: [
      {
        label: dataKey,
        data,
        backgroundColor: 'rgba(75,192,192,0.5)',
      },
    ],
  };
  const options = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      title: { display: true, text: 'Query Results' },
    },
  };
  return <Bar data={chartData} options={options} />;
}

export default ChartView;
