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

function ResultChart({ data }) {
  if (!Array.isArray(data) || data.length === 0) return null;

  const numericKeys = Object.keys(data[0]).filter((key) =>
    data.every((row) => typeof row[key] === 'number')
  );

  if (numericKeys.length === 0) return null;

  const key = numericKeys[0];
  const labels = data.map((_, idx) => String(idx + 1));
  const values = data.map((row) => row[key]);

  const chartData = {
    labels,
    datasets: [
      {
        label: key,
        data: values,
        backgroundColor: 'rgba(54, 162, 235, 0.5)',
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: `Chart of ${key}`,
      },
    },
  };

  return (
    <div className="w-full h-96 my-4">
      <Bar data={chartData} options={options} />
    </div>
  );
}

export default ResultChart;

